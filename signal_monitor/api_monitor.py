"""
API 监听模块
负责监听 valuescan.io API 请求并捕获数据
"""

import json
import time
import platform
import os
from datetime import datetime, timezone, timedelta
from DrissionPage import ChromiumPage, ChromiumOptions

try:
    from .logger import logger
    from .config import (
        API_PATH,
        CHROME_DEBUG_PORT,
        SEND_TG_IN_MODE_1,
        ENABLE_IPC_FORWARDING,
    )
    from .message_handler import process_response_data
    from .binance_alpha_cache import get_binance_alpha_cache
    try:
        from .ipc_client import forward_signal as default_signal_callback
    except ImportError:
        default_signal_callback = None
except ImportError:  # 兼容脚本执行
    from logger import logger
    from config import (
        API_PATH,
        CHROME_DEBUG_PORT,
        SEND_TG_IN_MODE_1,
        ENABLE_IPC_FORWARDING,
    )
    from message_handler import process_response_data
    from binance_alpha_cache import get_binance_alpha_cache
    try:
        from ipc_client import forward_signal as default_signal_callback
    except ImportError:
        default_signal_callback = None

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))


def get_beijing_time_str(format_str='%Y-%m-%d %H:%M:%S'):
    """
    获取当前北京时间字符串
    
    Args:
        format_str: 时间格式字符串，默认为 '%Y-%m-%d %H:%M:%S'
    
    Returns:
        str: 格式化后的北京时间字符串（带UTC+8标识）
    """
    dt = datetime.now(tz=BEIJING_TZ)
    return dt.strftime(format_str) + ' (UTC+8)'


def _get_chrome_paths():
    """获取不同平台的 Chrome 浏览器路径"""
    system = platform.system()
    
    if system == "Windows":
        return [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "Linux":
        return [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        ]
    elif system == "Darwin":  # macOS
        return [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:
        return []


def _kill_chrome_processes():
    """关闭所有 Chrome 进程（跨平台支持）"""
    import subprocess
    import platform
    
    system = platform.system()
    logger.info(f"正在关闭现有的 Chrome 进程 (系统: {system})...")
    
    try:
        if system == "Windows":
            # Windows: 使用 taskkill
            subprocess.run(
                ['taskkill', '/F', '/IM', 'chrome.exe', '/T'],
                capture_output=True,
                timeout=5
            )
        elif system in ["Linux", "Darwin"]:
            # Linux/macOS: 更精确地匹配 Chrome/Chromium 可执行文件
            # 避免误杀包含 'chrome' 关键字的其他进程（如 Python 脚本）
            try:
                # 方法1: 使用 pgrep 找到进程，然后用 kill 关闭
                result = subprocess.run(
                    ['pgrep', '-f', '(google-chrome|chromium-browser|chromium).*--'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], timeout=2)
                        except:
                            pass
            except:
                # 方法2: 如果 pgrep 失败，尝试直接 pkill（更保守的模式）
                subprocess.run(
                    ['pkill', '-9', '-f', '(google-chrome|chromium-browser|chromium).*--'],
                    capture_output=True,
                    timeout=5
                )
        
        time.sleep(2)
        logger.info("Chrome 进程已清理")
    except Exception as e:
        logger.warning(f"清理 Chrome 进程时出现问题: {e}")


def capture_api_request(headless=False, signal_callback=None):
    """
    连接到调试模式的浏览器并监听 API 请求
    使用当前目录下的 Chrome 用户数据

    Args:
        headless: 是否使用无头模式（不显示浏览器窗口）
        signal_callback: 新消息回调（可选）
    """
    if signal_callback is None and ENABLE_IPC_FORWARDING and default_signal_callback:
        signal_callback = default_signal_callback

    # 启动币安Alpha缓存自动刷新
    logger.info("🚀 初始化币安Alpha交集缓存...")
    try:
        alpha_cache = get_binance_alpha_cache()
        alpha_cache.start_auto_refresh()
        cache_info = alpha_cache.get_cache_info()
        logger.info(f"✅ 币安Alpha缓存已启动: {cache_info['count']} 个交集代币")
    except Exception as e:
        logger.warning(f"⚠️ 币安Alpha缓存启动失败（功能将不可用）: {e}")

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
            
            # 跨平台参数
            co.set_argument('--disable-gpu')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--disable-software-rasterizer')
            
            # 尝试自动检测并设置 Chrome 路径
            chrome_paths = _get_chrome_paths()
            chrome_found = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    co.set_browser_path(chrome_path)
                    logger.info(f"  找到 Chrome: {chrome_path}")
                    chrome_found = True
                    break
            
            if not chrome_found:
                logger.warning("未找到 Chrome，将使用系统默认路径")
            
            page = ChromiumPage(addr_or_opts=co)
            logger.info("✅ 成功启动无头模式 Chrome")
            
            # 获取并显示 Chrome 进程 ID（跨平台）
            try:
                import subprocess
                import psutil
                time.sleep(1)  # 等待进程完全启动
                
                system = platform.system()
                chrome_pids = []
                
                # 查找 Chrome 进程（跨平台）
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        proc_name = proc.info['name']
                        if proc_name:
                            # 支持不同平台的进程名
                            chrome_names = ['chrome', 'chromium', 'google-chrome']
                            if any(name in proc_name.lower() for name in chrome_names):
                                cmdline = proc.info['cmdline']
                                if cmdline and 'chrome-debug-profile' in ' '.join(cmdline):
                                    chrome_pids.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if chrome_pids:
                    logger.info(f"📋 Chrome 进程 ID: {', '.join(map(str, chrome_pids))}")
                    logger.info(f"📋 主进程 PID: {chrome_pids[0]}")
            except ImportError:
                # 如果没有 psutil，使用系统命令
                try:
                    system = platform.system()
                    if system == "Windows":
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
                    else:  # Linux/macOS
                        result = subprocess.run(
                            ['pgrep', '-f', 'chrome-debug-profile'],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0 and result.stdout:
                            pids = result.stdout.strip().split('\n')
                            logger.info(f"📋 Chrome 进程 PID: {pids[0]}")
                except Exception as e:
                    logger.debug(f"获取进程 ID 失败: {e}")
            except Exception as e:
                logger.debug(f"获取进程 ID 失败: {e}")
            
            # 无头模式：自动打开网站
            try:
                logger.info("🌍 正在打开 https://www.valuescan.io/AIGEMs/longInflowAlert ...")
                page.get('https://www.valuescan.io/AIGEMs/longInflowAlert')
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
            logger.info(f"捕获到第 {request_count} 个请求! ({get_beijing_time_str()})")
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
                        process_response_data(
                            response_data,
                            send_to_telegram=SEND_TG_IN_MODE_1,
                            seen_ids=seen_message_ids,
                            signal_callback=signal_callback,
                        )
                        
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
