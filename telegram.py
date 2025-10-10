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
    - predictType 5: AI 开始追踪潜力代币
    - predictType 16: 追踪后涨幅超过20%（上涨止盈）
    - predictType 19: 追踪后跌幅超过15%（下跌止盈）
    - predictType 24: 价格高点风险（疑似顶部）
    - predictType 29: 主力持仓减少加速
    - predictType 31: 追踪后跌幅超过5%（保护本金）
    """
    from config import TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
    
    symbol = content.get('symbol', 'N/A')
    price = content.get('price', 'N/A')
    change_24h = content.get('percentChange24h', 0)
    predict_type = content.get('predictType', 0)
    risk_decline = content.get('riskDecline', 0)
    gains = content.get('gains', 0)
    rebound = content.get('rebound', 0)
    scoring = content.get('scoring', 0)
    
    # 根据 predictType 判断场景
    if predict_type == 24:
        # 价格高点风险（疑似顶部）
        emoji = "📍"
        title = f"<b>${symbol} 价格高点警示</b>"
        tag = "#下跌风险"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ AI捕获疑似价格<b>高点</b>，注意回调风险",
            f"💵 现价: <b>${price}</b>",
        ]
        
        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            change_text = "涨幅" if change_24h >= 0 else "跌幅"
            message_parts.append(f"{change_emoji} 24H{change_text}: <code>{change_24h:+.2f}%</code>")
            
            # 如果涨幅较大，额外提示
            if change_24h > 10:
                message_parts.append(f"🔥 短期涨幅较大，回调风险增加")
        
        if scoring:
            score_int = int(scoring)
            message_parts.append(f"🎯 AI评分: <b>{score_int}</b>")
        
        message_parts.extend([
            f"",
            f"💡 风险提示:",
            f"   • ⚠️ <b>疑似价格顶部区域</b>",
            f"   • 📉 可能面临回调压力",
            f"   • 🛑 不建议追高，谨慎买入",
            f"   • 💰 已持仓可考虑分批减仓",
            f"   • 👀 AI 开始实时追踪走势",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 5:
        # AI 开始追踪潜力代币
        emoji = "🔍"
        title = f"<b>${symbol} AI 开始追踪</b>"
        tag = "#观察代币"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"🤖 AI捕获潜力代币，开始实时追踪",
            f"💵 现价: <b>${price}</b>",
        ]
        
        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            change_text = "涨幅" if change_24h >= 0 else "跌幅"
            message_parts.append(f"{change_emoji} 24H{change_text}: <code>{change_24h:+.2f}%</code>")
        
        if scoring:
            # 根据评分给出不同的评价
            score_int = int(scoring)
            if score_int >= 70:
                score_desc = "⭐⭐⭐ 高分"
            elif score_int >= 60:
                score_desc = "⭐⭐ 中上"
            elif score_int >= 50:
                score_desc = "⭐ 中等"
            else:
                score_desc = "观察中"
            message_parts.append(f"🎯 AI评分: <b>{score_int}</b> ({score_desc})")
        
        message_parts.extend([
            f"",
            f"💡 提示:",
            f"   • 🔍 AI 已开始实时监控",
            f"   • 📊 关注后续价格和资金动态",
            f"   • 🎯 等待更明确的入场信号",
            f"   • ⚠️ 追踪≠建议买入，注意风险",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 29:
        # 主力持仓减少加速
        emoji = "🚨"
        title = f"<b>${symbol} 主力加速减持</b>"
        tag = "#持仓减少加速"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ 疑似主力<b>大量抛售</b>，减持加速",
            f"💵 现价: <b>${price}</b>",
        ]
        
        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            change_text = "涨幅" if change_24h >= 0 else "跌幅"
            message_parts.append(f"{change_emoji} 24H{change_text}: <code>{change_24h:+.2f}%</code>")
        
        if rebound and rebound != 0:
            rebound_emoji = "📈" if rebound > 0 else "📉"
            message_parts.append(f"{rebound_emoji} 短期波动: <code>{rebound:+.2f}%</code>")
        
        if scoring:
            message_parts.append(f"🎯 AI评分: <b>{int(scoring)}</b>")
        
        message_parts.extend([
            f"",
            f"💡 风险警示:",
            f"   • 🚨 <b>高风险！主力加速离场</b>",
            f"   • 📉 价格可能面临大幅下跌",
            f"   • 🛑 已持仓建议及时止损离场",
            f"   • ⛔ 不建议抄底，等待企稳",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 4:
        # 主力减持风险
        emoji = "⚠️"
        title = f"<b>${symbol} 疑似主力减持</b>"
        risk_desc = "主力持仓减少，注意市场风险"
        tag = "#主力减持"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
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
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 16:
        # 追踪后涨幅超过20% - 上涨止盈
        emoji = "🎉"
        title = f"<b>${symbol} 上涨止盈信号</b>"
        gains_desc = f"AI追踪后上涨，涨幅已达 <b>{gains:.2f}%</b> 🚀"
        tag = "#上涨止盈"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"✅ {gains_desc}",
            f"💵 现价: <b>${price}</b>",
            f"📈 24H涨幅: <code>+{change_24h:.2f}%</code>",
        ]
        
        if scoring:
            message_parts.append(f"🎯 AI评分: <b>{int(scoring)}</b>")
        
        message_parts.extend([
            f"",
            f"💡 操作建议:",
            f"   • <b>🎯 移动止盈，锁定利润</b>",
            f"   • 📊 可考虑分批止盈离场",
            f"   • 🛡️ 避免回吐过多收益",
            f"   • ⏰ 保持警惕，注意回调风险",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 19:
        # 追踪后跌幅超过15% - 下跌止盈
        emoji = "🔴"
        title = f"<b>${symbol} 下跌止盈信号</b>"
        risk_desc = f"AI追踪后下跌，跌幅已超过 {risk_decline:.2f}%"
        tag = "#下跌止盈"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ {risk_desc}",
            f"💵 现价: <b>${price}</b>",
            f"📉 风险跌幅: <code>-{risk_decline:.2f}%</code>",
        ]
        
        if rebound:
            message_parts.append(f"📈 反弹幅度: <code>{rebound:+.2f}%</code>")
        
        message_parts.extend([
            f"",
            f"💡 操作建议:",
            f"   • <b>移动止盈，保护利润</b>",
            f"   • 避免回吐过多收益",
            f"   • 等待新的入场机会",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    elif predict_type == 31:
        # 追踪后跌幅5-15% - 保护本金
        emoji = "🟠"
        title = f"<b>${symbol} 本金保护警示</b>"
        risk_desc = f"AI追踪后下跌，跌幅已达 {risk_decline:.2f}%"
        tag = "#保护本金"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ {risk_desc}",
            f"💵 现价: <b>${price}</b>",
            f"📉 风险跌幅: <code>-{risk_decline:.2f}%</code>",
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
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
    else:
        # AI追踪结束 - 通用格式
        emoji = "🔔"
        title = f"<b>${symbol} AI追踪结束</b>"
        tag = "#追踪结束"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━━━━━━━━━━━",
            f"🤖 AI实时追踪已结束",
            f"💵 现价: <b>${price}</b>",
        ]
        
        # 根据涨跌显示不同提示
        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")
        
        if scoring:
            message_parts.append(f"🎯 AI评分: <b>{int(scoring)}</b>")
        
        if risk_decline:
            message_parts.append(f"📉 追踪期跌幅: <code>-{risk_decline:.2f}%</code>")
        if rebound:
            message_parts.append(f"📈 反弹幅度: <code>{rebound:+.2f}%</code>")
        
        message_parts.extend([
            f"",
            f"💡 提示:",
            f"   • AI追踪监控已结束",
            f"   • 建议关注后续走势变化",
            f"   • 如有持仓请自行评估风险",
            f"",
            f"{tag}",
            f"━━━━━━━━━━━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
    
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
    
    # Type 114 资金异常 - 特殊格式（包含追踪涨幅信息）
    if msg_type == 114:
        emoji = "💎"
        funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
        
        # 从 extField 中提取涨幅信息
        ext_field = content.get('extField', {})
        gains = ext_field.get('gains', 0) if isinstance(ext_field, dict) else 0
        
        # 根据涨幅判断消息类型
        if gains > 0:
            # 有涨幅数据 - 上涨止盈提示
            if gains >= 50:
                emoji = "🎉"
                title = f"<b>${symbol} 大幅上涨止盈</b>"
                tag = "#上涨止盈"
            elif gains >= 20:
                emoji = "🎊"
                title = f"<b>${symbol} 上涨止盈</b>"
                tag = "#上涨止盈"
            else:
                emoji = "💰"
                title = f"<b>${symbol} 资金异常</b>"
                tag = "#资金异常"
            
            message_parts = [
                f"{emoji} {title}",
                f"━━━━━━━━━",
            ]
            
            if gains >= 20:
                message_parts.append(f"✅ AI追踪后涨幅达 <b>{gains:.2f}%</b> 🚀")
            
            message_parts.extend([
                f"💼 资金类型: {funds_text}",
                f"💵 现价: <b>${price}</b>",
            ])
            
            if change_24h:
                change_emoji = "📈" if change_24h >= 0 else "📉"
                change_text = "涨幅" if change_24h >= 0 else "跌幅"
                message_parts.append(f"{change_emoji} 24H{change_text}: <code>{change_24h:+.2f}%</code>")
            
            if 'tradeType' in content:
                trade_type = content.get('tradeType')
                trade_text = TRADE_TYPE_MAP.get(trade_type, 'N/A')
                message_parts.append(f"📊 类型: {trade_text}")
            
            # 根据涨幅给出不同建议
            if gains >= 20:
                message_parts.extend([
                    f"",
                    f"💡 操作建议:",
                    f"   • 🎯 <b>移动止盈，锁定利润</b>",
                    f"   • 📊 可考虑分批止盈离场",
                    f"   • 🛡️ 避免回吐过多收益",
                ])
            
            message_parts.extend([
                f"",
                f"{tag}",
                f"━━━━━━━━━",
                f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
            ])
        else:
            # 没有涨幅数据 - 普通资金异常
            title = f"<b>${symbol} 资金异常</b>"
            tag = "#资金异常"
            
            message_parts = [
                f"{emoji} {title}",
                f"━━━━━━━━━",
                f"💼 资金类型: {funds_text}",
                f"💵 现价: <b>${price}</b>",
            ]
            
            if change_24h:
                change_emoji = "📈" if change_24h >= 0 else "📉"
                message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")
            
            if 'tradeType' in content:
                trade_type = content.get('tradeType')
                trade_text = TRADE_TYPE_MAP.get(trade_type, 'N/A')
                message_parts.append(f"📊 类型: {trade_text}")
            
            message_parts.extend([
                f"",
                f"{tag}",
                f"━━━━━━━━━",
                f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
            ])
        
        return "\n".join(message_parts)
    
    # Type 111 资金出逃 - 特殊格式
    elif msg_type == 111:
        emoji = "🚨"
        title = f"<b>${symbol} 主力资金出逃</b>"
        tag = "#追踪结束"
        
        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ 疑似主力资金已出逃",
            f"📊 资金异动监控结束",
            f"💵 现价: <b>${price}</b>",
            f"📉 24H: <code>{change_24h:+.2f}%</code>",
            f"",
            f"💡 操作建议:",
            f"   • <b>注意市场风险</b>",
            f"   • 已持仓建议及时止盈/止损",
            f"   • 观望为主，等待企稳信号",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ]
        
        return "\n".join(message_parts)
    
    # Type 110 Alpha - 优化格式
    elif msg_type == 110:
        emoji = "⭐"
        funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
        
        message_parts = [
            f"{emoji} <b>【Alpha】${symbol}</b>",
            f"━━━━━━━━━",
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
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
        
        return "\n".join(message_parts)
    
    # Type 108 资金异动
    elif msg_type == 108:
        emoji = "💰"
        funds_text = FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')
        
        message_parts = [
            f"{emoji} <b>【资金异动】${symbol}</b>",
            f"━━━━━━━━━",
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
        
        message_parts.extend([
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
        
        return "\n".join(message_parts)
    
    # 其他类型 - 通用格式
    else:
        type_emoji_map = {
            109: "📢",  # 上下币公告
            113: "🚀"   # FOMO
        }
        emoji = type_emoji_map.get(msg_type, "📋")
        
        message_parts = [
            f"{emoji} <b>【{msg_type_name}】${symbol}</b>",
            f"━━━━━━━━━",
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
        
        message_parts.extend([
            f"━━━━━━━━━",
            f"🕐 {time.strftime('%H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}"
        ])
        
        return "\n".join(message_parts)
