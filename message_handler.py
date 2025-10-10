"""
消息处理模块
负责消息的解析、打印和处理逻辑
"""

import json
import time
from logger import logger
from config import MESSAGE_TYPE_MAP, TRADE_TYPE_MAP, FUNDS_MOVEMENT_MAP
from telegram import send_telegram_message, format_message_for_telegram
from database import is_message_processed, mark_message_processed


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
    
    Returns:
        bool: 是否为新消息（未处理过的）
    """
    msg_id = item.get('id')
    
    # 检查数据库中是否已处理过
    if msg_id and is_message_processed(msg_id):
        logger.info(f"  ⏭️ 消息 ID {msg_id} 已处理过，跳过")
        return False
    
    # 打印消息详情
    print_message_details(item, idx)
    
    # 提取消息信息用于数据库记录
    msg_type = item.get('type')
    title = item.get('title')
    created_time = item.get('createTime')
    symbol = None
    
    # 尝试从 content 中提取币种符号
    if 'content' in item and item['content']:
        try:
            content = json.loads(item['content'])
            symbol = content.get('symbol')
        except:
            pass
    
    # 发送到 Telegram（如果启用）
    if send_to_telegram:
        logger.info(f"📤 发送消息到 Telegram...")
        telegram_message = format_message_for_telegram(item)
        if send_telegram_message(telegram_message):
            # 发送成功后记录到数据库
            if msg_id:
                if mark_message_processed(msg_id, msg_type, symbol, title, created_time):
                    logger.info(f"✅ 消息 ID {msg_id} 已记录到数据库")
                    return True  # 发送并记录成功
                else:
                    logger.warning(f"⚠️ 消息 ID {msg_id} 记录到数据库失败")
                    return False  # 记录失败，下次重试
            return True  # 没有 msg_id，但发送成功
        else:
            logger.warning(f"⚠️ Telegram 发送失败，消息 ID {msg_id} 未记录到数据库")
            return False  # 发送失败，下次重试
    else:
        # 即使不发送 Telegram，也记录到数据库（避免下次重复处理）
        if msg_id:
            if mark_message_processed(msg_id, msg_type, symbol, title, created_time):
                logger.info(f"✅ 消息 ID {msg_id} 已记录到数据库（未发送 TG）")
                return True  # 记录成功
            return False  # 记录失败
        return True  # 没有 msg_id，直接返回成功


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
        
        # 使用数据库进行持久化去重
        new_messages = []
        duplicate_in_batch = 0
        duplicate_in_db = 0
        
        for item in response_data['data']:
            msg_id = item.get('id')
            if not msg_id:
                continue
            
            # 检查本次批次中是否重复（内存去重）
            if seen_ids is not None and msg_id in seen_ids:
                duplicate_in_batch += 1
                continue
            
            # 检查数据库中是否已处理（持久化去重）
            if is_message_processed(msg_id):
                duplicate_in_db += 1
                if seen_ids is not None:
                    seen_ids.add(msg_id)
                continue
            
            # 新消息（注意：这里不提前添加到 seen_ids，等发送成功后再添加）
            new_messages.append(item)
        
        new_count = len(new_messages)
        duplicate_count = duplicate_in_batch + duplicate_in_db
        
        logger.info(f"  消息统计: 总共 {total_count} 条, 新消息 {new_count} 条, 重复 {duplicate_count} 条")
        if duplicate_in_db > 0:
            logger.info(f"    └─ 数据库已处理: {duplicate_in_db} 条")
        if duplicate_in_batch > 0:
            logger.info(f"    └─ 本次批次重复: {duplicate_in_batch} 条")
        if seen_ids is not None:
            logger.info(f"  本次运行已处理消息: {len(seen_ids)} 条")
        
        if new_messages:
            logger.info(f"  【新消息列表】:")
            # 倒序发送消息（最新的消息最先发送到 Telegram）
            for idx, item in enumerate(reversed(new_messages), 1):
                # 处理消息，成功后才添加到 seen_ids（防止发送失败时被标记为已处理）
                success = process_message_item(item, idx, send_to_telegram)
                if success and seen_ids is not None:
                    msg_id = item.get('id')
                    if msg_id:
                        seen_ids.add(msg_id)
        else:
            logger.info(f"  本次无新消息（所有消息都已处理过）")
        
        return new_count
    
    return 0
