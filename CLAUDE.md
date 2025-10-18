# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ValueScan is a complete cryptocurrency trading solution consisting of two integrated modules:

1. **Signal Monitor** (`signal_monitor/`) - Monitors valuescan.io API and forwards alerts to Telegram
2. **Binance Trader** (`binance_trader/`) - Automated trading based on signal aggregation (confluence strategy)

The signal monitor uses browser automation (DrissionPage) to intercept API calls and supports both headed (visible browser) and headless (background) modes.

## Common Commands

### Signal Monitor Module
```bash
# Navigate to signal monitor
cd signal_monitor

# Install dependencies
pip install -r ../requirements.txt

# Create config from template
cp config.example.py config.py

# First-time setup (must run in headed mode to log in)
python start_with_chrome.py  # with HEADLESS_MODE = False in config.py

# Run the monitor (mode controlled by config.py)
python start_with_chrome.py

# Kill all Chrome processes
python kill_chrome.py

# Test Telegram functionality
python test_telegram.py

# Database management
python db_manager.py
```

### Binance Trader Module
```bash
# Navigate to trader
cd binance_trader

# Install dependencies (includes python-binance)
pip install -r requirements.txt

# Create config from template
cp config.example.py config.py

# Run the trading system
python futures_main.py

# Choose mode:
# 1 - Standalone mode (manual signal input)
# 2 - Test signal aggregation
```

### Full System Deployment
```bash
# Install all dependencies
pip install -r requirements.txt
cd binance_trader && pip install -r requirements.txt

# Configure both modules
cp signal_monitor/config.example.py signal_monitor/config.py
cp binance_trader/config.example.py binance_trader/config.py

# Edit both config files with your credentials
```

### Integrated System via IPC Bridge
```bash
# Terminal 1: Start the trading system IPC bridge
python valuescan_futures_bridge.py
# This starts a TCP server on 127.0.0.1:8765 listening for signals

# Terminal 2: Start the signal monitor with IPC forwarding enabled
cd signal_monitor
# Edit config.py: set ENABLE_IPC_FORWARDING = True
python start_with_chrome.py

# Now signals flow automatically: Signal Monitor → IPC Bridge → Binance Trader
```

### Testing Commands
```bash
# Test signal aggregation logic
cd binance_trader
python futures_main.py  # Choose option 2

# Test trader with manual signals
python test_trader.py

# Test specific predict types
python test_predictType3.py
python test_all_predict_types.py
```

## Architecture

The project follows a modular two-tier architecture:

```
ValueScan.io API → Signal Monitor → Telegram Notifications
                        ↓
                  Signal Aggregator → Risk Manager → Binance Trader → Exchange
```

### Module 1: Signal Monitor (`signal_monitor/`)

**Purpose**: Capture and forward trading signals from ValueScan.io

**Key Components**:

1. **Browser Automation Layer** ([signal_monitor/api_monitor.py](signal_monitor/api_monitor.py))
   - Uses DrissionPage to control Chrome/Chromium
   - Intercepts API requests to `api/account/message/getWarnMessage`
   - Cross-platform Chrome detection (Windows/Linux/macOS)
   - Two operational modes:
     - **Headed mode**: Connects to existing debug Chrome (port 9222) - required for first login
     - **Headless mode**: Launches new Chrome instance automatically - for 24/7 operation

2. **Message Processing Pipeline**
   - [api_monitor.py](signal_monitor/api_monitor.py): Captures API responses
   - [message_handler.py](signal_monitor/message_handler.py): Parses and processes messages
   - [telegram.py](signal_monitor/telegram.py): Formats and sends to Telegram
   - [database.py](signal_monitor/database.py): Deduplication via SQLite

3. **Process Management** ([kill_chrome.py](signal_monitor/kill_chrome.py))
   - Cross-platform Chrome process management
   - Linux/macOS: Uses `pgrep`/`pkill` with precise regex `(google-chrome|chromium-browser|chromium).*--` to avoid killing Python processes
   - Windows: Uses `taskkill`
   - Critical for headless mode to prevent user data directory conflicts

