# Binance 合约自动化交易系统

基于 ValueScan 信号聚合的智能合约交易系统（带杠杆、移动止损、分批止盈）

## ⚠️ 重要风险提示

**合约交易使用杠杆，风险极高！**

- 💰 **高杠杆 = 高收益 + 高风险**
- 🔥 **可能面临爆仓（强制平仓）**
- 📉 **亏损可能超过本金**
- ⚡ **市场波动剧烈，需时刻监控**

**请务必：**
1. ✅ 先在测试网充分测试
2. ✅ 从低杠杆开始（建议≤5倍）
3. ✅ 只用可承受损失的资金
4. ✅ 设置严格的止损
5. ✅ 持续监控持仓

---

## 🚀 核心特性

### 1. 合约交易功能

- **杠杆交易**: 1-125倍杠杆（建议≤20倍）
- **保证金模式**: 逐仓/全仓可选（推荐逐仓）
- **双向交易**: 做多/做空（当前版本仅支持做多）
- **快速开平仓**: 市价单立即成交

### 2. 智能止损止盈

#### 固定止损
- 开仓后立即设置止损单
- 防止大幅亏损
- 自动触发平仓

#### 移动止损 (Trailing Stop)
```
盈利 2% → 激活移动止损
从最高点回撤 1.5% → 触发平仓

示例：
Entry: $100
Price: $102 → 盈利2%，移动止损激活
Highest: $105
Trailing Stop: $105 × (1 - 1.5%) = $103.43
Current: $103.40 → 触发平仓，锁定~3.4%利润
```

#### 分批止盈 (Pyramiding Exit)
```
金字塔式平仓策略：
- 盈利 3% → 平仓 30%（锁定部分利润）
- 盈利 5% → 再平 30%（累计平60%）
- 盈利 8% → 全部平仓（完成交易）

优势：
✅ 降低风险
✅ 锁定利润
✅ 保留上涨空间
```

### 3. 风险管理

#### 仓位控制
- 单币种最多 5% 本金
- 总仓位不超过 30% 本金
- 考虑杠杆后的实际风险

#### 交易限制
- 每日最多 15 笔交易
- 每日亏损 5% 自动停止
- 单笔交易上限保护

#### 强平风险监控
- 实时监控保证金率
- 低于 30% 时告警
- 低于 20% 强制平仓

### 4. 紧急安全机制

```bash
# 紧急停止交易
touch STOP_TRADING

# 恢复交易
rm STOP_TRADING
```

---

## 📖 快速开始

### 1. 安装依赖

```bash
pip install python-binance
```

### 2. 获取 API Key

**测试网（强烈推荐先用）**:
1. 访问 https://testnet.binancefuture.com/
2. 注册并获取测试 API Key
3. 启用 "Enable Futures" 权限

**生产环境**:
1. 访问 https://www.binance.com/en/my/settings/api-management
2. 创建 API Key
3. 启用 "Enable Futures" 权限
4. **必须设置 IP 白名单**

### 3. 配置系统

```bash
cd binance_trader
cp config.example.py config.py
```

编辑 `config.py`，关键配置：

```python
# API 配置
BINANCE_API_KEY = "your_api_key"
BINANCE_API_SECRET = "your_api_secret"
USE_TESTNET = True  # ⚠️ 先用测试网

# 合约配置
LEVERAGE = 10  # 杠杆倍数（建议≤10）
MARGIN_TYPE = "ISOLATED"  # 逐仓模式（推荐）

# 仓位配置
MAX_POSITION_PERCENT = 5.0  # 单币种5%本金
MAX_TOTAL_POSITION_PERCENT = 30.0  # 总仓位30%本金

# 止损止盈
STOP_LOSS_PERCENT = 2.0  # 止损2%
TAKE_PROFIT_1_PERCENT = 3.0  # 第一目标3%
TAKE_PROFIT_2_PERCENT = 6.0  # 第二目标6%

# 移动止损
ENABLE_TRAILING_STOP = True
TRAILING_STOP_ACTIVATION = 2.0  # 盈利2%启动
TRAILING_STOP_CALLBACK = 1.5  # 回撤1.5%触发

# 分批止盈
ENABLE_PYRAMIDING_EXIT = True
PYRAMIDING_EXIT_LEVELS = [
    (3.0, 0.3),  # 盈利3% → 平30%
    (5.0, 0.3),  # 盈利5% → 平30%
    (8.0, 1.0),  # 盈利8% → 全平
]

# 自动交易开关
AUTO_TRADING_ENABLED = False  # 先观察，确认后再开启
```

