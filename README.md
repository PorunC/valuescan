# ValueScan API 监听工具

监听 valuescan.io API 并将加密货币告警消息自动发送到 Telegram。

## 📁 项目结构

```
valuescan/
├── valuescan.py           # 主程序入口
├── start_with_chrome.py   # 启动脚本（自动管理 Chrome）
├── 启动.bat              # Windows 快捷启动脚本
├── kill_chrome.py         # Chrome 进程管理模块
├── config.py              # 配置文件（需自行创建）
├── config.example.py      # 配置文件模板
├── logger.py              # 日志工具模块
├── telegram.py            # Telegram 消息发送模块
├── message_handler.py     # 消息处理模块
├── api_monitor.py         # API 监听模块
├── test_logger.py         # 日志测试脚本
└── test_telegram.py       # Telegram 测试脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install DrissionPage requests
```

### 2. 配置文件

复制 `config.example.py` 为 `config.py` 并填写配置：

```bash
cp config.example.py config.py
```

编辑 `config.py`，填入以下必要信息：
- `TELEGRAM_BOT_TOKEN`: Telegram Bot Token（从 @BotFather 获取）
- `TELEGRAM_CHAT_ID`: 你的 Telegram 用户 ID（从 @userinfobot 获取）

### 3. 运行程序（一键启动）

**Windows 用户**：双击 `启动.bat` 文件

**或使用命令行**：
```bash
python start_with_chrome.py
```

**启动脚本会自动完成以下操作：**
1. ✅ 关闭所有现有的 Chrome 进程
2. ✅ 以调试模式启动 Chrome（使用当前目录下的 `chrome-debug-profile` 作为用户数据）
3. ✅ 启动 API 监听程序

**如果只想运行监听程序（Chrome 已启动）：**
```bash
python valuescan.py
```

## 📦 模块说明

### `valuescan.py` - 主程序
- API 监听程序入口
- 连接到调试模式的 Chrome 并监听 API

### `start_with_chrome.py` - 一键启动脚本
- 自动管理 Chrome 浏览器生命周期
- 关闭所有现有 Chrome 进程
- 以调试模式启动 Chrome（使用项目目录下的独立用户数据）
- 自动启动监听程序

### `kill_chrome.py` - Chrome 进程管理
- `kill_all_chrome_processes()`: 关闭所有 Chrome 和 ChromeDriver 进程
- `start_chrome_debug_mode()`: 以调试模式启动 Chrome
- `restart_chrome_in_debug_mode()`: 一键重启到调试模式
- 支持多种 Chrome 安装路径自动检测
- Chrome 用户数据存储在: `./chrome-debug-profile/`

### `config.py` - 配置管理
- **Telegram 配置**: Bot Token 和用户 ID
- **开关配置**: 是否发送 TG 消息
- **浏览器配置**: Chrome 调试端口（默认 9222）
- **API 配置**: 监听的 API 路径
- **类型映射**: 消息类型、交易类型、资金流向的映射表
- **日志配置**: 日志级别、文件输出等设置

### `logger.py` - 日志系统
- 统一的日志管理
- 支持控制台和文件输出
- 自动日志轮转（默认 10MB，保留 5 个文件）
- 可配置日志级别

### `telegram.py` - Telegram 集成
- `send_telegram_message()`: 发送消息到 Telegram
- `format_message_for_telegram()`: 格式化消息为 HTML 格式
- 支持表情符号和富文本格式

### `message_handler.py` - 消息处理
- `print_message_details()`: 打印消息详情到控制台
- `process_message_item()`: 处理单条消息
- `process_response_data()`: 处理 API 响应数据
- 支持消息去重（通过 ID）

### `api_monitor.py` - API 监听
- **模式1**: `capture_api_request()` - 自动启动浏览器
- **模式2**: `capture_with_existing_browser()` - 连接现有浏览器
- 实时捕获并解析 API 请求和响应
- 自动去重避免重复通知

## 🎯 使用方法

### 一键启动（推荐）

1. **Windows 用户**：直接双击 `启动.bat` 文件
2. **或运行命令**：
   ```bash
   python start_with_chrome.py
   ```
3. 脚本会自动：
   - 关闭所有现有 Chrome 进程
   - 以调试模式启动 Chrome（端口 9222）
   - 启动 API 监听程序
4. 在 Chrome 浏览器中访问 [valuescan.io](https://valuescan.io) 相关页面
5. 程序会自动捕获 API 请求并根据配置发送到 Telegram

### 仅运行监听（Chrome 已启动）

如果 Chrome 已经在调试模式下运行，可以直接运行监听程序：

```bash
python valuescan.py
```

## ⚙️ 配置说明

### Telegram 配置
- **获取 Bot Token**: 在 Telegram 中找到 @BotFather，发送 `/newbot` 创建机器人
- **获取用户 ID**: 在 Telegram 中找到 @userinfobot，发送任意消息获取你的 ID

### 日志配置
- **LOG_LEVEL**: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- **LOG_TO_FILE**: 是否输出到文件
- **LOG_FILE**: 日志文件路径
- **LOG_MAX_SIZE**: 单个日志文件最大大小
- **LOG_BACKUP_COUNT**: 保留的历史日志文件数量

### 消息类型映射
- `100`: 下跌风险
- `108`: 资金异动
- `109`: 上下币公告
- `110`: Alpha
- `111`: 资金出逃
- `113`: FOMO

## 🧪 测试工具

### 测试 Telegram 功能
```bash
python test_telegram.py
```

### 测试日志功能
```bash
python test_logger.py
```

## 📝 日志文件

程序运行时会生成 `valuescan.log` 文件，包含：
- 所有捕获的请求和响应
- 消息处理记录
- 错误和警告信息
- Telegram 发送状态

日志文件会自动轮转，不会无限增长。

## ⚠️ 注意事项

1. **配置文件安全**: 不要将包含真实 Token 的 `config.py` 提交到版本控制
2. **Chrome 浏览器**: 需要安装 Chrome 浏览器
3. **网络连接**: 需要能访问 Telegram API
4. **持续运行**: 程序会持续监听，按 Ctrl+C 停止

## 🔧 故障排查

### 无法连接浏览器
- 确保 Chrome 已安装
- 模式2 需要先用调试端口启动 Chrome
- 检查端口 9222 是否被占用

### Telegram 消息发送失败
- 检查 Bot Token 是否正确
- 检查用户 ID 是否正确
- 确保网络可以访问 api.telegram.org
- 运行 `test_telegram.py` 测试连接

### 没有捕获到消息
- 确保在浏览器中访问了正确的页面
- 检查 API_PATH 配置是否正确
- 查看日志文件了解详细信息

## 📄 许可

本项目仅供学习和个人使用。
