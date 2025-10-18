"""
本地 IPC 客户端
负责将 ValueScan 捕获的信号转发到交易模块
"""

import json
import socket
import time
from typing import Any, Dict, Optional

try:
    from .logger import logger
    from .config import (
        ENABLE_IPC_FORWARDING,
        IPC_HOST,
        IPC_PORT,
        IPC_CONNECT_TIMEOUT,
        IPC_RETRY_DELAY,
        IPC_MAX_RETRIES,
    )
except ImportError:  # 兼容脚本执行
    from logger import logger
    from config import (
        ENABLE_IPC_FORWARDING,
        IPC_HOST,
        IPC_PORT,
        IPC_CONNECT_TIMEOUT,
        IPC_RETRY_DELAY,
        IPC_MAX_RETRIES,
    )

# 支持的交易信号类型
FORWARD_TYPES = {110, 112, 113}


def _build_payload(item: Dict[str, Any], parsed_content: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    msg_type = item.get("type")
    if msg_type not in FORWARD_TYPES:
        return None

    message_id = item.get("id") or item.get("messageId")
    if not message_id:
        logger.debug("IPC 转发跳过：缺少 message_id => %s", item)
        return None

    payload = {
        "message_type": msg_type,
        "message_id": str(message_id),
        "title": item.get("title"),
        "symbol_hint": None,
        "created_time": item.get("createTime"),
        "data": {
            "raw_message": item,
            "content": parsed_content or {},
        },
    }

    if parsed_content and isinstance(parsed_content, dict):
        payload["symbol_hint"] = (
            parsed_content.get("symbol")
            or parsed_content.get("pair")
            or parsed_content.get("symbolName")
        )

    if not payload["symbol_hint"]:
        # 兜底：尝试从标题中解析
        title = item.get("title")
        if isinstance(title, str) and title:
            payload["symbol_hint"] = title.split(" ")[0]

    return payload


def _send_payload(payload: Dict[str, Any]) -> bool:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n"

    for attempt in range(1, IPC_MAX_RETRIES + 1):
        try:
            with socket.create_connection(
                (IPC_HOST, IPC_PORT), timeout=IPC_CONNECT_TIMEOUT
            ) as conn:
                conn.sendall(data)
            return True
        except (ConnectionRefusedError, TimeoutError, OSError) as exc:
            logger.warning(
                "IPC 信号发送失败 (第 %s 次尝试): %s", attempt, exc
            )
            if attempt < IPC_MAX_RETRIES:
                time.sleep(IPC_RETRY_DELAY)
    return False


def forward_signal(item: Dict[str, Any], parsed_content: Optional[Dict[str, Any]]):
    """
    将捕获到的 ValueScan 信号通过本地 IPC 发送给交易模块
    """
    if not ENABLE_IPC_FORWARDING:
        return

    payload = _build_payload(item, parsed_content)
    if not payload:
        return

    success = _send_payload(payload)
    if success:
        logger.info(
            "📡 IPC 已转发信号: type=%s id=%s symbol_hint=%s",
            payload["message_type"],
            payload["message_id"],
            payload["symbol_hint"],
        )
    else:
        logger.error(
            "❌ IPC 信号转发失败: id=%s type=%s",
            payload.get("message_id"),
            payload.get("message_type"),
        )
