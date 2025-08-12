#!/usr/bin/env python3
"""
Persian Language Utilities
Helper functions for Persian text processing and formatting.
"""

import re
from typing import Union

# Persian to English digit mapping
PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
ENGLISH_DIGITS = '0123456789'

# Persian to English digit translation table
PERSIAN_TO_ENGLISH = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)
ENGLISH_TO_PERSIAN = str.maketrans(ENGLISH_DIGITS, PERSIAN_DIGITS)

def persian_numbers(text: str) -> str:
    """
    Convert English numbers to Persian numbers
    
    Args:
        text: Text containing English digits
    
    Returns:
        Text with Persian digits
    """
    return text.translate(ENGLISH_TO_PERSIAN)

def english_numbers(text: str) -> str:
    """
    Convert Persian numbers to English numbers
    
    Args:
        text: Text containing Persian digits
    
    Returns:
        Text with English digits
    """
    return text.translate(PERSIAN_TO_ENGLISH)

def format_price(price: Union[int, float]) -> str:
    """
    Format price with Persian number separators
    
    Args:
        price: Price value
    
    Returns:
        Formatted price string with Persian digits and separators
    """
    if isinstance(price, float):
        price = int(price)
    
    # Add thousand separators
    price_str = f"{price:,}"
    
    # Convert to Persian digits
    price_str = persian_numbers(price_str)
    
    return price_str

def clean_persian_text(text: str) -> str:
    """
    Clean and normalize Persian text
    
    Args:
        text: Persian text to clean
    
    Returns:
        Cleaned Persian text
    """
    if not text:
        return ""
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Normalize Persian characters
    text = text.replace('ك', 'ک')  # Arabic Kaf to Persian Kaf
    text = text.replace('ي', 'ی')  # Arabic Yeh to Persian Yeh
    text = text.replace('ة', 'ه')  # Arabic Teh Marbuta to Heh
    
    return text

def is_persian_text(text: str) -> bool:
    """
    Check if text contains Persian characters
    
    Args:
        text: Text to check
    
    Returns:
        True if text contains Persian characters
    """
    persian_pattern = r'[\u0600-\u06FF\u200C\u200D]'
    return bool(re.search(persian_pattern, text))

def extract_numbers(text: str) -> list:
    """
    Extract all numbers (Persian and English) from text
    
    Args:
        text: Text to extract numbers from
    
    Returns:
        List of extracted numbers as integers
    """
    # Convert Persian digits to English first
    text = english_numbers(text)
    
    # Find all numbers
    numbers = re.findall(r'\d+', text)
    
    # Convert to integers
    return [int(num) for num in numbers]

def format_phone_number(phone: str) -> str:
    """
    Format Iranian phone number
    
    Args:
        phone: Phone number string
    
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', english_numbers(phone))
    
    # Iranian mobile number formatting
    if len(phone) == 11 and phone.startswith('09'):
        return persian_numbers(f"{phone[:4]}-{phone[4:7]}-{phone[7:]}")
    elif len(phone) == 10 and phone.startswith('9'):
        return persian_numbers(f"۰{phone[:3]}-{phone[3:6]}-{phone[6:]}")
    
    # Return as-is if doesn't match expected patterns
    return persian_numbers(phone)

def truncate_persian_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate Persian text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    
    # Try to break at word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    
    return truncated + suffix
