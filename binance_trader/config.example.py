"""
Binance 合约自动化交易配置文件示例
复制此文件为 config.py 并填入你的实际配置
"""

# ============ Binance API 配置 ============
# 从币安官网获取: https://www.binance.com/en/my/settings/api-management
# ⚠️ 重要：合约交易需要启用 "Enable Futures" 权限
BINANCE_API_KEY = "your_api_key_here"
BINANCE_API_SECRET = "your_api_secret_here"

# 是否使用测试网（强烈建议先用测试网验证策略）
# 合约测试网: https://testnet.binancefuture.com/
USE_TESTNET = True

# SOCKS5 代理配置（可选）
# 格式: socks5://用户名:密码@主机:端口
# 例如: socks5://user:pass@proxy.example.com:1080
# 留空或 None 表示不使用代理
SOCKS5_PROXY = None  # 示例: "socks5://user:pass@proxy.example.com:1080"

# ============ 合约交易配置 ============
# 交易对后缀（合约通常是 USDT）
SYMBOL_SUFFIX = "USDT"

# 杠杆倍数 (1-125倍，建议不超过20倍)
# 高杠杆 = 高收益 + 高风险
LEVERAGE = 10  # 10倍杠杆

# 保证金模式
# "ISOLATED": 逐仓模式 - 每个仓位独立保证金（推荐，风险隔离）
# "CROSSED": 全仓模式 - 所有仓位共享保证金（风险较高）
MARGIN_TYPE = "ISOLATED"  # 推荐逐仓模式

# 持仓方向（暂时只支持做多）
# "LONG": 做多（买涨）
# "SHORT": 做空（买跌）- 未来版本支持
POSITION_SIDE = "LONG"

# ============ 信号聚合配置 ============
# 信号匹配时间窗口（秒）
# FOMO 和 Alpha 信号在此时间内出现才视为有效聚合信号
SIGNAL_TIME_WINDOW = 300  # 5分钟

# 最低信号评分阈值（0-1）
# 低于此评分的聚合信号将被忽略
MIN_SIGNAL_SCORE = 0.6

# 是否启用 FOMO 加剧信号 (Type 112)
# True: Type 112 作为风险信号，可用于止盈判断
# False: 忽略 Type 112 信号
ENABLE_FOMO_INTENSIFY = True

# ⚠️ 重要：信号类型说明
# Type 113 (FOMO) + Type 110 (Alpha) = 买入信号 ✅
# Type 112 (FOMO加剧) = 风险信号，建议止盈 ⚠️
#
# FOMO加剧表示市场情绪过热，可能接近顶部，不适合开仓
# 如果已有持仓，收到FOMO加剧信号应考虑止盈离场

# ============ 风险管理配置 ============
# 单个标的最大仓位比例（占总资金百分比）
# 注意：这是本金比例，实际仓位会乘以杠杆
# 例如：10% 本金 × 10倍杠杆 = 100% 仓位
MAX_POSITION_PERCENT = 5.0  # 单币种最多5%本金（合约建议更保守）

# 总仓位比例上限（占总资金百分比）
MAX_TOTAL_POSITION_PERCENT = 30.0  # 所有持仓合计不超过30%本金

# 每日最大交易次数
MAX_DAILY_TRADES = 15  # 合约交易建议减少频率

# 每日最大亏损比例（达到后自动停止交易）
MAX_DAILY_LOSS_PERCENT = 5.0  # 单日亏损5%停止交易

# ============ 止损止盈配置 ============
# 固定止损百分比（基于开仓价格）
STOP_LOSS_PERCENT = 2.0  # 亏损2%止损（合约建议更严格）

# 第一目标盈利（减半仓位）
TAKE_PROFIT_1_PERCENT = 3.0  # 盈利3%减半仓位

# 第二目标盈利（清空仓位）
TAKE_PROFIT_2_PERCENT = 6.0  # 盈利6%全部平仓

# ============ 移动止损配置 ============
# 是否启用移动止损（Trailing Stop）
ENABLE_TRAILING_STOP = True

# 移动止损激活阈值（盈利达到此比例后启动移动止损）
# 例如：盈利2%后开始跟踪，此后如果回撤1.5%则触发止损
TRAILING_STOP_ACTIVATION = 2.0  # 盈利2%启动

# 移动止损回调比例（从最高点回撤多少触发止损）
TRAILING_STOP_CALLBACK = 1.5  # 回撤1.5%触发

# 移动止损更新间隔（秒）
TRAILING_STOP_UPDATE_INTERVAL = 10  # 每10秒检查一次

# 移动止损类型
# "PERCENTAGE": 百分比回撤
# "FIXED": 固定金额回撤（未来支持）
TRAILING_STOP_TYPE = "PERCENTAGE"