4. **Data Persistence** ([database.py](signal_monitor/database.py))
   - SQLite database (`valuescan.db`)
   - Tracks processed message IDs to prevent duplicate Telegram notifications
   - Singleton pattern via `get_database()`

**Message Type System** (see [message_types.py](signal_monitor/message_types.py) for complete mappings):
- Type 100: AI tracking alerts with `predictType` variants:
  - 2: Main force fleeing (risk increase)
  - 3: Main force accumulating (bullish sentiment)
  - 4/7: Main force reducing (risk signal)
  - 5: AI tracking started (potential token)
  - 8: Trend reversal (downtrend weakening)
  - 16: Take-profit on rise (10%+ gain)
  - 17: Take-profit on pullback (15%+ pullback)
  - 19: Stop-loss on drop (15%+ loss)
  - 24: Price peak warning (potential top)
  - 28: Accelerating accumulation (opportunity)
  - 29: Accelerating distribution (risk)
  - 30/31: Principal protection levels (5-15% moves)
- Type 108: Fund movements (1=24H inflow, 2=Extended inflow, 3=Sustained inflow, 4=Suspected outflow, 5=Volume surge, 6/7=Take-profit signals)
- Type 109: Listing/delisting announcements
- Type 110: Alpha opportunities (BUY signal when combined with FOMO)
- Type 111: Capital flight
- Type 112: FOMO intensification (RISK signal - should trigger take-profit, NOT buy)
- Type 113: FOMO alerts (BUY signal when combined with Alpha)
- Type 114: Abnormal fund activity with price movement (take-profit signal)

**Forwarded to Trading System**: Only types 110, 112, 113 are forwarded via IPC as they are actionable trading signals.

Each type has custom Telegram formatting in [telegram.py](signal_monitor/telegram.py).

### Module 2: Binance Trader (`binance_trader/`)

**Purpose**: Execute automated trades based on signal confluence strategy

**Core Strategy**: Only trade when FOMO (Type 113) + Alpha (Type 110) signals appear within a time window (default 5 minutes) for the same symbol. Type 112 (FOMO intensification) is treated as a RISK signal that should trigger profit-taking, not new entries.

**Key Components**:

1. **Signal Aggregator** ([signal_aggregator.py](binance_trader/signal_aggregator.py))
   - Maintains time-windowed caches of FOMO, Alpha, and Risk signals
   - Matches signals for the same symbol within configurable time window (default 300s)
   - Calculates signal scores (0-1) based on:
     - Time proximity (40% weight): Closer signals = higher score
     - FOMO strength (30% weight): Type 112 > Type 113
     - Signal freshness (30% weight): Newer signals = higher score
   - Only outputs confluence signals with score ≥ MIN_SIGNAL_SCORE (default 0.6)
   - Tracks risk signals separately (Type 112) for profit-taking decisions

2. **Risk Manager** ([risk_manager.py](binance_trader/risk_manager.py))
   - Position sizing: Single asset ≤ 10% total capital, all positions ≤ 50%
   - Daily limits: Max trades (20), max loss (5%) with automatic halt
   - Calculates stop-loss and take-profit prices
   - Generates trade recommendations (BUY/SKIP) with detailed reasoning

3. **Futures Trader** ([futures_trader.py](binance_trader/futures_trader.py))
   - Supports contract/futures trading on Binance Futures
   - Configurable leverage (1-125x, recommended ≤20x)
   - Margin mode: ISOLATED (recommended) or CROSSED
   - Advanced features:
     - **Trailing Stop**: Automatically follows price with dynamic stop-loss
     - **Pyramiding Exit**: Multi-level take-profit (e.g., 30% at +3%, 30% at +5%, 40% at +8%)
   - More conservative defaults for leveraged trading
   - Real-time margin ratio monitoring with liquidation warnings

4. **Main Controller** ([futures_main.py](binance_trader/futures_main.py))
   - Two running modes:
     - Mode 1: Standalone (manual signal input / external integration)
     - Mode 2: Test signal aggregation logic
   - Periodic tasks: Balance updates, position monitoring
   - Logging and status reporting

### Cross-Platform Design

Signal monitor supports all Chrome-related operations across platforms via `platform.system()`:
- Chrome executable paths: Different for Windows/Linux/macOS
- Process management: `taskkill` vs `pgrep/pkill`
- Path separators and environment variables

