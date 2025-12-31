#!/usr/bin/env python3
"""
Executable script for pool creation job.
Invoked by cron at 4:30 PM IST on weekdays.
"""

import sys
import os
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pool_creation_job import create_pool


def is_trading_day() -> bool:
    """
    Check if today is a trading day (weekday, not a holiday).
    For now, we only check if it's a weekday.
    In production, you would also check against a holiday calendar.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    is_weekday = now_ist.weekday() < 5
    
    return is_weekday


def main():
    """Main entry point for the script."""
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    
    print(f"Pool Creation Job - Started at {now_ist.strftime('%Y-%m-%d %H:%M:%S IST')}")
    
    # Validate it's a trading day
    if not is_trading_day():
        print(f"Today is not a trading day. Skipping pool creation.")
        sys.exit(0)
    
    try:
        # Run the pool creation job
        result_df = create_pool()
        
        print(f"Pool Creation Job - Completed at {datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')}")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error in pool creation job: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

