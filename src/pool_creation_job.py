"""Pool creation job - scans stocks and identifies trends"""

import pandas as pd
import os
from typing import List
from datetime import datetime

from .data_fetcher import fetch_stock_data_by_days
from .heiken_ashi import calculate_heiken_ashi
from .trend_detector import find_trends_in_stock
from config.stocks import NIFTY_500_STOCKS, LOOKBACK_DAYS


def create_pool(output_file: str = "data/pool.csv") -> pd.DataFrame:
    """
    Create pool of stocks that satisfy the trend criteria.
    
    Args:
        output_file: Path to output CSV file
    
    Returns:
        DataFrame with stocks that have detected trends
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
                print(f"Trend found! Candle 3 high: {trend['candle3_high']:.2f}")
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

