# CODEx SWITCH
[中文](#中文) | [English](#english)

---

## 中文

简洁、跨平台的 Codex 多账号切换命令行工具。当前版本：`v1.2.0`。

### ⚙️ 环境依赖
- 本工具基于 Python 编写，运行前需确保已安装 **[Python 3.10+](https://www.python.org/downloads/)**。
- 无第三方依赖库，无需额外执行 `pip install`，下载即用。

### ✨ 核心功能
- **账号快照**：保存每个账号的本地登录文件，并在启动或切换前自动同步当前账号的最新状态。
- **智能识别**：自动从 JWT 解析邮箱并识别当前账号。
- **状态展示**：直观显示订阅类型 (Team/Plus/Pro/Free) 及剩余额度。
- **极简交互**：双语菜单，操作简单直观。
- **跨平台**：提供 Windows/macOS/Linux 一键运行脚本。
- **安全切换**：切换前自动备份当前登录文件，切换后提示手动重开 Codex/ChatGPT 桌面端；工具不启动、不停止、不修改桌面端程序。

### 🚀 快速开始

#### 方式 1：一键自动安装 (推荐)
能自动检测环境、下载工具，并为您配置好系统全局命令 `codex-switch`。
* **Windows (PowerShell)**:
  ```powershell
  irm https://raw.githubusercontent.com/SoKeiKei/CODEx-SWITCH/master/install.ps1 | iex
  ```
* **macOS / Linux (Terminal)**:
  ```bash
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/SoKeiKei/CODEx-SWITCH/master/install.sh)"
  ```
> 💡 **安装成功后**，只需在任何终端输入 `codex-switch` 即可随时召唤切换器！

#### 方式 2：本地克隆运行 (绿色免安装)
如果你不想使用自动脚本，可以直接下载源码在本地运行：
1. **获取代码**：
   ```bash
   git clone https://github.com/SoKeiKei/CODEx-SWITCH.git
   cd CODEx-SWITCH
   ```
   *(或者在网页端点击 `Code` -> `Download ZIP` 解压)*
2. **运行工具**：
   - **Windows**: 双击运行目录下的 `run.bat`，或者在终端执行 `py -3 codex.py`
   - **macOS / Linux**: 在终端执行 `chmod +x run.sh && ./run.sh`，或者执行 `python3 codex.py`

### 📖 使用说明

#### 💡 如何登录并保存新账号？（重要指引）
1. **保存当前账号**：请**不要**在 Codex 软件内点击“退出登录(Logout)”。而是先运行本工具，按 `2` 将当前已登录的账号添加保存。
2. **清空登录状态**：运行本工具，按 `4` (切换账号)，然后选择 `0` (默认/干净状态)。工具会先备份当前登录文件。
3. **登录新账号**：完全关闭并重新打开 Codex/ChatGPT 桌面端，此时软件会提示重新登录。登录你的新账号。
4. **保存新账号**：再次运行本工具，按 `2` 把刚登录的新账号也添加进来。
5. **自由切换**：以后可以通过按 `4` 在这些收录的账号间切换。切换后请完全关闭并重新打开 Codex/ChatGPT 桌面端，让账号生效。

### 📁 目录结构

```text
.codex/
└── codex-switch/           # 账号存储目录
    ├── user@example.com/auth.json
    ├── backups/            # 切换或清空前自动保存的备份
    └── ...

codex-switch/
├── codex.py                # 主程序 CLI 入口
├── run.bat / run.sh        # 本地运行脚本
├── bin/                    # 核心逻辑与业务代码
├── config/accounts.json    # 账号列表配置
└── scripts/install.py      # 本地命令配置脚本
```

### 💻 界面预览

```text
+--------------------------------------------------+
| CODEx SWITCH                             v1.2.0  |
| account switcher                                 |
+--------------------------------------------------+
Current Account / 当前账号:
 Email / 邮箱            |  Plan / 订阅 | Usage / 额度
 user@example.com        |  free        | Weekly: 90.0% left (reset 2026-03-15)
==================================================

[1] 查看账号 / List Accounts
[2] 添加账号 / Add Account
[3] 删除账号 / Remove Account
[4] 切换账号 / Switch Account
[q] 退出程序 / Exit
```

### ⚠️ 注意事项
- 额度数据读取自本地 `~/.codex/sessions` 日志，显示可能存在少许延迟。
- 切换账号只会更新 `~/.codex/auth.json`，不会启动、停止、锁定或修改 Codex/ChatGPT 桌面端。
- 如果某个账号保存时间太久，可能需要重新登录一次；登录后再次保存即可继续切换。
- 工具**不上传任何数据**，所有数据及凭证仅在本地保存。

### 📄 许可证
本项目采用 [MIT License](LICENSE) 许可证。

---

## English

A lightweight, cross-platform CLI for managing and switching multiple Codex accounts. Current version: `v1.2.0`.

### ⚙️ Prerequisites
- This tool is written in Python. You must have **[Python 3.10+](https://www.python.org/downloads/)** installed before running it.
- No third-party dependencies are required (`pip install` is not needed), just download and run.

### ✨ Core Features
- **Account Snapshots**: Stores each account's local login file and syncs the current account before listing or switching.
- **Auto Parse**: Automatically parses email from JWT to identify the current account.
- **Status Display**: Intuitively shows subscription plan (Team/Plus/Pro/Free) and remaining usage.
- **Interactive UI**: Bilingual menu with simple, intuitive operations.
- **Cross-platform**: Provides one-click run scripts for Windows/macOS/Linux.
- **Safe Switching**: Backs up the current login file before switching and asks you to reopen Codex/ChatGPT Desktop; it does not start, stop, lock, or modify the desktop app.

### 🚀 Quick Start

#### Method 1: One-Click Install (Recommended)
Automatically detects your environment, downloads the tool, and sets up a global `codex-switch` command.
* **Windows (PowerShell)**:
  ```powershell
  irm https://raw.githubusercontent.com/SoKeiKei/CODEx-SWITCH/master/install.ps1 | iex
  ```
* **macOS / Linux (Terminal)**:
  ```bash
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/SoKeiKei/CODEx-SWITCH/master/install.sh)"
  ```
> 💡 **After successful installation**, simply type `codex-switch` in your terminal anytime to launch the switcher!

#### Method 2: Manual Clone & Run (Portable)
If you prefer not to use the automated scripts, you can download the source and run it locally:
1. **Get the code**:
   ```bash
   git clone https://github.com/SoKeiKei/CODEx-SWITCH.git
   cd CODEx-SWITCH
   ```
   *(Or click `Code` -> `Download ZIP` on the web interface to extract horizontally)*
2. **Run the tool**:
   - **Windows**: Double-click `run.bat` in the directory, or run `py -3 codex.py` in your terminal.
   - **macOS / Linux**: Run `chmod +x run.sh && ./run.sh` in your terminal, or run `python3 codex.py`.

### 📖 Usage

#### 💡 How to login and save a new account? (Important Guide)
1. **Save current account**: Please **DO NOT** click "Logout" inside the Codex app. Instead, run this tool first and press `2` to save the currently logged-in account by email.
2. **Clear auth state**: Run this tool, press `4` (Switch Account), and select `0` (Default/Clean state). The tool backs up the current login file first.
3. **Login new account**: Fully close and reopen Codex/ChatGPT Desktop. It will now ask you to log in. Log into your new account.
4. **Save new account**: Run this tool again and press `2` to save the newly logged-in account.
5. **Switch freely**: From now on, press `4` to switch between saved accounts. After switching, fully close and reopen Codex/ChatGPT Desktop to apply the account.

*(After switching accounts, the tool writes the local login file and asks you to fully close and reopen Codex/ChatGPT Desktop. It does not start, stop, lock, or modify the desktop app.)*

### 📁 Directory Layout

```text
.codex/
└── codex-switch/           # Account storage
    ├── user@example.com/auth.json
    ├── backups/            # Automatic backups before switching or clearing auth
    └── ...

codex-switch/
├── codex.py                # Main CLI entry point
├── run.bat / run.sh        # One-click runners
├── bin/                    # Core logic and business code
├── config/accounts.json    # Account list configuration
└── scripts/install.py      # Command install script
```

### 💻 UI Preview

```text
+--------------------------------------------------+
| CODEx SWITCH                             v1.2.0  |
| account switcher                                 |
+--------------------------------------------------+
Current Account / 当前账号:
 Email / 邮箱            |  Plan / 订阅 | Usage / 额度
 user@example.com        |  free        | Weekly: 90.0% left (reset 2026-03-15)
==================================================

[1] 查看账号 / List Accounts
[2] 添加账号 / Add Account
[3] 删除账号 / Remove Account
[4] 切换账号 / Switch Account
[q] 退出程序 / Exit
```

### ⚠️ Notes
- Usage data is read from local `~/.codex/sessions` logs; display might lag slightly.
- Switching accounts only updates `~/.codex/auth.json`; the tool does not start, stop, lock, or modify Codex/ChatGPT Desktop.
- If a saved account is too old, you may need to log in once again and save it again.
- The tool **does not upload any data**; all data and credentials belong firmly on local storage.

### 📄 License
This project is licensed under the [MIT License](LICENSE).
