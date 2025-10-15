"""
信号聚合器 - Signal Aggregator
实现多信号confluence策略，在时间窗口内匹配 FOMO 和 Alpha 信号
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import logging


@dataclass
class Signal:
    """交易信号数据结构"""
    signal_id: str
    symbol: str  # 交易对，如 "BTC"
    signal_type: str  # "FOMO" (113) 或 "ALPHA" (110)
    timestamp: datetime
    message_type: int  # 原始消息类型
    data: Dict  # 原始信号数据

    def __hash__(self):
        return hash(self.signal_id)


@dataclass
class ConfluenceSignal:
    """聚合信号 - 同时满足 FOMO 和 Alpha 的标的"""
    symbol: str
    fomo_signal: Signal
    alpha_signal: Signal
    confluence_time: datetime
    time_gap: float  # 两个信号之间的时间差（秒）
    score: float = 0.0  # 信号强度评分

    def __str__(self):
        return (f"ConfluenceSignal({self.symbol}, "
                f"gap={self.time_gap:.1f}s, score={self.score:.2f})")


class SignalAggregator:
    """
    信号聚合器

    核心功能：
    1. 接收来自 ValueScan 的实时信号流
    2. 在时间窗口内匹配 FOMO (Type 113) + Alpha (Type 110) 信号
    3. 计算信号强度评分
    4. 输出高质量的聚合信号供交易执行

    策略原理：
    - FOMO 信号表示市场情绪高涨，可能出现快速上涨
    - Alpha 信号表示存在超额收益机会
    - 两个信号在短时间内同时出现 = 高概率交易机会
    """

    # 消息类型映射
    FOMO_TYPE = 113  # FOMO 信号（买入信号）
    FOMO_INTENSIFY_TYPE = 112  # FOMO 加剧（风险信号，应止盈）
    ALPHA_TYPE = 110  # Alpha 机会

    def __init__(self,
                 time_window: int = 300,  # 时间窗口（秒），默认5分钟
                 min_score: float = 0.6):  # 最低信号评分
        """
        初始化信号聚合器

        Args:
            time_window: 信号匹配时间窗口（秒）
            min_score: 最低信号评分阈值（0-1）

        注意：
            - Type 113 (FOMO) 视为买入信号
            - Type 112 (FOMO加剧) 视为风险信号，用于触发止盈
        """
        self.time_window = time_window
        self.min_score = min_score

        # 活跃信号缓存 - 按标的分组
        self.fomo_signals: Dict[str, List[Signal]] = defaultdict(list)  # Type 113
        self.alpha_signals: Dict[str, List[Signal]] = defaultdict(list)  # Type 110
        self.risk_signals: Dict[str, List[Signal]] = defaultdict(list)  # Type 112 风险信号

        # 已匹配的聚合信号
        self.confluence_signals: List[ConfluenceSignal] = []

        # 已处理的信号ID（防重复）
        self.processed_signal_ids: Set[str] = set()

        self.logger = logging.getLogger(__name__)

        self.logger.info(
            f"信号聚合器已初始化: "
            f"时间窗口={time_window}秒, 最低评分={min_score}"
        )
        self.logger.info("📊 信号类型: Type 113 (FOMO) + Type 110 (Alpha) = 买入")
        self.logger.info("⚠️  信号类型: Type 112 (FOMO加剧) = 风险信号 (应止盈)")


    def add_signal(self, message_type: int, message_id: str,
                   symbol: str, data: Dict) -> Optional[ConfluenceSignal]:
        """
        添加新信号并尝试匹配

        Args:
            message_type: 消息类型 (110=Alpha, 113=FOMO, 112=FOMO加剧)
            message_id: 消息唯一ID
            symbol: 交易标的（如 "BTC", "ETH"）
            data: 原始消息数据

        Returns:
            如果匹配成功，返回 ConfluenceSignal；否则返回 None
        """
        # 防重复
        if message_id in self.processed_signal_ids:
            self.logger.debug(f"信号 {message_id} 已处理过，跳过")
            return None

        # 判断信号类型
        signal_type = self._get_signal_type(message_type)
        if not signal_type:
            self.logger.debug(f"消息类型 {message_type} 不在追踪范围内")
            return None

        # 创建信号对象
        signal = Signal(
            signal_id=message_id,
            symbol=symbol.upper(),
            signal_type=signal_type,
            timestamp=datetime.now(),
            message_type=message_type,
            data=data
        )

        # 添加到对应缓存
        if signal_type == "FOMO":
            self.fomo_signals[signal.symbol].append(signal)
            self.logger.info(f"📢 新 FOMO 信号: {signal.symbol} (Type 113)")
        elif signal_type == "ALPHA":
            self.alpha_signals[signal.symbol].append(signal)
            self.logger.info(f"🎯 新 Alpha 信号: {signal.symbol} (Type 110)")
        elif signal_type == "RISK":
            self.risk_signals[signal.symbol].append(signal)
            self.logger.warning(f"⚠️  风险信号检测到: {signal.symbol} (Type 112 - FOMO加剧，建议止盈)")

        self.processed_signal_ids.add(message_id)

        # 清理过期信号
        self._cleanup_expired_signals()

        # 尝试匹配聚合信号
        confluence = self._try_match_confluence(signal.symbol)

        if confluence:
            self.logger.warning(
                f"🔥 信号聚合成功: {confluence.symbol} "
                f"(时间差={confluence.time_gap:.1f}秒, 评分={confluence.score:.2f})"
            )
            self.confluence_signals.append(confluence)

        return confluence

    def _get_signal_type(self, message_type: int) -> Optional[str]:
        """判断消息类型"""
        if message_type == self.ALPHA_TYPE:
            return "ALPHA"
        elif message_type == self.FOMO_TYPE:
            return "FOMO"
        elif message_type == self.FOMO_INTENSIFY_TYPE:
            return "RISK"  # FOMO加剧视为风险信号
        return None

    def check_risk_signal(self, symbol: str) -> bool:
        """
        检查指定标的是否有风险信号

        Returns:
            True if 有风险信号（应止盈）
        """
        return len(self.risk_signals.get(symbol, [])) > 0

    def _try_match_confluence(self, symbol: str) -> Optional[ConfluenceSignal]:
        """
        尝试为指定标的匹配聚合信号

        匹配逻辑：
        1. 检查该标的是否同时有 FOMO 和 Alpha 信号
        2. 计算时间差，确保在时间窗口内
        3. 计算信号强度评分
        4. 如果评分达标，返回聚合信号
        """
        fomo_list = self.fomo_signals.get(symbol, [])
        alpha_list = self.alpha_signals.get(symbol, [])

        if not fomo_list or not alpha_list:
            return None

        # 找到最佳匹配（时间最接近的一对）
        best_match = None
        min_gap = float('inf')

        for fomo in fomo_list:
            for alpha in alpha_list:
                time_gap = abs((fomo.timestamp - alpha.timestamp).total_seconds())

                if time_gap < self.time_window and time_gap < min_gap:
                    min_gap = time_gap
                    best_match = (fomo, alpha, time_gap)

        if not best_match:
            return None

        fomo_signal, alpha_signal, time_gap = best_match

        # 计算信号评分
        score = self._calculate_score(fomo_signal, alpha_signal, time_gap)

        if score < self.min_score:
            self.logger.info(
                f"找到 {symbol} 的信号匹配，但评分 {score:.2f} < {self.min_score}，跳过"
            )
            return None

        # 创建聚合信号
        confluence = ConfluenceSignal(
            symbol=symbol,
            fomo_signal=fomo_signal,
            alpha_signal=alpha_signal,
            confluence_time=datetime.now(),
            time_gap=time_gap,
            score=score
        )

        # 从缓存中移除已匹配的信号（避免重复匹配）
        self.fomo_signals[symbol].remove(fomo_signal)
        self.alpha_signals[symbol].remove(alpha_signal)

        return confluence

    def _calculate_score(self, fomo: Signal, alpha: Signal, time_gap: float) -> float:
        """
        计算信号强度评分（0-1）

        评分因素：
        1. 时间接近度 (40%权重): 两信号时间越近越好
        2. FOMO 强度 (30%权重): Type 112 (FOMO加剧) > Type 113
        3. 信号新鲜度 (30%权重): 信号越新越好
        """
        # 1. 时间接近度评分 (时间差越小，分数越高)
        time_score = 1.0 - (time_gap / self.time_window)
        time_score = max(0, min(1, time_score))  # 限制在 [0, 1]

        # 2. FOMO 强度评分
        fomo_strength = 1.0 if fomo.message_type == self.FOMO_INTENSIFY_TYPE else 0.8

        # 3. 信号新鲜度评分 (距离现在越近越好，最多考虑1小时)
        now = datetime.now()
        avg_age = (
            (now - fomo.timestamp).total_seconds() +
            (now - alpha.timestamp).total_seconds()
        ) / 2
        freshness_score = 1.0 - min(avg_age / 3600, 1.0)  # 1小时后为0

        # 加权计算总分
        total_score = (
            time_score * 0.4 +
            fomo_strength * 0.3 +
            freshness_score * 0.3
        )

        self.logger.debug(
            f"{fomo.symbol} 评分计算: "
            f"时间接近度={time_score:.2f}, FOMO强度={fomo_strength:.2f}, "
            f"新鲜度={freshness_score:.2f} -> 总分={total_score:.2f}"
        )

        return total_score

    def _cleanup_expired_signals(self):
        """清理过期信号（超过时间窗口的信号）"""
        cutoff = datetime.now() - timedelta(seconds=self.time_window * 2)

        for symbol in list(self.fomo_signals.keys()):
            self.fomo_signals[symbol] = [
                s for s in self.fomo_signals[symbol]
                if s.timestamp > cutoff
            ]
            if not self.fomo_signals[symbol]:
                del self.fomo_signals[symbol]

        for symbol in list(self.alpha_signals.keys()):
            self.alpha_signals[symbol] = [
                s for s in self.alpha_signals[symbol]
                if s.timestamp > cutoff
            ]
            if not self.alpha_signals[symbol]:
                del self.alpha_signals[symbol]

        # 清理风险信号（保留更短时间，30分钟）
        risk_cutoff = datetime.now() - timedelta(seconds=1800)
        for symbol in list(self.risk_signals.keys()):
            self.risk_signals[symbol] = [
                s for s in self.risk_signals[symbol]
                if s.timestamp > risk_cutoff
            ]
            if not self.risk_signals[symbol]:
                del self.risk_signals[symbol]

    def get_pending_signals_count(self) -> Dict[str, int]:
        """获取待匹配信号数量统计"""
        return {
            "fomo": sum(len(signals) for signals in self.fomo_signals.values()),
            "alpha": sum(len(signals) for signals in self.alpha_signals.values()),
            "risk": sum(len(signals) for signals in self.risk_signals.values()),
            "symbols_with_fomo": len(self.fomo_signals),
            "symbols_with_alpha": len(self.alpha_signals),
            "symbols_with_risk": len(self.risk_signals)
        }

    def get_recent_confluences(self, limit: int = 10) -> List[ConfluenceSignal]:
        """获取最近的聚合信号"""
        return sorted(
            self.confluence_signals,
            key=lambda x: x.confluence_time,
            reverse=True
        )[:limit]
