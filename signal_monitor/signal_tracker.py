"""
信号追踪模块
追踪 Alpha 和 FOMO 信号的时间窗口，检测融合信号
"""

import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from logger import logger

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 信号时间窗口：2小时 (7200秒)
SIGNAL_WINDOW_SECONDS = 2 * 60 * 60


class SignalTracker:
    """
    追踪 Alpha (110) 和 FOMO (113) 信号的时间窗口
    检测同一标的在2小时内是否同时出现两种信号
    """

    def __init__(self, window_seconds=SIGNAL_WINDOW_SECONDS):
        """
        初始化信号追踪器

        Args:
            window_seconds: 时间窗口（秒），默认2小时
        """
        self.window_seconds = window_seconds
        # 存储格式: {symbol: {'alpha': [], 'fomo': []}}
        # 列表中每项: {'timestamp': xxx, 'price': xxx, 'message_id': xxx}
        self.signals = defaultdict(lambda: {'alpha': [], 'fomo': []})
        # 已发送过融合信号的标的（避免重复发送）
        # 格式: {symbol: last_sent_timestamp}
        self.sent_confluence_signals = {}
        # 融合信号冷却时间：发送后1小时内不再重复发送
        self.confluence_cooldown = 60 * 60  # 1小时

    def add_signal(self, symbol, signal_type, price, message_id, timestamp_ms):
        """
        添加一个信号到追踪器

        Args:
            symbol: 币种符号（如 'BTC'）
            signal_type: 信号类型 ('alpha' 或 'fomo')
            price: 价格
            message_id: 消息ID
            timestamp_ms: 时间戳（毫秒）

        Returns:
            bool: 如果检测到融合信号返回 True，否则返回 False
        """
        if not symbol or signal_type not in ['alpha', 'fomo']:
            return False

        # 清理过期信号
        self._clean_expired_signals(symbol, timestamp_ms)

        # 添加新信号
        signal_data = {
            'timestamp': timestamp_ms,
            'price': price,
            'message_id': message_id
        }
        self.signals[symbol][signal_type].append(signal_data)

        logger.info(f"📊 添加 {signal_type.upper()} 信号: ${symbol}, 价格: ${price}")

        # 检查是否形成融合信号
        return self._check_confluence(symbol, timestamp_ms)

    def _clean_expired_signals(self, symbol, current_timestamp_ms):
        """
        清理超过时间窗口的信号

        Args:
            symbol: 币种符号
            current_timestamp_ms: 当前时间戳（毫秒）
        """
        cutoff_time = current_timestamp_ms - (self.window_seconds * 1000)

        for signal_type in ['alpha', 'fomo']:
            # 过滤掉过期信号
            self.signals[symbol][signal_type] = [
                sig for sig in self.signals[symbol][signal_type]
                if sig['timestamp'] >= cutoff_time
            ]

    def _check_confluence(self, symbol, current_timestamp_ms):
        """
        检查是否存在融合信号（Alpha + FOMO 同时存在）

        Args:
            symbol: 币种符号
            current_timestamp_ms: 当前时间戳（毫秒）

        Returns:
            bool: 如果检测到融合信号返回 True，否则返回 False
        """
        alpha_signals = self.signals[symbol]['alpha']
        fomo_signals = self.signals[symbol]['fomo']

        # 必须同时有 Alpha 和 FOMO 信号
        if not alpha_signals or not fomo_signals:
            return False

        # 检查冷却时间（避免短时间内重复发送）
        last_sent = self.sent_confluence_signals.get(symbol, 0)
        if current_timestamp_ms - last_sent < (self.confluence_cooldown * 1000):
            logger.info(f"⏰ ${symbol} 融合信号在冷却期内，跳过")
            return False

        # 找到最新的 Alpha 和 FOMO 信号
        latest_alpha = max(alpha_signals, key=lambda x: x['timestamp'])
        latest_fomo = max(fomo_signals, key=lambda x: x['timestamp'])

        # 计算两个信号的时间差（毫秒转秒）
        time_diff = abs(latest_alpha['timestamp'] - latest_fomo['timestamp']) / 1000

        logger.info(f"🔍 ${symbol} 融合信号检测:")
        logger.info(f"   Alpha 信号: {len(alpha_signals)} 条, 最新价格: ${latest_alpha['price']}")
        logger.info(f"   FOMO 信号: {len(fomo_signals)} 条, 最新价格: ${latest_fomo['price']}")
        logger.info(f"   时间差: {time_diff:.0f} 秒 (窗口: {self.window_seconds} 秒)")

        # 如果两个信号都在时间窗口内，触发融合信号
        if time_diff <= self.window_seconds:
            logger.info(f"✅ 检测到 ${symbol} 融合信号！")
            # 记录发送时间
            self.sent_confluence_signals[symbol] = current_timestamp_ms
            return True

        return False

    def get_latest_price(self, symbol):
        """
        获取标的最新价格（从最近的信号中获取）

        Args:
            symbol: 币种符号

        Returns:
            float or None: 最新价格，如果没有信号返回 None
        """
        all_signals = (
            self.signals[symbol]['alpha'] +
            self.signals[symbol]['fomo']
        )

        if not all_signals:
            return None

        latest = max(all_signals, key=lambda x: x['timestamp'])
        return latest['price']

    def get_signal_summary(self, symbol):
        """
        获取标的的信号摘要

        Args:
            symbol: 币种符号

        Returns:
            dict: 包含 alpha_count, fomo_count, latest_price 等信息
        """
        alpha_count = len(self.signals[symbol]['alpha'])
        fomo_count = len(self.signals[symbol]['fomo'])
        latest_price = self.get_latest_price(symbol)

        return {
            'symbol': symbol,
            'alpha_count': alpha_count,
            'fomo_count': fomo_count,
            'latest_price': latest_price
        }


# 全局单例
_tracker_instance = None


def get_signal_tracker():
    """
    获取全局信号追踪器实例（单例模式）

    Returns:
        SignalTracker: 信号追踪器实例
    """
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = SignalTracker()
    return _tracker_instance
