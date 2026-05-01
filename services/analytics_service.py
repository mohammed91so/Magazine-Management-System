"""
Analytics service layer for dashboard metrics and insights.

Provides business intelligence and reporting functions.
"""

from typing import List, Dict, Any

from database import queries
from utils.logging_config import logger


# ----------------------------
# 📊 DASHBOARD METRICS
# ----------------------------

def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Get comprehensive dashboard metrics.
    
    Returns:
        Dictionary with all dashboard metrics including:
        - total_earnings: Total revenue from sales
        - total_profit: Total profit from sales
        - total_investment: Current inventory value
        - total_products: Number of unique products
        - low_stock_count: Products below threshold
        - out_of_stock_count: Products with zero stock
        - expired_count: Expired products
        - expiring_soon_count: Products expiring within 7 days
    """
    metrics = {
        "total_earnings": queries.get_total_earnings(),
        "total_profit": queries.get_total_profit(),
        "total_investment": queries.get_total_investment(),
        "total_products": queries.get_total_products(),
        "low_stock_count": len(queries.get_low_stock_products()),
        "out_of_stock_count": len(queries.get_out_of_stock_products()),
        "expired_count": len(queries.get_expired_products()),
        "expiring_soon_count": len(queries.get_expiring_soon_products()),
    }
    
    logger.debug(f"Dashboard metrics retrieved: {metrics}")
    return metrics


# ----------------------------
# 📈 INSIGHTS
# ----------------------------

def get_best_selling_products(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get best-selling products by quantity sold.
    
    Args:
        limit: Number of products to return.
        
    Returns:
        List of best-selling products with name and total_sold.
    """
    return queries.get_best_selling_products(limit)