"""
Binance 自动交易模块
根据 Alpha 和 FOMO 信号自动执行买入操作
要求：同时收到 Alpha 和 FOMO 两个信号的交易对才会执行买入
"""

import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from logger import logger
from config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_TESTNET,
    BINANCE_TRADE_ENABLED,
    BINANCE_TRADE_AMOUNT_USDT,
    BINANCE_LEVERAGE,
    BINANCE_SIGNAL_TIMEOUT_MINUTES,
    BINANCE_MIN_ORDER_USDT
)

# 信号缓存：记录每个币种收到的信号
# 结构: {symbol: {'Alpha': timestamp, 'FOMO': timestamp}}
signal_cache = {}


class BinanceTrader:
    """Binance 交易客户端（合约交易）"""
    
    def __init__(self):
        """初始化 Binance 合约交易客户端"""
        self.api_key = BINANCE_API_KEY
        self.api_secret = BINANCE_API_SECRET
        self.testnet = BINANCE_TESTNET
        
        # 设置 API 端点（合约交易）
        if self.testnet:
            self.base_url = "https://testnet.binancefuture.com"
            logger.info("🧪 使用 Binance 合约测试网络")
        else:
            self.base_url = "https://fapi.binance.com"
            logger.info("💰 使用 Binance 合约正式网络")
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key
        })
    
    def _generate_signature(self, params):
        """
        生成请求签名
        
        Args:
            params: 请求参数字典
        
        Returns:
            str: HMAC SHA256 签名
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method, endpoint, params=None, signed=False):
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法 (GET, POST, DELETE)
            endpoint: API 端点
            params: 请求参数
            signed: 是否需要签名
        
        Returns:
            dict: API 响应 JSON
        """
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, params=params, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"   错误详情: {error_data}")
                except:
                    logger.error(f"   响应内容: {e.response.text}")
            return None
    
    def get_account_info(self):
        """
        获取合约账户信息
        
        Returns:
            dict: 账户信息
        """
        return self._request('GET', '/fapi/v2/account', signed=True)
    
    def get_balance(self, asset='USDT'):
        """
        获取合约账户指定资产余额
        
        Args:
            asset: 资产符号，默认 USDT
        
        Returns:
            dict: 包含 availableBalance 和 balance 的余额信息
        """
        account_info = self.get_account_info()
        if not account_info:
            return None
        
        for balance in account_info.get('assets', []):
            if balance['asset'] == asset:
                return {
                    'asset': asset,
                    'available': float(balance['availableBalance']),
                    'balance': float(balance['walletBalance']),
                    'unrealized_pnl': float(balance.get('unrealizedProfit', 0))
                }
        return None
    
    def get_symbol_info(self, symbol):
        """
        获取合约交易对信息
        
        Args:
            symbol: 交易对符号，如 BTCUSDT
        
        Returns:
            dict: 交易对信息
        """
        exchange_info = self._request('GET', '/fapi/v1/exchangeInfo')
        if not exchange_info:
            return None
        
        for s in exchange_info.get('symbols', []):
            if s['symbol'] == symbol:
                return s
        return None
    
    def get_symbol_price(self, symbol):
        """
        获取合约交易对当前标记价格
        
        Args:
            symbol: 交易对符号，如 BTCUSDT
        
        Returns:
            float: 当前标记价格
        """
        result = self._request('GET', '/fapi/v1/premiumIndex', {'symbol': symbol})
        if result and 'markPrice' in result:
            return float(result['markPrice'])
        return None
    
    def set_leverage(self, symbol, leverage):
        """
        设置合约杠杆倍数
        
        Args:
            symbol: 交易对符号
            leverage: 杠杆倍数（1-125）
        
        Returns:
            dict: 设置结果
        """
        params = {
            'symbol': symbol,
            'leverage': leverage
        }
        
        logger.info(f"⚙️ 设置 {symbol} 杠杆: {leverage}x")
        result = self._request('POST', '/fapi/v1/leverage', params, signed=True)
        
        if result:
            logger.info(f"✅ 杠杆设置成功: {result.get('leverage')}x")
        
        return result
    
    def create_market_buy_order(self, symbol, quantity):
        """
        创建合约市价做多单（开多）
        
        Args:
            symbol: 交易对符号，如 BTCUSDT
            quantity: 买入数量（合约张数）
        
        Returns:
            dict: 订单信息
        """
        params = {
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': quantity
        }
        
        logger.info(f"📝 创建合约市价做多单: {symbol}, 数量: {quantity}")
        result = self._request('POST', '/fapi/v1/order', params, signed=True)
        
        if result:
            logger.info(f"✅ 订单创建成功:")
            logger.info(f"   订单ID: {result.get('orderId')}")
            logger.info(f"   状态: {result.get('status')}")
            if 'executedQty' in result:
                logger.info(f"   成交数量: {result.get('executedQty')}")
            if 'avgPrice' in result:
                logger.info(f"   成交均价: ${result.get('avgPrice')}")
        
        return result
    
    def can_trade(self, symbol):
        """
        检查交易对是否可以交易
        
        Args:
            symbol: 交易对符号
        
        Returns:
            bool: 是否可以交易
        """
        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            logger.warning(f"⚠️ 交易对 {symbol} 不存在")
            return False
        
        if symbol_info.get('status') != 'TRADING':
            logger.warning(f"⚠️ 交易对 {symbol} 当前状态: {symbol_info.get('status')}")
            return False
        
        return True


