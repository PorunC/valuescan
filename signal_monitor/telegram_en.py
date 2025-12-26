"""
English version of Telegram message formatting module
Provides English translations for all trading signals
"""

import json
from datetime import datetime, timezone, timedelta

# Beijing timezone (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


def get_beijing_time_str_en(timestamp_ms, format_str='%H:%M:%S'):
    """
    Convert timestamp to Beijing time string (English format)

    Args:
        timestamp_ms: Timestamp in milliseconds
        format_str: Time format string, default '%H:%M:%S'

    Returns:
        str: Formatted Beijing time string (with UTC+8 label)
    """
    if not timestamp_ms:
        return 'N/A'
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=BEIJING_TZ)
    return dt.strftime(format_str) + ' (UTC+8)'


def _get_binance_alpha_badge_en(symbol):
    """
    Get Binance Alpha badge (English)

    Args:
        symbol: Token symbol

    Returns:
        str: Badge if token is in Binance Alpha, empty string otherwise
    """
    if not symbol:
        return ""

    try:
        from binance_alpha_cache import is_binance_alpha_symbol
        if is_binance_alpha_symbol(symbol):
            return " 🔥 <b>Binance Alpha</b>"
    except Exception:
        pass

    return ""


def format_message_for_telegram_en(item):
    """
    Format message for Telegram in English (HTML format)

    Args:
        item: Message data dictionary

    Returns:
        str: Formatted HTML message text in English
    """
    # Message type mappings (English)
    MESSAGE_TYPE_MAP_EN = {
        100: 'AI Tracking',
        108: 'Fund Movement',
        109: 'Listing Announcement',
        110: 'Alpha Opportunity',
        111: 'Capital Flight',
        112: 'FOMO Intensification',
        113: 'FOMO Alert',
        114: 'Abnormal Funds'
    }

    TRADE_TYPE_MAP_EN = {
        1: 'Spot',
        2: 'Futures'
    }

    FUNDS_MOVEMENT_MAP_EN = {
        1: 'Inflow (24H)',
        2: 'Extended Inflow',
        3: 'Sustained Inflow',
        4: 'Suspected Outflow',
        5: 'Volume Surge',
        6: 'Take-Profit Alert',
        7: 'FOMO Intensification'
    }

    msg_type = item.get('type', 'N/A')
    msg_type_name = MESSAGE_TYPE_MAP_EN.get(msg_type, 'N/A') if isinstance(msg_type, int) else 'N/A'

    # Parse content field
    content = {}
    symbol = None
    if 'content' in item and item['content']:
        try:
            content = json.loads(item['content'])
            symbol = content.get('symbol')
        except json.JSONDecodeError:
            pass

    # Route to different formatters based on message type
    if msg_type == 100:  # AI Tracking - special format
        formatted_message = _format_risk_alert_en(item, content, msg_type_name)
    else:  # Other types - general format
        formatted_message = _format_general_message_en(item, content, msg_type, msg_type_name)

    # Add Binance Alpha badge if applicable
    if symbol and _get_binance_alpha_badge_en(symbol):
        lines = formatted_message.split('\n')
        if lines:
            for i, line in enumerate(lines):
                if f'${symbol}' in line and '<b>' in line:
                    lines[i] = line.rstrip('</b>') + ' 🔥 Binance Alpha</b>' if line.endswith('</b>') else line + ' 🔥 <b>Binance Alpha</b>'
                    break
            formatted_message = '\n'.join(lines)

    return formatted_message


