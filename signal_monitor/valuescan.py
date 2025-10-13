"""
ValueScan API 监听工具 - 主入口
监听 valuescan.io API 并将告警消息发送到 Telegram
"""

from logger import logger
from config import (
    TELEGRAM_BOT_TOKEN,
    SEND_TG_IN_MODE_1,
    CHROME_DEBUG_PORT
)
from api_monitor import capture_api_request

# 尝试导入无头模式配置
try:
    from config import HEADLESS_MODE
except ImportError:
    HEADLESS_MODE = False


def main():
    """主函数：显示配置信息并启动监听"""
    
    logger.info("ValueScan API 监听工具")
    logger.info("="*60)
    logger.info("当前配置:")
    logger.info(f"  Telegram Bot: {'已配置' if TELEGRAM_BOT_TOKEN else '未配置'}")
    logger.info(f"  发送TG消息: {'✅ 是' if SEND_TG_IN_MODE_1 else '❌ 否'}")
    logger.info(f"  运行模式: {'🚀 无头模式（后台）' if HEADLESS_MODE else '🖥️  有头模式（显示浏览器）'}")
    
    if not HEADLESS_MODE:
        logger.info(f"  调试端口: {CHROME_DEBUG_PORT}")
        logger.info(f"  Chrome数据: ./chrome-debug-profile")
        logger.info("确保 Chrome 已用调试模式启动 (端口 {})".format(CHROME_DEBUG_PORT))
        logger.info("如果还未启动，请运行: python start_with_chrome.py")
    else:
        logger.info(f"  Chrome数据: ./chrome-debug-profile")
        logger.info("⚠️  无头模式使用相同的用户目录，共享登录状态")
    
    logger.info("正在连接并开始监听...")
    
    capture_api_request(headless=HEADLESS_MODE)


if __name__ == "__main__":
    main()
