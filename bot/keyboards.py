#!/usr/bin/env python3
"""
Bot Keyboards
Manages all inline keyboards for the Telegram bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any
from data.product_data import PERSIAN_ALPHABET, get_category_product_icons, search_products_by_icon


class BotKeyboards:
    """Class to manage all bot keyboards"""

    def get_main_menu(self,
                      authenticated: bool = False) -> InlineKeyboardMarkup:
        """Get main menu keyboard"""
        buttons = []

        if authenticated:
            buttons.extend([[
                InlineKeyboardButton("🛒 شروع خرید",
                                     callback_data="start_shopping")
            ], [
                InlineKeyboardButton("🛍️ سبد خرید", callback_data="view_cart")
            ],
                            [
                                InlineKeyboardButton(
                                    "📋 مشاهده پیش فاکتور",
                                    callback_data="view_invoice")
                            ]])

        return InlineKeyboardMarkup(buttons)

    def get_categories_keyboard(self) -> InlineKeyboardMarkup:
        """Get main product categories keyboard"""
        buttons = [
            [
                InlineKeyboardButton(" کالای خواب نوزاد",
                                     callback_data="category_baby")
            ],
            [
                InlineKeyboardButton(" کالای خواب نوجوان",
                                     callback_data="category_teen")
            ],
            [
                InlineKeyboardButton("کالای خواب بزرگسال",
                                     callback_data="category_adult")
            ],
            [
                InlineKeyboardButton(" پرده",
                                     callback_data="category_curtain_only")
            ],
            [InlineKeyboardButton(" کوسن ", callback_data="category_cushion")],
            [
                InlineKeyboardButton(" فرشینه",
                                     callback_data="category_tablecloth")
            ],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(buttons)

    def get_curtain_subcategories(self, page: int = 0) -> InlineKeyboardMarkup:
        """Get curtain subcategories keyboard with icon navigation and pagination"""
        buttons = []

        # Get product icons for curtain_only category
        product_icons = get_category_product_icons('curtain_only')

        # Pagination settings
        items_per_page = 8  # 4 rows * 2 buttons
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_icons = product_icons[start_idx:end_idx]

        # Create buttons for each unique icon - 2 buttons per row
        row = []
        for i, (icon, description, product_id) in enumerate(page_icons):
            button_text = description
            callback_data = f"product_{product_id}"
            row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data))

            # Create rows of 2 buttons each
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []

        # Add remaining button if any
        if row:
            buttons.append(row)

        # Add pagination buttons
        nav_row = []
        total_pages = (len(product_icons) + items_per_page -
                       1) // items_per_page

        if page > 0:
            nav_row.append(
                InlineKeyboardButton("⬅️ صفحه قبل",
                                     callback_data=f"curtain_page_{page-1}"))

        if page < total_pages - 1:
            nav_row.append(
                InlineKeyboardButton("➡️ صفحه بعد",
                                     callback_data=f"curtain_page_{page+1}"))

        if nav_row:
            buttons.append(nav_row)

        # Add alphabet search button
        buttons.append([
            InlineKeyboardButton("🔤 جستجوی حروف الفبایی",
                                 callback_data="alphabet_search_curtain_only")
        ])

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_curtain_only_subcategories(self) -> InlineKeyboardMarkup:
        """Get curtain only subcategories keyboard with icon navigation"""
        buttons = []

        # Get product icons for curtain_only category
        product_icons = get_category_product_icons('curtain_only')

        # Create buttons for each unique icon - 2 buttons per row
        row = []
        for i, (icon, description, product_id) in enumerate(product_icons):
            button_text = description
            callback_data = f"product_{product_id}"
            row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data))

            # Create rows of 2 buttons each
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []

        # Add remaining button if any
        if row:
            buttons.append(row)

        # Add alphabet search button
        buttons.append([
            InlineKeyboardButton("🔤 جستجوی حروف الفبایی",
                                 callback_data="alphabet_search_curtain_only")
        ])

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_curtain_subcategories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_cushion_subcategories(self, page: int = 0) -> InlineKeyboardMarkup:
        """Get cushion subcategories keyboard with icon navigation and pagination"""
        buttons = []

        # Get product icons for cushion category
        product_icons = get_category_product_icons('cushion')

        # Pagination settings (کوسن کم محصول دارد - 6 تا)
        items_per_page = 6  # همه در یک صفحه
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_icons = product_icons[start_idx:end_idx]

        # Create buttons for each unique icon - 2 buttons per row
        row = []
        for i, (icon, description, product_id) in enumerate(page_icons):
            button_text = description
            callback_data = f"icon_cushion_{icon}"
            row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data))

            # Create rows of 2 buttons each
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []

        # Add remaining button if any
        if row:
            buttons.append(row)

        # Add pagination buttons (if needed)
        nav_row = []
        total_pages = (len(product_icons) + items_per_page -
                       1) // items_per_page

        if page > 0:
            nav_row.append(
                InlineKeyboardButton("⬅️ صفحه قبل",
                                     callback_data=f"cushion_page_{page-1}"))

        if page < total_pages - 1:
            nav_row.append(
                InlineKeyboardButton("➡️ صفحه بعد",
                                     callback_data=f"cushion_page_{page+1}"))

        if nav_row:
            buttons.append(nav_row)

        # Add alphabet search button
        buttons.append([
            InlineKeyboardButton("🔤 جستجوی حروف الفبایی",
                                 callback_data="alphabet_search_cushion")
        ])

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_baby_subcategories(self, page: int = 0) -> InlineKeyboardMarkup:
        """Get baby subcategories keyboard with icon navigation and pagination"""
        buttons = []

        # Get product icons for baby category
        product_icons = get_category_product_icons('baby')

        # Pagination settings
        items_per_page = 8  # 4 rows * 2 buttons
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_icons = product_icons[start_idx:end_idx]

        # Create buttons for each unique icon - 2 buttons per row
        row = []
        for i, (icon, description, product_id) in enumerate(page_icons):
            button_text = description
            callback_data = f"icon_baby_{icon}"
            row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data))

            # Create rows of 2 buttons each
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []

        # Add remaining button if any
        if row:
            buttons.append(row)

        # Add pagination buttons
        nav_row = []
        total_pages = (len(product_icons) + items_per_page -
                       1) // items_per_page

        if page > 0:
            nav_row.append(
                InlineKeyboardButton("⬅️ صفحه قبل",
                                     callback_data=f"baby_page_{page-1}"))

        if page < total_pages - 1:
            nav_row.append(
                InlineKeyboardButton("➡️ صفحه بعد",
                                     callback_data=f"baby_page_{page+1}"))

        if nav_row:
            buttons.append(nav_row)

        # Add alphabet search button
        buttons.append([
            InlineKeyboardButton("🔤 جستجوی حروف الفبایی",
                                 callback_data="alphabet_search_baby")
        ])

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_teen_subcategories(self) -> InlineKeyboardMarkup:
        """Get teen subcategories keyboard with size selection"""
        buttons = [[
            InlineKeyboardButton("📏 انتخاب سایز",
                                 callback_data="size_selection_teen")
        ],
                   [
                       InlineKeyboardButton("🔙 بازگشت",
                                            callback_data="back_to_categories")
                   ]]
        return InlineKeyboardMarkup(buttons)

    def get_adult_subcategories(self) -> InlineKeyboardMarkup:
        """Get adult subcategories keyboard with size selection"""
        buttons = [[
            InlineKeyboardButton("📏 انتخاب سایز",
                                 callback_data="size_selection_adult")
        ],
                   [
                       InlineKeyboardButton("🔙 بازگشت",
                                            callback_data="back_to_categories")
                   ]]
        return InlineKeyboardMarkup(buttons)

    def get_tablecloth_subcategories(self,
                                     page: int = 0) -> InlineKeyboardMarkup:
        """Get tablecloth subcategories keyboard with icon navigation and pagination"""
        buttons = []

        # Get product icons for tablecloth category
        product_icons = get_category_product_icons('tablecloth')

        # Pagination settings
        items_per_page = 8  # 4 rows * 2 buttons
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_icons = product_icons[start_idx:end_idx]

        # Create buttons for each unique icon - 2 buttons per row
        row = []
        for i, (icon, description, product_id) in enumerate(page_icons):
            button_text = description  # Remove icon from button text
            callback_data = f"product_{product_id}"
            row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data))

            # Create rows of 2 buttons each
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []

        # Add remaining button if any
        if row:
            buttons.append(row)

        # Add pagination buttons
        nav_row = []
        total_pages = (len(product_icons) + items_per_page -
                       1) // items_per_page

        if page > 0:
            nav_row.append(
                InlineKeyboardButton(
                    "⬅️ صفحه قبل", callback_data=f"tablecloth_page_{page-1}"))

        if page < total_pages - 1:
            nav_row.append(
                InlineKeyboardButton(
                    "➡️ صفحه بعد", callback_data=f"tablecloth_page_{page+1}"))

        if nav_row:
            buttons.append(nav_row)

        # Add alphabet search button
        buttons.append([
            InlineKeyboardButton("🔤 جستجوی حروف الفبایی",
                                 callback_data="alphabet_search_tablecloth")
        ])

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_alphabetical_keyboard(self,
                                  category: str,
                                  page: int = 0) -> InlineKeyboardMarkup:
        """Get alphabetical search keyboard with pagination"""
        buttons = []
        row = []

        # Pagination settings
        letters_per_page = 16  # 4 rows * 4 letters
        start_idx = page * letters_per_page
        end_idx = start_idx + letters_per_page
        page_letters = PERSIAN_ALPHABET[start_idx:end_idx]

        for i, letter in enumerate(page_letters):
            # Create consistent callback data format
            callback_data = f"alpha_{category}_{letter}"
            row.append(
                InlineKeyboardButton(letter, callback_data=callback_data))

            # Create rows of 4 buttons each
            if (i + 1) % 4 == 0:
                buttons.append(row)
                row = []

        # Add remaining buttons if any
        if row:
            buttons.append(row)

        # Add pagination buttons
        nav_row = []
        total_pages = (len(PERSIAN_ALPHABET) + letters_per_page -
                       1) // letters_per_page

        if page > 0:
            nav_row.append(
                InlineKeyboardButton(
                    "⬅️ صفحه قبل",
                    callback_data=f"alpha_page_{category}_{page-1}"))

        if page < total_pages - 1:
            nav_row.append(
                InlineKeyboardButton(
                    "➡️ صفحه بعد",
                    callback_data=f"alpha_page_{category}_{page+1}"))

        if nav_row:
            buttons.append(nav_row)

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_products_keyboard(self, products: List[Dict],
                              category: str) -> InlineKeyboardMarkup:
        """Get products list keyboard"""
        buttons = []

        for product in products:
            button_text = product['name']
            callback_data = f"product_{product['id']}"
            buttons.append([
                InlineKeyboardButton(button_text, callback_data=callback_data)
            ])

        # Add navigation buttons
        buttons.append(
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")])

        return InlineKeyboardMarkup(buttons)

    def get_category_products_keyboard(self,
                                       category: str) -> InlineKeyboardMarkup:
        """Get category products keyboard with icons"""
        buttons = []

        # Get product icons for this category
        product_icons = get_category_product_icons(category)

        # Create buttons for each unique icon - 2 buttons per row
        row = []
        for i, (icon, description, product_id) in enumerate(product_icons):
            button_text = description
            callback_data = f"product_{product_id}"
            row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data))

            # Create rows of 2 buttons each
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []

        # Add remaining button if any
        if row:
            buttons.append(row)

        # Add alphabet search button
        buttons.append([
            InlineKeyboardButton("🔤 جستجوی حروف الفبایی",
                                 callback_data=f"alphabet_search_{category}")
        ])

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_size_selection_keyboard(self,
                                    category: str) -> InlineKeyboardMarkup:
        """Get size selection keyboard based on category"""
        if category == 'baby':
            # Baby category: only 75×160
            sizes = ["75×160"]
        elif category in ['teen', 'adult']:
            # Teen and adult: specific sizes as requested
            if category == 'teen':
                sizes = [
                    "90×200",
                    "100×200",
                    "120×200",
                ]
            else:  # category == 'adult'
                sizes = [
                    "140×200",
                    "160×200",
                    "180×200",
                ]
        elif category == 'tablecloth':
            # Tablecloth category: custom sizes with different prices
            sizes = ["120×80", "100×100", "100×150", "120×180"]
        else:
            # Default sizes for other categories
            sizes = [
                "140×200",
                "160×200",
                "180×200",
            ]

        buttons = []
        row = []

        for i, size in enumerate(sizes):
            row.append(
                InlineKeyboardButton(size,
                                     callback_data=f"size_{size}_{category}"))

            # Create rows of 3 buttons each for better layout with more sizes
            if (i + 1) % 3 == 0:
                buttons.append(row)
                row = []

        # Add remaining buttons if any
        if row:
            buttons.append(row)

        # Add back button
        buttons.append([
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_categories")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_sewing_type_keyboard(self) -> InlineKeyboardMarkup:
        """Get sewing type selection keyboard for curtains"""
        buttons = [[
            InlineKeyboardButton("پانچ", callback_data="sewing_panch"),
            InlineKeyboardButton("نواردوزی", callback_data="sewing_navardozi")
        ],
                   [
                       InlineKeyboardButton("🔙 بازگشت",
                                            callback_data="back_to_categories")
                   ]]
        return InlineKeyboardMarkup(buttons)

    def get_fabric_selection_keyboard(self) -> InlineKeyboardMarkup:
        """Get fabric selection keyboard for curtains"""
        buttons = [[
            InlineKeyboardButton("حریر کتان",
                                 callback_data="fabric_silk_cotton"),
            InlineKeyboardButton("مخمل", callback_data="fabric_velvet")
        ],
                   [
                       InlineKeyboardButton(
                           "🔙 بازگشت", callback_data="back_to_sewing_type")
                   ]]
        return InlineKeyboardMarkup(buttons)

    def get_height_input_keyboard(self) -> InlineKeyboardMarkup:
        """Get height input keyboard for curtains"""
        buttons = [[
            InlineKeyboardButton("🔙 بازگشت",
                                 callback_data="back_to_fabric_selection")
        ]]
        return InlineKeyboardMarkup(buttons)

    def get_quantity_keyboard(self) -> InlineKeyboardMarkup:
        """Get quantity selection keyboard"""
        buttons = []
        row = []

        # Quantities 1-10
        for i in range(1, 11):
            row.append(InlineKeyboardButton(str(i), callback_data=f"qty_{i}"))

            # Create rows of 5 buttons each
            if i % 5 == 0:
                buttons.append(row)
                row = []

        # Add navigation buttons
        buttons.append([
            InlineKeyboardButton(" بازگشت", callback_data="back_to_products")
        ])

        return InlineKeyboardMarkup(buttons)

    def get_payment_keyboard(self) -> InlineKeyboardMarkup:
        """Get payment options keyboard"""
        buttons = [[
            InlineKeyboardButton(" پرداخت نقدی (۳۰٪ تخفیف)",
                                 callback_data="payment_cash_card")
        ],
                   [
                       InlineKeyboardButton(" پرداخت ۶۰ روز (۲۵٪ تخفیف)",
                                            callback_data="payment_60day_card")
                   ],
                   [
                       InlineKeyboardButton(
                           " پرداخت ۹۰ روز (۲۵٪ تخفیف + ۲۵٪ پیش‌پرداخت)",
                           callback_data="payment_90day_card")
                   ],
                   [
                       InlineKeyboardButton(" بازگشت به سبد خرید",
                                            callback_data="view_cart")
                   ],
                   [
                       InlineKeyboardButton(" منوی اصلی",
                                            callback_data="main_menu")
                   ]]
        return InlineKeyboardMarkup(buttons)

    def get_cart_management_keyboard(self) -> InlineKeyboardMarkup:
        """Get cart management keyboard"""
        buttons = [[
            InlineKeyboardButton(" مشاهده پیش فاکتور",
                                 callback_data="view_invoice")
        ], [
            InlineKeyboardButton(" ادامه خرید", callback_data="start_shopping")
        ], [InlineKeyboardButton(" پاک کردن سبد", callback_data="cart_clear")
            ], [InlineKeyboardButton(" منوی اصلی", callback_data="main_menu")]]
        return InlineKeyboardMarkup(buttons)

    def get_payment_type_keyboard(self,
                                  payment_method: str) -> InlineKeyboardMarkup:
        """Get payment type selection keyboard (Cash vs Check)"""
        buttons = [
            [
                InlineKeyboardButton(
                    " پرداخت نقدی",
                    callback_data=f"payment_type_cash_{payment_method}")
            ],
            [
                InlineKeyboardButton(
                    " پرداخت چکی",
                    callback_data=f"payment_type_check_{payment_method}")
            ], [InlineKeyboardButton(" بازگشت", callback_data="view_invoice")]
        ]
        return InlineKeyboardMarkup(buttons)

    def get_cash_payment_keyboard(self) -> InlineKeyboardMarkup:
        """Get cash payment confirmation keyboard"""
        buttons = [[
            InlineKeyboardButton(" ارسال فیش واریزی",
                                 callback_data="upload_receipt")
        ], [InlineKeyboardButton(" بازگشت", callback_data="view_invoice")]]
        return InlineKeyboardMarkup(buttons)

    def get_check_payment_keyboard(self) -> InlineKeyboardMarkup:
        """Get check payment keyboard"""
        buttons = [[
            InlineKeyboardButton(" ارسال عکس چک",
                                 callback_data="upload_check_photo")
        ],
                   [
                       InlineKeyboardButton(" در حال پیگیری",
                                            callback_data="check_follow_up")
                   ],
                   [
                       InlineKeyboardButton(" بازگشت",
                                            callback_data="view_invoice")
                   ]]
        return InlineKeyboardMarkup(buttons)

    def get_check_confirmation_keyboard(self) -> InlineKeyboardMarkup:
        """Get check confirmation keyboard after admin message"""
        buttons = [[
            InlineKeyboardButton("✅ چک را ثبت و ارسال می‌کنم به کارخانه",
                                 callback_data="confirm_check_submission")
        ],
                   [
                       InlineKeyboardButton("🔄 ارسال عکس چک جدید",
                                            callback_data="upload_check_photo")
                   ]]
        return InlineKeyboardMarkup(buttons)
