#!/usr/bin/env python3
"""
Shopping Cart Management
Handles cart operations with JSON file-based persistence.
"""

import json
import os
from typing import List, Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CartManager:
    """Manages shopping cart operations with file-based persistence"""
    
    def __init__(self, cart_data_dir: str = "cart_data"):
        self.cart_data_dir = cart_data_dir
        # Ensure cart data directory exists
        os.makedirs(self.cart_data_dir, exist_ok=True)
    
    def _get_cart_file_path(self, user_id: int) -> str:
        """Get the file path for a user's cart"""
        return os.path.join(self.cart_data_dir, f"cart_{user_id}.json")
    
    def get_cart(self, user_id: int) -> List[Dict[str, Any]]:
        """Get cart items for a user"""
        cart_file = self._get_cart_file_path(user_id)
        
        try:
            if os.path.exists(cart_file):
                with open(cart_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading cart for user {user_id}: {e}")
            return []
    
    def save_cart(self, user_id: int, cart_items: List[Dict[str, Any]]) -> bool:
        """Save cart items for a user"""
        cart_file = self._get_cart_file_path(user_id)
        
        try:
            with open(cart_file, 'w', encoding='utf-8') as f:
                json.dump(cart_items, f, ensure_ascii=False, indent=2)
            logger.info(f"Cart saved for user {user_id}: {len(cart_items)} items")
            return True
        except Exception as e:
            logger.error(f"Error saving cart for user {user_id}: {e}")
            return False
    
    def add_to_cart(self, user_id: int, item: Dict[str, Any]) -> bool:
        """Add an item to user's cart"""
        cart_items = self.get_cart(user_id)
        
        # Check if item already exists in cart
        existing_item = None
        for cart_item in cart_items:
            if (cart_item['product_id'] == item['product_id'] and 
                cart_item['size'] == item['size']):
                existing_item = cart_item
                break
        
        if existing_item:
            # Update quantity
            existing_item['quantity'] += item['quantity']
            logger.info(f"Updated quantity for product {item['product_id']} in cart of user {user_id}")
        else:
            # Add new item
            cart_items.append(item)
            logger.info(f"Added new product {item['product_id']} to cart of user {user_id}")
        
        return self.save_cart(user_id, cart_items)
    
    def remove_from_cart(self, user_id: int, product_id: str, size: str) -> bool:
        """Remove an item from user's cart"""
        cart_items = self.get_cart(user_id)
        
        # Find and remove the item
        cart_items = [
            item for item in cart_items 
            if not (item['product_id'] == product_id and item['size'] == size)
        ]
        
        logger.info(f"Removed product {product_id} (size {size}) from cart of user {user_id}")
        return self.save_cart(user_id, cart_items)
    
    def update_quantity(self, user_id: int, product_id: str, size: str, new_quantity: int) -> bool:
        """Update quantity of an item in user's cart"""
        cart_items = self.get_cart(user_id)
        
        for item in cart_items:
            if item['product_id'] == product_id and item['size'] == size:
                if new_quantity <= 0:
                    # Remove item if quantity is 0 or negative
                    return self.remove_from_cart(user_id, product_id, size)
                else:
                    item['quantity'] = new_quantity
                    logger.info(f"Updated quantity of product {product_id} to {new_quantity} for user {user_id}")
                    return self.save_cart(user_id, cart_items)
        
        logger.warning(f"Product {product_id} (size {size}) not found in cart of user {user_id}")
        return False
    
    def clear_cart(self, user_id: int) -> bool:
        """Clear all items from user's cart"""
        return self.save_cart(user_id, [])
    
    def get_cart_total(self, user_id: int) -> float:
        """Calculate total price of items in user's cart"""
        cart_items = self.get_cart(user_id)
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        return total
    
    def get_cart_item_count(self, user_id: int) -> int:
        """Get total number of items in user's cart"""
        cart_items = self.get_cart(user_id)
        return sum(item['quantity'] for item in cart_items)
    
    def is_cart_empty(self, user_id: int) -> bool:
        """Check if user's cart is empty"""
        cart_items = self.get_cart(user_id)
        return len(cart_items) == 0
    
    def get_cart_summary(self, user_id: int) -> Dict[str, Any]:
        """Get a summary of user's cart"""
        cart_items = self.get_cart(user_id)
        
        return {
            'items': cart_items,
            'item_count': sum(item['quantity'] for item in cart_items),
            'total_price': sum(item['price'] * item['quantity'] for item in cart_items),
            'unique_products': len(cart_items)
        }
