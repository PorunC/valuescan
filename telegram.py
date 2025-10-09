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
    格式化 AI 追踪告警（type 100）
    根据 predictType 区分不同场景：
    - predictType 4: 主力减持风险
    - predictType 19: 追踪后跌幅超过15%（下跌止盈）
    - predictType 31: 追踪后跌幅超过5%（保护本金）
    """
    from config import TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
    
    symbol = content.get('symbol', 'N/A')
    price = content.get('price', 'N/A')
    change_24h = content.get('percentChange24h', 0)
    predict_type = content.get('predictType', 0)
    risk_decline = content.get('riskDecline', 0)
    rebound = content.get('rebound', 0)
    scoring = content.get('scoring', 0)
    
    # 根据 predictType 判断场景
    if predict_type == 4:
        # 主力减持风险
        emoji = "⚠️"
        title = f"<b>{symbol} 疑似主力减持</b>"
        risk_desc = "主力持仓减少，注意市场风险"
        tag = "#主力减持"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━━━━━━━━━━━",
            f"📉 {risk_desc}",
            f"💵 现价: <b>${price}</b>",
            f"📊 24H: <code>{change_24h:+.2f}%</code>",
        ]
        
        if scoring:
            message_parts.append(f"🎯 AI评分: <b>{int(scoring)}</b>")
        
        message_parts.extend([
            f"",
            f"💡 操作建议:",
            f"   • 谨慎追高，等待企稳",
            f"   • 已持仓可考虑减仓观望",
            f"",
            f"{tag}",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 19:
        # 追踪后跌幅超过15% - 下跌止盈
        emoji = "�"
        title = f"<b>{symbol} 下跌止盈信号</b>"
        risk_desc = f"AI追踪后下跌，跌幅已超过 {risk_decline:.2f}%"
        tag = "#下跌止盈"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━━━━━━━━━━━",
            f"⚠️ {risk_desc}",
            f"💵 现价: <b>${price}</b>",
            f"📉 风险跌幅: <code>-{risk_decline:.2f}%</code>",
        ]
        
        if rebound:
            message_parts.append(f"📈 反弹幅度: <code>{rebound:+.2f}%</code>")
        
        message_parts.extend([
            f"",
            f"� 操作建议:",
            f"   • <b>移动止盈，保护利润</b>",
            f"   • 避免回吐过多收益",
            f"   • 等待新的入场机会",
            f"",
            f"{tag}",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 31:
        # 追踪后跌幅5-15% - 保护本金
        emoji = "🟠"
        title = f"<b>{symbol} 本金保护警示</b>"
        risk_desc = f"AI追踪后下跌，跌幅已达 {risk_decline:.2f}%"
        tag = "#保护本金"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━━━━━━━━━━━",
            f"⚠️ {risk_desc}",
            f"💵 现价: <b>${price}</b>",
            f"� 风险跌幅: <code>-{risk_decline:.2f}%</code>",
        ]
        
        if scoring:
            message_parts.append(f"🎯 AI评分: <b>{int(scoring)}</b>")
        if rebound:
            message_parts.append(f"📈 反弹幅度: <code>{rebound:+.2f}%</code>")
        
        message_parts.extend([
            f"",
            f"💡 操作建议:",
            f"   • <b>注意保护本金</b>",
            f"   • 设置止损位，控制风险",
            f"   • 观察是否企稳反弹",
            f"",
            f"{tag}",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    else:
        # 其他类型 - 通用格式
        emoji = "📊"
        message_parts = [
            f"{emoji} <b>【AI追踪】{symbol}</b>",
            f"━━━━━━━━━━━━━━━━━━━",
            f"� 现价: <b>${price}</b>",
            f"📊 24H: <code>{change_24h:+.2f}%</code>",
        ]
        
        if risk_decline:
            message_parts.append(f"📉 风险跌幅: <code>-{risk_decline:.2f}%</code>")
        if rebound:
            message_parts.append(f"📈 反弹幅度: <code>{rebound:+.2f}%</code>")
        if scoring:
            message_parts.append(f"🎯 AI评分: <b>{int(scoring)}</b>")
        
        message_parts.append(f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}")
    
    return "\n".join(message_parts)


def _format_general_message(item, content, msg_type, msg_type_name):
    """
    格式化通用消息（资金异动、Alpha等）
    特别优化 type 111（资金出逃）的提示
    """
    from config import TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
    
    symbol = content.get('symbol', 'N/A')
    price = content.get('price', 'N/A')
    change_24h = content.get('percentChange24h', 0)
    funds_type = content.get('fundsMovementType', 0)
    
    # Type 111 资金出逃 - 特殊格式
    if msg_type == 111:
        emoji = "🚨"
        title = f"<b>{symbol} 主力资金出逃</b>"
        tag = "#追踪结束"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━━━━━━━━━━━",
            f"⚠️ 疑似主力资金已出逃",
            f"📊 资金异动监控结束",
            f"💵 现价: <b>${price}</b>",
            f"� 24H: <code>{change_24h:+.2f}%</code>",
            f"",
            f"💡 操作建议:",
            f"   • <b>注意市场风险</b>",
            f"   • 已持仓建议及时止盈/止损",
            f"   • 观望为主，等待企稳信号",
            f"",
            f"{tag}",
            f"� {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ]
        
        return "\n".join(message_parts)
    
    # Type 110 Alpha - 优化格式
    elif msg_type == 110:
        emoji = "⭐"
        funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
        
        message_parts = [
            f"{emoji} <b>【Alpha】{symbol}</b>",
            f"━━━━━━━━━━━━━━━━━━━",
            f"💰 资金状态: {funds_text}",
            f"💵 现价: <b>${price}</b>",
        ]
        
        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")
        
        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP.get(trade_type, 'N/A')
            message_parts.append(f"📊 类型: {trade_text}")
        
        message_parts.extend([
            f"",
            f"💡 潜力标的，可关注后续表现",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
        
        return "\n".join(message_parts)
    
    # Type 108 资金异动
    elif msg_type == 108:
        emoji = "💰"
        funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
        
        message_parts = [
            f"{emoji} <b>【资金异动】{symbol}</b>",
            f"━━━━━━━━━━━━━━━━━━━",
            f"💼 资金流向: {funds_text}",
            f"💵 现价: <b>${price}</b>",
        ]
        
        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")
        
        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP.get(trade_type, 'N/A')
            message_parts.append(f"📊 类型: {trade_text}")
        
        message_parts.append(f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}")
        
        return "\n".join(message_parts)
    
    # 其他类型 - 通用格式
    else:
        type_emoji_map = {
            109: "📢",  # 上下币公告
            113: "🚀"   # FOMO
        }
        emoji = type_emoji_map.get(msg_type, "📋")
        
        message_parts = [
            f"{emoji} <b>【{msg_type_name}】{symbol}</b>",
            f"━━━━━━━━━━━━━━━━━━━",
        ]
        
        if price:
            message_parts.append(f"💵 现价: <b>${price}</b>")
        
        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")
        
        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP.get(trade_type, 'N/A')
            message_parts.append(f"📊 类型: {trade_text}")
        
        if 'fundsMovementType' in content and funds_type:
            funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
            message_parts.append(f"💼 资金: {funds_text}")
        
        if 'source' in content:
            message_parts.append(f"📰 来源: {content.get('source', 'N/A')}")
        
        if 'titleSimplified' in content:
            message_parts.append(f"")
            message_parts.append(f"💬 {content.get('titleSimplified', 'N/A')}")
        
        message_parts.append(f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}")
        
        return "\n".join(message_parts)
