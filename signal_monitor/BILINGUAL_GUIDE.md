# Telegram 双语发送功能使用指南 / Bilingual Sending Guide

## 功能概述 / Overview

该功能支持同时向中文和英文频道发送交易信号，每个频道收到对应语言的消息。

This feature supports sending trading signals to both Chinese and English channels simultaneously, with each channel receiving messages in its respective language.

## 配置方法 / Configuration

### 1. 编辑配置文件 / Edit Configuration File

打开 `signal_monitor/config.py` (如果不存在，从 `config.example.py` 复制一份)

Open `signal_monitor/config.py` (copy from `config.example.py` if not exists)

### 2. 配置频道 ID / Configure Channel IDs

```python
# 中文频道配置 / Chinese Channels
TELEGRAM_CHAT_ID = [
    "-1001234567890",  # 中文主频道 / Main Chinese channel
    "-1009876543210"   # 中文备份频道 / Backup Chinese channel
]

# 英文频道配置 / English Channels
TELEGRAM_CHAT_ID_EN = [
    "-1005555555555",  # 英文主频道 / Main English channel
    "-1006666666666"   # 英文备份频道 / Backup English channel
]
```

### 3. 特殊说明 / Special Notes

- **中文频道必填** / Chinese channels are required
- **英文频道可选** / English channels are optional (leave empty `""` or `[]` to disable)
- 支持单个或多个频道 / Supports single or multiple channels for each language

## 配置示例 / Configuration Examples

### 示例 1: 只发送中文 / Example 1: Chinese Only

```python
TELEGRAM_CHAT_ID = "-1001234567890"  # 单个中文频道
TELEGRAM_CHAT_ID_EN = ""             # 不发送英文版本
```

### 示例 2: 中英双语 / Example 2: Bilingual

```python
TELEGRAM_CHAT_ID = [
    "-1001234567890",  # 中文主频道
    "-1002222222222"   # 中文VIP频道
]

TELEGRAM_CHAT_ID_EN = [
    "-1003333333333",  # 英文主频道
    "-1004444444444"   # 英文区域频道
]
```

### 示例 3: 多频道中文 + 单频道英文 / Example 3: Multi-CN + Single-EN

```python
TELEGRAM_CHAT_ID = [
    "-1001234567890",  # 中文公开频道
    "-1009876543210",  # 中文私密频道
    "123456789"        # 个人测试账号
]

TELEGRAM_CHAT_ID_EN = "-1005555555555"  # 英文频道
```

## 消息示例 / Message Examples

### 中文消息示例 / Chinese Message Example

```
🔴 $BTC 主力出逃警示
━━━━━━━━━
⚠️ 疑似主力大量减持
📉 风险增加，建议止盈
💵 现价: $45,123.45
📉 24H跌幅: -3.25%
🎯 AI评分: 72

💡 风险警示:
   • 🔴 主力疑似出逃
   • 📉 价格可能进入调整期
   • 💰 建议大部分止盈
   • 🛡️ 保护已有利润
   • ⛔ 不建议继续追高

#主力出逃
━━━━━━━━━
🕐 12:34:56 (UTC+8)
```

### 英文消息示例 / English Message Example

```
🔴 $BTC Major Outflow Warning
━━━━━━━━━
⚠️ Suspected massive sell-off by major players
📉 Risk increasing, consider take-profit
💵 Current Price: $45,123.45
📉 24H Change: -3.25%
🎯 AI Score: 72

💡 Risk Alert:
   • 🔴 Major players possibly exiting
   • 📉 Price may enter correction phase
   • 💰 Consider taking most profits
   • 🛡️ Protect existing gains
   • ⛔ Not recommended to chase highs

#MajorOutflow
━━━━━━━━━
🕐 12:34:56 (UTC+8)
```

## 支持的信号类型 / Supported Signal Types

所有信号类型都支持双语发送 / All signal types support bilingual sending:

| 类型 Type | 中文名称 | English Name |
|-----------|---------|--------------|
| 100 | AI 追踪 | AI Tracking |
| 108 | 资金异动 | Fund Movement |
| 109 | 上下币公告 | Listing Announcement |
| 110 | Alpha 机会 | Alpha Opportunity |
| 111 | 资金出逃 | Capital Flight |
| 112 | FOMO 加剧 | FOMO Intensification |
| 113 | FOMO 告警 | FOMO Alert |
| 114 | 资金异常 | Abnormal Funds |

## 图表支持 / Chart Support

异步生成的 K线图会自动发送到所有配置的频道（中文和英文），每个频道的图片说明使用对应语言。

Asynchronously generated K-line charts are automatically sent to all configured channels (Chinese and English), with each channel's image caption in its respective language.

## 日志示例 / Log Examples

### 成功发送到多个频道（双语） / Successful Multi-Channel (Bilingual) Sending

