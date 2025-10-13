"""
数据库管理工具
用于查看和管理消息数据库
"""

import sys
from .database import MessageDatabase
from .logger import logger
import time
from datetime import datetime, timezone, timedelta

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


def get_beijing_time_str(timestamp, format_str='%Y-%m-%d %H:%M:%S'):
    """
    将时间戳转换为北京时间字符串
    
    Args:
        timestamp: 秒级时间戳
        format_str: 时间格式字符串，默认为 '%Y-%m-%d %H:%M:%S'
    
    Returns:
        str: 格式化后的北京时间字符串（带UTC+8标识）
    """
    if not timestamp:
        return 'N/A'
    dt = datetime.fromtimestamp(timestamp, tz=BEIJING_TZ)
    return dt.strftime(format_str) + ' (UTC+8)'


def show_statistics():
    """显示数据库统计信息"""
    db = MessageDatabase()
    stats = db.get_statistics()
    
    logger.info("="*60)
    logger.info("📊 数据库统计信息")
    logger.info("="*60)
    logger.info(f"总消息数: {stats.get('total', 0)} 条")
    
    if 'by_type' in stats and stats['by_type']:
        logger.info("\n按类型统计:")
        for msg_type, count in sorted(stats['by_type'].items()):
            logger.info(f"  类型 {msg_type}: {count} 条")
    
    if 'earliest' in stats and 'latest' in stats:
        earliest = get_beijing_time_str(stats['earliest'])
        latest = get_beijing_time_str(stats['latest'])
        logger.info(f"\n最早记录: {earliest}")
        logger.info(f"最新记录: {latest}")
    
    logger.info("="*60)
    db.close()


def show_recent_messages(limit=20):
    """显示最近的消息"""
    db = MessageDatabase()
    messages = db.get_recent_messages(limit)
    
    logger.info("="*60)
    logger.info(f"📝 最近 {limit} 条消息")
    logger.info("="*60)
    
    if not messages:
        logger.info("暂无消息记录")
    else:
        for msg in messages:
            msg_id, msg_type, symbol, title, processed_time, created_time = msg
            processed_str = get_beijing_time_str(processed_time)
            logger.info(f"\nID: {msg_id}")
            logger.info(f"  类型: {msg_type}")
            logger.info(f"  币种: {symbol or 'N/A'}")
            logger.info(f"  标题: {title or 'N/A'}")
            logger.info(f"  处理时间: {processed_str}")
    
    logger.info("="*60)
    db.close()


def clean_old_data(days=30):
    """清理旧数据"""
    logger.info(f"🗑️ 准备清理 {days} 天前的数据...")
    
    db = MessageDatabase()
    deleted = db.clean_old_messages(days)
    
    if deleted > 0:
        logger.info(f"✅ 已清理 {deleted} 条旧消息")
    else:
        logger.info("ℹ️ 没有需要清理的消息")
    
    db.close()


def clear_all_data():
    """清空所有数据"""
    logger.warning("⚠️ 即将清空所有数据库记录！")
    confirm = input("确认清空？输入 'yes' 继续: ")
    
    if confirm.lower() != 'yes':
        logger.info("操作已取消")
        return
    
    db = MessageDatabase()
    try:
        db.cursor.execute('DELETE FROM processed_messages')
        db.conn.commit()
        logger.info("✅ 数据库已清空")
    except Exception as e:
        logger.error(f"❌ 清空数据库失败: {e}")
    finally:
        db.close()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python db_manager.py stats          - 显示统计信息")
        print("  python db_manager.py recent [数量]  - 显示最近的消息（默认20条）")
        print("  python db_manager.py clean [天数]   - 清理N天前的数据（默认30天）")
        print("  python db_manager.py clear          - 清空所有数据（需确认）")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'stats':
        show_statistics()
    
    elif command == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        show_recent_messages(limit)
    
    elif command == 'clean':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        clean_old_data(days)
    
    elif command == 'clear':
        clear_all_data()
    
    else:
        logger.error(f"未知命令: {command}")


if __name__ == "__main__":
    main()
