"""
币安交易器 - Binance Trader
负责执行实际的交易操作，包括下单、止损止盈设置
"""

import time
import logging
from typing import Dict, Optional, List
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from .risk_manager import RiskManager, TradeRecommendation


class OrderInfo:
    """订单信息"""
    def __init__(self, order_data: Dict):
        self.order_id = order_data.get('orderId')
        self.symbol = order_data.get('symbol')
        self.side = order_data.get('side')  # BUY/SELL
        self.type = order_data.get('type')  # LIMIT/MARKET/STOP_LOSS_LIMIT
        self.status = order_data.get('status')
        self.price = float(order_data.get('price', 0))
        self.quantity = float(order_data.get('origQty', 0))
        self.executed_qty = float(order_data.get('executedQty', 0))
        self.timestamp = order_data.get('transactTime', 0)


class BinanceTrader:
    """
    币安交易执行器

    核心功能：
    1. 连接币安 API
    2. 执行市价买入
    3. 自动设置止损止盈订单
    4. 监控订单状态
    5. 管理持仓
    """

    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 risk_manager: RiskManager,
                 testnet: bool = False):
        """
        初始化交易器

        Args:
            api_key: Binance API Key
            api_secret: Binance API Secret
            risk_manager: 风险管理器实例
            testnet: 是否使用测试网（建议先用测试网验证）
        """
        self.risk_manager = risk_manager
        self.testnet = testnet

        # 初始化 Binance 客户端
        if testnet:
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.API_URL = 'https://testnet.binance.vision/api'
            self.logger = logging.getLogger(__name__)
            self.logger.warning("⚠️  Running in TESTNET mode")
        else:
            self.client = Client(api_key, api_secret)
            self.logger = logging.getLogger(__name__)
            self.logger.info("Running in PRODUCTION mode")

        # 活跃订单跟踪
        self.active_orders: Dict[str, List[OrderInfo]] = {}  # symbol -> [orders]

        # 测试连接
        try:
            self.client.ping()
            self.logger.info("✅ Binance API connection successful")
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Binance API: {e}")
            raise

    def get_account_balance(self) -> tuple[float, float]:
        """
        获取账户余额

        Returns:
            (总余额USDT, 可用余额USDT)
        """
        try:
            account = self.client.get_account()
            usdt_balance = next(
                (float(asset['free']) + float(asset['locked'])
                 for asset in account['balances']
                 if asset['asset'] == 'USDT'),
                0.0
            )
            usdt_free = next(
                (float(asset['free'])
                 for asset in account['balances']
                 if asset['asset'] == 'USDT'),
                0.0
            )
            return usdt_balance, usdt_free
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get account balance: {e}")
            return 0.0, 0.0

    def update_risk_manager_balance(self):
        """更新风险管理器的余额信息"""
        total, available = self.get_account_balance()
        self.risk_manager.update_balance(total, available)

    def get_symbol_price(self, symbol: str) -> Optional[float]:
        """
        获取交易对当前价格

        Args:
            symbol: 交易对，如 "BTCUSDT"
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """获取交易对信息（用于精度处理）"""
        try:
            info = self.client.get_symbol_info(symbol)
            return info
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get symbol info for {symbol}: {e}")
            return None

    def format_quantity(self, symbol: str, quantity: float) -> float:
        """根据交易对规则格式化数量"""
        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            return round(quantity, 6)

        # 获取 LOT_SIZE 过滤器
        lot_size_filter = next(
            (f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'),
            None
        )

        if lot_size_filter:
            step_size = float(lot_size_filter['stepSize'])
            # 根据 step_size 调整精度
            precision = len(str(step_size).rstrip('0').split('.')[-1])
            return round(quantity, precision)

        return round(quantity, 6)

    def format_price(self, symbol: str, price: float) -> float:
        """根据交易对规则格式化价格"""
        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            return round(price, 2)

        # 获取 PRICE_FILTER
        price_filter = next(
            (f for f in symbol_info['filters'] if f['filterType'] == 'PRICE_FILTER'),
            None
        )

        if price_filter:
            tick_size = float(price_filter['tickSize'])
            precision = len(str(tick_size).rstrip('0').split('.')[-1])
            return round(price, precision)

        return round(price, 2)

    def execute_trade(self, recommendation: TradeRecommendation,
                     symbol_suffix: str = "USDT") -> bool:
        """
        执行交易建议

        Args:
            recommendation: 交易建议对象
            symbol_suffix: 交易对后缀（默认USDT）

        Returns:
            是否成功
        """
        if recommendation.action != "BUY":
            self.logger.info(f"Skipping trade for {recommendation.symbol}: {recommendation.reason}")
            return False

        # 构建完整的币安交易对符号
        binance_symbol = f"{recommendation.symbol}{symbol_suffix}"

        self.logger.info(
            f"\n{'='*60}\n"
            f"🎯 EXECUTING TRADE\n"
            f"Symbol: {binance_symbol}\n"
            f"Action: {recommendation.action}\n"
            f"Quantity: {recommendation.quantity:.6f}\n"
            f"Stop Loss: {recommendation.stop_loss:.2f}\n"
            f"Take Profit 1: {recommendation.take_profit_1:.2f} (50% position)\n"
            f"Take Profit 2: {recommendation.take_profit_2:.2f} (remaining)\n"
            f"Risk Level: {recommendation.risk_level}\n"
            f"Reason: {recommendation.reason}\n"
            f"{'='*60}"
        )

        try:
            # 1. 获取当前价格
            current_price = self.get_symbol_price(binance_symbol)
            if not current_price:
                self.logger.error(f"Failed to get price for {binance_symbol}")
                return False

            # 2. 格式化数量
            quantity = self.format_quantity(binance_symbol, recommendation.quantity)

            # 3. 执行市价买入
            self.logger.info(f"📈 Placing MARKET BUY order: {binance_symbol} x{quantity}")

            buy_order = self.client.order_market_buy(
                symbol=binance_symbol,
                quantity=quantity
            )

            buy_order_info = OrderInfo(buy_order)
            self.logger.info(
                f"✅ BUY order filled: {binance_symbol} "
                f"OrderID={buy_order_info.order_id}, "
                f"Qty={buy_order_info.executed_qty}, "
                f"Price≈{current_price}"
            )

            # 4. 更新风险管理器持仓
            self.risk_manager.add_position(
                symbol=recommendation.symbol,
                quantity=buy_order_info.executed_qty,
                entry_price=current_price
            )

            # 5. 设置止损订单 (OCO order - One-Cancels-the-Other)
            # 注意：币安现货 OCO 订单同时包含止损和限价卖出
            self.logger.info(f"🛡️  Setting up Stop-Loss and Take-Profit orders...")

            # 格式化价格
            stop_loss_price = self.format_price(binance_symbol, recommendation.stop_loss)
            stop_limit_price = self.format_price(binance_symbol, stop_loss_price * 0.99)  # 止损触发后的限价

            # 第一个止盈目标（50%仓位）
            tp1_quantity = self.format_quantity(binance_symbol, quantity * 0.5)
            tp1_price = self.format_price(binance_symbol, recommendation.take_profit_1)

            # 第二个止盈目标（剩余仓位）
            tp2_quantity = self.format_quantity(binance_symbol, quantity - tp1_quantity)
            tp2_price = self.format_price(binance_symbol, recommendation.take_profit_2)

            # 设置 OCO 订单（止损 + 第一目标价）
            try:
                oco_order = self.client.create_oco_order(
                    symbol=binance_symbol,
                    side='SELL',
                    quantity=tp1_quantity,
                    price=tp1_price,  # 限价卖出价格
                    stopPrice=stop_loss_price,  # 止损触发价格
                    stopLimitPrice=stop_limit_price,  # 止损后的限价
                    stopLimitTimeInForce='GTC'
                )

                self.logger.info(
                    f"✅ OCO order created: "
                    f"TP1={tp1_price} (qty={tp1_quantity}), "
                    f"SL={stop_loss_price}"
                )

                # 保存活跃订单
                if binance_symbol not in self.active_orders:
                    self.active_orders[binance_symbol] = []
                # OCO 返回多个订单
                for order in oco_order.get('orderReports', []):
                    self.active_orders[binance_symbol].append(OrderInfo(order))

            except BinanceAPIException as e:
                self.logger.error(f"Failed to create OCO order: {e}")
                # 如果 OCO 失败，设置简单的止损单
                try:
                    stop_order = self.client.create_order(
                        symbol=binance_symbol,
                        side='SELL',
                        type='STOP_LOSS_LIMIT',
                        quantity=quantity,
                        price=stop_limit_price,
                        stopPrice=stop_loss_price,
                        timeInForce='GTC'
                    )
                    self.logger.info(f"✅ Stop-Loss order created as fallback")
                except Exception as e2:
                    self.logger.error(f"Failed to create fallback stop-loss: {e2}")

            # 设置第二个止盈订单（限价单）
            if tp2_quantity > 0:
                try:
                    tp2_order = self.client.order_limit_sell(
                        symbol=binance_symbol,
                        quantity=tp2_quantity,
                        price=tp2_price
                    )
                    self.logger.info(f"✅ TP2 order created: {tp2_price} (qty={tp2_quantity})")

                    if binance_symbol not in self.active_orders:
                        self.active_orders[binance_symbol] = []
                    self.active_orders[binance_symbol].append(OrderInfo(tp2_order))

                except BinanceAPIException as e:
                    self.logger.error(f"Failed to create TP2 order: {e}")

            # 6. 记录交易
            self.risk_manager.record_trade(recommendation.symbol)

            # 7. 更新余额
            self.update_risk_manager_balance()

            return True

        except BinanceOrderException as e:
            self.logger.error(f"❌ Order failed: {e}")
            return False
        except BinanceAPIException as e:
            self.logger.error(f"❌ API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            return False

    def cancel_all_orders(self, symbol: str):
        """取消指定交易对的所有活跃订单"""
        try:
            result = self.client.cancel_open_orders(symbol=symbol)
            self.logger.info(f"Cancelled all orders for {symbol}")
            if symbol in self.active_orders:
                del self.active_orders[symbol]
        except BinanceAPIException as e:
            self.logger.error(f"Failed to cancel orders for {symbol}: {e}")

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """获取未完成订单"""
        try:
            if symbol:
                return self.client.get_open_orders(symbol=symbol)
            else:
                return self.client.get_open_orders()
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return []

    def monitor_positions(self):
        """监控持仓状态并更新价格"""
        for symbol in list(self.risk_manager.positions.keys()):
            binance_symbol = f"{symbol}USDT"
            current_price = self.get_symbol_price(binance_symbol)

            if current_price:
                self.risk_manager.update_position_price(symbol, current_price)

                position = self.risk_manager.positions[symbol]
                self.logger.debug(
                    f"{symbol}: Entry={position.entry_price:.2f}, "
                    f"Current={current_price:.2f}, "
                    f"PnL={position.unrealized_pnl_percent:.2f}%"
                )
