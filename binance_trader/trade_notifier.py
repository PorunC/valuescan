"""
交易通知模块 - Trade Notifier
负责发送交易事件的 Telegram 通知
"""

import sys
import os
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TradeNotifier:
    """交易通知器 - 发送 Telegram 通知"""

    def __init__(self, bot_token: str = "", chat_id: str = "", enabled: bool = True):
        """
        初始化交易通知器

        Args:
            bot_token: Telegram Bot Token
            chat_id: Telegram Chat ID
            enabled: 是否启用通知
        """
        self.enabled = enabled
        self.bot_token = bot_token
        self.chat_id = chat_id

        # 如果未提供 token/chat_id，尝试从信号监控模块读取
        if not self.bot_token or not self.chat_id:
            try:
                # 添加父目录到 Python 路径
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                signal_monitor_path = os.path.join(parent_dir, 'signal_monitor')
                sys.path.insert(0, signal_monitor_path)

                from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
                self.bot_token = self.bot_token or TELEGRAM_BOT_TOKEN
                self.chat_id = self.chat_id or TELEGRAM_CHAT_ID
                logger.info("✅ 已从信号监控模块加载 Telegram 配置")
            except ImportError:
                logger.warning("⚠️  无法从信号监控模块加载 Telegram 配置")
                self.enabled = False

        if self.enabled and self.bot_token and self.chat_id:
            logger.info("✅ Telegram 交易通知已启用")
        else:
            logger.warning("⚠️  Telegram 交易通知未启用")
            self.enabled = False

    def _send_message(self, text: str, pin: bool = False) -> bool:
        """
        发送 Telegram 消息

        Args:
            text: 消息文本（支持 HTML 格式）
            pin: 是否置顶消息

        Returns:
            是否发送成功
        """
        if not self.enabled:
            logger.debug("Telegram 通知未启用，跳过发送")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.debug("✅ Telegram 消息发送成功")

                # 置顶消息
                if pin:
                    message_id = response.json()['result']['message_id']
                    pin_url = f"https://api.telegram.org/bot{self.bot_token}/pinChatMessage"
                    requests.post(pin_url, json={
                        'chat_id': self.chat_id,
                        'message_id': message_id,
                        'disable_notification': True
                    }, timeout=10)

                return True
            else:
                logger.error(f"❌ Telegram 消息发送失败: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Telegram 消息发送异常: {e}")
            return False

    def notify_open_position(self, symbol: str, side: str, quantity: float,
                            price: float, leverage: int, stop_loss: float,
                            take_profit: float, reason: str) -> bool:
        """
        开仓通知

        Args:
            symbol: 交易对
            side: 方向 (LONG/SHORT)
            quantity: 数量
            price: 开仓价格
            leverage: 杠杆倍数
            stop_loss: 止损价格
            take_profit: 止盈价格
            reason: 开仓原因

        Returns:
            是否发送成功
        """
        side_emoji = "🟢" if side == "LONG" else "🔴"
        side_text = "做多" if side == "LONG" else "做空"

        message = f"""
{side_emoji} <b>开仓通知</b>

📊 <b>交易对</b>: {symbol}
📈 <b>方向</b>: {side_text} ({side})
💰 <b>数量</b>: {quantity:.6f}
💵 <b>开仓价</b>: ${price:.6f}
⚡ <b>杠杆</b>: {leverage}x
🛡️ <b>止损</b>: ${stop_loss:.6f}
🎯 <b>止盈</b>: ${take_profit:.6f}

💡 <b>原因</b>: {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self._send_message(message.strip(), pin=False)

    def notify_close_position(self, symbol: str, side: str, quantity: float,
                             entry_price: float, exit_price: float,
                             pnl: float, pnl_percent: float, reason: str) -> bool:
        """
        平仓通知

        Args:
            symbol: 交易对
            side: 方向
            quantity: 数量
            entry_price: 开仓价格
            exit_price: 平仓价格
            pnl: 盈亏金额
            pnl_percent: 盈亏百分比
            reason: 平仓原因

        Returns:
            是否发送成功
        """
        pnl_emoji = "💚" if pnl > 0 else "❤️"
        pnl_sign = "+" if pnl > 0 else ""

        message = f"""
{pnl_emoji} <b>平仓通知</b>

📊 <b>交易对</b>: {symbol}
📈 <b>方向</b>: {'做多' if side == 'LONG' else '做空'}
💰 <b>数量</b>: {quantity:.6f}
💵 <b>开仓价</b>: ${entry_price:.6f}
💵 <b>平仓价</b>: ${exit_price:.6f}
📊 <b>盈亏</b>: {pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_percent:.2f}%)