**Critical**: Linux process killing uses regex pattern `(google-chrome|chromium-browser|chromium).*--` to match only browser executables, not Python scripts containing 'chrome' keywords.

## Key Development Patterns

### Signal Monitor: Headed vs Headless Mode

**Headed Mode** (HEADLESS_MODE = False in `signal_monitor/config.py`):
- User must manually start Chrome in debug mode (port 9222) OR script connects to existing Chrome
- Script connects to existing Chrome via `co.set_local_port(CHROME_DEBUG_PORT)`
- Required for first-time login to save cookies
- Uses `chrome-debug-profile` directory for persistent login state

**Headless Mode** (HEADLESS_MODE = True):
- Automatically kills existing Chrome processes to avoid conflicts
- Launches new Chrome with `co.headless(True)`
- Auto-opens valuescan.io website
- Shares `chrome-debug-profile` with headed mode (same login state)
- Designed for server deployment and 24/7 operation
- Displays Chrome process ID for monitoring

### Deduplication Strategy (Signal Monitor)

Three-layer deduplication prevents duplicate Telegram notifications:
1. **In-memory**: `seen_ids` set passed through `process_response_data()`
2. **Database**: SQLite check via `is_message_processed(message_id)`
3. **Post-send**: Only marks as processed after successful Telegram delivery

This ensures no message is sent twice, even across restarts.

### Signal Confluence Strategy (Binance Trader)

**Why it works**:
- Single signals may be noise; multiple independent signals = confirmation
- FOMO (Type 113) = market sentiment/emotion
- Alpha (Type 110) = fundamental value opportunity
- Both signals together within short time = high-probability setup
- Type 112 (FOMO intensification) = market overheating, RISK signal for profit-taking

**Implementation**:
```python
# Pseudocode
if (FOMO signal exists AND Alpha signal exists AND
    same symbol AND
    time_gap < 5 minutes AND
    signal_score > 0.6):
    execute_trade()
```

**Risk signal handling**:
- Type 112 signals are cached separately as "risk signals"
- When detected, should trigger profit-taking on existing positions
- Do NOT use Type 112 as a buy signal (common mistake)

### Trading Mode

**Futures Trading** ([futures_trader.py](binance_trader/futures_trader.py)):
- Contract trading with leverage (1-125x)
- Higher risk/reward potential
- Advanced features:
  - Trailing stop-loss (follows price up, locks in profits)
  - Pyramiding exit (3+ levels of take-profit)
  - Margin ratio monitoring
  - Liquidation warnings
- More conservative defaults (smaller position sizes, tighter stops)
- **Always start with testnet** (testnet.binancefuture.com)

## Important Implementation Notes

### Security

1. **Never commit config files** - Both `signal_monitor/config.py` and `binance_trader/config.py` contain sensitive tokens/API keys. Always use `.example.py` as template.

2. **Binance API security**:
   - Use testnet first (USE_TESTNET = True)
   - Enable only required permissions (Futures trading, NOT Withdrawal)
   - Set IP whitelist if possible
   - Rotate API keys periodically
   - Use separate keys for testnet and production

3. **Emergency stop**: Create a file named `STOP_TRADING` in binance_trader directory to halt all trading immediately (if ENABLE_EMERGENCY_STOP = True).

### Chrome User Data Directory

The `chrome-debug-profile` directory is critical for signal monitor:
- Stores login session across headed/headless modes
- Must be transferred when deploying from Windows to Linux
- Cannot be used by multiple Chrome instances simultaneously (causes 404 handshake errors)
- Headless mode automatically kills conflicting processes before starting

### Module Integration

**Three Integration Methods**:

