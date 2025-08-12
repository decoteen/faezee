
#!/usr/bin/env python3
"""
Daily Payment Reminder Script
Run this script daily to send payment reminders for 90-day payment plans.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.payment_reminder import run_daily_reminder_check
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def main():
    """Main function to run daily reminders"""
    logger.info("Starting daily payment reminder check...")
    
    try:
        await run_daily_reminder_check()
        logger.info("Daily payment reminder check completed successfully")
        
    except Exception as e:
        logger.error(f"Error in daily reminder check: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
