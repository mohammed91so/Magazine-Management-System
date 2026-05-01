"""
Unit tests for sales service layer.
"""

import pytest
from services.sales_service import sell_product, get_sales_history
from services.inventory_service import create_product
from utils.validators import ValidationError


class TestSalesService:
    """Test sales service layer."""
    
    def test_sell_product(self, temp_db):
        product_id = create_product("Test Product", 10.0, 15.0, 50, "2030-12-31")
        
        result = sell_product(product_id, 5)
        
        assert result["product_name"] == "Test Product"
        assert result["quantity"] == 5
        assert result["total_price"] == 75.0
        assert result["profit"] == 25.0
        
        # Verify stock decreased
        from services.inventory_service import get_product
        product = get_product(product_id)
        assert product["quantity"] == 45
    
    def test_sell_product_invalid_quantity(self, temp_db):
        product_id = create_product("Test", 10.0, 15.0, 50, "2030-12-31")
        
        with pytest.raises(ValidationError, match="Quantity must be greater than zero"):
            sell_product(product_id, 0)
        
        with pytest.raises(ValidationError, match="Quantity cannot be negative"):
            sell_product(product_id, -5)
    
    def test_sell_product_insufficient_stock(self, temp_db):
        product_id = create_product("Test", 10.0, 15.0, 10, "2030-12-31")
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            sell_product(product_id, 20)
    
    def test_sell_product_expired(self, temp_db):
        product_id = create_product("Expired", 10.0, 15.0, 50, "2020-01-01")
        
        with pytest.raises(ValueError, match="Cannot sell expired product"):
            sell_product(product_id, 5)
    
    def test_sell_product_not_found(self, temp_db):
        with pytest.raises(ValueError, match="Product not found"):
            sell_product(99999, 5)
    
    def test_get_sales_history(self, temp_db):
        product_id = create_product("Test", 10.0, 15.0, 50, "2030-12-31")
        
        sell_product(product_id, 5)
        sell_product(product_id, 3)
        
        history = get_sales_history()
        assert len(history) == 2
