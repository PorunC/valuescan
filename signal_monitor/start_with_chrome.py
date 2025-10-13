"""
ValueScan 一键启动脚本
根据配置自动选择有头模式或无头模式
- 有头模式: 显示浏览器窗口，适合首次登录和调试
- 无头模式: 后台运行，不显示窗口，适合服务器和长期运行
"""

import sys
import time
from logger import logger
from kill_chrome import restart_chrome_in_debug_mode
from api_monitor import capture_api_request

# 尝试导入无头模式配置
try:
    from config import HEADLESS_MODE
except ImportError:
    HEADLESS_MODE = False


def start_valuescan_headless():
    """
    无头模式启动流程:
    1. 清理现有 Chrome 进程（自动完成）
    2. 以无头模式启动 Chrome（使用 chrome-debug-profile 用户数据）
    3. 运行 ValueScan API 监听程序
    """
    logger.info("🚀 ValueScan 无头模式启动")
    logger.info("="*60)
    logger.info("⚠️  注意事项：")
    logger.info("  1. 无头模式需要已登录的 Cookie 才能工作")
    logger.info("  2. 首次使用请先运行有头模式登录账号")
    logger.info("  3. 无头模式会自动使用 chrome-debug-profile 目录")
    logger.info("="*60)
    
    # 步骤1 & 2: 启动无头 Chrome（会自动清理进程）
    logger.info("正在启动无头 Chrome...")
    
    # 步骤3: 启动监听程序
    try:
        capture_api_request(headless=True)
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        logger.info("程序将在 5 秒后退出...")
        time.sleep(5)


def start_valuescan_with_chrome():
    """
    有头模式启动流程:
    1. 关闭所有现有 Chrome 进程
    2. 以调试模式启动 Chrome (使用当前目录下的用户数据)
    3. 运行 ValueScan API 监听程序
    """
    logger.info("🚀 ValueScan 有头模式启动")
    logger.info("="*60)
    
    # 步骤1: 重启 Chrome 到调试模式
    if not restart_chrome_in_debug_mode():
        logger.error("❌ Chrome 启动失败，无法继续")
        logger.info("请检查:")
        logger.info("  1. Chrome 是否已正确安装")
        logger.info("  2. 端口 9222 是否被其他程序占用")
        logger.info("  3. 是否有足够的系统权限")
        logger.info("程序将在 5 秒后退出...")
        time.sleep(5)
        sys.exit(1)
    
    # 步骤2: 启动监听程序
    logger.info("="*60)
    logger.info("✅ Chrome 已就绪，正在启动 API 监听...")
    logger.info("="*60)
    
    # 启动主程序
    from valuescan import main
    try:
        main()
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        logger.info("程序将在 5 秒后退出...")
        time.sleep(5)


def main():
    """
    根据配置选择启动模式
    """
    if HEADLESS_MODE:
        logger.info("📋 检测到配置: HEADLESS_MODE = True")
        logger.info("📋 将使用无头模式启动（后台运行）")
        logger.info("")
        start_valuescan_headless()
    else:
        logger.info("📋 检测到配置: HEADLESS_MODE = False")
        logger.info("📋 将使用有头模式启动（显示浏览器）")
        logger.info("")
        start_valuescan_with_chrome()


if __name__ == "__main__":
    main()
