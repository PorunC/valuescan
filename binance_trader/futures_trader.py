"""
币安合约交易器 - Binance Futures Trader
负责执行合约交易操作，包括开仓、平仓、移动止损等
"""

import time
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from .risk_manager import RiskManager, TradeRecommendation


class PositionInfo:
    """合约持仓信息"""
    def __init__(self, data: Dict):
        self.symbol = data.get('symbol', '')
        self.position_side = data.get('positionSide', 'LONG')
        self.quantity = float(data.get('positionAmt', 0))
        self.entry_price = float(data.get('entryPrice', 0))
        self.mark_price = float(data.get('markPrice', 0))
        self.unrealized_pnl = float(data.get('unRealizedProfit', 0))
        self.leverage = int(data.get('leverage', 1))
        self.liquidation_price = float(data.get('liquidationPrice', 0))
        self.margin_type = data.get('marginType', 'isolated')

        # 计算盈亏百分比
        if self.entry_price > 0:
            self.unrealized_pnl_percent = ((self.mark_price - self.entry_price) / self.entry_price) * 100
        else:
            self.unrealized_pnl_percent = 0.0

        # 移动止损相关
        self.highest_price = self.mark_price  # 持仓以来的最高价
        self.trailing_stop_activated = False  # 移动止损是否已激活
        self.trailing_stop_price = 0.0  # 当前移动止损价格


