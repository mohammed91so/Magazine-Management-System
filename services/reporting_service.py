"""
Reporting service for Excel exports.

Provides sales summary and inventory snapshot exports using pandas and openpyxl.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import pandas as pd

from database import queries
from services.analytics_service import get_dashboard_metrics
from utils.logging_config import logger


class ReportingService:
    """Service for generating Excel reports."""
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize reporting service.
        
        Args:
            output_dir: Directory to save reports. Defaults to current directory.
        """
        self.output_dir = output_dir or Path.cwd()
    
    def export_sales_report(self, filename: str = None) -> Path:
        """
        Export sales summary to Excel.
        
        Args:
            filename: Optional filename. If not provided, generates timestamped name.
            
        Returns:
            Path to the generated Excel file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_report_{timestamp}.xlsx"
        
        output_path = self.output_dir / filename
        
        try:
            # Get sales data
            sales = queries.get_all_sales()
            
            if not sales:
                logger.warning("No sales data to export")
                raise ValueError("No sales data available")
            
            # Create DataFrame
            df = pd.DataFrame(sales)
            
            # Select and rename columns
            df = df[["id", "product_name", "quantity", "total_price", "profit", "date"]]
            df.columns = ["Sale ID", "Product", "Quantity", "Total Price", "Profit", "Date"]
            
            # Calculate summary statistics
            total_sales = df["Total Price"].sum()
            total_profit = df["Profit"].sum()
            total_quantity = df["Quantity"].sum()
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                # Sales data sheet
                df.to_excel(writer, sheet_name="Sales", index=False)
                
                # Summary sheet
                summary_data = {
                    "Metric": ["Total Sales", "Total Profit", "Total Quantity Sold", "Number of Transactions"],
                    "Value": [total_sales, total_profit, total_quantity, len(sales)]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            logger.info(f"Sales report exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export sales report: {e}")
            raise
    
    def export_inventory_report(self, filename: str = None) -> Path:
        """
        Export inventory snapshot to Excel.
        
        Args:
            filename: Optional filename. If not provided, generates timestamped name.
            
        Returns:
            Path to the generated Excel file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inventory_report_{timestamp}.xlsx"
        
        output_path = self.output_dir / filename
        
        try:
            # Get inventory data
            products = queries.get_all_products()
            
            if not products:
                logger.warning("No inventory data to export")
                raise ValueError("No inventory data available")
            
            # Create DataFrame
            df = pd.DataFrame(products)
            
            # Select and rename columns
            df = df[["id", "name", "purchase_price", "selling_price", "quantity", "expiration_date", "created_at"]]
            df.columns = ["ID", "Name", "Purchase Price", "Selling Price", "Quantity", "Expiration Date", "Date Added"]
            
            # Calculate additional columns
            df["Potential Revenue"] = df["Selling Price"] * df["Quantity"]
            df["Total Investment"] = df["Purchase Price"] * df["Quantity"]
            df["Potential Profit"] = df["Potential Revenue"] - df["Total Investment"]
            
            # Calculate summary statistics
            total_products = len(df)
            total_quantity = df["Quantity"].sum()
            total_investment = df["Total Investment"].sum()
            total_potential_revenue = df["Potential Revenue"].sum()
            total_potential_profit = df["Potential Profit"].sum()
            
            # Get alert counts
            low_stock = len(queries.get_low_stock_products())
            out_of_stock = len(queries.get_out_of_stock_products())
            expired = len(queries.get_expired_products())
            expiring_soon = len(queries.get_expiring_soon_products())
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                # Inventory data sheet
                df.to_excel(writer, sheet_name="Inventory", index=False)
                
                # Summary sheet
                summary_data = {
                    "Metric": [
                        "Total Products",
                        "Total Quantity",
                        "Total Investment",
                        "Total Potential Revenue",
                        "Total Potential Profit",
                        "Low Stock Items",
                        "Out of Stock Items",
                        "Expired Items",
                        "Expiring Soon Items"
                    ],
                    "Value": [
                        total_products,
                        total_quantity,
                        total_investment,
                        total_potential_revenue,
                        total_potential_profit,
                        low_stock,
                        out_of_stock,
                        expired,
                        expiring_soon
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            logger.info(f"Inventory report exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export inventory report: {e}")
            raise
    
    def export_combined_report(self, filename: str = None) -> Path:
        """
        Export combined sales and inventory report to Excel.
        
        Args:
            filename: Optional filename. If not provided, generates timestamped name.
            
        Returns:
            Path to the generated Excel file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"combined_report_{timestamp}.xlsx"
        
        output_path = self.output_dir / filename
        
        try:
            # Get data
            sales = queries.get_all_sales()
            products = queries.get_all_products()
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                # Sales sheet
                if sales:
                    sales_df = pd.DataFrame(sales)
                    sales_df = sales_df[["id", "product_name", "quantity", "total_price", "profit", "date"]]
                    sales_df.columns = ["Sale ID", "Product", "Quantity", "Total Price", "Profit", "Date"]
                    sales_df.to_excel(writer, sheet_name="Sales", index=False)
                
                # Inventory sheet
                if products:
                    products_df = pd.DataFrame(products)
                    products_df = products_df[["id", "name", "purchase_price", "selling_price", "quantity", "expiration_date"]]
                    products_df.columns = ["ID", "Name", "Purchase Price", "Selling Price", "Quantity", "Expiration Date"]
                    products_df.to_excel(writer, sheet_name="Inventory", index=False)
                
                # Dashboard summary sheet
                metrics = get_dashboard_metrics()
                metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
                metrics_df.to_excel(writer, sheet_name="Dashboard", index=False)
            
            logger.info(f"Combined report exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export combined report: {e}")
            raise
