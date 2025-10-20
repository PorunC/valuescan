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
            self.logger.warning("⚠️  运行于合约测试网模式")
        else:
            self.logger.info("运行于合约生产环境模式")

        # 持仓信息缓存
        self.positions: Dict[str, PositionInfo] = {}

        # 已执行的分批止盈级别（避免重复执行）
        self.executed_tp_levels: Dict[str, set] = {}

        # 测试连接
        try:
            self.client.ping()
            self.logger.info("✅ 币安合约 API 连接成功")
        except Exception as e:
            self.logger.error(f"❌ 币安合约 API 连接失败: {e}")
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

            self.logger.debug(f"账户余额: 总额={total_wallet_balance}, 可用={available_balance}")
            return total_wallet_balance, available_balance
        except BinanceAPIException as e:
            self.logger.error(f"获取账户余额失败 (Binance API): {e}")
            return 0.0, 0.0
        except Exception as e:
            self.logger.warning(f"获取账户余额失败 (网络错误): {e}")
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
            self.logger.error(f"获取 {symbol} 价格失败 (Binance API): {e}")
            return None
        except Exception as e:
            self.logger.warning(f"获取 {symbol} 价格失败 (网络错误): {e}")
            return None

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """设置杠杆倍数（带重试机制）"""
        max_retries = 3
        retry_delay = 2  # 秒

        for attempt in range(max_retries):
            try:
                result = self.client.futures_change_leverage(
                    symbol=symbol,
                    leverage=leverage
                )
                self.logger.info(f"✅ 设置 {symbol} 杠杆: {leverage}x")
                return True
            except BinanceAPIException as e:
                if "No need to change leverage" in str(e):
                    self.logger.debug(f"{symbol} 杠杆已设为 {leverage}x")
                    return True

                # 超时错误，尝试重试
                if e.code == -1007 or "Timeout" in str(e):
                    if attempt < max_retries - 1:
                        self.logger.warning(f"⏳ 设置杠杆超时，{retry_delay}秒后重试 ({attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        self.logger.error(f"设置 {symbol} 杠杆失败（已重试{max_retries}次）: {e}")
                        return False
                else:
                    self.logger.error(f"设置 {symbol} 杠杆失败: {e}")
                    return False

        return False

    def set_margin_type(self, symbol: str, margin_type: str) -> bool:
        """设置保证金模式（带重试机制）"""
        max_retries = 3
        retry_delay = 2  # 秒

        for attempt in range(max_retries):
            try:
                self.client.futures_change_margin_type(
                    symbol=symbol,
                    marginType=margin_type
                )
                self.logger.info(f"✅ 设置 {symbol} 保证金类型: {margin_type}")
                return True
            except BinanceAPIException as e:
                if "No need to change margin type" in str(e):
                    self.logger.debug(f"{symbol} 保证金类型已设为 {margin_type}")
                    return True

                # 超时错误，尝试重试
                if e.code == -1007 or "Timeout" in str(e):
                    if attempt < max_retries - 1:
                        self.logger.warning(f"⏳ 设置保证金模式超时，{retry_delay}秒后重试 ({attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        self.logger.error(f"设置 {symbol} 保证金类型失败（已重试{max_retries}次）: {e}")
                        return False
                else:
                    self.logger.error(f"设置 {symbol} 保证金类型失败: {e}")
                    return False

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
            self.logger.error(f"获取 {symbol} 持仓信息失败 (Binance API): {e}")
            return None
        except Exception as e:
            self.logger.warning(f"获取 {symbol} 持仓信息失败 (网络错误): {e}")
            return None

    def verify_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        验证订单状态

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            订单信息字典，如果查询失败返回None
        """
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            return order
        except Exception as e:
            self.logger.error(f"查询订单 {order_id} 状态失败: {e}")
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
            self.logger.error(f"格式化数量失败: {e}")
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
            self.logger.info(f"跳过 {recommendation.symbol} 交易: {recommendation.reason}")
            return False

        # 使用指定杠杆或默认杠杆
        leverage = leverage or self.leverage
        margin_type = margin_type or self.margin_type

        # 构建完整的交易对符号
        binance_symbol = f"{recommendation.symbol}{symbol_suffix}"

        try:
            # 1. 设置杠杆（尽力而为，即使失败也继续）
            leverage_set = self.set_leverage(binance_symbol, leverage)
            if not leverage_set:
                self.logger.warning(f"⚠️  设置杠杆失败，使用当前杠杆继续交易")

            # 2. 设置保证金模式（尽力而为，即使失败也继续）
            margin_set = self.set_margin_type(binance_symbol, margin_type)
            if not margin_set:
                self.logger.warning(f"⚠️  设置保证金模式失败，使用当前模式继续交易")

            # 3. 获取当前价格
            current_price = self.get_symbol_price(binance_symbol)
            if not current_price:
                self.logger.error(f"获取 {binance_symbol} 价格失败")
                return False

            # 使用风控建议的币数量计算等值本金
            notional_usdt = recommendation.quantity * current_price

            self.logger.info(
                f"\n{'='*60}\n"
                f"🚀 开多仓 (合约)\n"
                f"交易对: {binance_symbol}\n"
                f"杠杆: {leverage}x\n"
                f"保证金类型: {margin_type}\n"
                f"数量: {recommendation.quantity:.6f} {recommendation.symbol}\n"
                f"名义价值: {notional_usdt:.2f} USDT (x{leverage} => {notional_usdt * leverage:.2f})\n"
                f"止损: {recommendation.stop_loss:.2f}\n"
                f"止盈 1: {recommendation.take_profit_1:.2f}\n"
                f"止盈 2: {recommendation.take_profit_2:.2f}\n"
                f"风险等级: {recommendation.risk_level}\n"
                f"原因: {recommendation.reason}\n"
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

            self.logger.info(f"📊 计算数量: {quantity} 张合约 @ {current_price}")

            # 5. 开仓（市价做多）- 带重试和状态验证
            max_order_retries = 2
            order_retry_delay = 3  # 秒
            order = None
            order_id = None

            for order_attempt in range(max_order_retries):
                try:
                    self.logger.info(f"🔄 尝试下单 ({order_attempt + 1}/{max_order_retries})...")
                    order = self.client.futures_create_order(
                        symbol=binance_symbol,
                        side='BUY',
                        positionSide='LONG',  # 单向持仓模式的做多
                        type='MARKET',
                        quantity=quantity
                    )
                    order_id = order.get('orderId')
                    self.logger.info(f"✅ 订单已提交，ID: {order_id}")
                    break  # 成功则跳出重试循环

                except BinanceAPIException as e:
                    # 超时错误且未达最大重试次数
                    if (e.code == -1007 or "Timeout" in str(e)) and order_attempt < max_order_retries - 1:
                        self.logger.warning(
                            f"⏳ 下单超时，{order_retry_delay}秒后重试 "
                            f"({order_attempt + 1}/{max_order_retries})"
                        )
                        time.sleep(order_retry_delay)
                        continue
                    else:
                        # 非超时错误或已达最大重试次数
                        self.logger.error(f"❌ 下单失败: {e}")

                        # 超时情况下尝试检查是否有新持仓
                        if e.code == -1007 or "Timeout" in str(e):
                            self.logger.warning("⚠️  超时错误，检查是否有新持仓...")
                            time.sleep(2)  # 等待2秒让订单可能完成
                            position = self.get_position_info(binance_symbol)
                            if position and position.quantity > 0:
                                self.logger.warning(
                                    f"⚠️  检测到新持仓 {position.quantity} 张合约，"
                                    f"订单可能已执行但响应超时"
                                )
                                # 构造一个虚拟订单对象继续流程
                                order = {
                                    'orderId': 'UNKNOWN_TIMEOUT',
                                    'status': 'FILLED',
                                    'executedQty': str(position.quantity),
                                    'origQty': str(quantity)
                                }
                                self.logger.info("✅ 使用检测到的持仓信息继续流程")
                                break
                        raise  # 重新抛出异常

            # 检查是否成功下单
            if not order:
                self.logger.error("❌ 下单失败，未获取到订单信息")
                return False

            # 6. 验证订单状态（如果有订单ID）
            if order_id and order_id != 'UNKNOWN_TIMEOUT':
                time.sleep(1)  # 等待1秒确保订单处理完成
                verified_order = self.verify_order_status(binance_symbol, order_id)
                if verified_order:
                    order = verified_order  # 使用验证后的订单信息
                    self.logger.info(f"✅ 订单状态已验证: {verified_order.get('status')}")

            executed_quantity = float(order.get('executedQty') or order.get('origQty') or 0)

            self.logger.info(
                f"✅ 多仓已开: {binance_symbol} "
                f"x{executed_quantity or quantity} (请求 {quantity})"
            )
            self.logger.info(f"订单 ID: {order.get('orderId')}, 状态: {order.get('status')}")

            # 7. 更新风险管理器持仓（使用实际成交数量）
            self.risk_manager.add_position(
                symbol=recommendation.symbol,
                quantity=executed_quantity or quantity,
                entry_price=current_price
            )

            # 8. 设置止损单
            stop_loss_price = recommendation.stop_loss
            self.logger.info(f"🛡️  设置止损于 {stop_loss_price}")

            try:
                stop_order = self.client.futures_create_order(
                    symbol=binance_symbol,
                    side='SELL',
                    positionSide='LONG',
                    type='STOP_MARKET',
                    stopPrice=stop_loss_price,
                    closePosition=True  # 止损时平掉整个仓位
                )
                self.logger.info(f"✅ 止损已设于 {stop_loss_price}")
            except BinanceAPIException as e:
                self.logger.error(f"设置止损失败: {e}")

            # 9. 记录交易
            self.risk_manager.record_trade(recommendation.symbol)

            # 10. 更新余额
            self.update_risk_manager_balance()

            # 11. 初始化止盈级别跟踪
            self.executed_tp_levels[recommendation.symbol] = set()

            return True

        except BinanceOrderException as e:
            self.logger.error(f"❌ 订单失败: {e}")
            return False
        except BinanceAPIException as e:
            self.logger.error(f"❌ API 错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ 未预期的错误: {e}")
            return False

    def close_position(self, symbol: str, reason: str = "手动平仓") -> bool:
        """
        平仓

        Args:
            symbol: 交易对（如 BTCUSDT）
            reason: 平仓原因

        Returns:
            是否成功
        """
        try:
            self.logger.info(f"🔻 平仓: {symbol} - 原因: {reason}")

            # 市价平仓
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide='LONG',
                type='MARKET',
                closePosition=True  # 平掉整个仓位
            )

            self.logger.info(f"✅ 仓位已平: {symbol}")
            self.logger.info(f"订单 ID: {order.get('orderId')}")

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
            self.logger.error(f"平仓 {symbol} 失败: {e}")
            return False

    def partial_close_position(self, symbol: str, close_percent: float,
                               reason: str = "止盈") -> bool:
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
                self.logger.warning(f"未找到 {symbol} 的持仓")
                return False

            # 计算平仓数量
            close_quantity = abs(position.quantity) * close_percent
            close_quantity = self.format_quantity(symbol, close_quantity)

            self.logger.info(
                f"📉 部分平仓 {close_percent*100:.0f}% {symbol}: "
                f"{close_quantity} 张合约 - 原因: {reason}"
            )

            # 市价平仓
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide='LONG',
                type='MARKET',
                quantity=close_quantity
            )

            self.logger.info(f"✅ 部分平仓成功: {close_quantity} 张合约")
            return True

        except BinanceAPIException as e:
            self.logger.error(f"部分平仓 {symbol} 失败: {e}")
            return False

    def cancel_all_orders(self, symbol: str):
        """取消指定交易对的所有未成交订单"""
        try:
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            self.logger.info(f"已取消 {symbol} 的所有订单")
        except BinanceAPIException as e:
            self.logger.error(f"取消 {symbol} 订单失败: {e}")

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """获取未成交订单"""
        try:
            if symbol:
                return self.client.futures_get_open_orders(symbol=symbol)
            else:
                return self.client.futures_get_open_orders()
        except BinanceAPIException as e:
            self.logger.error(f"获取未成交订单失败: {e}")
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
            self.logger.error(f"更新持仓失败 (Binance API): {e}")
        except Exception as e:
            # 捕获网络连接错误等其他异常
            self.logger.warning(f"更新持仓失败 (网络错误): {e}")
            # 保留之前的持仓数据，不做更新

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
                        f"⚠️  强平风险: {symbol} "
                        f"标记={position.mark_price:.2f}, "
                        f"强平={position.liquidation_price:.2f}, "
                        f"距离={distance:.1f}%"
                    )

        return risky_positions
