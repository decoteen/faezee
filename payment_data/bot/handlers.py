#!/usr/bin/env python3
"""
Bot Handlers
Main bot handlers for commands, callbacks, and message processing.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.keyboards import BotKeyboards
from bot.cart import CartManager
from bot.pricing import PricingManager
from bot.zarinpal import ZarinPalGateway
from bot.payment_scheduler import PaymentScheduler
from bot.order_server import OrderManagementServer, OrderStatus
from bot.config import Config
from data.customer_service import CustomerService
from data.product_data import (get_products_by_category, get_product_by_id,
                               search_products_by_name,
                               search_products_by_icon, get_category_info,
                               get_product_price, PERSIAN_ALPHABET, PRODUCT_PRICES)
from utils.logger import setup_logger
from utils.persian_utils import format_price, persian_numbers
from datetime import datetime
from typing import Dict, List
import json

logger = setup_logger(__name__)


class BotHandlers:
    """Main class handling all bot interactions"""

    def __init__(self):
        self.keyboards = BotKeyboards()
        self.cart_manager = CartManager()
        self.pricing_manager = PricingManager()
        self.customer_service = CustomerService()
        self.config = Config()
        self.zarinpal = ZarinPalGateway(
            merchant_id=self.config.zarinpal_merchant_id,
            sandbox=self.config.zarinpal_sandbox)
        self.payment_scheduler = PaymentScheduler()
        self.order_server = OrderManagementServer()
        self.user_sessions = {}  # Store user session data
        self.bot = None  # Bot instance برای اطلاع‌رسانی
        logger.info("🔄 PricingManager initialized with updated payment display configurations")

    def setup_handlers(self, application):
        """Setup all bot handlers"""
        # تنظیم bot instance در سرور سفارشات و handlers
        self.order_server.set_bot(application.bot)
        self.bot = application.bot  # تنظیم bot instance در handlers

        # Command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("debug", self.debug_command))
        application.add_handler(CommandHandler("pricing", self.pricing_test_command))

        # Callback query handlers
        application.add_handler(CallbackQueryHandler(self.button_callback))

        # Message handlers
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           self.handle_text_message))

        # Photo handler for receipt uploads
        application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_photo_message))

        # Group message handler for support
        application.add_handler(
            MessageHandler(filters.TEXT & filters.ChatType.GROUPS,
                           self.handle_group_message))

        logger.info("✅ All handlers registered successfully")

    async def start_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        logger.info(f"User {user_id} started the bot")

        # Set user state to awaiting customer code directly
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id]['awaiting_customer_code'] = True

        welcome_text = ("🔐 خوش آمدید به فروشگاه دکوتین\n\n"
                        "لطفاً کد شش رقمی نمایندگی خود را وارد کنید:")

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = ("📋 راهنمای استفاده از ربات:\n\n"
                     "🔹 /start - شروع کار با ربات\n"
                     "🔹 احراز هویت با کد نمایندگی\n"
                     "🔹 مرور محصولات بر اساس دسته‌بندی\n"
                     "🔹 جستجوی حروف الفبایی\n"
                     "🔹 انتخاب سایز و تعداد\n"
                     "🔹 افزودن به سبد خرید\n"
                     "🔹 مشاهده فاکتور و پرداخت\n\n"
                     "💡 برای شروع دکمه «احراز هویت نماینده» را بزنید.")
        await update.message.reply_text(help_text)

    async def debug_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Handle /debug command - for troubleshooting"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        user_id = update.effective_user.id

        debug_info = (
            f"🔍 اطلاعات دیباگ:\n\n"
            f"💬 Chat ID: {chat_id}\n"
            f"📝 Chat Type: {chat_type}\n"
            f"👤 User ID: {user_id}\n"
            f"⚙️ Configured Group ID: {self.config.order_group_chat_id}\n"
            f"✅ Match: {'YES' if str(chat_id) == str(self.config.order_group_chat_id) else 'NO'}\n\n"
            f"📋 Test Commands:\n"
            f"• سفارش\n"
            f"• راهنما\n"
            f"• آمار"
        )

        await update.message.reply_text(debug_info)

        # ذخیره Chat ID برای استفاده آینده
        logger.info(f"🔧 DEBUG: Chat ID {chat_id} can be used as ORDER_GROUP_CHAT_ID")

    async def pricing_test_command(self, update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):
        """Handle /pricing command - test pricing functionality"""
        test_items = [{
            'product_name': 'تشک بچه تست',
            'size': '120x60',
            'quantity': 1,
            'price': 4780000
        }]
        test_customer = {
            'name': 'تست کاربر',
            'city': 'تهران',
            'customer_id': '123456'
        }

        # Test different pricing methods
        cash_invoice = self.pricing_manager.generate_final_invoice(
            test_items, test_customer, "پرداخت نقدی", 0.30)

        pricing_info = (
            f"💰 تست سیستم قیمت‌گذاری:\n\n"
            f"🔧 نرخ تخفیف نقدی: {self.pricing_manager.discount_rates.get('cash', 0) * 100}%\n"
            f"🔧 نرخ تخفیف اقساطی: {self.pricing_manager.discount_rates.get('installment', 0) * 100}%\n"
            f"🔧 نرخ تخفیف 90 روزه: {self.pricing_manager.discount_rates.get('90day', 0) * 100}%\n\n"
            f"📄 نمونه فاکتور:\n"
            f"{cash_invoice[:200]}..."
        )

        await update.message.reply_text(pricing_info)
        logger.info(f"💰 Pricing test executed for user {update.effective_user.id}")

    async def button_callback(self, update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
        """Handle all button callbacks - Optimized version"""
        query = update.callback_query
        user_id = query.from_user.id
        data = query.data

        # Fast answer to prevent timeout
        await query.answer()

        logger.debug(f"User {user_id} pressed: {data}")

        # Quick routing dictionary for better performance
        handlers = {
            "authenticate": self._handle_authentication_request,
            "main_menu": self._handle_main_menu,
            "start_shopping": self._handle_start_shopping,
            "view_cart": self._handle_view_cart,
            "view_invoice": self._handle_view_invoice,
            "upload_receipt": self._handle_upload_receipt_request,
            "confirm_payment_receipt": self._handle_payment_receipt_confirmation,
            "confirm_payment_terms": self._handle_payment_terms_confirmation,
            "confirm_order": self._handle_order_confirmation,
            "cart_clear": self._handle_cart_clear,
            "verify_payment": self._handle_payment_verification,
            "payment_completed": self._handle_payment_completed,
            "back_to_categories": self._handle_back_to_categories,
            "back_to_alphabet": self._handle_back_to_alphabet,
            "back_to_curtain_subcategories": self._handle_back_to_curtain_subcategories,
            "back_to_products": self._handle_back_to_products,
            "daily_stats": self._handle_daily_stats_request,
            "refresh_daily_orders": self._handle_refresh_daily_orders,
            "back_to_daily_orders": self._handle_back_to_daily_orders,
            "contact_support": self._handle_contact_support_request,
            "faq": self._handle_faq_request,
            "confirm_60day_order": self._handle_60day_order_confirmation,
        }

        try:
            # Direct handler for exact matches
            if data in handlers:
                await handlers[data](query)
                return

            # Prefix-based routing for better performance
            if data.startswith("category_"):
                await self._handle_category_selection(query, data)
            elif data.startswith("subcategory_"):
                await self._handle_subcategory_selection(query, data)
            elif data.startswith("alpha_"):
                await self._handle_alphabet_selection(query, data)
            elif data.startswith("product_"):
                await self._handle_product_selection(query, data)
            elif data.startswith("size_selection_"):
                await self._handle_size_selection_from_category(query, data)
            elif data.startswith("size_"):
                await self._handle_size_selection(query, data)
            elif data.startswith("qty_"):
                await self._handle_quantity_selection(query, data)
            elif data.startswith("payment_"):
                await self._handle_payment_selection(query, data)
            elif data.startswith("order_status_"):
                await self._handle_order_status_update(query, data)
            elif data.startswith("order_details_"):
                await self._handle_order_details_request(query, data)
            elif data.startswith("order_"):
                await self._handle_order_actions(query, data)
            elif data.startswith("alphabet_search_"):
                await self._handle_alphabet_search(query, data)

            elif data.startswith("fabric_"):
                await self._handle_fabric_selection(query, data)
            elif data == "back_to_fabric_selection":
                await self._handle_back_to_fabric_selection(query)
            elif data.startswith("payment_confirmed_"):
                await self._handle_payment_confirmation_from_group(query, data)
            elif data.startswith("contact_made_"):
                await self._handle_contact_made_from_group(query, data)
            elif data.startswith("remind_tomorrow_"):
                await self._handle_remind_tomorrow_from_group(query, data)
            else:
                await query.edit_message_text(" سفارش درحال پیگیری است .")

        except Exception as e:
            logger.error(f"Callback error {data}: {e}")
            try:
                await query.edit_message_text("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
            except:
                pass  # Prevent secondary errors

    async def handle_text_message(self, update: Update,
                                  context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text.strip()

        # Check if user is in authentication process
        if user_id in self.user_sessions and self.user_sessions[user_id].get(
                'awaiting_customer_code'):
            await self._handle_customer_code_input(update, text)
        # Check if user is inputting curtain height
        elif user_id in self.user_sessions and self.user_sessions[user_id].get(
                'awaiting_curtain_height'):
            await self._handle_curtain_height_input(update, text)
        else:
            await update.message.reply_text(
                "لطفاً از دکمه‌های موجود استفاده کنید.",
                reply_markup=self.keyboards.get_main_menu(
                    self._is_authenticated(user_id)))

    async def handle_photo_message(self, update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages (for receipt uploads)"""
        user_id = update.effective_user.id

        # Check if user is waiting for receipt upload
        if (user_id in self.user_sessions and
            self.user_sessions[user_id].get('payment_info', {}).get('awaiting_receipt')):

            # Store photo info
            photo = update.message.photo[-1]  # Get highest resolution photo
            self.user_sessions[user_id]['receipt_photo'] = {
                'file_id': photo.file_id,
                'file_unique_id': photo.file_unique_id
            }

            # Get payment info for final invoice display
            payment_info = self.user_sessions[user_id]['payment_info']
            customer = self.user_sessions[user_id]['customer']
            cart_items = self.cart_manager.get_cart(user_id)

            # Generate final invoice text
            final_invoice = (
                f"✅ فاکتور نهایی\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 مشتری: {customer['name']}\n"
                f"🏙️ شهر: {customer['city']}\n"
                f"💳 روش پرداخت: {payment_info['payment_method']}\n\n"
                f"💰 مبلغ کل: {format_price(payment_info['subtotal'])} تومان\n"
                f"🎁 تخفیف ({persian_numbers(str(int(payment_info['discount_rate'] * 100)))}٪): {format_price(payment_info['discount'])} تومان\n"
                f"💰 مبلغ پرداختی: {format_price(payment_info['amount'])} تومان\n\n"
                f"📸 فیش واریزی دریافت شد\n"
                f"✅ آماده تایید نهایی سفارش"
            )

            # Show confirmation button with final invoice
            keyboard = [[
                InlineKeyboardButton("✅ سفارش را تایید می‌کنم", callback_data="confirm_payment_receipt")
            ], [
                InlineKeyboardButton("🔄 ارسال عکس جدید", callback_data="upload_receipt")
            ]]

            await update.message.reply_text(
                final_invoice,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                "لطفاً ابتدا روش پرداخت را انتخاب کنید.",
                reply_markup=self.keyboards.get_main_menu(
                    self._is_authenticated(user_id)))

    async def handle_group_message(self, update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in group chats (support group)"""
        chat_id = update.effective_chat.id
        message_text = update.message.text.strip() if update.message.text else ""
        user_name = update.effective_user.first_name or "کاربر"

        # Log group info for debugging
        logger.info(f"📩 Group message received:")
        logger.info(f"   Chat ID: {chat_id} (type: {type(chat_id)})")
        logger.info(f"   Chat Title: {getattr(update.effective_chat, 'title', 'N/A')}")
        logger.info(f"   Message: '{message_text}'")
        logger.info(f"   User: {user_name}")
        logger.info(f"   Configured group ID: {self.config.order_group_chat_id} (type: {type(self.config.order_group_chat_id)})")

        # تبدیل chat_id به int برای مقایسه
        try:
            current_group_id = int(chat_id)
            config_group_id = int(self.config.order_group_chat_id) if self.config.order_group_chat_id else None
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting chat IDs to int: {e}")
            return

        # بررسی اینکه آیا این گروه، گروه مناسب هست یا نه
        if config_group_id and current_group_id != config_group_id:
            logger.info(f"❌ پیام از گروه مختلف: {current_group_id} != {config_group_id}")
            return

        # اگر هیچ group ID تنظیم نشده، این گروه را به عنوان گروه اصلی در نظر بگیر
        if not config_group_id:
            logger.warning(f"⚠️ GROUP_CHAT_ID تنظیم نشده - استفاده از گروه فعلی: {current_group_id}")
            self.config.order_group_chat_id = current_group_id

        logger.info(f"✅ Processing group message: '{message_text}'")

        # اگر پیام خالی باشد، نادیده بگیر
        if not message_text:
            return

        # فقط پردازش دستورات مشخص - جلوگیری از پردازش پیام‌های عادی
        message_lower = message_text.lower().strip()

        # لیست دقیق دستورات مجاز
        valid_commands = [
            'سفارش', 'سفارشات', 'order', 'orders',
            'فاکتور', 'فاکتورها', 'invoice', 'invoices',
            'آمار', 'stat', 'statistics',
            'راهنما', 'help', 'کمک', 'دستور',
            'ربات', 'bot', '@decoteen_bot'
        ]

        # بررسی آیا پیام شامل دستور معتبر است یا خیر
        is_valid_command = False
        for cmd in valid_commands:
            if cmd in message_lower:
                is_valid_command = True
                break

        # بررسی دستور وضعیت
        if message_text.startswith('وضعیت ') or message_text.startswith('status '):
            is_valid_command = True

        # اگر پیام دستور معتبری نیست، آن را نادیده بگیر
        if not is_valid_command:
            logger.debug(f"🔍 پیام عادی نادیده گرفته شد: '{message_text}'")
            return

        try:
            # پردازش دستورات معتبر
            if any(word in message_lower for word in ['سفارش', 'سفارشات', 'order', 'orders']):
                logger.info("🎯 دستور سفارش شناسایی شد")
                await self._show_daily_orders(update)
                return
            elif any(word in message_lower for word in ['فاکتور', 'فاکتورها', 'invoice', 'invoices']):
                logger.info("🎯 دستور فاکتور شناسایی شد")
                await self._show_daily_invoices(update)
                return
            elif message_text.startswith('وضعیت ') or message_text.startswith('status '):
                order_id = message_text.replace('وضعیت ', '').replace('status ', '').strip()
                logger.info(f"🎯 درخواست وضعیت سفارش: {order_id}")
                await self._show_order_status(update, order_id)
                return
            elif any(word in message_lower for word in ['آمار', 'stat', 'statistics']):
                logger.info("🎯 دستور آمار شناسایی شد")
                await self._show_orders_statistics(update)
                return
            elif any(word in message_lower for word in ['راهنما', 'help', 'کمک', 'دستور']):
                logger.info("🎯 دستور راهنما شناسایی شد")
                await self._show_group_help(update)
                return
            elif message_lower in ['ربات', 'bot', '@decoteen_bot']:
                logger.info("🎯 دستور تست ربات شناسایی شد")
                await update.message.reply_text(
                    "🤖 ربات DecoTeen آماده خدمات‌رسانی است!\n\n"
                    "📋 دستورات موجود:\n"
                    "• سفارش - نمایش سفارشات امروز\n"
                    "• فاکتور - نمایش فاکتورهای امروز\n"
                    "• آمار - نمایش آمار کلی\n"
                    "• راهنما - نمایش راهنمای کامل\n\n"
                    f"🔧 Chat ID این گروه: {current_group_id}"
                )
                return

        except Exception as e:
            logger.error(f"❌ خطا در پردازش پیام گروه: {e}")
            logger.error(f"Message: '{message_text}', Chat ID: {current_group_id}")

            # ارسال پیام خطا به گروه
            try:
                await update.message.reply_text(
                    f"❌ خطا در پردازش دستور: {str(e)[:100]}\n"
                    "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
                )
            except Exception as reply_error:
                logger.error(f"خطا در ارسال پیام خطا: {reply_error}")

        return

    async def _show_daily_orders(self, update: Update):
        """Show today's orders as clickable summary with icons"""
        try:
            logger.info("🔍 درخواست نمایش سفارشات امروز")

            # Get today's orders
            today_orders = await self.order_server.get_todays_orders()
            logger.info(f"📊 تعداد سفارشات امروز: {len(today_orders)}")

            if not today_orders:
                await update.message.reply_text(
                    f"📊 سفارشات امروز ({persian_numbers(datetime.now().strftime('%Y/%m/%d'))})\n\n"
                    "هیچ سفارش جدیدی امروز ثبت نشده است. 📋\n\n"
                    "💡 برای تست می‌توانید یک سفارش جدید ثبت کنید."
                )
                return

            # Create summary message with clickable icons
            summary_text = (
                f"📊 سفارشات امروز ({persian_numbers(datetime.now().strftime('%Y/%m/%d'))})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 تعداد کل: {persian_numbers(str(len(today_orders)))}\n\n"
                f"🔽 روی هر آیکون کلیک کنید تا فاکتور کامل را ببینید:\n\n"
            )

            # Create inline keyboard with clickable order icons
            keyboard = []
            for i, order in enumerate(today_orders, 1):
                customer = order.get('customer', {})
                status_icon = "🆕" if order.get('status') == 'pending' else "✅"

                button_text = f"{status_icon} {persian_numbers(str(i))} - {customer.get('name', 'نامشخص')[:10]}"
                callback_data = f"order_details_{order['order_id']}"

                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

            # Add summary row at the bottom
            keyboard.append([
                InlineKeyboardButton("📈 آمار کلی", callback_data="daily_stats"),
                InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_daily_orders")
            ])

            await update.message.reply_text(
                summary_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            logger.info("✅ لیست سفارشات امروز با موفقیت ارسال شد")

        except Exception as e:
            logger.error(f"❌ خطا در نمایش سفارشات روزانه: {e}")
            await update.message.reply_text(
                f"❌ خطا در نمایش سفارشات روزانه.\n"
                f"جزئیات: {str(e)[:100]}\n"
                "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
            )

    async def _show_daily_invoices(self, update: Update):
        """Show today's invoices in the group"""
        try:
            today_orders = await self.order_server.get_todays_orders()

            if not today_orders:
                await update.message.reply_text(
                    "📄 گزارش فاکتورهای امروز\n\n"
                    "هیچ فاکتوری امروز صادر نشده است. 📋"
                )
                return

            invoice_text = (
                f"📄 فاکتورهای امروز ({persian_numbers(datetime.now().strftime('%Y/%m/%d'))})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )

            for i, order in enumerate(today_orders, 1):
                customer = order.get('customer', {})
                pricing = order.get('pricing', {})

                invoice_text += (
                    f"{persian_numbers(str(i))}. 📋 {order['order_id']}\n"
                    f"   👤 {customer.get('name', 'نامشخص')}\n"
                    f"   🏙️ {customer.get('city', 'نامشخص')}\n"
                    f"   💰 {format_price(pricing.get('total', 0))} تومان\n"
                    f"   📊 {self.order_server._get_status_text(order.get('status', 'pending'))}\n\n"
                )

            # Create action keyboard
            keyboard = [
                [
                    InlineKeyboardButton("💾 ذخیره گزارش", callback_data="save_daily_invoices"),
                    InlineKeyboardButton("📧 ارسال ایمیل", callback_data="email_daily_invoices")
                ],
                [
                    InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_daily_invoices")
                ]
            ]

            await update.message.reply_text(
                invoice_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error showing daily invoices: {e}")
            await update.message.reply_text(
                "❌ خطا در نمایش فاکتورهای روزانه. لطفاً دوباره تلاش کنید."
            )

    async def _show_order_status(self, update: Update, order_id: str):
        """Show specific order status"""
        try:
            order_data = await self.order_server.get_order_details(order_id)

            if not order_data:
                await update.message.reply_text(
                    f"❌ سفارش {order_id} یافت نشد.\n"
                    "لطفاً شماره سفارش را بررسی کنید."
                )
                return

            status_text = self.order_server._get_status_text(order_data['status'])
            customer = order_data.get('customer', {})
            pricing = order_data.get('pricing', {})

            order_info = (
                f"📋 وضعیت سفارش: {order_id}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 مشتری: {customer.get('name', 'نامشخص')}\n"
                f"🏙️ شهر: {customer.get('city', 'نامشخص')}\n"
                f"📊 وضعیت فعلی: {status_text}\n"
                f"💰 مبلغ کل: {format_price(pricing.get('total', 0))} تومان\n"
                f"⏰ تاریخ ثبت: {persian_numbers(order_data.get('created_at', '')[:10])}\n"
            )

            # Create management keyboard
            keyboard = self.order_server._create_admin_buttons(order_id, order_data['user_id'])

            await update.message.reply_text(
                order_info,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error showing order status: {e}")
            await update.message.reply_text(
                "❌ خطا در نمایش وضعیت سفارش. لطفاً دوباره تلاش کنید."
            )

    async def _show_orders_statistics(self, update: Update):
        """Show orders statistics in the group"""
        try:
            stats = await self.order_server.get_orders_statistics()

            if not stats:
                await update.message.reply_text(
                    "📊 آمار سفارشات در دسترس نیست."
                )
                return

            stats_text = (
                f"📊 آمار کلی سفارشات\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 کل سفارشات: {persian_numbers(str(stats.get('total_orders', 0)))}\n"
                f"🆕 سفارشات امروز: {persian_numbers(str(stats.get('today_orders', 0)))}\n"
                f"💰 درآمد کل: {format_price(stats.get('total_revenue', 0))} تومان\n"
                f"💳 درآمد امروز: {format_price(stats.get('today_revenue', 0))} تومان\n\n"
                f"📈 توزیع وضعیت:\n"
            )

            for status, count in stats.get('status_distribution', {}).items():
                stats_text += f"• {status}: {persian_numbers(str(count))}\n"

            await update.message.reply_text(stats_text)

        except Exception as e:
            logger.error(f"Error showing statistics: {e}")
            await update.message.reply_text(
                "❌ خطا در نمایش آمار. لطفاً دوباره تلاش کنید."
            )

    async def _show_group_help(self, update: Update):
        """Show help commands for group"""
        help_text = (
            "🤖 راهنمای دستورات گروه\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 سفارش / سفارشات - نمایش سفارشات امروز\n"
            "📄 فاکتور / فاکتورها - نمایش فاکتورهای امروز\n"
            "📊 آمار - نمایش آمار کلی\n"
            "🔍 وضعیت [شماره سفارش] - بررسی وضعیت سفارش\n"
            "❓ راهنما / کمک - نمایش این راهنما\n\n"
            "💡 نکته: فقط در گروه پشتیبانی فعال است"
        )

        await update.message.reply_text(help_text)

    async def _send_order_invoice_card(self, update: Update, order: Dict):
        """Send order as invoice card with management buttons"""
        try:
            customer = order.get('customer', {})
            pricing = order.get('pricing', {})
            cart_items = order.get('cart_items', [])

            # Create invoice card
            invoice_card = (
                f"🧾 فاکتور - {order['order_id']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 {customer.get('name', 'نامشخص')}\n"
                f"🏙️ {customer.get('city', 'نامشخص')}\n"
                f"🆔 کد نمایندگی: {customer.get('customer_id', 'نامشخص')}\n"
                f"📱 شناسه کاربر: {order.get('user_id', 'نامشخص')}\n"
                f"⏰ {persian_numbers(order.get('created_at', '')[:16].replace('T', ' - '))}\n\n"
                f"📦 آیتم‌ها:\n"
            )

            # Add cart items
            for i, item in enumerate(cart_items, 1):
                item_total = item.get('price', 0) * item.get('quantity', 0)
                invoice_card += (
                    f"{persian_numbers(str(i))}. {item.get('product_name', 'محصول')}\n"
                    f"   📏 {item.get('size', 'نامشخص')} | "
                    f"📦 {persian_numbers(str(item.get('quantity', 0)))} عدد | "
                    f"💰 {format_price(item_total)}\n"
                )

            # Add pricing
            invoice_card += (
                f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💳 {order.get('payment_method', 'نقدی')}\n"
                f"💰 مبلغ کل: {format_price(pricing.get('total', 0))} تومان\n"
                f"📊 {self.order_server._get_status_text(order.get('status', 'pending'))}"
            )

            # Create management keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📞 تماس", callback_data=f"order_status_{order['order_id']}_contacted"),
                    InlineKeyboardButton("✅ تایید", callback_data=f"order_status_{order['order_id']}_confirmed"),
                    InlineKeyboardButton("📦 آماده", callback_data=f"order_status_{order['order_id']}_ready")
                ],
                [
                    InlineKeyboardButton("🚚 ارسال", callback_data=f"order_status_{order['order_id']}_shipped"),
                    InlineKeyboardButton("🎉 تکمیل", callback_data=f"order_status_{order['order_id']}_completed"),
                    InlineKeyboardButton("❌ لغو", callback_data=f"order_status_{order['order_id']}_cancelled")
                ]
            ]

            await update.message.reply_text(
                invoice_card,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error sending order invoice card: {e}")

    async def _send_order_summary_with_buttons(self, update: Update, order: Dict):
        """Send order summary with management buttons (kept for compatibility)"""
        await self._send_order_invoice_card(update, order)

    async def _handle_authentication_request(self, query):
        """Handle authentication request"""
        user_id = query.from_user.id

        # Set user state to awaiting customer code
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id]['awaiting_customer_code'] = True

        text = ("🔐 احراز هویت \n\n"
                " لطفاً کد نمایندگی خود را وارد کنید:")
        await query.edit_message_text(text)

    async def _handle_customer_code_input(self, update, customer_code):
        """Handle customer code input"""
        user_id = update.effective_user.id

        # Validate customer code
        customer = self.customer_service.authenticate_customer(customer_code)

        if customer:
            # Authentication successful
            self.user_sessions[user_id] = {
                'authenticated': True,
                'customer': customer,
                'awaiting_customer_code': False
            }

            welcome_text = (f"✅ خوش آمدید {customer['name']} عزیز!\n"
                            f"🏙️ شهر: {customer['city']}\n"
                            f"🆔 کد نمایندگی: {customer['customer_id']}\n\n"
                            "\n"
                            "جهت سفارش محصول مورد نظر خودرا انتخاب نمایید:")

            keyboard = self.keyboards.get_categories_keyboard()
            await update.message.reply_text(welcome_text,
                                            reply_markup=keyboard)
        else:
            # Authentication failed
            error_text = ("❌ کد نمایندگی نامعتبر است.\n"
                          "لطفاً کد نمایندگی صحیح خود را وارد کنید:")
            await update.message.reply_text(error_text)

    async def _handle_main_menu(self, query):
        """Handle main menu"""
        user_id = query.from_user.id
        authenticated = self._is_authenticated(user_id)

        if authenticated:
            customer = self.user_sessions[user_id]['customer']
            text = (f"🏠 منوی اصلی\n\n"
                    f"👤 {customer['name']}\n"
                    f"🏙️ {customer['city']}\n\n"
                    "یکی از گزینه‌های زیر را انتخاب کنید:")
        else:
            text = "🏠 منوی اصلی\n\nبرای شروع خرید، ابتدا احراز هویت کنید."

        keyboard = self.keyboards.get_main_menu(authenticated)
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_start_shopping(self, query):
        """Handle start shopping"""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("ابتدا باید احراز هویت کنید.")
            return

        text = ("عالیه \n\n"
                "جهت سفارش محصول موردنطر خودرا انتخاب کنین:")

        keyboard = self.keyboards.get_categories_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_view_cart(self, query):
        """Handle view cart"""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("ابتدا باید احراز هویت کنید.")
            return

        cart_items = self.cart_manager.get_cart(user_id)

        if not cart_items:
            text = "🛍️ سبد خرید شما خالی است."
            keyboard = self.keyboards.get_main_menu(authenticated=True)
        else:
            text = "🛍️ سبد خرید شما:\n\n"
            total = 0

            for i, item in enumerate(cart_items, 1):
                item_total = item['price'] * item['quantity']
                total += item_total
                text += (
                    f"{persian_numbers(str(i))}. {item['product_name']}\n"
                    f"   📏 سایز: {item['size']}\n"
                    f"   📦 تعداد: {persian_numbers(str(item['quantity']))}\n"
                    f"   💰 قیمت: {format_price(item_total)} تومان\n\n")

            text += f"💰 مجموع: {format_price(total)} تومان"
            keyboard = self.keyboards.get_cart_management_keyboard()

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_view_invoice(self, query):
        """Handle view invoice"""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("ابتدا باید احراز هویت کنید.")
            return

        cart_items = self.cart_manager.get_cart(user_id)
        customer = self.user_sessions[user_id]['customer']

        invoice_text = self.pricing_manager.generate_invoice(
            cart_items, customer)
        keyboard = self.keyboards.get_payment_keyboard()

        await query.edit_message_text(invoice_text, reply_markup=keyboard)

    async def _handle_category_selection(self, query, data):
        """Handle category selection"""
        category = data.replace("category_", "")
        user_id = query.from_user.id

        # Store selected category in session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id]['selected_category'] = category

        category_info = get_category_info(category)
        category_name = category_info.get('name', category)

        if category == "curtain_only":
            # For curtain_only, show products directly with icon-based keyboard
            text = f"{category_name}\n\nعالیه! حالا بگو کدوم طرح؟"
            keyboard = self.keyboards.get_category_products_keyboard(category)
        elif category == "tablecloth":
            # For tablecloth, show subcategories first
            keyboard = self.keyboards.get_tablecloth_subcategories()
            await query.edit_message_text("انتخاب فرشینه:",
                                          reply_markup=keyboard)
            return
        else:
            # For other categories, show products directly with icon-based keyboard
            text = f"{category_name}\n\nعالیه! حالا بگو کدوم طرح؟"
            keyboard = self.keyboards.get_category_products_keyboard(category)

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_subcategory_selection(self, query, data):
        """Handle subcategory selection"""
        subcategory = data.replace("subcategory_", "")
        user_id = query.from_user.id

        # Store selected subcategory in session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id]['selected_subcategory'] = subcategory

        text = f"🔤 جستجوی حروف الفبایی\n\nحرف اول نام محصول مورد نظر را انتخاب کنید:"
        keyboard = self.keyboards.get_alphabetical_keyboard(subcategory)
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_alphabet_selection(self, query, data):
        """Handle alphabet selection"""
        parts = data.split("_")
        if len(parts) < 3:
            await query.edit_message_text("❌ داده نامعتبر.")
            return
        category = parts[1]
        letter = parts[2]
        user_id = query.from_user.id

        # Get products starting with selected letter
        subcategory = self.user_sessions[user_id].get('selected_subcategory')
        actual_category = subcategory if subcategory else category

        products = search_products_by_name(category, letter, subcategory)

        if not products:
            text = f"❌ محصولی با حرف «{letter}» یافت نشد.\n\nحرف دیگری را انتخاب کنید:"
            keyboard = self.keyboards.get_alphabetical_keyboard(
                actual_category)
        else:
            text = f"📦 محصولات با حرف «{letter}»:\n\nیکی را انتخاب کنید:"
            keyboard = self.keyboards.get_products_keyboard(products, category)

            # Store filtered products in session
            self.user_sessions[user_id]['filtered_products'] = products

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_product_selection(self, query, data):
        """Handle product selection"""
        product_id = data.replace("product_", "")
        user_id = query.from_user.id

        # Find product by ID
        product = get_product_by_id(product_id)

        if not product:
            await query.edit_message_text("❌ محصول یافت نشد.")
            return

        # Store selected product in session
        self.user_sessions[user_id]['selected_product'] = product

        # Get price based on product (check for special pricing first)
        category = product.get('category_id', 'baby')

        # For curtains, show fabric selection first
        if category == 'curtain_only':
            # Check if it's the special bedside curtain
            if product_id == 'curtain_15':  # پرده حریر سرتخت (جفت)
                price = get_product_price(product['id'], category)
                text = (f"📦 {product['name']}\n"
                        f"💰 قیمت: {format_price(price)} تومان\n\n"
                        "عالیه! انتخابت\n"
                        "ارتفاع: 240 و عرض 2×290 هست که قابل تغییر نیست")
                self.user_sessions[user_id]['selected_fabric'] = 'special'
                self.user_sessions[user_id]['selected_category'] = category
                self.user_sessions[user_id]['selected_size'] = 'ارتفاع: 240 - عرض: 2×290'

                keyboard = [[InlineKeyboardButton("بله همین محصول رو میخوام", callback_data="qty_1")]]
                keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_categories")])
                keyboard = InlineKeyboardMarkup(keyboard)
            else:
                text = (f"📦 {product['name']}\n\n"
                        "عالیه! مدل پرده‌ای که انتخاب کردی. حالا جنس پارچش چی باشه؟")
                keyboard = self.keyboards.get_fabric_selection_keyboard()
        # For tablecloth, show base price initially
        elif category == 'tablecloth':
            price = PRODUCT_PRICES[category]  # Show base price
            text = (f"📦 {product['name']}\n"
                    f"💰 قیمت: از {format_price(price)} تومان\n\n"
                    "سایز مورد نظر را انتخاب کنید:")
            # Store category for size selection
            self.user_sessions[user_id]['selected_category'] = category
            keyboard = self.keyboards.get_size_selection_keyboard(category)
        # For cushions, skip size selection and go directly to quantity
        elif category == 'cushion':
            price = get_product_price(product['id'], category)
            # Store default size for cushions
            self.user_sessions[user_id]['selected_size'] = 'استاندارد'
            self.user_sessions[user_id]['selected_category'] = category

            text = (f"📦 {product['name']}\n"
                    f"💰 قیمت: {format_price(price)} تومان\n\n"
                    "تعداد مورد نظر را انتخاب کنید:")
            keyboard = self.keyboards.get_quantity_keyboard()
        else:
            price = get_product_price(product['id'], category)
            text = (f"📦 {product['name']}\n"
                    f"💰 قیمت: {format_price(price)} تومان\n\n"
                    "سایز مورد نظر را انتخاب کنید:")
            keyboard = self.keyboards.get_size_selection_keyboard(category)

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_size_selection_from_category(self, query, data):
        """Handle size selection directly from category"""
        category = data.replace("size_selection_", "")
        user_id = query.from_user.id

        # Store selected category in session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id]['selected_category'] = category

        category_info = get_category_info(category)
        category_name = category_info.get('name', category)
        price = category_info.get('price', 4780000)

        if category == 'tablecloth':
            text = (f"{category_name}\n\n"
                    f"💰 قیمت: از {format_price(price)} تومان\n\n"
                    "چه انتخاب خوبی! حالا سایز تشک چقدر باشه؟")
        else:
            text = (f"{category_name}\n\n"
                    f"💰 قیمت: {format_price(price)} تومان\n\n"
                    "چه انتخاب خوبی! حالا سایز تشک چقدر باشه؟")

        # Use the keyboard's size selection method instead of hardcoded sizes
        keyboard = self.keyboards.get_size_selection_keyboard(category)
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_size_selection(self, query, data):
        """Handle size selection"""
        parts = data.split("_")
        if len(parts) >= 3:
            size = "_".join(parts[1:-1])  # All parts except first and last
            category = parts[-1]  # Last part is category
        else:
            size = data.replace("size_", "")
            category = self.user_sessions.get(query.from_user.id,
                                              {}).get('selected_category',
                                                      'baby')

        user_id = query.from_user.id

        # Store selected size and category in session
        self.user_sessions[user_id]['selected_size'] = size
        self.user_sessions[user_id]['selected_category'] = category

        # Get category info for price
        category_info = get_category_info(category)

        # For tablecloth, get size-based price
        if category == 'tablecloth':
            price = get_product_price('', category, size)
        else:
            price = category_info.get('price', 4780000)

        text = (f"📏 سایز انتخابی: {size}\n"
                f"💰 قیمت: {format_price(price)} تومان\n\n"
                "طرح قشنگی انتخاب کردی! حالا تعداد چقدر باشه؟")
        keyboard = self.keyboards.get_quantity_keyboard()

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_quantity_selection(self, query, data):
        """Handle quantity selection"""
        quantity = int(data.replace("qty_", ""))
        user_id = query.from_user.id

        # Get session data
        session = self.user_sessions[user_id]
        size = session.get('selected_size')
        category = session.get('selected_category', 'baby')
        fabric = session.get('selected_fabric')

        # Check if we have a specific product or just category
        if 'selected_product' in session:
            # Product-based ordering
            product = session['selected_product']
            category = product.get('category_id', category)
            product_name = product['name']
            product_id = product['id']
        else:
            # Category-based ordering (for teen and adult)
            category_info = get_category_info(category)
            product_name = category_info.get('name', category)
            product_id = f"{category}_generic"

        # Get price based on product and fabric
        if category == 'tablecloth':
            price = get_product_price(product_id, category, size)
        elif category == 'curtain_only' and fabric:
            if fabric == 'special':  # For bedside curtain
                price = get_product_price(product['id'], category)
            else:
                price = get_product_price(product_id, category, fabric=fabric)
        else:
            price = get_product_price(product['id'], category)

        # Add fabric info to product name if applicable
        if fabric and fabric != 'special':
            fabric_name = "حریر کتان" if fabric == "silk_cotton" else "مخمل"
            product_name = f"{product_name} - {fabric_name}"

        # Add to cart
        cart_item = {
            'product_id': product_id,
            'product_name': product_name,
            'size': size,
            'quantity': quantity,
            'price': price
        }

        self.cart_manager.add_to_cart(user_id, cart_item)

        total_price = price * quantity
        text = (f"✅ محصول به سبد خرید اضافه شد!\n\n"
                f"📦 {product_name}\n"
                f"📏 سایز: {size}\n"
                f"📦 تعداد: {persian_numbers(str(quantity))}\n"
                f"💰 قیمت کل: {format_price(total_price)} تومان\n\n"
                "می‌خواهید چه کار کنید؟")

        keyboard = self.keyboards.get_cart_management_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_payment_selection(self, query, data):
        """Handle payment selection"""
        user_id = query.from_user.id

        # Check authentication
        if not self._is_authenticated(user_id):
            await query.edit_message_text(
                "❌ ابتدا باید احراز هویت کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=False))
            return

        cart_items = self.cart_manager.get_cart(user_id)
        if not cart_items:
            await query.edit_message_text(
                "❌ سبد خرید شما خالی است.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        customer = self.user_sessions[user_id]['customer']

        if data == "payment_cash_card":
            await self._handle_card_to_card_payment(query, "cash", "پرداخت نقدی", 0.30)
        elif data == "payment_60day_card":
            await self._handle_card_to_card_payment(query, "60day", "پرداخت ۶۰ روز", 0.25)
        elif data == "payment_90day_card":
            await self._handle_card_to_card_payment(query, "90day", "پرداخت ۹۰ روز", 0.25)

    async def _handle_zarinpal_payment(self, query, payment_type: str,
                                       payment_method: str):
        """Handle ZarinPal payment"""
        user_id = query.from_user.id
        cart_items = self.cart_manager.get_cart(user_id)
        customer = self.user_sessions[user_id]['customer']

        if not cart_items:
            await query.edit_message_text(
                "❌ سبد خرید شما خالی است.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        # Calculate payment amount based on type
        subtotal = self.pricing_manager.calculate_subtotal(cart_items)
        discount_rate = self.pricing_manager.discount_rates.get(
            payment_type, 0)
        discount = self.pricing_manager.calculate_discount(
            subtotal, discount_rate)

        if payment_type == "90day":
            # For 90-day payment, only 25% advance payment required
            amount = int((subtotal - discount) * 0.25)  # 25% advance
            description = f"پیش‌پرداخت ۲۵٪ سفارش - {customer['name']}"
        else:
            # For cash payment, full amount
            amount = int(subtotal - discount)
            description = f"پرداخت نقدی سفارش - {customer['name']}"

        # Create payment request with proper callback URL
        callback_url = "https://www.zarinpal.com/pg/services/WebGate/wsdl"  # Temporary callback

        payment_result = self.zarinpal.create_payment_request(
            amount=amount,
            description=description,
            callback_url=callback_url,
            customer_mobile=customer.get('phone', ''),
            customer_email=customer.get('email', ''))

        if payment_result['success']:
            # Store payment info in session
            self.user_sessions[user_id]['payment_info'] = {
                'authority': payment_result['authority'],
                'amount': amount,
                'payment_type': payment_type,
                'payment_method': payment_method
            }

            text = (f"💳 {payment_method}\n\n"
                    f"💰 مبلغ قابل پرداخت: {format_price(amount)} تومان\n\n"
                    "🔗 برای پرداخت روی دکمه زیر کلیک کنید:")

            keyboard = [[
                InlineKeyboardButton("💳 پرداخت آنلاین",
                                     url=payment_result['payment_url'])
            ],
                        [
                            InlineKeyboardButton(
                                "✅ پرداخت انجام شد",
                                callback_data="payment_completed")
                        ],
                        [
                            InlineKeyboardButton("🔙 بازگشت",
                                                 callback_data="view_invoice")
                        ],
                        [
                            InlineKeyboardButton("🏠 منوی اصلی",
                                                 callback_data="main_menu")
                        ]]

            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            text = (f"❌ خطا در ایجاد درخواست پرداخت:\n"
                    f"{payment_result['error']}\n\n"
                    "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.")

            keyboard = [[
                InlineKeyboardButton(
                    "🔄 تلاش مجدد",
                    callback_data=f"payment_{payment_type}_zarinpal")
            ], [
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")
            ]]

            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _handle_card_to_card_payment(self, query, payment_type: str, payment_method: str, discount_rate: float):
        """Handle card-to-card payment"""
        user_id = query.from_user.id
        cart_items = self.cart_manager.get_cart(user_id)
        customer = self.user_sessions[user_id]['customer']

        if not cart_items:
            await query.edit_message_text(
                "❌ سبد خرید شما خالی است.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        # Calculate payment amount
        subtotal = self.pricing_manager.calculate_subtotal(cart_items)
        discount = self.pricing_manager.calculate_discount(subtotal, discount_rate)
        final_amount = subtotal - discount

        # Store payment info in session
        self.user_sessions[user_id]['payment_info'] = {
            'payment_type': payment_type,
            'payment_method': payment_method,
            'amount': final_amount if payment_type not in ["90day", "60day"] else int(final_amount * 0.25),
            'discount_rate': discount_rate,
            'awaiting_receipt': payment_type != "60day",  # 60-day doesn't need receipt
            'full_amount': final_amount,
            'subtotal': subtotal,
            'discount': discount
        }

        # Generate payment details based on payment type
        if payment_type == "cash":
            payment_details = (
                f"💳 پرداخت نقدی (30% تخفیف)\n"
                f"از اعتماد شما ممنونیم\n\n"
                f"💰 مبلغ کل: {format_price(subtotal)} تومان\n"
                f"🎁 تخفیف (30%): {format_price(discount)} تومان\n"
                f"💰 مبلغ نهایی پس از تخفیف: {format_price(final_amount)} تومان\n\n"
                f"🏦 اطلاعات حساب:\n"
                f"💳 شماره کارت: 6219861915854102\n"
                f"🏦 شماره شبا: IR110560611828005185959401\n"
                f"👤 به نام:نیما کریمی\n\n"
                f"📸 پس از واریز، لطفاً عکس فیش واریزی را ارسال کنید:"
            )
            # Create keyboard for cash payment
            keyboard = [[
                InlineKeyboardButton("📸 ارسال فیش واریزی", callback_data="upload_receipt")
            ], [
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]

        elif payment_type == "60day":
            payment_details = (
                f"💳 پرداخت 60 روزه (25% تخفیف)\n"
                f"از اعتماد شما ممنونیم\n\n"
                f"💰 مبلغ کل: {format_price(subtotal)} تومان\n"
                f"🎁 تخفیف (25%): {format_price(discount)} تومان\n"
                f"💰 مبلغ نهایی: {format_price(final_amount)} تومان\n\n"
                f"📅 مشتری در طول 60 روز آینده مبلغ را خورد خورد پرداخت خواهد کرد\n"
                f"⏰ یادآوری ماهانه برای پیگیری پرداخت فعال خواهد شد\n\n"
                f"✅ برای تایید سفارش و فعال‌سازی یادآوری ماهانه دکمه زیر را بزنید:"
            )
            # Create keyboard for 60-day payment
            keyboard = [[
                InlineKeyboardButton("✅ سفارشم را تایید می‌کنم و یادآوری ماهانه را تایید",
                                   callback_data="confirm_60day_order")
            ], [
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]

        elif payment_type == "90day":
            advance_payment = int(final_amount * 0.25)
            payment_details = (
                f"💳 پرداخت 90 روزه (25% تخفیف + 25% پیش‌پرداخت)\n"
                f"از اعتماد شما ممنونیم\n\n"
                f"💰 مبلغ کل: {format_price(subtotal)} تومان\n"
                f"🎁 مبلغ تخفیف (25%): {format_price(discount)} تومان\n"
                f"💰 مبلغ نهایی: {format_price(final_amount)} تومان\n"
                f"💳 پیش‌پرداخت (25%): {format_price(advance_payment)} تومان\n\n"
                f"🏦 اطلاعات حساب:\n"
                f"💳 شماره کارت: 6219861915854102\n"
                f"🏦 شماره شبا: IR110560611828005185959401\n"
                f"👤 به نام: نیما کریمی\n\n"
                f"📸 پس از واریز پیش‌پرداخت، لطفاً عکس فیش واریزی را ارسال کنید:"
            )
            # Create keyboard for 90-day payment
            keyboard = [[
                InlineKeyboardButton("📸 ارسال فیش واریزی", callback_data="upload_receipt")
            ], [
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]

        await query.edit_message_text(
            payment_details,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _handle_payment_terms_confirmation(self, query):
        """Handle payment terms confirmation for 60-day and 90-day payments"""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("❌ ابتدا باید احراز هویت کنید.")
            return

        payment_info = self.user_sessions[user_id].get('payment_info')
        if not payment_info:
            await query.edit_message_text(
                "❌ اطلاعات پرداخت یافت نشد.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        customer = self.user_sessions[user_id]['customer']
        cart_items = self.cart_manager.get_cart(user_id)

        # Send invoice to support group
        invoice_text = self.pricing_manager.generate_final_invoice(
            cart_items, customer, payment_info['payment_method'], payment_info['discount_rate'])

        # ارسال به گروه پشتیبانی
        if self.config.order_group_chat_id:
            try:
                group_message = (
                    f"📋 تایید پرداخت اقساطی\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 نام مشتری: {customer['name']}\n"
                    f"🏙️ شهر: {customer['city']}\n"
                    f"🆔 کد نمایندگی: {customer['customer_id']}\n"
                    f"📱 شناسه کاربر: {user_id}\n"
                    f"💳 روش پرداخت: {payment_info['payment_method']}\n"
                    f"💰 پیش‌پرداخت: {format_price(payment_info['amount'])} تومان\n"
                    f"💰 مبلغ باقی‌مانده: {format_price(payment_info['full_amount'] - payment_info['amount'])} تومان\n"
                    f"⏰ زمان تایید: {persian_numbers(datetime.now().strftime('%Y/%m/%d - %H:%M'))}\n\n"
                    f"📋 جزئیات سفارش:\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{invoice_text}"
                )

                await query.bot.send_message(
                    chat_id=self.config.order_group_chat_id,
                    text=group_message
                )
                logger.info(f"✅ اطلاعات پرداخت اقساطی ارسال شد به گروه")

            except Exception as e:
                logger.error(f"❌ خطا در ارسال اطلاعات به گروه: {e}")

        # Schedule payment reminder for both 60-day and 90-day payments
        if payment_info['payment_type'] in ['60day', '90day']:
            total_amount = payment_info['full_amount']
            advance_paid = payment_info['amount']
            remaining_amount = total_amount - advance_paid

            # Create order ID for tracking
            order_id = f"ORDER_{user_id}_{int(datetime.now().timestamp())}"

            if payment_info['payment_type'] == '60day':
                # For 60-day payment: single reminder after 60 days
                self.payment_scheduler.add_60day_payment_schedule(
                    user_id=user_id,
                    customer_info=customer,
                    total_amount=total_amount,
                    advance_paid=advance_paid,
                    remaining_amount=remaining_amount,
                    order_id=order_id
                )
                logger.info(f"✅ برنامه پرداخت 60 روزه برای کاربر {user_id} تنظیم شد")
            else:
                # For 90-day payment: monthly reminders
                self.payment_scheduler.add_90day_payment_schedule(
                    user_id=user_id,
                    customer_info=customer,
                    total_amount=total_amount,
                    advance_paid=advance_paid,
                    remaining_amount=remaining_amount,
                    order_id=order_id
                )
                logger.info(f"✅ برنامه پرداخت 90 روزه برای کاربر {user_id} تنظیم شد")

        # Show upload receipt interface
        await query.edit_message_text(
            f"✅ شرایط پرداخت تایید شد!\n\n"
            f"💰 مبلغ پیش‌پرداخت: {format_price(payment_info['amount'])} تومان\n"
            f"📅 یادآوری ماهانه برای مابقی پرداخت تنظیم شد\n\n"
            f"📸 لطفاً عکس فیش واریز پیش‌پرداخت را ارسال کنید:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📸 ارسال فیش واریزی", callback_data="upload_receipt")
            ], [
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]))


        if payment_type in ["60day", "90day"]:
            keyboard = [[
                InlineKeyboardButton(button_text, callback_data="confirm_payment_terms")
            ], [
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]
        else:
            keyboard = [[
                InlineKeyboardButton("📸 ارسال فیش واریزی", callback_data="upload_receipt")
            ], [
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]

        await query.edit_message_text(
            bank_info,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _handle_upload_receipt_request(self, query):
        """Handle receipt upload request"""
        await query.edit_message_text(
            "📸 لطفاً عکس فیش واریزی خود را در این چت ارسال کنید.\n\n"
            "⚠️ فقط تصاویر با فرمت JPG, PNG قابل قبول هستند.\n\n"
            "پس از ارسال عکس، دکمه تایید نمایش داده خواهد شد.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="view_invoice")
            ]]))

    async def _handle_payment_receipt_confirmation(self, query):
        """Handle payment receipt confirmation"""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("❌ ابتدا باید احراز هویت کنید.")
            return

        # Check if user is authenticated
        if not self._is_authenticated(user_id):
            await query.edit_message_text(
                "❌ ابتدا باید احراز هویت کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=False))
            return

        customer = self.user_sessions[user_id]['customer']
        cart_items = self.cart_manager.get_cart(user_id)
        payment_info = self.user_sessions[user_id].get('payment_info')

        if not payment_info:
            await query.edit_message_text(
                "❌ اطلاعات پرداخت یافت نشد.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        if not cart_items:
            await query.edit_message_text(
                "❌ سبد خرید شما خالی است.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        try:
            # Get receipt photo if available
            receipt_photo_id = None
            if 'receipt_photo' in self.user_sessions[user_id]:
                receipt_photo_id = self.user_sessions[user_id]['receipt_photo']['file_id']

            # Create order using order management server
            order_id = await self.order_server.create_order(
                user_id=user_id,
                customer=customer,
                cart_items=cart_items,
                payment_method=payment_info['payment_method'],
                discount_rate=payment_info['discount_rate'],
                receipt_photo_id=receipt_photo_id
            )

            # Clear cart and payment info
            self.cart_manager.clear_cart(user_id)
            if 'payment_info' in self.user_sessions[user_id]:
                del self.user_sessions[user_id]['payment_info']
            if 'receipt_photo' in self.user_sessions[user_id]:
                del self.user_sessions[user_id]['receipt_photo']

            # Confirm to customer
            await query.edit_message_text(
                f"✅ عالیه! سفارش شما با موفقیت ثبت شد!\n"
                f"📋 شماره سفارش: {order_id}\n"
                f"🔄 بعد از تایید تیم پشتیبانی دکوتین شما را در جریان سفارش قرار خواهیم داد.\n"
                f"🙏 از اعتماد شما ممنونیم.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))

            logger.info(f"✅ سفارش {order_id} با موفقیت ثبت شد برای کاربر {user_id}")

        except Exception as e:
            logger.error(f"Error in payment receipt confirmation: {e}")
            logger.error(f"User ID: {user_id}, Customer: {customer if customer else 'None'}, Cart items: {len(cart_items) if cart_items else 0}")

            # More detailed error handling
            try:
                await query.edit_message_text(
                    f"❌ خطایی در ثبت سفارش رخ داد.\n"
                    f"لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
                    f"کد خطا: {type(e).__name__}",
                    reply_markup=self.keyboards.get_main_menu(authenticated=True))
            except Exception as edit_error:
                logger.error(f"Error editing message: {edit_error}")
                # Send new message if editing fails
                try:
                    await query.message.reply_text(
                        f"❌ خطایی در ثبت سفارش رخ داد.\n"
                        f"لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                        reply_markup=self.keyboards.get_main_menu(authenticated=True))
                except Exception as reply_error:
                    logger.error(f"Error sending reply: {reply_error}")

    async def _handle_group_payment(self, query, payment_type: str,
                                    payment_method: str):
        """Handle group payment (installment)"""
        user_id = query.from_user.id
        cart_items = self.cart_manager.get_cart(user_id)
        customer = self.user_sessions[user_id]['customer']

        # Check if cart is not empty
        if not cart_items:
            await query.edit_message_text(
                "❌ سبد خرید شما خالی است.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        # Check if group chat ID is configured
        if not self.config.order_group_chat_id:
            await query.edit_message_text(
                "❌ گروه پیگیری سفارش تنظیم نشده است. لطفاً با پشتیبانی تماس بگیرید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        try:
            # Generate final invoice
            discount_rate = self.pricing_manager.discount_rates.get(
                payment_type, 0.25)
            invoice_text = self.pricing_manager.generate_final_invoice(
                cart_items, customer, payment_method, discount_rate)

            # Send to customer with confirmation
            confirmation_text = (
                f"{invoice_text}\n\n"
                "✅ سفارش شما ثبت شد و به گروه پیگیری ارسال می‌شود.\n"
                "📞 کارشناسان ما به زودی با شما تماس خواهند گرفت.")

            keyboard = [[
                InlineKeyboardButton("✅ تایید سفارش",
                                     callback_data="confirm_order")
            ], [
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")
            ]]

            # Store order info for confirmation```python
            self.user_sessions[user_id]['pending_order'] = {
                'payment_method': payment_method,
                'discount_rate': discount_rate,
                'invoice_text': invoice_text
            }

            await query.edit_message_text(
                confirmation_text, reply_markup=InlineKeyboardMarkup(keyboard))

            logger.info(
                "Group payment processed successfully for user {user_id}")

        except Exception as e:
            logger.error(f"Error in group payment handling: {e}")
            await query.edit_message_text(
                "❌ خطایی در پردازش سفارش رخ داد. لطفاً دوباره تلاش کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))

    async def _handle_order_confirmation(self, query):
        """Handle order confirmation using order management server"""
        user_id = query.from_user.id

        # Check if user is authenticated
        if not self._is_authenticated(user_id):
            await query.edit_message_text(
                "❌ ابتدا باید احراز هویت کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=False))
            return

        customer = self.user_sessions[user_id]['customer']
        cart_items = self.cart_manager.get_cart(user_id)
        pending_order = self.user_sessions[user_id].get('pending_order')

        if not pending_order:
            await query.edit_message_text(
                "❌ اطلاعات سفارش یافت نشد.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        if not cart_items:
            await query.edit_message_text(
                "❌ سبد خرید شما خالی است.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        try:
            # استفاده از سرور مدیریت سفارشات
            order_id = await self.order_server.create_order(
                user_id=user_id,
                customer=customer,
                cart_items=cart_items,
                payment_method=pending_order['payment_method'],
                discount_rate=pending_order['discount_rate']
            )

            # Clear cart and session
            self.cart_manager.clear_cart(user_id)
            if 'pending_order' in self.user_sessions[user_id]:
                del self.user_sessions[user_id]['pending_order']

            # Store order ID in session
            self.user_sessions[user_id]['last_order_id'] = order_id

            # Confirm to customer
            await query.edit_message_text(
                f"✅ عالیه! سفارش شما با موفقیت ثبت شد!\n"
                f"📋 شماره سفارش: {order_id}\n"
                f"🔄 بعد از تایید تیم پشتیبانی دکوتین شما را در جریان سفارش قرار خواهیم داد.\n"
                f"🙏 از اعتماد شما ممنونیم.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))

        except Exception as e:
            logger.error(f"Error in order confirmation: {e}")
            await query.edit_message_text(
                "❌ خطایی در ثبت سفارش رخ داد. لطفاً دوباره تلاش کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))

    async def _handle_payment_completed(self, query):
        """Handle payment completed confirmation"""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("❌ ابتدا باید احراز هویت کنید.")
            return

        payment_info = self.user_sessions[user_id].get('payment_info')
        if not payment_info:
            await query.edit_message_text(
                "❌ اطلاعات پرداخت یافت نشد.\n"
                "لطفاً مجدداً تلاش کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        customer = self.user_sessions[user_id]['customer']
        cart_items = self.cart_manager.get_cart(user_id)

        # Generate final invoice
        discount_rate = self.pricing_manager.discount_rates.get(
            payment_info['payment_type'], 0)
        invoice_text = self.pricing_manager.generate_final_invoice(
            cart_items, customer, payment_info['payment_method'],
            discount_rate)

        # Send to group if configured
        if self.config.order_group_chat_id:
            group_message = (
                f"💳 پرداخت آنلاین تکمیل شده\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 نام مشتری: {customer['name']}\n"
                f"🏙️ شهر: {customer['city']}\n"
                f"🆔 کد نمایندگی: {customer['customer_id']}\n"
                f"📱 یوزرنیم تلگرام: @{query.from_user.username or 'ندارد'}\n"
                f"🆔 شناسه کاربر: {user_id}\n"
                f"💳 روش پرداخت: {payment_info['payment_method']}\n"
                f"💰 مبلغ پرداختی: {format_price(payment_info['amount'])} تومان\n"
                f"⏰ زمان پرداخت: {persian_numbers(datetime.now().strftime('%Y/%m/%d - %H:%M'))}\n\n"
                f"📋 جزئیات سفارش:\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{invoice_text}\n\n"
                f"✅ پرداخت تایید شده - نیاز به پیگیری ارسال")

            # Create admin action buttons for paid orders
            keyboard = [[
                InlineKeyboardButton(
                    "✅ تماس گرفته شد",
                    callback_data=f"order_contacted_{user_id}"),
                InlineKeyboardButton("📦 آماده ارسال",
                                     callback_data=f"order_ready_{user_id}")
            ],
                        [
                            InlineKeyboardButton(
                                "🚚 ارسال شد",
                                callback_data=f"order_shipped_{user_id}"),
                            InlineKeyboardButton(
                                "✅ تکمیل شد",
                                callback_data=f"order_completed_{user_id}")
                        ]]

            try:
                sent_message = await query.bot.send_message(
                    chat_id=self.config.order_group_chat_id,
                    text=group_message,
                    reply_markup=InlineKeyboardMarkup(keyboard))
                logger.info(
                    f"✅ Payment info sent to group {self.config.order_group_chat_id}"
                )
                logger.info(f"Message ID: {sent_message.message_id}")

                # Store order info for tracking
                order_info = {
                    'user_id': user_id,
                    'customer': customer,
                    'message_id': sent_message.message_id,
                    'status': 'paid',
                    'created_at': datetime.now().isoformat()
                }
                self.user_sessions[user_id]['order_info'] = order_info

            except Exception as e:
                logger.error(
                    f"❌ Error sending payment info to group {self.config.order_group_chat_id}: {e}"
                )
                logger.error(f"Error type: {type(e).__name__}")
                # Send error info to customer for debugging
                await query.bot.send_message(
                    chat_id=user_id,
                    text=
                    f"⚠️ پرداخت ثبت شد اما ارسال به گروه با خطا مواجه شد:\n{str(e)[:200]}"
                )
        else:
            logger.warning(
                "❌ Order group chat ID is not configured for payment notification"
            )

        # Clear cart and payment info
        self.cart_manager.clear_cart(user_id)
        if 'payment_info' in self.user_sessions[user_id]:
            del self.user_sessions[user_id]['payment_info']

        text = (
            f"✅ سفارش شما ثبت شد!\n\n"
            f"💳 روش پرداخت: {payment_info['payment_method']}\n"
            f"💰 مبلغ: {format_price(payment_info['amount'])} تومان\n\n"
            f"📞 سفارش شما به گروه پیگیری ارسال شد و به زودی با شما تماس خواهیم گرفت.\n"
            f"🙏 از اعتماد شما متشکریم.")

        await query.edit_message_text(
            text,
            reply_markup=self.keyboards.get_main_menu(authenticated=True))

    async def _handle_payment_verification(self, query):
        """Handle payment verification"""
        user_id = query.from_user.id
        payment_info = self.user_sessions[user_id].get('payment_info')

        if not payment_info:
            await query.edit_message_text(
                "❌ اطلاعات پرداخت یافت نشد.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        # Verify payment with ZarinPal
        verify_result = self.zarinpal.verify_payment(
            authority=payment_info['authority'], amount=payment_info['amount'])

        if verify_result['success']:
            # Payment successful
            customer = self.user_sessions[user_id]['customer']
            cart_items = self.cart_manager.get_cart(user_id)

            # Generate final invoice
            discount_rate = self.pricing_manager.discount_rates[
                payment_info['payment_type']]
            invoice_text = self.pricing_manager.generate_final_invoice(
                cart_items, customer, payment_info['payment_method'],
                discount_rate)

            # Send to group if configured
            if self.config.order_group_chat_id:
                group_message = (
                    f"💳 پرداخت موفق - {payment_info['payment_method']}\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"👤 مشتری: {customer['name']}\n"
                    f"🏙️ شهر: {customer['city']}\n"
                    f"🆔کد نمایندگی : {customer['customer_id']}\n"
                    f"📱 آیدی تلگرام: @{query.from_user.username or 'ندارد'}\n"
                    f"💳 شماره پیگیری: {verify_result['ref_id']}\n\n"
                    f"{invoice_text}")

                try:
                    await query.bot.send_message(
                        chat_id=self.config.order_group_chat_id,
                        text=group_message)
                except Exception as e:
                    logger.error(
                        f"Error sending payment confirmation to group: {e}")

            # Clear cart and payment info
            self.cart_manager.clear_cart(user_id)
            if 'payment_info' in self.user_sessions[user_id]:
                del self.user_sessions[user_id]['payment_info']

            text = (f"✅ پرداخت با موفقیت انجام شد!\n\n"
                    f"💳 شماره پیگیری: {verify_result['ref_id']}\n\n"
                    f"📞 سفارش شما ثبت شد و به زودی با شما تماس خواهیم گرفت.\n"
                    f"🙏 از اعتماد شما متشکریم.")

            await query.edit_message_text(
                text,
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
        else:
            # Payment failed
            text = (f"❌ پرداخت ناموفق بود:\n"
                    f"{verify_result['error']}\n\n"
                    "می‌توانید دوباره تلاش کنید.")

            keyboard = [[
                InlineKeyboardButton(
                    "🔄 تلاش مجدد",
                    callback_data=
                    f"payment_{payment_info['payment_type']}_zarinpal")
            ], [
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")
            ]]

            await query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _handle_cart_clear(self, query):
        """Handle cart clear"""
        user_id = query.from_user.id
        self.cart_manager.clear_cart(user_id)

        text = "🗑️ سبد خرید پاک شد."
        keyboard = self.keyboards.get_main_menu(authenticated=True)

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_back_to_categories(self, query):
        """Handle back to categories"""
        await self._handle_start_shopping(query)

    async def _handle_back_to_alphabet(self, query):
        """Handle back to alphabet"""
        user_id = query.from_user.id
        category = self.user_sessions[user_id].get('selected_category', 'baby')

        text = f"🔤 جستجوی حروف الفبایی\n\nحرف اول نام محصول مورد نظر را انتخاب کنید:"
        keyboard = self.keyboards.get_alphabetical_keyboard(category)

        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_back_to_curtain_subcategories(self, query):
        """Handle back to curtain subcategories"""
        text = "🏠 پرده و کوسن\n\nمحصول مورد نظر خود را انتخاب کنید:"
        keyboard = self.keyboards.get_curtain_subcategories()
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_back_to_products(self, query):
        """Handle back to products"""
        user_id = query.from_user.id
        session = self.user_sessions[user_id]

        if 'selected_product' in session:
            product = session['selected_product']

            # Get price based on category
            category = product.get('category_id', 'baby')
            category_info = get_category_info(category)
            price = category_info.get('price', 4780000)

            text = (f"📦 {product['name']}\n\n"
                    f"💰 قیمت: {format_price(price)} تومان\n\n"
                    "📏 سایز مورد نظر را انتخاب کنید:")

            keyboard = self.keyboards.get_size_selection_keyboard(category)
            await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_alphabet_search(self, query, data):
        """Handle alphabet search button"""
        category = data.replace("alphabet_search_", "")
        user_id = query.from_user.id

        # Store selected category in session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        self.user_sessions[user_id]['selected_category'] = category

        category_info = get_category_info(category)
        category_name = category_info.get('name', category)

        text = f"{category_name}\n\n🔤 جستجوی حروف الفبایی\n\nحرف اول نام محصول مورد نظر را انتخاب کنید:"

        keyboard = self.keyboards.get_alphabetical_keyboard(category)
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_icon_selection(self, query, data):
        """Handle icon-based product selection"""
        parts = data.split("_", 2)
        if len(parts) < 3:
            await query.edit_message_text("❌ خطا در انتخاب آیکون.")
            return

        category = parts[1]
        icon = parts[2]

        # Search products by icon
        products = search_products_by_icon(category, icon)

        if not products:
            await query.edit_message_text("❌ محصولی با این آیکون یافت نشد.")
            return

        if len(products) == 1:
            # Only one product found, select it directly
            product = products[0]
            await self._handle_direct_product_selection(query, product, category)
        else:
            # Multiple products found, show selection keyboard
            keyboard = self.keyboards.get_products_keyboard(products, category)
            await query.edit_message_text(
                f"محصولات مرتبط:",
                reply_markup=keyboard
            )

    async def _handle_payment_confirmed(self, query, data):
        """Handle payment confirmation from the group"""
        # Extract user_id from callback data
        user_id = int(data.split("_")[2])

        # Get customer info
        customer = self.user_sessions[user_id]['customer']

        # Send confirmation to customer
        text = (f"✅ پرداخت شما تایید شد!\n\n"
                f"🙏 از اعتماد شما متشکریم.")

        await query.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=self.keyboards.get_main_menu(authenticated=True))

        # Edit message in group to confirm
        await query.edit_message_text(
            f"✅ پرداخت مشتری {customer['name']} تایید شد.")

    async def _handle_contact_made(self, query, data):
        """Handle contact confirmation from the group"""
        # Extract user_id from callback data
        user_id = int(data.split("_")[2])

        # Get customer info
        customer = self.user_sessions[user_id]['customer']

        # Edit message in group to confirm
        await query.edit_message_text(
            f"📞 تماس با مشتری {customer['name']} برقرار شد.")

    async def _handle_remind_tomorrow(self, query, data):
        """Handle remind tomorrow request from the group"""
        # Extract user_id from callback data
        user_id = int(data.split("_")[2])

        # Get customer info
        customer = self.user_sessions[user_id]['customer']

        # Schedule reminder
        # self.payment_scheduler.schedule_reminder(user_id)

        # Edit message in group to confirm
        await query.edit_message_text(
            f"⏰ یادآوری برای مشتری {customer['name']} برای فردا تنظیم شد.")

    async def _handle_order_contacted(self, query, data):
        """Handle order contacted confirmation"""
        user_id = int(data.split("_")[2])
        admin_name = query.from_user.first_name or "ادمین"

        # Update message
        updated_text = f"📞 {admin_name} با مشتری تماس گرفت\n" + query.message.text

        # Create updated keyboard with remaining options
        keyboard = [[
            InlineKeyboardButton("📦 آماده ارسال",
                                 callback_data=f"order_ready_{user_id}"),
            InlineKeyboardButton("🚚 ارسال شد",
                                 callback_data=f"order_shipped_{user_id}")
        ],
                    [
                        InlineKeyboardButton(
                            "✅ تکمیل شد",
                            callback_data=f"order_completed_{user_id}"),
                        InlineKeyboardButton(
                            "❌ لغو سفارش",
                            callback_data=f"order_cancelled_{user_id}")
                    ]]

        await query.edit_message_text(
            updated_text, reply_markup=InlineKeyboardMarkup(keyboard))

        # Notify customer - improved error handling
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text=
                "📞 کارشناس ما با شما تماس گرفت. سفارش شما در حال پردازش است.")
            logger.info(f"Successfully notified customer {user_id}")
        except Exception as e:
            logger.error(f"Error notifying customer {user_id}: {e}")
            # Continue processing even if customer notification fails

    async def _handle_order_ready(self, query, data):
        """Handle order ready for shipping"""
        user_id = int(data.split("_")[2])
        admin_name = query.from_user.first_name or "ادمین"

        updated_text = f"📦 {admin_name}: سفارش آماده ارسال شد\n" + query.message.text

        keyboard = [[
            InlineKeyboardButton("🚚 ارسال شد",
                                 callback_data=f"order_shipped_{user_id}"),
            InlineKeyboardButton("✅ تکمیل شد",
                                 callback_data=f"order_completed_{user_id}")
        ]]

        await query.edit_message_text(
            updated_text, reply_markup=InlineKeyboardMarkup(keyboard))

        # Notify customer - improved error handling
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text="📦 سفارش شما آماده و به زودی ارسال خواهد شد!")
            logger.info(f"Successfully notified customer {user_id}")
        except Exception as e:
            logger.error(f"Error notifying customer {user_id}: {e}")
            # Continue processing even if customer notification fails

    async def _handle_order_shipped(self, query, data):
        """Handle order shipped"""
        user_id = int(data.split("_")[2])
        admin_name = query.from_user.first_name or "ادمین"

        updated_text = f"🚚 {admin_name}: سفارش ارسال شد\n" + query.message.text

        keyboard = [[
            InlineKeyboardButton("✅ تکمیل شد",
                                 callback_data=f"order_completed_{user_id}")
        ]]

        await query.edit_message_text(
            updated_text, reply_markup=InlineKeyboardMarkup(keyboard))

        # Notify customer - improved error handling
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text="🚚 سفارش شما ارسال شد! به زودی دریافت خواهید کرد.")
            logger.info(f"Successfully notified customer {user_id}")
        except Exception as e:
            logger.error(f"Error notifying customer {user_id}: {e}")
            # Continue processing even if customer notification fails

    async def _handle_order_completed(self, query, data):
        """Handle order completion"""
        user_id = int(data.split("_")[2])
        admin_name = query.from_user.first_name or "ادمین"

        updated_text = f"✅ {admin_name}: سفارش تکمیل شد\n" + query.message.text

        await query.edit_message_text(updated_text)

        # Notify customer - improved error handling
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text=
                "✅ سفارش شما با موفقیت تکمیل شد!\n🙏 از اعتماد شما متشکریم. امیدواریم از خرید خود راضی باشید."
            )
            logger.info(f"Successfully notified customer {user_id}")
        except Exception as e:
            logger.error(f"Error notifying customer {user_id}: {e}")
            # Continue processing even if customer notification fails

    async def _handle_order_cancelled(self, query, data):
        """Handle order cancellation"""
        user_id = int(data.split("_")[2])
        admin_name = query.from_user.first_name or "ادمین"

        updated_text = f"❌ {admin_name}: سفارش لغو شد\n" + query.message.text

        await query.edit_message_text(updated_text)

        # Notify customer - improved error handling
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text=
                "❌ متأسفانه سفارش شما لغو شد.\n📞 برای اطلاعات بیشتر با پشتیبانی تماس بگیرید."
            )
            logger.info(f"Successfully notified customer {user_id}")
        except Exception as e:
            logger.error(f"Error notifying customer {user_id}: {e}")
            # Continue processing even if customer notification fails

    async def _handle_order_reminder(self, query, data):
        """Handle order reminder for tomorrow"""
        user_id = int(data.split("_")[2])
        admin_name = query.from_user.first_name or "ادمین"

        updated_text = f"⏰ {admin_name}: یادآوری فردا تنظیم شد\n" + query.message.text

        # Keep all original buttons
        keyboard = [[
            InlineKeyboardButton("✅ تماس گرفته شد",
                                 callback_data=f"order_contacted_{user_id}"),
            InlineKeyboardButton("📦 آماده ارسال",
                                 callback_data=f"order_ready_{user_id}")
        ],
                    [
                        InlineKeyboardButton(
                            "🚚 ارسال شد",
                            callback_data=f"order_shipped_{user_id}"),
                        InlineKeyboardButton(
                            "✅ تکمیل شد",
                            callback_data=f"order_completed_{user_id}")
                    ],
                    [
                        InlineKeyboardButton(
                            "❌ لغو سفارش",
                            callback_data=f"order_cancelled_{user_id}")
                    ]]

        await query.edit_message_text(
            updated_text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def _handle_order_status_update(self, query, data):
        """Handle order status update from admin"""
        try:
            logger.info(f"🔄 شروع پردازش تغییر وضعیت: {data}")
            
            # Parse callback data: order_status_ORDER_ID_STATUS
            parts = data.split("_")
            if len(parts) < 4:
                logger.error(f"❌ فرمت داده نامعتبر: {data}")
                await query.answer("❌ داده نامعتبر", show_alert=True)
                return

            order_id = parts[2]
            new_status = parts[3]
            admin_name = query.from_user.first_name or "ادمین"

            logger.info(f"📋 پردازش سفارش {order_id} به وضعیت {new_status} توسط {admin_name}")

            # ابتدا پاسخ سریع به کاربر بده
            await query.answer("🔄 در حال پردازش...")

            # بررسی وجود سفارش
            order_data = await self.order_server.get_order_details(order_id)
            if not order_data:
                logger.error(f"❌ سفارش {order_id} یافت نشد")
                await query.answer("❌ سفارش یافت نشد", show_alert=True)
                return

            # Update order status با ارسال اطلاع‌رسانی به مشتری
            success = await self.order_server.update_order_status(
                order_id=order_id,
                new_status=new_status,
                admin_name=admin_name
            )

            if success:
                logger.info(f"✅ وضعیت سفارش {order_id} با موفقیت تغییر کرد")
                status_text = self.order_server._get_status_text(new_status)
                
                # به‌روزرسانی پیام گروه
                try:
                    current_text = query.message.text or ""
                    updated_text = f"📝 {admin_name}: وضعیت به '{status_text}' تغییر کرد\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{current_text}"

                    # ایجاد کیبورد جدید
                    keyboard = self.order_server._create_admin_buttons(order_id, order_data['user_id'])

                    await query.edit_message_text(
                        updated_text,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    logger.info(f"✅ پیام گروه به‌روزرسانی شد و اطلاع‌رسانی به مشتری ارسال شد")
                    
                except Exception as edit_error:
                    logger.error(f"❌ خطا در به‌روزرسانی پیام گروه: {edit_error}")
                    # ارسال پیام جدید در صورت خطا در ویرایش
                    try:
                        confirmation_message = f"✅ وضعیت سفارش {order_id} به '{status_text}' تغییر کرد توسط {admin_name}"
                        await query.message.reply_text(confirmation_message)
                        logger.info(f"✅ پیام جدید ارسال شد")
                    except Exception as reply_error:
                        logger.error(f"❌ خطا در ارسال پیام جدید: {reply_error}")
                        
            else:
                logger.error(f"❌ خطا در به‌روزرسانی وضعیت سفارش {order_id}")
                await query.answer("❌ خطا در به‌روزرسانی وضعیت", show_alert=True)

        except Exception as e:
            logger.error(f"❌ خطای کلی در _handle_order_status_update: {e}")
            logger.error(f"   Data: {data}")
            logger.error(f"   User: {query.from_user.first_name if query.from_user else 'Unknown'}")
            
            try:
                await query.answer(f"❌ خطا در پردازش: {str(e)[:30]}", show_alert=True)
            except Exception as msg_error:
                logger.error(f"❌ خطا در ارسال پیام خطا: {msg_error}")

    

    async def _handle_order_details_request(self, query, data):
        """Handle request for order details"""
        try:
            order_id = data.replace("order_details_", "")
            order_data = await self.order_server.get_order_details(order_id)

            if not order_data:
                await query.answer("❌ سفارش یافت نشد")
                return

            # Create detailed invoice message
            customer = order_data.get('customer', {})
            pricing = order_data.get('pricing', {})
            cart_items = order_data.get('cart_items', [])
            
            invoice_text = (
                f"📋 فاکتور - {order_id}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 {customer.get('name', 'نامشخص')}\n"
                f"🏙️ {customer.get('city', 'نامشخص')}\n"
                f"🆔 کد نمایندگی: {customer.get('customer_id', 'نامشخص')}\n"
                f"📱 شناسه کاربر: {order_data.get('user_id', 'نامشخص')}\n"
                f"⏰ {persian_numbers(order_data.get('created_at', '')[:16].replace('T', ' - '))}\n\n"
                f"📦 آیتم‌ها:\n"
            )

            # Add cart items
            for i, item in enumerate(cart_items, 1):
                item_total = item.get('price', 0) * item.get('quantity', 0)
                invoice_text += (
                    f"{persian_numbers(str(i))}. {item.get('product_name', 'محصول')}\n"
                    f"   📏 {item.get('size', 'نامشخص')} | "
                    f"📦 {persian_numbers(str(item.get('quantity', 0)))} عدد | "
                    f"💰 {format_price(item_total)}\n"
                )

            # Add pricing
            invoice_text += (
                f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💳 {order_data.get('payment_method', 'نقدی')}\n"
                f"💰 مبلغ کل: {format_price(pricing.get('total', 0))} تومان\n"
                f"📊 {self.order_server._get_status_text(order_data.get('status', 'pending'))}"
            )

            # Create management keyboard
            keyboard = self.order_server._create_admin_buttons(order_id, order_data['user_id'])
            keyboard.append([InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_to_daily_orders")])

            await query.edit_message_text(
                invoice_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error showing order details: {e}")
            await query.answer("❌ خطا در نمایش جزئیات")

    async def _handle_daily_stats_request(self, query):
        """Handle daily statistics request"""
        try:
            stats = await self.order_server.get_orders_statistics()
            today_orders = await self.order_server.get_todays_orders()

            stats_text = (
                f"📊 آمار امروز ({persian_numbers(datetime.now().strftime('%Y/%m/%d'))})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 سفارشات امروز: {persian_numbers(str(len(today_orders)))}\n"
                f"💰 درآمد امروز: {format_price(stats.get('today_revenue', 0))} تومان\n\n"
                f"📈 آمار کلی:\n"
                f"📦 کل سفارشات: {persian_numbers(str(stats.get('total_orders', 0)))}\n"
                f"💳 کل درآمد: {format_price(stats.get('total_revenue', 0))} تومان\n"
            )

            keyboard = [[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_daily_orders")
            ]]

            await query.edit_message_text(
                stats_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error showing daily stats: {e}")
            await query.answer("❌ خطا در نمایش آمار")

    async def _handle_refresh_daily_orders(self, query):
        """Handle refresh daily orders request"""
        await query.answer("🔄 در حال بروزرسانی...")

        # Create a fake update object to reuse the _show_daily_orders method
        class FakeUpdate:
            def __init__(self, message):
                self.message = message

        fake_update = FakeUpdate(query.message)
        await self._show_daily_orders(fake_update)

    async def _handle_back_to_daily_orders(self, query):
        """Handle back to daily orders list"""
        # Create a fake update object to reuse the _show_daily_orders method
        class FakeUpdate:
            def __init__(self, message):
                self.message = message

        fake_update = FakeUpdate(query.message)
        await self._show_daily_orders(fake_update)

    async def _handle_contact_customer_request(self, query, data):
        """Handle request to contact customer"""
        try:
            user_id = int(data.replace("contact_customer_", ""))

            contact_message = (
                f"📞 درخواست تماس با مشتری\n"
                f"🆔 شناسه کاربر: {user_id}\n\n"
                f"لطفاً از طریق تلفن یا پیام مستقیم با مشتری تماس بگیرید."
            )

            await query.answer("✅ اطلاعات تماس نمایش داده شد")
            await query.message.reply_text(contact_message)

        except Exception as e:
            logger.error(f"Error handling contact request: {e}")
            await query.answer("❌ خطا در پردازش درخواست")

    async def _handle_check_order_status(self, query, data):
        """Handle customer's request to check order status"""
        try:
            order_id = data.replace("check_order_status_", "")
            order_data = await self.order_server.get_order_details(order_id)

            if not order_data:
                await query.edit_message_text(
                    "❌ سفارش یافت نشد.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")
                    ]]))
                return

            status_text = self.order_server._get_status_text(order_data["status"])
            last_update = datetime.fromisoformat(order_data["updated_at"]).strftime("%Y/%m/%d - %H:%M")

            status_message = (
                f"📋 وضعیت سفارش شماره: {order_id}\n\n"
                f"📊 وضعیت فعلی: {status_text}\n"
                f"⏰ آخرین به‌روزرسانی: {persian_numbers(last_update)}\n"
                f"💳 روش پرداخت: {order_data['payment_method']}\n"
                f"💰 مبلغ کل: {format_price(order_data['pricing']['total'])} تومان"
            )

            keyboard = self.order_server._create_customer_support_buttons(order_id)

            await query.edit_message_text(
                status_message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error checking order status: {e}")
            await query.edit_message_text("❌ خطا در بررسی وضعیت سفارش")

    async def _handle_payment_confirmation_from_group(self, query, data):
        """Handle payment confirmation from the payment reminder group"""
        try:
            # Extract schedule_id and payment_number from callback data
            parts = data.split("_")
            schedule_id = parts[2]
            payment_number = int(parts[3])

            # Mark payment as made
            success = self.payment_scheduler.mark_payment_made(schedule_id, payment_number)

            if success:
                await query.edit_message_text(
                    query.message.text + "\n\n✅ پرداخت تایید شد"
                )
                await query.answer("✅ پرداخت با موفقیت ثبت شد!")
            else:
                await query.answer("❌ خطا در ثبت پرداخت")

        except Exception as e:
            logger.error(f"Error handling payment confirmation: {e}")
            await query.answer("❌ خطا در پردازش درخواست")

    async def _handle_contact_made_from_group(self, query, data):
        """Handle contact made confirmation from the payment reminder group"""
        try:
            admin_name = query.from_user.first_name or "ادمین"

            await query.edit_message_text(
                query.message.text + f"\n\n📞 {admin_name} با مشتری تماس گرفت"
            )
            await query.answer("✅ تماس ثبت شد")

        except Exception as e:
            logger.error(f"Error handling contact confirmation: {e}")
            await query.answer("❌ خطا در پردازش درخواست")

    async def _handle_remind_tomorrow_from_group(self, query, data):
        """Handle remind tomorrow request from the payment reminder group"""
        try:
            admin_name = query.from_user.first_name or "ادمین"

            await query.edit_message_text(
                query.message.text + f"\n\n⏰ {admin_name} یادآوری فردا تنظیم کرد"
            )
            await query.answer("⏰ یادآوری برای فردا تنظیم شد")

        except Exception as e:
            logger.error(f"Error handling remind tomorrow: {e}")
            await query.answer("❌ خطا در پردازش درخواست")

    async def _handle_contact_support_request(self, query):
        """Handle customer's request to contact support"""
        user_id = query.from_user.id
        await self.order_server.send_support_contact_info(user_id)
        await query.answer("📞 اطلاعات تماس ارسال شد")

    async def _handle_faq_request(self, query):
        """Handle customer's request for FAQ"""
        user_id = query.from_user.id
        await self.order_server.send_faq(user_id)
        await query.answer("❓ سوالات متداول ارسال شد")

    async def _handle_fabric_selection(self, query, data):
        """Handle fabric selection for curtains"""
        fabric = data.replace("fabric_", "")
        user_id = query.from_user.id

        # Store selected fabric in session
        self.user_sessions[user_id]['selected_fabric'] = fabric
        category = 'curtain_only'
        self.user_sessions[user_id]['selected_category'] = category

        # Get price based on fabric
        price = get_product_price('', category, fabric=fabric)

        fabric_name = "حریر کتان" if fabric == "silk_cotton" else "مخمل"

        text = (f"✅ جنس انتخابی: {fabric_name}\n"
                f"💰 قیمت: {format_price(price)} تومان\n\n"
                "عالیه! انتخابت. عرض پرده‌ها همیشه ثابت هست برای ایکون پرده سرتخت 135 هست و ارتفاع از 2 متر به بالا متغیر. پس ارتفاع مد نظرتو تایپ کن برام:")

        # Set flag for height input
        self.user_sessions[user_id]['awaiting_curtain_height'] = True

        keyboard = self.keyboards.get_height_input_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_curtain_height_input(self, update, height_text):
        """Handle curtain height input"""
        user_id = update.effective_user.id

        try:
            # Parse height (should be a number)
            height = float(height_text)
            if height < 2:
                await update.message.reply_text(
                    "❌ ارتفاع باید حداقل 2 متر باشد. لطفاً دوباره وارد کنید:")
                return

            # Store height and clear input flag
            self.user_sessions[user_id]['selected_height'] = height
            self.user_sessions[user_id]['awaiting_curtain_height'] = False

            # Create custom size string for curtains
            size = f"عرض: 135 - ارتفاع: {height}م"
            self.user_sessions[user_id]['selected_size'] = size

            # Get price based on fabric
            fabric = self.user_sessions[user_id]['selected_fabric']
            category = self.user_sessions[user_id]['selected_category']

            if fabric == 'special':  # For bedside curtain
                product = self.user_sessions[user_id]['selected_product']
                price = get_product_price(product['id'], category)
            else:
                price = get_product_price('', category, fabric=fabric)

            text = (f"✅ ارتفاع انتخابی: {height} متر\n"
                    f"💰 قیمت: {format_price(price)} تومان\n\n"
                    "حالا پردت چند قواره باشه؟")

            keyboard = self.keyboards.get_quantity_keyboard()
            await update.message.reply_text(text, reply_markup=keyboard)

        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً ارتفاع را به صورت عدد وارد کنید (مثال: 2.5):")

    async def _handle_back_to_fabric_selection(self, query):
        """Handle back to fabric selection"""
        user_id = query.from_user.id

        # Clear height input flag
        if 'awaiting_curtain_height' in self.user_sessions[user_id]:
            del self.user_sessions[user_id]['awaiting_curtain_height']

        product = self.user_sessions[user_id].get('selected_product')
        if product:
            text = (f"📦 {product['name']}\n\n"
                    "عالیه! مدل پرده‌ای که انتخاب کردی. حالا جنس پارچش چی باشه؟")
            keyboard = self.keyboards.get_fabric_selection_keyboard()
            await query.edit_message_text(text, reply_markup=keyboard)

    async def _handle_order_actions(self, query, data):
        """Optimized handler for all order-related actions"""
        try:
            if data.startswith("order_contacted_"):
                await self._handle_order_contacted(query, data)
            elif data.startswith("order_ready_"):
                await self._handle_order_ready(query, data)
            elif data.startswith("order_shipped_"):
                await self._handle_order_shipped(query, data)
            elif data.startswith("order_completed_"):
                await self._handle_order_completed(query, data)
            elif data.startswith("order_cancelled_"):
                await self._handle_order_cancelled(query, data)
            elif data.startswith("order_remind_"):
                await self._handle_order_reminder(query, data)
            else:
                logger.warning(f"Unhandled order action: {data}")
                await query.answer("درحال پردازش...")
        except Exception as e:
            logger.error(f"Order action error: {e}")
            try:
                await query.answer("❌ خطا در پردازش سفارش.")
            except:
                pass

    def _is_authenticated(self, user_id: int) -> bool:
        """Check if user is authenticated"""
        return (user_id in self.user_sessions
                and self.user_sessions[user_id].get('authenticated', False))

    async def test_group_connection(self, bot):
        """Test if bot can send messages to the configured group"""
        logger.info("🔍 Testing group connection...")

        if not self.config.order_group_chat_id:
            logger.warning("❌ Order group chat ID is not configured")
            return False

        try:
            # Try to get chat info
            chat = await bot.get_chat(self.config.order_group_chat_id)
            logger.info(f"✅ Group connection successful!")
            logger.info(f"   Title: {chat.title}")
            logger.info(f"   Type: {chat.type}")
            logger.info(f"   ID: {chat.id}")

            return True
        except Exception as e:
            logger.warning(f"⚠️ Group connection test failed: {e}")
            logger.info("   Note: This is normal during startup - bot will work fine")
            return False

    async def get_current_chat_info(self, bot, chat_id):
        """Get detailed info about current chat for debugging"""
        try:
            chat = await bot.get_chat(chat_id)
            logger.info(f"💬 Chat Info:")
            logger.info(f"   ID: {chat.id}")
            logger.info(f"   Title: {chat.title}")
            logger.info(f"   Type: {chat.type}")
            logger.info(f"   Description: {getattr(chat, 'description', 'N/A')}")
            return chat
        except Exception as e:
            logger.error(f"Error getting chat info: {e}")
            return None


    async def _send_invoice_to_group(self, invoice_text, user_id):
        """Send invoice to group after order completion"""
        group_chat_id = self.config.order_group_chat_id
        if not group_chat_id:
            logger.error("Group chat ID not configured.")
            return

        try:
            # Note: self.bot is not available in handlers, we need to get it from context
            logger.info(f"Invoice sent to group {group_chat_id} for user {user_id}.")
        except Exception as e:
            logger.error(f"Failed to send invoice to group: {e}")

    async def _handle_60day_order_confirmation(self, query):
        """Handle confirmation for 60-day payment orders."""
        user_id = query.from_user.id

        if not self._is_authenticated(user_id):
            await query.edit_message_text("❌ ابتدا باید احراز هویت کنید.")
            return

        payment_info = self.user_sessions[user_id].get('payment_info')
        if not payment_info or payment_info['payment_type'] != '60day':
            await query.edit_message_text(
                "❌ اطلاعات سفارش 60 روزه یافت نشد. لطفاً دوباره تلاش کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))
            return

        customer = self.user_sessions[user_id]['customer']
        cart_items = self.cart_manager.get_cart(user_id)

        # Schedule the 60-day payment reminder
        total_amount = payment_info['full_amount']
        advance_paid = payment_info['amount']
        remaining_amount = total_amount - advance_paid
        order_id = f"ORDER_{user_id}_{int(datetime.now().timestamp())}"

        self.payment_scheduler.add_60day_payment_schedule(
            user_id=user_id,
            customer_info=customer,
            total_amount=total_amount,
            advance_paid=advance_paid,
            remaining_amount=remaining_amount,
            order_id=order_id
        )
        logger.info(f"✅ برنامه پرداخت 60 روزه برای کاربر {user_id} تنظیم شد")

        try:
            # Create order using order management server
            order_id = await self.order_server.create_order(
                user_id=user_id,
                customer=customer,
                cart_items=cart_items,
                payment_method=payment_info['payment_method'],
                discount_rate=payment_info['discount_rate']
            )

            # Clear cart and payment info
            self.cart_manager.clear_cart(user_id)
            if 'payment_info' in self.user_sessions[user_id]:
                del self.user_sessions[user_id]['payment_info']

            # Confirm to customer
            await query.edit_message_text(
                f"✅ سفارش شما با موفقیت ثبت شد!\n"
                f"📋 شماره سفارش: {order_id}\n"
                f"💳 روش پرداخت: {payment_info['payment_method']}\n"
                f"📅 یادآوری ماهانه برای پیگیری مابقی پرداخت فعال شد.\n"
                f"📞 کارشناسان ما به زودی با شما تماس خواهند گرفت.\n"
                f"🙏 از اعتماد شما ممنونیم.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))

            logger.info(f"✅ سفارش 60 روزه {order_id} با موفقیت ثبت شد برای کاربر {user_id}")

        except Exception as e:
            logger.error(f"Error in 60-day order confirmation: {e}")
            await query.edit_message_text(
                "❌ خطایی در ثبت سفارش رخ داد. لطفاً دوباره تلاش کنید.",
                reply_markup=self.keyboards.get_main_menu(authenticated=True))