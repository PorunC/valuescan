"""
消息处理模块
负责消息的解析、打印和处理逻辑
"""

import json
import time
from logger import logger
from config import MESSAGE_TYPE_MAP, TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
from telegram import send_telegram_message, format_message_for_telegram


def get_message_type_name(msg_type):
    """
    获取消息类型名称
    
    Args:
        msg_type: 消息类型代码
    
    Returns:
        str: 消息类型名称
    """
    return MESSAGE_TYPE_MAP.get(msg_type, 'N/A')


def get_trade_type_text(trade_type):
    """
    获取交易类型文本
    
    Args:
        trade_type: 交易类型代码
    
    Returns:
        str: 交易类型文本
    """
    return TRADE_TYPE_MAP.get(trade_type, 'N/A')


def get_funds_movement_text(funds_type):
    """
    获取资金流向文本
    
    Args:
        funds_type: 资金流向类型代码
    
    Returns:
        str: 资金流向文本
    """
    return FUNDS_MOVEMENT_MAP.get(funds_type, 'N/A')


def print_message_details(item, idx=None):
    """
    打印单条消息的详细信息到控制台
    
    Args:
        item: 消息数据字典
        idx: 消息序号（可选）
    """
    msg_type = item.get('type', 'N/A')
    msg_type_name = get_message_type_name(msg_type) if isinstance(msg_type, int) else 'N/A'
    
    # 打印基本信息
    if idx is not None:
        logger.info(f"  [{idx}] {item.get('title', 'N/A')} - {msg_type} {msg_type_name}")
    else:
        logger.info(f"  {item.get('title', 'N/A')} - {msg_type} {msg_type_name}")
    
    logger.info(f"      类型代码: {msg_type}")
    logger.info(f"      ID: {item.get('id', 'N/A')}")
    logger.info(f"      已读: {'是' if item.get('isRead') else '否'}")
    logger.info(f"      创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('createTime', 0)/1000))}")
    
    # 解析 content 字段
    if 'content' in item and item['content']:
        try:
            content = json.loads(item['content'])
            if 'symbol' in content:
                logger.info(f"      币种: ${content.get('symbol', 'N/A')}")
            if 'price' in content:
                logger.info(f"      价格: {content.get('price', 'N/A')}")
            if 'percentChange24h' in content:
                logger.info(f"      24h涨跌: {content.get('percentChange24h', 'N/A')}%")
            if 'tradeType' in content:
                trade_type = content.get('tradeType')
                trade_text = get_trade_type_text(trade_type)
                logger.info(f"      交易类型: {trade_type} {trade_text}")
            if 'fundsMovementType' in content:
                funds_type = content.get('fundsMovementType')
                funds_text = get_funds_movement_text(funds_type)
                logger.info(f"      资金流向: {funds_type} {funds_text}")
            if 'source' in content:
                logger.info(f"      来源: {content.get('source', 'N/A')}")
            if 'titleSimplified' in content:
                logger.info(f"      标题: {content.get('titleSimplified', 'N/A')}")
        except:
            pass


def process_message_item(item, idx=None, send_to_telegram=False):
    """
    处理单条消息：打印详情并可选发送到 Telegram
    
    Args:
        item: 消息数据字典
        idx: 消息序号（可选）
        send_to_telegram: 是否发送到 Telegram
    """
    # 打印消息详情
    print_message_details(item, idx)
    
    # 发送到 Telegram（如果启用）
    if send_to_telegram:
        logger.info(f"📤 发送消息到 Telegram...")
        telegram_message = format_message_for_telegram(item)
        send_telegram_message(telegram_message)


def process_response_data(response_data, send_to_telegram=False, seen_ids=None):
    """
    处理 API 响应数据
    
    Args:
        response_data: API 响应的 JSON 数据
        send_to_telegram: 是否将消息发送到 Telegram
        seen_ids: 已见过的消息 ID 集合（用于去重）
    
    Returns:
        int: 新消息数量
    """
    # 提取关键信息
    if 'code' in response_data:
        logger.info(f"  状态码: {response_data['code']}")
    if 'msg' in response_data:
        logger.info(f"  消息: {response_data['msg']}")
    
    # 提取 data 数组中的重要信息
    if 'data' in response_data and isinstance(response_data['data'], list):
        total_count = len(response_data['data'])
        
        # 如果提供了 seen_ids，进行去重
        if seen_ids is not None:
            new_messages = []
            for item in response_data['data']:
                msg_id = item.get('id')
                if msg_id and msg_id not in seen_ids:
                    new_messages.append(item)
                    seen_ids.add(msg_id)
            
            new_count = len(new_messages)
            duplicate_count = total_count - new_count
            
            logger.info(f"  消息统计: 总共 {total_count} 条, 新消息 {new_count} 条, 重复 {duplicate_count} 条")
            logger.info(f"  已记录消息 ID 数量: {len(seen_ids)}")
            
            if new_messages:
                logger.info(f"  【新消息列表】:")
                for idx, item in enumerate(new_messages, 1):
                    process_message_item(item, idx, send_to_telegram)
            else:
                logger.info(f"  本次无新消息（所有消息都已显示过）")
            
            return new_count
        else:
            # 不去重，显示所有消息
            logger.info(f"  消息列表 (共 {total_count} 条):")
            for idx, item in enumerate(response_data['data'], 1):
                process_message_item(item, idx, send_to_telegram)
            return total_count
    
    return 0
