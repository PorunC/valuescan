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
# 是否发送 TG 消息
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

# ==================== 消息类型映射 ====================
# 注意：消息类型映射已移至 message_types.py 文件
# 可通过以下方式导入：
# from message_types import MESSAGE_TYPE_MAP, TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP, PREDICT_TYPE_MAP

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
