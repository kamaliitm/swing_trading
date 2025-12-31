"""Finalization job - checks pool stocks and generates buy signals"""

import pandas as pd
import os
from typing import List, Optional
from datetime import datetime
import pytz

from .data_fetcher import fetch_stock_data_by_days
from .heiken_ashi import calculate_heiken_ashi


def get_today_heiken_ashi(symbol: str) -> Optional[dict]:
    """
    Get today's and yesterday's Heiken Ashi data for a stock.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Dictionary with today's and yesterday's HA data:
        {
            'today_open': float,
            'today_close': float,
            'today_high': float,
            'today_low': float,
            'yesterday_close': float or None  # None if not available
        }
        or None if not available
    """
    try:
        # Fetch recent data (last 5 days to ensure we get today and yesterday)
        df = fetch_stock_data_by_days(symbol, days=5)
        
        if df is None or df.empty:
            return None
        
        # Calculate Heiken Ashi
        ha_df = calculate_heiken_ashi(df)
        
        if ha_df is None or ha_df.empty:
            return None
        
        # Get the most recent (today's) candle
        today_candle = ha_df.iloc[-1]
        
        # Get yesterday's close if available
        yesterday_close = None
        if len(ha_df) >= 2:
            yesterday_candle = ha_df.iloc[-2]
            yesterday_close = float(yesterday_candle['Close'])
        
        return {
            'today_open': float(today_candle['Open']),
            'today_close': float(today_candle['Close']),
            'today_high': float(today_candle['High']),
            'today_low': float(today_candle['Low']),
            'yesterday_close': yesterday_close
        }
    
    except Exception as e:
        print(f"Error getting today's HA for {symbol}: {e}")
        return None


def finalize_stocks(
    pool_file: str = "data/pool.csv",
    output_file: str = "data/final_stocks.csv"
) -> pd.DataFrame:
    """
    Finalize stocks from pool that meet buy signal criteria.
    
    Criteria:
    1. Today's Heiken Ashi open < Candle 3's high (breakout hasn't happened at open)
    2. Current Heiken Ashi close > Candle 3's high (breakout happened today)
    
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
            'symbol', 'candle3_high', 'ha_open', 'ha_close', 'signal_date'
        ])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        empty_df.to_csv(output_file, index=False)
        return empty_df
    
    pool_df = pd.read_csv(pool_file)
    
    if pool_df.empty:
        print("Pool is empty. No stocks to finalize.")
        # Create empty CSV
        empty_df = pd.DataFrame(columns=[
            'symbol', 'candle3_high', 'ha_open', 'ha_close', 'signal_date'
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
            # Get today's Heiken Ashi data
            today_ha = get_today_heiken_ashi(symbol)
            
            if today_ha is None:
                print("Failed to get today's Heiken Ashi data")
                continue
            
            ha_open = today_ha['today_open']
            ha_close = today_ha['today_close']
            yesterday_close = today_ha['yesterday_close']
            
            print(f"HA Open: {ha_open:.2f}, HA Close: {ha_close:.2f}, Candle 3 High: {candle3_high:.2f}", end=" ")
            
            # Check criteria:
            # 1. Today's open < Candle 3 high (breakout hasn't happened at open)
            # 2. Current close > Candle 3 high (breakout happened)
            # 3. Yesterday's close < Candle 3 high (breakout happened TODAY, not earlier)
            breakout_today = False
            
            if ha_open < candle3_high and ha_close > candle3_high:
                # Check if breakout happened today (yesterday was below)
                if yesterday_close is not None:
                    if yesterday_close < candle3_high:
                        breakout_today = True
                    else:
                        print("✗ Breakout happened earlier (yesterday close >= Candle 3 high)")
                else:
                    # If we don't have yesterday's data, assume breakout is today
                    breakout_today = True
            
            if breakout_today:
                print("✓ BUY SIGNAL (breakout today)")
                final_stocks.append({
                    'symbol': symbol,
                    'candle3_high': candle3_high,
                    'ha_open': ha_open,
                    'ha_close': ha_close,
                    'signal_date': datetime.now()
                })
            elif ha_close <= candle3_high:
                print("✗ No breakout (HA close <= Candle 3 high)")
            elif ha_open >= candle3_high:
                print("✗ Breakout already happened (HA open >= Candle 3 high)")
            else:
                print("✗ No signal")
        
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
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
            'symbol', 'candle3_high', 'ha_open', 'ha_close', 'signal_date'
        ])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        empty_df.to_csv(output_file, index=False)
        return empty_df


if __name__ == "__main__":
    # For testing
    finalize_stocks()

