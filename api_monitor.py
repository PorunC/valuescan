"""
API 监听模块
负责监听 valuescan.io API 请求并捕获数据
"""

import json
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from logger import logger
from config import API_PATH, CHROME_DEBUG_PORT, SEND_TG_IN_MODE_1
from message_handler import process_response_data

# 尝试导入自动重启配置
try:
    from config import CHROME_AUTO_RESTART_HOURS
except ImportError:
    CHROME_AUTO_RESTART_HOURS = 0


def capture_api_request():
    """
    连接到调试模式的浏览器并监听 API 请求
    使用当前目录下的 Chrome 用户数据
    """
    # 配置浏览器选项，连接到调试端口
    try:
        co = ChromiumOptions()
        co.set_local_port(CHROME_DEBUG_PORT)  # 连接到调试端口
        page = ChromiumPage(addr_or_opts=co)
        logger.info(f"成功连接到调试端口 {CHROME_DEBUG_PORT} 的浏览器")
    except Exception as e:
        logger.error(f"连接浏览器失败: {e}")
        logger.error(f"请确保 Chrome 已在调试模式下运行 (端口 {CHROME_DEBUG_PORT})")
        return
    
    # 启动监听
    page.listen.start(API_PATH)
    logger.info("开始监听 API 请求...")
    logger.info(f"目标 URL: https://api.valuescan.io/{API_PATH}")
    logger.info("请在浏览器中访问相关页面触发 API 请求...")
    
    # 持续监听并捕获请求
    logger.info("提示: 按 Ctrl+C 停止监听")
    
    # 自动重启提示
    if CHROME_AUTO_RESTART_HOURS > 0:
        logger.info(f"⏰ 自动重启: 每 {CHROME_AUTO_RESTART_HOURS} 小时")
    
    request_count = 0
    seen_message_ids = set()  # 用于记录已经显示过的消息 ID
    start_time = time.time()  # 记录启动时间
    
    try:
        # 持续监听
        for packet in page.listen.steps():
            request_count += 1
            
            logger.info("="*60)
            logger.info(f"捕获到第 {request_count} 个请求! ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            logger.info("="*60)
            
            # 响应信息
            if packet.response:
                try:
                    logger.info(f"响应状态码: {packet.response.status}")
                    
                    try:
                        response_body = packet.response.body
                        if isinstance(response_body, str):
                            response_data = json.loads(response_body)
                        else:
                            response_data = response_body
                        
                        # 处理响应数据（启用去重，根据全局配置决定是否发送TG）
                        process_response_data(response_data, send_to_telegram=SEND_TG_IN_MODE_1, seen_ids=seen_message_ids)
                        
                        logger.info(f"  原始完整响应已省略，如需查看请修改代码")
                    except Exception as e:
                        logger.error(f"  响应体解析失败: {e}")
                        logger.error(packet.response.body)
                except Exception as e:
                    logger.error(f"响应信息获取失败: {e}")
            
            logger.info("="*60)
            logger.info("等待下一个请求...")
            logger.info("="*60)
            
            # 检查是否需要自动重启
            if CHROME_AUTO_RESTART_HOURS > 0:
                elapsed_hours = (time.time() - start_time) / 3600
                if elapsed_hours >= CHROME_AUTO_RESTART_HOURS:
                    logger.info("="*60)
                    logger.info(f"⏰ 已运行 {elapsed_hours:.1f} 小时，触发自动重启")
                    logger.info(f"📊 本次运行统计: 捕获 {request_count} 个请求")
                    logger.info("="*60)
                    break  # 退出循环，触发重启
    
    except KeyboardInterrupt:
        elapsed_hours = (time.time() - start_time) / 3600
        logger.info(f"监听已停止 (运行时长: {elapsed_hours:.1f} 小时, 捕获 {request_count} 个请求)")
    finally:
        page.listen.stop()
        logger.info("监听已关闭")
