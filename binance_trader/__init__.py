"""
Binance Auto Trading Module
币安自动化交易模块 - 基于信号聚合的智能交易系统
"""

__version__ = "1.0.0"
__author__ = "ValueScan Team"

from .signal_aggregator import SignalAggregator
from .trader import BinanceTrader
from .risk_manager import RiskManager

__all__ = [
    'SignalAggregator',
    'BinanceTrader',
    'RiskManager',
]
