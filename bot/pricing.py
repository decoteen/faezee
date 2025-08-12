#!/usr/bin/env python3
"""
Pricing and Invoice Management
Handles price calculations and invoice generation.
"""

from typing import List, Dict, Any
from utils.persian_utils import format_price, persian_numbers
from datetime import datetime


class PricingManager:
    """Manages pricing and invoice generation"""

    def __init__(self):
        # نرخ‌های تخفیف به‌روزرسانی شده
        self.discount_rates = {
            'cash': 0.30,  # تخفیف ۳۰٪ نقدی
            'installment': 0.25,  # تخفیف ۲۵٪ اقساطی
            '60day': 0.25,  # تخفیف ۲۵٪ برای ۶۰ روزه
            '90day': 0.25  # تخفیف ۲۵٪ برای ۹۰ روزه
        }

        # اطلاعات حساب بانکی
        self.bank_info = {
            'card_number': '6219861915854102',
            'sheba_number': '110560611828005185959401',
            'account_holder': 'نیما کریمی'
        }

    def calculate_subtotal(self, cart_items: List[Dict[str, Any]]) -> float:
        """Calculate subtotal from cart items"""
        return sum(item['price'] * item['quantity'] for item in cart_items)

    def calculate_discount(self, subtotal: float, discount_rate: float) -> int:
        """محاسبه تخفیف"""
        return int(subtotal * discount_rate)

    def calculate_tax(self, amount: int) -> int:
        """محاسبه مالیات ()"""
        return int(amount * 0.09)

    def calculate_total(self, subtotal: float, discount: float = 0) -> float:
        """Calculate final total"""
        return subtotal - discount

    def generate_invoice(self, cart_items: List[Dict[str, Any]],
                         customer: Dict[str, Any]) -> str:
        """Generate invoice with all payment options displayed"""
        if not cart_items:
            return "❌ سبد خرید خالی است."

        # Calculate amounts
        subtotal = self.calculate_subtotal(cart_items)

        # Calculate discounts for each option
        cash_discount = self.calculate_discount(subtotal, 0.30)
        installment_discount = self.calculate_discount(subtotal, 0.25)

        cash_total = subtotal - cash_discount
        installment_total = subtotal - installment_discount
        advance_payment_90 = installment_total * 0.25

        # Generate invoice text
        invoice_lines = [
            "📋 پیش‌فاکتور سفارش", "=" * 30, "", f"👤 مشتری: {customer['name']}",
            f"🏙️ شهر: {customer['city']}",
            f"🆔 کد مشتری: {customer['customer_id']}",
            f"📅 تاریخ: {self._get_persian_date()}", "", "📦 اقلام سفارش:",
            "-" * 20
        ]

        # Add cart items
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_lines.extend([
                f"{persian_numbers(str(i))}. {item['product_name']}",
                f"   📏 سایز: {item['size']}",
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}",
                f"   💰 قیمت واحد: {format_price(item['price'])} تومان",
                f"   💰 قیمت کل: {format_price(item_total)} تومان", ""
            ])

        # Add total amount
        invoice_lines.extend([
            "-" * 20, f"💰 مبلغ کل: {format_price(subtotal)} تومان",
            "",
            "💳 برای انتخاب روش پرداخت، یکی از گزینه‌های زیر را انتخاب کنید:"
        ])

        return "\n".join(invoice_lines)

    def generate_final_invoice(self, cart_items: List[Dict[str, Any]],
                               customer: Dict[str, Any], payment_method: str,
                               discount_rate: float) -> str:
        """Generate final invoice with payment method and discounts"""
        if not cart_items:
            return "❌ سبد خرید خالی است."

        # Calculate amounts
        subtotal = self.calculate_subtotal(cart_items)
        discount = self.calculate_discount(subtotal, discount_rate)
        total = subtotal - discount

        # Generate invoice text
        invoice_lines = [
            "📋 فاکتور نهایی", "=" * 30, "", f"👤 مشتری: {customer['name']}",
            f"🏙️ شهر: {customer['city']}",
            f"🆔 کد مشتری: {customer['customer_id']}",
            f"📅 تاریخ: {self._get_persian_date()}",
            f"💳 روش پرداخت: {payment_method}", "", "📦 اقلام سفارش:", "-" * 20
        ]

        # Add cart items
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_lines.extend([
                f"{persian_numbers(str(i))}. {item['product_name']}",
                f"   📏 سایز: {item['size']}",
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}",
                f"   💰 قیمت واحد: {format_price(item['price'])} تومان",
                f"   💰 قیمت کل: {format_price(item_total)} تومان", ""
            ])

        # Add calculations
        invoice_lines.extend([
            "-" * 20, f"💰 مجموع: {format_price(subtotal)} تومان",
            f"🎁 تخفیف ({persian_numbers(str(int(discount_rate * 100)))}٪): {format_price(discount)} تومان",
            f"💰 مبلغ قابل پرداخت: {format_price(total)} تومان"
        ])

        # Add special details for installment payment
        if payment_method == "پرداخت اقساطی":
            invoice_lines.extend([
                "", "💳 جزئیات پرداخت اقساطی:",
                f"🎁 تخفیف ویژه: {persian_numbers(str(int(discount_rate * 100)))}٪",
                "📞 جزئیات اقساط با تماس کارشناس اعلام خواهد شد"
            ])

        invoice_lines.extend(
            ["", "✅ سفارش شما ثبت شد و به زودی با شما تماس خواهیم گرفت."])

        return "\n".join(invoice_lines)

    def generate_invoice_text(self, order_data: Dict) -> str:
        """تولید متن پیش‌فاکتور"""
        customer = order_data["customer"]
        cart_items = order_data["items"]

        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        discount_rate = 0.25
        discount = subtotal * discount_rate
        total = subtotal - discount
        advance_payment = total * 0.25

        invoice_text = (
            f"🆕 سفارش جدید - شماره: {order_data['order_id']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 نام مشتری: {customer['name']}\n"
            f"🏙️ شهر: {customer['city']}\n"
            f"💰 قیمت کل: {format_price(subtotal)} تومان\n"
            f"🎁 تخفیف (25٪): {format_price(discount)} تومان\n"
            f"💰 مبلغ قابل پرداخت: {format_price(total)} تومان\n"
            f"💳 پیش‌پرداخت (25٪): {format_price(advance_payment)} تومان\n"
            f"📅 تاریخ: ۱۴۰۴/۰۵/۱۴\n"
            f"📋 جزئیات سفارش:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_text += (
                f"{persian_numbers(str(i))}. {item['product_name']}\n"
                f"   📏 سایز: {item['size']}\n"
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}\n"
                f"   💰 قیمت: {format_price(item_total)} تومان\n\n")
        return invoice_text

    def generate_cash_payment_invoice(self, order_data: Dict) -> str:
        """تولید فاکتور پرداخت نقدی با تخفیف 30%"""
        customer = order_data["customer"]
        cart_items = order_data["items"]

        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        discount_rate = 0.30  # 30% discount for cash payment
        discount = subtotal * discount_rate
        total = subtotal - discount

        invoice_text = (f"💳 پرداخت نقدی (30% تخفیف)\n"
                        f"شماره سفارش: {order_data['order_id']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 نام مشتری: {customer['name']}\n"
                        f"🏙️ شهر: {customer['city']}\n"
                        f"📅 تاریخ: {self._get_persian_date()}\n\n"
                        f"📋 جزئیات سفارش:\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Add cart items
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_text += (
                f"{persian_numbers(str(i))}. {item['product_name']}\n"
                f"   📏 سایز: {item['size']}\n"
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}\n"
                f"   💰 قیمت: {format_price(item_total)} تومان\n\n")

        # Add totals
        invoice_text += (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 مبلغ کل: {format_price(subtotal)} تومان\n"
            f"🎁 مبلغ تخفیف ({persian_numbers('30')}٪): {format_price(discount)} تومان\n\n"
            f"💳 اطلاعات پرداخت:\n"
            f"🏪 نام صاحب حساب: {self.bank_info['account_holder']}\n"
            f"💳 شماره کارت: {self.bank_info['card_number']}\n"
            f"🏦 شماره شبا: IR{self.bank_info['sheba_number']}\n\n"
            f"✅ پس از واریز، لطفاً فیش واریزی را ارسال کنید.")

        return invoice_text

    def generate_installment_payment_invoice(self, order_data: Dict) -> str:
        """تولید فاکتور پرداخت اقساطی با تخفیف 25%"""
        customer = order_data["customer"]
        cart_items = order_data["items"]

        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        discount_rate = 0.25  # 25% discount for installment payment
        discount = subtotal * discount_rate
        total = subtotal - discount

        invoice_text = (f"📅 پرداخت اقساطی (25% تخفیف)\n"
                        f"شماره سفارش: {order_data['order_id']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 نام مشتری: {customer['name']}\n"
                        f"🏙️ شهر: {customer['city']}\n"
                        f"📅 تاریخ: {self._get_persian_date()}\n\n"
                        f"📋 جزئیات سفارش:\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Add cart items
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_text += (
                f"{persian_numbers(str(i))}. {item['product_name']}\n"
                f"   📏 سایز: {item['size']}\n"
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}\n"
                f"   💰 قیمت: {format_price(item_total)} تومان\n\n")

        # Add totals
        invoice_text += (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 مبلغ کل: {format_price(subtotal)} تومان\n"
            f"🎁 مبلغ تخفیف ({persian_numbers('25')}٪): {format_price(discount)} تومان\n"
            f"💰 مبلغ نهایی: {format_price(total)} تومان")

        return invoice_text

    def generate_60day_payment_invoice(self, order_data: Dict) -> str:
        """تولید فاکتور پرداخت 60 روزه با تخفیف 25% + پیش پرداخت 25%"""
        customer = order_data["customer"]
        cart_items = order_data["items"]

        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        discount_rate = 0.25  # 25% discount
        discount = subtotal * discount_rate
        total = subtotal - discount
        advance_payment = total * 0.25  # 25% advance payment from final amount

        invoice_text = (f"🕐 پرداخت 60 روزه (25% تخفیف)\n"
                        f"شماره سفارش: {order_data['order_id']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 نام مشتری: {customer['name']}\n"
                        f"🏙️ شهر: {customer['city']}\n"
                        f"📅 تاریخ: {self._get_persian_date()}\n\n"
                        f"📋 جزئیات سفارش:\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Add cart items
        for i, item in enumerate(cart_items, 1):
            item_total = item['price'] * item['quantity']
            invoice_text += (
                f"{persian_numbers(str(i))}. {item['product_name']}\n"
                f"   📏 سایز: {item['size']}\n"
                f"   📦 تعداد: {persian_numbers(str(item['quantity']))}\n"
                f"   💰 قیمت: {format_price(item_total)} تومان\n\n")

        # Add totals and payment terms
        invoice_text += (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 مبلغ کل: {format_price(subtotal)} تومان\n"
            f"🎁 مبلغ تخفیف ({persian_numbers('25')}٪): {format_price(discount)} تومان\n"
            f"💰 مبلغ نهایی: {format_price(total)} تومان\n"
            f"💳 مبلغ پیش‌پرداخت ({persian_numbers('25')}٪): {format_price(advance_payment)} تومان\n\n"
            f"💳 اطلاعات پرداخت پیش‌پرداخت:\n"
            f"🏪 نام صاحب حساب: {self.bank_info['account_holder']}\n"
            f"💳 شماره کارت: {self.bank_info['card_number']}\n"
            f"🏦 شماره شبا: IR{self.bank_info['sheba_number']}\n\n"
            f"📅 شرایط پرداخت:\n"
            f"• پیش‌پرداخت 25٪ از مبلغ نهایی\n"
            f"• مابقی 60 روز پس از تحویل\n"
            f"• تخفیف ویژه 25٪ اعمال شده\n\n"
            f"✅ پس از واریز پیش‌پرداخت، فیش واریزی را ارسال کنید.")

        return invoice_text

    def _get_persian_date(self) -> str:
        """Get current date in Persian format"""
        # Return current Persian date: 1404/5/14
        return persian_numbers("14 مرداد 1404")
