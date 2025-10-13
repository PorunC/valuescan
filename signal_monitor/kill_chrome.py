"""
Chrome 进程管理工具
用于关闭所有 Chrome 进程并以调试模式启动 Chrome
支持 Windows、Linux 和 macOS
"""

import subprocess
import time
import sys
import os
import platform
from logger import logger
from config import CHROME_DEBUG_PORT


def kill_all_chrome_processes():
    """
    关闭所有 Chrome 相关进程（跨平台支持）
    """
    system = platform.system()
    logger.info(f"正在关闭 Chrome 进程 (系统: {system})...")
    
    try:
        if system == "Windows":
            # Windows: 使用 taskkill
            chrome_processes = ['chrome.exe', 'chromedriver.exe']
            
            for process_name in chrome_processes:
                try:
                    logger.info(f"正在关闭 {process_name}...")
                    result = subprocess.run(
                        ['taskkill', '/F', '/IM', process_name, '/T'],
                        capture_output=True,
                        text=True,
                        encoding='gbk'
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"✅ {process_name} 进程已关闭")
                    else:
                        if "找不到" in result.stderr or "not found" in result.stderr.lower():
                            logger.info(f"ℹ️  未找到运行中的 {process_name} 进程")
                        else:
                            logger.warning(f"关闭 {process_name} 时出现提示: {result.stderr.strip()}")
                            
                except Exception as e:
                    logger.error(f"关闭 {process_name} 时发生错误: {e}")
        
        elif system in ["Linux", "Darwin"]:
            # Linux/macOS: 使用更精确的进程匹配，避免误杀 Python 脚本
            try:
                # 尝试使用 pgrep + kill 更精确匹配 Chrome 可执行文件
                result = subprocess.run(
                    ['pgrep', '-f', '(google-chrome|chromium-browser|chromium|chromedriver).*--'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout.strip():
                    # 找到进程，逐个 kill
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], timeout=2)
                        except Exception as e:
                            logger.warning(f"关闭进程 {pid} 失败: {e}")
                    logger.info(f"✅ 已关闭 {len(pids)} 个 Chrome 进程")
                else:
                    logger.info("ℹ️  未找到运行中的 Chrome 进程")
                    
            except FileNotFoundError:
                # 如果没有 pgrep，回退到 pkill（但仍使用更精确的模式）
                try:
                    subprocess.run(
                        ['pkill', '-9', '-f', '(google-chrome|chromium-browser|chromium|chromedriver).*--'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    logger.info("✅ Chrome 进程已关闭")
                except Exception as e:
                    logger.error(f"关闭 Chrome 进程时发生错误: {e}")
            except Exception as e:
                logger.error(f"关闭 Chrome 进程时发生错误: {e}")
        
        # 等待进程完全关闭
        time.sleep(2)
        logger.info("所有 Chrome 进程已清理完成")
        
    except Exception as e:
        logger.error(f"清理进程时发生错误: {e}")


def start_chrome_debug_mode(port=None):
    """
    以调试模式启动 Chrome（跨平台支持）
    
    Args:
        port: 远程调试端口，默认使用配置文件中的端口
    """
    if port is None:
        port = CHROME_DEBUG_PORT
    
    system = platform.system()
    
    # 不同平台的 Chrome 安装路径
    if system == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "Linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]
    elif system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:
        logger.error(f"❌ 不支持的操作系统: {system}")
        return False
    
    # 查找 Chrome 可执行文件
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        logger.error(f"❌ 未找到 Chrome 浏览器 (系统: {system})")
        logger.error("尝试的路径:")
        for path in chrome_paths:
            logger.error(f"  - {path}")
        return False
    
    logger.info(f"找到 Chrome: {chrome_exe}")
    logger.info(f"正在以调试模式启动 Chrome (端口: {port})...")
    
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Chrome 用户数据目录路径（存储在当前文件夹下）
        user_data_dir = os.path.join(current_dir, "chrome-debug-profile")
        
        logger.info(f"Chrome 数据目录: {user_data_dir}")
        
        # 启动 Chrome 的命令参数
        chrome_args = [
            chrome_exe,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",  # 使用当前文件夹下的独立用户数据目录
            "--no-first-run",  # 跳过首次运行体验
            "--no-default-browser-check",  # 跳过默认浏览器检查
            "https://valuescan.io"  # 自动打开 valuescan.io 网站
        ]
        
        # 使用 subprocess.Popen 启动 Chrome（非阻塞）
        process = subprocess.Popen(
            chrome_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )
        
        # 等待 Chrome 启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            logger.info(f"✅ Chrome 已成功启动 (PID: {process.pid})")
            logger.info(f"📍 调试端口: {port}")
            logger.info(f"🌐 调试地址: http://localhost:{port}")
            logger.info(f"🌍 已自动打开: https://valuescan.io")
            return True
        else:
            logger.error("❌ Chrome 启动失败")
            return False
            
    except Exception as e:
        logger.error(f"启动 Chrome 时发生错误: {e}")
        return False


def restart_chrome_in_debug_mode(port=None):
    """
    重启 Chrome 到调试模式（先关闭所有进程，再启动调试模式）
    
    Args:
        port: 远程调试端口，默认使用配置文件中的端口
    
    Returns:
        bool: 启动成功返回 True，否则返回 False
    """
    logger.info("="*60)
    logger.info("开始重启 Chrome 到调试模式")
    logger.info("="*60)
    
    # 1. 关闭所有 Chrome 进程
    kill_all_chrome_processes()
    
    # 2. 以调试模式启动 Chrome
    success = start_chrome_debug_mode(port)
    
    if success:
        logger.info("="*60)
        logger.info("✅ Chrome 调试模式启动完成")
        logger.info("="*60)
    else:
        logger.error("="*60)
        logger.error("❌ Chrome 调试模式启动失败")
        logger.error("="*60)
    
    return success


if __name__ == "__main__":
    # 当直接运行此脚本时，执行重启操作
    restart_chrome_in_debug_mode()
