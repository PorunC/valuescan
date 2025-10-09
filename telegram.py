"""
Telegram 消息发送模块
负责格式化消息并发送到 Telegram Bot
"""

import json
import time
import requests
from logger import logger
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message_text):
    """
    发送消息到 Telegram
    
    Args:
        message_text: 要发送的消息文本（支持 HTML 格式）
    
    Returns:
        bool: 发送成功返回 True，否则返回 False
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("  ⚠️ Telegram Bot Token 未配置，跳过发送")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("  ✅ Telegram 消息发送成功")
            return True
        else:
            logger.error(f"  ❌ Telegram 消息发送失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"  ❌ Telegram 消息发送异常: {e}")
        return False


def format_message_for_telegram(item):
    """
    格式化消息为 Telegram HTML 格式
    
    Args:
        item: 消息数据字典
    
    Returns:
        str: 格式化后的 HTML 消息文本
    """
    from config import MESSAGE_TYPE_MAP, TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
    
    msg_type = item.get('type', 'N/A')
    msg_type_name = MESSAGE_TYPE_MAP.get(msg_type, 'N/A') if isinstance(msg_type, int) else 'N/A'
    
    # 解析 content 字段
    content = {}
    if 'content' in item and item['content']:
        try:
            content = json.loads(item['content'])
        except json.JSONDecodeError:
            pass
    
    # 根据消息类型使用不同的格式
    if msg_type == 100:  # 下跌风险 - 特殊格式
        return _format_risk_alert(item, content, msg_type_name)
    else:  # 其他类型 - 通用格式
        return _format_general_message(item, content, msg_type, msg_type_name)


def _format_risk_alert(item, content, msg_type_name):
    """
    格式化下跌风险告警（type 100）
    """
    from config import TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
    
    symbol = content.get('symbol', 'N/A')
    price = content.get('price', 'N/A')
    change_24h = content.get('percentChange24h', 0)
    risk_decline = content.get('riskDecline', 0)
    rebound = content.get('rebound', 0)
    
    # 风险等级判断
    if risk_decline >= 15:
        risk_emoji = "🔴"
        risk_level = "高风险"
    elif risk_decline >= 10:
        risk_emoji = "🟠"
        risk_level = "中风险"
    else:
        risk_emoji = "🟡"
        risk_level = "低风险"
    
    message_parts = [
        f"{risk_emoji} <b>【{msg_type_name}】${symbol}</b>",
        f"━━━━━━━━━━━━━━━━━━━",
        f"⚠️ <b>风险等级:</b> {risk_level}",
        f"📉 <b>风险跌幅:</b> {risk_decline}%",
        f"💵 <b>当前价格:</b> ${price}",
        f"📊 <b>24H涨跌:</b> {change_24h}%",
    ]
    
    if rebound:
        message_parts.append(f"� <b>反弹幅度:</b> {rebound}%")
    
    message_parts.extend([
        f"━━━━━━━━━━━━━━━━━━━",
        f"💡 <b>建议:</b> 移动止盈，保护利润",
        f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
    ])
    
    return "\n".join(message_parts)


def _format_general_message(item, content, msg_type, msg_type_name):
    """
    格式化通用消息（资金异动、Alpha等）
    """
    from config import TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
    
    symbol = content.get('symbol', 'N/A')
    
    # 根据消息类型选择表情
    type_emoji_map = {
        108: "💰",  # 资金异动
        109: "📢",  # 上下币公告
        110: "⭐",  # Alpha
        111: "🏃",  # 资金出逃
        113: "🚀"   # FOMO
    }
    emoji = type_emoji_map.get(msg_type, "📋")
    
    message_parts = [
        f"{emoji} <b>【{msg_type_name}】${symbol}</b>",
        f"━━━━━━━━━━━━━━━━━━━",
    ]
    
    if 'price' in content:
        message_parts.append(f"💵 <b>价格:</b> ${content.get('price', 'N/A')}")
    
    if 'percentChange24h' in content:
        change = content.get('percentChange24h', 0)
        emoji = "📈" if change > 0 else "📉"
        message_parts.append(f"{emoji} <b>24H涨跌:</b> {change}%")
    
    if 'tradeType' in content:
        trade_type = content.get('tradeType')
        trade_text = TRADE_TYPE_MAP.get(trade_type, 'N/A')
        message_parts.append(f"📊 <b>交易类型:</b> {trade_text}")
    
    if 'fundsMovementType' in content:
        funds_type = content.get('fundsMovementType')
        funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
        message_parts.append(f"💼 <b>资金流向:</b> {funds_text}")
    
    if 'source' in content:
        message_parts.append(f"📰 <b>来源:</b> {content.get('source', 'N/A')}")
    
    if 'titleSimplified' in content:
        message_parts.append(f"💬 {content.get('titleSimplified', 'N/A')}")
    
    message_parts.extend([
        f"━━━━━━━━━━━━━━━━━━━",
        f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
    ])
    
    return "\n".join(message_parts)