def check_dual_signal(symbol, signal_type):
    """
    检查是否同时收到 Alpha 和 FOMO 两个信号
    
    Args:
        symbol: 币种符号，如 BTC
        signal_type: 当前信号类型，如 Alpha 或 FOMO
    
    Returns:
        bool: 是否满足双信号条件（同时有 Alpha 和 FOMO）
    """
    current_time = time.time()
    
    # 初始化该币种的信号记录
    if symbol not in signal_cache:
        signal_cache[symbol] = {}
    
    # 记录当前信号
    signal_cache[symbol][signal_type] = current_time
    logger.info(f"📝 记录 {symbol} 的 {signal_type} 信号")
    
    # 清理过期信号（超过配置的时间窗口）
    timeout_seconds = BINANCE_SIGNAL_TIMEOUT_MINUTES * 60
    for sig_type in list(signal_cache[symbol].keys()):
        if current_time - signal_cache[symbol][sig_type] > timeout_seconds:
            logger.info(f"� {symbol} 的 {sig_type} 信号已过期，移除")
            del signal_cache[symbol][sig_type]
    
    # 检查是否同时有 Alpha 和 FOMO 信号
    has_alpha = 'Alpha' in signal_cache[symbol]
    has_fomo = 'FOMO' in signal_cache[symbol]
    
    if has_alpha and has_fomo:
        logger.info(f"✅ {symbol} 同时满足 Alpha 和 FOMO 双信号条件！")
        # 清除该币种的信号记录，避免重复交易
        del signal_cache[symbol]
        return True
    else:
        if has_alpha:
            logger.info(f"⏳ {symbol} 已有 Alpha 信号，等待 FOMO 信号...")
        if has_fomo:
            logger.info(f"⏳ {symbol} 已有 FOMO 信号，等待 Alpha 信号...")
        return False


