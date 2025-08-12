#!/usr/bin/env python3
"""
تلاش مجدد برای ثبت فاکتور حسابفا برای سفارش موجود
"""

import asyncio
import json
from bot.hesabfa_integration import HesabfaAPI
from bot.order_server import OrderManagementServer

async def retry_hesabfa_for_order():
    """تلاش مجدد برای ثبت فاکتور حسابفا"""
    
    # بارگذاری سفارش آخرین
    order_server = OrderManagementServer()
    order_id = "00027"  # آخرین سفارش
    
    order_data = await order_server._load_order(order_id)
    if not order_data:
        print(f"❌ سفارش {order_id} یافت نشد")
        return
    
    print(f"📋 بارگذاری سفارش {order_id}")
    print(f"👤 مشتری: {order_data['customer']['name']}")
    print(f"💰 مبلغ کل: {order_data['pricing']['total']:,} تومان")
    
    # تلاش برای ثبت در حسابفا
    hesabfa_api = HesabfaAPI()
    
    print("\n🔄 تلاش مجدد برای ثبت فاکتور در حسابفا...")
    
    # ابتدا ایجاد مخاطب
    print("👤 ایجاد مخاطب...")
    contact_result = await hesabfa_api.create_contact_if_not_exists(order_data["customer"])
    print(f"   نتیجه: {contact_result}")
    
    # سپس ایجاد فاکتور
    print("🧾 ایجاد فاکتور...")
    invoice_result = await hesabfa_api.create_invoice(order_data)
    print(f"   نتیجه: {invoice_result}")
    
    if invoice_result.get("success"):
        # به‌روزرسانی سفارش با اطلاعات حسابفا
        order_data["hesabfa_invoice_id"] = invoice_result.get("invoice_id")
        order_data["hesabfa_invoice_number"] = invoice_result.get("invoice_number")
        
        # اضافه کردن به تاریخچه
        from datetime import datetime
        hesabfa_entry = {
            "status": "hesabfa_created",
            "timestamp": datetime.now().isoformat(),
            "admin": "دستی",
            "note": f"پیش‌فاکتور در حسابفا ثبت شد - شماره: {invoice_result.get('invoice_number')}"
        }
        order_data["status_history"].append(hesabfa_entry)
        
        # ذخیره تغییرات
        await order_server._save_order(order_id, order_data)
        
        print(f"✅ فاکتور در حسابفا ثبت شد!")
        print(f"   شماره فاکتور: {invoice_result.get('invoice_number')}")
        print(f"   شناسه: {invoice_result.get('invoice_id')}")
    else:
        print(f"❌ خطا: {invoice_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(retry_hesabfa_for_order())