```
2025-12-26 12:34:56 [INFO] 📤 发送消息到 Telegram...
2025-12-26 12:34:56 [INFO]   📝 已生成英文版本消息
2025-12-26 12:34:56 [INFO]   ✅ Telegram 消息发送成功 (Chat ID: -1001234567890, CN)
2025-12-26 12:34:57 [INFO]   ✅ Telegram 消息发送成功 (Chat ID: -1009876543210, CN)
2025-12-26 12:34:58 [INFO]   ✅ Telegram 消息发送成功 (Chat ID: -1005555555555, EN)
2025-12-26 12:34:58 [INFO]   📊 消息发送统计: 成功 3/3 (CN:2, EN:1)
2025-12-26 12:35:10 [INFO] 📊 图表生成完成，等待 1.2秒后编辑消息: $BTC (任务ID: abc123)
2025-12-26 12:35:12 [INFO]   ✅ Telegram 消息编辑成功 (Chat ID: -1001234567890, Message ID: 123)
2025-12-26 12:35:13 [INFO]   ✅ Telegram 消息编辑成功 (Chat ID: -1009876543210, Message ID: 456)
2025-12-26 12:35:14 [INFO]   ✅ Telegram 消息编辑成功 (Chat ID: -1005555555555, Message ID: 789)
2025-12-26 12:35:14 [INFO]   📊 消息编辑统计: 成功 3/3
```

## 技术细节 / Technical Details

### 工作流程 / Workflow

1. **消息生成 / Message Generation**
   - 系统同时生成中文和英文两个版本的消息
   - The system generates both Chinese and English versions of the message

2. **频道分类 / Channel Classification**
   - 根据配置自动识别中文和英文频道
   - Automatically identifies Chinese and English channels based on configuration

3. **智能分发 / Smart Distribution**
   - 中文频道接收中文消息
   - Chinese channels receive Chinese messages
   - 英文频道接收英文消息
   - English channels receive English messages

4. **图表编辑 / Chart Editing**
   - 图表生成后，每个频道的图片说明使用对应语言
   - After chart generation, each channel's image caption uses its respective language

### 核心函数签名 / Core Function Signatures

```python
# 发送消息（支持双语）
def send_telegram_message(
    message_text,           # 中文消息 / Chinese message
    pin_message=False,
    message_text_en=None    # 英文消息（可选）/ English message (optional)
) -> dict

# 编辑消息添加图片（支持双语caption）
def edit_message_with_photo(
    message_ids,            # 消息ID字典 / Message ID dict
    photo_data,             # 图片数据 / Photo data
    caption=None,           # 中文说明 / Chinese caption
    caption_en=None         # 英文说明（可选）/ English caption (optional)
) -> bool

# 发送消息并异步生成图表（支持双语）
def send_message_with_async_chart(
    message_text,           # 中文消息 / Chinese message
    symbol,                 # 币种符号 / Symbol
    pin_message=False,
    message_text_en=None    # 英文消息（可选）/ English message (optional)
) -> dict
```

## 性能影响 / Performance Impact

- **发送时间 / Send Time**: 每个额外频道增加约 100-200ms / ~100-200ms per additional channel
- **建议频道数 / Recommended**: ≤ 5 个频道 / ≤ 5 channels total
- **网络要求 / Network**: 稳定的互联网连接 / Stable internet connection

## 常见问题 / FAQ

### Q1: 如何禁用英文发送？ / How to disable English sending?

**答 / Answer**:
```python
TELEGRAM_CHAT_ID_EN = ""  # 留空即可 / Leave empty
```

### Q2: 可以只发送英文吗？ / Can I send English only?

**答 / Answer**: 不可以，中文频道必填。如果只想发送英文，可以将中文和英文频道设置为相同的值。

No, Chinese channels are required. If you only want English, you can set the same channel for both Chinese and English.

### Q3: 英文翻译是自动的吗？ / Is English translation automatic?

**答 / Answer**: 是的，系统会自动生成英文版本的消息，不需要手动翻译。

Yes, the system automatically generates English versions of messages without manual translation.

### Q4: 英文消息和中文消息完全一致吗？ / Are English and Chinese messages identical?

**答 / Answer**: 内容一致，但表达方式符合各语言习惯。例如：
- 中文："主力出逃"
- English: "Major Outflow"

Content is identical, but expressions follow language conventions. For example:
- Chinese: "主力出逃"
- English: "Major Outflow"

### Q5: 如果英文消息生成失败会怎样？ / What happens if English message generation fails?

**答 / Answer**: 系统会记录警告日志，但不影响中文消息的发送。英文频道将不会收到消息。

The system logs a warning but continues sending Chinese messages. English channels won't receive the message.

## 版本历史 / Version History

### v2.1 (2025-12-26)
- ✅ 新增双语发送支持 / Added bilingual sending support
- ✅ 创建完整的英文消息模板 / Created complete English message templates
- ✅ 支持独立配置英文频道 / Support independent English channel configuration
- ✅ 图表caption支持双语 / Chart captions support bilingual
- ✅ 智能语言路由 / Smart language routing

## 联系支持 / Contact Support

如有问题，请查看：
- [MULTI_CHANNEL_GUIDE.md](MULTI_CHANNEL_GUIDE.md) - 多频道功能指南
- [CLAUDE.md](../CLAUDE.md) - 完整项目文档
- [README.md](../README.md) - 快速开始指南

For issues, please check:
- [MULTI_CHANNEL_GUIDE.md](MULTI_CHANNEL_GUIDE.md) - Multi-channel guide
- [CLAUDE.md](../CLAUDE.md) - Complete project documentation
- [README.md](../README.md) - Quick start guide
