"""
数据库模块
使用 SQLite 存储已处理的消息 ID，防止重复发送
"""

import sqlite3
import os
import time
from .logger import logger


class MessageDatabase:
    """消息数据库管理类"""
    
    def __init__(self, db_path='valuescan.db'):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库，创建表结构"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # 创建消息记录表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id TEXT PRIMARY KEY,
                    message_type INTEGER,
                    symbol TEXT,
                    title TEXT,
                    processed_time INTEGER,
                    created_time INTEGER
                )
            ''')
            
            # 创建索引以提高查询效率
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_message_id 
                ON processed_messages(message_id)
            ''')
            
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_processed_time 
                ON processed_messages(processed_time)
            ''')
            
            self.conn.commit()
            
            # 获取数据库中已有的记录数
            count = self.get_total_count()
            logger.info(f"✅ 数据库已初始化: {self.db_path}")
            logger.info(f"📊 已记录消息数量: {count} 条")
            
        except sqlite3.Error as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            raise
    
    def is_processed(self, message_id):
        """
        检查消息 ID 是否已处理过
        
        Args:
            message_id: 消息 ID
        
        Returns:
            bool: True 表示已处理过，False 表示未处理
        """
        try:
            self.cursor.execute(
                'SELECT message_id FROM processed_messages WHERE message_id = ?',
                (str(message_id),)
            )
            result = self.cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            logger.error(f"❌ 查询消息 ID 失败: {e}")
            return False
    
    def add_message(self, message_id, message_type=None, symbol=None, title=None, created_time=None):
        """
        添加消息到数据库
        
        Args:
            message_id: 消息 ID
            message_type: 消息类型代码
            symbol: 币种符号
            title: 消息标题
            created_time: 消息创建时间（毫秒时间戳）
        
        Returns:
            bool: 添加成功返回 True，失败或已存在返回 False
        """
        # 先检查是否已存在
        if self.is_processed(message_id):
            return False
        
        try:
            current_time = int(time.time())
            
            self.cursor.execute('''
                INSERT INTO processed_messages 
                (message_id, message_type, symbol, title, processed_time, created_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(message_id),
                message_type,
                symbol,
                title,
                current_time,
                created_time
            ))
            
            self.conn.commit()
            return True
            
        except sqlite3.IntegrityError:
            # 主键冲突，消息已存在
            return False
        except sqlite3.Error as e:
            logger.error(f"❌ 添加消息到数据库失败: {e}")
            return False
    
    def get_total_count(self):
        """
        获取数据库中消息总数
        
        Returns:
            int: 消息总数
        """
        try:
            self.cursor.execute('SELECT COUNT(*) FROM processed_messages')
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"❌ 获取消息总数失败: {e}")
            return 0
    
    def get_recent_messages(self, limit=10):
        """
        获取最近处理的消息
        
        Args:
            limit: 返回的消息数量
        
        Returns:
            list: 消息列表
        """
        try:
            self.cursor.execute('''
                SELECT message_id, message_type, symbol, title, 
                       processed_time, created_time
                FROM processed_messages
                ORDER BY processed_time DESC
                LIMIT ?
            ''', (limit,))
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"❌ 获取最近消息失败: {e}")
            return []
    
    def clean_old_messages(self, days=30):
        """
        清理指定天数之前的旧消息
        
        Args:
            days: 保留最近多少天的数据
        
        Returns:
            int: 删除的消息数量
        """
        try:
            cutoff_time = int(time.time()) - (days * 24 * 3600)
            
            self.cursor.execute('''
                DELETE FROM processed_messages 
                WHERE processed_time < ?
            ''', (cutoff_time,))
            
            deleted_count = self.cursor.rowcount
            self.conn.commit()
            
            if deleted_count > 0:
                logger.info(f"🗑️ 已清理 {deleted_count} 条超过 {days} 天的旧消息")
            
            return deleted_count
            
        except sqlite3.Error as e:
            logger.error(f"❌ 清理旧消息失败: {e}")
            return 0
    
    def get_statistics(self):
        """
        获取数据库统计信息
        
        Returns:
            dict: 统计信息字典
        """
        try:
            stats = {}
            
            # 总消息数
            stats['total'] = self.get_total_count()
            
            # 按类型统计
            self.cursor.execute('''
                SELECT message_type, COUNT(*) 
                FROM processed_messages 
                GROUP BY message_type
            ''')
            stats['by_type'] = dict(self.cursor.fetchall())
            
            # 最早和最晚的消息时间
            self.cursor.execute('''
                SELECT MIN(processed_time), MAX(processed_time)
                FROM processed_messages
            ''')
            result = self.cursor.fetchone()
            if result and result[0]:
                stats['earliest'] = result[0]
                stats['latest'] = result[1]
            
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()


# 创建全局数据库实例
_db_instance = None


def get_database():
    """
    获取全局数据库实例（单例模式）
    
    Returns:
        MessageDatabase: 数据库实例
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = MessageDatabase()
    return _db_instance


def is_message_processed(message_id):
    """
    快捷函数：检查消息是否已处理
    
    Args:
        message_id: 消息 ID
    
    Returns:
        bool: True 表示已处理，False 表示未处理
    """
    db = get_database()
    return db.is_processed(message_id)


def mark_message_processed(message_id, message_type=None, symbol=None, title=None, created_time=None):
    """
    快捷函数：标记消息为已处理
    
    Args:
        message_id: 消息 ID
        message_type: 消息类型
        symbol: 币种符号
        title: 消息标题
        created_time: 创建时间
    
    Returns:
        bool: 成功返回 True
    """
    db = get_database()
    return db.add_message(message_id, message_type, symbol, title, created_time)
