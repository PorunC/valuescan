# Binance 自动化交易系统

基于 ValueScan 信号聚合的智能交易系统

## 📖 项目概述

这是一个智能的加密货币自动交易系统，通过聚合来自 ValueScan 的多个信号类型，在高概率交易机会出现时自动执行交易。

### 核心策略

**信号聚合 (Signal Confluence)**

系统监听两种关键信号：
- **FOMO 信号** (Type 113, 112): 市场情绪高涨，可能出现快速上涨
- **Alpha 信号** (Type 110): 存在超额收益机会

当这两个信号在**短时间窗口内（默认5分钟）**同时出现在**同一标的**时，系统判定为高质量交易机会。

### 为什么这个策略有效？

1. **多重确认** - 单一信号可能是噪音，多信号聚合大幅提升准确性
2. **时间敏感** - 加密市场变化快，信号时效性很重要
3. **情绪+基本面** - FOMO代表市场情绪，Alpha代表价值发现，双重验证
4. **风险可控** - 严格的仓位管理和止损机制

## 🏗️ 系统架构

```
binance_trader/
├── signal_aggregator.py    # 信号聚合器（核心逻辑）
├── trader.py               # 币安交易执行器
├── risk_manager.py         # 风险管理和仓位控制
├── main.py                 # 主程序入口
├── config.example.py       # 配置文件模板
└── README.md              # 本文档
```

### 数据流

```
ValueScan API
    ↓
[信号监控] signal_monitor/
    ↓
[信号聚合器] signal_aggregator.py
    ├─ 时间窗口匹配
    ├─ 信号评分
    └─ 输出聚合信号
        ↓
[风险管理器] risk_manager.py
    ├─ 仓位计算
    ├─ 风险检查
    └─ 生成交易建议
        ↓
[交易执行器] trader.py
    ├─ 市价买入
    ├─ 设置止损
    └─ 设置止盈
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install python-binance
```

### 2. 配置系统

复制配置文件模板：

```bash
cd binance_trader
cp config.example.py config.py
```

编辑 `config.py`，填入你的配置：

```python
# Binance API 配置
BINANCE_API_KEY = "your_api_key"
BINANCE_API_SECRET = "your_api_secret"

# ⚠️ 强烈建议先用测试网
USE_TESTNET = True

# 自动交易开关（建议先关闭观察）
AUTO_TRADING_ENABLED = False
```

### 3. 获取 Binance API 密钥

