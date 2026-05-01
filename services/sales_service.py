"""
Sales service layer with transaction safety and validation.

Provides business logic for sales transactions.
"""

from typing import List, Dict, Any

from database import queries
from services.inventory_service import get_product, decrease_stock, get_expiration_status
from utils.validators import validate_product_id, validate_quantity, ValidationError
from utils.logging_config import logger


# ----------------------------
# 💰 CORE SALE LOGIC
# ----------------------------

def sell_product(product_id: int, quantity: int) -> Dict[str, Any]:
    """
    Process a product sale with validation and transaction safety.
    
    Args:
        product_id: Product ID to sell.
        quantity: Quantity to sell.
        
    Returns:
        Dictionary with sale details (product_name, quantity, total_price, profit).
        
    Raises:
        ValidationError: If validation fails.
        ValueError: If product not found, expired, or insufficient stock.
    """
    # Validate inputs
    product_id = validate_product_id(product_id)
    quantity = validate_quantity(quantity)
    
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero")

    # Get product
    product = get_product(product_id)

    # Check expiration
    status = get_expiration_status(product["expiration_date"])
    if status == "expired":
        logger.warning(f"Attempted to sell expired product: {product['name']} (ID: {product_id})")
        raise ValueError("Cannot sell expired product")

    # Check stock
    if quantity > product["quantity"]:
        logger.warning(f"Insufficient stock for product: {product['name']} (ID: {product_id})")
        raise ValueError("Insufficient stock")

    # Calculate totals
    selling_price = product["selling_price"]
    purchase_price = product["purchase_price"]

    total_price = selling_price * quantity
    profit = (selling_price - purchase_price) * quantity

    # Update stock (this will fail if stock check fails)
    decrease_stock(product_id, quantity)

    # Record sale
    queries.record_sale(product_id, quantity, total_price, profit)
    
    logger.info(f"Sale completed: {product['name']} x{quantity} = ${total_price:.2f} (profit: ${profit:.2f})")

    return {
        "product_name": product["name"],
        "quantity": quantity,
        "total_price": round(total_price, 2),
        "profit": round(profit, 2)
    }


# ----------------------------
# 📊 SALES HISTORY
# ----------------------------

def get_sales_history() -> List[Dict[str, Any]]:
    """
    Get complete sales history.
    
    Returns:
        List of all sales transactions.
    """
    return queries.get_all_sales()