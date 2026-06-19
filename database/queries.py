"""
Database queries for the inventory system.

Provides all CRUD operations and analytics queries with transaction support.
"""

from typing import List, Optional, Dict, Any

from database.db import get_connection
from utils.logging_config import logger


# ----------------------------
# 📦 PRODUCT QUERIES
# ----------------------------

def add_product(name: str, purchase_price: float, selling_price: float, quantity: int, expiration_date: str) -> int:
    """Add a new product to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, purchase_price, selling_price, quantity, expiration_date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, purchase_price, selling_price, quantity, expiration_date))

    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Added product: {name} (ID: {product_id})")
    return product_id


def get_all_products() -> List[Dict[str, Any]]:
    """Get all products ordered by creation date."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Get a product by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


def update_product(product_id: int, name: str, purchase_price: float, selling_price: float, quantity: int, expiration_date: str) -> None:
    """Update an existing product."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, purchase_price = ?, selling_price = ?, quantity = ?, expiration_date = ?
        WHERE id = ?
    """, (name, purchase_price, selling_price, quantity, expiration_date, product_id))

    conn.commit()
    conn.close()
    logger.info(f"Updated product ID {product_id}: {name}")


def delete_product(product_id: int) -> None:
    """Delete a product by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()
    logger.info(f"Deleted product ID {product_id}")


# ----------------------------
# 📊 INVENTORY HELPERS
# ----------------------------

def update_stock(product_id: int, new_quantity: int) -> None:
    """Update product stock quantity."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET quantity = ?
        WHERE id = ?
    """, (new_quantity, product_id))

    conn.commit()
    conn.close()
    logger.debug(f"Updated stock for product {product_id} to {new_quantity}")


def get_low_stock_products(threshold: int = 10) -> List[Dict[str, Any]]:
    """Get products with stock below threshold."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE quantity < ?
        ORDER BY quantity ASC
    """, (threshold,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_out_of_stock_products() -> List[Dict[str, Any]]:
    """Get products with zero stock."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE quantity = 0
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ----------------------------
# 💰 SALES QUERIES
# ----------------------------

def record_sale(product_id: int, quantity: int, total_price: float, profit: float) -> int:
    """Record a sales transaction."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sales (product_id, quantity, total_price, profit)
        VALUES (?, ?, ?, ?)
    """, (product_id, quantity, total_price, profit))

    sale_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Recorded sale: product_id={product_id}, quantity={quantity}, profit={profit}")
    return sale_id


def record_sale_transaction(product_id: int, quantity: int, total_price: float, profit: float) -> int:
    """
    Record a sale and decrement stock in a single transaction.

    Args:
        product_id: Product ID being sold.
        quantity: Quantity sold.
        total_price: Total sale price.
        profit: Total profit for the sale.

    Returns:
        The created sale ID.

    Raises:
        ValueError: If the product is missing or stock is insufficient.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        product_row = cursor.fetchone()
        if not product_row:
            raise ValueError("Product not found")

        current_quantity = product_row["quantity"]
        if quantity > current_quantity:
            raise ValueError("Insufficient stock")

        new_quantity = current_quantity - quantity
        cursor.execute("""
            UPDATE products
            SET quantity = ?
            WHERE id = ?
        """, (new_quantity, product_id))

        cursor.execute("""
            INSERT INTO sales (product_id, quantity, total_price, profit)
            VALUES (?, ?, ?, ?)
        """, (product_id, quantity, total_price, profit))

        sale_id = cursor.lastrowid
        conn.commit()
        logger.info(
            f"Recorded transactional sale: product_id={product_id}, quantity={quantity}, profit={profit}"
        )
        return sale_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_sales() -> List[Dict[str, Any]]:
    """Get all sales with product names."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, p.name AS product_name
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        ORDER BY s.date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ----------------------------
# 📈 DASHBOARD QUERIES
# ----------------------------

def get_total_earnings() -> float:
    """Get total earnings from all sales."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(total_price) as total FROM sales")
    result = cursor.fetchone()

    conn.close()
    return result["total"] if result["total"] else 0


def get_total_profit() -> float:
    """Get total profit from all sales."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(profit) as total FROM sales")
    result = cursor.fetchone()

    conn.close()
    return result["total"] if result["total"] else 0


def get_total_investment() -> float:
    """Get total investment in current inventory."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(purchase_price * quantity) as total FROM products
    """)
    result = cursor.fetchone()

    conn.close()
    return result["total"] if result["total"] else 0


def get_total_products() -> int:
    """Get total number of products."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM products")
    result = cursor.fetchone()

    conn.close()
    return result["total"]


# ----------------------------
# ⏳ EXPIRATION QUERIES
# ----------------------------

def get_expired_products() -> List[Dict[str, Any]]:
    """Get all expired products."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE date(expiration_date) < date('now')
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_expiring_soon_products(days: int = 7) -> List[Dict[str, Any]]:
    """Get products expiring within specified days."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT * FROM products
        WHERE date(expiration_date)
        BETWEEN date('now') AND date('now', '+{days} days')
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ----------------------------
# 📊 ANALYTICS (BONUS)
# ----------------------------

def get_best_selling_products(limit: int = 5) -> List[Dict[str, Any]]:
    """Get best-selling products by quantity sold."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, SUM(s.quantity) as total_sold
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY s.product_id
        ORDER BY total_sold DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
