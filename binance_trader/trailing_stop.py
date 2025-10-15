"""
移动止损管理器 - Trailing Stop Manager
负责管理移动止损和分批止盈策略
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class TrailingStopManager:
    """
    移动止损管理器

    核心功能：
    1. 跟踪持仓最高价
    2. 自动更新移动止损价格
    3. 检测止损触发
    4. 管理分批止盈
    """

    def __init__(self,
                 activation_percent: float = 2.0,  # 激活阈值
                 callback_percent: float = 1.5,  # 回调触发百分比
                 update_interval: int = 10):  # 更新间隔（秒）
        """
        初始化移动止损管理器

        Args:
            activation_percent: 盈利达到此百分比后启动移动止损
            callback_percent: 从最高点回撤此百分比时触发止损
            update_interval: 更新间隔（秒）
        """
        self.activation_percent = activation_percent
        self.callback_percent = callback_percent
        self.update_interval = update_interval

        # 每个标的的跟踪数据
        self.tracking_data: Dict[str, dict] = {}

        self.logger = logging.getLogger(__name__)

        self.logger.info(
            f"移动止损管理器已初始化: "
            f"激活={activation_percent}%, 回调={callback_percent}%"
        )

    def add_position(self, symbol: str, entry_price: float, current_price: float):
        """添加新持仓到跟踪列表"""
        self.tracking_data[symbol] = {
            'entry_price': entry_price,
            'highest_price': current_price,
            'current_price': current_price,
            'activated': False,
            'trailing_stop_price': 0.0,
            'last_update': datetime.now()
        }

        self.logger.info(f"📊 开始追踪 {symbol} @ {entry_price}")

    def update_price(self, symbol: str, current_price: float) -> Optional[Dict]:
        """
        更新价格并检查止损触发

        Args:
            symbol: 交易标的
            current_price: 当前价格

        Returns:
            如果触发止损，返回止损信息；否则返回 None
        """
        if symbol not in self.tracking_data:
            return None

        data = self.tracking_data[symbol]
        data['current_price'] = current_price
        data['last_update'] = datetime.now()

        # 更新最高价
        if current_price > data['highest_price']:
            data['highest_price'] = current_price

        entry_price = data['entry_price']
        highest_price = data['highest_price']

        # 计算当前盈利百分比
        profit_percent = ((current_price - entry_price) / entry_price) * 100

        # 检查是否达到激活阈值
        if not data['activated'] and profit_percent >= self.activation_percent:
            data['activated'] = True
            self.logger.info(
                f"🎯 {symbol} 移动止损已激活: "
                f"盈利={profit_percent:.2f}% >= {self.activation_percent}%"
            )

        # 如果已激活，更新移动止损价格
        if data['activated']:
            # 移动止损价格 = 最高价 × (1 - 回调百分比)
            trailing_stop_price = highest_price * (1 - self.callback_percent / 100)
            data['trailing_stop_price'] = trailing_stop_price

            # 检查是否触发止损
            if current_price <= trailing_stop_price:
                trigger_info = {
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'highest_price': highest_price,
                    'current_price': current_price,
                    'trailing_stop_price': trailing_stop_price,
                    'profit_percent': profit_percent,
                    'reason': '移动止损已触发'
                }

                self.logger.warning(
                    f"🛑 移动止损已触发: {symbol}\n"
                    f"  入场: {entry_price:.2f}\n"
                    f"  最高: {highest_price:.2f}\n"
                    f"  当前: {current_price:.2f}\n"
                    f"  止损: {trailing_stop_price:.2f}\n"
                    f"  盈利: {profit_percent:.2f}%"
                )

                # 移除跟踪
                del self.tracking_data[symbol]

                return trigger_info

            # 记录调试信息
            self.logger.debug(
                f"追踪 {symbol}: "
                f"入场={entry_price:.2f}, "
                f"最高={highest_price:.2f}, "
                f"当前={current_price:.2f}, "
                f"止损={trailing_stop_price:.2f}, "
                f"盈利={profit_percent:.2f}%"
            )

        return None

    def remove_position(self, symbol: str):
        """从跟踪列表移除持仓"""
        if symbol in self.tracking_data:
            del self.tracking_data[symbol]
            self.logger.info(f"停止追踪 {symbol}")

    def get_status(self, symbol: str) -> Optional[Dict]:
        """获取指定标的的跟踪状态"""
        return self.tracking_data.get(symbol)

    def get_all_status(self) -> Dict[str, Dict]:
        """获取所有跟踪状态"""
        return self.tracking_data.copy()


class PyramidingExitManager:
    """
    分批止盈管理器

    实现金字塔式平仓策略：
    - 盈利3% → 平30%
    - 盈利5% → 平30% (累计60%)
    - 盈利8% → 全平
    """

    def __init__(self, exit_levels: List[Tuple[float, float]]):
        """
        初始化分批止盈管理器

        Args:
            exit_levels: [(盈利百分比, 平仓比例), ...]
                        例如: [(3.0, 0.3), (5.0, 0.3), (8.0, 1.0)]
        """
        # 按盈利百分比排序
        self.exit_levels = sorted(exit_levels, key=lambda x: x[0])

        # 记录每个标的已执行的级别
        self.executed_levels: Dict[str, set] = {}

        # 记录每个标的的入场价格
        self.entry_prices: Dict[str, float] = {}

        self.logger = logging.getLogger(__name__)

        self.logger.info(f"金字塔退出管理器已初始化，共 {len(exit_levels)} 个级别")
        for profit_pct, close_pct in self.exit_levels:
            self.logger.info(f"  级别: {profit_pct}% 盈利 → 平仓 {close_pct*100}%")

    def add_position(self, symbol: str, entry_price: float):
        """添加新持仓"""
        self.entry_prices[symbol] = entry_price
        self.executed_levels[symbol] = set()
        self.logger.info(f"📊 开始金字塔追踪 {symbol} @ {entry_price}")

    def check_exit_trigger(self, symbol: str, current_price: float) -> Optional[Tuple[float, float, int]]:
        """
        检查是否触发分批止盈

        Args:
            symbol: 交易标的
            current_price: 当前价格

        Returns:
            如果触发，返回 (盈利百分比, 平仓比例, 级别索引)；否则返回 None
        """
        if symbol not in self.entry_prices:
            return None

        entry_price = self.entry_prices[symbol]
        executed = self.executed_levels[symbol]

        # 计算当前盈利百分比
        profit_percent = ((current_price - entry_price) / entry_price) * 100

        # 检查每个级别
        for level_idx, (target_profit, close_ratio) in enumerate(self.exit_levels):
            # 如果该级别未执行且达到目标盈利
            if level_idx not in executed and profit_percent >= target_profit:
                # 标记为已执行
                executed.add(level_idx)

                self.logger.info(
                    f"🎯 {symbol} 触发金字塔退出: "
                    f"级别 {level_idx+1}, "
                    f"盈利 {profit_percent:.2f}% >= {target_profit}%, "
                    f"平仓 {close_ratio*100}%"
                )

                return (profit_percent, close_ratio, level_idx)

        return None

    def remove_position(self, symbol: str):
        """移除持仓"""
        if symbol in self.entry_prices:
            del self.entry_prices[symbol]
        if symbol in self.executed_levels:
            del self.executed_levels[symbol]
        self.logger.info(f"停止金字塔追踪 {symbol}")

    def get_status(self, symbol: str) -> Optional[Dict]:
        """获取分批止盈状态"""
        if symbol not in self.entry_prices:
            return None

        entry_price = self.entry_prices[symbol]
        executed = self.executed_levels[symbol]

        return {
            'entry_price': entry_price,
            'executed_levels': list(executed),
            'total_levels': len(self.exit_levels),
            'next_level': self._get_next_level(executed)
        }

    def _get_next_level(self, executed: set) -> Optional[Tuple[float, float]]:
        """获取下一个未执行的级别"""
        for level_idx, (profit_pct, close_pct) in enumerate(self.exit_levels):
            if level_idx not in executed:
                return (profit_pct, close_pct)
        return None


class StopLossManager:
    """
    止损管理器

    负责管理固定止损和动态止损
    """

    def __init__(self, stop_loss_percent: float = 2.0):
        """
        初始化止损管理器

        Args:
            stop_loss_percent: 止损百分比
        """
        self.stop_loss_percent = stop_loss_percent

        # 记录每个标的的止损价格
        self.stop_loss_prices: Dict[str, float] = {}

        self.logger = logging.getLogger(__name__)

    def add_position(self, symbol: str, entry_price: float):
        """添加新持仓的止损"""
        stop_loss_price = entry_price * (1 - self.stop_loss_percent / 100)
        self.stop_loss_prices[symbol] = stop_loss_price

        self.logger.info(
            f"🛡️  {symbol} 止损已设: "
            f"{stop_loss_price:.2f} (-{self.stop_loss_percent}%)"
        )

    def check_stop_loss(self, symbol: str, current_price: float) -> Optional[Dict]:
        """
        检查是否触发止损

        Returns:
            如果触发，返回止损信息；否则返回 None
        """
        if symbol not in self.stop_loss_prices:
            return None

        stop_loss_price = self.stop_loss_prices[symbol]

        if current_price <= stop_loss_price:
            loss_percent = ((current_price - stop_loss_price) / stop_loss_price) * 100

            self.logger.warning(
                f"🛑 止损已触发: {symbol}\n"
                f"  当前: {current_price:.2f}\n"
                f"  止损: {stop_loss_price:.2f}\n"
                f"  亏损: {loss_percent:.2f}%"
            )

            # 移除止损记录
            del self.stop_loss_prices[symbol]

            return {
                'symbol': symbol,
                'current_price': current_price,
                'stop_loss_price': stop_loss_price,
                'loss_percent': loss_percent,
                'reason': '止损已触发'
            }

        return None

    def remove_position(self, symbol: str):
        """移除止损"""
        if symbol in self.stop_loss_prices:
            del self.stop_loss_prices[symbol]

    def update_stop_loss(self, symbol: str, new_stop_loss: float):
        """更新止损价格（用于移动止损等场景）"""
        if symbol in self.stop_loss_prices:
            old_stop = self.stop_loss_prices[symbol]
            self.stop_loss_prices[symbol] = new_stop_loss

            self.logger.info(
                f"📊 {symbol} 止损已更新: "
                f"{old_stop:.2f} → {new_stop_loss:.2f}"
            )
