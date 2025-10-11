# ValueScan API 监听工具

监听 valuescan.io API 并将加密货币告警消息自动发送到 Telegram。

支持**有头模式**（显示浏览器）和**无头模式**（后台运行），适用于开发调试和服务器部署。

## ✨ 特性

- 🔄 自动监听 API 请求并实时推送
- 📱 支持 Telegram 消息推送
- 🖥️ 有头模式 - 显示浏览器窗口，方便调试和首次登录
- 🚀 无头模式 - 后台运行，适合服务器和长期运行
- 🌍 无头模式自动打开网站并监听
- 📊 显示 Chrome 进程 ID，便于管理
- 🔐 自动保持登录状态，共享用户数据
- 📝 完善的日志系统，支持日志轮转
- ⚡ 自动去重，避免重复通知

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install DrissionPage requests psutil
```

### 2. 配置文件

复制 `config.example.py` 为 `config.py` 并填写配置：

```bash
# Windows
copy config.example.py config.py

# Linux/macOS
cp config.example.py config.py
```

编辑 `config.py`，填入以下必要信息：
- `TELEGRAM_BOT_TOKEN`: Telegram Bot Token（从 @BotFather 获取）
- `TELEGRAM_CHAT_ID`: 你的 Telegram 用户 ID（从 @userinfobot 获取）
- `HEADLESS_MODE`: 选择运行模式（True=无头模式，False=有头模式）

### 3. 首次登录（重要）

无论后续使用哪种模式，**首次使用都必须用有头模式登录**：

```bash
# 1. 确保配置文件中 HEADLESS_MODE = False
# 2. 运行启动脚本
python start_with_chrome.py

# 3. 在打开的浏览器中登录 valuescan.io 账号
# 4. 登录成功后，按 Ctrl+C 停止程序
```

登录状态会自动保存在 `chrome-debug-profile` 目录中。

### 4. 日常使用

**方式一：通过配置文件控制**（推荐）

编辑 `config.py`：
```python
# 有头模式（显示浏览器）
HEADLESS_MODE = False

# 无头模式（后台运行）
HEADLESS_MODE = True
```

然后运行：
```bash
python start_with_chrome.py
```

**方式二：直接运行主程序**
```bash
python valuescan.py
```

## 📖 运行模式

### 🖥️ 有头模式（Headed Mode）

**适用场景**：
- ✅ 首次登录账号
- ✅ 调试和测试
- ✅ 需要查看浏览器状态

**特点**：
- 显示浏览器窗口
- 需要手动在浏览器中操作
- 占用较多资源

**启动方式**：
```bash
# config.py 中设置
HEADLESS_MODE = False

# 运行
python start_with_chrome.py
```

### 🚀 无头模式（Headless Mode）

**适用场景**：
- ✅ 服务器后台运行
- ✅ 长期7×24小时监控
- ✅ 节省系统资源
- ✅ VPS/云服务器部署

**特点**：
- 不显示浏览器窗口
- 自动打开 valuescan.io 网站
- 自动开始监听 API
- 显示 Chrome 进程 ID
- 资源占用低（节省 30-50% 内存）

**启动方式**：
```bash
# config.py 中设置
HEADLESS_MODE = True

# 运行
python start_with_chrome.py
```

**无头模式启动流程**：
1. 自动清理现有 Chrome 进程
2. 启动无头 Chrome 浏览器
3. 显示进程 ID
4. 自动打开 valuescan.io
5. 开始监听 API 请求
6. 自动捕获和推送消息

## 📊 模式对比

| 特性 | 有头模式 | 无头模式 |
|------|---------|----------|
| 显示浏览器窗口 | ✅ 是 | ❌ 否 |
| 资源占用 | 较高 | 较低 |
| 内存使用 | ~300-500 MB | ~150-250 MB |
| 可以手动登录 | ✅ 是 | ❌ 否（需已登录） |
| 适用场景 | 首次登录、调试 | 长期后台运行 |
| 服务器使用 | ⚠️ 需要图形界面 | ✅ 完美支持 |
| 自动打开网站 | ❌ 需手动 | ✅ 自动 |
| 进程ID显示 | ❌ 否 | ✅ 是 |

## ⚙️ 配置说明

### Telegram 配置
- **获取 Bot Token**: 在 Telegram 中找到 @BotFather，发送 `/newbot` 创建机器人
- **获取用户 ID**: 在 Telegram 中找到 @userinfobot，发送任意消息获取你的 ID
- **频道推送**: 如果要推送到频道，使用频道 ID（-100 开头的数字）

### 浏览器配置
- **CHROME_DEBUG_PORT**: Chrome 调试端口（默认 9222）
- **HEADLESS_MODE**: 运行模式（True=无头，False=有头）

### 日志配置
- **LOG_LEVEL**: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- **LOG_TO_FILE**: 是否输出到文件
- **LOG_FILE**: 日志文件路径
- **LOG_MAX_SIZE**: 单个日志文件最大大小（默认 10MB）
- **LOG_BACKUP_COUNT**: 保留的历史日志文件数量（默认 5 个）

### 消息类型
程序支持以下类型的告警消息：
- `100`: 下跌风险
- `108`: 资金异动
- `109`: 上下币公告
- `110`: Alpha
- `111`: 资金出逃
- `113`: FOMO
- `114`: 资金异常

## 📁 项目结构

```
valuescan/
├── valuescan.py              # 主程序入口
├── start_with_chrome.py      # 统一启动脚本（支持两种模式）
├── 启动.bat                 # Windows 快捷启动脚本
├── api_monitor.py            # API 监听模块（核心）
├── message_handler.py        # 消息处理模块
├── telegram.py               # Telegram 消息发送模块
├── kill_chrome.py            # Chrome 进程管理模块
├── logger.py                 # 日志工具模块
├── database.py               # 数据库模块
├── db_manager.py             # 数据库管理工具
├── config.py                 # 配置文件（需自行创建）
├── config.example.py         # 配置文件模板
├── requirements.txt          # 依赖包列表
├── README.md                 # 本文件
├── chrome-debug-profile/     # Chrome 用户数据目录
└── valuescan.db              # 数据库文件
```

## 🔧 高级功能

### 进程管理

**查看 Chrome 进程**：
```powershell
# Windows
tasklist | findstr chrome.exe

