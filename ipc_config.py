"""
本地 IPC 桥接配置
供 signal_monitor 与 binance_trader 共同使用
"""

# 监听地址和端口（使用环回地址保证仅本机访问）
IPC_HOST = "127.0.0.1"
IPC_PORT = 8765

# 连接/发送超时（秒）
IPC_CONNECT_TIMEOUT = 1.5

# 失败时的重试等待（秒）
IPC_RETRY_DELAY = 2.0

# 允许的重试次数
IPC_MAX_RETRIES = 3

__all__ = [
    "IPC_HOST",
    "IPC_PORT",
    "IPC_CONNECT_TIMEOUT",
    "IPC_RETRY_DELAY",
    "IPC_MAX_RETRIES",
]
