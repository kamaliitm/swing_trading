"""Pool creation job - scans stocks and identifies trends"""

import pandas as pd
import os
from typing import List
from datetime import datetime

from .data_fetcher import fetch_stock_data_by_days
from .heiken_ashi import calculate_heiken_ashi
from .trend_detector import find_trends_in_stock
from config.stocks import NIFTY_500_STOCKS, LOOKBACK_DAYS


def check_reversal_already_crossed(
    ha_df: pd.DataFrame,
    candle1_date: datetime,
    candle3_high: float
) -> bool:
    """
    Check if reversal signal has already been crossed.
    
    Args:
        ha_df: Heiken Ashi DataFrame
        candle1_date: Date of Candle 1 (newest candle in trend)
        candle3_high: High value of Candle 3 (oldest candle in trend)
    
    Returns:
        True if reversal already crossed, False otherwise
    """
    # Find the index of Candle 1 in the dataframe
    candle1_idx = None
    for idx in ha_df.index:
        idx_date = idx.date() if isinstance(idx, datetime) else pd.Timestamp(idx).date()
        candle1_date_obj = candle1_date.date() if isinstance(candle1_date, datetime) else pd.Timestamp(candle1_date).date()
        if idx_date == candle1_date_obj:
            candle1_idx = ha_df.index.get_loc(idx)
            break
    
    # Check if reversal already happened after Candle 1
    if candle1_idx is not None and candle1_idx < len(ha_df) - 1:
        # Check all days after Candle 1
        for idx in range(candle1_idx + 1, len(ha_df)):
            day_ha_close = ha_df.iloc[idx]['Close']
            if day_ha_close > candle3_high:
                return True
    
    return False


def create_pool(output_file: str = "data/pool.csv") -> pd.DataFrame:
    """
    Create pool of stocks that satisfy the trend criteria.
    
    Only includes stocks where:
    1. A 3-candle downward trend pattern is detected (all RED candles)
    2. The reversal signal has NOT been crossed yet (no day after Candle 1 
       where HA close > Candle 3 high)
    
    This ensures we only track stocks with active trends that haven't 
    already reversed.
    
    Args:
        output_file: Path to output CSV file
    
    Returns:
        DataFrame with stocks that have detected trends (not yet breached)
    """
    print(f"Starting pool creation job at {datetime.now()}")
    print(f"Scanning {len(NIFTY_500_STOCKS)} stocks...")
    
    pool_results = []
    
    for i, symbol in enumerate(NIFTY_500_STOCKS, 1):
        print(f"[{i}/{len(NIFTY_500_STOCKS)}] Processing {symbol}...", end=" ")
        
        try:
            # Fetch stock data
            df = fetch_stock_data_by_days(symbol, days=LOOKBACK_DAYS)
            
            if df is None or df.empty:
                print("No data")
                continue
            
            # Calculate Heiken Ashi candles
            ha_df = calculate_heiken_ashi(df)
            
            if ha_df is None or ha_df.empty:
                print("Failed to calculate Heiken Ashi")
                continue
            
            # Detect trend
            trend = find_trends_in_stock(symbol, ha_df)
            
            if trend:
                # Check if reversal signal has already been crossed
                # We only want stocks where the trend exists but hasn't been breached yet
                candle1_date = trend['candle1_date']
                candle3_high = trend['candle3_high']
                
                reversal_already_crossed = check_reversal_already_crossed(
                    ha_df, candle1_date, candle3_high
                )
                
                if reversal_already_crossed:
                    print(f"Trend found but reversal already crossed (Candle 3 high: {candle3_high:.2f})")
                else:
                    print(f"Trend found! Candle 3 high: {candle3_high:.2f}")
                    pool_results.append({
                        'symbol': symbol,
                        'candle1_date': trend['candle1_date'],
                        'candle2_date': trend['candle2_date'],
                        'candle3_date': trend['candle3_date'],
                        'candle3_high': trend['candle3_high'],
                        'detection_date': trend['detection_date']
                    })
            else:
                print("No trend")
        
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Create DataFrame
    if pool_results:
        pool_df = pd.DataFrame(pool_results)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save to CSV
        pool_df.to_csv(output_file, index=False)
        print(f"\nPool creation completed. Found {len(pool_df)} stocks with trends.")
        print(f"Results saved to {output_file}")
        
        return pool_df
    else:
        print("\nPool creation completed. No stocks with trends found.")
        # Create empty CSV with headers
        empty_df = pd.DataFrame(columns=[
            'symbol', 'candle1_date', 'candle2_date', 'candle3_date',
            'candle3_high', 'detection_date'
        ])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        empty_df.to_csv(output_file, index=False)
        return empty_df


if __name__ == "__main__":
    # For testing
    create_pool()

