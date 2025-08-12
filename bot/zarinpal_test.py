#!/usr/bin/env python3
"""
ZarinPal Payment Integration - Fixed Version
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
            # Sandbox URLs
            self.request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
            self.verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
            self.gateway_url = "https://sandbox.zarinpal.com/pg/StartPay/"
        else:
            # Production URLs - API v4
            self.request_url = "https://api.zarinpal.com/pg/v4/payment/request/"
            self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify/"
            self.gateway_url = "https://www.zarinpal.com/pg/StartPay/"

    def create_payment_request(self,
                               amount: int,
                               description: str,
                               callback_url: str,
                               customer_email: str = "",
                               customer_mobile: str = "") -> Dict[str, Any]:
        """Create payment request"""
        try:
            if self.sandbox:
                # Sandbox API (v3 format)
                data = {
                    "MerchantID": self.merchant_id,
                    "Amount": amount,
                    "Description": description,
                    "CallbackURL": callback_url,
                    "Email": customer_email,
                    "Mobile": customer_mobile
                }
                headers = {'Content-Type': 'application/json'}
            else:
                # Production API (v4 format)
                data = {
                    "merchant_id": self.merchant_id,
                    "amount": amount,
                    "description": description,
                    "callback_url": callback_url,
                    "metadata": {
                        "email": customer_email,
                        "mobile": customer_mobile
                    }
                }
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

            logger.info(f"Sending payment request to: {self.request_url}")
            logger.info(
                f"Request data: {json.dumps(data, ensure_ascii=False)}")

            response = requests.post(self.request_url,
                                     json=data,
                                     headers=headers,
                                     timeout=15)

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response text: {response.text}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error":
                    f"HTTP Error {response.status_code}: {response.text}"
                }

            result = response.json()

            if self.sandbox:
                # Sandbox response format
                if result.get("Status") == 100:
                    authority = result.get("Authority")
                    payment_url = f"{self.gateway_url}{authority}"

                    logger.info(
                        f"Payment request created successfully. Authority: {authority}"
                    )
                    return {
                        "success": True,
                        "authority": authority,
                        "payment_url": payment_url
                    }
                else:
                    error_msg = self._get_error_message(
                        result.get("Status", -999))
                    logger.error(
                        f"ZarinPal payment request failed: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                # Production response format
                if result.get("data") and result["data"].get("code") == 100:
                    authority = result["data"].get("authority")
                    payment_url = f"{self.gateway_url}{authority}"

                    logger.info(
                        f"Payment request created successfully. Authority: {authority}"
                    )
                    return {
                        "success": True,
                        "authority": authority,
                        "payment_url": payment_url
                    }
                else:
                    error_msg = result.get("errors",
                                           {}).get("message", "خطای نامشخص")
                    logger.error(
                        f"ZarinPal payment request failed: {error_msg}")
                    return {"success": False, "error": error_msg}

        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return {
                "success": False,
                "error": "زمان درخواست به پایان رسید. لطفاً دوباره تلاش کنید."
            }
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return {
                "success":
                False,
                "error":
                "خطا در اتصال به درگاه پرداخت. اتصال اینترنت خود را بررسی کنید."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {"success": False, "error": "خطا در ارتباط با درگاه پرداخت"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"success": False, "error": "پاسخ نامعتبر از درگاه پرداخت"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": "خطای غیرمنتظره در ایجاد درخواست پرداخت"
            }

    def verify_payment(self, authority: str, amount: int) -> Dict[str, Any]:
        """Verify payment"""
        try:
            if self.sandbox:
                # Sandbox API (v3 format)
                data = {
                    "MerchantID": self.merchant_id,
                    "Authority": authority,
                    "Amount": amount
                }
                headers = {'Content-Type': 'application/json'}
            else:
                # Production API (v4 format)
                data = {
                    "merchant_id": self.merchant_id,
                    "authority": authority,
                    "amount": amount
                }
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

            logger.info(f"Verifying payment with authority: {authority}")

            response = requests.post(self.verify_url,
                                     json=data,
                                     headers=headers,
                                     timeout=15)

            logger.info(
                f"Verification response status: {response.status_code}")
            logger.info(f"Verification response: {response.text}")

            if response.status_code != 200:
                return {
                    "success": False,
                    "error":
                    f"HTTP Error {response.status_code}: {response.text}"
                }

            result = response.json()

            if self.sandbox:
                # Sandbox response format
                if result.get("Status") == 100:
                    ref_id = result.get("RefID")
                    logger.info(
                        f"Payment verified successfully. RefID: {ref_id}")
                    return {
                        "success": True,
                        "ref_id": ref_id,
                        "status": "verified"
                    }
                else:
                    error_msg = self._get_error_message(
                        result.get("Status", -999))
                    logger.error(f"Payment verification failed: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                # Production response format
                if result.get("data") and result["data"].get("code") == 100:
                    ref_id = result["data"].get("ref_id")
                    logger.info(
                        f"Payment verified successfully. RefID: {ref_id}")
                    return {
                        "success": True,
                        "ref_id": ref_id,
                        "status": "verified"
                    }
                else:
                    error_msg = result.get("errors",
                                           {}).get("message", "خطای نامشخص")
                    logger.error(f"Payment verification failed: {error_msg}")
                    return {"success": False, "error": error_msg}

        except requests.exceptions.Timeout:
            logger.error("Verification request timeout")
            return {
                "success": False,
                "error": "زمان تأیید پرداخت به پایان رسید"
            }
        except requests.exceptions.ConnectionError:
            logger.error("Verification connection error")
            return {
                "success": False,
                "error": "خطا در اتصال برای تأیید پرداخت"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Verification request error: {e}")
            return {"success": False, "error": "خطا در تأیید پرداخت"}
        except json.JSONDecodeError as e:
            logger.error(f"Verification JSON decode error: {e}")
            return {"success": False, "error": "پاسخ نامعتبر در تأیید پرداخت"}
        except Exception as e:
            logger.error(f"Unexpected verification error: {e}")
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
            -42:
            "مدت زمان معتبر طول عمر شناسه پرداخت باید بین ۳۰ دقیقه تا ۴۵ روز باشد",
            -54: "درخواست مورد نظر آرشیو شده است",
            101:
            "عملیات پرداخت موفق بوده و قبلاً PaymentVerification تراکنش انجام شده است",
            -999: "خطای نامشخص - پاسخ از سرور دریافت نشد"
        }

        return error_messages.get(status_code,
                                  f"خطای نامشخص با کد {status_code}")
