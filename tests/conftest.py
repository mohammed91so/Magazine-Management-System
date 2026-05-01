"""
Pytest configuration and fixtures for the inventory system tests.
"""

import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pytest

from config.settings import settings


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    temp_db_path = Path(temp_dir) / "test_inventory.db"
    
    # Store original DB path
    original_db_path = settings.DB_PATH
    
    # Override DB path
    settings.DB_PATH = temp_db_path
    
    # Initialize test database
    from database.db import initialize_db
    initialize_db()
    
    yield temp_db_path
    
    # Cleanup
    settings.DB_PATH = original_db_path
    if temp_db_path.exists():
        temp_db_path.unlink()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_product(temp_db):
    """Create a sample product for testing."""
    from database.queries import add_product
    
    product_id = add_product(
        name="Test Product",
        purchase_price=10.0,
        selling_price=15.0,
        quantity=50,
        expiration_date="2030-12-31"
    )
    
    return product_id


@pytest.fixture
def sample_products(temp_db):
    """Create multiple sample products for testing."""
    from database.queries import add_product
    
    product_ids = []
    
    # Product 1 - Normal stock
    product_ids.append(add_product(
        name="Canned Beans",
        purchase_price=2.50,
        selling_price=4.00,
        quantity=100,
        expiration_date="2030-12-31"
    ))
    
    # Product 2 - Low stock
    product_ids.append(add_product(
        name="Canned Corn",
        purchase_price=3.00,
        selling_price=5.00,
        quantity=5,
        expiration_date="2030-12-31"
    ))
    
    # Product 3 - Out of stock
    product_ids.append(add_product(
        name="Canned Soup",
        purchase_price=2.00,
        selling_price=3.50,
        quantity=0,
        expiration_date="2030-12-31"
    ))
    
    # Product 4 - Expired
    product_ids.append(add_product(
        name="Canned Tomatoes",
        purchase_price=1.50,
        selling_price=3.00,
        quantity=20,
        expiration_date="2020-01-01"
    ))
    
    return product_ids
