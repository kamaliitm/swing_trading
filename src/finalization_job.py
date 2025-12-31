"""Finalization job - checks pool stocks and generates buy signals"""

import pandas as pd
import os
from typing import List
from datetime import datetime

from .data_fetcher import get_current_price


def finalize_stocks(
    pool_file: str = "data/pool.csv",
    output_file: str = "data/final_stocks.csv"
) -> pd.DataFrame:
    """
    Finalize stocks from pool that meet buy signal criteria.
    
    Criteria: Current price > Candle 3's high (oldest candle in pattern)
    
    Args:
        pool_file: Path to pool CSV file
        output_file: Path to output CSV file
    
    Returns:
        DataFrame with final stocks ready for investment
    """
    print(f"Starting finalization job at {datetime.now()}")
    
    # Read pool file
    if not os.path.exists(pool_file):
        print(f"Pool file not found: {pool_file}")
        print("Please run pool creation job first.")
        # Create empty CSV
        empty_df = pd.DataFrame(columns=[
            'symbol', 'candle3_high', 'current_price', 'signal_date'
        ])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        empty_df.to_csv(output_file, index=False)
        return empty_df
    
    pool_df = pd.read_csv(pool_file)
    
    if pool_df.empty:
        print("Pool is empty. No stocks to finalize.")
        # Create empty CSV
        empty_df = pd.DataFrame(columns=[
            'symbol', 'candle3_high', 'current_price', 'signal_date'
        ])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        empty_df.to_csv(output_file, index=False)
        return empty_df
    
    print(f"Checking {len(pool_df)} stocks from pool...")
    
    final_stocks = []
    
    for idx, row in pool_df.iterrows():
        symbol = row['symbol']
        candle3_high = float(row['candle3_high'])
        
        print(f"Checking {symbol}...", end=" ")
        
        try:
            # Get current price
            current_price = get_current_price(symbol)
            
            if current_price is None:
                print("Failed to get current price")
                continue
            
            print(f"Current: {current_price:.2f}, Candle 3 High: {candle3_high:.2f}", end=" ")
            
            # Check if current price > Candle 3's high
            if current_price > candle3_high:
                print("✓ BUY SIGNAL")
                final_stocks.append({
                    'symbol': symbol,
                    'candle3_high': candle3_high,
                    'current_price': current_price,
                    'signal_date': datetime.now()
                })
            else:
                print("✗ No signal")
        
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Create DataFrame
    if final_stocks:
        final_df = pd.DataFrame(final_stocks)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save to CSV
        final_df.to_csv(output_file, index=False)
        print(f"\nFinalization completed. Found {len(final_df)} stocks with buy signals.")
        print(f"Results saved to {output_file}")
        
        return final_df
    else:
        print("\nFinalization completed. No stocks with buy signals found.")
        # Create empty CSV with headers
        empty_df = pd.DataFrame(columns=[
            'symbol', 'candle3_high', 'current_price', 'signal_date'
        ])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        empty_df.to_csv(output_file, index=False)
        return empty_df


if __name__ == "__main__":
    # For testing
    finalize_stocks()

