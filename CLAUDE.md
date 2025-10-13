# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ValueScan is a cryptocurrency alert monitoring tool that listens to valuescan.io API requests and automatically forwards alert messages to Telegram. It uses browser automation (DrissionPage) to intercept API calls and supports both headed (with visible browser) and headless (background) modes.

## Common Commands

### Development & Testing
```bash
# Install dependencies
pip install -r requirements.txt

# First-time setup (must run in headed mode to log in)
python start_with_chrome.py  # with HEADLESS_MODE = False in config.py

# Run the main program (mode controlled by config.py)
python start_with_chrome.py

# Run directly (connects to existing debug Chrome)
python valuescan.py

# Kill all Chrome processes
python kill_chrome.py

# Test Telegram functionality
python test_telegram.py

# Database management
python db_manager.py
```

### Configuration
```bash
# Create config from template
cp config.example.py config.py
# Then edit config.py with your Telegram credentials and settings
```

## Architecture

### Core Components

1. **Browser Automation Layer** ([api_monitor.py](api_monitor.py))
   - Uses DrissionPage to control Chrome/Chromium
   - Intercepts API requests to `api/account/message/getWarnMessage`
   - Supports cross-platform Chrome detection (Windows/Linux/macOS)
   - Two modes:
     - **Headed mode**: Connects to existing debug Chrome (port 9222)
     - **Headless mode**: Launches new Chrome instance automatically

2. **Message Processing Pipeline**
   - [api_monitor.py](api_monitor.py): Captures API responses
   - [message_handler.py](message_handler.py): Parses and processes messages
   - [telegram.py](telegram.py): Formats and sends to Telegram
   - [database.py](database.py): Deduplication via SQLite

3. **Process Management** ([kill_chrome.py](kill_chrome.py))
   - Cross-platform Chrome process management
   - Linux/macOS: Uses `pgrep`/`pkill` with precise regex to avoid killing Python processes
   - Windows: Uses `taskkill`
   - Critical for headless mode to prevent user data directory conflicts

4. **Data Persistence** ([database.py](database.py))
   - SQLite database (`valuescan.db`)
   - Tracks processed message IDs to prevent duplicate Telegram notifications
   - Singleton pattern via `get_database()`

### Message Type System

The system handles multiple alert types (defined in `config.py`):
- Type 100: AI tracking alerts with multiple `predictType` variants (2, 4, 5, 7, 8, 16, 17, 19, 24, 28-31)
- Type 108: Fund movements
- Type 109: Listing/delisting announcements
- Type 110: Alpha opportunities
- Type 111: Capital flight
- Type 112: FOMO intensification
- Type 113: FOMO alerts
- Type 114: Abnormal fund activity (includes profit-taking signals)

Each type has custom Telegram formatting in [telegram.py](telegram.py) with specific emojis and action recommendations.

### Cross-Platform Design

All Chrome-related operations detect the platform via `platform.system()` and adapt:
- Chrome executable paths: Different for Windows/Linux/macOS
- Process management: `taskkill` vs `pgrep/pkill`
- Path separators and environment variables

**Important**: Linux process killing uses regex pattern `(google-chrome|chromium-browser|chromium).*--` to match only browser executables, not Python scripts containing 'chrome' keywords.

## Key Development Patterns

### Headed vs Headless Mode

**Headed Mode** (HEADLESS_MODE = False):
- User must manually start Chrome in debug mode (port 9222)
- Script connects to existing Chrome via `co.set_local_port(CHROME_DEBUG_PORT)`
- Required for first-time login to save cookies
- Uses `chrome-debug-profile` directory for persistent login state

**Headless Mode** (HEADLESS_MODE = True):
- Automatically kills existing Chrome processes
- Launches new Chrome with `co.headless(True)`
- Auto-opens valuescan.io website
- Shares `chrome-debug-profile` with headed mode (same login state)
- Designed for server deployment and 24/7 operation

### Deduplication Strategy

Three-layer deduplication:
1. **In-memory**: `seen_ids` set passed through `process_response_data()`
2. **Database**: SQLite check via `is_message_processed(message_id)`
3. **Post-send**: Only marks as processed after successful Telegram delivery

This ensures no message is sent twice, even across restarts.

### Telegram Formatting

[telegram.py](telegram.py) uses HTML formatting with:
- Type-specific formatting functions: `_format_risk_alert()` for type 100, `_format_general_message()` for others
- Inline keyboard with "Visit ValueScan" button
- Different emojis and action recommendations based on `predictType` and `fundsMovementType`
- Special handling for profit-taking signals (predictType 16, 17, 19, 30, 31)

## Important Implementation Notes

1. **Never commit `config.py`** - It contains sensitive Telegram tokens. Always use `config.example.py` as template.

2. **Chrome user data directory** - The `chrome-debug-profile` directory is critical:
   - Stores login session across headed/headless modes
   - Must be transferred when deploying from Windows to Linux
   - Cannot be used by multiple Chrome instances simultaneously (causes 404 handshake errors)

3. **Linux deployment** - The project includes comprehensive Linux support:
   - Auto-detects Chrome/Chromium paths
   - Requires system libraries (listed in README)
   - Headless mode is mandatory for Linux servers without X11
   - See [README.md](README.md) sections "Linux 服务器部署" for systemd service setup

4. **Message processing order** - Messages are reversed before sending to Telegram (`reversed(new_messages)`) so newest alerts appear first.

5. **Logging** - Comprehensive logging via [logger.py](logger.py) with file rotation (10MB max, 5 backups).

6. **Process safety** - The headless mode startup sequence is:
   1. Kill all Chrome processes
   2. Wait 2 seconds
   3. Launch new Chrome with user data directory
   4. Display process ID for monitoring

7. **API monitoring** - Uses DrissionPage's `page.listen.start(API_PATH)` to intercept network requests. The listener yields packets indefinitely in `page.listen.steps()`.

## Configuration Priorities

When modifying the system, respect this priority order:
1. Security (never expose tokens)
2. Deduplication (prevent spam)
3. Cross-platform compatibility (test on all OSes)
4. User experience (clear logs, helpful error messages)
