"""Nifty 500 stock list configuration"""

# Nifty 500 stock symbols (with .NS suffix for yfinance)
# This is a sample list - in production, you would fetch the complete Nifty 500 list
# For now, using a subset of major stocks for testing

NIFTY_500_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "BHARTIARTL.NS",
    "SBIN.NS",
    "BAJFINANCE.NS",
    "LICI.NS",
    "ITC.NS",
    "HCLTECH.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "ASIANPAINT.NS",
    "MARUTI.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "SUNPHARMA.NS",
    "NESTLEIND.NS",
    "ONGC.NS",
    "NTPC.NS",
    "POWERGRID.NS",
    "M&M.NS",
    "TATAMOTORS.NS",
    "WIPRO.NS",
    "ADANIENT.NS",
    "JSWSTEEL.NS",
    "COALINDIA.NS",
]

# Configuration
LOOKBACK_DAYS = 30  # Number of days to look back for trend detection

