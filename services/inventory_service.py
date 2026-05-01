"""
Inventory service layer with transaction safety and validation.

Provides business logic for product and inventory management.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from database import queries
from utils.validators import (
    validate_product_name,
    validate_price,
    validate_quantity,
    validate_expiration_date,
    validate_product_id,
    ValidationError
)
from utils.logging_config import logger


# ----------------------------
# 📦 PRODUCT MANAGEMENT
# ----------------------------

def create_product(name: str, purchase_price: float, selling_price: float, quantity: int, expiration_date: str) -> int:
    """
    Create a new product with validation.
    
    Args:
        name: Product name.
        purchase_price: Purchase price per unit.
        selling_price: Selling price per unit.
        quantity: Initial stock quantity.
        expiration_date: Expiration date (YYYY-MM-DD).
        
    Returns:
        ID of the created product.
        
    Raises:
        ValidationError: If validation fails.
    """
    # Validate inputs
    name = validate_product_name(name)
    purchase_price = validate_price(purchase_price, "Purchase price")
    selling_price = validate_price(selling_price, "Selling price")
    quantity = validate_quantity(quantity)
    expiration_date = validate_expiration_date(expiration_date)
    
    # Create product
    product_id = queries.add_product(name, purchase_price, selling_price, quantity, expiration_date)
    logger.info(f"Created product: {name} (ID: {product_id})")
    
    return product_id


def update_product(product_id: int, name: str, purchase_price: float, selling_price: float, quantity: int, expiration_date: str) -> None:
    """
    Update an existing product with validation.
    
    Args:
        product_id: Product ID to update.
        name: New product name.
        purchase_price: New purchase price.
        selling_price: New selling price.
        quantity: New quantity.
        expiration_date: New expiration date.
        
    Raises:
        ValidationError: If validation fails.
        ValueError: If product not found.
    """
    # Validate product ID
    product_id = validate_product_id(product_id)
    
    # Check if product exists
    existing = queries.get_product_by_id(product_id)
    if not existing:
        raise ValueError("Product not found")
    
    # Validate inputs
    name = validate_product_name(name)
    purchase_price = validate_price(purchase_price, "Purchase price")
    selling_price = validate_price(selling_price, "Selling price")
    quantity = validate_quantity(quantity)
    expiration_date = validate_expiration_date(expiration_date)
    
    # Update product
    queries.update_product(product_id, name, purchase_price, selling_price, quantity, expiration_date)
    logger.info(f"Updated product ID {product_id}: {name}")


def delete_product(product_id: int) -> None:
    """
    Delete a product by ID.
    
    Args:
        product_id: Product ID to delete.
        
    Raises:
        ValidationError: If validation fails.
        ValueError: If product not found.
    """
    # Validate product ID
    product_id = validate_product_id(product_id)
    
    # Check if product exists
    existing = queries.get_product_by_id(product_id)
    if not existing:
        raise ValueError("Product not found")
    
    # Delete product
    queries.delete_product(product_id)
    logger.info(f"Deleted product ID {product_id}")


def list_products() -> List[Dict[str, Any]]:
    """
    Get all products.
    
    Returns:
        List of all products.
    """
    return queries.get_all_products()


def get_product(product_id: int) -> Dict[str, Any]:
    """
    Get a product by ID.
    
    Args:
        product_id: Product ID.
        
    Returns:
        Product data.
        
    Raises:
        ValidationError: If validation fails.
        ValueError: If product not found.
    """
    # Validate product ID
    product_id = validate_product_id(product_id)
    
    # Get product
    product = queries.get_product_by_id(product_id)
    if not product:
        raise ValueError("Product not found")
    
    return product


# ----------------------------
# 📊 STOCK MANAGEMENT
# ----------------------------

def increase_stock(product_id: int, quantity: int) -> None:
    """
    Increase stock for a product.
    
    Args:
        product_id: Product ID.
        quantity: Quantity to add.
        
    Raises:
        ValidationError: If validation fails.
        ValueError: If product not found.
    """
    # Validate inputs
    product_id = validate_product_id(product_id)
    quantity = validate_quantity(quantity)
    
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    # Get product
    product = get_product(product_id)
    
    # Update stock
    new_quantity = product["quantity"] + quantity
    queries.update_stock(product_id, new_quantity)
    logger.info(f"Increased stock for product {product_id} by {quantity} (new: {new_quantity})")


def decrease_stock(product_id: int, quantity: int) -> None:
    """
    Decrease stock for a product.
    
    Args:
        product_id: Product ID.
        quantity: Quantity to subtract.
        
    Raises:
        ValidationError: If validation fails.
        ValueError: If product not found or insufficient stock.
    """
    # Validate inputs
    product_id = validate_product_id(product_id)
    quantity = validate_quantity(quantity)
    
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    # Get product
    product = get_product(product_id)
    
    # Check stock
    if quantity > product["quantity"]:
        raise ValueError("Not enough stock available")
    
    # Update stock
    new_quantity = product["quantity"] - quantity
    queries.update_stock(product_id, new_quantity)
    logger.info(f"Decreased stock for product {product_id} by {quantity} (new: {new_quantity})")


# ----------------------------
# ⏳ EXPIRATION LOGIC
# ----------------------------

def get_expiration_status(expiration_date: str) -> str:
    """
    Get expiration status of a product.
    
    Args:
        expiration_date: Expiration date (YYYY-MM-DD).
        
    Returns:
        Status: "expired", "expiring_soon", or "valid".
    """
    today = datetime.today().date()
    exp = datetime.strptime(expiration_date, "%Y-%m-%d").date()

    if exp < today:
        return "expired"
    elif exp <= today + timedelta(days=7):
        return "expiring_soon"
    return "valid"


def get_expired_products() -> List[Dict[str, Any]]:
    """Get all expired products."""
    return queries.get_expired_products()


def get_expiring_soon_products() -> List[Dict[str, Any]]:
    """Get products expiring within 7 days."""
    return queries.get_expiring_soon_products()


# ----------------------------
# 🚨 ALERTS
# ----------------------------

def get_low_stock_products(threshold: int = 10) -> List[Dict[str, Any]]:
    """
    Get products with low stock.
    
    Args:
        threshold: Stock threshold.
        
    Returns:
        List of low stock products.
    """
    return queries.get_low_stock_products(threshold)


def get_out_of_stock_products() -> List[Dict[str, Any]]:
    """Get products with zero stock."""
    return queries.get_out_of_stock_products()