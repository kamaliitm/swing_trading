"""Trend detection module for 3-candle downward pattern"""

import pandas as pd
from typing import Optional
from datetime import datetime


def detect_trend(ha_df: pd.DataFrame) -> Optional[dict]:
    """
    Detect 3-candle downward trend pattern in reverse chronological order.
    
    Pattern criteria (in reverse chronological order, newest first):
    - All 3 candles must be RED (bearish): Open > Close
    - Candle 1 (newest): low < Candle 2 low, high < Candle 2 high
    - Candle 2 (middle): low < Candle 3 low, high < Candle 3 high
    - Candle 3 (oldest): Highest point in the pattern
    
    In chronological order, this represents a downward trend with all red candles.
    
    Args:
        ha_df: DataFrame with Heiken Ashi OHLC data, sorted oldest first
               Must have columns: ['Open', 'High', 'Low', 'Close']
    
    Returns:
        Dictionary with trend information if found:
        {
            'candle1_date': datetime,
            'candle2_date': datetime,
            'candle3_date': datetime,
            'candle1_high': float,
            'candle2_high': float,
            'candle3_high': float,
            'candle1_low': float,
            'candle2_low': float,
            'candle3_low': float,
            'detection_date': datetime
        }
        Returns None if no trend is found
    """
    if ha_df is None or len(ha_df) < 3:
        return None
    
    required_cols = ['Open', 'High', 'Low', 'Close']
    if not all(col in ha_df.columns for col in required_cols):
        return None
    
    # Reverse the dataframe to work in reverse chronological order (newest first)
    # We'll iterate from newest to oldest
    reversed_df = ha_df.iloc[::-1].reset_index()
    
    # Look for 3 consecutive candles matching the pattern
    for i in range(len(reversed_df) - 2):
        # Get the 3 candles in reverse chronological order (newest first)
        candle1 = reversed_df.iloc[i]      # Newest
        candle2 = reversed_df.iloc[i + 1]  # Middle
        candle3 = reversed_df.iloc[i + 2]  # Oldest
        
        # Extract values
        c1_open = candle1['Open']
        c1_close = candle1['Close']
        c1_low = candle1['Low']
        c1_high = candle1['High']
        
        c2_open = candle2['Open']
        c2_close = candle2['Close']
        c2_low = candle2['Low']
        c2_high = candle2['High']
        
        c3_open = candle3['Open']
        c3_close = candle3['Close']
        c3_low = candle3['Low']
        c3_high = candle3['High']
        
        # Check that all 3 candles are RED (bearish): Open > Close
        all_red = (c1_open > c1_close and 
                   c2_open > c2_close and 
                   c3_open > c3_close)
        
        if not all_red:
            continue  # Skip if not all candles are red
        
        # Check all 4 trend conditions:
        # 1. Candle 1 low < Candle 2 low
        # 2. Candle 1 high < Candle 2 high
        # 3. Candle 2 low < Candle 3 low
        # 4. Candle 2 high < Candle 3 high
        
        if (c1_low < c2_low and
            c1_high < c2_high and
            c2_low < c3_low and
            c2_high < c3_high):
            
            # Pattern found!
            # Get dates from the original index (before reversal)
            # Since we reversed, we need to map back to original indices
            orig_idx1 = len(ha_df) - 1 - i      # Newest candle (Candle 1)
            orig_idx2 = len(ha_df) - 2 - i      # Middle candle (Candle 2)
            orig_idx3 = len(ha_df) - 3 - i      # Oldest candle (Candle 3)
            
            # Extract dates from original DataFrame index
            if isinstance(ha_df.index[0], datetime):
                candle1_date = ha_df.index[orig_idx1]
                candle2_date = ha_df.index[orig_idx2]
                candle3_date = ha_df.index[orig_idx3]
            elif 'Date' in reversed_df.columns:
                candle1_date = candle1['Date']
                candle2_date = candle2['Date']
                candle3_date = candle3['Date']
            else:
                # Fallback: use index values as dates
                candle1_date = ha_df.index[orig_idx1]
                candle2_date = ha_df.index[orig_idx2]
                candle3_date = ha_df.index[orig_idx3]
            
            return {
                'candle1_date': candle1_date,
                'candle2_date': candle2_date,
                'candle3_date': candle3_date,
                'candle1_high': float(c1_high),
                'candle2_high': float(c2_high),
                'candle3_high': float(c3_high),
                'candle1_low': float(c1_low),
                'candle2_low': float(c2_low),
                'candle3_low': float(c3_low),
                'detection_date': datetime.now()
            }
    
    return None


def find_trends_in_stock(
    symbol: str,
    ha_df: pd.DataFrame
) -> Optional[dict]:
    """
    Find trend pattern in a stock's Heiken Ashi data.
    
    Args:
        symbol: Stock symbol
        ha_df: Heiken Ashi DataFrame
    
    Returns:
        Dictionary with trend info including symbol, or None if not found
    """
    trend = detect_trend(ha_df)
    if trend:
        trend['symbol'] = symbol
        return trend
    return None

