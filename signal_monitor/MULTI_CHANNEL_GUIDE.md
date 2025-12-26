# Telegram 多频道发送功能使用指南

## 功能概述

该功能允许信号监控系统同时向多个 Telegram 频道或用户发送消息，支持：
- ✅ 同时向多个频道发送文字消息
- ✅ 同时向多个频道发送图片消息
- ✅ 同时编辑多个频道的消息（添加图表）
- ✅ 同时置顶多个频道的消息
- ✅ 向后兼容单频道配置

## 配置方法

### 1. 编辑配置文件

打开 `signal_monitor/config.py`（如果不存在，从 `config.example.py` 复制一份）

### 2. 配置 Chat ID

#### 单个频道配置（向后兼容）
```python
TELEGRAM_CHAT_ID = "-1001234567890"
```

#### 多个频道配置（推荐）
```python
TELEGRAM_CHAT_ID = [
    "-1001234567890",  # 频道1
    "-1009876543210",  # 频道2
    "123456789"        # 私聊用户
]
```

### 3. 获取 Chat ID 的方法

#### 获取私聊用户 ID
1. 在 Telegram 中找到 `@userinfobot`
2. 发送任意消息
3. Bot 会回复你的用户 ID（纯数字，如 `123456789`）

#### 获取频道 ID
1. 将你的 Bot 添加为频道管理员
2. 方法一：使用 `@userinfobot`
   - 转发频道的任意一条消息给 `@userinfobot`
   - Bot 会显示频道 ID（格式：`-100` 开头的数字）
3. 方法二：使用 Telegram API
   - 在频道发送任意消息
   - 使用 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 查看消息
   - 在返回的 JSON 中找到 `chat.id` 字段

#### 获取群组 ID
方法同频道 ID，群组 ID 通常是负数（如 `-123456789`）

## 配置示例

### 示例 1: 单个频道
```python
# 适合只有一个目标频道的情况
TELEGRAM_CHAT_ID = "-1001234567890"
```

### 示例 2: 两个频道
```python
# 同时向两个频道发送信号
TELEGRAM_CHAT_ID = [
    "-1001234567890",  # 主频道
    "-1009876543210"   # 备份频道
]
```

### 示例 3: 多个频道 + 私聊
```python
# 向多个频道和个人账号同时发送
TELEGRAM_CHAT_ID = [
    "-1001234567890",  # 公开频道
    "-1009876543210",  # 私密频道
    "-123456789",      # 测试群组
    "987654321"        # 个人账号（自己）
]
```

## 功能特性

### 1. 批量发送统计

发送消息时会显示统计信息：
```
✅ Telegram 消息发送成功 (Chat ID: -1001234567890)
✅ Telegram 消息发送成功 (Chat ID: -1009876543210)
📊 消息发送统计: 成功 2/2
```

### 2. 失败处理

如果某个频道发送失败，其他频道不受影响：
```
✅ Telegram 消息发送成功 (Chat ID: -1001234567890)
❌ Telegram 消息发送失败 (Chat ID: -1009876543210): 403 Forbidden
📊 消息发送统计: 成功 1/2
```

### 3. 自动重试

- 遇到 429 速率限制时自动等待并重试（最多 3 次）
- 自动处理 Telegram API 的 `retry_after` 参数
- 支持递增延迟（2s, 4s, 6s）

### 4. 图表生成支持

异步生成的 K线图会自动发送到所有配置的频道：
```
📊 图表生成完成，等待 1.2秒后编辑消息
✅ Telegram 消息编辑成功 (Chat ID: -1001234567890, Message ID: 123)
✅ Telegram 消息编辑成功 (Chat ID: -1009876543210, Message ID: 456)
📊 消息编辑统计: 成功 2/2
```

## 测试方法

### 方法 1: 使用测试脚本

```bash
cd signal_monitor
python test_multi_channel.py
```

测试脚本会：
1. 验证 `_normalize_chat_ids()` 函数
2. 显示当前配置的频道列表
3. 询问是否发送测试消息

### 方法 2: 使用内置测试工具

```bash
cd signal_monitor
python test_telegram.py
```

这个脚本会向配置的所有频道发送测试消息。

## 常见问题

### Q1: Bot 发送失败，显示 403 Forbidden？

**原因**: Bot 没有权限向该频道发送消息

**解决方法**:
1. 将 Bot 添加为频道管理员
2. 确保 Bot 有 "发送消息" 权限
3. 如果是群组，确保 Bot 已加入群组

### Q2: 如何确认 Chat ID 是否正确？

**验证方法**:
```bash
# 使用 curl 测试（替换 <YOUR_BOT_TOKEN> 和 <CHAT_ID>）
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=测试消息"
```

如果返回 `"ok": true`，说明 Chat ID 正确。

