
#!/usr/bin/env python3
"""
ZarinPal Payment Integration
Handles payment processing through ZarinPal gateway.
"""

import requests
import json
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ZarinPalGateway:
    """ZarinPal payment gateway integration"""

    def __init__(self, merchant_id: str, sandbox: bool = True):
        self.merchant_id = merchant_id
        self.sandbox = sandbox

        if sandbox:
            self.request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
            self.verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
            self.gateway_url = "https://sandbox.zarinpal.com/pg/StartPay/"
        else:
            self.request_url = "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
            self.verify_url = "https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
            self.gateway_url = "https://www.zarinpal.com/pg/StartPay/"

    def create_payment_request(self, amount: int, description: str, 
                             callback_url: str, customer_email: str = "",
                             customer_mobile: str = "") -> Dict[str, Any]:
        """Create payment request"""
        try:
            data = {
                "MerchantID": self.merchant_id,
                "Amount": amount,
                "Description": description,
                "CallbackURL": callback_url,
                "Email": customer_email,
                "Mobile": customer_mobile
            }

            response = requests.post(self.request_url, json=data, timeout=10)
            result = response.json()

            if result["Status"] == 100:
                authority = result["Authority"]
                payment_url = f"{self.gateway_url}{authority}"

                logger.info(f"Payment request created successfully. Authority: {authority}")
                return {
                    "success": True,
                    "authority": authority,
                    "payment_url": payment_url
                }
            else:
                error_msg = self._get_error_message(result["Status"])
                logger.error(f"ZarinPal payment request failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                "success": False,
                "error": "خطا در ارتباط با درگاه پرداخت"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": "خطای غیرمنتظره در ایجاد درخواست پرداخت"
            }

    def verify_payment(self, authority: str, amount: int) -> Dict[str, Any]:
        """Verify payment"""
        try:
            data = {
                "MerchantID": self.merchant_id,
                "Authority": authority,
                "Amount": amount
            }

            response = requests.post(self.verify_url, json=data, timeout=10)
            result = response.json()

            if result["Status"] == 100:
                ref_id = result["RefID"]
                logger.info(f"Payment verified successfully. RefID: {ref_id}")
                return {
                    "success": True,
                    "ref_id": ref_id,
                    "status": "verified"
                }
            else:
                error_msg = self._get_error_message(result["Status"])
                logger.error(f"Payment verification failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during verification: {e}")
            return {
                "success": False,
                "error": "خطا در تأیید پرداخت"
            }
        except Exception as e:
            logger.error(f"Unexpected error during verification: {e}")
            return {
                "success": False,
                "error": "خطای غیرمنتظره در تأیید پرداخت"
            }

    def _get_error_message(self, status_code: int) -> str:
        """Get Persian error message for status code"""
        error_messages = {
            -1: "اطلاعات ارسال شده ناقص است",
            -2: "IP یا مرچنت کد پذیرنده صحیح نیست",
            -3: "با توجه به محدودیت‌های شاپرک امکان پردازش وجود ندارد",
            -4: "سطح تأیید پذیرنده پایین‌تر از سطح نقره‌ای است",
            -11: "درخواست مورد نظر یافت نشد",
            -12: "امکان ویرایش درخواست میسر نمی‌باشد",
            -21: "هیچ نوع عملیات مالی برای این تراکنش یافت نشد",
            -22: "تراکنش ناموفق می‌باشد",
            -33: "رقم تراکنش با رقم پرداخت شده مطابقت ندارد",
            -34: "سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده است",
            -40: "اجازه دسترسی به متد مربوطه وجود ندارد",
            -41: "اطلاعات ارسال شده مربوط به AdditionalData غیر معتبر می‌باشد",
            -42: "مدت زمان معتبر طول عمر شناسه پرداخت باید بین ۳۰ دقیقه تا ۴۵ روز باشد",
            -54: "درخواست مورد نظر آرشیو شده است",
            101: "عملیات پرداخت موفق بوده و قبلاً PaymentVerification تراکنش انجام شده است"
        }
        
        return error_messages.get(status_code, f"خطای نامشخص با کد {status_code}")
