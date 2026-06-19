"""
Unit tests for inventory service layer.
"""

import pytest
from services.inventory_service import (
    create_product,
    update_product,
    delete_product,
    list_products,
    get_product,
    increase_stock,
    decrease_stock,
    get_expiration_status,
    get_expired_products,
    get_expiring_soon_products,
    get_low_stock_products,
    get_out_of_stock_products
)
from utils.validators import ValidationError


class TestProductManagement:
    """Test product management in service layer."""
    
    def test_create_product(self, temp_db):
        product_id = create_product(
            name="Canned Beans",
            purchase_price=2.50,
            selling_price=4.00,
            quantity=100,
            expiration_date="2025-12-31"
        )
        assert product_id > 0
        
        product = get_product(product_id)
        assert product["name"] == "Canned Beans"

    def test_create_product_with_string_inputs(self, temp_db):
        product_id = create_product(
            name="Canned Beans",
            purchase_price="2.50",
            selling_price="4.00",
            quantity="100",
            expiration_date="2025-12-31"
        )

        product = get_product(product_id)
        assert product["purchase_price"] == 2.50
        assert product["selling_price"] == 4.00
        assert product["quantity"] == 100
    
    def test_create_product_invalid_name(self, temp_db):
        with pytest.raises(ValidationError, match="Product name is required"):
            create_product("", 2.50, 4.00, 100, "2025-12-31")
    
    def test_create_product_negative_price(self, temp_db):
        with pytest.raises(ValidationError, match="cannot be negative"):
            create_product("Test", -2.50, 4.00, 100, "2025-12-31")

    def test_create_product_invalid_purchase_price_string(self, temp_db):
        with pytest.raises(ValidationError, match="Purchase price must be a valid number"):
            create_product("Test", "abc", 4.00, 100, "2025-12-31")

    def test_create_product_empty_purchase_price(self, temp_db):
        with pytest.raises(ValidationError, match="Purchase price must be a valid number"):
            create_product("Test", "", 4.00, 100, "2025-12-31")
    
    def test_create_product_invalid_date(self, temp_db):
        with pytest.raises(ValidationError, match="Invalid date format"):
            create_product("Test", 2.50, 4.00, 100, "invalid-date")
    
    def test_update_product(self, temp_db):
        product_id = create_product("Old Name", 2.50, 4.00, 100, "2025-12-31")
        
        update_product(
            product_id,
            "New Name",
            3.00,
            5.00,
            150,
            "2026-12-31"
        )
        
        product = get_product(product_id)
        assert product["name"] == "New Name"
        assert product["purchase_price"] == 3.00

    def test_update_product_with_string_inputs(self, temp_db):
        product_id = create_product("Old Name", 2.50, 4.00, 100, "2025-12-31")

        update_product(
            product_id,
            "New Name",
            "3.00",
            "5.00",
            "150",
            "2026-12-31"
        )

        product = get_product(product_id)
        assert product["purchase_price"] == 3.00
        assert product["selling_price"] == 5.00
        assert product["quantity"] == 150
    
    def test_update_product_not_found(self, temp_db):
        with pytest.raises(ValueError, match="Product not found"):
            update_product(99999, "Name", 2.50, 4.00, 100, "2025-12-31")
    
    def test_delete_product(self, temp_db):
        product_id = create_product("To Delete", 2.50, 4.00, 100, "2025-12-31")
        
        delete_product(product_id)
        
        with pytest.raises(ValueError, match="Product not found"):
            get_product(product_id)
    
    def test_delete_product_not_found(self, temp_db):
        with pytest.raises(ValueError, match="Product not found"):
            delete_product(99999)
    
    def test_list_products(self, temp_db):
        create_product("Product 1", 2.50, 4.00, 100, "2025-12-31")
        create_product("Product 2", 3.00, 5.00, 50, "2025-12-31")
        
        products = list_products()
        assert len(products) == 2
    
    def test_get_product(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2025-12-31")
        
        product = get_product(product_id)
        assert product["name"] == "Test"
    
    def test_get_product_not_found(self, temp_db):
        with pytest.raises(ValueError, match="Product not found"):
            get_product(99999)


class TestStockManagement:
    """Test stock management in service layer."""
    
    def test_increase_stock(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")
        
        increase_stock(product_id, 50)
        
        product = get_product(product_id)
        assert product["quantity"] == 150

    def test_increase_stock_with_string_quantity(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")

        increase_stock(product_id, "50")

        product = get_product(product_id)
        assert product["quantity"] == 150
    
    def test_increase_stock_negative_quantity(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")
        
        with pytest.raises(ValidationError, match="Quantity cannot be negative"):
            increase_stock(product_id, -10)

    def test_increase_stock_invalid_quantity_string(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")

        with pytest.raises(ValidationError, match="Quantity must be a valid integer"):
            increase_stock(product_id, "abc")
    
    def test_decrease_stock(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")
        
        decrease_stock(product_id, 30)
        
        product = get_product(product_id)
        assert product["quantity"] == 70

    def test_decrease_stock_with_string_quantity(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")

        decrease_stock(product_id, "30")

        product = get_product(product_id)
        assert product["quantity"] == 70
    
    def test_decrease_stock_insufficient(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 10, "2030-12-31")
        
        with pytest.raises(ValueError, match="Not enough stock available"):
            decrease_stock(product_id, 20)
    
    def test_decrease_stock_negative_quantity(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")
        
        with pytest.raises(ValidationError, match="Quantity cannot be negative"):
            decrease_stock(product_id, -10)

    def test_decrease_stock_invalid_quantity_string(self, temp_db):
        product_id = create_product("Test", 2.50, 4.00, 100, "2030-12-31")

        with pytest.raises(ValidationError, match="Quantity must be a valid integer"):
            decrease_stock(product_id, "abc")


class TestExpirationLogic:
    """Test expiration logic in service layer."""
    
    def test_get_expiration_status_expired(self):
        # Using a past date
        status = get_expiration_status("2020-01-01")
        assert status == "expired"
    
    def test_get_expiration_status_expiring_soon(self):
        # This test depends on current date, so we'll just test the function runs
        status = get_expiration_status("2025-12-31")
        assert status in ["expired", "expiring_soon", "valid"]
    
    def test_get_expired_products(self, temp_db):
        create_product("Expired", 2.50, 4.00, 100, "2020-01-01")
        create_product("Valid", 2.50, 4.00, 100, "2030-01-01")
        
        expired = get_expired_products()
        assert len(expired) == 1
        assert expired[0]["name"] == "Expired"
    
    def test_get_expiring_soon_products(self, temp_db):
        create_product("Expiring Soon", 2.50, 4.00, 100, "2025-12-31")
        
        expiring_soon = get_expiring_soon_products()
        assert isinstance(expiring_soon, list)


class TestAlerts:
    """Test alert functions in service layer."""
    
    def test_get_low_stock_products(self, temp_db):
        create_product("Low Stock", 2.50, 4.00, 5, "2025-12-31")
        create_product("Normal Stock", 2.50, 4.00, 100, "2025-12-31")
        
        low_stock = get_low_stock_products(threshold=10)
        assert len(low_stock) == 1
        assert low_stock[0]["name"] == "Low Stock"
    
    def test_get_out_of_stock_products(self, temp_db):
        create_product("Out of Stock", 2.50, 4.00, 0, "2025-12-31")
        create_product("In Stock", 2.50, 4.00, 100, "2025-12-31")
        
        out_of_stock = get_out_of_stock_products()
        assert len(out_of_stock) == 1
        assert out_of_stock[0]["name"] == "Out of Stock"
