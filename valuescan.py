"""
ValueScan API 监听工具 - 主入口
监听 valuescan.io API 并将告警消息发送到 Telegram
"""

from logger import logger
from config import (
    TELEGRAM_BOT_TOKEN,
    SEND_TG_IN_MODE_1,
    SEND_TG_IN_MODE_2,
    CHROME_DEBUG_PORT
)
from api_monitor import capture_api_request, capture_with_existing_browser


def main():
    """主函数：显示菜单并启动监听"""
    
    logger.info("DrissionPage API 抓包工具")
    logger.info("="*60)
    logger.info("\n当前配置:")
    logger.info(f"  Telegram Bot: {'已配置' if TELEGRAM_BOT_TOKEN else '未配置'}")
    logger.info(f"  选项1发送TG: {'✅ 是' if SEND_TG_IN_MODE_1 else '❌ 否'}")
    logger.info(f"  选项2发送TG: {'✅ 是' if SEND_TG_IN_MODE_2 else '❌ 否'}")
    logger.info("\n选择模式:")
    logger.info("1. 自动启动浏览器并监听")
    logger.info("2. 连接到已存在的浏览器 (需要先用调试模式启动 Chrome)")
    
    choice = input("\n请选择 (1/2): ")
    
    if choice == "1":
        capture_api_request()
    elif choice == "2":
        logger.info("\n确保 Chrome 已用以下命令启动:")
        logger.info(f"chrome.exe --remote-debugging-port={CHROME_DEBUG_PORT}")
        input("按回车继续...")
        capture_with_existing_browser()
    else:
        logger.warning("无效选择")


if __name__ == "__main__":
    main()
