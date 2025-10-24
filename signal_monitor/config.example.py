"""
ValuesCan API 监听工具配置文件示例
请复制此文件为 config.py 并填入您的配置
"""

# ==================== Telegram Bot 配置 ====================
# Telegram Bot Token (从 @BotFather 获取)
# 获取方式: 在 Telegram 中找到 @BotFather，发送 /newbot 创建机器人
TELEGRAM_BOT_TOKEN = ""

# Telegram 目标用户 ID
# 频道 ID 格式：-100 开头的数字
# 获取方式: 在 Telegram 中找到 @userinfobot，发送任意消息获取您的 ID
TELEGRAM_CHAT_ID = ""

# ==================== 消息发送开关 ====================
# 是否启用 Telegram 通知功能（总开关）
# False: 完全跳过 Telegram 发送，但不影响数据库存储和 IPC 转发
# True: 尝试发送 Telegram 通知
ENABLE_TELEGRAM = True

# 是否发送 TG 消息（需要 ENABLE_TELEGRAM = True 才有效）
SEND_TG_IN_MODE_1 = True

# ==================== 浏览器配置 ====================
# Chrome 远程调试端口
CHROME_DEBUG_PORT = 9222

# 无头模式（不显示浏览器窗口）
# True: 后台运行，不显示浏览器界面（推荐服务器使用）
# False: 显示浏览器窗口（需要手动登录账号）
HEADLESS_MODE = False

# ==================== API 配置 ====================
# 监听的 API 路径（部分匹配）
API_PATH = "api/account/message/getWarnMessage"

# ==================== 本地 IPC 转发 ====================
# 是否将捕获到的信号通过本地 IPC 转发给交易模块
ENABLE_IPC_FORWARDING = True

try:
    # 与交易端共享的 IPC 基础配置
    from ipc_config import IPC_HOST, IPC_PORT, IPC_CONNECT_TIMEOUT, IPC_RETRY_DELAY, IPC_MAX_RETRIES
except ImportError:
    IPC_HOST = "127.0.0.1"
    IPC_PORT = 8765
    IPC_CONNECT_TIMEOUT = 1.5
    IPC_RETRY_DELAY = 2.0
    IPC_MAX_RETRIES = 3

# ==================== 网络代理配置 ====================
# SOCKS5 代理（用于访问币安API获取Alpha交集）
# 格式: "socks5://username:password@host:port"
# 留空则不使用代理
SOCKS5_PROXY = ""
# 示例: SOCKS5_PROXY = "socks5://user:pass@proxy.example.com:1080"

# HTTP/HTTPS 代理（备选方案）
# 格式: {"http": "http://proxy:port", "https": "http://proxy:port"}
# 留空则不使用代理
HTTP_PROXY = ""
# 示例: HTTP_PROXY = "http://proxy.example.com:8080"

# ==================== 日志配置 ====================
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
# DEBUG: 详细的调试信息
# INFO: 一般信息（推荐）
# WARNING: 警告信息
# ERROR: 错误信息
# CRITICAL: 严重错误
LOG_LEVEL = "INFO"

# 是否输出日志到文件
LOG_TO_FILE = True

# 日志文件路径
LOG_FILE = "valuescan.log"

# 日志文件最大大小（字节）10MB
LOG_MAX_SIZE = 10 * 1024 * 1024

# 保留的日志文件数量（日志轮转）
LOG_BACKUP_COUNT = 5

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

# 日期格式
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
