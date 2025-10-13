"""
Binance 自动交易主程序
整合信号监控 + 信号聚合 + 自动交易执行
"""

import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# 添加父目录到路径，以便导入 signal_monitor 模块（如果需要集成）
sys.path.insert(0, str(Path(__file__).parent.parent))

from binance_trader.signal_aggregator import SignalAggregator
from binance_trader.risk_manager import RiskManager
from binance_trader.trader import BinanceTrader

# 导入配置
try:
    from binance_trader import config
except ImportError:
    print("❌ Error: config.py not found!")
    print("Please copy config.example.py to config.py and fill in your settings.")
    sys.exit(1)


class AutoTradingSystem:
    """自动交易系统主类"""

    def __init__(self):
        """初始化系统"""
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

        self.logger.info("="*80)
        self.logger.info("🚀 Initializing Binance Auto Trading System")
        self.logger.info("="*80)

        # 1. 初始化信号聚合器
        self.signal_aggregator = SignalAggregator(
            time_window=config.SIGNAL_TIME_WINDOW,
            min_score=config.MIN_SIGNAL_SCORE,
            enable_fomo_intensify=config.ENABLE_FOMO_INTENSIFY
        )

        # 2. 初始化风险管理器
        self.risk_manager = RiskManager(
            max_position_percent=config.MAX_POSITION_PERCENT,
            max_total_position_percent=config.MAX_TOTAL_POSITION_PERCENT,
            max_daily_trades=config.MAX_DAILY_TRADES,
            max_daily_loss_percent=config.MAX_DAILY_LOSS_PERCENT,
            stop_loss_percent=config.STOP_LOSS_PERCENT,
            take_profit_1_percent=config.TAKE_PROFIT_1_PERCENT,
            take_profit_2_percent=config.TAKE_PROFIT_2_PERCENT
        )

        # 3. 初始化币安交易器
        try:
            self.trader = BinanceTrader(
                api_key=config.BINANCE_API_KEY,
                api_secret=config.BINANCE_API_SECRET,
                risk_manager=self.risk_manager,
                testnet=config.USE_TESTNET
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize BinanceTrader: {e}")
            self.logger.error("Please check your API credentials in config.py")
            sys.exit(1)

        # 4. 更新账户余额
        self.trader.update_risk_manager_balance()

        # 状态跟踪
        self.last_balance_update = time.time()
        self.last_position_monitor = time.time()

        self.logger.info("✅ System initialized successfully")
        self._print_system_status()

    def _setup_logging(self):
        """配置日志系统"""
        log_dir = Path(config.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def _print_system_status(self):
        """打印系统状态"""
        status = self.risk_manager.get_status()

        self.logger.info("\n" + "="*80)
        self.logger.info("📊 SYSTEM STATUS")
        self.logger.info("="*80)
        self.logger.info(f"Trading Mode: {'TESTNET ⚠️' if config.USE_TESTNET else 'PRODUCTION 🔴'}")
        self.logger.info(f"Auto Trading: {'ENABLED ✅' if config.AUTO_TRADING_ENABLED else 'DISABLED (观察模式)'}")
        self.logger.info(f"Total Balance: {status['total_balance']:.2f} USDT")
        self.logger.info(f"Available Balance: {status['available_balance']:.2f} USDT")
        self.logger.info(f"Active Positions: {status['position_count']}")
        self.logger.info(f"Total Position Value: {status['total_position_value']:.2f} USDT ({status['total_position_percent']:.1f}%)")
        self.logger.info(f"Daily Trades: {status['daily_trades']}/{config.MAX_DAILY_TRADES}")
        self.logger.info(f"Daily PnL: {status['daily_pnl']:.2f} USDT")
        self.logger.info(f"Trading Status: {'ACTIVE' if status['trading_enabled'] else 'HALTED: ' + status['halt_reason']}")
        self.logger.info("="*80 + "\n")

    def process_signal(self, message_type: int, message_id: str, symbol: str, data: dict):
        """
        处理来自信号监控模块的信号

        Args:
            message_type: ValueScan 消息类型 (110=Alpha, 113=FOMO)
            message_id: 消息ID
            symbol: 交易标的（如 "BTC"）
            data: 原始消息数据
        """
        # 1. 添加到信号聚合器
        confluence = self.signal_aggregator.add_signal(
            message_type=message_type,
            message_id=message_id,
            symbol=symbol,
            data=data
        )

        # 2. 如果匹配到聚合信号
        if confluence:
            self.logger.warning("\n" + "🔥"*40)
            self.logger.warning(f"CONFLUENCE SIGNAL DETECTED: {confluence}")
            self.logger.warning("🔥"*40 + "\n")

            # 3. 检查是否启用自动交易
            if not config.AUTO_TRADING_ENABLED:
                self.logger.info("⏸️  Auto trading disabled, skipping execution (观察模式)")
                return

            # 4. 获取当前价格
            binance_symbol = f"{confluence.symbol}{config.SYMBOL_SUFFIX}"
            current_price = self.trader.get_symbol_price(binance_symbol)

            if not current_price:
                self.logger.error(f"Failed to get price for {binance_symbol}, skipping trade")
                return

            # 5. 生成交易建议
            recommendation = self.risk_manager.generate_trade_recommendation(
                symbol=confluence.symbol,
                current_price=current_price,
                signal_score=confluence.score
            )

            self.logger.info(f"Trade Recommendation: {recommendation.action} - {recommendation.reason}")

            # 6. 执行交易
            if recommendation.action == "BUY":
                success = self.trader.execute_trade(recommendation, config.SYMBOL_SUFFIX)

                if success:
                    self.logger.info("✅ Trade executed successfully")
                else:
                    self.logger.error("❌ Trade execution failed")

    def monitor_positions(self):
        """定期监控持仓"""
        now = time.time()

        if now - self.last_position_monitor >= config.POSITION_MONITOR_INTERVAL:
            self.trader.monitor_positions()
            self.last_position_monitor = now

    def update_balance(self):
        """定期更新余额"""
        now = time.time()

        if now - self.last_balance_update >= config.BALANCE_UPDATE_INTERVAL:
            self.trader.update_risk_manager_balance()
            self.last_balance_update = now

    def run_with_signal_monitor(self):
        """
        运行模式1：整合信号监控（推荐）
        自动启动 ValueScan 信号监控，并处理捕获的信号
        """
        self.logger.info("🔄 Starting integrated mode with signal monitor...")

        # 导入信号监控模块
        from signal_monitor.message_handler import process_response_data
        from signal_monitor.api_monitor import ValueScanMonitor

        # 创建监控器
        monitor = ValueScanMonitor()

        # 定义信号回调函数
        def on_new_message(message_type: int, message_id: str, symbol: str, data: dict):
            """当捕获到新信号时的回调"""
            # 只处理 FOMO 和 Alpha 信号
            if message_type in [110, 112, 113]:
                self.process_signal(message_type, message_id, symbol, data)

        self.logger.info("✅ Signal monitor integration ready")
        self.logger.info("Waiting for signals from ValueScan...")

        try:
            while True:
                # 这里需要与 signal_monitor 模块集成
                # 实际实现时，需要修改 message_handler 以支持回调
                self.logger.info("⚠️  Note: Full integration requires modifying signal_monitor module")
                self.logger.info("Please use standalone mode or implement callback mechanism")
                time.sleep(10)

                # 定期维护任务
                self.monitor_positions()
                self.update_balance()

        except KeyboardInterrupt:
            self.logger.info("\n🛑 Shutting down...")
            self._print_system_status()

    def run_standalone(self):
        """
        运行模式2：独立模式
        仅运行交易系统，手动调用 process_signal() 处理信号
        适合与外部信号源集成
        """
        self.logger.info("📡 Running in standalone mode")
        self.logger.info("Waiting for external signals via process_signal() method...")
        self.logger.info("Example usage:")
        self.logger.info("  system.process_signal(message_type=113, message_id='abc', symbol='BTC', data={})")

        try:
            while True:
                # 定期维护任务
                self.monitor_positions()
                self.update_balance()

                # 打印状态
                if time.time() % 300 < 1:  # 每5分钟
                    self._print_system_status()

                    # 打印信号统计
                    stats = self.signal_aggregator.get_pending_signals_count()
                    self.logger.info(
                        f"📊 Signal Buffer: "
                        f"FOMO={stats['fomo']} ({stats['symbols_with_fomo']} symbols), "
                        f"ALPHA={stats['alpha']} ({stats['symbols_with_alpha']} symbols)"
                    )

                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("\n🛑 Shutting down...")
            self._print_system_status()


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🚀 Binance Auto Trading System - ValueScan Signal Based")
    print("="*80)
    print("\nSelect running mode:")
    print("1. Integrated mode (with signal monitor) - Recommended")
    print("2. Standalone mode (manual signal input)")
    print("3. Test signal aggregation")
    print()

    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "3":
        # 测试模式
        test_signal_aggregation()
        return

    # 初始化系统
    system = AutoTradingSystem()

    if choice == "1":
        system.run_with_signal_monitor()
    elif choice == "2":
        system.run_standalone()
    else:
        print("Invalid choice")


def test_signal_aggregation():
    """测试信号聚合功能"""
    print("\n🧪 Testing Signal Aggregation...\n")

    aggregator = SignalAggregator(
        time_window=300,
        min_score=0.6,
        enable_fomo_intensify=True
    )

    # 模拟信号
    print("1️⃣ Adding FOMO signal for BTC...")
    result1 = aggregator.add_signal(113, "msg1", "BTC", {})
    print(f"   Result: {result1}\n")

    print("2️⃣ Adding Alpha signal for BTC...")
    result2 = aggregator.add_signal(110, "msg2", "BTC", {})
    print(f"   Result: {result2}\n")

    if result2:
        print("✅ Confluence detected successfully!")
        print(f"   Symbol: {result2.symbol}")
        print(f"   Time Gap: {result2.time_gap:.2f}s")
        print(f"   Score: {result2.score:.2f}")
    else:
        print("❌ No confluence detected (this shouldn't happen)")

    print("\n3️⃣ Adding FOMO signal for ETH (no Alpha)...")
    result3 = aggregator.add_signal(113, "msg3", "ETH", {})
    print(f"   Result: {result3} (expected None)\n")

    stats = aggregator.get_pending_signals_count()
    print(f"📊 Pending signals: {stats}")


if __name__ == "__main__":
    main()
