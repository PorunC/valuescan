"""
日志工具模块
提供统一的日志记录功能，支持控制台和文件输出
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from .config import (
    LOG_LEVEL,
    LOG_TO_FILE,
    LOG_FILE,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT,
    LOG_FORMAT,
    LOG_DATE_FORMAT
)


def setup_logger(name='valuescan'):
    """
    配置并返回logger实例
    
    Args:
        name: logger名称
    
    Returns:
        logging.Logger: 配置好的logger实例
    """
    logger = logging.getLogger(name)
    
    # 如果logger已经有处理器，说明已经配置过了，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # 控制台处理器 - 始终输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 可选
    if LOG_TO_FILE:
        try:
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_SIZE,
                backupCount=LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件: {e}")
    
    # 防止日志传播到根logger
    logger.propagate = False
    
    return logger


# 创建默认的logger实例
logger = setup_logger()
