# ValueScan 项目文件说明

## 📁 根目录文件

### 文档文件
- **README.md** - 项目主文档，包含完整的使用说明
- **ARCHITECTURE.md** - 系统架构详解，深入理解项目设计
- **QUICKSTART.md** - 5分钟快速入门指南（推荐首先阅读）
- **CLAUDE.md** - Claude Code 项目指引

### 配置文件
- **config.example.py** - 配置文件模板（用于信号监控模块）
- **config.py** - 你的个人配置（已保留）
- **requirements.txt** - 项目依赖列表

## 📦 模块目录

### signal_monitor/ - 信号监控模块
负责监听 valuescan.io API 并推送到 Telegram

**使用方法**:
```bash
cd signal_monitor
cp config.example.py config.py
# 编辑 config.py 填入 Telegram 配置
python start_with_chrome.py
```

**查看详细文档**: [signal_monitor/README.md](signal_monitor/README.md)

### binance_trader/ - 自动化交易模块
基于信号聚合的智能交易系统

**使用方法**:
```bash
cd binance_trader
pip install -r requirements.txt
cp config.example.py config.py
# 编辑 config.py 填入 Binance API 配置
python futures_main.py
```

**查看详细文档**: [binance_trader/README.md](binance_trader/README.md)

## 🚀 快速开始

### 新手推荐阅读顺序

1. **[QUICKSTART.md](QUICKSTART.md)** - 5分钟上手 ⭐
2. **[README.md](README.md)** - 完整功能说明
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 深入理解架构

### 老用户迁移说明

如果你之前使用的是旧版本（根目录直接运行 Python 文件），请注意：

**旧的使用方式** (已废弃):
```bash
python start_with_chrome.py  # 在根目录
```

**新的使用方式** (推荐):
```bash
cd signal_monitor
python start_with_chrome.py
```

你的 `config.py` 已经保留在根目录，但需要：
1. 复制到 `signal_monitor/config.py` 以继续使用信号监控
2. 如果使用交易模块，需要在 `binance_trader/` 创建新的配置

## 📝 配置文件位置

- **信号监控配置**: `signal_monitor/config.py`
- **交易系统配置**: `binance_trader/config.py`
- **根目录 config.py**: 可以删除或作为备份保留

## 🆘 需要帮助？

- 快速问题 → 查看 [QUICKSTART.md](QUICKSTART.md) 的 FAQ 部分
- 配置问题 → 查看对应模块的 `config.example.py`
- 架构问题 → 查看 [ARCHITECTURE.md](ARCHITECTURE.md)
- 报告 Bug → 提交 GitHub Issue

---

**更新日期**: 2025-10-13
**项目版本**: v1.0.0
