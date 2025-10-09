"""
ValuesCan API 监听工具配置文件示例
请复制此文件为 config.py 并填入您的配置
"""

# ==================== Telegram Bot 配置 ====================
# Telegram Bot Token (从 @BotFather 获取)
# 获取方式: 在 Telegram 中找到 @BotFather，发送 /newbot 创建机器人
TELEGRAM_BOT_TOKEN = ""

# Telegram 目标用户 ID
# 获取方式: 在 Telegram 中找到 @userinfobot，发送任意消息获取您的 ID
TELEGRAM_CHAT_ID = ""

# ==================== 消息发送开关 ====================
# 是否发送 TG 消息
SEND_TG_IN_MODE_1 = True

# ==================== Binance API 配置（合约交易）====================
# Binance API Key（在 Binance 账户设置中创建）
# 注意：需要在 API 管理中开启 "期货交易" 权限
BINANCE_API_KEY = ""

# Binance API Secret
BINANCE_API_SECRET = ""

# 是否使用测试网络（True: 测试网, False: 正式网）
# 合约测试网地址: https://testnet.binancefuture.com/
BINANCE_TESTNET = True

# 是否启用自动交易（谨慎开启！）
BINANCE_TRADE_ENABLED = False

# 每次开仓使用的保证金（USDT）
# 注意：这是保证金金额，实际名义价值 = 保证金 × 杠杆
BINANCE_TRADE_AMOUNT_USDT = 20

# 杠杆倍数（1-125）
# 建议：新手 1-5x，有经验 5-10x，高风险 10-20x
# 警告：高杠杆高风险，可能导致快速爆仓
BINANCE_LEVERAGE = 5

# 最小订单金额（USDT）- Binance 合约最低限制
BINANCE_MIN_ORDER_USDT = 5

# 信号有效时间窗口（分钟）
# 在此时间内同时收到 Alpha 和 FOMO 信号才会执行买入
# 例如：30 表示 30 分钟内必须同时收到两个信号
BINANCE_SIGNAL_TIMEOUT_MINUTES = 30

# ==================== 浏览器配置 ====================
# Chrome 远程调试端口
CHROME_DEBUG_PORT = 9222

# ==================== API 配置 ====================
# 监听的 API 路径（部分匹配）
API_PATH = "api/account/message/getWarnMessage"

# ==================== 消息类型映射 ====================
MESSAGE_TYPE_MAP = {
    100: '下跌风险',
    108: '资金异动',
    109: '上下币公告',
    110: 'Alpha',
    111: '资金出逃',
    113: 'FOMO'
}

# 交易类型映射
TRADE_TYPE_MAP = {
    1: '现货',
    2: '合约'
}

# 资金流向映射
FUNDS_MOVEMENT_MAP = {
    1: '24H内异动',  # 24H内出现大量资金异常流入（短期异动）
    2: '24H外异动',  # 24H外出现大量资金异常流入（中期异动）
    3: '持续流入',   # 资金持续流入，活跃异常（利多信号）
    4: '疑似资金出逃',
    5: '交易量激增'
}

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
