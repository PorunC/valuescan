"""
ValueScan 无头模式启动脚本
直接启动无头 Chrome 运行 API 监听，不显示浏览器窗口
适合在服务器后台运行
"""

from logger import logger
from api_monitor import capture_api_request


def main():
    """无头模式启动主函数"""
    logger.info("🚀 ValueScan 无头模式启动")
    logger.info("="*60)
    logger.info("⚠️  注意事项：")
    logger.info("  1. 无头模式需要已登录的 Cookie 才能工作")
    logger.info("  2. 首次使用请先运行有头模式登录账号")
    logger.info("  3. 或手动复制 chrome-debug-profile 到 chrome-headless-profile")
    logger.info("="*60)
    logger.info("正在启动无头 Chrome...")
    
    try:
        capture_api_request(headless=True)
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()
