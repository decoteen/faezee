
#!/usr/bin/env python3
"""
Payment Reminder System
Automated system to send monthly payment reminders for 90-day payment plans.
"""

import asyncio
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from bot.payment_scheduler import PaymentScheduler
from bot.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class PaymentReminderBot:
    """Automated payment reminder system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.bot = Bot(token=config.bot_token)
        self.payment_scheduler = PaymentScheduler()
    
    async def send_daily_reminders(self):
        """Check and send daily payment reminders"""
        try:
            pending_reminders = self.payment_scheduler.get_pending_reminders()
            
            if not pending_reminders:
                logger.info("No payment reminders due today")
                return
            
            logger.info(f"Found {len(pending_reminders)} payment reminders to send")
            
            for reminder in pending_reminders:
                await self._send_reminder_to_group(reminder)
                
        except Exception as e:
            logger.error(f"Error sending daily reminders: {e}")
    
    async def _send_reminder_to_group(self, reminder_info):
        """Send payment reminder to order group"""
        try:
            message = self.payment_scheduler.generate_reminder_message(reminder_info)
            
            # Create keyboard for payment confirmation
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ پرداخت انجام شد",
                        callback_data=f"payment_confirmed_{reminder_info['schedule_id']}_{reminder_info['payment_number']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📞 تماس گرفته شد",
                        callback_data=f"contact_made_{reminder_info['schedule_id']}_{reminder_info['payment_number']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⏰ یادآوری فردا",
                        callback_data=f"remind_tomorrow_{reminder_info['schedule_id']}_{reminder_info['payment_number']}"
                    )
                ]
            ]
            
            await self.bot.send_message(
                chat_id=self.config.order_group_chat_id,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            logger.info(f"Sent payment reminder for user {reminder_info['user_id']}")
            
        except Exception as e:
            logger.error(f"Error sending reminder to group: {e}")
    
    async def handle_payment_confirmation(self, schedule_id: str, payment_number: int):
        """Handle payment confirmation from group admin"""
        try:
            success = self.payment_scheduler.mark_payment_made(schedule_id, payment_number)
            
            if success:
                logger.info(f"Payment {payment_number} confirmed for schedule {schedule_id}")
                return "✅ پرداخت با موفقیت ثبت شد!"
            else:
                logger.error(f"Failed to confirm payment {payment_number} for schedule {schedule_id}")
                return "❌ خطا در ثبت پرداخت"
                
        except Exception as e:
            logger.error(f"Error handling payment confirmation: {e}")
            return "❌ خطا در ثبت پرداخت"

async def run_daily_reminder_check():
    """Function to run daily reminder check"""
    config = Config()
    reminder_bot = PaymentReminderBot(config)
    await reminder_bot.send_daily_reminders()

if __name__ == "__main__":
    # Run daily reminder check
    asyncio.run(run_daily_reminder_check())