class BinanceFuturesTrader:
    """
    币安合约交易执行器

    核心功能：
    1. 连接币安合约 API
    2. 设置杠杆和保证金模式
    3. 执行市价开仓
    4. 管理止损止盈订单
    5. 实现移动止损策略
    6. 分批止盈管理
    7. 强平风险监控
    """

    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 risk_manager: RiskManager,
                 leverage: int = 10,
                 margin_type: str = "ISOLATED",
                 testnet: bool = False):
        """
        初始化合约交易器

        Args:
            api_key: Binance API Key
            api_secret: Binance API Secret
            risk_manager: 风险管理器实例
            leverage: 杠杆倍数（1-125）
            margin_type: 保证金模式 ISOLATED/CROSSED
            testnet: 是否使用测试网
        """
        self.risk_manager = risk_manager
        self.leverage = leverage
        self.margin_type = margin_type
        self.testnet = testnet

        # 初始化 Binance 合约客户端
        self.client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            # python-binance 默认只切换现货测试网，需要手动指定合约测试网入口
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        self.logger = logging.getLogger(__name__)

        if testnet:
            self.logger.warning("⚠️  Running in FUTURES TESTNET mode")
        else:
            self.logger.info("Running in FUTURES PRODUCTION mode")

        # 持仓信息缓存
        self.positions: Dict[str, PositionInfo] = {}

        # 已执行的分批止盈级别（避免重复执行）
        self.executed_tp_levels: Dict[str, set] = {}

        # 测试连接
        try:
            self.client.ping()
            self.logger.info("✅ Binance Futures API connection successful")
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Binance Futures API: {e}")
            raise

    def get_account_balance(self) -> Tuple[float, float]:
        """
        获取合约账户余额

        Returns:
            (总余额USDT, 可用余额USDT)
        """
        try:
            account = self.client.futures_account()
            total_wallet_balance = float(account.get('totalWalletBalance', 0))
            available_balance = float(account.get('availableBalance', 0))

            self.logger.debug(f"Account balance: total={total_wallet_balance}, available={available_balance}")
            return total_wallet_balance, available_balance
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get account balance: {e}")
            return 0.0, 0.0

    def update_risk_manager_balance(self):
        """更新风险管理器的余额信息"""
        total, available = self.get_account_balance()
        self.risk_manager.update_balance(total, available)

    def get_symbol_price(self, symbol: str) -> Optional[float]:
        """获取合约当前标记价格"""
        try:
            ticker = self.client.futures_mark_price(symbol=symbol)
            return float(ticker['markPrice'])
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """设置杠杆倍数"""
        try:
            result = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            self.logger.info(f"✅ Set leverage for {symbol}: {leverage}x")
            return True
        except BinanceAPIException as e:
            if "No need to change leverage" in str(e):
                self.logger.debug(f"Leverage for {symbol} already set to {leverage}x")
                return True
            self.logger.error(f"Failed to set leverage for {symbol}: {e}")
            return False

    def set_margin_type(self, symbol: str, margin_type: str) -> bool:
        """设置保证金模式"""
        try:
            self.client.futures_change_margin_type(
                symbol=symbol,
                marginType=margin_type
            )
            self.logger.info(f"✅ Set margin type for {symbol}: {margin_type}")
            return True
        except BinanceAPIException as e:
            if "No need to change margin type" in str(e):
                self.logger.debug(f"Margin type for {symbol} already set to {margin_type}")
                return True
            self.logger.error(f"Failed to set margin type for {symbol}: {e}")
            return False

    def get_position_info(self, symbol: str) -> Optional[PositionInfo]:
        """获取指定标的的持仓信息"""
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            for pos in positions:
                qty = float(pos.get('positionAmt', 0))
                if qty != 0:  # 有持仓
                    return PositionInfo(pos)
            return None
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get position info for {symbol}: {e}")
            return None

    def calculate_quantity(self, symbol: str, usdt_amount: float,
                          leverage: int, current_price: float) -> float:
        """
        计算合约数量

        Args:
            symbol: 交易对
            usdt_amount: 使用的USDT金额（本金）
            leverage: 杠杆倍数
            current_price: 当前价格

        Returns:
            合约数量
        """
        # 合约价值 = 本金 × 杠杆
        position_value = usdt_amount * leverage

        # 数量 = 合约价值 / 当前价格
        quantity = position_value / current_price

        # 预留手续费（0.05%）
        quantity *= 0.9995

        return quantity

    def format_quantity(self, symbol: str, quantity: float) -> float:
        """根据交易对规则格式化数量"""
        try:
            exchange_info = self.client.futures_exchange_info()
            symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)

            if symbol_info:
                for filter_item in symbol_info['filters']:
                    if filter_item['filterType'] == 'LOT_SIZE':
                        step_size = float(filter_item['stepSize'])
                        precision = len(str(step_size).rstrip('0').split('.')[-1])
                        return round(quantity, precision)

            return round(quantity, 3)  # 默认3位小数
        except Exception as e:
            self.logger.error(f"Failed to format quantity: {e}")
            return round(quantity, 3)

    def open_long_position(self, recommendation: TradeRecommendation,
                          symbol_suffix: str = "USDT",
                          leverage: int = None,
                          margin_type: str = None) -> bool:
        """
        开多仓

        Args:
            recommendation: 交易建议
            symbol_suffix: 交易对后缀
            leverage: 杠杆倍数（None则使用默认）
            margin_type: 保证金模式（None则使用默认）

        Returns:
            是否成功
        """
        if recommendation.action != "BUY":
            self.logger.info(f"Skipping trade for {recommendation.symbol}: {recommendation.reason}")
            return False

        # 使用指定杠杆或默认杠杆
        leverage = leverage or self.leverage
        margin_type = margin_type or self.margin_type

        # 构建完整的交易对符号
        binance_symbol = f"{recommendation.symbol}{symbol_suffix}"

        try:
            # 1. 设置杠杆
            if not self.set_leverage(binance_symbol, leverage):
                return False

            # 2. 设置保证金模式
            if not self.set_margin_type(binance_symbol, margin_type):
                return False

            # 3. 获取当前价格
            current_price = self.get_symbol_price(binance_symbol)
            if not current_price:
                self.logger.error(f"Failed to get price for {binance_symbol}")
                return False

            # 使用风控建议的币数量计算等值本金
            notional_usdt = recommendation.quantity * current_price

            self.logger.info(
                f"\n{'='*60}\n"
                f"🚀 OPENING LONG POSITION (FUTURES)\n"
                f"Symbol: {binance_symbol}\n"
                f"Leverage: {leverage}x\n"
                f"Margin Type: {margin_type}\n"
                f"Size: {recommendation.quantity:.6f} {recommendation.symbol}\n"
                f"Notional: {notional_usdt:.2f} USDT (x{leverage} => {notional_usdt * leverage:.2f})\n"
                f"Stop Loss: {recommendation.stop_loss:.2f}\n"
                f"Take Profit 1: {recommendation.take_profit_1:.2f}\n"
                f"Take Profit 2: {recommendation.take_profit_2:.2f}\n"
                f"Risk Level: {recommendation.risk_level}\n"
                f"Reason: {recommendation.reason}\n"
                f"{'='*60}"
            )

            # 4. 计算合约数量
            quantity = self.calculate_quantity(
                binance_symbol,
                notional_usdt,  # 使用等值USDT本金
                leverage,
                current_price
            )

            # 格式化数量
            quantity = self.format_quantity(binance_symbol, quantity)

            self.logger.info(f"📊 Calculated quantity: {quantity} contracts @ {current_price}")

            # 5. 开仓（市价做多）
            order = self.client.futures_create_order(
                symbol=binance_symbol,
                side='BUY',
                positionSide='LONG',  # 单向持仓模式的做多
                type='MARKET',
                quantity=quantity
            )

            executed_quantity = float(order.get('executedQty') or order.get('origQty') or 0)

            self.logger.info(
                f"✅ LONG position opened: {binance_symbol} "
                f"x{executed_quantity or quantity} (requested {quantity})"
            )
            self.logger.info(f"Order ID: {order.get('orderId')}, Status: {order.get('status')}")

            # 6. 更新风险管理器持仓（使用实际成交数量）
            self.risk_manager.add_position(
                symbol=recommendation.symbol,
                quantity=executed_quantity or quantity,
                entry_price=current_price
            )

            # 7. 设置止损单
            stop_loss_price = recommendation.stop_loss
            self.logger.info(f"🛡️  Setting Stop Loss at {stop_loss_price}")

            try:
                stop_order = self.client.futures_create_order(
                    symbol=binance_symbol,
                    side='SELL',
                    positionSide='LONG',
                    type='STOP_MARKET',
                    stopPrice=stop_loss_price,
                    closePosition=True  # 止损时平掉整个仓位
                )
                self.logger.info(f"✅ Stop Loss set at {stop_loss_price}")
            except BinanceAPIException as e:
                self.logger.error(f"Failed to set stop loss: {e}")

            # 8. 记录交易
            self.risk_manager.record_trade(recommendation.symbol)

            # 9. 更新余额
            self.update_risk_manager_balance()

            # 10. 初始化止盈级别跟踪
            self.executed_tp_levels[recommendation.symbol] = set()

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

    def close_position(self, symbol: str, reason: str = "Manual close") -> bool:
        """
        平仓

        Args:
            symbol: 交易对（如 BTCUSDT）
            reason: 平仓原因

        Returns:
            是否成功
        """
        try:
            self.logger.info(f"🔻 Closing position: {symbol} - Reason: {reason}")

            # 市价平仓
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide='LONG',
                type='MARKET',
                closePosition=True  # 平掉整个仓位
            )

            self.logger.info(f"✅ Position closed: {symbol}")
            self.logger.info(f"Order ID: {order.get('orderId')}")

            # 取消该标的的所有未成交订单
            self.cancel_all_orders(symbol)

            # 从风险管理器移除持仓
            symbol_base = symbol.replace("USDT", "")
            self.risk_manager.remove_position(symbol_base)

            # 清理止盈级别记录
            if symbol_base in self.executed_tp_levels:
                del self.executed_tp_levels[symbol_base]

            return True

        except BinanceAPIException as e:
            self.logger.error(f"Failed to close position {symbol}: {e}")
            return False

    def partial_close_position(self, symbol: str, close_percent: float,
                               reason: str = "Take profit") -> bool:
        """
        部分平仓

        Args:
            symbol: 交易对
            close_percent: 平仓比例 (0-1)
            reason: 平仓原因

        Returns:
            是否成功
        """
        try:
            # 获取当前持仓
            position = self.get_position_info(symbol)
            if not position or position.quantity == 0:
                self.logger.warning(f"No position found for {symbol}")
                return False

            # 计算平仓数量
            close_quantity = abs(position.quantity) * close_percent
            close_quantity = self.format_quantity(symbol, close_quantity)

            self.logger.info(
                f"📉 Partial closing {close_percent*100:.0f}% of {symbol}: "
                f"{close_quantity} contracts - Reason: {reason}"
            )

            # 市价平仓
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide='LONG',
                type='MARKET',
                quantity=close_quantity
            )

            self.logger.info(f"✅ Partial close successful: {close_quantity} contracts")
            return True

        except BinanceAPIException as e:
            self.logger.error(f"Failed to partial close {symbol}: {e}")
            return False

    def cancel_all_orders(self, symbol: str):
        """取消指定交易对的所有未成交订单"""
        try:
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            self.logger.info(f"Cancelled all orders for {symbol}")
        except BinanceAPIException as e:
            self.logger.error(f"Failed to cancel orders for {symbol}: {e}")

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """获取未成交订单"""
        try:
            if symbol:
                return self.client.futures_get_open_orders(symbol=symbol)
            else:
                return self.client.futures_get_open_orders()
        except BinanceAPIException as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return []

    def update_positions(self):
        """更新所有持仓信息"""
        try:
            positions = self.client.futures_position_information()
            previous_positions = self.positions
            updated_positions: Dict[str, PositionInfo] = {}

            for pos_data in positions:
                qty = float(pos_data.get('positionAmt', 0))
                if qty != 0:  # 只保存有持仓的
                    symbol = pos_data.get('symbol')
                    position = PositionInfo(pos_data)

                    # 如果之前有缓存，继承移动止损数据
                    if symbol in previous_positions:
                        old_pos = previous_positions[symbol]
                        position.highest_price = max(position.mark_price, old_pos.highest_price)
                        position.trailing_stop_activated = old_pos.trailing_stop_activated
                        position.trailing_stop_price = old_pos.trailing_stop_price

                    updated_positions[symbol] = position

                    # 同步更新风险管理器的持仓价格
                    symbol_base = symbol.replace("USDT", "")
                    self.risk_manager.update_position_price(symbol_base, position.mark_price)

            # 用最新数据替换缓存
            self.positions = updated_positions

        except BinanceAPIException as e:
            self.logger.error(f"Failed to update positions: {e}")

    def monitor_positions(self):
        """监控持仓状态并更新价格"""
        self.update_positions()

        for symbol, position in self.positions.items():
            symbol_base = symbol.replace("USDT", "")

            self.logger.debug(
                f"{symbol_base}: Entry={position.entry_price:.2f}, "
                f"Mark={position.mark_price:.2f}, "
                f"PnL={position.unrealized_pnl_percent:.2f}%, "
                f"Leverage={position.leverage}x"
            )

    def check_liquidation_risk(self) -> List[Tuple[str, float]]:
        """
        检查强平风险

        Returns:
            [(symbol, margin_ratio), ...] 保证金率较低的持仓列表
        """
        risky_positions = []

        for symbol, position in self.positions.items():
            if position.liquidation_price > 0:
                # 计算距离强平价格的百分比
                distance = abs(position.mark_price - position.liquidation_price) / position.mark_price * 100

                if distance < 30:  # 距离强平价格小于30%
                    risky_positions.append((symbol, distance))
                    self.logger.warning(
                        f"⚠️  LIQUIDATION RISK: {symbol} "
                        f"Mark={position.mark_price:.2f}, "
                        f"Liq={position.liquidation_price:.2f}, "
                        f"Distance={distance:.1f}%"
                    )

        return risky_positions
