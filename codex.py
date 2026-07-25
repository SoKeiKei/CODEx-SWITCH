import sys
import os
from pathlib import Path
from bin.service import CodexService
from scripts.install import install

USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None

def _enable_ansi():
    if os.name == "nt":
        try:
            os.system("")
        except Exception:
            pass

def _style(text, *codes):
    if not USE_COLOR or not codes:
        return text
    return "\033[" + ";".join(codes) + "m" + text + "\033[0m"

def _banner():
    line = "+" + "-" * 50 + "+"
    print(_style(line, "36"))
    print(_style(f"| CODEx SWITCH {'v1.2.0':>34} |", "36", "1"))
    print(_style("| account switcher                                |", "36"))
    print(_style(line, "36"))

def _section(title):
    print(_style(title, "36", "1"))
    print(_style("-" * 50, "2"))

def check_installation():
    profile = Path.home() / ".zshrc" if os.name != 'nt' else Path.home() / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
    if profile.exists():
        with open(profile, 'r') as f:
            if "codex-switch" in f.read():
                return True
    return False

def interactive_menu():
    _enable_ansi()
    if not check_installation():
        print("Codex Switch is not installed in your shell profile. / Codex Switch 未在您的 Shell 配置文件中安装。")
        choice = input("Do you want to install it now? (y/n) / 是否现在安装？(y/n): ")
        if choice.lower() == 'y':
            install()
            return

    service = CodexService()
    while True:
        service.sync_current_account()
        # 获取当前账号详细信息
        current_info = service.get_current_account_info()
        usage = service.get_usage_stats()
        
        print("")
        _banner()
        print(f"\n{'='*50}")
        print("Current Account / 当前账号:")
        print(" Email / 邮箱            |  Plan / 订阅 | Usage / 额度")
        print(
            f" {current_info['email']:<23} |  "
            f"{current_info['plan']:<12}| "
            f"{usage}"
        )
        print(f"{'='*50}")
        print("")
        print("[1] 查看账号 / List Accounts")
        print("[2] 添加账号 / Add Account")
        print("[3] 删除账号 / Remove Account")
        print("[4] 切换账号 / Switch Account")
        print("[q] 退出程序 / Exit")
        print("")
        
        choice = input("Select an option / 请选择操作: ")
        
        if choice == '1':
            accounts = service.get_accounts()
            if not accounts:
                print("No accounts found / 未找到账号")
            else:
                _section("Account List")
                print(f"\n{'='*60}")
                print(f"{'Email/邮箱':<32} {'Plan/订阅':<10}")
                print(f"{'-'*60}")
                for email_key, data in accounts.items():
                    email = data.get('email', 'Unknown')
                    plan = data.get('plan', 'Unknown')
                    # 标记当前账号
                    marker = " *" if email.lower() == current_info['email'].lower() else ""
                    print(f"{email_key:<32} {plan:<10}{marker}")
                print(f"{'='*60}")
                print("* = Current account / * = 当前账号")
        elif choice == '2':
            service.add_account()
        elif choice == '3':
            accounts = service.get_accounts()
            if not accounts:
                print("No accounts found / 未找到账号")
                continue
            
            _section("Remove Account")
            print("\nSelect account to remove / 选择要删除的账号:")
            account_keys = list(accounts.keys())
            for i, email_key in enumerate(account_keys):
                plan = accounts[email_key].get('plan', 'Unknown')
                print(f"  {i+1}. {email_key} ({plan})")
            print("  q. Cancel / 取消")
            
            idx = input("Select index / 选择序号: ")
            if idx.strip().lower() == 'q':
                print("Canceled. / 已取消。")
                continue
            if idx.isdigit() and 1 <= int(idx) <= len(account_keys):
                service.remove_account(account_keys[int(idx)-1])
            else:
                print("Invalid choice / 无效选择")
        elif choice == '4':
            accounts = service.get_accounts()
            
            _section("Switch Account")
            print("\nSelect account to switch / 选择要切换的账号:")
            print("  0. Default (Clean) / 默认 (干净环境)")
            account_keys = list(accounts.keys())
            for i, email_key in enumerate(account_keys):
                plan = accounts[email_key].get('plan', 'Unknown')
                print(f"  {i+1}. {email_key} ({plan})")
            print("  q. Cancel / 取消")
            
            idx = input("Select index / 选择序号: ")
            if idx == '0':
                service.sync_current_account(silent=False)
                service.clear_current_auth()
                print("You can now login with a new account. / 您现在可以登录新账号。")
            elif idx.strip().lower() == 'q':
                print("Canceled. / 已取消。")
                continue
            elif idx.isdigit() and 1 <= int(idx) <= len(account_keys):
                service.switch_account(account_keys[int(idx)-1])
            else:
                print("Invalid choice / 无效选择")
        elif choice.strip().lower() == 'q':
            print("Goodbye / 再见")
            break
        else:
            print("Invalid choice / 无效选择")

def main():
    interactive_menu()

if __name__ == "__main__":
    main()
