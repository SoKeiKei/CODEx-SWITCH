import json
import os
import shutil
import stat
import base64
import time
from datetime import datetime, timezone
from pathlib import Path

class CodexService:
    ACCOUNTS_DIR = "codex-switch"
    AUTH_FILENAME = "auth.json"
    
    def __init__(self, config_path: str = "config/accounts.json"):
        self.config_path = Path(__file__).parent.parent / config_path
        self.config_path.parent.mkdir(exist_ok=True)
        if not self.config_path.exists():
            with open(self.config_path, 'w') as f:
                json.dump({}, f)
        
        self.accounts_dir = Path.home() / ".codex" / self.ACCOUNTS_DIR
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        self._migrate_accounts_to_email_keys()

    def get_accounts(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_accounts(self, accounts):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=4)

    def _migrate_accounts_to_email_keys(self):
        accounts = self.get_accounts()
        migrated = {}
        changed = False

        for key, data in accounts.items():
            if not isinstance(data, dict):
                continue

            email = data.get("email") or key
            new_key = email if "@" in email else key
            account_data = dict(data)
            account_data["email"] = email
            account_data.pop("alias", None)

            legacy_names = account_data.get("legacy_names", [])
            if not isinstance(legacy_names, list):
                legacy_names = []
            old_legacy_aliases = account_data.pop("legacy_aliases", [])
            if isinstance(old_legacy_aliases, list):
                legacy_names.extend(old_legacy_aliases)
            old_alias = data.get("alias")
            for legacy in (key, old_alias):
                if legacy and legacy != new_key and legacy not in legacy_names:
                    legacy_names.append(legacy)
                    changed = True
            if legacy_names:
                deduped = []
                for legacy in legacy_names:
                    if legacy and legacy != new_key and legacy not in deduped:
                        deduped.append(legacy)
                account_data["legacy_names"] = deduped

            if key != new_key or data.get("alias") is not None or data.get("legacy_aliases") is not None:
                changed = True

            if new_key in migrated:
                existing = migrated[new_key]
                existing_names = existing.setdefault("legacy_names", [])
                for legacy in account_data.get("legacy_names", []):
                    if legacy not in existing_names:
                        existing_names.append(legacy)
                for field in ("account_id", "last_refresh", "saved_at"):
                    if account_data.get(field) and not existing.get(field):
                        existing[field] = account_data[field]
                if account_data.get("plan") and existing.get("plan") in (None, "Unknown", "unknown"):
                    existing["plan"] = account_data["plan"]
                changed = True
            else:
                migrated[new_key] = account_data

        if changed:
            self.save_accounts(migrated)

    def _account_auth_path(self, account_key: str, account_data: dict):
        candidates = [account_key]
        email = account_data.get("email")
        if email and email not in candidates:
            candidates.append(email)
        for legacy in account_data.get("legacy_names", []):
            if legacy and legacy not in candidates:
                candidates.append(legacy)
        old_alias = account_data.get("alias")
        if old_alias and old_alias not in candidates:
            candidates.append(old_alias)

        for name in candidates:
            path = self.accounts_dir / name / self.AUTH_FILENAME
            if path.exists():
                return path
        return self.accounts_dir / account_key / self.AUTH_FILENAME

    @staticmethod
    def parse_jwt_email(jwt_token):
        try:
            payload = jwt_token.split('.')[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)
            return data.get('email', '')
        except:
            return ''

    @staticmethod
    def parse_jwt_plan(jwt_token):
        try:
            payload = jwt_token.split('.')[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            data = json.loads(decoded)
            if 'https://api.openai.com/auth' in data:
                return data['https://api.openai.com/auth'].get('chatgpt_plan_type', 'unknown')
            return 'unknown'
        except:
            return 'unknown'

    @staticmethod
    def _codex_dir():
        return Path.home() / ".codex"

    @classmethod
    def _current_auth_path(cls):
        return cls._codex_dir() / cls.AUTH_FILENAME

    def _auth_backup_dir(self):
        path = self.accounts_dir / "backups"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _load_json(path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _backup_current_auth(self, reason: str):
        auth_file = self._current_auth_path()
        if not auth_file.exists():
            return None
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_reason = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in reason)[:40]
        backup_path = self._auth_backup_dir() / f"auth-{timestamp}-{safe_reason}.json"
        shutil.copy2(auth_file, backup_path)
        return backup_path

    @staticmethod
    def _atomic_copy_file(source: Path, target: Path):
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target.with_name(f".{target.name}.tmp-{os.getpid()}")
        shutil.copy2(source, tmp_path)
        os.replace(tmp_path, target)
        try:
            os.utime(target, None)
        except Exception:
            pass

    def _extract_auth_details(self, auth_data):
        tokens = auth_data.get('tokens', {})
        id_token = tokens.get('id_token', '')
        email = self.parse_jwt_email(id_token)
        return {
            "email": email,
            "plan": self.parse_jwt_plan(id_token) if id_token else "unknown",
            "account_id": tokens.get('account_id', ''),
            "last_refresh": auth_data.get('last_refresh', ''),
        }

    def get_current_email_and_plan(self):
        auth_file = self._current_auth_path()
        if not auth_file.exists():
            return None, None
        
        try:
            details = self._extract_auth_details(self._load_json(auth_file))
            if details["email"]:
                return details["email"], details["plan"]
        except:
            pass
        return None, None

    def get_current_account_info(self):
        email, plan = self.get_current_email_and_plan()
        
        if not email:
            return {
                'email': 'N/A',
                'plan': 'N/A'
            }
        
        accounts = self.get_accounts()
        for _, data in accounts.items():
            if data.get('email', '').lower() == email.lower():
                return {
                    'email': email,
                    'plan': plan or data.get('plan', 'Unknown')
                }
        
        return {
            'email': email,
            'plan': plan or 'Unknown'
        }

    @staticmethod
    def _remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def add_account(self):
        accounts = self.get_accounts()

        auth_file = self._current_auth_path()
        
        if not auth_file.exists():
            print(f"No auth.json found. Please login first. / 未找到 auth.json，请先登录账号。")
            return False
        
        auth_data = self._load_json(auth_file)
        details = self._extract_auth_details(auth_data)
        email = details["email"]
        plan = details["plan"]
        
        if not email:
            print(f"Cannot parse email from auth.json. / 无法从 auth.json 解析邮箱。")
            return False
        
        account_dir = self.accounts_dir / email
        existed = email in accounts
        account_dir.mkdir(parents=True, exist_ok=True)
        
        self._atomic_copy_file(auth_file, account_dir / self.AUTH_FILENAME)
        
        existing = accounts.get(email, {})
        legacy_names = existing.get("legacy_names", [])
        if not isinstance(legacy_names, list):
            legacy_names = []

        accounts[email] = {
            "email": email,
            "plan": plan,
            "account_id": details["account_id"],
            "last_refresh": details["last_refresh"],
            "saved_at": datetime.now().isoformat(timespec="seconds")
        }
        if legacy_names:
            accounts[email]["legacy_names"] = legacy_names
        self.save_accounts(accounts)
        action = "updated" if existed else "created"
        action_cn = "已更新" if existed else "已创建"
        print(f"Account '{email}' {action}. / 账号 '{email}' {action_cn}。")
        print(f"  Plan: {plan}")
        return True

    def sync_current_account(self, silent=True):
        auth_file = self._current_auth_path()
        if not auth_file.exists():
            return False

        try:
            auth_data = self._load_json(auth_file)
            details = self._extract_auth_details(auth_data)
        except Exception:
            return False

        email = details["email"]
        account_id = details["account_id"]
        if not email and not account_id:
            return False

        accounts = self.get_accounts()
        matched_key = None
        for key, data in accounts.items():
            if email and data.get('email', '').lower() == email.lower():
                matched_key = key
                break
            if account_id and data.get('account_id') == account_id:
                matched_key = key
                break

        if not matched_key:
            return False

        account_dir = self.accounts_dir / matched_key
        account_dir.mkdir(parents=True, exist_ok=True)
        target_auth = account_dir / self.AUTH_FILENAME

        changed = True
        if target_auth.exists():
            try:
                changed = auth_file.read_bytes() != target_auth.read_bytes()
            except Exception:
                changed = True

        if changed:
            self._atomic_copy_file(auth_file, target_auth)

        account_data = accounts[matched_key]
        metadata_changed = False
        for key, value in {
            "email": email,
            "plan": details["plan"],
            "account_id": account_id,
            "last_refresh": details["last_refresh"],
        }.items():
            if value and account_data.get(key) != value:
                account_data[key] = value
                metadata_changed = True

        if changed:
            account_data["saved_at"] = datetime.now().isoformat(timespec="seconds")
            metadata_changed = True

        if metadata_changed:
            self.save_accounts(accounts)

        if changed and not silent:
            print(f"Updated saved login for account: {email}")
        return changed or metadata_changed

    def remove_account(self, account_key):
        accounts = self.get_accounts()
        if account_key in accounts:
            account_data = accounts[account_key]
            dirs_to_remove = [account_key]
            for legacy in account_data.get("legacy_names", []):
                if legacy and legacy not in dirs_to_remove:
                    dirs_to_remove.append(legacy)
            for dirname in dirs_to_remove:
                account_dir = self.accounts_dir / dirname
                if account_dir.exists():
                    shutil.rmtree(account_dir, onerror=self._remove_readonly)
            del accounts[account_key]
            self.save_accounts(accounts)
            print(f"Account '{account_key}' removed. / 账号 '{account_key}' 已删除。")
        else:
            print(f"Account '{account_key}' not found. / 未找到账号 '{account_key}'。")

    def clear_current_auth(self):
        auth_file = self._current_auth_path()
        backup_path = self._backup_current_auth("before-clean")
        if auth_file.exists():
            auth_file.unlink()
        if backup_path:
            print(f"Previous login backed up at: {backup_path}")
        print("Switched to Default (Clean) environment. / 已切换到默认 (干净) 环境。")
        self.refresh_codex_app()

    def get_usage_stats(self):
        """解析会话日志获取额度信息"""
        session_dir = Path.home() / ".codex" / "sessions"
        
        # 递归查找所有 rollout-*.jsonl 文件
        log_files = []
        for root, dirs, files in os.walk(session_dir):
            for f in files:
                if f.startswith("rollout-") and f.endswith(".jsonl"):
                    log_files.append(os.path.join(root, f))
        
        if not log_files:
            return "N/A"
        
        # 按修改时间排序，取最新的
        log_files.sort(key=os.path.getmtime, reverse=True)
        
        try:
            with open(log_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    return "N/A"
                
                # 从后往前找包含 rate_limits 的行
                for line in reversed(lines):
                    try:
                        data = json.loads(line.strip())
                        if data.get('type') == 'event_msg' and 'payload' in data:
                            payload = data['payload']
                            if payload.get('type') == 'token_count':
                                rate_limits = payload.get('rate_limits', {})
                                primary = rate_limits.get('primary', {})
                                secondary = rate_limits.get('secondary', {})
                                
                                limits = []
                                if primary:
                                    limits.append(primary)
                                if secondary:
                                    limits.append(secondary)

                                def label_for_window(minutes):
                                    if minutes is None:
                                        return "Unknown"
                                    if minutes >= 10080:
                                        return "Weekly"
                                    if 240 <= minutes <= 360:
                                        return "5h"
                                    return f"{minutes}m"

                                parts = []
                                for lim in limits:
                                    used = lim.get('used_percent', 0)
                                    if used is None:
                                        used = 0
                                    try:
                                        used = float(used)
                                    except Exception:
                                        used = 0
                                    minutes = lim.get('window_minutes')
                                    label = label_for_window(minutes)
                                    left = round(max(0.0, 100.0 - used), 1)
                                    resets_at = lim.get('resets_at')
                                    reset_text = "unknown"
                                    if isinstance(resets_at, (int, float)):
                                        try:
                                            reset_text = datetime.fromtimestamp(resets_at).strftime("%Y-%m-%d %H:%M")
                                        except Exception:
                                            reset_text = "unknown"
                                    parts.append(f"{label}: {left}% left (reset {reset_text})")

                                return " | ".join(parts) if parts else "N/A"
                    except:
                        continue
                return "N/A"
        except:
            return "Error parsing logs / 日志解析错误"

    def switch_account(self, email_or_fragment):
        self.sync_current_account(silent=False)
        accounts = self.get_accounts()
        
        matched_key = None
        needle = email_or_fragment.lower()
        for key, data in accounts.items():
            email = data.get("email", key)
            if needle in email.lower() or needle in key.lower():
                matched_key = key
                break
        
        if not matched_key:
            print(f"No account matched '{email_or_fragment}'. / 未找到匹配 '{email_or_fragment}' 的账号。")
            return
        
        account_data = accounts[matched_key]
        target_auth = self._account_auth_path(matched_key, account_data)
        
        if not target_auth.exists():
            print(f"No auth.json found for '{matched_key}'. / 账号 '{matched_key}' 未找到认证文件。")
            return

        self._warn_if_saved_auth_old(target_auth)
        
        codex_dir = self._codex_dir()
        target_path = codex_dir / self.AUTH_FILENAME
        backup_path = self._backup_current_auth(f"before-switch-{matched_key}")
        self._atomic_copy_file(target_auth, target_path)
        
        email = account_data.get('email', matched_key)
        plan = account_data.get('plan', 'Unknown')
        print(f"Successfully switched to account: {email} / 已成功切换至账号: {email}")
        print(f"  Plan: {plan}")
        if backup_path:
            print(f"Previous login backed up at: {backup_path}")
        self.refresh_codex_app()
        self._verify_auth_persisted(expected_email=email)

    def _warn_if_saved_auth_old(self, auth_path: Path, max_age_days: int = 14):
        try:
            auth_data = self._load_json(auth_path)
            last_refresh = auth_data.get("last_refresh")
            if not last_refresh:
                return
            normalized = last_refresh.replace("Z", "+00:00")
            if "." in normalized:
                head, tail = normalized.split(".", 1)
                if "+" in tail:
                    fraction, offset = tail.split("+", 1)
                    normalized = f"{head}.{fraction[:6]}+{offset}"
                elif "-" in tail:
                    fraction, offset = tail.rsplit("-", 1)
                    normalized = f"{head}.{fraction[:6]}-{offset}"
            refreshed_at = datetime.fromisoformat(normalized)
            if refreshed_at.tzinfo is None:
                refreshed_at = refreshed_at.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - refreshed_at.astimezone(timezone.utc)).days
            if age_days > max_age_days:
                print(f"Saved login for this account is {age_days} days old. If Codex asks to login, login once and add/switch this account again.")
        except Exception:
            return

    def refresh_codex_app(self):
        """提示用户手动重启 Codex，避免工具杀掉当前桌面端进程。"""
        print("账号文件已更新。工具不会启动、停止或修改 Codex/ChatGPT 桌面端。")
        print("请完全关闭并重新打开 Codex/ChatGPT 桌面端，让账号切换生效。")
        return False

    def _verify_auth_persisted(self, expected_email: str, wait_seconds: float = 1.5):
        if not expected_email:
            return
        try:
            time.sleep(wait_seconds)
        except Exception:
            pass
        current_email, _ = self.get_current_email_and_plan()
        if not current_email:
            return
        if current_email.lower() == expected_email.lower():
            return
        print("Detected auth.json was overwritten by desktop cache. Please close and reopen Codex desktop, then retry.")