def execute_buy_signal(symbol):
    """
    执行买入信号（仅在双信号确认后调用）
    
    Args:
        symbol: 币种符号，如 BTC
    
    Returns:
        bool: 是否执行成功
    """
    # 检查是否启用交易
    if not BINANCE_TRADE_ENABLED:
        logger.info(f"💡 交易功能未启用，跳过 {symbol}")
        return False
    
    # 构建交易对符号（币种+USDT）
    trading_pair = f"{symbol}USDT"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 执行双信号买入: {symbol}")
    logger.info(f"{'='*60}")
    
    # 创建交易客户端
    trader = BinanceTrader()
    
    # 检查 API 配置
    if not trader.api_key or not trader.api_secret:
        logger.error("❌ Binance API 密钥未配置")
        return False
    
    # 检查交易对是否可交易
    if not trader.can_trade(trading_pair):
        logger.error(f"❌ {trading_pair} 不可交易")
        return False
    
    # 设置杠杆
    from config import BINANCE_LEVERAGE
    leverage_result = trader.set_leverage(trading_pair, BINANCE_LEVERAGE)
    if not leverage_result:
        logger.warning(f"⚠️ 设置杠杆失败，使用默认杠杆")
    
    # 获取当前价格
    current_price = trader.get_symbol_price(trading_pair)
    if not current_price:
        logger.error(f"❌ 无法获取 {trading_pair} 价格")
        return False
    
    logger.info(f"💵 当前标记价格: ${current_price}")
    
    # 检查账户余额
    balance = trader.get_balance('USDT')
    if not balance:
        logger.error("❌ 无法获取账户余额")
        return False
    
    available_balance = balance['available']
    logger.info(f"💰 可用余额: {available_balance:.2f} USDT")
    if balance['unrealized_pnl'] != 0:
        logger.info(f"📊 未实现盈亏: {balance['unrealized_pnl']:.2f} USDT")
    
    # 检查余额是否足够
    if available_balance < BINANCE_MIN_ORDER_USDT:
        logger.warning(f"⚠️ 可用余额不足最小交易金额 ({BINANCE_MIN_ORDER_USDT} USDT)")
        return False
    
    # 确定买入金额（考虑杠杆）
    buy_amount_usdt = min(BINANCE_TRADE_AMOUNT_USDT, available_balance)
    
    if buy_amount_usdt < BINANCE_MIN_ORDER_USDT:
        logger.warning(f"⚠️ 买入金额 ({buy_amount_usdt} USDT) 低于最小限制")
        return False
    
    # 计算合约数量（名义价值 = 买入金额 * 杠杆）
    nominal_value = buy_amount_usdt * BINANCE_LEVERAGE
    quantity = nominal_value / current_price
    
    # 获取交易对精度信息
    symbol_info = trader.get_symbol_info(trading_pair)
    if symbol_info:
        # 根据数量精度调整
        quantity_precision = symbol_info.get('quantityPrecision', 3)
        quantity = round(quantity, quantity_precision)
    
    logger.info(f"💸 计划买入:")
    logger.info(f"   保证金: {buy_amount_usdt:.2f} USDT")
    logger.info(f"   杠杆: {BINANCE_LEVERAGE}x")
    logger.info(f"   名义价值: {nominal_value:.2f} USDT")
    logger.info(f"   合约数量: {quantity}")
    
    # 执行市价做多
    try:
        order = trader.create_market_buy_order(trading_pair, quantity)
        
        if order:
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ 双信号买入成功: {symbol}")
            logger.info(f"{'='*60}\n")
            return True
        else:
            logger.error(f"❌ 双信号买入失败: {symbol}")
            return False
    
    except Exception as e:
        logger.error(f"❌ 执行买入时发生异常: {e}")
        return False


def handle_signal_message(content, msg_type):
    """
    处理信号消息，判断是否需要执行交易
    要求：必须同时收到 Alpha 和 FOMO 两个信号才执行买入
    
    Args:
        content: 消息内容字典
        msg_type: 消息类型代码
    
    Returns:
        bool: 是否执行了交易
    """
    from config import MESSAGE_TYPE_MAP
    
    # 获取信号类型名称
    signal_type = MESSAGE_TYPE_MAP.get(msg_type, '')
    
    # 只处理 Alpha (110) 和 FOMO (113) 信号
    if msg_type not in [110, 113]:
        return False
    
    # 提取币种符号
    symbol = content.get('symbol')
    if not symbol:
        logger.warning(f"⚠️ {signal_type} 信号缺少币种信息")
        return False
    
    # 检查是否满足双信号条件
    if check_dual_signal(symbol, signal_type):
        # 满足条件，执行买入
        return execute_buy_signal(symbol)
    else:
        # 不满足条件，等待另一个信号
        return False