# ============ 分批止盈配置 ============
# 是否启用分批止盈（金字塔式平仓）
ENABLE_PYRAMIDING_EXIT = True

# 分批止盈策略：[(盈利百分比, 平仓比例), ...]
# 例如：盈利3%时平30%，盈利5%时再平30%，盈利8%时全平
PYRAMIDING_EXIT_LEVELS = [
    (3.0, 0.3),   # 盈利3% → 平仓30%
    (5.0, 0.3),   # 盈利5% → 再平30%（累计60%）
    (8.0, 1.0),   # 盈利8% → 全部平仓
]

# ============ 交易执行配置 ============
# 是否启用自动交易
# True: 发现聚合信号后自动执行交易
# False: 仅记录信号，不执行交易（观察模式）
AUTO_TRADING_ENABLED = False  # 默认关闭，确认策略后再开启

# 订单类型
# "MARKET": 市价单（立即成交，有滑点）
# "LIMIT": 限价单（指定价格，可能不成交）
ORDER_TYPE = "MARKET"

# 仓位精度（小数点后几位）
# 自动从交易所获取，这里是默认值
POSITION_PRECISION = 3

# ============ 监控配置 ============
# 持仓监控间隔（秒）
# 合约需要更频繁监控，特别是启用移动止损时
POSITION_MONITOR_INTERVAL = 10  # 每10秒检查一次持仓

# 余额更新间隔（秒）
BALANCE_UPDATE_INTERVAL = 60  # 每分钟更新一次余额

# 强平风险监控阈值（保证金率低于此值时告警）
LIQUIDATION_WARNING_MARGIN_RATIO = 30.0  # 保证金率 < 30% 时告警

# ============ 日志配置 ============
# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# 日志文件路径
LOG_FILE = "logs/binance_futures_trader.log"

# ============ Telegram 通知配置（可选）============
# 如果需要接收交易通知，填入 Telegram 配置
# 留空则不发送通知
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# 是否发送重要通知（开仓、平仓、止损触发等）
ENABLE_TELEGRAM_ALERTS = True

# ============ 高级配置 ============
# 价格滑点容忍度（百分比）
SLIPPAGE_TOLERANCE = 0.5  # 0.5%

# API 请求重试次数
API_RETRY_COUNT = 3

# API 请求超时（秒）
API_TIMEOUT = 30

# 是否使用对冲模式（Hedge Mode）
# True: 可以同时持有多空仓位
# False: 单向持仓模式（推荐）
USE_HEDGE_MODE = False

# ============ 安全配置 ============
# 最大单笔交易金额（USDT）
# 防止程序错误导致的大额交易
MAX_SINGLE_TRADE_VALUE = 1000.0  # 单笔最多1000 USDT

# 强制平仓保证金率（低于此值强制平仓所有持仓）
FORCE_CLOSE_MARGIN_RATIO = 20.0  # 保证金率 < 20% 强制平仓

# 是否启用紧急停止按钮（检测特定文件存在则停止交易）
ENABLE_EMERGENCY_STOP = True
EMERGENCY_STOP_FILE = "STOP_TRADING"  # 创建此文件即停止交易

# ============ 性能优化配置 ============
# 是否启用 WebSocket 实时价格推送（更快，推荐）
ENABLE_WEBSOCKET = True

# WebSocket 重连间隔（秒）
WEBSOCKET_RECONNECT_INTERVAL = 5

# ============ Telegram 通知配置 ============
# 是否启用交易通知
ENABLE_TRADE_NOTIFICATIONS = True

# Telegram Bot Token（从 @BotFather 获取）
# 如果留空，将尝试从信号监控模块的配置中读取
TELEGRAM_BOT_TOKEN = ""  # 留空则自动从 ../signal_monitor/config.py 读取

# Telegram Chat ID（你的用户 ID 或频道 ID）
# 如果留空，将尝试从信号监控模块的配置中读取
TELEGRAM_CHAT_ID = ""  # 留空则自动从 ../signal_monitor/config.py 读取

# 通知事件类型
NOTIFY_OPEN_POSITION = True      # 开仓通知
NOTIFY_CLOSE_POSITION = True     # 平仓通知
NOTIFY_STOP_LOSS = True          # 止损触发通知
NOTIFY_TAKE_PROFIT = True        # 止盈触发通知
NOTIFY_PARTIAL_CLOSE = True      # 部分平仓通知
NOTIFY_ERRORS = True             # 错误通知

# ============ 回测配置（未来版本）============
# 是否启用回测模式
ENABLE_BACKTEST = False

# 回测起始日期
BACKTEST_START_DATE = "2024-01-01"

# 回测结束日期
BACKTEST_END_DATE = "2024-12-31"
