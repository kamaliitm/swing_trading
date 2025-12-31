# Swing Trading Automation System

Automated swing trading system that uses Heiken Ashi candles to identify stocks with downward trend patterns that indicate potential reversal opportunities.

## Strategy Overview

The system identifies a 3-candle downward trend pattern (in chronological order) using Heiken Ashi candles:
- **Candle 1** (newest): Lowest point
- **Candle 2** (middle): Higher than Candle 1
- **Candle 3** (oldest): Highest point in the pattern

Buy signals are generated when the current price crosses above **Candle 3's high**, indicating a potential upward reversal.

## Project Structure

```
swing_trading/
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py          # Fetch stock data from yfinance
│   ├── heiken_ashi.py           # Calculate Heiken Ashi candles
│   ├── trend_detector.py        # Detect 3-candle trends
│   ├── pool_creation_job.py    # Pool creation job logic
│   └── finalization_job.py     # Finalization job logic
├── scripts/
│   ├── run_pool_creation.py    # Executable script for pool creation (cron entry)
│   └── run_finalization.py     # Executable script for finalization (cron entry)
├── data/
│   ├── pool.csv                 # Stocks with detected trends
│   └── final_stocks.csv         # Final buy signals
├── config/
│   └── stocks.py                # Nifty 500 stock list configuration
├── logs/                        # Log files (created automatically)
├── requirements.txt
├── crontab.example              # Example cron configuration
└── README.md
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd swing_trading
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure stock list:**
   - Edit `config/stocks.py` to add/update the Nifty 500 stock symbols
   - Update `LOOKBACK_DAYS` if needed (default: 30 days)

## Usage

### Manual Execution

You can run the jobs manually for testing:

**Pool Creation Job:**
```bash
source .venv/bin/activate  # Activate venv first
python scripts/run_pool_creation.py
```

**Finalization Job:**
```bash
source .venv/bin/activate  # Activate venv first
python scripts/run_finalization.py
```

### Automated Scheduling (Cron)

1. **Update crontab.example:**
   - Replace `/Users/kamalkambe/swameeyam/projects/swing_trading` with your actual project path
   - Replace `/opt/homebrew/opt/python@3.13/bin/python3.13` with your Python 3 executable path
   - Find your Python path: `which python3` or `python3 -c "import sys; print(sys.executable)"`

2. **Update crontab.example:**
   - Replace `/Users/kamalkambe/swameeyam/projects/swing_trading` with your actual project path
   - Replace the Python path with your venv Python path: `.venv/bin/python3`
   - Or use the full path: `/path/to/swing_trading/.venv/bin/python3`

3. **Add cron jobs:**
   ```bash
   # Edit crontab
   crontab -e
   
   # Add the lines from crontab.example (adjust paths as needed)
   ```

3. **Verify cron jobs:**
   ```bash
   # Quick check
   crontab -l
   
   # Or use the verification script (recommended)
   python scripts/verify_cron.py
   ```

**Job Schedule:**
- **Finalization Job**: 3:15 PM IST (weekdays only)
- **Pool Creation Job**: 4:30 PM IST (weekdays only)

Note: The scripts handle IST timezone conversion internally and skip non-trading days (weekends).

## How It Works

### Pool Creation Job (4:30 PM IST)

1. Scans all configured stocks (Nifty 500)
2. Fetches historical OHLC data (last 30 days by default)
3. Converts to Heiken Ashi candles
4. Detects 3-candle downward trend patterns
5. Saves stocks with detected trends to `data/pool.csv`

### Finalization Job (3:15 PM IST)

1. Reads stocks from `data/pool.csv`
2. Fetches current price for each stock
3. Checks if current price > Candle 3's high
4. Saves stocks meeting criteria to `data/final_stocks.csv` (buy signals)

## Output Files

- **`data/pool.csv`**: Contains stocks with detected trends
  - Columns: symbol, candle1_date, candle2_date, candle3_date, candle3_high, detection_date

- **`data/final_stocks.csv`**: Contains final buy signals
  - Columns: symbol, candle3_high, current_price, signal_date

## Configuration

Edit `config/stocks.py` to:
- Update the stock list (NIFTY_500_STOCKS)
- Change lookback period (LOOKBACK_DAYS)

## Logs

Log files are created in the `logs/` directory:
- `logs/finalization.log` - Finalization job logs
- `logs/pool_creation.log` - Pool creation job logs

## Verification

Run the verification script to check your setup:

```bash
python scripts/verify_cron.py
```

This will:
- Check if all required paths exist
- Verify scripts are valid and executable
- Check if cron jobs are installed
- Show current crontab entries
- Display log file status
- Provide instructions if setup is incomplete

## Troubleshooting

1. **Import errors**: Make sure you're running scripts from the project root directory
2. **Data fetch failures**: Check internet connection and stock symbol format (should end with `.NS` for Indian stocks)
3. **Cron not running**: 
   - Check cron service is running: `sudo service cron status` (Linux) or check System Settings on macOS
   - Verify paths in crontab are absolute
   - Check log files for errors: `tail -f logs/*.log`
   - On macOS, ensure Terminal/iTerm has Full Disk Access permissions
4. **Check cron jobs**: Run `crontab -l` to view installed jobs
5. **Remove cron jobs**: Run `crontab -e` and delete the lines, or `crontab -r` to remove all

## Notes

- The system uses yfinance for stock data (free, but may have rate limits)
- Stock symbols must include `.NS` suffix for Indian stocks (e.g., `RELIANCE.NS`)
- The system automatically skips weekends and non-trading days
- For production use, consider adding holiday calendar support
