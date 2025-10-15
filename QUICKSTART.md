# 🚀 ValueScan 快速入门指南

## 5分钟上手

### 第一步：选择你的使用场景

#### 场景 1: 我只想接收交易信号通知 📱

**需求**: Telegram 账号

**步骤**:
```bash
# 1. 进入信号监控目录
cd signal_monitor

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置
cp config.example.py config.py
# 编辑 config.py，填入 Telegram Bot Token 和 Chat ID

# 4. 首次运行（需要登录）
# 设置 config.py 中 HEADLESS_MODE = False
python start_with_chrome.py
# 在打开的浏览器中登录 valuescan.io
# Ctrl+C 停止

# 5. 后台运行
# 设置 config.py 中 HEADLESS_MODE = True
python start_with_chrome.py
```

**完成！** 现在你会在 Telegram 收到所有交易信号。

---

#### 场景 2: 我想自动交易（基于信号） 🤖

**需求**:
- Binance 账号
- API Key（建议先用测试网）
- 一定的交易知识

**步骤**:
```bash
# 1. 先完成"场景1"的设置（可选，用于观察信号）

# 2. 进入交易模块
cd binance_trader

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置
cp config.example.py config.py
# 编辑 config.py：
# - 填入 Binance API Key 和 Secret
# - 设置 USE_TESTNET = True（强烈建议）
# - 设置 AUTO_TRADING_ENABLED = False（先观察）

# 5. 测试信号聚合
python futures_main.py
# 选择 2 - Test signal aggregation

# 6. 运行系统（观察模式）
python futures_main.py
# 选择 1 - Standalone mode
# 此时只会记录信号，不会实际下单

# 7. 启用自动交易（确认策略后）
# 编辑 config.py: AUTO_TRADING_ENABLED = True
python futures_main.py
# 选择 1 - Standalone mode
```

**完成！** 系统现在会在检测到高质量信号时自动交易。

---

## 常见问题速查

### Q1: 如何获取 Telegram Bot Token？

```
1. 在 Telegram 搜索 @BotFather
2. 发送 /newbot
3. 按提示创建机器人
4. 复制提供的 Token
```

### Q2: 如何获取 Telegram Chat ID？

```
1. 在 Telegram 搜索 @userinfobot
2. 发送任意消息
3. 复制返回的 ID
```

### Q3: 如何获取 Binance API Key？

**生产环境**:
1. 登录 Binance → 个人中心 → API 管理
2. 创建 API Key
3. 启用"合约交易 (Futures)"权限
4. **重要**: 设置 IP 白名单

**测试网（推荐）**:
1. 访问 https://testnet.binancefuture.com/
2. 注册或登录测试网账户
3. 创建 Futures API Key 与 Secret
4. 在测试网页面领取 USDT（Futures Testnet Faucet），并记下 REST 入口 `https://testnet.binancefuture.com/fapi`

### Q4: 第一次运行遇到 "未登录" 错误？

```bash
# 必须先用有头模式登录一次
cd signal_monitor
# 编辑 config.py: HEADLESS_MODE = False
python start_with_chrome.py
# 在浏览器中手动登录
# Ctrl+C 停止
# 现在可以使用无头模式了
```

### Q5: 如何知道我的策略是否盈利？

```python
# 查看风险管理器状态
from binance_trader.futures_main import FuturesAutoTradingSystem

system = FuturesAutoTradingSystem()
status = system.risk_manager.get_status()

print(f"今日盈亏: {status['daily_pnl']:.2f} USDT")
print(f"未实现盈亏: {status['total_unrealized_pnl']:.2f} USDT")
```

### Q6: 信号太多/太少怎么办？

**太多** → 提高 `MIN_SIGNAL_SCORE` (默认 0.6)
```python
# config.py
MIN_SIGNAL_SCORE = 0.75  # 只交易高评分信号
```

**太少** → 扩大 `SIGNAL_TIME_WINDOW` (默认 300秒)
```python
# config.py
SIGNAL_TIME_WINDOW = 600  # 扩大到10分钟
```

### Q7: 如何修改止损止盈比例？