# 查看占用的端口
netstat -ano | findstr :9222
```

**手动关闭 Chrome**：
```bash
python kill_chrome.py
```

### 后台运行（Linux/macOS）

```bash
# 使用 nohup
nohup python start_with_chrome.py > output.log 2>&1 &

# 查看日志
tail -f valuescan.log

# 停止程序
ps aux | grep python
kill <PID>
```

### 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/valuescan.service`：

```ini
[Unit]
Description=ValueScan API Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/valuescan
ExecStart=/usr/bin/python3 start_with_chrome.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable valuescan
sudo systemctl start valuescan
sudo systemctl status valuescan
```

## 🧪 测试工具

### 测试 Telegram 功能
```bash
python test_telegram.py
```

### 测试日志功能
```bash
python test_logger.py
```

## 🔍 故障排查

### 无法启动 Chrome

**症状**：
```
错误: 启动浏览器失败
```

**解决方案**：
1. 确保已安装 Chrome 浏览器
2. 检查端口 9222 是否被占用
3. 确认有足够的系统权限
4. 尝试手动运行 `python kill_chrome.py` 清理进程

### 无法获取 API 数据

**症状**：
```
未捕获到任何请求
```

**解决方案**：
1. 检查是否已登录 valuescan.io 账号
2. 有头模式：手动在浏览器中访问网站
3. 无头模式：程序会自动打开网站，等待2-3秒
4. 检查 `API_PATH` 配置是否正确
5. 查看 `valuescan.log` 了解详细信息

### Telegram 消息发送失败

**解决方案**：
1. 检查 `TELEGRAM_BOT_TOKEN` 是否正确
2. 检查 `TELEGRAM_CHAT_ID` 是否正确
3. 确保网络可以访问 `api.telegram.org`
4. 运行 `python test_telegram.py` 测试连接
5. 检查 Bot 是否被封禁

### 无头模式登录状态丢失

**解决方案**：
1. Cookie 可能过期，重新用有头模式登录
2. 确保 `chrome-debug-profile` 目录完整
3. 不要手动删除该目录中的文件
4. 两种模式共享同一个用户目录

### 进程冲突

**症状**：
```
Handshake status 404 Not Found
```

**原因**：
同一个 Chrome 用户目录不能被多个进程同时使用

**解决方案**：
1. 无头模式会自动清理冲突进程
2. 不要同时运行两种模式
3. 手动运行 `python kill_chrome.py`
4. 重启计算机（最后手段）

## 💡 最佳实践

### 开发阶段
```bash
# 使用有头模式，方便调试
HEADLESS_MODE = False
python start_with_chrome.py
```

### 生产部署
```bash
# 使用无头模式，节省资源
HEADLESS_MODE = True
python start_with_chrome.py
```

### 服务器部署建议
1. ✅ 使用无头模式
2. ✅ 配置为系统服务（systemd）
3. ✅ 启用日志文件输出
4. ✅ 定期检查日志文件大小
5. ✅ 设置 Telegram 告警

## ⚠️ 注意事项

1. **配置文件安全**: 不要将包含真实 Token 的 `config.py` 提交到版本控制
2. **首次必须登录**: 无论使用哪种模式，首次都要用有头模式登录
3. **用户目录共享**: 有头和无头模式共享 `chrome-debug-profile` 目录
4. **不要同时运行**: 两种模式不能同时运行（会自动清理冲突）
5. **定期检查日志**: 日志文件会自动轮转，但建议定期检查

## 📄 许可

本项目仅供学习和个人使用。

## 🔗 相关链接

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [DrissionPage 文档](https://github.com/g1879/DrissionPage)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

---

**更新日期**: 2025-10-11  
**版本**: 2.0
