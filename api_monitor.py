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
    logger.info("\n请在浏览器中访问相关页面触发 API 请求...")
    
    # 持续监听并捕获请求
    logger.info("\n提示: 按 Ctrl+C 停止监听\n")
    
    request_count = 0
    seen_message_ids = set()  # 用于记录已经显示过的消息 ID
    
    try:
        # 持续监听
        for packet in page.listen.steps():
            request_count += 1
            
            logger.info("\n" + "="*60)
            logger.info(f"捕获到第 {request_count} 个请求! ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            logger.info("="*60)
            
            # 请求信息
            logger.info(f"\n请求 URL: {packet.url}")
            logger.info(f"请求方法: {packet.method}")
            
            # 请求体
            try:
                request_body = packet.request.body if hasattr(packet, 'request') else packet.postData if hasattr(packet, 'postData') else None
                if request_body:
                    logger.info("\n【请求体】")
                    try:
                        body = json.loads(request_body)
                        logger.info(json.dumps(body, indent=2, ensure_ascii=False))
                    except:
                        logger.info(request_body)
            except Exception as e:
                logger.warning(f"\n请求体获取失败: {e}")
            
            # 响应信息
            if packet.response:
                try:
                    logger.info(f"\n响应状态码: {packet.response.status}")
                    
                    # 响应体 - 提取重要信息
                    logger.info("\n【响应体 - 重要信息提取】")
                    try:
                        response_body = packet.response.body
                        if isinstance(response_body, str):
                            response_data = json.loads(response_body)
                        else:
                            response_data = response_body
                        
                        # 处理响应数据（启用去重，根据全局配置决定是否发送TG）
                        process_response_data(response_data, send_to_telegram=SEND_TG_IN_MODE_1, seen_ids=seen_message_ids)
                        
                        logger.info(f"\n  原始完整响应已省略，如需查看请修改代码")
                    except Exception as e:
                        logger.error(f"  响应体解析失败: {e}")
                        logger.error(packet.response.body)
                except Exception as e:
                    logger.error(f"\n响应信息获取失败: {e}")
            
            logger.info("\n" + "="*60)
            logger.info("等待下一个请求...")
            logger.info("="*60)
    
    except KeyboardInterrupt:
        logger.info(f"\n\n监听已停止 (共捕获 {request_count} 个请求)")
    finally:
        page.listen.stop()
        logger.info("监听已关闭")
