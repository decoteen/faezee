#!/usr/bin/env python3
"""
تست اتصال به حسابفا
"""

import os
import requests
import json
from bot.hesabfa_integration import HesabfaAPI

def test_hesabfa_connection():
    """تست اتصال به حسابفا"""
    
    # دریافت اطلاعات احراز هویت
    api_key = os.getenv("HESABFA_API_KEY")
    login_token = os.getenv("HESABFA_LOGIN_TOKEN")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: ❌ Not Found")
    print(f"Login Token: {login_token[:10]}..." if login_token else "Login Token: ❌ Not Found")
    
    if not api_key or not login_token:
        print("❌ اطلاعات احراز هویت حسابفا یافت نشد")
        return False
    
    # تست endpoint های مختلف
    endpoints_to_test = [
        "/Setting",
        "/contact", 
        "/invoice",
        "/item"
    ]
    
    base_url = "https://api.hesabfa.com/v1"
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key,
        "logintoken": login_token
    }
    
    print("\n🔍 تست endpoint های مختلف:")
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 تست {endpoint}...")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout - {endpoint}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error - {endpoint}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🧪 تست ایجاد فاکتور نمونه:")
    
    # تست ایجاد فاکتور با داده‌های نمونه
    try:
        hesabfa_api = HesabfaAPI()
        
        sample_order = {
            "order_id": "TEST001",
            "customer": {
                "name": "مشتری تست",
                "customer_id": "TEST001",
                "city": "تهران"
            },
            "cart_items": [{
                "product_id": "TEST_PRODUCT",
                "product_name": "محصول تست",
                "size": "استاندارد",
                "quantity": 1,
                "price": 100000
            }],
            "pricing": {
                "subtotal": 100000,
                "discount": 10000,
                "tax": 9000,
                "total": 99000
            },
            "payment_method": "نقدی",
            "user_id": "TEST_USER"
        }
        
        print("📋 داده‌های نمونه آماده شد...")
        
        # اول تست ایجاد مخاطب
        print("👤 تست ایجاد مخاطب...")
        contact_result = await hesabfa_api.create_contact_if_not_exists(sample_order["customer"])
        print(f"   نتیجه مخاطب: {contact_result}")
        
        # بعد تست ایجاد فاکتور  
        print("🧾 تست ایجاد فاکتور...")
        invoice_result = await hesabfa_api.create_invoice(sample_order)
        print(f"   نتیجه فاکتور: {invoice_result}")
        
        return invoice_result.get("success", False)
        
    except Exception as e:
        print(f"❌ خطا در تست فاکتور: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_hesabfa_connection())
    if result:
        print("\n✅ تست حسابفا موفق بود!")
    else:
        print("\n❌ تست حسابفا ناموفق بود!")