"""
ValuesCan API 监听工具配置文件示例
请复制此文件为 config.py 并填入您的配置
"""

# ==================== Telegram Bot 配置 ====================
# Telegram Bot Token (从 @BotFather 获取)
# 获取方式: 在 Telegram 中找到 @BotFather，发送 /newbot 创建机器人
TELEGRAM_BOT_TOKEN = ""

# Telegram 目标用户 ID 或频道 ID（支持单个或多个）
# 单个频道示例: TELEGRAM_CHAT_ID = "-1001234567890"
# 多个频道示例: TELEGRAM_CHAT_ID = ["-1001234567890", "-1009876543210", "123456789"]
#
# 频道 ID 格式：-100 开头的数字
# 获取方式: 在 Telegram 中找到 @userinfobot，发送任意消息获取您的 ID
TELEGRAM_CHAT_ID = ""

# Telegram 英文频道 ID（可选，支持单个或多个）
# 如果配置此项，系统会向这些频道发送英文版本的消息
# 留空则不发送英文版本
# 单个频道示例: TELEGRAM_CHAT_ID_EN = "-1001234567890"
# 多个频道示例: TELEGRAM_CHAT_ID_EN = ["-1001234567890", "-1009876543210"]
TELEGRAM_CHAT_ID_EN = ""

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

# ==================== TradingView 图表配置 ====================
# 是否启用 TradingView 图表生成（融合信号时自动生成图表）
ENABLE_TRADINGVIEW_CHART = True

# chart-img.com API Key
# 获取方式: https://www.chart-img.com/
CHART_IMG_API_KEY = ""

# TradingView 布局 ID（需要公开分享的布局）
# 获取方式:
#   1. 在 TradingView 中创建并保存你的图表布局
#   2. 点击右上角 "分享" 按钮，选择 "Make chart public"
#   3. 布局 URL 中的最后一部分就是 Layout ID
#   例如: https://www.tradingview.com/chart/oeTZqtUR/ -> Layout ID = oeTZqtUR
CHART_IMG_LAYOUT_ID = "oeTZqtUR"

# 图表尺寸（像素）
# 根据您的订阅计划选择合适的分辨率：
# 免费/基础计划：最大 800x600
# MEGA 订阅：最大 1920x1600，推荐 1920x1200 或 1600x1000
CHART_IMG_WIDTH = 1600
CHART_IMG_HEIGHT = 1000

# 图表生成超时时间（秒，建议 60-90 秒）
CHART_IMG_TIMEOUT = 90

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