### 4. 运行系统

```bash
python futures_main.py
```

---

## ⚙️ 配置详解

### 杠杆配置

```python
LEVERAGE = 10  # 杠杆倍数
```

**杠杆对比**:

| 杠杆 | 100 USDT本金能开的仓位 | 涨1%收益 | 跌1%亏损 | 强平距离 |
|-----|---------------------|---------|---------|---------|
| 1x  | 100 USDT | 1 USDT | 1 USDT | -100% |
| 5x  | 500 USDT | 5 USDT | 5 USDT | -20% |
| 10x | 1000 USDT | 10 USDT | 10 USDT | -10% |
| 20x | 2000 USDT | 20 USDT | 20 USDT | -5% |

**建议**:
- 新手: 1-3倍
- 中级: 5-10倍
- 高级: 10-20倍
- 不建议超过20倍

### 保证金模式

```python
MARGIN_TYPE = "ISOLATED"  # 或 "CROSSED"
```

**逐仓 (ISOLATED) - 推荐**:
- ✅ 风险隔离：每个仓位独立
- ✅ 爆仓只影响该仓位
- ✅ 更安全

**全仓 (CROSSED)**:
- ⚠️ 所有仓位共享保证金
- ⚠️ 一个爆仓可能影响所有
- ⚠️ 风险较高

### 移动止损调优

```python
# 保守策略（早锁定利润）
TRAILING_STOP_ACTIVATION = 1.5  # 盈利1.5%启动
TRAILING_STOP_CALLBACK = 1.0  # 回撤1%触发

# 激进策略（追求更高利润）
TRAILING_STOP_ACTIVATION = 3.0  # 盈利3%启动
TRAILING_STOP_CALLBACK = 2.0  # 回撤2%触发
```

### 分批止盈调优

```python
# 保守策略（快速止盈）
PYRAMIDING_EXIT_LEVELS = [
    (2.0, 0.5),  # 盈利2% → 平50%
    (4.0, 1.0),  # 盈利4% → 全平
]

# 激进策略（追求大利润）
PYRAMIDING_EXIT_LEVELS = [
    (5.0, 0.3),   # 盈利5% → 平30%
    (10.0, 0.3),  # 盈利10% → 平30%
    (15.0, 1.0),  # 盈利15% → 全平
]
```

---

## 🎯 交易流程

### 完整交易周期

```
1. 信号接收
   ↓
2. 信号聚合 (FOMO + Alpha)
   ↓
3. 风险检查
   ├─ 仓位限制 ✓
   ├─ 交易次数 ✓
   └─ 日亏损额 ✓
   ↓
4. 设置杠杆和保证金模式
   ↓
5. 市价开多仓
   ↓
6. 立即设置止损单
   ↓
7. 持仓监控
   ├─ 移动止损跟踪
   ├─ 分批止盈检查
   └─ 强平风险监控
   ↓
8. 触发条件 → 平仓
   ├─ 止损触发
   ├─ 移动止损触发
   ├─ 分批止盈触发
   └─ 手动平仓
```

### 开仓示例

```
接收信号: BTC FOMO + Alpha
当前价格: $50,000
账户余额: 10,000 USDT
配置杠杆: 10x
单币仓位: 5% = 500 USDT本金

计算:
仓位价值 = 500 × 10 = 5,000 USDT
合约数量 = 5,000 / 50,000 = 0.1 BTC

止损价: 50,000 × (1 - 2%) = $49,000
止盈1: 50,000 × (1 + 3%) = $51,500 (平30%)
止盈2: 50,000 × (1 + 6%) = $53,000 (全平)

移动止损: 盈利2%后启动，回撤1.5%触发
```

---

## 📊 监控和管理

### 实时监控

系统自动监控：
- 🔍 持仓盈亏
- 📈 移动止损状态
- 🎯 分批止盈进度
- ⚠️ 强平风险
- 💰 账户余额

### 日志查看

