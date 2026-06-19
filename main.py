"""
Main entry point for the Inventory System.

Enterprise-grade desktop application for inventory and sales management.
"""

import sys
import customtkinter as ctk  
from tkinter import messagebox
from ui.products import ProductsPage
from ui.sales import SalesPage
from ui.dashboard import DashboardPage
from ui.reports import ReportsPage
from database.db import initialize_db
from config.settings import settings
from utils.logging_config import logger
from utils.monitoring import monitoring


class App(ctk.CTk):
    """Main application class with graceful error handling."""
    
    def __init__(self):
        super().__init__()
        
        # Configure app
        self.title(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        self.geometry("1200x700")
        
        # Initialize database with error handling
        try:
            initialize_db()
            logger.info("Application started successfully")
            monitoring.log_operation("application_start")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            monitoring.log_error(e, "database_initialization")
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize the application database.\n\nError: {e}\n\n"
                "Please check the logs for more details."
            )
            sys.exit(1)
        
        # Setup layout with error handling
        try:
            self._setup_layout()
            self._setup_pages()
            self._setup_navigation()
        except Exception as e:
            logger.error(f"Failed to setup UI: {e}")
            monitoring.log_error(e, "ui_setup")
            messagebox.showerror(
                "UI Error",
                f"Failed to initialize the user interface.\n\nError: {e}"
            )
            sys.exit(1)
        
        # Show default page
        self.show_page("dashboard")
    
    def _setup_layout(self):
        """Setup application layout."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
    
    def _setup_pages(self):
        """Setup application pages."""
        self.pages = {
            "dashboard": DashboardPage(self.content),
            "products": ProductsPage(self.content),
            "sales": SalesPage(self.content),
            "reports": ReportsPage(self.content)
        }
        
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
    
    def _setup_navigation(self):
        """Setup sidebar navigation."""
        # App title in sidebar
        title_label = ctk.CTkLabel(
            self.sidebar,
            text=settings.APP_NAME,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Navigation buttons
        ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=lambda: self.show_page("dashboard"),
            height=40
        ).pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(
            self.sidebar,
            text="Products",
            command=lambda: self.show_page("products"),
            height=40
        ).pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(
            self.sidebar,
            text="Sales",
            command=lambda: self.show_page("sales"),
            height=40
        ).pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(
            self.sidebar,
            text="Reports",
            command=lambda: self.show_page("reports"),
            height=40
        ).pack(pady=5, padx=10, fill="x")
        
        # Version label
        version_label = ctk.CTkLabel(
            self.sidebar,
            text=f"v{settings.APP_VERSION}",
            font=("Arial", 10),
            text_color="gray"
        )
        version_label.pack(side="bottom", pady=10)
    
    def show_page(self, name: str):
        """
        Show a specific page with error handling.
        
        Args:
            name: Page name to show.
        """
        try:
            if name in self.pages:
                page = self.pages[name]
                on_show = getattr(page, "on_show", None)
                if callable(on_show):
                    on_show()
                page.tkraise()
                logger.debug(f"Switched to page: {name}")
                monitoring.log_operation(f"page_switch_{name}")
        except Exception as e:
            logger.error(f"Failed to switch to page {name}: {e}")
            monitoring.log_error(e, f"page_switch_{name}")
            messagebox.showerror(
                "Navigation Error",
                f"Failed to load page: {name}\n\nError: {e}"
            )

    def refresh_all_pages(self):
        """Refresh all pages that expose an on_show lifecycle hook."""
        for page in self.pages.values():
            on_show = getattr(page, "on_show", None)
            if callable(on_show):
                on_show()


def handle_global_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for uncaught exceptions."""
    logger.critical(
        f"Uncaught exception: {exc_type.__name__}: {exc_value}",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    monitoring.log_error(exc_value, "global_exception")


if __name__ == "__main__":
    # Set global exception handler
    sys.excepthook = handle_global_exception
    
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Fatal application error: {e}")
        monitoring.log_error(e, "fatal_error")
        messagebox.showerror(
            "Fatal Error",
            f"The application encountered a fatal error and must close.\n\nError: {e}"
        )
        sys.exit(1)



