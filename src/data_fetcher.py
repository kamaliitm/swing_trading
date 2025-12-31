"""Stock data fetching module using yfinance"""

import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta


def fetch_stock_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Fetch OHLC data for a stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE.NS")
        period: Period to fetch (default: "1mo" for 1 month)
        interval: Data interval (default: "1d" for daily)
    
    Returns:
        DataFrame with OHLC data, or None if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return None
        
        # Ensure we have the required columns
        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            return None
        
        # Return only OHLC columns
        return df[required_cols].copy()
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def fetch_stock_data_by_days(
    symbol: str,
    days: int = 30
) -> Optional[pd.DataFrame]:
    """
    Fetch stock data for a specific number of days.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE.NS")
        days: Number of days to fetch
    
    Returns:
        DataFrame with OHLC data, or None if fetch fails
    """
    # Calculate start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 10)  # Add buffer for weekends/holidays
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval="1d")
        
        if df.empty:
            return None
        
        # Ensure we have the required columns
        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            return None
        
        # Return only OHLC columns, sorted by date (oldest first)
        return df[required_cols].copy().sort_index()
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def get_current_price(symbol: str) -> Optional[float]:
    """
    Get the current/latest price for a stock.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE.NS")
    
    Returns:
        Current price as float, or None if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try to get current price from info
        if 'currentPrice' in info:
            return float(info['currentPrice'])
        elif 'regularMarketPrice' in info:
            return float(info['regularMarketPrice'])
        elif 'previousClose' in info:
            return float(info['previousClose'])
        
        # Fallback: get latest close from history
        hist = ticker.history(period="1d", interval="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        
        return None
    
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None

