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


def _kill_chrome_processes():
    """关闭所有 Chrome 进程（仅在无头模式使用）"""
    import subprocess
    try:
        logger.info("正在关闭现有的 Chrome 进程...")
        subprocess.run(
            ['taskkill', '/F', '/IM', 'chrome.exe', '/T'],
            capture_output=True,
            timeout=5
        )
        time.sleep(2)
        logger.info("Chrome 进程已清理")
    except Exception as e:
        logger.warning(f"清理 Chrome 进程时出现问题: {e}")


def capture_api_request(headless=False):
    """
    连接到调试模式的浏览器并监听 API 请求
    使用当前目录下的 Chrome 用户数据
    
    Args:
        headless: 是否使用无头模式（不显示浏览器窗口）
    """
    # 无头模式下先关闭所有 Chrome 进程，避免用户目录冲突
    if headless:
        _kill_chrome_processes()
    
    # 配置浏览器选项
    try:
        co = ChromiumOptions()
        
        if headless:
            # 无头模式：启动新的 Chrome 实例
            logger.info("正在以无头模式启动 Chrome...")
            co.headless(True)  # 启用无头模式
            co.set_user_data_path('./chrome-debug-profile')  # 使用 chrome-debug-profile 用户目录
            co.set_argument('--disable-gpu')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            page = ChromiumPage(addr_or_opts=co)
            logger.info("✅ 成功启动无头模式 Chrome")
            
            # 获取并显示 Chrome 进程 ID
            try:
                import subprocess
                import psutil
                time.sleep(1)  # 等待进程完全启动
                
                # 查找 Chrome 进程
                chrome_pids = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'chrome.exe' in proc.info['name'].lower():
                            cmdline = proc.info['cmdline']
                            if cmdline and 'chrome-debug-profile' in ' '.join(cmdline):
                                chrome_pids.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if chrome_pids:
                    logger.info(f"📋 Chrome 进程 ID: {', '.join(map(str, chrome_pids))}")
                    logger.info(f"📋 主进程 PID: {chrome_pids[0]}")
            except ImportError:
                # 如果没有 psutil，使用 tasklist 命令
                try:
                    result = subprocess.run(
                        ['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/FO', 'CSV', '/NH'],
                        capture_output=True,
                        text=True,
                        encoding='gbk'
                    )
                    if result.returncode == 0 and result.stdout:
                        lines = result.stdout.strip().split('\n')
                        if lines and lines[0]:
                            first_line = lines[0].strip('"').split('","')
                            if len(first_line) >= 2:
                                pid = first_line[1]
                                logger.info(f"📋 Chrome 进程 PID: {pid}")
                except Exception as e:
                    logger.debug(f"获取进程 ID 失败: {e}")
            except Exception as e:
                logger.debug(f"获取进程 ID 失败: {e}")
            
            # 无头模式：自动打开网站
            try:
                logger.info("🌍 正在打开 https://valuescan.io ...")
                page.get('https://valuescan.io')
                time.sleep(2)  # 等待页面加载
                logger.info("✅ 网站已自动打开")
            except Exception as e:
                logger.error(f"打开网站失败: {e}")
                logger.warning("请检查网络连接和登录状态")
        else:
            # 有头模式：连接到已有的调试端口
            co.set_local_port(CHROME_DEBUG_PORT)  # 连接到调试端口
            page = ChromiumPage(addr_or_opts=co)
            logger.info(f"成功连接到调试端口 {CHROME_DEBUG_PORT} 的浏览器")
            
    except Exception as e:
        logger.error(f"{'启动' if headless else '连接'}浏览器失败: {e}")
        if not headless:
            logger.error(f"请确保 Chrome 已在调试模式下运行 (端口 {CHROME_DEBUG_PORT})")
        return
    
    # 启动监听
    page.listen.start(API_PATH)
    logger.info("开始监听 API 请求...")
    logger.info(f"目标 URL: https://api.valuescan.io/{API_PATH}")
    
    if not headless:
        logger.info("请在浏览器中访问相关页面触发 API 请求...")
    
    # 持续监听并捕获请求
    logger.info("提示: 按 Ctrl+C 停止监听")
    
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
    
    except KeyboardInterrupt:
        elapsed_hours = (time.time() - start_time) / 3600
        logger.info(f"监听已停止 (运行时长: {elapsed_hours:.1f} 小时, 捕获 {request_count} 个请求)")
    finally:
        page.listen.stop()
        logger.info("监听已关闭")
