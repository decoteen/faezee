
#!/usr/bin/env python3
"""
Hesabfa API Integration
ادغام با نرم‌افزار حسابفا برای ثبت خودکار پیش‌فاکتورها
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import setup_logger
from utils.persian_utils import format_price, persian_numbers

logger = setup_logger(__name__)

class HesabfaAPI:
    """کلاس ادغام با API حسابفا"""
    
    def __init__(self, api_key: str = "WjJ88NUd9rjK6dIUKYilbtCoPFCUFHs8"):
        self.api_key = api_key
        self.base_url = "https://api.hesabfa.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    async def create_invoice(self, order_data: Dict) -> Dict[str, Any]:
        """ایجاد پیش‌فاکتور در حسابفا"""
        try:
            logger.info(f"🔄 شروع ثبت فاکتور در حسابفا برای سفارش {order_data.get('order_id')}")
            
            # آماده‌سازی داده‌های فاکتور
            invoice_data = self._prepare_invoice_data(order_data)
            logger.info(f"📋 داده‌های فاکتور آماده شد: {json.dumps(invoice_data, ensure_ascii=False, indent=2)}")
            
            # ارسال درخواست به API حسابفا
            url = f"{self.base_url}/invoice"
            logger.info(f"🌐 ارسال درخواست به: {url}")
            
            response = requests.post(
                url, 
                headers=self.headers, 
                json=invoice_data,
                timeout=30  # افزودن timeout
            )
            
            logger.info(f"📡 پاسخ حسابفا: Status={response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📄 محتوای پاسخ: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get("Success"):
                    invoice_result = result.get("Result", {})
                    logger.info(f"✅ پیش‌فاکتور با موفقیت در حسابفا ثبت شد - ID: {invoice_result.get('Id')}")
                    return {
                        "success": True,
                        "invoice_id": invoice_result.get("Id"),
                        "invoice_number": invoice_result.get("Number"),
                        "message": "پیش‌فاکتور با موفقیت در حسابفا ثبت شد"
                    }
                else:
                    error_msg = result.get("ErrorMessage", "خطای نامشخص")
                    logger.error(f"❌ خطا در ثبت پیش‌فاکتور: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }
            else:
                response_text = response.text[:500] if response.text else "بدون محتوا"
                logger.error(f"❌ خطا در ارتباط با حسابفا: HTTP {response.status_code}")
                logger.error(f"   Response: {response_text}")
                return {
                    "success": False,
                    "error": f"خطا در ارتباط با حسابفا: {response.status_code} - {response_text[:100]}"
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout در ارتباط با حسابفا")
            return {
                "success": False,
                "error": "زمان انتظار ارتباط با حسابفا به پایان رسید"
            }
        except requests.exceptions.ConnectionError:
            logger.error("❌ مشکل در اتصال به حسابفا")
            return {
                "success": False,
                "error": "عدم دسترسی به سرور حسابفا"
            }
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد پیش‌فاکتور حسابفا: {e}")
            logger.error(f"   نوع خطا: {type(e).__name__}")
            return {
                "success": False,
                "error": f"خطای سیستمی: {str(e)}"
            }
    
    def _prepare_invoice_data(self, order_data: Dict) -> Dict:
        """آماده‌سازی داده‌های فاکتور برای حسابفا"""
        customer = order_data.get("customer", {})
        cart_items = order_data.get("cart_items", [])
        pricing = order_data.get("pricing", {})
        
        # آماده‌سازی اطلاعات مشتری
        contact_data = {
            "Name": customer.get("name", "مشتری"),
            "Code": customer.get("customer_id", ""),
            "City": customer.get("city", ""),
            "ContactType": 1  # 1 = مشتری
        }
        
        # آماده‌سازی آیتم‌های فاکتور
        invoice_items = []
        for item in cart_items:
            invoice_items.append({
                "ItemCode": item.get("product_id", ""),
                "ItemName": item.get("product_name", ""),
                "Description": f"سایز: {item.get('size', '')}",
                "Quantity": item.get("quantity", 1),
                "UnitPrice": item.get("price", 0),
                "Tax": 0,  # مالیات محاسبه شده جداگانه
                "Discount": 0
            })
        
        # داده‌های اصلی فاکتور
        invoice_data = {
            "Contact": contact_data,
            "InvoiceItems": invoice_items,
            "Number": order_data.get("order_id", ""),
            "Date": datetime.now().strftime("%Y/%m/%d"),
            "DueDate": datetime.now().strftime("%Y/%m/%d"),
            "Status": 0,  # 0 = پیش‌فاکتور
            "Reference": f"سفارش تلگرام - {order_data.get('order_id')}",
            "Notes": f"روش پرداخت: {order_data.get('payment_method', '')}\nکاربر تلگرام: {order_data.get('user_id', '')}",
            "Tag": "تلگرام-بات",
            "Project": "DecoTeen Bot Orders",
            "SalesPerson": "ربات فروش",
            "Currency": "IRR"
        }
        
        # اضافه کردن تخفیف در صورت وجود
        if pricing.get("discount", 0) > 0:
            invoice_data["Discount"] = pricing.get("discount", 0)
            invoice_data["DiscountType"] = 1  # 1 = مقدار ثابت
        
        return invoice_data
    
    async def create_contact_if_not_exists(self, customer: Dict) -> Dict[str, Any]:
        """ایجاد مخاطب در حسابفا در صورت عدم وجود"""
        try:
            contact_data = {
                "Name": customer.get("name", "مشتری"),
                "Code": customer.get("customer_id", ""),
                "City": customer.get("city", ""),
                "ContactType": 1,  # 1 = مشتری
                "Tag": "تلگرام-بات",
                "Notes": f"مشتری ثبت شده از طریق ربات تلگرام"
            }
            
            url = f"{self.base_url}/contact"
            response = requests.post(url, headers=self.headers, json=contact_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("Success"):
                    logger.info(f"✅ مخاطب جدید در حسابفا ثبت شد: {customer.get('name')}")
                    return {
                        "success": True,
                        "contact_id": result.get("Result", {}).get("Id")
                    }
                else:
                    # اگر مخاطب از قبل وجود داشت، خطا نیست
                    logger.info(f"ℹ️ مخاطب قبلاً در حسابفا وجود داشت: {customer.get('name')}")
                    return {"success": True}
            else:
                logger.warning(f"⚠️ مشکل در ایجاد مخاطب: HTTP {response.status_code}")
                return {"success": False}
                
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد مخاطب: {e}")
            return {"success": False}
    
    async def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """دریافت وضعیت فاکتور از حسابفا"""
        try:
            url = f"{self.base_url}/invoice/{invoice_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("Success"):
                    return {
                        "success": True,
                        "invoice": result.get("Result")
                    }
            
            return {"success": False}
            
        except Exception as e:
            logger.error(f"خطا در دریافت وضعیت فاکتور: {e}")
            return {"success": False}
    
    async def update_invoice_status(self, invoice_id: str, status: int) -> Dict[str, Any]:
        """به‌روزرسانی وضعیت فاکتور در حسابفا"""
        try:
            # 0 = پیش‌فاکتور، 1 = فاکتور، 2 = پرداخت شده
            url = f"{self.base_url}/invoice/{invoice_id}"
            data = {"Status": status}
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("Success"):
                    logger.info(f"✅ وضعیت فاکتور {invoice_id} به‌روزرسانی شد")
                    return {"success": True}
            
            return {"success": False}
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی وضعیت فاکتور: {e}")
            return {"success": False}
