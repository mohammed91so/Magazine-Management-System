"""
Input validation utilities for the inventory system.

Provides centralized validation for all user inputs.
"""

from datetime import datetime
from typing import Any


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_product_name(name: str) -> str:
    """
    Validate product name.
    
    Args:
        name: Product name to validate.
        
    Returns:
        Validated product name.
        
    Raises:
        ValidationError: If name is invalid.
    """
    if not name or not name.strip():
        raise ValidationError("Product name is required")
    
    name = name.strip()
    
    if len(name) < 2:
        raise ValidationError("Product name must be at least 2 characters")
    
    if len(name) > 100:
        raise ValidationError("Product name must not exceed 100 characters")
    
    return name


def validate_price(price: Any, field_name: str = "price") -> float:
    """
    Validate price value.
    
    Args:
        price: Price value to validate.
        field_name: Name of the field for error messages.
        
    Returns:
        Validated price as float.
        
    Raises:
        ValidationError: If price is invalid.
    """
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a valid number")
    
    if price_float < 0:
        raise ValidationError(f"{field_name} cannot be negative")
    
    if price_float > 1000000:
        raise ValidationError(f"{field_name} is unreasonably high")
    
    return round(price_float, 2)


def validate_quantity(quantity: Any) -> int:
    """
    Validate quantity value.
    
    Args:
        quantity: Quantity value to validate.
        
    Returns:
        Validated quantity as integer.
        
    Raises:
        ValidationError: If quantity is invalid.
    """
    try:
        quantity_int = int(quantity)
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be a valid integer")
    
    if quantity_int < 0:
        raise ValidationError("Quantity cannot be negative")
    
    if quantity_int > 100000:
        raise ValidationError("Quantity is unreasonably high")
    
    return quantity_int


def validate_expiration_date(date_str: str) -> str:
    """
    Validate expiration date format.
    
    Args:
        date_str: Date string to validate.
        
    Returns:
        Validated date string in YYYY-MM-DD format.
        
    Raises:
        ValidationError: If date is invalid.
    """
    if not date_str or not date_str.strip():
        raise ValidationError("Expiration date is required")
    
    date_str = date_str.strip()
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Invalid date format. Use YYYY-MM-DD")
    
    # Check if date is not too far in the past
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        min_date = datetime(2000, 1, 1).date()
        if date_obj < min_date:
            raise ValidationError("Date cannot be before year 2000")
    except ValueError:
        raise ValidationError("Invalid date")
    
    return date_str


def validate_product_id(product_id: Any) -> int:
    """
    Validate product ID.
    
    Args:
        product_id: Product ID to validate.
        
    Returns:
        Validated product ID as integer.
        
    Raises:
        ValidationError: If product ID is invalid.
    """
    try:
        product_id_int = int(product_id)
    except (TypeError, ValueError):
        raise ValidationError("Product ID must be a valid integer")
    
    if product_id_int <= 0:
        raise ValidationError("Product ID must be positive")
    
    return product_id_int
