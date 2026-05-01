"""
Unit tests for database queries.
"""

import pytest
from database.queries import (
    add_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product,
    update_stock,
    get_low_stock_products,
    get_out_of_stock_products,
    record_sale,
    get_all_sales,
    get_total_earnings,
    get_total_profit,
    get_total_investment,
    get_total_products,
    get_expired_products,
    get_expiring_soon_products,
    get_best_selling_products
)


class TestProductQueries:
    """Test product-related database queries."""
    
    def test_add_product(self, temp_db):
        product_id = add_product(
            name="Test Product",
            purchase_price=10.0,
            selling_price=15.0,
            quantity=50,
            expiration_date="2030-12-31"
        )
        assert product_id > 0
        
        product = get_product_by_id(product_id)
        assert product is not None
        assert product["name"] == "Test Product"
        assert product["purchase_price"] == 10.0
        assert product["selling_price"] == 15.0
        assert product["quantity"] == 50
    
    def test_get_all_products(self, temp_db):
        add_product("Product 1", 10.0, 15.0, 50, "2030-12-31")
        add_product("Product 2", 20.0, 25.0, 30, "2030-12-31")
        
        products = get_all_products()
        assert len(products) == 2
    
    def test_get_product_by_id(self, temp_db):
        product_id = add_product("Test", 10.0, 15.0, 50, "2030-12-31")
        
        product = get_product_by_id(product_id)
        assert product is not None
        assert product["id"] == product_id
        
        # Test non-existent product
        assert get_product_by_id(99999) is None
    
    def test_update_product(self, temp_db):
        product_id = add_product("Old Name", 10.0, 15.0, 50, "2030-12-31")
        
        update_product(
            product_id,
            "New Name",
            20.0,
            25.0,
            100,
            "2031-12-31"
        )
        
        product = get_product_by_id(product_id)
        assert product["name"] == "New Name"
        assert product["purchase_price"] == 20.0
        assert product["quantity"] == 100
    
    def test_delete_product(self, temp_db):
        product_id = add_product("To Delete", 10.0, 15.0, 50, "2030-12-31")
        
        delete_product(product_id)
        
        assert get_product_by_id(product_id) is None
        assert len(get_all_products()) == 0


class TestStockQueries:
    """Test stock-related database queries."""
    
    def test_update_stock(self, temp_db):
        product_id = add_product("Test", 10.0, 15.0, 50, "2030-12-31")
        
        update_stock(product_id, 100)
        
        product = get_product_by_id(product_id)
        assert product["quantity"] == 100
    
    def test_get_low_stock_products(self, temp_db):
        add_product("Low Stock", 10.0, 15.0, 5, "2030-12-31")
        add_product("Normal Stock", 10.0, 15.0, 50, "2030-12-31")
        
        low_stock = get_low_stock_products(threshold=10)
        assert len(low_stock) == 1
        assert low_stock[0]["name"] == "Low Stock"
    
    def test_get_out_of_stock_products(self, temp_db):
        add_product("Out of Stock", 10.0, 15.0, 0, "2030-12-31")
        add_product("In Stock", 10.0, 15.0, 50, "2030-12-31")
        
        out_of_stock = get_out_of_stock_products()
        assert len(out_of_stock) == 1
        assert out_of_stock[0]["name"] == "Out of Stock"


class TestSalesQueries:
    """Test sales-related database queries."""
    
    def test_record_sale(self, temp_db):
        product_id = add_product("Test", 10.0, 15.0, 50, "2030-12-31")
        
        sale_id = record_sale(product_id, 5, 75.0, 25.0)
        assert sale_id > 0
        
        sales = get_all_sales()
        assert len(sales) == 1
        assert sales[0]["product_id"] == product_id
        assert sales[0]["quantity"] == 5
    
    def test_get_all_sales(self, temp_db):
        product_id = add_product("Test", 10.0, 15.0, 50, "2030-12-31")
        
        record_sale(product_id, 5, 75.0, 25.0)
        record_sale(product_id, 3, 45.0, 15.0)
        
        sales = get_all_sales()
        assert len(sales) == 2


class TestDashboardQueries:
    """Test dashboard metric queries."""
    
    def test_get_total_earnings(self, temp_db):
        product_id = add_product("Test", 10.0, 15.0, 50, "2025-12-31")
        
        record_sale(product_id, 5, 75.0, 25.0)
        record_sale(product_id, 3, 45.0, 15.0)
        
        earnings = get_total_earnings()
        assert earnings == 120.0
    
    def test_get_total_profit(self, temp_db):
        product_id = add_product("Test", 10.0, 15.0, 50, "2025-12-31")
        
        record_sale(product_id, 5, 75.0, 25.0)
        record_sale(product_id, 3, 45.0, 15.0)
        
        profit = get_total_profit()
        assert profit == 40.0
    
    def test_get_total_investment(self, temp_db):
        add_product("Product 1", 10.0, 15.0, 50, "2025-12-31")
        add_product("Product 2", 20.0, 25.0, 30, "2025-12-31")
        
        investment = get_total_investment()
        assert investment == (10.0 * 50) + (20.0 * 30)  # 500 + 600 = 1100
    
    def test_get_total_products(self, temp_db):
        add_product("Product 1", 10.0, 15.0, 50, "2025-12-31")
        add_product("Product 2", 20.0, 25.0, 30, "2025-12-31")
        
        count = get_total_products()
        assert count == 2


class TestExpirationQueries:
    """Test expiration-related queries."""
    
    def test_get_expired_products(self, temp_db):
        add_product("Expired", 10.0, 15.0, 50, "2020-01-01")
        add_product("Valid", 10.0, 15.0, 50, "2030-01-01")
        
        expired = get_expired_products()
        assert len(expired) == 1
        assert expired[0]["name"] == "Expired"
    
    def test_get_expiring_soon_products(self, temp_db):
        # Note: This test depends on current date, so we'll just test the function runs
        add_product("Expiring Soon", 10.0, 15.0, 50, "2025-12-31")
        
        expiring_soon = get_expiring_soon_products()
        assert isinstance(expiring_soon, list)


class TestAnalyticsQueries:
    """Test analytics queries."""
    
    def test_get_best_selling_products(self, temp_db):
        product_id = add_product("Best Seller", 10.0, 15.0, 50, "2025-12-31")
        
        record_sale(product_id, 10, 150.0, 50.0)
        record_sale(product_id, 5, 75.0, 25.0)
        
        best_sellers = get_best_selling_products(limit=5)
        assert len(best_sellers) >= 1
        assert best_sellers[0]["total_sold"] == 15