```python
# binance_trader/config.py
STOP_LOSS_PERCENT = 3.0      # 止损 3%
TAKE_PROFIT_1_PERCENT = 5.0  # 第一目标 5%
TAKE_PROFIT_2_PERCENT = 10.0 # 第二目标 10%

# 保守策略示例
STOP_LOSS_PERCENT = 2.0
TAKE_PROFIT_1_PERCENT = 3.0
TAKE_PROFIT_2_PERCENT = 6.0

# 激进策略示例
STOP_LOSS_PERCENT = 5.0
TAKE_PROFIT_1_PERCENT = 8.0
TAKE_PROFIT_2_PERCENT = 15.0
```

### Q8: 如何在服务器上后台运行？

```bash
# 方式 1: nohup
nohup python start_with_chrome.py > output.log 2>&1 &

# 方式 2: screen
screen -S valuescan
python start_with_chrome.py
# Ctrl+A+D 退出（保持运行）
# screen -r valuescan 重新连接

# 方式 3: systemd (推荐)
# 参考 README.md 中的 systemd 配置
```

### Q9: 测试网和生产环境有什么区别？

| 特性 | 测试网 | 生产环境 |
|------|--------|---------|
| 资金 | 免费测试币 | 真实资金 |
| API | testnet.binancefuture.com/fapi | fapi.binance.com |
| 风险 | ✅ 零风险 | ⚠️ 真实风险 |
| 数据 | 模拟行情 | 真实行情 |
| 建议 | 先在这里测试 | 验证后再用 |

### Q10: 出现错误如何调试？

```python
# 1. 查看日志
tail -f logs/binance_futures_trader.log

# 2. 启用详细日志
# config.py
LOG_LEVEL = "DEBUG"

# 3. 测试各个组件
# 测试信号聚合
python futures_main.py → 选择 2

# 测试 Futures API 连接
python -c "from binance.client import Client; c = Client('key', 'secret', testnet=True); c.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'; print(c.futures_ping())"

# 4. 查看系统状态
# 在 futures_main.py 运行时会定期打印状态
```

---

## 推荐的学习路径

### 第 1 周：观察和学习
- ✅ 运行信号监控，观察信号质量
- ✅ 阅读文档，理解策略原理
- ✅ 在测试网配置交易系统
- ✅ 观察模式运行，不实际交易

### 第 2 周：测试网验证
- ✅ 启用测试网自动交易
- ✅ 观察策略表现
- ✅ 调整参数优化
- ✅ 记录所有交易

### 第 3 周：小额实盘
- ✅ 切换到生产环境
- ✅ 使用小额资金（100-500 USDT）
- ✅ 验证实际执行效果
- ✅ 处理真实市场情况

### 第 4 周+：正式运行
- ✅ 增加到正常仓位
- ✅ 持续监控和优化
- ✅ 记录交易日志
- ✅ 定期回顾和改进

---

## 安全检查清单

在启用真实交易前，确保：

- [ ] ✅ 我已经在测试网充分测试
- [ ] ✅ 我理解策略的工作原理
- [ ] ✅ 我设置了合理的仓位限制
- [ ] ✅ 我配置了止损止盈
- [ ] ✅ 我设置了每日交易次数限制
- [ ] ✅ 我设置了每日亏损限制
- [ ] ✅ 我的 API Key 设置了 IP 白名单
- [ ] ✅ 我的 API Key 禁用了提现权限
- [ ] ✅ 我准备好接受可能的损失
- [ ] ✅ 我会定期检查系统状态

---

## 需要帮助？

### 查看文档
- 📖 [项目总览](README.md)
- 🏗️ [架构说明](ARCHITECTURE.md)
- 📡 [信号监控文档](signal_monitor/README.md)
- 🤖 [交易系统文档](binance_trader/README.md)

### 常见问题
- 配置问题 → 查看 config.example.py 注释
- API 错误 → 查看日志文件
- 策略问题 → 查看 ARCHITECTURE.md

### 报告问题
- GitHub Issues: https://github.com/PorunC/valuescan/issues

---

**祝交易顺利！记住：风险管理永远是第一位的。** 🚀

**最后更新**: 2025-10-13
