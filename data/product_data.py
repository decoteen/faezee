#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional

# Persian alphabet for search
PERSIAN_ALPHABET = [
    'آ', 'ا', 'ب', 'پ', 'ت', 'ث', 'ج', 'چ', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'ژ',
    'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن',
    'و', 'ه', 'ی'
]

# Product prices by category
PRODUCT_PRICES = {
    'baby': 4780000,
    'teen': 4780000,
    'adult': 5600000,
    'curtain_only': 1550000,  # Base price for silk-cotton fabric
    'cushion': 2800000,
    'tablecloth': 2400000  # Base price (will be overridden by size-based pricing)
}

# Fabric-based pricing for curtains
CURTAIN_FABRIC_PRICES = {
    'silk_cotton': 1550000,  # حریر کتان
    'velvet': 1950000        # مخمل
}

# Size-based pricing for tablecloth category
TABLECLOTH_SIZE_PRICES = {
    '120×80': 2400000,
    '100×100': 2400000,
    '100×150': 3600000,
    '120×180': 5200000
}

# Special pricing for specific products
SPECIAL_PRODUCT_PRICES = {
    'cushion_5': 585000,  # کوسن مخمل گیم دسته بازی سفید
    'cushion_6': 585000,  # کوسن مخمل گیم zone
    'cushion_7': 855000,  # کوسن مخمل awsd
    'cushion_8': 855000,  # کوسن مخمل ENTER
    'cushion_9': 3350000,  # کوسن مخمل گیم PS-KING
    'cushion_10': 585000,  # کوسن مخمل گیم دسته بازی سیاه
    'curtain_15': 1950000,  # پرده حریر سرتخت (جفت) - قیمت ثابت
}

