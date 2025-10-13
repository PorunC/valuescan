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
python main.py

# Choose mode:
# 1 - Integrated with signal monitor (recommended)
# 2 - Standalone mode (manual signal input)
# 3 - Test signal aggregation
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

**Message Type System**:
- Type 100: AI tracking alerts with multiple `predictType` variants (2, 4, 5, 7, 8, 16, 17, 19, 24, 28-31)
- Type 108: Fund movements
- Type 109: Listing/delisting announcements
- Type 110: Alpha opportunities (BUY signal when combined with FOMO)
- Type 111: Capital flight
- Type 112: FOMO intensification (RISK signal - should trigger take-profit, NOT buy)
- Type 113: FOMO alerts (BUY signal when combined with Alpha)
- Type 114: Abnormal fund activity

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

3. **Trader Executor** ([trader.py](binance_trader/trader.py))
   - Executes trades on Binance (supports both testnet and production)
   - Implements split take-profit strategy:
     - Entry → Stop-loss at -3%
     - Take-profit 1 at +5% (50% position)
     - Take-profit 2 at +10% (remaining 50%)
   - Monitors positions for stop-loss/take-profit triggers
   - Updates risk manager with balances and positions

4. **Futures Trader** ([futures_trader.py](binance_trader/futures_trader.py)) **[New Feature]**
   - Supports contract/futures trading on Binance Futures
   - Configurable leverage (1-125x, recommended ≤20x)
   - Margin mode: ISOLATED (recommended) or CROSSED
   - Advanced features:
     - **Trailing Stop**: Automatically follows price with dynamic stop-loss
     - **Pyramiding Exit**: Multi-level take-profit (e.g., 30% at +3%, 30% at +5%, 40% at +8%)
   - More conservative defaults for leveraged trading
   - Real-time margin ratio monitoring with liquidation warnings

5. **Main Controller** ([main.py](binance_trader/main.py))
   - Three running modes:
     - Mode 1: Integrated with signal monitor (auto-capture signals)
     - Mode 2: Standalone (manual signal input via API)
     - Mode 3: Test signal aggregation logic
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

### Trading Modes: Spot vs Futures

**Spot Trading** ([trader.py](binance_trader/trader.py)):
- Direct asset ownership (no leverage)
- Lower risk, suitable for beginners
- Split take-profit: 50% at +5%, 50% at +10%
- Fixed stop-loss at -3%

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
   - Enable only required permissions (Spot Trading or Futures, NOT Withdrawal)
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

**Integrated Mode** (binance_trader Mode 1):
- Signal monitor runs within trader process
- Signals automatically feed into aggregator
- Single process, unified logging
- **Note**: Currently requires callback mechanism implementation in signal_monitor

**Separate Processes** (Manual integration):
- Run signal monitor independently: `cd signal_monitor && python start_with_chrome.py`
- Run trader in standalone mode: `cd binance_trader && python main.py` (choose Mode 2)
- Manually bridge signals via custom integration code
- Better isolation, independent restarts

### Deployment Best Practices

**Development Workflow**:
1. Windows/macOS with headed mode for signal monitor (first login)
2. Test signal aggregation: `python main.py` → Mode 3
3. Run with AUTO_TRADING_ENABLED = False (observation mode)
4. Validate on testnet with small trades
5. Transfer `chrome-debug-profile` to Linux if deploying there

**Production Deployment** (Linux):
- Signal monitor: Headless mode mandatory (HEADLESS_MODE = True)
- Binance trader: Start with testnet, small capital
- Use systemd for process management (see README.md "Linux 服务器部署")
- Monitor logs regularly
- Set up Telegram alerts for trading events

### Message Processing Order

Messages are reversed before sending to Telegram (`reversed(new_messages)`) so newest alerts appear first in the chat.

### Logging

- Signal monitor: Comprehensive logging via [logger.py](signal_monitor/logger.py) with file rotation (10MB max, 5 backups)
- Binance trader: Logging configured in [main.py](binance_trader/main.py), outputs to `logs/binance_futures_trader.log`
- Both modules support configurable log levels (DEBUG, INFO, WARNING, ERROR)

### API Monitoring Mechanics

Uses DrissionPage's `page.listen.start(API_PATH)` to intercept network requests. The listener yields packets indefinitely in `page.listen.steps()`. This is non-blocking and captures all matching API responses.

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
