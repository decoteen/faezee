#!/usr/bin/env python3
"""
Payment Scheduler for 90-day Payment Plans
Manages monthly reminders for remaining payments.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from utils.logger import setup_logger
from utils.persian_utils import format_price, persian_numbers

logger = setup_logger(__name__)

class PaymentScheduler:
    """Manages payment schedules and monthly reminders"""

    def __init__(self, data_dir: str = "payment_data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.payment_file = os.path.join(self.data_dir, "payment_schedules.json")

    def _load_payment_schedules(self) -> Dict[str, Any]:
        """Load payment schedules from file"""
        try:
            if os.path.exists(self.payment_file):
                with open(self.payment_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading payment schedules: {e}")
            return {}

    def _save_payment_schedules(self, schedules: Dict[str, Any]) -> bool:
        """Save payment schedules to file"""
        try:
            with open(self.payment_file, 'w', encoding='utf-8') as f:
                json.dump(schedules, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving payment schedules: {e}")
            return False

    def add_60day_payment_schedule(self, user_id: int, customer_info: Dict[str, Any], 
                                 total_amount: float, advance_paid: float, 
                                 remaining_amount: float, order_id: str) -> bool:
        """Add a new 60-day payment schedule"""
        schedules = self._load_payment_schedules()

        # Calculate payment date (60 days from now)
        today = datetime.now()
        payment_date = (today + timedelta(days=60)).strftime("%Y-%m-%d")

        schedule_id = f"{user_id}_{order_id}_{int(today.timestamp())}"

        payment_schedule = {
            'user_id': user_id,
            'customer_info': customer_info,
            'order_id': order_id,
            'total_amount': total_amount,
            'advance_paid': advance_paid,
            'remaining_amount': remaining_amount,
            'payment_date': payment_date,
            'payment_type': '60day',
            'payments_made': [],
            'created_date': today.strftime("%Y-%m-%d"),
            'status': 'active'
        }

        schedules[schedule_id] = payment_schedule

        if self._save_payment_schedules(schedules):
            logger.info(f"Added 60-day payment schedule for user {user_id}, order {order_id}")
            return True
        return False

    def add_90day_payment_schedule(self, user_id: int, customer_info: Dict[str, Any], 
                                 total_amount: float, advance_paid: float, 
                                 remaining_amount: float, order_id: str) -> bool:
        """Add a new 90-day payment schedule"""
        schedules = self._load_payment_schedules()

        # Calculate monthly payments (remaining amount / 3 months)
        monthly_amount = remaining_amount / 3

        # Calculate payment dates
        today = datetime.now()
        payment_dates = [
            (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            (today + timedelta(days=60)).strftime("%Y-%m-%d"),
            (today + timedelta(days=90)).strftime("%Y-%m-%d")
        ]

        schedule_id = f"{user_id}_{order_id}_{int(today.timestamp())}"

        payment_schedule = {
            'user_id': user_id,
            'customer_info': customer_info,
            'order_id': order_id,
            'total_amount': total_amount,
            'advance_paid': advance_paid,
            'remaining_amount': remaining_amount,
            'monthly_amount': monthly_amount,
            'payment_dates': payment_dates,
            'payments_made': [],
            'created_date': today.strftime("%Y-%m-%d"),
            'status': 'active'
        }

        schedules[schedule_id] = payment_schedule

        if self._save_payment_schedules(schedules):
            logger.info(f"Added 90-day payment schedule for user {user_id}, order {order_id}")
            return True
        return False

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Get list of users who need payment reminders today"""
        schedules = self._load_payment_schedules()
        today = datetime.now().strftime("%Y-%m-%d")
        pending_reminders = []

        for schedule_id, schedule in schedules.items():
            if schedule['status'] != 'active':
                continue

            payment_type = schedule.get('payment_type', '90day')
            
            if payment_type == '60day':
                # For 60-day payments: single payment date
                payment_date = schedule['payment_date']
                if payment_date == today and not schedule['payments_made']:
                    reminder_info = {
                        'schedule_id': schedule_id,
                        'user_id': schedule['user_id'],
                        'customer_info': schedule['customer_info'],
                        'payment_number': 1,
                        'payment_amount': schedule['remaining_amount'],
                        'payment_type': '60day',
                        'payment_date': payment_date
                    }
                    pending_reminders.append(reminder_info)
            else:
                # For 90-day payments: multiple payment dates
                for i, payment_date in enumerate(schedule['payment_dates']):
                    if payment_date == today:
                        # Check if this payment hasn't been made yet
                        if i not in schedule['payments_made']:
                            reminder_info = {
                                'schedule_id': schedule_id,
                                'user_id': schedule['user_id'],
                                'customer_info': schedule['customer_info'],
                                'payment_number': i + 1,
                                'monthly_amount': schedule['monthly_amount'],
                                'remaining_payments': 3 - len(schedule['payments_made']),
                                'payment_type': '90day',
                                'payment_date': payment_date
                            }
                            pending_reminders.append(reminder_info)

        return pending_reminders

    def mark_payment_made(self, schedule_id: str, payment_number: int) -> bool:
        """Mark a payment as completed"""
        schedules = self._load_payment_schedules()

        if schedule_id not in schedules:
            logger.error(f"Schedule {schedule_id} not found")
            return False

        schedule = schedules[schedule_id]
        payment_type = schedule.get('payment_type', '90day')

        if payment_type == '60day':
            # For 60-day payments: mark as completed immediately
            schedule['payments_made'] = [0]  # Single payment made
            schedule['status'] = 'completed'
        else:
            # For 90-day payments: add payment to made payments list
            if payment_number - 1 not in schedule['payments_made']:
                schedule['payments_made'].append(payment_number - 1)
                schedule['payments_made'].sort()

            # Check if all payments are completed
            if len(schedule['payments_made']) >= 3:
                schedule['status'] = 'completed'

        if self._save_payment_schedules(schedules):
            logger.info(f"Marked payment {payment_number} as completed for schedule {schedule_id}")
            return True
        return False

    def get_user_payment_schedules(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all payment schedules for a specific user"""
        schedules = self._load_payment_schedules()
        user_schedules = []

        for schedule_id, schedule in schedules.items():
            if schedule['user_id'] == user_id:
                user_schedules.append({
                    'schedule_id': schedule_id,
                    **schedule
                })

        return user_schedules

    def generate_reminder_message(self, reminder_info: Dict[str, Any]) -> str:
        """Generate reminder message for payment"""
        customer = reminder_info['customer_info']
        payment_type = reminder_info.get('payment_type', '90day')
        
        if payment_type == '60day':
            amount = reminder_info['payment_amount']
            message = [
                "🔔 یادآوری پرداخت 60 روزه",
                "=" * 30,
                "",
                f"👤 مشتری: {customer['name']}",
                f"🏙️ شهر: {customer['city']}",
                f"🆔 کد مشتری: {customer['customer_id']}",
                "",
                f"💰 مبلغ باقی‌مانده: {format_price(amount)} تومان",
                f"📅 سررسید پرداخت: امروز",
                "",
                "📞 لطفاً با مشتری تماس بگیرید تا پرداخت کامل را انجام دهد.",
                "",
                "برای ثبت پرداخت از دکمه‌های زیر استفاده کنید:"
            ]
        else:
            payment_num = reminder_info['payment_number']
            amount = reminder_info['monthly_amount']
            remaining = reminder_info['remaining_payments']
            
            message = [
                "🔔 یادآوری پرداخت قسط ماهانه",
                "=" * 30,
                "",
                f"👤 مشتری: {customer['name']}",
                f"🏙️ شهر: {customer['city']}",
                f"🆔 کد مشتری: {customer['customer_id']}",
                "",
                f"📅 قسط شماره: {persian_numbers(str(payment_num))} از ۳",
                f"💰 مبلغ قسط: {format_price(amount)} تومان",
                f"📊 اقساط باقی‌مانده: {persian_numbers(str(remaining - 1))}",
                "",
                "📞 لطفاً با مشتری تماس بگیرید تا پرداخت را انجام دهد.",
                "",
                "برای ثبت پرداخت از دکمه‌های زیر استفاده کنید:"
            ]

        return "\n".join(message)

    def cancel_payment_schedule(self, schedule_id: str) -> bool:
        """Cancel a payment schedule"""
        schedules = self._load_payment_schedules()

        if schedule_id not in schedules:
            logger.error(f"Schedule {schedule_id} not found")
            return False

        schedules[schedule_id]['status'] = 'cancelled'

        if self._save_payment_schedules(schedules):
            logger.info(f"Cancelled payment schedule {schedule_id}")
            return True
        return False

    def schedule_payment_reminder(self, user_id: int, customer_name: str, amount: int, due_days: int, order_data: Dict):
        """Schedule a payment reminder"""
        try:
            # Load existing schedules
            schedules = self._load_payment_schedules()

            # Calculate due date
            due_date = (datetime.now() + timedelta(days=due_days)).isoformat()

            # Create schedule entry
            schedule_id = f"{user_id}_{int(datetime.now().timestamp())}"
            schedules[schedule_id] = {
                'user_id': user_id,
                'customer_name': customer_name,
                'amount': amount,
                'due_date': due_date,
                'due_days': due_days,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'order_data': order_data
            }

            # Save schedules
            if self._save_payment_schedules(schedules):
                logger.info(f"Payment reminder scheduled for user {user_id}, due in {due_days} days")
                return schedule_id
            else:
                return None


        except Exception as e:
            logger.error(f"Error scheduling payment reminder: {e}")
            return None