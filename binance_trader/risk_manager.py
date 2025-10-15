"""
风险管理器 - Risk Manager
负责仓位控制、资金管理和风险限制
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class PositionInfo:
    """持仓信息"""
    symbol: str
    quantity: float  # 持仓数量
    entry_price: float  # 入场价格
    current_price: float  # 当前价格
    entry_time: datetime  # 入场时间
    unrealized_pnl: float = 0.0  # 未实现盈亏
    unrealized_pnl_percent: float = 0.0  # 未实现盈亏百分比

    def update_price(self, current_price: float):
        """更新当前价格和盈亏"""
        self.current_price = current_price
        self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        self.unrealized_pnl_percent = ((current_price - self.entry_price) / self.entry_price) * 100


@dataclass
class TradeRecommendation:
    """交易建议"""
    symbol: str
    action: str  # "BUY" 或 "SKIP"
    quantity: float = 0.0  # 建议交易数量
    stop_loss: float = 0.0  # 止损价格
    take_profit_1: float = 0.0  # 第一目标价（50%仓位）
    take_profit_2: float = 0.0  # 第二目标价（剩余仓位）
    reason: str = ""  # 决策原因
    risk_level: str = "MEDIUM"  # 风险等级: LOW, MEDIUM, HIGH


class RiskManager:
    """
    风险管理器

    核心功能：
    1. 仓位控制：限制单个标的和总持仓
    2. 资金管理：根据账户余额动态调整仓位
    3. 风险限制：每日交易次数、最大回撤控制
    4. 止损止盈计算
    """

    def __init__(self,
                 max_position_percent: float = 10.0,  # 单个标的最大仓位比例(%)
                 max_total_position_percent: float = 50.0,  # 总仓位比例(%)
                 max_daily_trades: int = 20,  # 每日最大交易次数
                 max_daily_loss_percent: float = 5.0,  # 每日最大亏损比例(%)
                 stop_loss_percent: float = 3.0,  # 止损百分比
                 take_profit_1_percent: float = 5.0,  # 第一目标盈利(50%仓位)
                 take_profit_2_percent: float = 10.0):  # 第二目标盈利(剩余仓位)
        """
        初始化风险管理器

        Args:
            max_position_percent: 单个标的最大仓位占总资金比例
            max_total_position_percent: 所有持仓占总资金比例
            max_daily_trades: 每日最大交易次数限制
            max_daily_loss_percent: 每日最大亏损比例，达到后停止交易
            stop_loss_percent: 默认止损百分比
            take_profit_1_percent: 第一目标价盈利百分比（减半仓位）
            take_profit_2_percent: 第二目标价盈利百分比（清仓）
        """
        self.max_position_percent = max_position_percent
        self.max_total_position_percent = max_total_position_percent
        self.max_daily_trades = max_daily_trades
        self.max_daily_loss_percent = max_daily_loss_percent
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_1_percent = take_profit_1_percent
        self.take_profit_2_percent = take_profit_2_percent

        # 当前持仓
        self.positions: Dict[str, PositionInfo] = {}

        # 账户信息
        self.total_balance: float = 0.0  # 总余额(USDT)
        self.available_balance: float = 0.0  # 可用余额

        # 交易统计
        self.daily_trades: Dict[str, int] = defaultdict(int)  # 日期 -> 交易次数
        self.daily_pnl: Dict[str, float] = defaultdict(float)  # 日期 -> 盈亏

        # 风控状态
        self.trading_enabled: bool = True
        self.halt_reason: str = ""

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"风险管理器已初始化: "
            f"单标的最大仓位={max_position_percent}%, "
            f"总仓位最大={max_total_position_percent}%, "
            f"止损={stop_loss_percent}%, "
            f"止盈1={take_profit_1_percent}%, 止盈2={take_profit_2_percent}%"
        )

    def update_balance(self, total_balance: float, available_balance: float):
        """更新账户余额"""
        self.total_balance = total_balance
        self.available_balance = available_balance
        self.logger.info(
            f"余额已更新: 总额={total_balance:.2f} USDT, "
            f"可用={available_balance:.2f} USDT"
        )

    def add_position(self, symbol: str, quantity: float,
                     entry_price: float, entry_time: datetime = None):
        """添加新持仓"""
        if entry_time is None:
            entry_time = datetime.now()

        position = PositionInfo(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            entry_time=entry_time
        )
        self.positions[symbol] = position
        self.logger.info(f"持仓已添加: {symbol} x{quantity} @ {entry_price}")

    def remove_position(self, symbol: str) -> Optional[PositionInfo]:
        """移除持仓"""
        position = self.positions.pop(symbol, None)
        if position:
            self.logger.info(f"持仓已移除: {symbol}")
        return position

    def update_position_price(self, symbol: str, current_price: float):
        """更新持仓价格"""
        if symbol in self.positions:
            self.positions[symbol].update_price(current_price)

    def calculate_position_size(self, symbol: str, current_price: float) -> float:
        """
        计算建议仓位大小

        Returns:
            建议购买数量（单位：币）
        """
        # 单个标的最大可用资金
        max_position_value = self.total_balance * (self.max_position_percent / 100)

        # 考虑可用余额
        max_position_value = min(max_position_value, self.available_balance)

        # 计算购买数量
        quantity = max_position_value / current_price

        # 预留一些余额用于手续费（0.1%）
        quantity *= 0.999

        return quantity

    def can_open_position(self, symbol: str) -> tuple[bool, str]:
        """
        检查是否可以开仓

        Returns:
            (是否可以, 原因)
        """
        # 1. 检查交易是否被暂停
        if not self.trading_enabled:
            return False, f"交易已暂停: {self.halt_reason}"

        # 2. 检查是否已持仓该标的
        if symbol in self.positions:
            return False, f"已持有 {symbol} 仓位"

        # 3. 检查每日交易次数限制
        today = datetime.now().strftime("%Y-%m-%d")
        if self.daily_trades[today] >= self.max_daily_trades:
            return False, f"达到每日交易次数限制 ({self.max_daily_trades})"

        # 4. 检查每日亏损限制
        if self.daily_pnl[today] < -(self.total_balance * self.max_daily_loss_percent / 100):
            self.halt_trading(f"达到每日亏损限制 ({self.max_daily_loss_percent}%)")
            return False, self.halt_reason

        # 5. 账户余额校验
        if self.total_balance <= 0:
            return False, "账户余额不可用"

        # 6. 检查总仓位限制
        total_position_value = sum(
            pos.quantity * pos.current_price
            for pos in self.positions.values()
        )
        total_position_percent = (total_position_value / self.total_balance) * 100

        if total_position_percent >= self.max_total_position_percent:
            return False, (f"达到总仓位限制 "
                          f"({total_position_percent:.1f}% >= {self.max_total_position_percent}%)")

        # 7. 检查可用余额
        if self.available_balance < (self.total_balance * 0.05):  # 至少保留5%
            return False, "可用余额不足"

        return True, "OK"

    def generate_trade_recommendation(self,
                                     symbol: str,
                                     current_price: float,
                                     signal_score: float) -> TradeRecommendation:
        """
        生成交易建议

        Args:
            symbol: 交易标的
            current_price: 当前价格
            signal_score: 信号评分 (0-1)

        Returns:
            交易建议对象
        """
        can_trade, reason = self.can_open_position(symbol)

        if not can_trade:
            return TradeRecommendation(
                symbol=symbol,
                action="SKIP",
                reason=reason
            )

        # 计算仓位大小
        quantity = self.calculate_position_size(symbol, current_price)

        # 根据信号评分调整仓位
        # 评分越高，仓位越大（范围：50% - 100%）
        quantity *= (0.5 + 0.5 * signal_score)

        # 计算止损止盈价格
        stop_loss = current_price * (1 - self.stop_loss_percent / 100)
        take_profit_1 = current_price * (1 + self.take_profit_1_percent / 100)
        take_profit_2 = current_price * (1 + self.take_profit_2_percent / 100)

        # 确定风险等级
        if signal_score >= 0.8:
            risk_level = "LOW"
        elif signal_score >= 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return TradeRecommendation(
            symbol=symbol,
            action="BUY",
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            reason=f"信号评分: {signal_score:.2f}",
            risk_level=risk_level
        )

    def record_trade(self, symbol: str, pnl: float = 0.0):
        """记录交易"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_trades[today] += 1
        if pnl != 0:
            self.daily_pnl[today] += pnl
            self.logger.info(f"交易已记录: {symbol}, 盈亏={pnl:.2f}, 今日盈亏={self.daily_pnl[today]:.2f}")

    def halt_trading(self, reason: str):
        """暂停交易"""
        self.trading_enabled = False
        self.halt_reason = reason
        self.logger.error(f"⛔ 交易已暂停: {reason}")

    def resume_trading(self):
        """恢复交易"""
        self.trading_enabled = True
        self.halt_reason = ""
        self.logger.info("✅ 交易已恢复")

    def get_status(self) -> Dict:
        """获取风控状态"""
        today = datetime.now().strftime("%Y-%m-%d")

        total_position_value = sum(
            pos.quantity * pos.current_price
            for pos in self.positions.values()
        )
        total_unrealized_pnl = sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )

        return {
            "trading_enabled": self.trading_enabled,
            "halt_reason": self.halt_reason,
            "total_balance": self.total_balance,
            "available_balance": self.available_balance,
            "position_count": len(self.positions),
            "total_position_value": total_position_value,
            "total_position_percent": (total_position_value / self.total_balance * 100) if self.total_balance > 0 else 0,
            "total_unrealized_pnl": total_unrealized_pnl,
            "daily_trades": self.daily_trades[today],
            "daily_pnl": self.daily_pnl[today],
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_percent": pos.unrealized_pnl_percent
                }
                for symbol, pos in self.positions.items()
            }
        }