# Product categories with updated icons and search characters
PRODUCT_CATEGORIES = {
    'baby': {
        'name':
        '👶 کالای خواب نوزاد',
        'price':
        4780000,
        'products': [{
            'id': 'baby_1',
            'name': 'آنجل',
            'icon': '👼',
            'search_char': 'آ'
        }, {
            'id': 'baby_2',
            'name': 'آلیسون',
            'icon': '🌸',
            'search_char': 'آ'
        }, {
            'id': 'baby_3',
            'name': 'باربی',
            'icon': '💄',
            'search_char': 'ب'
        }, {
            'id': 'baby_4',
            'name': 'باستر',
            'icon': '🚀',
            'search_char': 'ب'
        }, {
            'id': 'baby_5',
            'name': 'بلا',
            'icon': '🌟',
            'search_char': 'ب'
        }, {
            'id': 'baby_6',
            'name': 'بو',
            'icon': '👻',
            'search_char': 'ب'
        }, {
            'id': 'baby_7',
            'name': 'پدینگتون',
            'icon': '🧸',
            'search_char': 'پ'
        }, {
            'id': 'baby_8',
            'name': 'دریم بیگ',
            'icon': '💤',
            'search_char': 'د'
        }, {
            'id': 'baby_9',
            'name': 'رینبو',
            'icon': '🌈',
            'search_char': 'ر'
        }, {
            'id': 'baby_10',
            'name': 'سوفی',
            'icon': '👶',
            'search_char': 'س'
        }, {
            'id': 'baby_11',
            'name': 'شوکا',
            'icon': '🍭',
            'search_char': 'ش'
        }, {
            'id': 'baby_12',
            'name': 'فارست',
            'icon': '🌲',
            'search_char': 'ف'
        }, {
            'id': 'baby_13',
            'name': 'کیوت بیر',
            'icon': '🧸',
            'search_char': 'ک'
        }, {
            'id': 'baby_14',
            'name': 'لئو',
            'icon': '🦁',
            'search_char': 'ل'
        }, {
            'id': 'baby_15',
            'name': 'مدل ویکی',
            'icon': '🦄',
            'search_char': 'م'
        }, {
            'id': 'baby_16',
            'name': 'ولکام',
            'icon': '🎉',
            'search_char': 'و'
        }, {
            'id': 'baby_17',
            'name': 'هپی طوسی',
            'icon': '😊',
            'search_char': 'ه'
        }, {
            'id': 'baby_18',
            'name': 'هپی صورتی',
            'icon': '💖',
            'search_char': 'ه'
        }, {
            'id': 'baby_19',
            'name': 'یونیکورن',
            'icon': '🦄',
            'search_char': 'ی'
        }]
    },
    'teen': {
        'name':
        '🧒 کالای خواب نوجوان',
        'price':
        4780000,
        'products': [{
            'id': 'teen_1',
            'name': 'آرتا طوسی',
            'icon': '🎨',
            'search_char': 'آ'
        }, {
            'id': 'teen_2',
            'name': 'A4 سورمه ایی',
            'icon': '📄',
            'search_char': 'ا'
        }, {
            'id': 'teen_3',
            'name': 'بالرین سبز چین دار',
            'icon': '🩰',
            'search_char': 'ب'
        }, {
            'id': 'teen_4',
            'name': 'بالرین سبز بدون چین',
            'icon': '💚',
            'search_char': 'ب'
        }, {
            'id': 'teen_5',
            'name': 'بالرین طوسی چین دار',
            'icon': '🩰',
            'search_char': 'ب'
        }, {
            'id': 'teen_6',
            'name': 'بالرین طوسی بدون چین',
            'icon': '🤍',
            'search_char': 'ب'
        }, {
            'id': 'teen_7',
            'name': 'پارادایس',
            'icon': '🏝️',
            'search_char': 'پ'
        }, {
            'id': 'teen_8',
            'name': 'گیم',
            'icon': '🎯',
            'search_char': 'گ'
        }, {
            'id': 'teen_9',
            'name': 'گوتیک',
            'icon': '🖤',
            'search_char': 'گ'
        }, {
            'id': 'teen_10',
            'name': 'گرافیت طوسی',
            'icon': '✏️',
            'search_char': 'گ'
        }, {
            'id': 'teen_11',
            'name': 'کاج',
            'icon': '🌲',
            'search_char': 'ک'
        }, {
            'id': 'teen_12',
            'name': 'کارن A4 سورمه ایی',
            'icon': '📋',
            'search_char': 'ک'
        }, {
            'id': 'teen_13',
            'name': 'مدل گیم قرمز',
            'icon': '🎮',
            'search_char': 'م'
        }, {
            'id': 'teen_14',
            'name': 'فضا',
            'icon': '🚀',
            'search_char': 'ف'
        }]
    },
    'adult': {
        'name':
        '👨 کالای خواب بزرگسال',
        'price':
        5600000,
        'products': [{
            'id': 'adult_1',
            'name': 'آوانگارد',
            'icon': '🎭',
            'search_char': 'آ'
        }, {
            'id': 'adult_2',
            'name': 'آرتا طوسی',
            'icon': '🎨',
            'search_char': 'آ'
        }, {
            'id': 'adult_3',
            'name': 'برگ طوسی',
            'icon': '🍃',
            'search_char': 'ب'
        }, {
            'id': 'adult_4',
            'name': 'بوهو',
            'icon': '🌻',
            'search_char': 'ب'
        }, {
            'id': 'adult_5',
            'name': 'پارادایس طوسی',
            'icon': '🏖️',
            'search_char': 'پ'
        }, {
            'id': 'adult_6',
            'name': 'فرشته',
            'icon': '😇',
            'search_char': 'ف'
        }, {
            'id': 'adult_7',
            'name': 'گوتیک',
            'icon': '🖤',
            'search_char': 'گ'
        }, {
            'id': 'adult_8',
            'name': 'هلن',
            'icon': '👑',
            'search_char': 'ه'
        }]
    },
    'curtain_only': {
        'name':
        '🪟 پرده',
        'price':
        1550000,
        'products': [{
            'id': 'curtain_1',
            'name': 'فارست',
            'icon': '🌲',
            'search_char': 'ف'
        }, {
            'id': 'curtain_2',
            'name': 'گیم',
            'icon': '🎮',
            'search_char': 'گ'
        }, {
            'id': 'curtain_3',
            'name': 'کیوت بیر',
            'icon': '🧸',
            'search_char': 'ک'
        }, {
            'id': 'curtain_4',
            'name': 'بو',
            'icon': '👻',
            'search_char': 'ب'
        }, {
            'id': 'curtain_5',
            'name': 'پدینگتون',
            'icon': '🧸',
            'search_char': 'پ'
        }, {
            'id': 'curtain_6',
            'name': 'آنجل',
            'icon': '👼',
            'search_char': 'آ'
        }, {
            'id': 'curtain_7',
            'name': 'الیسون',
            'icon': '🌸',
            'search_char': 'ا'
        }, {
            'id': 'curtain_8',
            'name': 'ولکام',
            'icon': '🎉',
            'search_char': 'و'
        }, {
            'id': 'curtain_9',
            'name': 'دریم بیگ',
            'icon': '💤',
            'search_char': 'د'
        }, {
            'id': 'curtain_10',
            'name': 'چیکو',
            'icon': '🐥',
            'search_char': 'چ'
        }, {
            'id': 'curtain_11',
            'name': 'ویکی',
            'icon': '🦄',
            'search_char': 'و'
        }, {
            'id': 'curtain_12',
            'name': 'هپی طوسی',
            'icon': '😊',
            'search_char': 'ه'
        }, {
            'id': 'curtain_13',
            'name': 'هپی صورتی',
            'icon': '💖',
            'search_char': 'ه'
        }, {
            'id': 'curtain_14',
            'name': 'یونیکورن',
            'icon': '🦄',
            'search_char': 'ی'
        }, {
            'id': 'curtain_15',
            'name': 'پرده حریر سرتخت (جفت)',
            'icon': '🪟',
            'search_char': 'پ'
        }, {
            'id': 'curtain_16',
            'name': 'رینبو',
            'icon': '🌈',
            'search_char': 'ر'
        }, {
            'id': 'curtain_17',
            'name': 'GT قرمز',
            'icon': '🏎️',
            'search_char': 'گ'
        }]
    },
    'cushion': {
        'name':
        '🧸 کوسن و عروسک',
        'price':
        2800000,
        'products': [{
            'id': 'cushion_5',
            'name': 'کوسن مخمل گیم دسته بازی سفید',
            'icon': '🎮',
            'search_char': 'ک'
        }, {
            'id': 'cushion_6',
            'name': 'کوسن مخمل گیم zone',
            'icon': '🎯',
            'search_char': 'ک'
        }, {
            'id': 'cushion_7',
            'name': 'کوسن مخمل awsd',
            'icon': '⌨️',
            'search_char': 'ک'
        }, {
            'id': 'cushion_8',
            'name': 'کوسن مخمل ENTER',
            'icon': '⏎',
            'search_char': 'ک'
        }, {
            'id': 'cushion_9',
            'name': 'کوسن مخمل گیم PS-KING',
            'icon': '🎮',
            'search_char': 'ک'
        }, {
            'id': 'cushion_10',
            'name': 'کوسن مخمل گیم دسته بازی سیاه',
            'icon': '🖤',
            'search_char': 'ک'
        }]
    },
    'tablecloth': {
        'name':
        'فرشینه',
        'price':
        2400000,  # Base price for smallest size
        'products': [{
            'id': 'tablecloth_1',
            'name': 'کیوت بیر',
            'icon': '🧸',
            'search_char': 'ک'
        }, {
            'id': 'tablecloth_2',
            'name': 'مدل فارست',
            'icon': '🌲',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_3',
            'name': 'مدل گیم',
            'icon': '🎮',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_4',
            'name': 'مدل رینبو',
            'icon': '🌈',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_5',
            'name': 'مدل بو',
            'icon': '👻',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_6',
            'name': 'مدل پدینگتون',
            'icon': '🧸',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_7',
            'name': 'مدل هپی سیتی',
            'icon': '🏙️',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_8',
            'name': 'مدل هپی طوسی',
            'icon': '😊',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_9',
            'name': 'مدل GTA',
            'icon': '🚗',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_10',
            'name': 'مدل یونیکورن',
            'icon': '🦄',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_11',
            'name': 'مدل باستر',
            'icon': '🚀',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_12',
            'name': 'مدل الیسون',
            'icon': '🌸',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_13',
            'name': 'مدل race',
            'icon': '🏁',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_14',
            'name': 'مدل هپی صورتی',
            'icon': '💖',
            'search_char': 'م'
        }, {
            'id': 'tablecloth_15',
            'name': 'مدل ولکام',
            'icon': '🎉',
            'search_char': 'م'
        }]
    }
}


