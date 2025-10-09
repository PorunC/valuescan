# Binance 合约交易 - 快速参考

## 🎯 核心逻辑
同时收到 **Alpha + FOMO** 双信号 → 合约做多 (5x杠杆)

## ⚙️ 关键配置

```python
# config.py 关键参数

BINANCE_API_KEY = "your_key"           # 需要"期货交易"权限
BINANCE_API_SECRET = "your_secret"
BINANCE_TESTNET = True                 # True=测试网, False=正式网
BINANCE_TRADE_ENABLED = False          # True=自动交易, False=只记录
BINANCE_LEVERAGE = 5                   # 杠杆 1-125x（建议5-10x）
BINANCE_TRADE_AMOUNT_USDT = 20         # 每次开仓保证金（USDT）
BINANCE_SIGNAL_TIMEOUT_MINUTES = 30    # 信号有效时间（分钟）
```

## 📊 杠杆选择参考

| 杠杆 | 爆仓距离 | 适用人群 | 风险等级 |
|------|----------|----------|----------|
| 1x   | -100%    | 极保守   | ⭐ 极低  |
| 3x   | -33%     | 新手     | ⭐⭐ 低  |
| 5x   | -20%     | 一般     | ⭐⭐⭐ 中 |
| 10x  | -10%     | 有经验   | ⭐⭐⭐⭐ 高 |
| 20x  | -5%      | 高手     | ⭐⭐⭐⭐⭐ 极高 |

## 💰 资金示例

### 示例 1：保守配置
```
保证金: 20 USDT
杠杆: 3x
名义价值: 60 USDT
爆仓距离: -33%
```

### 示例 2：平衡配置（推荐）
```
保证金: 20 USDT
杠杆: 5x
名义价值: 100 USDT
爆仓距离: -20%
```

### 示例 3：激进配置
```
保证金: 50 USDT
杠杆: 10x
名义价值: 500 USDT
爆仓距离: -10%
```

## 🚀 使用步骤

### 1. 获取测试 API
访问：https://testnet.binancefuture.com/
- 注册/登录
- 创建 API Key
- 获取免费测试 USDT

### 2. 配置文件
```bash
# 复制配置模板
cp config.example.py config.py

# 编辑 config.py
# 填入 API Key 和 Secret
```

### 3. 测试
```bash
# 测试配置
python test_binance_trader.py

# 查看双信号逻辑
python test_binance_trader.py
```

### 4. 启动
```bash
# 启动监听（会自动处理双信号）
python start_with_chrome.py
```

## ⚠️ 安全检查清单

开始交易前，确保：

- [ ] 已在测试网充分测试
- [ ] 理解合约交易和爆仓机制
- [ ] API 只开启"期货交易"权限
- [ ] 杠杆设置合理（建议≤10x）
- [ ] 保证金金额可承受全损
- [ ] 设置了 IP 白名单
- [ ] 合约账户余额充足
- [ ] 了解如何手动止损/平仓

## 🔥 风险提示

### 爆仓示例
```
开仓价: $50,000
杠杆: 10x
保证金: 100 USDT
爆仓价: $45,000 (下跌10%)

如果 BTC 跌到 $45,000：
→ 仓位被强制平仓
→ 损失全部 100 USDT 保证金
```

### 建议
1. **新手**：1-3x 杠杆
2. **有经验**：5-10x 杠杆
3. **高手**：10-20x 杠杆
4. **不推荐**：>20x 杠杆

## 📱 监控要点

### 每天检查
- 持仓列表和数量
- 未实现盈亏
- 强制平仓价格
- 账户保证金率

### 及时平仓条件
- 连续亏损
- 市场剧烈波动
- 达到止损位
- 系统异常

## 🆘 紧急操作

### 停止交易
```python
# config.py
BINANCE_TRADE_ENABLED = False
```

### 平仓所有持仓
1. 登录 Binance 合约账户
2. 点击持仓列表
3. 点击"全部平仓"

### 禁用 API
1. 登录 Binance
2. API 管理
3. 删除或禁用 API Key

## 📚 更多信息

完整文档：`BINANCE_GUIDE.md`

测试脚本：`test_binance_trader.py`

日志文件：`valuescan.log`

---

**记住：合约有风险，交易需谨慎！** ⚠️
