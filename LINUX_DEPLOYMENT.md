# Linux 服务器部署指南

本指南详细说明如何将 ValueScan 从 Windows 迁移到 Linux 服务器运行。

## 📋 目录

- [系统要求](#系统要求)
- [安装依赖](#安装依赖)
- [配置文件迁移](#配置文件迁移)
- [Chrome/Chromium 安装](#chromechromium-安装)
- [首次登录](#首次登录)
- [后台运行](#后台运行)
- [systemd 服务配置](#systemd-服务配置)
- [常见问题](#常见问题)

## 🖥️ 系统要求

### 推荐配置
- **操作系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **内存**: 至少 2GB RAM（推荐 4GB）
- **CPU**: 2 核心以上
- **磁盘**: 至少 2GB 可用空间
- **Python**: Python 3.8+

### 网络要求
- 能访问 valuescan.io
- 能访问 Telegram API (api.telegram.org)
- 开放必要的出站端口（HTTP/HTTPS）

## 📦 安装依赖

### 1. 更新系统

```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. 安装 Python 和 pip

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install -y python3 python3-pip

# 验证安装
python3 --version
pip3 --version
```

### 3. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt install -y \
    wget \
    curl \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils

# CentOS/RHEL
sudo yum install -y \
    wget \
    curl \
    unzip \
    liberation-fonts \
    alsa-lib \
    atk \
    at-spi2-atk \
    cups-libs \
    dbus-libs \
    libdrm \
    libXcomposite \
    libXdamage \
    libXfixes \
    libXrandr \
    gtk3 \
    nss
```

## 🌐 Chrome/Chromium 安装

Linux 上推荐使用 Chromium（开源版本）或 Chrome 浏览器。

### 方案 1: 安装 Chromium（推荐）

```bash
# Ubuntu/Debian
sudo apt install -y chromium-browser

# 或者使用 snap
sudo snap install chromium

# 验证安装
chromium-browser --version
# 或
chromium --version

# 查找 Chromium 路径
which chromium-browser
which chromium
```

### 方案 2: 安装 Google Chrome

```bash
# Ubuntu/Debian
# 1. 下载 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 2. 安装
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 3. 验证
google-chrome --version

# 4. 查找路径
which google-chrome
```

```bash
# CentOS/RHEL
# 1. 下载 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

# 2. 安装
sudo yum localinstall -y google-chrome-stable_current_x86_64.rpm

# 3. 验证
google-chrome --version
```

### 方案 3: 使用 Playwright 的 Chromium（最简单）

```bash
# 安装 playwright
pip3 install playwright

# 自动下载 Chromium
playwright install chromium

# Chromium 会被下载到 ~/.cache/ms-playwright/
```

## 🔧 配置文件迁移

### 1. 传输项目文件

从 Windows 传输到 Linux：

```bash
# 方法1: 使用 scp（从 Windows PowerShell 运行）
scp -r E:\Code\valuescan user@your-server-ip:/home/user/

# 方法2: 使用 git
# 在 Linux 服务器上
git clone https://github.com/your-username/valuescan.git
cd valuescan
```

### 2. 创建虚拟环境（推荐）

```bash
cd /home/user/valuescan

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 config.py

```bash
# 复制配置文件模板
cp config.example.py config.py

# 编辑配置
nano config.py
# 或
vi config.py
```

**重要配置项**：

```python
# 设置为无头模式（必须）
HEADLESS_MODE = True

# Telegram 配置
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Chrome 调试端口
CHROME_DEBUG_PORT = 9222
```

### 4. Chrome 路径配置（自动检测）

**✅ 无需手动配置！** 程序已支持跨平台自动检测：

- **Windows**: 自动检测 Program Files、LocalAppData 等路径
- **Linux**: 自动检测 /usr/bin/google-chrome、chromium-browser 等
- **macOS**: 自动检测 /Applications 下的 Chrome

程序会自动：
1. 检测当前操作系统
2. 遍历对应平台的常见 Chrome 路径
3. 自动使用找到的第一个可用路径

**手动指定路径**（仅在自动检测失败时）：

如果自动检测失败，可以在启动时通过环境变量指定：

```bash
# Linux 示例
export CHROME_PATH="/usr/bin/chromium-browser"
python3 start_with_chrome.py
```

或者直接修改 `api_monitor.py` 的 `_get_chrome_paths()` 函数添加你的路径。

## 🔑 首次登录

Linux 服务器通常没有图形界面，首次登录有两种方案：

### 方案 1: 在本地 Windows 登录后传输

**推荐方式**，最简单：

```bash
# 1. 在 Windows 上用有头模式登录
python start_with_chrome.py
# 在浏览器中登录 valuescan.io

# 2. 停止程序后，将 chrome-debug-profile 目录传输到 Linux
# 在 Windows PowerShell 中：
scp -r E:\Code\valuescan\chrome-debug-profile user@your-server-ip:/home/user/valuescan/

# 3. 在 Linux 上验证
ls -la /home/user/valuescan/chrome-debug-profile/
```

### 方案 2: 在 Linux 上使用 X11 转发

如果必须在 Linux 上登录：

```bash
# 1. 在本地启用 X11 转发（SSH 连接时）
ssh -X user@your-server-ip

# 2. 安装 X11 支持
sudo apt install -y xauth xvfb

# 3. 设置显示
export DISPLAY=:0

# 4. 临时启用有头模式
# 编辑 config.py: HEADLESS_MODE = False
python3 start_with_chrome.py

# 5. 登录后，改回无头模式
# 编辑 config.py: HEADLESS_MODE = True
```

### 方案 3: 使用 VNC（图形界面）

如果服务器支持 VNC：

```bash
# 1. 安装桌面环境和 VNC
sudo apt install -y xfce4 xfce4-goodies tightvncserver

# 2. 启动 VNC
vncserver :1

# 3. 通过 VNC 客户端连接
# 4. 在图形界面中运行有头模式登录
```

## 🚀 后台运行

### 方法 1: 使用 nohup

```bash
# 激活虚拟环境
source venv/bin/activate

# 后台运行
nohup python3 start_with_chrome.py > output.log 2>&1 &

# 查看进程
ps aux | grep python

# 查看日志
tail -f valuescan.log
tail -f output.log

# 停止程序
ps aux | grep python
kill <PID>
```

### 方法 2: 使用 screen

```bash
# 安装 screen
sudo apt install -y screen

# 创建新 session
screen -S valuescan

# 在 screen 中运行
source venv/bin/activate
python3 start_with_chrome.py

# 断开（保持运行）: Ctrl+A 然后 D

# 重新连接
screen -r valuescan

# 查看所有 session
screen -ls

# 杀死 session
screen -X -S valuescan quit
```

### 方法 3: 使用 tmux

```bash
# 安装 tmux
sudo apt install -y tmux

# 创建新 session
tmux new -s valuescan

# 在 tmux 中运行
source venv/bin/activate
python3 start_with_chrome.py

# 断开: Ctrl+B 然后 D

# 重新连接
tmux attach -t valuescan

# 列出 session
tmux ls

# 杀死 session
tmux kill-session -t valuescan
```

## 🔧 systemd 服务配置

### 创建服务文件

```bash
sudo nano /etc/systemd/system/valuescan.service
```

**服务配置内容**：

```ini
[Unit]
Description=ValueScan API Monitor
After=network.target

[Service]
Type=simple
User=your_username
Group=your_username
WorkingDirectory=/home/your_username/valuescan
Environment="PATH=/home/your_username/valuescan/venv/bin"
ExecStart=/home/your_username/valuescan/venv/bin/python3 start_with_chrome.py
Restart=always
RestartSec=10
StandardOutput=append:/home/your_username/valuescan/output.log
StandardError=append:/home/your_username/valuescan/error.log

# 环境变量
Environment="DISPLAY=:99"
Environment="HEADLESS=true"

[Install]
WantedBy=multi-user.target
```

### 启动和管理服务

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable valuescan

# 启动服务
sudo systemctl start valuescan

# 查看状态
sudo systemctl status valuescan

# 停止服务
sudo systemctl stop valuescan

# 重启服务
sudo systemctl restart valuescan

# 查看日志
sudo journalctl -u valuescan -f
sudo journalctl -u valuescan --since today
sudo journalctl -u valuescan --since "1 hour ago"

# 禁用服务
sudo systemctl disable valuescan
```

## 📊 监控和维护

### 1. 查看日志

```bash
# 程序日志
tail -f /home/user/valuescan/valuescan.log

# systemd 日志
sudo journalctl -u valuescan -f

# 查看最近 100 行
tail -n 100 valuescan.log
```

### 2. 监控进程

```bash
# 查看 Python 进程
ps aux | grep python

# 查看 Chrome 进程
ps aux | grep chrome

# 查看资源占用
top -p $(pgrep -f "python3 start_with_chrome.py")

# 或使用 htop
htop -p $(pgrep -f "python3 start_with_chrome.py")
```

### 3. 定时任务检查

创建检查脚本 `check_valuescan.sh`：

```bash
#!/bin/bash

# 检查进程是否运行
if ! pgrep -f "python3 start_with_chrome.py" > /dev/null; then
    echo "$(date): ValueScan is not running, restarting..."
    cd /home/user/valuescan
    source venv/bin/activate
    nohup python3 start_with_chrome.py > output.log 2>&1 &
fi
```

添加到 crontab：

```bash
# 编辑 crontab
crontab -e

# 每 5 分钟检查一次
*/5 * * * * /home/user/valuescan/check_valuescan.sh >> /home/user/valuescan/check.log 2>&1
```

## ⚠️ 注意事项

### 1. 权限问题

```bash
# 确保文件有执行权限
chmod +x start_with_chrome.py

# 确保 chrome-debug-profile 目录可写
chmod -R 755 chrome-debug-profile/

# 如果使用 systemd，确保用户有权限
sudo chown -R your_username:your_username /home/your_username/valuescan
```

### 2. 防火墙配置

```bash
# 如果有防火墙，确保出站流量畅通
# Ubuntu/Debian (ufw)
sudo ufw allow out to any port 443  # HTTPS
sudo ufw allow out to any port 80   # HTTP

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. 时区设置

```bash
# 查看当前时区
timedatectl

# 设置时区
sudo timedatectl set-timezone Asia/Shanghai

# 或
sudo ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

### 4. 文件路径差异

| Windows | Linux |
|---------|-------|
| `E:\Code\valuescan` | `/home/user/valuescan` |
| `.\chrome-debug-profile` | `./chrome-debug-profile` |
| `\` (路径分隔符) | `/` (路径分隔符) |
| `python` | `python3` |
| `pip` | `pip3` |

### 5. 字符编码

```bash
# 确保使用 UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 在 systemd 服务中添加
Environment="LANG=en_US.UTF-8"
Environment="LC_ALL=en_US.UTF-8"
```

## 🔍 常见问题

### 1. Chrome 启动失败

**错误**: `Failed to launch chrome!`

**解决方案**:
```bash
# 检查 Chrome 是否安装
which chromium-browser
which google-chrome

# 手动测试 Chrome
chromium-browser --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com

# 如果缺少依赖
ldd /usr/bin/chromium-browser | grep "not found"
```

### 2. 内存不足

**症状**: Chrome 崩溃或 OOM killer 杀死进程

**解决方案**:
```bash
# 检查内存使用
free -h
top

# 添加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. 显示相关错误

**错误**: `No usable sandbox!` 或 `Display not found`

**解决方案**:
```bash
# 使用 --no-sandbox 参数（已在代码中添加）
# 或安装虚拟显示
sudo apt install -y xvfb

# 启动虚拟显示
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

### 4. 无法访问 Telegram API

**解决方案**:
```bash
# 测试连接
curl -I https://api.telegram.org

# 如果需要代理
export HTTP_PROXY=http://proxy-server:port
export HTTPS_PROXY=http://proxy-server:port

# 在 Python 中使用代理（修改 telegram.py）
proxies = {
    'http': 'http://proxy-server:port',
    'https': 'http://proxy-server:port'
}
```

### 5. Cookie 丢失或过期

**解决方案**:
```bash
# 检查 chrome-debug-profile 目录
ls -la chrome-debug-profile/

# 重新传输目录
scp -r user@windows-machine:/path/to/chrome-debug-profile ./

# 或重新登录（使用 VNC/X11）
```

## 📚 快速部署脚本

创建一键部署脚本 `deploy.sh`：

```bash
#!/bin/bash

echo "=== ValueScan Linux 部署脚本 ==="

# 1. 更新系统
echo "1. 更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
echo "2. 安装系统依赖..."
sudo apt install -y python3 python3-pip python3-venv chromium-browser

# 3. 创建虚拟环境
echo "3. 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 4. 安装 Python 包
echo "4. 安装 Python 依赖..."
pip install -r requirements.txt

# 5. 配置文件
echo "5. 创建配置文件..."
if [ ! -f config.py ]; then
    cp config.example.py config.py
    echo "请编辑 config.py 填入你的配置"
fi

# 6. 创建 systemd 服务
echo "6. 创建 systemd 服务..."
cat > /tmp/valuescan.service <<EOF
[Unit]
Description=ValueScan API Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python3 start_with_chrome.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/valuescan.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "=== 部署完成 ==="
echo "下一步："
echo "1. 编辑 config.py"
echo "2. 传输 chrome-debug-profile 目录（如果从 Windows 迁移）"
echo "3. 启动服务: sudo systemctl start valuescan"
```

运行部署脚本：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 📖 完整迁移流程示例

```bash
# === 在 Windows 上 ===
# 1. 提交代码到 git
git add -A
git commit -m "准备迁移到 Linux"
git push

# 2. 打包 chrome-debug-profile
tar -czf chrome-profile.tar.gz chrome-debug-profile/

# === 在 Linux 服务器上 ===
# 1. 克隆代码
git clone https://github.com/your-username/valuescan.git
cd valuescan

# 2. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 传输 Chrome 配置（从 Windows）
scp user@windows-machine:/path/to/chrome-profile.tar.gz ./
tar -xzf chrome-profile.tar.gz

# 4. 配置
nano config.py  # 修改配置，设置 HEADLESS_MODE = True

# 5. 测试运行
source venv/bin/activate
python3 start_with_chrome.py
# Ctrl+C 停止测试

# 6. 启动服务
sudo systemctl enable valuescan
sudo systemctl start valuescan
sudo systemctl status valuescan

# 7. 查看日志
tail -f valuescan.log
```

## 🎯 总结

### 关键步骤
1. ✅ 安装 Chromium/Chrome
2. ✅ 配置 Python 环境
3. ✅ 传输 chrome-debug-profile
4. ✅ 设置 HEADLESS_MODE = True
5. ✅ 使用 systemd 守护进程
6. ✅ 配置日志和监控

### 推荐配置
- 使用 Chromium（开源，更适合服务器）
- 使用 systemd 管理服务
- 启用日志轮转
- 配置监控和告警
- 定期备份 chrome-debug-profile

---

**更新时间**: 2025-10-11  
**适用版本**: v2.0+
