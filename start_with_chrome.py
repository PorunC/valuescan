"""
ValueScan 一键启动脚本
自动处理 Chrome 调试模式启动并运行主程序
"""

import sys
import time
from logger import logger
from kill_chrome import restart_chrome_in_debug_mode
from valuescan import main


def start_valuescan_with_chrome():
    """
    完整启动流程:
    1. 关闭所有现有 Chrome 进程
    2. 以调试模式启动 Chrome (使用当前目录下的用户数据)
    3. 运行 ValueScan API 监听程序
    """
    logger.info("🚀 ValueScan 一键启动")
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
    try:
        main()
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        logger.info("程序将在 5 秒后退出...")
        time.sleep(5)


if __name__ == "__main__":
    start_valuescan_with_chrome()
