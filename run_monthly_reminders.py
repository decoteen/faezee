
#!/usr/bin/env python3
"""
Monthly Payment Reminder Runner
اجرای یادآوری‌های پرداخت ماهانه برای پرداخت‌های اقساطی
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.payment_reminder import PaymentReminderBot
from bot.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def run_monthly_reminders():
    """اجرای یادآوری‌های ماهانه"""
    try:
        logger.info("🔄 شروع بررسی یادآوری‌های پرداخت ماهانه...")
        
        config = Config()
        reminder_bot = PaymentReminderBot(config)
        
        # ارسال یادآوری‌های روزانه (که شامل یادآوری‌های ماهانه هم می‌شود)
        await reminder_bot.send_daily_reminders()
        
        logger.info("✅ بررسی یادآوری‌های ماهانه با موفقیت تکمیل شد")
        
    except Exception as e:
        logger.error(f"❌ خطا در اجرای یادآوری‌های ماهانه: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_monthly_reminders())
