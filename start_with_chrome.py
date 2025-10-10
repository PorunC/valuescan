"""
ValueScan 一键启动脚本
自动处理 Chrome 调试模式启动并运行主程序
支持定时自动重启功能，防止内存泄漏导致卡顿
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


def start_with_auto_restart():
    """
    带自动重启功能的启动流程
    根据配置定时重启 Chrome 和监听程序，防止内存泄漏
    """
    try:
        from config import CHROME_AUTO_RESTART_HOURS
    except ImportError:
        logger.warning("⚠️ 未找到 CHROME_AUTO_RESTART_HOURS 配置，使用默认值 0（不自动重启）")
        CHROME_AUTO_RESTART_HOURS = 0
    
    if CHROME_AUTO_RESTART_HOURS <= 0:
        logger.info("ℹ️ 自动重启功能已禁用")
        start_valuescan_with_chrome()
        return
    
    restart_count = 0
    
    while True:
        restart_count += 1
        
        if restart_count > 1:
            logger.info("="*60)
            logger.info(f"🔄 第 {restart_count} 次自动重启")
            logger.info("="*60)
        else:
            logger.info(f"⏰ 已启用自动重启功能（每 {CHROME_AUTO_RESTART_HOURS} 小时）")
        
        try:
            # 启动 Chrome 和监听程序
            start_valuescan_with_chrome()
            
            # 如果正常退出（用户按 Ctrl+C），则不再重启
            logger.info("程序已正常退出，不再重启")
            break
            
        except KeyboardInterrupt:
            logger.info("收到停止信号，程序退出")
            break
            
        except Exception as e:
            logger.error(f"程序异常退出: {e}")
            logger.info(f"将在 {CHROME_AUTO_RESTART_HOURS} 小时后自动重启...")
            
        # 等待指定时间后重启
        restart_seconds = CHROME_AUTO_RESTART_HOURS * 3600
        logger.info(f"⏳ 下次重启时间: {CHROME_AUTO_RESTART_HOURS} 小时后")
        logger.info(f"💡 提示: 按 Ctrl+C 可以停止自动重启")
        
        try:
            time.sleep(restart_seconds)
        except KeyboardInterrupt:
            logger.info("收到停止信号，取消自动重启")
            break


if __name__ == "__main__":
    # 使用带自动重启功能的启动方式
    start_with_auto_restart()
