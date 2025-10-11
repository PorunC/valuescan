# 跨平台支持说明

ValueScan 已实现完整的跨平台支持，可在 Windows、Linux 和 macOS 上无缝运行。

## ✨ 自动化特性

### 1. 自动平台检测

程序会自动检测运行平台并使用对应的系统命令：

```python
system = platform.system()  # 'Windows', 'Linux', 或 'Darwin' (macOS)
```

### 2. 自动 Chrome 路径检测

程序会根据平台自动搜索 Chrome/Chromium 的常见安装位置：

**Windows**:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
- `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`

**Linux**:
- `/usr/bin/google-chrome`
- `/usr/bin/google-chrome-stable`
- `/usr/bin/chromium-browser`
- `/usr/bin/chromium`
- `/snap/bin/chromium`

**macOS**:
- `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- `/Applications/Chromium.app/Contents/MacOS/Chromium`

### 3. 自动进程管理

**Windows**:
```powershell
taskkill /F /IM chrome.exe /T
```

**Linux/macOS**:
```bash
pkill -9 -f 'chrome|chromium'
```

### 4. 自动进程 ID 获取

支持 `psutil` 库（推荐）或系统命令：

**Windows**:
```powershell
tasklist /FI "IMAGENAME eq chrome.exe"
```

**Linux/macOS**:
```bash
pgrep -f chrome-debug-profile
```

## 📦 依赖要求

### 必需
- Python 3.8+
- DrissionPage
- requests

### 推荐（用于进程管理）
- psutil (跨平台)

```bash
pip install psutil
```

## 🚀 使用方式

### 相同的代码，任何平台

**Windows**:
```powershell
python start_with_chrome.py
```

**Linux**:
```bash
python3 start_with_chrome.py
```

**macOS**:
```bash
python3 start_with_chrome.py
```

### 配置文件通用

`config.py` 在所有平台上完全相同：

```python
HEADLESS_MODE = True  # 或 False
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

### Chrome 用户数据通用

`chrome-debug-profile` 目录可以在平台间共享（需要重新登录）：

```bash
# 从 Windows 传输到 Linux
scp -r chrome-debug-profile user@linux-server:~/valuescan/

# 从 Linux 传输到 macOS
rsync -av chrome-debug-profile user@mac:~/valuescan/
```

## 🔧 平台特定说明

### Windows

**优势**:
- 图形界面，方便首次登录
- 原生支持，无需额外配置

**注意**:
- 路径使用反斜杠 `\`
- 使用 `python` 命令
- 编码可能是 GBK

### Linux

**优势**:
- 完美支持无头模式
- 适合服务器部署
- 资源占用低

**注意**:
- 路径使用正斜杠 `/`
- 使用 `python3` 命令
- 需要安装 Chromium 或 Chrome
- 可能需要虚拟显示 (Xvfb)

**安装 Chromium**:
```bash
# Ubuntu/Debian
sudo apt install chromium-browser

# CentOS/RHEL
sudo yum install chromium
```

### macOS

**优势**:
- Unix-like 系统，类似 Linux
- 有图形界面，方便登录

**注意**:
- 路径使用正斜杠 `/`
- 使用 `python3` 命令
- Chrome 安装在 `/Applications`
- 可能需要授予权限

## 🎯 最佳实践

### 开发环境

**推荐**: Windows 或 macOS
- 有图形界面，方便调试
- 容易进行首次登录
- 可视化测试

### 生产环境

**推荐**: Linux
- 稳定性高
- 资源占用低
- 便于自动化部署
- 完美支持无头模式

### 混合使用

1. **在 Windows 上开发和登录**
   ```powershell
   # 有头模式登录
   python start_with_chrome.py
   ```

2. **传输到 Linux 服务器运行**
   ```bash
   # 传输代码和用户数据
   scp -r valuescan user@server:~/
   
   # 在服务器上运行（无头模式）
   ssh user@server
   cd valuescan
   python3 start_with_chrome.py
   ```

## 📊 平台对比

| 特性 | Windows | Linux | macOS |
|------|---------|-------|-------|
| 有头模式 | ✅ 完美 | ⚠️ 需要 X11 | ✅ 完美 |
| 无头模式 | ✅ 支持 | ✅ 完美 | ✅ 支持 |
| 首次登录 | ✅ 简单 | ⚠️ 需要 VNC/X11 | ✅ 简单 |
| 服务器部署 | ⚠️ 需要 RDP | ✅ 完美 | ⚠️ 较少使用 |
| 资源占用 | 中等 | 低 | 中等 |
| 推荐用途 | 开发/测试 | 生产部署 | 开发/测试 |

## 🔍 故障排查

### 问题 1: 找不到 Chrome

**症状**:
```
❌ 未找到 Chrome 浏览器
```

**解决方案**:

**Windows**:
```powershell
# 检查是否安装
Get-Command chrome

# 查找路径
where.exe chrome
```

**Linux**:
```bash
# 检查是否安装
which google-chrome
which chromium-browser

# 安装
sudo apt install chromium-browser
```

**macOS**:
```bash
# 检查是否安装
ls -la "/Applications/Google Chrome.app"

# 下载安装
# 访问 https://www.google.com/chrome/
```

### 问题 2: 进程管理失败

**症状**:
```
清理 Chrome 进程时出现问题
```

**解决方案**:

**Windows**:
```powershell
# 手动查看进程
tasklist | findstr chrome

# 手动关闭
taskkill /F /IM chrome.exe /T
```

**Linux/macOS**:
```bash
# 手动查看进程
ps aux | grep chrome

# 手动关闭
pkill -9 chrome
```

### 问题 3: 权限不足

**症状**:
```
Permission denied
```

**解决方案**:

**Linux/macOS**:
```bash
# 给予执行权限
chmod +x start_with_chrome.py
chmod +x *.py

# 确保目录可写
chmod -R 755 chrome-debug-profile/
```

## 💡 技术实现

### 平台检测

```python
import platform

system = platform.system()
# 返回: 'Windows', 'Linux', 或 'Darwin'
```

### 条件执行

```python
if system == "Windows":
    # Windows 特定代码
    subprocess.run(['taskkill', ...])
elif system in ["Linux", "Darwin"]:
    # Unix-like 系统代码
    subprocess.run(['pkill', ...])
```

### 路径处理

```python
import os

# 自动处理路径分隔符
path = os.path.join('chrome-debug-profile', 'Default')

# 展开用户目录
home = os.path.expanduser('~')

# 展开环境变量
localappdata = os.path.expandvars('%LOCALAPPDATA%')
```

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [LINUX_DEPLOYMENT.md](LINUX_DEPLOYMENT.md) - Linux 部署详细指南
- [requirements.txt](requirements.txt) - Python 依赖列表

---

**更新时间**: 2025-10-11  
**版本**: 2.0
