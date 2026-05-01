"""
Helper utilities for the inventory system.

Provides common utility functions used across the application.
"""

from datetime import datetime, timedelta
from typing import Optional


def format_currency(amount: float) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format.
        
    Returns:
        Formatted currency string.
    """
    return f"${amount:,.2f}"


def format_date(date_str: Optional[str], input_format: str = "%Y-%m-%d", output_format: str = "%Y-%m-%d") -> str:
    """
    Format date string.
    
    Args:
        date_str: Date string to format.
        input_format: Format of input date string.
        output_format: Desired output format.
        
    Returns:
        Formatted date string.
    """
    if not date_str:
        return "N/A"
    
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str


def get_days_until_expiration(expiration_date: str) -> int:
    """
    Calculate days until expiration.
    
    Args:
        expiration_date: Expiration date string (YYYY-MM-DD).
        
    Returns:
        Number of days until expiration (negative if expired).
    """
    try:
        exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        today = datetime.today().date()
        delta = exp_date - today
        return delta.days
    except ValueError:
        return 0


def is_expired(expiration_date: str) -> bool:
    """
    Check if product is expired.
    
    Args:
        expiration_date: Expiration date string (YYYY-MM-DD).
        
    Returns:
        True if expired, False otherwise.
    """
    return get_days_until_expiration(expiration_date) < 0


def is_expiring_soon(expiration_date: str, days_threshold: int = 7) -> bool:
    """
    Check if product is expiring soon.
    
    Args:
        expiration_date: Expiration date string (YYYY-MM-DD).
        days_threshold: Number of days threshold.
        
    Returns:
        True if expiring soon, False otherwise.
    """
    days_until = get_days_until_expiration(expiration_date)
    return 0 <= days_until <= days_threshold


def calculate_profit(selling_price: float, purchase_price: float, quantity: int) -> float:
    """
    Calculate profit from sale.
    
    Args:
        selling_price: Selling price per unit.
        purchase_price: Purchase price per unit.
        quantity: Quantity sold.
        
    Returns:
        Total profit.
    """
    return (selling_price - purchase_price) * quantity


def calculate_total_price(selling_price: float, quantity: int) -> float:
    """
    Calculate total sale price.
    
    Args:
        selling_price: Selling price per unit.
        quantity: Quantity sold.
        
    Returns:
        Total price.
    """
    return selling_price * quantity
