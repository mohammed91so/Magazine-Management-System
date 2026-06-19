"""
Sales page with production-grade UI.

Features:
- Product dropdown selection
- Profit preview
- Error dialogs
- Sales history table
"""

import customtkinter as ctk
from tkinter import messagebox
from services.sales_service import sell_product, get_sales_history
from services.inventory_service import list_products
from utils.helpers import format_currency


class SalesPage(ctk.CTkFrame):
    """Sales page with product selection and profit preview."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)
        
        self._setup_ui()
        self.refresh_products()
        self.refresh_history()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Sales Management",
            font=("Arial", 24, "bold")
        )
        self.title.pack(pady=15)
        
        # Form frame
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=10)
        
        # Product selection
        ctk.CTkLabel(self.form_frame, text="Select Product:").pack(anchor="w", padx=10, pady=5)
        self.product_dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            values=[],
            command=self.on_product_select
        )
        self.product_dropdown.pack(fill="x", padx=10, pady=5)
        
        # Quantity
        ctk.CTkLabel(self.form_frame, text="Quantity:").pack(anchor="w", padx=10, pady=5)
        self.quantity_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Enter quantity")
        self.quantity_entry.pack(fill="x", padx=10, pady=5)
        self.quantity_entry.bind("<KeyRelease>", self.update_preview)
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.pack(fill="x", padx=20, pady=10)
        
        self.total_price_label = ctk.CTkLabel(
            self.preview_frame,
            text="Total Price: $0.00",
            font=("Arial", 16, "bold")
        )
        self.total_price_label.pack(pady=5)
        
        self.profit_label = ctk.CTkLabel(
            self.preview_frame,
            text="Profit: $0.00",
            font=("Arial", 16, "bold"),
            text_color="#2E8B57"
        )
        self.profit_label.pack(pady=5)
        
        # Sell button
        self.sell_btn = ctk.CTkButton(
            self,
            text="Complete Sale",
            command=self.sell,
            fg_color="#2E8B57",
            height=40
        )
        self.sell_btn.pack(fill="x", padx=20, pady=10)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self,
            text="Refresh",
            command=self.refresh_all
        )
        self.refresh_btn.pack(pady=5)
        
        # Sales history
        self._setup_history_table()
    
    def _setup_history_table(self):
        """Setup sales history table."""
        history_label = ctk.CTkLabel(
            self,
            text="Sales History",
            font=("Arial", 18, "bold")
        )
        history_label.pack(pady=10)
        
        self.history_frame = ctk.CTkScrollableFrame(self, height=200)
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._create_history_header()
    
    def _create_history_header(self):
        """Create history table header."""
        header_frame = ctk.CTkFrame(self.history_frame)
        header_frame.pack(fill="x", pady=5)
        
        headers = ["Product", "Quantity", "Total", "Profit", "Date"]
        for header in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                width=100
            )
            label.pack(side="left", padx=5)
    
    def _create_history_row(self, sale):
        """Create a row for a sale."""
        row_frame = ctk.CTkFrame(self.history_frame)
        row_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            row_frame,
            text=sale.get("product_name", "N/A")[:20],
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row_frame,
            text=str(sale["quantity"]),
            width=60
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row_frame,
            text=format_currency(sale["total_price"]),
            width=80
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row_frame,
            text=format_currency(sale["profit"]),
            width=80,
            text_color="#2E8B57"
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row_frame,
            text=sale["date"][:10] if sale["date"] else "N/A",
            width=100
        ).pack(side="left", padx=5)
    
    def refresh_products(self):
        """Refresh product dropdown."""
        products = list_products()
        product_names = [f"{p['id']} - {p['name']}" for p in products]
        self.product_dropdown.configure(values=product_names)
        
        if product_names:
            self.product_dropdown.set(product_names[0])
            self.on_product_select(product_names[0])
    
    def refresh_history(self):
        """Refresh sales history table."""
        # Clear existing rows
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        # Recreate header
        self._create_history_header()
        
        # Add sale rows
        sales = get_sales_history()
        for sale in sales:
            self._create_history_row(sale)
    
    def refresh_all(self):
        """Refresh all data."""
        self.refresh_products()
        self.refresh_history()

    def on_show(self):
        """Refresh product and sales data when the page becomes visible."""
        self.refresh_products()
        self.refresh_history()
    
    def on_product_select(self, selection):
        """Handle product selection."""
        if selection:
            product_id = int(selection.split(" - ")[0])
            self.selected_product_id = product_id
            self.update_preview()
    
    def update_preview(self, event=None):
        """Update profit preview."""
        try:
            if hasattr(self, 'selected_product_id'):
                products = list_products()
                product = next((p for p in products if p["id"] == self.selected_product_id), None)
                
                if product:
                    quantity = int(self.quantity_entry.get() or 0)
                    total_price = product["selling_price"] * quantity
                    profit = (product["selling_price"] - product["purchase_price"]) * quantity
                    
                    self.total_price_label.configure(text=f"Total Price: {format_currency(total_price)}")
                    self.profit_label.configure(text=f"Profit: {format_currency(profit)}")
        except (ValueError, AttributeError):
            self.total_price_label.configure(text="Total Price: $0.00")
            self.profit_label.configure(text="Profit: $0.00")
    
    def sell(self):
        """Process sale."""
        try:
            if not hasattr(self, 'selected_product_id'):
                messagebox.showwarning("Warning", "Please select a product")
                return
            
            quantity = self.quantity_entry.get()
            
            result = sell_product(self.selected_product_id, quantity)
            
            messagebox.showinfo(
                "Sale Completed",
                f"Sold {result['quantity']} x {result['product_name']}\n"
                f"Total: {format_currency(result['total_price'])}\n"
                f"Profit: {format_currency(result['profit'])}"
            )
            
            self.quantity_entry.delete(0, "end")
            self.update_preview()
            self.refresh_history()
            self.refresh_products()
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete sale: {e}")

