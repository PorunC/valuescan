"""
Binance 自动化交易配置文件示例
复制此文件为 config.py 并填入你的实际配置
"""

# ============ Binance API 配置 ============
# 从币安官网获取: https://www.binance.com/en/my/settings/api-management
BINANCE_API_KEY = "your_api_key_here"
BINANCE_API_SECRET = "your_api_secret_here"

# 是否使用测试网（强烈建议先用测试网验证策略）
# 测试网申请: https://testnet.binance.vision/
USE_TESTNET = True

# ============ 信号聚合配置 ============
# 信号匹配时间窗口（秒）
# FOMO 和 Alpha 信号在此时间内出现才视为有效聚合信号
SIGNAL_TIME_WINDOW = 300  # 5分钟

# 最低信号评分阈值（0-1）
# 低于此评分的聚合信号将被忽略
MIN_SIGNAL_SCORE = 0.6

# 是否启用 FOMO 加剧信号 (Type 112)
# True: Type 112 和 113 都视为 FOMO 信号
# False: 仅 Type 113 视为 FOMO 信号
ENABLE_FOMO_INTENSIFY = True

# ============ 风险管理配置 ============
# 单个标的最大仓位比例（占总资金百分比）
MAX_POSITION_PERCENT = 10.0  # 单币种最多10%

# 总仓位比例上限（占总资金百分比）
MAX_TOTAL_POSITION_PERCENT = 50.0  # 所有持仓合计不超过50%

# 每日最大交易次数
MAX_DAILY_TRADES = 20

# 每日最大亏损比例（达到后自动停止交易）
MAX_DAILY_LOSS_PERCENT = 5.0  # 单日亏损5%停止交易

# 止损百分比
STOP_LOSS_PERCENT = 3.0  # 下跌3%止损

# 第一目标盈利（减半仓位）
TAKE_PROFIT_1_PERCENT = 5.0  # 上涨5%卖出50%

# 第二目标盈利（清空仓位）
TAKE_PROFIT_2_PERCENT = 10.0  # 上涨10%卖出剩余

# ============ 交易执行配置 ============
# 交易对后缀（默认 USDT）
SYMBOL_SUFFIX = "USDT"

# 是否启用自动交易
# True: 发现聚合信号后自动执行交易
# False: 仅记录信号，不执行交易（观察模式）
AUTO_TRADING_ENABLED = False  # 默认关闭，确认策略后再开启

# ============ 监控配置 ============
# 持仓监控间隔（秒）
POSITION_MONITOR_INTERVAL = 60  # 每分钟检查一次持仓

# 余额更新间隔（秒）
BALANCE_UPDATE_INTERVAL = 300  # 每5分钟更新一次余额

# ============ 日志配置 ============
# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# 日志文件路径
LOG_FILE = "logs/binance_trader.log"

# ============ Telegram 通知配置（可选）============
# 如果需要接收交易通知，填入 Telegram 配置
# 留空则不发送通知
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# ============ 数据库配置 ============
# 数据库文件路径（用于存储交易记录和信号历史）
DATABASE_PATH = "binance_trader.db"

# ============ 高级配置 ============
# 价格滑点容忍度（百分比）
SLIPPAGE_TOLERANCE = 0.5  # 0.5%

# API 请求重试次数
API_RETRY_COUNT = 3

# API 请求超时（秒）
API_TIMEOUT = 30
