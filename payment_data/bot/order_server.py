#!/usr/bin/env python3
"""
Order Management Server
سرور مدیریت و پیگیری سفارشات
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import Config
from bot.pricing import PricingManager
from bot.hesabfa_integration import HesabfaAPI
from utils.logger import setup_logger
from utils.persian_utils import format_price, persian_numbers

logger = setup_logger(__name__)

class OrderStatus:
    """وضعیت‌های مختلف سفارش"""
    PENDING = "pending"           # در انتظار
    CONTACTED = "contacted"       # تماس گرفته شد
    CONFIRMED = "confirmed"       # تایید شد
    PREPARING = "preparing"       # در حال آماده‌سازی
    READY = "ready"              # آماده ارسال
    SHIPPED = "shipped"          # ارسال شد
    DELIVERED = "delivered"      # تحویل داده شد
    COMPLETED = "completed"      # تکمیل شد
    CANCELLED = "cancelled"      # لغو شد

class OrderManagementServer:
    """سرور مدیریت سفارشات"""

    def __init__(self):
        self.config = Config()
        self.pricing_manager = PricingManager()
        self.hesabfa_api = HesabfaAPI()
        self.orders_dir = "order_data"
        self.bot = None

        # ایجاد دایرکتوری سفارشات
        os.makedirs(self.orders_dir, exist_ok=True)

        # پیام‌های وضعیت برای مشتری
        self.status_messages = {
            OrderStatus.PENDING: "📋 سفارش شما ثبت شد و در حال بررسی است.",
            OrderStatus.CONTACTED: "🔄 سفارش شما توسط تیم پشتیبانی دکوتین درحال آماده سازی است.",
            OrderStatus.CONFIRMED: "✅ عالیه! سفارش شما توسط تیم پشتیبانی دکوتین تایید شد.\n🏦 پیش‌فاکتور شما در سیستم حسابداری ثبت شد.\n📞 به زودی برای هماهنگی ارسال با شما تماس خواهیم گرفت.",
            OrderStatus.PREPARING: "🔧 سفارش شما در حال آماده‌سازی است.",
            OrderStatus.READY: "📦 سفارش شما آماده ارسال شد!",
            OrderStatus.SHIPPED: "🚚 از انتخاب شما برای خرید از مجموعه دکوتین ممنونیم و سفارش شما ارسال شد.",
            OrderStatus.DELIVERED: "✅ سفارش شما تحویل داده شد.",
            OrderStatus.COMPLETED: "🎉 کاربر گرامی سفارش شما تکمیل شده و در صف ارسال میباشد.",
            OrderStatus.CANCELLED: ""  # پیام خاص در متد جداگانه
        }

    def set_bot(self, bot: Bot):
        """تنظیم bot instance"""
        self.bot = bot

    def _get_order_file_path(self, order_id: str) -> str:
        """مسیر فایل سفارش"""
        return os.path.join(self.orders_dir, f"order_{order_id}.json")

    def _generate_order_id(self, user_id: int) -> str:
        """ایجاد شناسه یکتای سفارش"""
        # ایجاد شماره سفارش ساده
        counter_file = os.path.join(self.orders_dir, "order_counter.txt")

        try:
            # خواندن شماره فعلی
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    counter = int(f.read().strip())
            else:
                counter = 0

            # افزایش شماره
            counter += 1

            # ذخیره شماره جدید
            with open(counter_file, 'w') as f:
                f.write(str(counter))

            return f"{counter:05d}"  # شماره 5 رقمی: 00001, 00002, ...

        except Exception as e:
            logger.error(f"خطا در ایجاد شماره سفارش: {e}")
            # fallback to timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            return f"ORD{timestamp}"

    async def create_order(self, user_id: int, customer: Dict, cart_items: List[Dict], 
                          payment_method: str, discount_rate: float = 0, receipt_photo_id: str = None) -> str:
        """ایجاد سفارش جدید"""
        try:
            order_id = self._generate_order_id(user_id)

            # محاسبه قیمت‌ها
            subtotal = self.pricing_manager.calculate_subtotal(cart_items)
            discount = self.pricing_manager.calculate_discount(subtotal, discount_rate)
            tax = self.pricing_manager.calculate_tax(subtotal - discount)
            total = subtotal - discount + tax

            # ایجاد سفارش
            order_data = {
                "order_id": order_id,
                "user_id": user_id,
                "customer": customer,
                "cart_items": cart_items,
                "payment_method": payment_method,
                "pricing": {
                    "subtotal": subtotal,
                    "discount_rate": discount_rate,
                    "discount": discount,
                    "tax": tax,
                    "total": total
                },
                "status": OrderStatus.PENDING,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status_history": [
                    {
                        "status": OrderStatus.PENDING,
                        "timestamp": datetime.now().isoformat(),
                        "note": "سفارش ایجاد شد"
                    }
                ]
            }

            # ذخیره سفارش
            await self._save_order(order_data)

            # ارسال پیش‌فاکتور به گروه پشتیبانی
            await self._send_invoice_to_support_group(order_data, receipt_photo_id)

            # اطلاع‌رسانی به مشتری
            await self._notify_customer(user_id, OrderStatus.PENDING, order_id)

            logger.info(f"سفارش جدید ایجاد شد: {order_id}")
            return order_id

        except Exception as e:
            logger.error(f"خطا در ایجاد سفارش: {e}")
            raise

    async def _save_order(self, order_data: Dict):
        """ذخیره سفارش در فایل"""
        order_file = self._get_order_file_path(order_data["order_id"])

        try:
            with open(order_file, 'w', encoding='utf-8') as f:
                json.dump(order_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطا در ذخیره سفارش: {e}")
            raise

    async def _send_invoice_to_support_group(self, order_data: Dict, receipt_photo_id: str = None):
        """ارسال پیش‌فاکتور به گروه پشتیبانی"""
        if not self.bot:
            logger.warning("❌ Bot instance تنظیم نشده است")
            return

        if not self.config.order_group_chat_id:
            logger.warning("❌ گروه پشتیبانی تنظیم نشده است")
            return

        try:
            # بررسی دسترسی به گروه
            try:
                chat_info = await self.bot.get_chat(self.config.order_group_chat_id)
                logger.info(f"✅ دسترسی به گروه تایید شد: {chat_info.title}")
            except Exception as chat_error:
                logger.error(f"❌ عدم دسترسی به گروه {self.config.order_group_chat_id}: {chat_error}")
                return

            # ایجاد پیش‌فاکتور
            invoice_text = self._generate_invoice_text(order_data)

            # دکمه‌های مدیریت سفارش
            keyboard = self._create_admin_buttons(order_data["order_id"], order_data["user_id"])

            # اگر عکس فیش وجود دارد، ابتدا آن را ارسال کن
            if receipt_photo_id:
                try:
                    photo_message = await self.bot.send_photo(
                        chat_id=self.config.order_group_chat_id,
                        photo=receipt_photo_id,
                        caption="📸 فیش واریزی مشتری"
                    )
                    logger.info(f"✅ عکس فیش ارسال شد - Message ID: {photo_message.message_id}")
                except Exception as photo_error:
                    logger.error(f"❌ خطا در ارسال عکس فیش: {photo_error}")
                    # ادامه دادن حتی اگر عکس ارسال نشود

            # ارسال فاکتور به گروه
            sent_message = await self.bot.send_message(
                chat_id=self.config.order_group_chat_id,
                text=invoice_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            logger.info(f"✅ پیش‌فاکتور سفارش {order_data['order_id']} به گروه ارسال شد")
            logger.info(f"   Group ID: {self.config.order_group_chat_id}")
            logger.info(f"   Message ID: {sent_message.message_id}")

        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیش‌فاکتور به گروه: {e}")
            logger.error(f"   Order ID: {order_data.get('order_id', 'Unknown')}")
            logger.error(f"   Group ID: {self.config.order_group_chat_id}")
            logger.error(f"   Error type: {type(e).__name__}")

            # ارسال اطلاعات بیشتر برای دیباگ
            if hasattr(e, 'message'):
                logger.error(f"   Error message: {e.message}")

            # حتی اگر ارسال به گروه ناموفق باشد، ادامه پردازش

    def _generate_invoice_text(self, order_data: Dict) -> str:
        """تولید متن پیش‌فاکتور"""
        customer = order_data["customer"]
        cart_items = order_data["cart_items"]
        pricing = order_data["pricing"]

        invoice_text = (
            f"🆕 سفارش جدید - شماره: {order_data['order_id']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 نام مشتری: {customer['name']}\n"
            f"🏙️ شهر: {customer['city']}\n"
            f"🆔 کد نمایندگی: {customer['customer_id']}\n"
            f"📱 شناسه کاربر: {order_data['user_id']}\n"
            f"💳 روش پرداخت: {order_data['payment_method']}\n"
            f"⏰ زمان ثبت: {persian_numbers('1404/05/14')} - {persian_numbers(datetime.fromisoformat(order_data['created_at']).strftime('%H:%M'))}\n\n"
            f"📋 جزئیات سفارش:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        # آیتم‌های سفارش
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_text += (
                f"{persian_numbers(str(i))}. {item['product_name']}\n"
                f"   📏 سایز: {item['size']}\n"
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}\n"
                f"   💰 قیمت: {format_price(item_total)} تومان\n\n"
            )

        # جمع‌بندی قیمت
        invoice_text += (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 جمع کل: {format_price(pricing['subtotal'])} تومان\n"
        )

        if pricing['discount'] > 0:
            invoice_text += f"🎁 تخفیف ({persian_numbers(str(int(pricing['discount_rate'] * 100)))}٪): {format_price(pricing['discount'])} تومان\n"

        invoice_text += (
            f"📊 مالیات (۹٪): {format_price(pricing['tax'])} تومان\n"
            f"💳 مبلغ نهایی: {format_price(pricing['total'])} تومان\n\n"
            f"📌 وضعیت: {self._get_status_text(order_data['status'])}"
        )
        
        # اضافه کردن اطلاعات حسابفا در صورت وجود
        if order_data.get("hesabfa_invoice_id"):
            invoice_text += (
                f"\n\n🏦 اطلاعات حسابفا:\n"
                f"📋 شماره فاکتور: {order_data.get('hesabfa_invoice_number', 'نامشخص')}\n"
                f"🆔 شناسه فاکتور: {order_data.get('hesabfa_invoice_id')}"
            )

        return invoice_text

    def _create_admin_buttons(self, order_id: str, user_id: int) -> List[List[InlineKeyboardButton]]:
        """ایجاد دکمه‌های مدیریت برای ادمین (ساده شده)"""
        return [
            [
                InlineKeyboardButton("✅ تایید سفارش", callback_data=f"order_status_{order_id}_confirmed"),
                InlineKeyboardButton("🔄 در حال پیگیری", callback_data=f"order_status_{order_id}_contacted")
            ],
            [
                InlineKeyboardButton("🚚 سفارش ارسال شد", callback_data=f"order_status_{order_id}_shipped"),
                InlineKeyboardButton("🎉 سفارش تکمیل شد", callback_data=f"order_status_{order_id}_completed")
            ],
            [
                InlineKeyboardButton("❌ لغو سفارش", callback_data=f"order_status_{order_id}_cancelled")
            ]
        ]

    async def update_order_status(self, order_id: str, new_status: str, admin_name: str = "ادمین", note: str = "") -> bool:
        """به‌روزرسانی وضعیت سفارش"""
        try:
            logger.info(f"🔄 شروع به‌روزرسانی وضعیت سفارش {order_id} به {new_status}")
            
            # بارگیری سفارش
            order_data = await self._load_order(order_id)
            if not order_data:
                logger.error(f"❌ سفارش یافت نشد: {order_id}")
                return False

            # به‌روزرسانی وضعیت
            old_status = order_data["status"]
            order_data["status"] = new_status
            order_data["updated_at"] = datetime.now().isoformat()

            # اضافه کردن به تاریخچه
            status_entry = {
                "status": new_status,
                "timestamp": datetime.now().isoformat(),
                "admin": admin_name,
                "note": note or f"وضعیت از {self._get_status_text(old_status)} به {self._get_status_text(new_status)} تغییر کرد"
            }
            order_data["status_history"].append(status_entry)

            # ابتدا وضعیت را ذخیره کن تا در صورت خطای حسابفا، کار ادامه یابد
            await self._save_order(order_data)
            logger.info(f"✅ وضعیت سفارش {order_id} ذخیره شد")

            # ثبت پیش‌فاکتور در حسابفا هنگام تایید سفارش (به صورت غیرهمزمان)
            if new_status == OrderStatus.CONFIRMED and not order_data.get("hesabfa_invoice_id"):
                logger.info(f"🔄 شروع ثبت پیش‌فاکتور در حسابفا برای سفارش {order_id}")
                
                # اجرای غیرهمزمان حسابفا برای جلوگیری از blocking
                import asyncio
                asyncio.create_task(self._process_hesabfa_invoice(order_id, order_data))

            # اطلاع‌رسانی مستقیم به مشتری
            user_id = order_data["user_id"]
            if user_id and self.bot:
                try:
                    await self._notify_customer(user_id, new_status, order_id, admin_name)
                    logger.info(f"✅ اطلاع‌رسانی به مشتری {user_id} ارسال شد")
                except Exception as notify_error:
                    logger.error(f"❌ خطا در اطلاع‌رسانی به مشتری: {notify_error}")
                    # اجرای غیرهمزمان در صورت خطا
                    import asyncio
                    asyncio.create_task(self._notify_customer_async(user_id, new_status, order_id, admin_name))

            logger.info(f"✅ وضعیت سفارش {order_id} به {new_status} تغییر کرد")
            return True

        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی وضعیت سفارش {order_id}: {e}")
            logger.error(f"   خطا: {str(e)}")
            return False

    async def _load_order(self, order_id: str) -> Optional[Dict]:
        """بارگیری سفارش از فایل"""
        order_file = self._get_order_file_path(order_id)

        try:
            if os.path.exists(order_file):
                with open(order_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"خطا در بارگیری سفارش {order_id}: {e}")
            return None

    async def _process_hesabfa_invoice(self, order_id: str, order_data: Dict):
        """پردازش فاکتور حسابفا به صورت غیرهمزمان"""
        try:
            logger.info(f"🔄 شروع پردازش فاکتور حسابفا برای سفارش {order_id}")
            
            # ابتدا مخاطب را ایجاد کن (در صورت عدم وجود)
            contact_result = await self.hesabfa_api.create_contact_if_not_exists(order_data["customer"])
            logger.info(f"📞 نتیجه ایجاد مخاطب: {contact_result.get('success', False)}")
            
            # ایجاد پیش‌فاکتور در حسابفا با timeout کوتاه‌تر
            hesabfa_result = await self.hesabfa_api.create_invoice(order_data)
            logger.info(f"🏦 نتیجه ثبت فاکتور: {hesabfa_result}")
            
            # بارگیری مجدد سفارش برای به‌روزرسانی
            current_order = await self._load_order(order_id)
            if not current_order:
                logger.error(f"❌ خطا در بارگیری مجدد سفارش {order_id}")
                return
                
            if hesabfa_result.get("success"):
                # ذخیره شناسه فاکتور حسابفا در سفارش
                current_order["hesabfa_invoice_id"] = hesabfa_result.get("invoice_id")
                current_order["hesabfa_invoice_number"] = hesabfa_result.get("invoice_number")
                
                # اضافه کردن به تاریخچه
                hesabfa_entry = {
                    "status": "hesabfa_created",
                    "timestamp": datetime.now().isoformat(),
                    "admin": "سیستم",
                    "note": f"پیش‌فاکتور در حسابفا ثبت شد - شماره: {hesabfa_result.get('invoice_number')}"
                }
                current_order["status_history"].append(hesabfa_entry)
                
                # ذخیره تغییرات
                await self._save_order(current_order)
                
                logger.info(f"✅ پیش‌فاکتور سفارش {order_id} در حسابفا ثبت شد")
                logger.info(f"   📋 شماره فاکتور: {hesabfa_result.get('invoice_number')}")
                logger.info(f"   🆔 شناسه حسابفا: {hesabfa_result.get('invoice_id')}")
                logger.info(f"   👤 مشتری: {order_data['customer']['name']}")
            else:
                error_message = hesabfa_result.get('error', 'خطای نامشخص')
                logger.error(f"❌ خطا در ثبت پیش‌فاکتور حسابفا: {error_message}")
                
                # ثبت خطا در تاریخچه
                error_entry = {
                    "status": "hesabfa_error",
                    "timestamp": datetime.now().isoformat(),
                    "admin": "سیستم",
                    "note": f"خطا در ثبت پیش‌فاکتور حسابفا: {error_message}"
                }
                current_order["status_history"].append(error_entry)
                await self._save_order(current_order)
                
        except Exception as hesabfa_exception:
            logger.error(f"❌ خطای غیرمنتظره در ثبت حسابفا: {hesabfa_exception}")
            
            # بارگیری مجدد و ثبت خطا
            try:
                current_order = await self._load_order(order_id)
                if current_order:
                    error_entry = {
                        "status": "hesabfa_error",
                        "timestamp": datetime.now().isoformat(),
                        "admin": "سیستم",
                        "note": f"خطای سیستمی در ثبت پیش‌فاکتور: {str(hesabfa_exception)[:100]}"
                    }
                    current_order["status_history"].append(error_entry)
                    await self._save_order(current_order)
            except Exception as save_error:
                logger.error(f"❌ خطا در ذخیره خطای حسابفا: {save_error}")

    async def _notify_customer_async(self, user_id: int, status: str, order_id: str, admin_name: str = ""):
        """اطلاع‌رسانی غیرهمزمان به مشتری"""
        try:
            await self._notify_customer(user_id, status, order_id, admin_name)
        except Exception as e:
            logger.error(f"❌ خطا در اطلاع‌رسانی غیرهمزمان: {e}")

    async def _notify_customer(self, user_id: int, status: str, order_id: str, admin_name: str = ""):
        """اطلاع‌رسانی به مشتری"""
        if not self.bot:
            logger.warning("Bot instance تنظیم نشده است")
            return

        try:
            logger.info(f"🔔 شروع اطلاع‌رسانی به مشتری {user_id} برای سفارش {order_id}")
            
            # بررسی لغو سفارش برای پیام خاص
            if status == OrderStatus.CANCELLED:
                # دریافت اطلاعات مشتری
                order_data = await self._load_order(order_id)
                customer_name = "مشتری گرامی"

                if order_data and order_data.get('customer'):
                    customer_name = order_data['customer'].get('name', 'مشتری گرامی')

                full_message = (
                    f"📋 سفارش شماره: {order_id}\n\n"
                    f"از انتخاب شما برای خرید از شرکت دکوتین ممنونیم {customer_name} عزیز\n\n"
                    f"سقف اعتبار خرید شما به علت مانده حساب مسدود شده است\n\n"
                    f"لطفا مانده حساب خود را واریز نمایید و با ارسال فیش ادامه خرید خود را انجام دهید\n\n"
                    f"با تشکر\n"
                    f"مجموعه دکوتین 🌟"
                )
            else:
                message = self.status_messages.get(status, f"وضعیت سفارش شما به {status} تغییر کرد.")

                # افزودن شماره سفارش
                full_message = (
                    f"📋 سفارش شماره: {order_id}\n"
                    f"{message}\n"
                )

                if admin_name and status != OrderStatus.PENDING:
                    full_message += f"\n👤 توسط: {admin_name}"

            # دکمه‌های کمکی برای ارتباط با پشتیبانی
            keyboard = self._create_customer_support_buttons(order_id)

            # ارسال پیام با retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=full_message,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    logger.info(f"✅ اطلاع‌رسانی وضعیت {status} به مشتری {user_id} ارسال شد")
                    return
                except Exception as send_error:
                    logger.warning(f"⚠️ تلاش {attempt + 1} ناموفق: {send_error}")
                    if attempt == max_retries - 1:
                        # آخرین تلاش با پیام ساده
                        simple_message = f"📋 سفارش {order_id} به‌روزرسانی شد."
                        await self.bot.send_message(
                            chat_id=user_id,
                            text=simple_message
                        )
                        logger.info(f"✅ پیام ساده به مشتری {user_id} ارسال شد")

        except Exception as e:
            logger.error(f"❌ خطا در اطلاع‌رسانی به مشتری {user_id}: {e}")
            logger.error(f"   سفارش: {order_id}, وضعیت: {status}")
            logger.error(f"   خطای کامل: {str(e)}")
            
            # تلاش نهایی برای ارسال پیام بسیار ساده
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"سفارش {order_id} به‌روزرسانی شد."
                )
                logger.info(f"✅ پیام اضطراری به مشتری {user_id} ارسال شد")
            except:
                logger.error(f"❌ حتی پیام اضطراری نیز ارسال نشد")

    def _create_customer_support_buttons(self, order_id: str) -> List[List[InlineKeyboardButton]]:
        """Create customer support buttons for order status"""
        return [
            [
                InlineKeyboardButton("📋 وضعیت سفارش", callback_data=f"check_order_status_{order_id}"),
                InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="contact_support")
            ],
            [
                InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")
            ]
        ]

    def _get_status_text(self, status: str) -> str:
        """متن فارسی وضعیت"""
        status_texts = {
            OrderStatus.PENDING: "در انتظار",
            OrderStatus.CONTACTED: "در حال پیگیری",
            OrderStatus.CONFIRMED: "تایید شد",
            OrderStatus.PREPARING: "در حال آماده‌سازی",
            OrderStatus.READY: "آماده ارسال",
            OrderStatus.SHIPPED: "ارسال شد",
            OrderStatus.DELIVERED: "تحویل داده شد",
            OrderStatus.COMPLETED: "تکمیل شد",
            OrderStatus.CANCELLED: "لغو شد"
        }
        return status_texts.get(status, status)

    async def get_order_details(self, order_id: str) -> Optional[Dict]:
        """دریافت جزئیات سفارش"""
        return await self._load_order(order_id)

    async def get_customer_orders(self, user_id: int) -> List[Dict]:
        """دریافت تمام سفارشات یک مشتری"""
        orders = []

        try:
            for filename in os.listdir(self.orders_dir):
                if filename.startswith(f"order_{user_id}_") and filename.endswith(".json"):
                    order_id = filename.replace("order_", "").replace(".json", "")
                    order_data = await self._load_order(order_id)
                    if order_data:
                        orders.append(order_data)

            # مرتب‌سازی بر اساس تاریخ ایجاد (جدیدترین اول)
            orders.sort(key=lambda x: x["created_at"], reverse=True)
            return orders

        except Exception as e:
            logger.error(f"خطا در دریافت سفارشات مشتری {user_id}: {e}")
            return []

    async def get_all_orders(self, status_filter: str = None) -> List[Dict]:
        """دریافت تمام سفارشات (برای ادمین)"""
        orders = []

        try:
            for filename in os.listdir(self.orders_dir):
                if filename.startswith("order_") and filename.endswith(".json"):
                    order_id = filename.replace("order_", "").replace(".json", "")
                    order_data = await self._load_order(order_id)
                    if order_data:
                        if status_filter is None or order_data["status"] == status_filter:
                            orders.append(order_data)

            # مرتب‌سازی بر اساس تاریخ ایجاد (جدیدترین اول)
            orders.sort(key=lambda x: x["created_at"], reverse=True)
            return orders

        except Exception as e:
            logger.error(f"خطا در دریافت تمام سفارشات: {e}")
            return []

    async def send_support_contact_info(self, user_id: int):
        """ارسال اطلاعات تماس پشتیبانی"""
        if not self.bot:
            return

        try:
            contact_message = (
                "📞 اطلاعات تماس پشتیبانی\n\n"
                "🕐 ساعات کاری: شنبه تا پنج‌شنبه - ۹ صبح تا ۶ عصر\n"
                "📞 تلفن: ۰۲۱-۱۲۳۴۵۶۷۸\n"
                "📱 واتساپ: ۰۹۱۲۳۴۵۶۷۸۹\n"
                "✉️ ایمیل: support@example.com\n\n"
                "⚡ پاسخگویی سریع در ساعات کاری"
            )

            keyboard = [[
                InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")
            ]]

            await self.bot.send_message(
                chat_id=user_id,
                text=contact_message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"خطا در ارسال اطلاعات تماس: {e}")

    async def send_faq(self, user_id: int):
        """ارسال سوالات متداول"""
        if not self.bot:
            return

        try:
            faq_message = (
                "❓ سوالات متداول\n\n"
                "🔸 چقدر طول می‌کشد تا سفارش آماده شود؟\n"
                "معمولاً ۳ تا ۵ روز کاری\n\n"
                "🔸 هزینه ارسال چقدر است؟\n"
                "برای سفارشات بالای ۵ میلیون تومان رایگان\n\n"
                "🔸 آیا امکان تغییر یا لغو سفارش وجود دارد؟\n"
                "تا قبل از آماده‌سازی امکان‌پذیر است\n\n"
                "🔸 چگونه می‌توانم وضعیت سفارش را پیگیری کنم؟\n"
                "از طریق همین ربات یا تماس با پشتیبانی"
            )

            keyboard = [
                [InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="contact_support")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]

            await self.bot.send_message(
                chat_id=user_id,
                text=faq_message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"خطا در ارسال سوالات متداول: {e}")

    async def get_todays_orders(self) -> List[Dict]:
        """دریافت سفارشات امروز"""
        today_orders = []
        today_date = datetime.now().strftime("%Y-%m-%d")

        try:
            for filename in os.listdir(self.orders_dir):
                if filename.startswith("order_") and filename.endswith(".json"):
                    order_id = filename.replace("order_", "").replace(".json", "")
                    order_data = await self._load_order(order_id)

                    if order_data:
                        # بررسی تاریخ ایجاد سفارش
                        order_date = order_data.get('created_at', '')[:10]
                        if order_date == today_date:
                            today_orders.append(order_data)

            # مرتب‌سازی بر اساس زمان ایجاد (جدیدترین اول)
            today_orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return today_orders

        except Exception as e:
            logger.error(f"خطا در دریافت سفارشات امروز: {e}")
            return []

    async def get_orders_by_date(self, target_date: str) -> List[Dict]:
        """دریافت سفارشات بر اساس تاریخ (فرمت: YYYY-MM-DD)"""
        date_orders = []

        try:
            for filename in os.listdir(self.orders_dir):
                if filename.startswith("order_") and filename.endswith(".json"):
                    order_id = filename.replace("order_", "").replace(".json", "")
                    order_data = await self._load_order(order_id)

                    if order_data:
                        order_date = order_data.get('created_at', '')[:10]
                        if order_date == target_date:
                            date_orders.append(order_data)

            # مرتب‌سازی بر اساس زمان ایجاد
            date_orders.sort(key=lambda x: x.get('created_at', ''))
            return date_orders

        except Exception as e:
            logger.error(f"خطا در دریافت سفارشات تاریخ {target_date}: {e}")
            return []

    async def get_orders_statistics(self) -> Dict:
        """دریافت آمار کلی سفارشات"""
        try:
            all_orders = await self.get_all_orders()
            today_orders = await self.get_todays_orders()

            # آمار کلی
            total_orders = len(all_orders)
            today_count = len(today_orders)

            # آمار وضعیت
            status_stats = {}
            total_revenue = 0
            today_revenue = 0

            for order in all_orders:
                status = order.get('status', 'pending')
                status_text = self._get_status_text(status)
                status_stats[status_text] = status_stats.get(status_text, 0) + 1
                total_revenue += order.get('pricing', {}).get('total', 0)

            for order in today_orders:
                today_revenue += order.get('pricing', {}).get('total', 0)

            return {
                'total_orders': total_orders,
                'today_orders': today_count,
                'total_revenue': total_revenue,
                'today_revenue': today_revenue,
                'status_distribution': status_stats
            }

        except Exception as e:
            logger.error(f"خطا در محاسبه آمار: {e}")
            return {}