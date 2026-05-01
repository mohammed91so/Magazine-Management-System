"""
Unit tests for analytics service layer.
"""

import pytest
from services.analytics_service import get_dashboard_metrics, get_best_selling_products
from services.inventory_service import create_product
from services.sales_service import sell_product


class TestAnalyticsService:
    """Test analytics service layer."""
    
    def test_get_dashboard_metrics(self, temp_db):
        product_id = create_product("Test", 10.0, 15.0, 50, "2030-12-31")
        sell_product(product_id, 5)
        
        metrics = get_dashboard_metrics()
        
        assert "total_earnings" in metrics
        assert "total_profit" in metrics
        assert "total_investment" in metrics
        assert "total_products" in metrics
        assert "low_stock_count" in metrics
        assert "out_of_stock_count" in metrics
        assert "expired_count" in metrics
        assert "expiring_soon_count" in metrics
        
        assert metrics["total_earnings"] == 75.0
        assert metrics["total_profit"] == 25.0
        assert metrics["total_products"] == 1
    
    def test_get_best_selling_products(self, temp_db):
        product_id = create_product("Best Seller", 10.0, 15.0, 50, "2030-12-31")
        
        sell_product(product_id, 10)
        sell_product(product_id, 5)
        
        best_sellers = get_best_selling_products(limit=5)
        
        assert len(best_sellers) >= 1
        assert best_sellers[0]["name"] == "Best Seller"
        assert best_sellers[0]["total_sold"] == 15
