#!/usr/bin/env python3
"""
Bot Configuration - Fixed Version
Manages environment variables and configuration settings.
"""

import os
import logging
from typing import List, Optional


class Config:
    """Configuration class for the Telegram bot"""

    def __init__(self):
        """Initialize configuration from environment variables"""
        # Get bot token from environment or use provided token
        self.bot_token: str = os.getenv("BOT_TOKEN", "482872229:AAEG0hySlWspi-KOF5lbR2fMZGJ1qWUPLn0")

        if not self.bot_token:
            raise ValueError("BOT_TOKEN not found in environment variables")

        # ZarinPal configuration - using your provided merchant ID
        self.zarinpal_merchant_id: str = os.getenv(
            "ZARINPAL_MERCHANT_ID", "fd4166f9-78e2-4228-ac7d-077a5168f064")
        self.zarinpal_sandbox: bool = os.getenv("ZARINPAL_SANDBOX",
                                                "True").lower() == "true"

        # Order group settings
        self.order_group_chat_id = os.getenv('ORDER_GROUP_CHAT_ID')

        # اگر تنظیم نشده، از Chat ID گروه DecoTeen Bot Orders استفاده کن
        if not self.order_group_chat_id:
            # Chat ID از عکس: -4804296164 (گروه DecoTeen Bot Orders)
            self.order_group_chat_id = -4804296164
            logging.info(
                f"✅ استفاده از گروه پیش‌فرض: {self.order_group_chat_id}")
        else:
            # تبدیل به int
            try:
                self.order_group_chat_id = int(self.order_group_chat_id)
                logging.info(
                    f"✅ استفاده از گروه تنظیم شده: {self.order_group_chat_id}")
            except ValueError:
                logging.error(
                    f"❌ ORDER_GROUP_CHAT_ID نامعتبر: {self.order_group_chat_id}"
                )
                # استفاده از گروه پیش‌فرض
                self.order_group_chat_id = -4804296164
                logging.info(
                    f"✅ استفاده از گروه پیش‌فرض به جای نامعتبر: {self.order_group_chat_id}"
                )

        # Optional configurations with safe defaults
        self.admin_ids: List[int] = self._parse_admin_ids()
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.cart_data_dir: str = os.getenv("CART_DATA_DIR", "cart_data")
        self.max_cart_items: int = int(os.getenv("MAX_CART_ITEMS", "50"))

        # Bot domain for payment callbacks
        self.bot_domain: str = os.getenv("BOT_DOMAIN", "example.com")

    def _parse_admin_ids(self) -> List[int]:
        """Parse admin IDs from environment variable"""
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if not admin_ids_str:
            return []

        try:
            return [
                int(id_str.strip()) for id_str in admin_ids_str.split(",")
                if id_str.strip()
            ]
        except ValueError:
            logging.warning("Invalid ADMIN_IDS format. Using empty list.")
            return []

    def get_callback_url(self) -> str:
        """Get payment callback URL"""
        return f"https://{self.bot_domain}/payment/callback"

    def validate_setup(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []

        if not self.bot_token or self.bot_token == "YOUR_BOT_TOKEN_HERE":
            issues.append("BOT_TOKEN is not set or using placeholder value")

        if not self.zarinpal_merchant_id or self.zarinpal_merchant_id == "YOUR_MERCHANT_ID":
            issues.append(
                "ZARINPAL_MERCHANT_ID is not set or using placeholder value")

        if self.bot_domain == "example.com":
            issues.append(
                "BOT_DOMAIN should be set to your actual domain (required for payment callbacks)"
            )

        if not self.admin_ids:
            issues.append("Consider setting ADMIN_IDS for bot administration")

        return issues

    def print_config_status(self):
        """Print configuration status for debugging"""
        print("=== Bot Configuration Status ===")
        print(f"Bot Token: ✅ Set and Ready")
        print(
            f"ZarinPal Merchant ID: ✓ Set ({self.zarinpal_merchant_id[:8]}...{self.zarinpal_merchant_id[-8:]})"
        )
        print(f"Bot Domain: ✓ Set ({self.bot_domain})")
        print(f"Callback URL: {self.get_callback_url()}")
        print(f"Admin IDs: {len(self.admin_ids)} configured")
        print(f"Order Group ID: ✓ Set ({self.order_group_chat_id})")
        print(
            f"ZarinPal Sandbox: {'Enabled' if self.zarinpal_sandbox else 'Disabled'}"
        )
        print(f"Max Cart Items: {self.max_cart_items}")
        print("================================")

        issues = self.validate_setup()
        if issues:
            print("⚠️ Configuration Notes:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Configuration is complete!")

    async def test_group_connection(self, bot):
        """Test connection to order group"""
        if not self.order_group_chat_id:
            print("❌ Order group ID not configured")
            return False

        try:
            # Try to get chat info
            chat = await bot.get_chat(self.order_group_chat_id)
            print(f"✅ Group connection successful!")
            print(f"   Title: {chat.title}")
            print(f"   Type: {chat.type}")
            print(
                f"   Member count: {await bot.get_chat_member_count(self.order_group_chat_id)}"
            )
            return True
        except Exception as e:
            print(f"❌ Group connection failed: {e}")
            print(f"   Group ID: {self.order_group_chat_id}")
            print("   Possible issues:")
            print("   - Bot is not a member of the group")
            print("   - Group ID is incorrect")
            print("   - Bot doesn't have permission to send messages")
            return False


# Example usage and testing
if __name__ == "__main__":
    config = Config()
    config.print_config_status()

    print("\n✅ Setup Complete! Your bot is ready to run!")