def _format_risk_alert_en(item, content, msg_type_name):
    """
    Format AI Tracking alert (type 100) in English
    Different scenarios based on predictType
    """
    symbol = content.get('symbol', 'N/A')
    price = content.get('price', 'N/A')
    change_24h = content.get('percentChange24h', 0)
    predict_type = content.get('predictType', 0)
    risk_decline = content.get('riskDecline', 0)
    gains = content.get('gains', 0)
    rebound = content.get('rebound', 0)
    scoring = content.get('scoring', 0)

    # Format based on predictType
    if predict_type == 2:
        # Major players fleeing (risk increase)
        emoji = "🔴"
        title = f"<b>${symbol} Major Outflow Warning</b>"
        tag = "#MajorOutflow"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ Suspected <b>massive sell-off</b> by major players",
            f"📉 <b>Risk increasing</b>, consider take-profit",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            message_parts.append(f"{change_emoji} 24H Change: <code>{change_24h:+.2f}%</code>")

        if gains and gains > 0:
            message_parts.append(f"📈 Tracked Gain: <code>+{gains:.2f}%</code>")
        if content.get('decline', 0) > 0:
            decline = content.get('decline', 0)
            message_parts.append(f"📉 Pullback: <code>-{decline:.2f}%</code>")

        if scoring:
            message_parts.append(f"🎯 AI Score: <b>{int(scoring)}</b>")

        message_parts.extend([
            f"",
            f"💡 Risk Alert:",
            f"   • 🔴 <b>Major players possibly exiting</b>",
            f"   • 📉 Price may enter correction phase",
            f"   • 💰 <b>Consider taking most profits</b>",
            f"   • 🛡️ Protect existing gains",
            f"   • ⛔ Not recommended to chase highs",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

    elif predict_type == 24:
        # Price peak risk
        emoji = "📍"
        title = f"<b>${symbol} Price Peak Warning</b>"
        tag = "#PeakRisk"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ AI detected potential price <b>peak</b>, watch for pullback risk",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            message_parts.append(f"{change_emoji} 24H Change: <code>{change_24h:+.2f}%</code>")

            if change_24h > 10:
                message_parts.append(f"🔥 High short-term gain, increased pullback risk")

        if scoring:
            message_parts.append(f"🎯 AI Score: <b>{int(scoring)}</b>")

        message_parts.extend([
            f"",
            f"💡 Risk Warning:",
            f"   • ⚠️ <b>Potential top zone detected</b>",
            f"   • 📉 May face correction pressure",
            f"   • 🛑 Not recommended to chase, caution on buying",
            f"   • 💰 Consider reducing position in batches",
            f"   • 👀 AI real-time tracking active",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

    elif predict_type == 5:
        # AI tracking started
        emoji = "🔍"
        title = f"<b>${symbol} AI Tracking Started</b>"
        tag = "#Observation"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"🤖 AI detected potential token, real-time tracking initiated",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            message_parts.append(f"{change_emoji} 24H Change: <code>{change_24h:+.2f}%</code>")

        if scoring:
            score_int = int(scoring)
            if score_int >= 70:
                score_desc = "⭐⭐⭐ High"
            elif score_int >= 60:
                score_desc = "⭐⭐ Above Average"
            elif score_int >= 50:
                score_desc = "⭐ Average"
            else:
                score_desc = "Monitoring"
            message_parts.append(f"🎯 AI Score: <b>{score_int}</b> ({score_desc})")

        message_parts.extend([
            f"",
            f"💡 Note:",
            f"   • 🔍 AI real-time monitoring active",
            f"   • 📊 Watch for price and fund dynamics",
            f"   • 🎯 Wait for clearer entry signals",
            f"   • ⚠️ Tracking ≠ Buy recommendation, manage risk",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

    elif predict_type == 3:
        # Major accumulation
        emoji = "💚"
        title = f"<b>AI Opportunity Alert</b>"
        tag = "#Accumulation"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"<b>${symbol}</b> Suspected major accumulation, watch market changes",
            f"${symbol} Major position increasing, current price <b>${price}</b>, 24H change {change_24h:.2f}%, market sentiment bullish, but watch for high selling risk.",
            f"",
            f"🪙 <b>${symbol}</b>",
            f"💼 Major Accumulation",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            message_parts.append(f"{change_emoji} 24H Change: <code>{change_24h:+.2f}%</code>")

        if scoring:
            message_parts.append(f"🎯 AI Score: <b>{int(scoring)}</b>")

        message_parts.extend([
            f"",
            f"💡 Strategy:",
            f"   • 📊 Market sentiment bullish",
            f"   • ✅ Consider entry opportunity",
            f"   • ⚠️ Watch risk at highs",
            f"   • 🎯 Set stop-loss/take-profit",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

    elif predict_type == 16:
        # Take-profit on rise
        emoji = "🎉"
        title = f"<b>${symbol} Take-Profit Signal</b>"
        tag = "#TakeProfit"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"✅ AI tracked gain reached <b>{gains:.2f}%</b> 🚀",
            f"💵 Current Price: <b>${price}</b>",
            f"📈 24H Gain: <code>+{change_24h:.2f}%</code>",
        ]

        if scoring:
            message_parts.append(f"🎯 AI Score: <b>{int(scoring)}</b>")

        message_parts.extend([
            f"",
            f"💡 Strategy:",
            f"   • <b>🎯 Trailing stop-loss, lock profits</b>",
            f"   • 📊 Consider taking profits in batches",
            f"   • 🛡️ Avoid giving back too much gain",
            f"   • ⏰ Stay alert, watch for pullback risk",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

    else:
        # Default AI tracking format
        emoji = "🔔"
        title = f"<b>${symbol} AI Tracking Update</b>"
        tag = "#Tracking"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"🤖 AI monitoring update",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")

        if scoring:
            message_parts.append(f"🎯 AI Score: <b>{int(scoring)}</b>")

        message_parts.extend([
            f"",
            f"💡 Note:",
            f"   • AI tracking update",
            f"   • Monitor subsequent movements",
            f"   • Assess risk if holding position",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

    return "\n".join(message_parts)


def _format_general_message_en(item, content, msg_type, msg_type_name):
    """
    Format general messages (fund movements, Alpha, etc.) in English
    """
    TRADE_TYPE_MAP_EN = {
        1: 'Spot',
        2: 'Futures'
    }

    FUNDS_MOVEMENT_MAP_EN = {
        1: 'Inflow (24H)',
        2: 'Extended Inflow',
        3: 'Sustained Inflow',
        4: 'Suspected Outflow',
        5: 'Volume Surge',
        6: 'Take-Profit Alert',
        7: 'FOMO Intensification'
    }

    symbol = content.get('symbol', 'N/A')
    price = content.get('price', 'N/A')
    change_24h = content.get('percentChange24h', 0)
    funds_type = content.get('fundsMovementType', 0)

    # Type 112 FOMO Intensification - special format
    if msg_type == 112:
        emoji = "🔥"
        title = f"<b>${symbol} FOMO Intensification</b>"
        funds_text = FUNDS_MOVEMENT_MAP_EN.get(funds_type, 'N/A')
        tag = "#FOMORisk"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ <b>Market overheated, consider take-profit</b>",
            f"🌡️ FOMO sentiment peaked, guard against sudden correction",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            message_parts.append(f"{change_emoji} 24H Change: <code>{change_24h:+.2f}%</code>")

            if change_24h > 15:
                message_parts.append(f"🔥 High short-term gain, pullback risk significantly increased")
            elif change_24h > 10:
                message_parts.append(f"⚠️ Significant short-term gain, consider profit-taking")

        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP_EN.get(trade_type, 'N/A')
            message_parts.append(f"📊 Type: {trade_text}")

        if funds_type:
            message_parts.append(f"💼 Fund Status: {funds_text}")

        message_parts.extend([
            f"",
            f"💡 Risk Warning:",
            f"   • 🔥 <b>FOMO overheated (risk signal)</b>",
            f"   • 📉 Market may face sudden correction",
            f"   • 💰 <b>Consider taking profits in batches</b>",
            f"   • 🛑 <b>Not recommended to chase highs</b>",
            f"   • 🎯 Set trailing stop-loss to protect profits",
            f"   • ⏰ Monitor price movements closely",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

        return "\n".join(message_parts)

    # Type 110 Alpha - optimized format
    elif msg_type == 110:
        emoji = "⭐"
        funds_text = FUNDS_MOVEMENT_MAP_EN.get(funds_type, 'N/A')

        message_parts = [
            f"{emoji} <b>【Alpha】${symbol}</b>",
            f"━━━━━━━━━",
            f"💰 Fund Status: {funds_text}",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")

        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP_EN.get(trade_type, 'N/A')
            message_parts.append(f"📊 Type: {trade_text}")

        message_parts.extend([
            f"",
            f"💡 Potential opportunity, watch for performance",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

        return "\n".join(message_parts)

    # Type 111 Capital Flight - special format
    elif msg_type == 111:
        emoji = "🚨"
        title = f"<b>${symbol} Capital Flight</b>"
        funds_text = FUNDS_MOVEMENT_MAP_EN.get(funds_type, 'N/A')
        tag = "#TrackingEnded"

        message_parts = [
            f"{emoji} {title}",
            f"━━━━━━━━━",
            f"⚠️ Fund movement tracking ended",
            f"💼 Major capital suspected to have fled, fund monitoring ended",
            f"💵 Current Price: <b>${price}</b>",
        ]

        if change_24h:
            change_emoji = "📈" if change_24h >= 0 else "📉"
            message_parts.append(f"{change_emoji} 24H Change: <code>{change_24h:+.2f}%</code>")

        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP_EN.get(trade_type, 'N/A')
            message_parts.append(f"📊 Fund Type: {trade_text}")

        message_parts.extend([
            f"",
            f"💡 Risk Warning:",
            f"   • 🚨 <b>Major capital suspected to have exited</b>",
            f"   • 📉 <b>Watch market risk</b>",
            f"   • 💰 Consider timely stop-loss/take-profit if holding",
            f"   • 🛑 Wait and see, watch for stability signals",
            f"   • 👀 Fund tracking stopped",
            f"",
            f"{tag}",
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

        return "\n".join(message_parts)

    # Other types - general format
    else:
        type_emoji_map = {
            108: "💰",
            109: "📢",
            113: "🚀"
        }
        emoji = type_emoji_map.get(msg_type, "📋")

        message_parts = [
            f"{emoji} <b>【{msg_type_name}】${symbol}</b>",
            f"━━━━━━━━━",
        ]

        if price:
            message_parts.append(f"💵 Current Price: <b>${price}</b>")

        if change_24h:
            change_emoji = "📈" if change_24h > 0 else "📉"
            message_parts.append(f"{change_emoji} 24H: <code>{change_24h:+.2f}%</code>")

        if 'tradeType' in content:
            trade_type = content.get('tradeType')
            trade_text = TRADE_TYPE_MAP_EN.get(trade_type, 'N/A')
            message_parts.append(f"📊 Type: {trade_text}")

        if 'fundsMovementType' in content and funds_type:
            funds_text = FUNDS_MOVEMENT_MAP_EN.get(funds_type, 'N/A')
            message_parts.append(f"💼 Funds: {funds_text}")

        if 'source' in content:
            message_parts.append(f"📰 Source: {content.get('source', 'N/A')}")

        if 'titleSimplified' in content:
            message_parts.append(f"")
            message_parts.append(f"💬 {content.get('titleSimplified', 'N/A')}")

        message_parts.extend([
            f"━━━━━━━━━",
            f"🕐 {get_beijing_time_str_en(item.get('createTime', 0))}"
        ])

        return "\n".join(message_parts)


def format_confluence_message_en(symbol, price, alpha_count, fomo_count):
    """
    Format confluence signal message (Alpha + FOMO) in English

    Args:
        symbol: Token symbol
        price: Current price
        alpha_count: Number of Alpha signals
        fomo_count: Number of FOMO signals

    Returns:
        str: Formatted HTML message text in English
    """
    from datetime import datetime, timezone, timedelta

    # Beijing timezone
    BEIJING_TZ = timezone(timedelta(hours=8))
    now = datetime.now(tz=BEIJING_TZ)
    time_str = now.strftime('%H:%M:%S') + ' (UTC+8)'

    # Get Binance Alpha badge
    binance_alpha_badge = _get_binance_alpha_badge_en(symbol)

    emoji = "🚨"
    title = f"<b>【Alpha + FOMO】${symbol}</b> {binance_alpha_badge}"
    tag = "#AlphaFOMO"

    message_parts = [
        f"{emoji} {title}",
        f"━━━━━━━━━",
        f"🔥 <b>Alpha + FOMO signals detected!</b>",
        f"⚡ Both Alpha and FOMO signals appeared within 2 hours",
        f"",
        f"💵 Current Price: <b>${price}</b>",
        f"⭐ Alpha Signals: <b>{alpha_count}</b>",
        f"🚀 FOMO Signals: <b>{fomo_count}</b>",
        f"",
        f"💡 Strategy:",
        f"   • 🎯 <b>High-probability entry opportunity</b>",
        f"   • 📊 Alpha (value opportunity) + FOMO (market sentiment)",
        f"   • ✅ Consider appropriate participation",
        f"   • ⚠️ Control position size and risk",
        f"   • 🎯 Set stop-loss/take-profit levels",
        f"",
        f"{tag}",
        f"━━━━━━━━━",
        f"🕐 {time_str}"
    ]

    return "\n".join(message_parts)