**生产环境:**
1. 访问 [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. 创建 API Key
3. 启用 "Spot & Margin Trading"
4. **重要**: 设置 IP 白名单以增强安全性

**测试网 (推荐先用这个):**
1. 访问 [Binance Testnet](https://testnet.binance.vision/)
2. 注册并获取测试 API Key
3. 使用测试网 USDT 进行无风险测试

### 4. 运行系统

```bash
python main.py
```

选择运行模式：
- **模式 1**: 整合信号监控（自动捕获信号）
- **模式 2**: 独立模式（手动输入信号）
- **模式 3**: 测试信号聚合功能

### 5. 测试信号聚合

在正式运行前，建议先测试信号聚合逻辑：

```bash
python main.py
# 选择 3 - Test signal aggregation
```

这会模拟 FOMO 和 Alpha 信号，验证聚合逻辑是否正常工作。

## ⚙️ 配置说明

### 信号聚合参数

```python
# 时间窗口（秒）- FOMO和Alpha信号需在此时间内出现
SIGNAL_TIME_WINDOW = 300  # 5分钟

# 最低信号评分 (0-1)
MIN_SIGNAL_SCORE = 0.6  # 低于0.6的信号会被忽略

# 是否启用 FOMO 加剧信号 (Type 112)
ENABLE_FOMO_INTENSIFY = True
```

**如何调整：**
- 缩短 `SIGNAL_TIME_WINDOW` = 更严格的匹配，信号更少但质量更高
- 提高 `MIN_SIGNAL_SCORE` = 只交易最高质量信号
- 关闭 `ENABLE_FOMO_INTENSIFY` = 只使用 Type 113 FOMO 信号

### 风险管理参数

```python
# 仓位控制
MAX_POSITION_PERCENT = 10.0        # 单币种最多10%
MAX_TOTAL_POSITION_PERCENT = 50.0  # 所有持仓合计不超过50%

# 交易限制
MAX_DAILY_TRADES = 20             # 每天最多20笔交易
MAX_DAILY_LOSS_PERCENT = 5.0      # 单日亏损5%自动停止

# 止损止盈
STOP_LOSS_PERCENT = 3.0           # 下跌3%止损
TAKE_PROFIT_1_PERCENT = 5.0       # 上涨5%卖出50%
TAKE_PROFIT_2_PERCENT = 10.0      # 上涨10%全部卖出
```

**建议配置（保守型）：**
```python
MAX_POSITION_PERCENT = 5.0
STOP_LOSS_PERCENT = 2.0
TAKE_PROFIT_1_PERCENT = 3.0
```

**建议配置（激进型）：**
```python
MAX_POSITION_PERCENT = 15.0
STOP_LOSS_PERCENT = 5.0
TAKE_PROFIT_1_PERCENT = 8.0
```

## 📊 信号评分机制

系统通过以下因素计算信号评分（0-1）：

### 评分因素

1. **时间接近度** (40% 权重)
   - 两个信号时间越接近，评分越高
   - 同时出现 > 时间差小 > 时间差大

2. **FOMO 强度** (30% 权重)
   - Type 112 (FOMO加剧) = 1.0
   - Type 113 (FOMO) = 0.8

3. **信号新鲜度** (30% 权重)
   - 信号越新越好
   - 1小时内 = 高分，超过1小时衰减

### 示例

```
场景1: BTC 在1分钟内先后出现 FOMO + Alpha
- 时间接近度: 0.99 (1分钟差距)
- FOMO强度: 0.80 (Type 113)
- 新鲜度: 1.00 (刚发生)
→ 总评分: 0.92 ✅ 高质量信号

场景2: ETH 在4分钟内出现 Alpha + FOMO加剧
- 时间接近度: 0.20 (4分钟差距，接近窗口边缘)
- FOMO强度: 1.00 (Type 112)
- 新鲜度: 1.00
→ 总评分: 0.68 ✅ 仍可交易

场景3: SOL 在30分钟前出现 FOMO，现在出现 Alpha
- 时间接近度: 0.00 (超出时间窗口)
→ 不匹配 ❌
```

## 🛡️ 风险管理详解

### 1. 仓位控制

**单币种限制**
- 防止单一标的风险过大
- 默认每个币种最多占总资金10%

**总仓位限制**
- 防止过度杠杆
- 默认所有持仓合计不超过总资金50%
- 保留至少50%现金应对市场波动

### 2. 止损止盈策略

系统采用**分批止盈**策略：

```
入场价格: $100
├─ 止损: $97 (-3%)
├─ 第一目标: $105 (+5%) → 卖出50%仓位
└─ 第二目标: $110 (+10%) → 卖出剩余50%
```

**优势：**
- 保护部分利润的同时保留上涨空间
- 降低"卖飞"的心理压力
- 提高资金周转率

### 3. 交易限制

**每日交易次数限制**
- 防止过度交易（过度交易是亏损的主要原因）
- 强制筛选最优信号

**每日亏损限制**
- 触发后自动停止当日所有交易
- 防止情绪化报复性交易
- 保护本金

### 4. 实时监控

系统持续监控：
- 持仓盈亏
- 止损止盈触发
- 账户余额变化
- 风险指标

## 🔧 高级功能

### 自定义信号处理

如果需要从外部数据源接入信号：

```python
from binance_trader.main import AutoTradingSystem

system = AutoTradingSystem()

# 手动添加信号
system.process_signal(
    message_type=113,  # FOMO
    message_id="custom_001",
    symbol="BTC",
    data={}
)

system.process_signal(
    message_type=110,  # Alpha
    message_id="custom_002",
    symbol="BTC",
    data={}
)
# 如果在时间窗口内，会自动触发交易
```

### 监控持仓

```python
# 获取系统状态
status = system.risk_manager.get_status()
print(f"持仓数量: {status['position_count']}")
print(f"未实现盈亏: {status['total_unrealized_pnl']:.2f} USDT")
print(f"今日交易: {status['daily_trades']}")
print(f"今日盈亏: {status['daily_pnl']:.2f} USDT")
```

### 手动风控干预

```python
# 紧急停止所有交易
system.risk_manager.halt_trading("Manual halt")

# 恢复交易
system.risk_manager.resume_trading()

# 取消某个标的的所有订单
system.trader.cancel_all_orders("BTCUSDT")
```

## ⚠️ 风险提示

### 1. 市场风险

- 加密货币市场极度波动
- 过去表现不代表未来收益
- 可能面临本金损失

### 2. 技术风险

- API 连接中断
- 订单执行延迟
- 滑点影响实际价格

### 3. 策略风险

- 信号可能失效
- 市场环境变化
- 黑天鹅事件

### 建议

1. **从测试网开始** - 完全熟悉系统后再用真钱
2. **小额测试** - 先用小额资金验证策略
3. **持续监控** - 不要完全无人值守
4. **设置警报** - 配置 Telegram 通知
5. **定期回顾** - 每周检查交易记录和策略表现

## 📈 性能优化建议

### 1. 参数优化

建议进行回测和纸面交易，优化以下参数：
- 时间窗口大小
- 信号评分阈值
- 止损止盈比例

### 2. 信号质量改进

可以增加更多过滤条件：
- 成交量确认
- 技术指标辅助（RSI, MACD）
- 市场大盘状态判断

### 3. 执行优化

- 使用限价单替代市价单（减少滑点）
- 分批建仓（降低风险）
- 动态调整止损位（trailing stop）

## 🔍 故障排查

### 问题: API 连接失败

```
检查清单:
☐ API Key 和 Secret 是否正确
☐ 是否启用了 Spot Trading 权限
☐ IP 白名单是否正确（如果设置了）
☐ 网络连接是否正常
☐ 测试网模式配置是否匹配
```

### 问题: 订单被拒绝

```
可能原因:
- 余额不足
- 数量精度不符合交易对要求
- 价格超出允许范围
- 触发风控限制（仓位/交易次数）

解决方法:
检查日志中的具体错误信息
```

### 问题: 信号不匹配

```
检查:
- 时间窗口是否过小
- 信号评分阈值是否过高
- 信号类型配置是否正确
- 运行模式3测试聚合功能
```

## 📝 开发计划

### v1.1 计划功能

- [ ] Telegram 实时通知
- [ ] Web 仪表板
- [ ] 回测框架
- [ ] 更多技术指标集成
- [ ] 机器学习信号评分

### v1.2 计划功能

- [ ] 多交易所支持
- [ ] 网格交易策略
- [ ] 动态止损（trailing stop）
- [ ] 仓位动态调整

## 📚 相关资源

- [Binance API 文档](https://binance-docs.github.io/apidocs/spot/en/)
- [python-binance 库](https://github.com/sammchardy/python-binance)
- [ValueScan 信号监控](../signal_monitor/README.md)

## 📄 许可

本项目仅供学习和研究使用。使用本系统进行实际交易的风险由使用者自行承担。

---

**祝交易顺利！记住：风险管理永远是第一位的。** 🚀
