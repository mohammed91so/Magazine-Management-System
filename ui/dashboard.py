"""
Dashboard page with production-grade UI.

Features:
- Metric cards with color-coded alerts
- Responsive layout
- Real-time data refresh
- Visual indicators for critical metrics
"""

import customtkinter as ctk
from services.analytics_service import get_dashboard_metrics
from services.inventory_service import (
    get_low_stock_products,
    get_out_of_stock_products,
    get_expired_products,
    get_expiring_soon_products
)
from utils.helpers import format_currency


class DashboardPage(ctk.CTkFrame):
    """Dashboard page with metric cards and alerts."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)
        
        self._setup_ui()
        self.load_metrics()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 24, "bold")
        )
        self.title.pack(pady=15)
        
        # Metrics frame
        self.metrics_frame = ctk.CTkFrame(self)
        self.metrics_frame.pack(fill="x", padx=20, pady=10)
        
        self._setup_metric_cards()
        
        # Alerts frame
        self.alerts_frame = ctk.CTkFrame(self)
        self.alerts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._setup_alerts_section()
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self,
            text="Refresh Dashboard",
            command=self.load_metrics,
            height=40
        )
        self.refresh_btn.pack(fill="x", padx=20, pady=10)
    
    def _setup_metric_cards(self):
        """Setup metric cards."""
        # Financial metrics
        self.earnings_card = self._create_metric_card(
            "Total Earnings",
            "$0.00",
            "#2E8B57"
        )
        self.earnings_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.profit_card = self._create_metric_card(
            "Total Profit",
            "$0.00",
            "#2E8B57"
        )
        self.profit_card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.investment_card = self._create_metric_card(
            "Total Investment",
            "$0.00",
            "#4682B4"
        )
        self.investment_card.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        # Inventory metrics
        self.products_card = self._create_metric_card(
            "Total Products",
            "0",
            "#4682B4"
        )
        self.products_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.low_stock_card = self._create_metric_card(
            "Low Stock",
            "0",
            "#FF8C00"
        )
        self.low_stock_card.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        self.out_of_stock_card = self._create_metric_card(
            "Out of Stock",
            "0",
            "#DC143C"
        )
        self.out_of_stock_card.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        
        # Expiration metrics
        self.expired_card = self._create_metric_card(
            "Expired",
            "0",
            "#DC143C"
        )
        self.expired_card.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        self.expiring_soon_card = self._create_metric_card(
            "Expiring Soon",
            "0",
            "#FF8C00"
        )
        self.expiring_soon_card.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        self.metrics_frame.grid_columnconfigure(0, weight=1)
        self.metrics_frame.grid_columnconfigure(1, weight=1)
        self.metrics_frame.grid_columnconfigure(2, weight=1)
    
    def _create_metric_card(self, title, value, color):
        """Create a metric card."""
        card = ctk.CTkFrame(self.metrics_frame)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12)
        )
        title_label.pack(pady=5)
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 20, "bold"),
            text_color=color
        )
        value_label.pack(pady=5)
        
        # Store reference to value label
        setattr(card, "value_label", value_label)
        
        return card
    
    def _setup_alerts_section(self):
        """Setup alerts section."""
        alerts_title = ctk.CTkLabel(
            self.alerts_frame,
            text="Alerts",
            font=("Arial", 18, "bold")
        )
        alerts_title.pack(pady=10)
        
        self.alerts_scroll = ctk.CTkScrollableFrame(self.alerts_frame, height=200)
        self.alerts_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def on_show(self):
        """Refresh dashboard data when the page becomes visible."""
        self.load_metrics()
    
    def load_metrics(self):
        """Load and display dashboard metrics."""
        try:
            metrics = get_dashboard_metrics()
            
            # Update metric cards
            self.earnings_card.value_label.configure(text=format_currency(metrics["total_earnings"]))
            self.profit_card.value_label.configure(text=format_currency(metrics["total_profit"]))
            self.investment_card.value_label.configure(text=format_currency(metrics["total_investment"]))
            self.products_card.value_label.configure(text=str(metrics["total_products"]))
            self.low_stock_card.value_label.configure(text=str(metrics["low_stock_count"]))
            self.out_of_stock_card.value_label.configure(text=str(metrics["out_of_stock_count"]))
            self.expired_card.value_label.configure(text=str(metrics["expired_count"]))
            self.expiring_soon_card.value_label.configure(text=str(metrics["expiring_soon_count"]))
            
            # Update alerts
            self._update_alerts()
            
        except Exception as e:
            self._show_alert("Error", f"Failed to load metrics: {e}", "#DC143C")
    
    def _update_alerts(self):
        """Update alerts section."""
        # Clear existing alerts
        for widget in self.alerts_scroll.winfo_children():
            widget.destroy()
        
        # Get alert data
        low_stock = get_low_stock_products(threshold=10)
        out_of_stock = get_out_of_stock_products()
        expired = get_expired_products()
        expiring_soon = get_expiring_soon_products()
        
        # Display alerts
        if out_of_stock:
            self._show_alert(
                "Out of Stock",
                f"{len(out_of_stock)} products are out of stock",
                "#DC143C"
            )
        
        if expired:
            self._show_alert(
                "Expired Products",
                f"{len(expired)} products have expired",
                "#DC143C"
            )
        
        if low_stock:
            self._show_alert(
                "Low Stock",
                f"{len(low_stock)} products are running low",
                "#FF8C00"
            )
        
        if expiring_soon:
            self._show_alert(
                "Expiring Soon",
                f"{len(expiring_soon)} products expire within 7 days",
                "#FF8C00"
            )
        
        if not (low_stock or out_of_stock or expired or expiring_soon):
            self._show_alert(
                "All Clear",
                "No alerts at this time",
                "#2E8B57"
            )
    
    def _show_alert(self, title, message, color):
        """Show an alert in the alerts section."""
        alert_frame = ctk.CTkFrame(self.alerts_scroll)
        alert_frame.pack(fill="x", pady=5)
        
        title_label = ctk.CTkLabel(
            alert_frame,
            text=title,
            font=("Arial", 12, "bold"),
            text_color=color
        )
        title_label.pack(anchor="w", padx=10, pady=2)
        
        message_label = ctk.CTkLabel(
            alert_frame,
            text=message,
            font=("Arial", 10)
        )
        message_label.pack(anchor="w", padx=10, pady=2)