1. **IPC Bridge (Recommended for Production)**:
   ```bash
   # Start IPC bridge server
   python valuescan_futures_bridge.py

   # In signal_monitor/config.py:
   ENABLE_IPC_FORWARDING = True
   IPC_HOST = "127.0.0.1"  # From ipc_config.py
   IPC_PORT = 8765         # From ipc_config.py

   # Start signal monitor
   cd signal_monitor && python start_with_chrome.py
   ```

   **How it works**:
   - [valuescan_futures_bridge.py](valuescan_futures_bridge.py): TCP server listening on `127.0.0.1:8765`
   - [ipc_client.py](signal_monitor/ipc_client.py): Forwards signals (types 110, 112, 113) as JSON lines
   - [ipc_config.py](ipc_config.py): Shared configuration (host, port, timeouts, retries)
   - Signal flow: `signal_monitor` → TCP socket → `SignalTCPServer` → `FuturesAutoTradingSystem.process_signal()`
   - Automatic symbol extraction from message title/content
   - Retry logic with configurable timeouts (default: 3 retries, 1.5s timeout)

2. **Standalone Mode**:
   ```bash
   cd binance_trader
   python futures_main.py  # Choose Mode 1
   # Manually input signals or integrate via custom bridge
   ```

3. **Test Mode** (signal aggregation testing):
   ```bash
   cd binance_trader
   python futures_main.py  # Choose Mode 2
   ```

### Deployment Best Practices

**Development Workflow**:
1. Windows/macOS with headed mode for signal monitor (first login)
2. Test signal aggregation: `python futures_main.py` → Mode 2
3. Run with AUTO_TRADING_ENABLED = False (observation mode)
4. Validate on testnet with small trades
5. Transfer `chrome-debug-profile` to Linux if deploying there

**Production Deployment** (Linux):
- Signal monitor: Headless mode mandatory (HEADLESS_MODE = True)
- IPC bridge: Run as a separate service (`python valuescan_futures_bridge.py`)
- Binance trader: Start with testnet, small capital
- Use systemd for process management (see README.md "Linux 服务器部署")
- Recommended setup: 3 systemd services (signal_monitor, ipc_bridge, binance_trader) or use the bridge which runs trader internally
- Monitor logs regularly
- Set up Telegram alerts for trading events

