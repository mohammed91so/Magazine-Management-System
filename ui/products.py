"""
Products page with production-grade UI.

Features:
- Error dialogs for validation failures
- Confirmation modals for destructive actions
- Responsive table layout
- Form validation
"""

import customtkinter as ctk
from tkinter import messagebox, StringVar
from services.inventory_service import (
    create_product,
    list_products,
    update_product,
    delete_product,
    get_product,
    get_low_stock_products,
    get_out_of_stock_products,
    get_expired_products,
    get_expiring_soon_products,
)
from utils.helpers import format_currency


class ProductsPage(ctk.CTkFrame):
    """Products management page with table view and CRUD operations."""

    FILTER_OPTIONS = ["All", "Low stock", "Out of stock", "Expired", "Expiring soon"]
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)
        
        self.selected_product_id = None
        self.selected_filter = "All"
        self.search_var = StringVar(value="")
        
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Products Management",
            font=("Arial", 24, "bold")
        )
        self.title.pack(pady=15)
        
        # Form frame
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=10)
        
        # Form inputs
        self._setup_form()
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack(fill="x", padx=20, pady=5)
        
        self._setup_buttons()

        # Filter controls
        self._setup_filter_controls()
        
        # Products table
        self._setup_table()
    
    def _setup_form(self):
        """Setup form input fields."""
        # Grid layout for form
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Name
        ctk.CTkLabel(self.form_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Product name")
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Purchase Price
        ctk.CTkLabel(self.form_frame, text="Purchase Price:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.purchase_entry = ctk.CTkEntry(self.form_frame, placeholder_text="0.00")
        self.purchase_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Selling Price
        ctk.CTkLabel(self.form_frame, text="Selling Price:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.selling_entry = ctk.CTkEntry(self.form_frame, placeholder_text="0.00")
        self.selling_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Quantity
        ctk.CTkLabel(self.form_frame, text="Quantity:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.quantity_entry = ctk.CTkEntry(self.form_frame, placeholder_text="0")
        self.quantity_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Expiration Date
        ctk.CTkLabel(self.form_frame, text="Expiration Date:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.expiration_entry = ctk.CTkEntry(self.form_frame, placeholder_text="YYYY-MM-DD")
        self.expiration_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
    
    def _setup_buttons(self):
        """Setup action buttons."""
        self.add_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Add Product",
            command=self.add_product,
            fg_color="#2E8B57"
        )
        self.add_btn.pack(side="left", padx=5, pady=10)
        
        self.update_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Update Product",
            command=self.update_product,
            fg_color="#FF8C00"
        )
        self.update_btn.pack(side="left", padx=5, pady=10)
        
        self.delete_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Delete Product",
            command=self.delete_product,
            fg_color="#DC143C"
        )
        self.delete_btn.pack(side="left", padx=5, pady=10)
        
        self.clear_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Clear Form",
            command=self.clear_form
        )
        self.clear_btn.pack(side="left", padx=5, pady=10)
        
        self.refresh_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Refresh",
            command=self.refresh
        )
        self.refresh_btn.pack(side="right", padx=5, pady=10)

    def _setup_filter_controls(self):
        """Setup search and filter controls above the table."""
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.filter_frame, text="Search:").pack(side="left", padx=(10, 5), pady=10)
        self.search_entry = ctk.CTkEntry(
            self.filter_frame,
            textvariable=self.search_var,
            placeholder_text="Search by product name"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh())

        ctk.CTkLabel(self.filter_frame, text="Filter:").pack(side="left", padx=(10, 5), pady=10)
        self.filter_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=self.FILTER_OPTIONS,
            command=self.on_filter_change
        )
        self.filter_menu.pack(side="left", padx=(5, 10), pady=10)
        self.filter_menu.set(self.selected_filter)
    
    def _setup_table(self):
        """Setup products table."""
        # Scrollable frame for table
        self.table_frame = ctk.CTkScrollableFrame(self, height=300)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Table header
        self._create_table_header()
    
    def _create_table_header(self):
        """Create table header row."""
        header_frame = ctk.CTkFrame(self.table_frame)
        header_frame.pack(fill="x", pady=5)
        
        headers = ["ID", "Name", "Purchase", "Selling", "Qty", "Expiration", "Action"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=("Arial", 12, "bold"),
                width=100
            )
            label.pack(side="left", padx=5)
    
    def _create_product_row(self, product):
        """Create a row for a product."""
        row_frame = ctk.CTkFrame(self.table_frame)
        row_frame.pack(fill="x", pady=2)
        
        # Product data
        ctk.CTkLabel(row_frame, text=str(product["id"]), width=50).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=product["name"][:20], width=120).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=format_currency(product["purchase_price"]), width=80).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=format_currency(product["selling_price"]), width=80).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=str(product["quantity"]), width=50).pack(side="left", padx=5)
        ctk.CTkLabel(row_frame, text=product["expiration_date"], width=100).pack(side="left", padx=5)
        
        # Select button
        select_btn = ctk.CTkButton(
            row_frame,
            text="Select",
            width=60,
            command=lambda pid=product["id"]: self.select_product(pid)
        )
        select_btn.pack(side="left", padx=5)

    def on_filter_change(self, selected_filter):
        """Update the current filter and refresh the visible product rows."""
        self.selected_filter = selected_filter
        self.refresh()

    def _get_products_for_filter(self, filter_name):
        """Get the product list for the selected filter option."""
        if filter_name == "Low stock":
            return get_low_stock_products(threshold=10)
        if filter_name == "Out of stock":
            return get_out_of_stock_products()
        if filter_name == "Expired":
            return get_expired_products()
        if filter_name == "Expiring soon":
            return get_expiring_soon_products()
        return list_products()

    def _apply_search(self, products, search_text):
        """Apply a case-insensitive name search to a product list."""
        normalized_search = search_text.strip().lower()
        if not normalized_search:
            return products

        return [
            product for product in products
            if normalized_search in product["name"].lower()
        ]

    def _get_filtered_products(self):
        """Get products for the current filter and search state."""
        products = self._get_products_for_filter(self.selected_filter)
        return self._apply_search(products, self.search_var.get())

    def _render_products(self, products):
        """Render the provided product list in the table."""
        # Clear existing rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Recreate header
        self._create_table_header()

        # Add product rows
        for product in products:
            self._create_product_row(product)
    
    def add_product(self):
        """Add a new product."""
        try:
            name = self.name_entry.get()
            purchase_price = self.purchase_entry.get()
            selling_price = self.selling_entry.get()
            quantity = self.quantity_entry.get()
            expiration_date = self.expiration_entry.get()
            
            create_product(name, purchase_price, selling_price, quantity, expiration_date)
            
            messagebox.showinfo("Success", "Product added successfully!")
            self.clear_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {e}")
    
    def update_product(self):
        """Update selected product."""
        if self.selected_product_id is None:
            messagebox.showwarning("Warning", "Please select a product to update")
            return
        
        try:
            name = self.name_entry.get()
            purchase_price = self.purchase_entry.get()
            selling_price = self.selling_entry.get()
            quantity = self.quantity_entry.get()
            expiration_date = self.expiration_entry.get()
            
            update_product(
                self.selected_product_id,
                name, purchase_price, selling_price, quantity, expiration_date
            )
            
            messagebox.showinfo("Success", "Product updated successfully!")
            self.clear_form()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {e}")
    
    def delete_product(self):
        """Delete selected product with confirmation."""
        if self.selected_product_id is None:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
        
        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this product? This action cannot be undone."
        )
        
        if confirm:
            try:
                delete_product(self.selected_product_id)
                messagebox.showinfo("Success", "Product deleted successfully!")
                self.clear_form()
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")
    
    def select_product(self, product_id):
        """Select a product and populate form."""
        try:
            product = get_product(product_id)
            self.selected_product_id = product_id
            
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, product["name"])
            
            self.purchase_entry.delete(0, "end")
            self.purchase_entry.insert(0, str(product["purchase_price"]))
            
            self.selling_entry.delete(0, "end")
            self.selling_entry.insert(0, str(product["selling_price"]))
            
            self.quantity_entry.delete(0, "end")
            self.quantity_entry.insert(0, str(product["quantity"]))
            
            self.expiration_entry.delete(0, "end")
            self.expiration_entry.insert(0, product["expiration_date"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product: {e}")
    
    def clear_form(self):
        """Clear form fields."""
        self.name_entry.delete(0, "end")
        self.purchase_entry.delete(0, "end")
        self.selling_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")
        self.expiration_entry.delete(0, "end")
        self.selected_product_id = None

    def on_show(self):
        """Refresh product data when the page becomes visible."""
        self.refresh()
    
    def refresh(self):
        """Refresh products table."""
        products = self._get_filtered_products()
        self._render_products(products)


