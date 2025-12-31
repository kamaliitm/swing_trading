"""Heiken Ashi candle calculation module"""

import pandas as pd
from typing import Optional


def calculate_heiken_ashi(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Convert regular OHLC candles to Heiken Ashi candles.
    
    Heiken Ashi formulas:
    - Close = (Open + High + Low + Close) / 4
    - Open = (Previous HA Open + Previous HA Close) / 2
    - High = max(High, HA Open, HA Close)
    - Low = min(Low, HA Open, HA Close)
    
    Args:
        df: DataFrame with columns ['Open', 'High', 'Low', 'Close']
            Index should be datetime, sorted oldest first
    
    Returns:
        DataFrame with Heiken Ashi OHLC values, or None if input is invalid
    """
    if df is None or df.empty:
        return None
    
    required_cols = ['Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_cols):
        return None
    
    # Create a copy to avoid modifying original
    ha_df = df.copy()
    
    # Initialize Heiken Ashi columns
    ha_df['HA_Close'] = (ha_df['Open'] + ha_df['High'] + ha_df['Low'] + ha_df['Close']) / 4.0
    
    # Calculate HA_Open (needs previous values)
    ha_df['HA_Open'] = 0.0
    ha_df['HA_High'] = 0.0
    ha_df['HA_Low'] = 0.0
    
    # First candle: HA_Open = (regular Open + regular Close) / 2
    ha_df.iloc[0, ha_df.columns.get_loc('HA_Open')] = (
        ha_df.iloc[0]['Open'] + ha_df.iloc[0]['Close']
    ) / 2.0
    
    # Calculate for remaining candles
    for i in range(1, len(ha_df)):
        prev_ha_open = ha_df.iloc[i-1]['HA_Open']
        prev_ha_close = ha_df.iloc[i-1]['HA_Close']
        
        # HA_Open = (Previous HA_Open + Previous HA_Close) / 2
        ha_df.iloc[i, ha_df.columns.get_loc('HA_Open')] = (
            prev_ha_open + prev_ha_close
        ) / 2.0
    
    # Calculate HA_High and HA_Low for all candles
    for i in range(len(ha_df)):
        ha_open = ha_df.iloc[i]['HA_Open']
        ha_close = ha_df.iloc[i]['HA_Close']
        regular_high = ha_df.iloc[i]['High']
        regular_low = ha_df.iloc[i]['Low']
        
        # HA_High = max(High, HA_Open, HA_Close)
        ha_df.iloc[i, ha_df.columns.get_loc('HA_High')] = max(
            regular_high, ha_open, ha_close
        )
        
        # HA_Low = min(Low, HA_Open, HA_Close)
        ha_df.iloc[i, ha_df.columns.get_loc('HA_Low')] = min(
            regular_low, ha_open, ha_close
        )
    
    # Create result DataFrame with standard column names
    result = pd.DataFrame({
        'Open': ha_df['HA_Open'],
        'High': ha_df['HA_High'],
        'Low': ha_df['HA_Low'],
        'Close': ha_df['HA_Close']
    }, index=ha_df.index)
    
    return result

