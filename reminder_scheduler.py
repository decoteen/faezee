
#!/usr/bin/env python3
"""
Automated Reminder Scheduler
اجرای خودکار یادآوری‌های پرداخت
"""

import asyncio
import schedule
import time
import threading
from datetime import datetime
from bot.payment_reminder import run_daily_reminder_check
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ReminderScheduler:
    """زمان‌بند خودکار یادآوری‌ها"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start_scheduler(self):
        """شروع زمان‌بند"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        # تنظیم زمان اجرا - هر روز ساعت 9 صبح
        schedule.every().day.at("09:00").do(self._run_daily_check)
        
        # تنظیم اجرای هر 4 ساعت برای پیگیری بیشتر
        schedule.every(4).hours.do(self._run_hourly_check)
        
        logger.info("✅ Reminder scheduler started - Daily at 9:00 AM, Every 4 hours")
        
        # اجرا در thread جداگانه
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
    
    def stop_scheduler(self):
        """توقف زمان‌بند"""
        self.running = False
        schedule.clear()
        logger.info("🛑 Reminder scheduler stopped")
    
    def _scheduler_loop(self):
        """حلقه اصلی زمان‌بند"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # چک هر دقیقه
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # در صورت خطا، 5 دقیقه صبر کن
    
    def _run_daily_check(self):
        """اجرای چک روزانه"""
        try:
            logger.info("🔔 Running daily reminder check...")
            asyncio.run(run_daily_reminder_check())
            logger.info("✅ Daily reminder check completed")
        except Exception as e:
            logger.error(f"Daily reminder error: {e}")
    
    def _run_hourly_check(self):
        """اجرای چک 4 ساعته"""
        try:
            current_hour = datetime.now().hour
            if 8 <= current_hour <= 20:  # فقط در ساعات کاری
                logger.info("🔔 Running hourly reminder check...")
                asyncio.run(run_daily_reminder_check())
                logger.info("✅ Hourly reminder check completed")
        except Exception as e:
            logger.error(f"Hourly reminder error: {e}")

# Instance برای استفاده در main
reminder_scheduler = ReminderScheduler()

if __name__ == "__main__":
    reminder_scheduler.start_scheduler()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reminder_scheduler.stop_scheduler()
        print("👋 Reminder scheduler stopped")