**Systemd Service Example for IPC Bridge**:
```ini
[Unit]
Description=ValueScan IPC Bridge
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/valuescan
ExecStart=/path/to/venv/bin/python valuescan_futures_bridge.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Message Processing Order

Messages are reversed before sending to Telegram (`reversed(new_messages)`) so newest alerts appear first in the chat.

### Logging

- Signal monitor: Comprehensive logging via [logger.py](signal_monitor/logger.py) with file rotation (10MB max, 5 backups)
- Binance trader: Logging configured in [futures_main.py](binance_trader/futures_main.py), outputs to `logs/binance_futures_trader.log`
- Both modules support configurable log levels (DEBUG, INFO, WARNING, ERROR)

### API Monitoring Mechanics

Uses DrissionPage's `page.listen.start(API_PATH)` to intercept network requests. The listener yields packets indefinitely in `page.listen.steps()`. This is non-blocking and captures all matching API responses.

### IPC Signal Format

When `ENABLE_IPC_FORWARDING = True`, signals are forwarded as JSON lines over TCP:

```json
{
  "message_type": 113,
  "message_id": "12345",
  "title": "$BTC FOMO Alert",
  "symbol_hint": "BTC",
  "created_time": "2024-10-13 12:34:56",
  "data": {
    "raw_message": { /* original API response */ },
    "content": { /* parsed content */ }
  }
}
```

**Symbol Extraction Hierarchy** (in [valuescan_futures_bridge.py](valuescan_futures_bridge.py)):
1. `symbol_hint` from IPC payload
2. `data.content.symbol`, `data.content.pair`, or `data.content.symbolName`
3. `data.raw_message.symbol`
4. First word of `data.raw_message.title`

**Symbol Normalization**:
- Strips `$` prefix (e.g., `$BTC` → `BTC`)
- Removes `/USDT` suffix if present
- Converts to uppercase
- Extracts base symbol from pairs (e.g., `BTC/USDT` → `BTC`)

### Position Sizing Formula

```python
single_asset_limit = total_balance × MAX_POSITION_PERCENT (default 10%)
actual_purchase = min(single_asset_limit, available_balance)
quantity = actual_purchase / current_price
adjusted_quantity = quantity × (0.5 + 0.5 × signal_score)
```

For futures with leverage:
```python
margin_required = position_value / leverage
actual_position_value = margin_required × leverage
```

## Configuration Priorities

When modifying the system, respect this priority order:
1. **Security** (never expose tokens/keys, use testnet first)
2. **Risk Management** (position limits, daily loss limits, stop-losses)
3. **Deduplication** (prevent spam notifications and duplicate trades)
4. **Cross-platform compatibility** (test on all target OSes)
5. **User experience** (clear logs, helpful error messages)

## Critical Signal Type Distinction

**BUY Signals** (open new positions):
- Type 113 (FOMO) + Type 110 (Alpha) within time window = BUY
- Both signals must be present for same symbol

**RISK Signals** (close positions, take profit):
- Type 112 (FOMO intensification) = Market overheating
- Should trigger profit-taking on existing positions
- Do NOT use as a buy signal

This distinction is critical for the trading strategy. Misinterpreting Type 112 as a buy signal will lead to poor entries at market tops.

## Common Issues and Solutions

### IPC Connection Problems

**Issue**: Signal monitor can't connect to IPC bridge
```
IPC 信号发送失败 (第 1 次尝试): Connection refused
```

**Solutions**:
1. Ensure IPC bridge is running: `python valuescan_futures_bridge.py`
2. Check port availability: `netstat -an | grep 8765` (Linux/macOS) or `netstat -an | findstr 8765` (Windows)
3. Verify firewall allows localhost connections on port 8765
4. Check `ipc_config.py` settings match in both modules

**Issue**: Signals not reaching trading system

**Debug steps**:
1. Check signal monitor logs for "📡 IPC 已转发信号" messages
2. Check IPC bridge logs for "➡️ 收到信号" messages
3. Verify `ENABLE_IPC_FORWARDING = True` in `signal_monitor/config.py`
4. Ensure message types are 110, 112, or 113 (other types are not forwarded)
5. Check symbol extraction succeeded (not None)

### Symbol Extraction Failures

**Issue**: Trading system skips signals due to missing symbol

**Debug**:
- Check IPC bridge logs for "无法解析标的符号" warnings
- Verify message has symbol in title, content, or raw data
- Check if symbol format is recognized (should be like `BTC`, `$BTC`, `BTC/USDT`)

**Fix**: Update symbol extraction logic in [valuescan_futures_bridge.py](valuescan_futures_bridge.py) `_extract_symbol()` function

### Chrome Process Conflicts

**Issue**: "Handshake status 404 Not Found" when starting signal monitor

**Cause**: Multiple Chrome instances trying to use same user data directory

**Solution**:
```bash
# Kill all Chrome processes
cd signal_monitor
python kill_chrome.py

# Or manually (Linux/macOS)
pkill -f "(google-chrome|chromium-browser|chromium).*--"

# Windows
taskkill /F /IM chrome.exe /T
```

### Testing Without Real Trading

**Safe testing workflow**:
```bash
# 1. Test signal aggregation only (no API calls)
cd binance_trader
python futures_main.py  # Choose Mode 2

# 2. Test with observation mode (connects to exchange but doesn't trade)
# In binance_trader/config.py:
AUTO_TRADING_ENABLED = False

# 3. Use testnet for real order testing
USE_TESTNET = True
BINANCE_FUTURES_TESTNET_URL = "https://testnet.binancefuture.com/fapi"
```

### Network Connection Issues

**Issue**: "Remote end closed connection without response" in maintenance loop

**Cause**: Binance API server temporarily drops connections (common during high load or network issues)

**Solution**: The system now has automatic retry logic:
- Network errors are logged as warnings (not errors)
- Previous data is retained when updates fail
- Maintenance loop tolerates up to 10 consecutive failures before stopping
- 5-second wait between retries to avoid error storms

**Expected behavior**:
```
2025-10-18 21:43:43 [WARNING] 更新持仓失败 (网络错误): Remote end closed...
2025-10-18 21:43:48 [WARNING] 维护循环发生异常 (第 1 次): ...
# System automatically retries after 5 seconds
2025-10-18 21:43:53 [INFO] 持仓更新成功
# Error counter resets to 0
```

**When to worry**:
- Only if you see "维护循环连续失败 10 次，停止运行"
- This indicates sustained network issues or API problems
- Check your internet connection and Binance API status