💡 <b>原因</b>: {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self._send_message(message.strip(), pin=False)

    def notify_stop_loss(self, symbol: str, side: str, quantity: float,
                        entry_price: float, stop_price: float,
                        loss: float, loss_percent: float) -> bool:
        """
        止损触发通知

        Args:
            symbol: 交易对
            side: 方向
            quantity: 数量
            entry_price: 开仓价格
            stop_price: 止损价格
            loss: 亏损金额
            loss_percent: 亏损百分比

        Returns:
            是否发送成功
        """
        message = f"""
🛑 <b>止损触发</b>

📊 <b>交易对</b>: {symbol}
📈 <b>方向</b>: {'做多' if side == 'LONG' else '做空'}
💰 <b>数量</b>: {quantity:.6f}
💵 <b>开仓价</b>: ${entry_price:.6f}
💵 <b>止损价</b>: ${stop_price:.6f}
📉 <b>亏损</b>: -${abs(loss):.2f} ({loss_percent:.2f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self._send_message(message.strip(), pin=False)

    def notify_take_profit(self, symbol: str, side: str, quantity: float,
                          entry_price: float, tp_price: float,
                          profit: float, profit_percent: float, level: int = 1) -> bool:
        """
        止盈触发通知

        Args:
            symbol: 交易对
            side: 方向
            quantity: 数量
            entry_price: 开仓价格
            tp_price: 止盈价格
            profit: 盈利金额
            profit_percent: 盈利百分比
            level: 止盈级别

        Returns:
            是否发送成功
        """
        message = f"""
✅ <b>止盈触发 (级别 {level})</b>

📊 <b>交易对</b>: {symbol}
📈 <b>方向</b>: {'做多' if side == 'LONG' else '做空'}
💰 <b>数量</b>: {quantity:.6f}
💵 <b>开仓价</b>: ${entry_price:.6f}
💵 <b>止盈价</b>: ${tp_price:.6f}
📈 <b>盈利</b>: +${profit:.2f} (+{profit_percent:.2f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self._send_message(message.strip(), pin=False)

    def notify_partial_close(self, symbol: str, side: str, closed_qty: float,
                            remaining_qty: float, close_percent: float,
                            current_price: float, pnl: float, reason: str) -> bool:
        """
        部分平仓通知

        Args:
            symbol: 交易对
            side: 方向
            closed_qty: 已平仓数量
            remaining_qty: 剩余数量
            close_percent: 平仓比例
            current_price: 当前价格
            pnl: 盈亏
            reason: 原因

        Returns:
            是否发送成功
        """
        pnl_emoji = "💚" if pnl > 0 else "❤️"
        pnl_sign = "+" if pnl > 0 else ""

        message = f"""
{pnl_emoji} <b>部分平仓</b>

📊 <b>交易对</b>: {symbol}
📈 <b>方向</b>: {'做多' if side == 'LONG' else '做空'}
💰 <b>平仓比例</b>: {close_percent:.0f}%
📊 <b>已平</b>: {closed_qty:.6f}
📊 <b>剩余</b>: {remaining_qty:.6f}
💵 <b>当前价</b>: ${current_price:.6f}
📊 <b>盈亏</b>: {pnl_sign}${pnl:.2f}

💡 <b>原因</b>: {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self._send_message(message.strip(), pin=False)

    def notify_error(self, error_type: str, symbol: str, message: str) -> bool:
        """
        错误通知

        Args:
            error_type: 错误类型
            symbol: 交易对
            message: 错误消息

        Returns:
            是否发送成功
        """
        text = f"""
⚠️ <b>交易错误</b>

🔴 <b>类型</b>: {error_type}
📊 <b>交易对</b>: {symbol}
💬 <b>消息</b>: {message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self._send_message(text.strip(), pin=False)


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    # 测试通知器
    notifier = TradeNotifier()

    if notifier.enabled:
        print("\n测试开仓通知...")
        notifier.notify_open_position(
            symbol="BTCUSDT",
            side="LONG",
            quantity=0.1,
            price=50000.0,
            leverage=10,
            stop_loss=49000.0,
            take_profit=52000.0,
            reason="信号聚合评分 0.85"
        )

        print("\n测试平仓通知...")
        notifier.notify_close_position(
            symbol="BTCUSDT",
            side="LONG",
            quantity=0.1,
            entry_price=50000.0,
            exit_price=52000.0,
            pnl=200.0,
            pnl_percent=4.0,
            reason="止盈目标达成"
        )
    else:
        print("Telegram 通知未启用，请配置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