def get_products_by_category(category_id: str) -> List[Dict[str, Any]]:
    """Get all products for a specific category"""
    category = PRODUCT_CATEGORIES.get(category_id, {})
    products = category.get('products', [])

    # Add category_id to each product
    for product in products:
        product['category_id'] = category_id

    return products


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Find a product by its ID across all categories"""
    for category_id, category_info in PRODUCT_CATEGORIES.items():
        for product in category_info.get('products', []):
            if product['id'] == product_id:
                product['category_id'] = category_id
                # Add special price if exists
                if product_id in SPECIAL_PRODUCT_PRICES:
                    product['special_price'] = SPECIAL_PRODUCT_PRICES[
                        product_id]
                return product
    return None


def get_product_price(product_id: str, category_id: str, size: str = None, fabric: str = None) -> int:
    """Get price for a specific product, checking for special pricing first"""
    if product_id in SPECIAL_PRODUCT_PRICES:
        return SPECIAL_PRODUCT_PRICES[product_id]
    
    # Size-based pricing for tablecloth category
    if category_id == 'tablecloth' and size and size in TABLECLOTH_SIZE_PRICES:
        return TABLECLOTH_SIZE_PRICES[size]
    
    # Fabric-based pricing for curtains
    if category_id == 'curtain_only' and fabric and fabric in CURTAIN_FABRIC_PRICES:
        return CURTAIN_FABRIC_PRICES[fabric]
    
    return PRODUCT_PRICES.get(category_id, 2800000)


def search_products_by_name(
        category_id: str,
        search_letter: str,
        subcategory_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search products by first letter in a category"""
    # Handle subcategory mapping
    actual_category = subcategory_id if subcategory_id else category_id

    products = get_products_by_category(actual_category)

    # Filter by first letter
    filtered_products = []
    for product in products:
        if product.get('search_char', '').startswith(search_letter):
            filtered_products.append(product)

    return filtered_products


def get_category_info(category_id: str) -> Dict[str, Any]:
    """Get category information"""
    return PRODUCT_CATEGORIES.get(category_id, {})


def get_all_categories() -> Dict[str, Any]:
    """Get all product categories"""
    return PRODUCT_CATEGORIES


def get_category_product_icons(category_id: str) -> List[tuple]:
    """Get individual products with their icons and descriptions for a category"""
    products = get_products_by_category(category_id)

    # Return individual products instead of grouping
    result = []
    for product in products:
        icon = product.get('icon', '🛍️')
        description = product['name']  # Just the product name without emoji
        result.append((icon, description,
                       product['id']))  # Include product ID for callback

    return result


def search_products_by_icon(category_id: str,
                            target_icon: str) -> List[Dict[str, Any]]:
    """Search products by icon in a category"""
    products = get_products_by_category(category_id)

    # Filter by icon
    filtered_products = []
    for product in products:
        if product.get('icon', '🛍️') == target_icon:
            filtered_products.append(product)

    return filtered_products