### Q3: 只想向某些频道发送特定类型的信号？

**当前限制**: 目前所有配置的频道会接收相同的信号

**未来计划**: 可以通过修改 `telegram.py` 添加过滤逻辑，例如：
```python
# 示例（需要自行实现）
CHANNEL_FILTERS = {
    "-1001234567890": ["type_110", "type_112", "type_113"],  # 只接收交易信号
    "-1009876543210": None  # 接收所有信号
}
```

### Q4: 多频道会影响发送速度吗？

**影响**: 会略微延长发送时间，但不会造成明显延迟

**原因**:
- 每个频道按顺序发送（串行）
- 单次 API 调用约 10-100ms
- 3 个频道约增加 200-300ms

**优化建议**:
- 限制频道数量在 5 个以内
- 避免配置相同的频道 ID

### Q5: 配置错误会导致程序崩溃吗？

**不会**，代码有完善的错误处理：
```python
# 空配置 - 只记录警告，不崩溃
TELEGRAM_CHAT_ID = ""
# 或
TELEGRAM_CHAT_ID = []

# 混合配置 - 自动规范化
TELEGRAM_CHAT_ID = "-1001234567890"  # 自动转为 ["-1001234567890"]
```

## 日志示例

### 成功发送到多个频道
```
2025-12-24 12:34:56 [INFO] 📝 立即发送融合信号（文字）: $BTC
2025-12-24 12:34:56 [INFO]   ✅ Telegram 消息发送成功 (Chat ID: -1001234567890)
2025-12-24 12:34:56 [INFO]   📌 消息已置顶 (Chat ID: -1001234567890, Message ID: 123)
2025-12-24 12:34:57 [INFO]   ✅ Telegram 消息发送成功 (Chat ID: -1009876543210)
2025-12-24 12:34:57 [INFO]   📌 消息已置顶 (Chat ID: -1009876543210, Message ID: 456)
2025-12-24 12:34:57 [INFO]   📊 消息发送统计: 成功 2/2
2025-12-24 12:35:10 [INFO] 📊 图表生成完成，等待 1.5秒后编辑融合信号: $BTC (任务ID: abc123)
2025-12-24 12:35:12 [INFO]   ✅ Telegram 消息编辑成功 (Chat ID: -1001234567890, Message ID: 123)
2025-12-24 12:35:13 [INFO]   ✅ Telegram 消息编辑成功 (Chat ID: -1009876543210, Message ID: 456)
2025-12-24 12:35:13 [INFO]   📊 消息编辑统计: 成功 2/2
```

### 部分频道失败
```
2025-12-24 12:40:00 [INFO]   ✅ Telegram 消息发送成功 (Chat ID: -1001234567890)
2025-12-24 12:40:01 [ERROR]   ❌ Telegram 消息发送失败 (Chat ID: -1009876543210): 403 - {"ok":false,"error_code":403,"description":"Forbidden: bot was blocked by the user"}
2025-12-24 12:40:01 [INFO]   📊 消息发送统计: 成功 1/2
```

## 版本兼容性

- ✅ **向后兼容**: 原有的单频道配置（字符串格式）仍然有效
- ✅ **自动转换**: 字符串格式会自动转为列表格式
- ✅ **旧代码支持**: `edit_message_with_photo()` 支持旧的单 `message_id` 参数

## 技术细节

### 数据结构变化

**发送前**:
```python
TELEGRAM_CHAT_ID = ["-1001234567890", "-1009876543210"]
```

**发送后返回值**:
```python
{
    "success": True,
    "message_ids": {
        "-1001234567890": 123,
        "-1009876543210": 456
    }
}
```

### 核心函数签名

```python
# 规范化 Chat ID
def _normalize_chat_ids(chat_id_config) -> list

# 发送消息（支持多频道）
def send_telegram_message(message_text, pin_message=False) -> dict

# 发送图片（支持多频道）
def send_telegram_photo(photo_data, caption=None, pin_message=False) -> bool

# 编辑消息（支持多频道）
def edit_message_with_photo(message_ids, photo_data, caption=None) -> bool

# 置顶消息（新增 chat_id 参数）
def _pin_telegram_message(chat_id, message_id) -> bool
```

## 更新日志

### v2.0 (2025-12-24)
- ✅ 新增多频道发送支持
- ✅ 自动统计发送成功/失败数量
- ✅ 改进错误处理和日志输出
- ✅ 添加向后兼容性支持
- ✅ 新增测试脚本 `test_multi_channel.py`

## 联系支持

如有问题，请检查：
1. [CLAUDE.md](../CLAUDE.md) - 项目完整文档
2. [README.md](../README.md) - 快速开始指南
3. [Issues](https://github.com/your-repo/valuescan/issues) - 提交 Bug 或功能请求
