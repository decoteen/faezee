#!/usr/bin/env python3
"""
DecoTeen Telegram Bot - Main Entry Point
ربات تلگرام فروشگاه دکوتین
"""

import logging
from telegram.ext import ApplicationBuilder
from bot.handlers import BotHandlers
from bot.config import Config
from utils.logger import setup_logger
from reminder_scheduler import reminder_scheduler

# تنظیم لاگر
logger = setup_logger(__name__)


def main():
    """تابع اصلی برای اجرای ربات"""
    try:
        # بارگذاری تنظیمات
        config = Config()

        if not config.bot_token:
            logger.error("❌ BOT_TOKEN not found in environment variables")
            print("❌ توکن ربات یافت نشد")
            return

        config.print_config_status()

        # ایجاد Application
        app = ApplicationBuilder().token(config.bot_token).build()

        # ایجاد handlers
        bot_handlers = BotHandlers()

        # تنظیم handlers
        bot_handlers.setup_handlers(app)

        # شروع سیستم یادآوری
        reminder_scheduler.start_scheduler()
        
        # شروع ربات
        logger.info("🚀 Starting DecoTeen Bot...")
        print("✅ ربات شروع شد...")
        print("🔔 سیستم یادآوری فعال شد...")

        # Add error handling for multiple bot instances
        try:
            app.run_polling(
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
                timeout=30,
                read_timeout=10,
                write_timeout=10,
                connect_timeout=10,
                pool_timeout=10
            )
        except Exception as polling_error:
            logger.error(f"Polling error: {polling_error}")
            # Wait a bit before potentially restarting
            import time
            time.sleep(5)
            raise

    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        print(f"❌ خطا در اجرای ربات: {e}")
        raise
    finally:
        logger.info("🛑 Bot stopped")


if __name__ == "__main__":
    print("🤖 DecoTeen Telegram Bot")
    print("=" * 40)

    try:
        # اجرای ربات
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        exit(1)