```bash
# 实时日志
tail -f logs/binance_futures_trader.log

# 查找错误
grep ERROR logs/binance_futures_trader.log
```

### 紧急操作

```bash
# 紧急停止所有交易
touch STOP_TRADING

# 手动平仓（进入Python）
from binance_trader.futures_main import FuturesAutoTradingSystem
system = FuturesAutoTradingSystem()

# 平掉所有持仓
for symbol in system.trader.positions.keys():
    system.trader.close_position(symbol, "Manual close")
```

---

## 🔧 故障排查

### API 连接失败

```
检查清单:
☐ API Key/Secret 是否正确
☐ 是否启用 Futures 权限
☐ IP 白名单是否正确
☐ 测试网模式是否匹配
```

### 订单被拒绝

**可能原因**:
- 余额不足
- 杠杆未设置
- 保证金模式未设置
- 数量精度错误
- 触发风控限制

### 移动止损不生效

**检查**:
- `ENABLE_TRAILING_STOP = True`
- 盈利是否达到激活阈值
- 更新间隔是否合理
- 查看日志确认激活

---

## 💡 最佳实践

### 新手起步

**第1周: 测试和学习**
```python
USE_TESTNET = True
LEVERAGE = 3  # 低杠杆
MAX_POSITION_PERCENT = 3.0  # 小仓位
AUTO_TRADING_ENABLED = False  # 观察模式
```

**第2周: 小额实盘**
```python
USE_TESTNET = False
LEVERAGE = 5
MAX_POSITION_PERCENT = 5.0
账户投入: 100-500 USDT（可承受损失的金额）
```

**第3周+: 正常运行**
- 根据表现调整参数
- 持续监控和优化
- 记录交易日志

### 参数优化建议

**保守配置**（推荐新手）:
```python
LEVERAGE = 5
MAX_POSITION_PERCENT = 3.0
STOP_LOSS_PERCENT = 1.5
TRAILING_STOP_ACTIVATION = 1.5
TRAILING_STOP_CALLBACK = 1.0
```

**平衡配置**（推荐）:
```python
LEVERAGE = 10
MAX_POSITION_PERCENT = 5.0
STOP_LOSS_PERCENT = 2.0
TRAILING_STOP_ACTIVATION = 2.0
TRAILING_STOP_CALLBACK = 1.5
```

**激进配置**（高风险）:
```python
LEVERAGE = 15
MAX_POSITION_PERCENT = 8.0
STOP_LOSS_PERCENT = 3.0
TRAILING_STOP_ACTIVATION = 3.0
TRAILING_STOP_CALLBACK = 2.0
```

---

## 📈 性能优化

### 降低延迟

```python
# 启用 WebSocket（实时价格推送）
ENABLE_WEBSOCKET = True

# 缩短监控间隔
POSITION_MONITOR_INTERVAL = 5  # 5秒
```

### 提高成功率

```python
# 提高信号质量阈值
MIN_SIGNAL_SCORE = 0.75

# 缩短时间窗口（更严格匹配）
SIGNAL_TIME_WINDOW = 180  # 3分钟
```

---

## ⚠️ 风险管理检查清单

交易前必须确认：

- [ ] ✅ 已在测试网充分测试
- [ ] ✅ 理解杠杆风险
- [ ] ✅ 设置了止损
- [ ] ✅ 仓位控制合理
- [ ] ✅ 准备好监控持仓
- [ ] ✅ 只用可承受损失的资金
- [ ] ✅ 设置了紧急停止机制
- [ ] ✅ 了解强平机制
- [ ] ✅ 配置了 IP 白名单
- [ ] ✅ API Key 权限最小化

---

## 📚 相关文档

- [配置说明](config.example.py)
- [风险管理](risk_manager.py)
- [移动止损](trailing_stop.py)
- [现货交易版本](README.md)

---

## 🚨 免责声明

**本系统仅供学习和研究使用。**

- ⚠️ 合约交易风险极高
- ⚠️ 可能导致本金全部损失
- ⚠️ 过去表现不代表未来
- ⚠️ 作者不承担任何交易损失

**请务必在充分了解风险的前提下使用本系统。**

---

**祝交易顺利！记住：活下来比赚钱更重要。** 🚀

**最后更新**: 2025-10-13
