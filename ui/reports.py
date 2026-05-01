"""
Reports page with Excel export functionality.

Features:
- Export sales reports
- Export inventory reports
- Export combined reports
- Error handling for export failures
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from services.reporting_service import ReportingService


class ReportsPage(ctk.CTkFrame):
    """Reports page with Excel export functionality."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)
        
        self.reporting_service = ReportingService()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Reports & Exports",
            font=("Arial", 24, "bold")
        )
        self.title.pack(pady=15)
        
        # Description
        self.description = ctk.CTkLabel(
            self,
            text="Export data to Excel for analysis and record-keeping",
            font=("Arial", 12)
        )
        self.description.pack(pady=5)
        
        # Reports frame
        self.reports_frame = ctk.CTkFrame(self)
        self.reports_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sales report button
        self.sales_report_btn = ctk.CTkButton(
            self.reports_frame,
            text="Export Sales Report",
            command=self.export_sales_report,
            fg_color="#4682B4",
            height=50
        )
        self.sales_report_btn.pack(fill="x", padx=20, pady=10)
        
        # Inventory report button
        self.inventory_report_btn = ctk.CTkButton(
            self.reports_frame,
            text="Export Inventory Report",
            command=self.export_inventory_report,
            fg_color="#4682B4",
            height=50
        )
        self.inventory_report_btn.pack(fill="x", padx=20, pady=10)
        
        # Combined report button
        self.combined_report_btn = ctk.CTkButton(
            self.reports_frame,
            text="Export Combined Report",
            command=self.export_combined_report,
            fg_color="#2E8B57",
            height=50
        )
        self.combined_report_btn.pack(fill="x", padx=20, pady=10)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            self.reports_frame,
            text="Reports will be saved to the application directory",
            font=("Arial", 10),
            text_color="gray"
        )
        self.info_label.pack(pady=20)
    
    def export_sales_report(self):
        """Export sales report to Excel."""
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                title="Save Sales Report",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                output_path = self.reporting_service.export_sales_report(filename)
                messagebox.showinfo(
                    "Success",
                    f"Sales report exported successfully!\n\nLocation: {output_path}"
                )
        except ValueError as e:
            messagebox.showwarning("No Data", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export sales report: {e}")
    
    def export_inventory_report(self):
        """Export inventory report to Excel."""
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                title="Save Inventory Report",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                output_path = self.reporting_service.export_inventory_report(filename)
                messagebox.showinfo(
                    "Success",
                    f"Inventory report exported successfully!\n\nLocation: {output_path}"
                )
        except ValueError as e:
            messagebox.showwarning("No Data", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export inventory report: {e}")
    
    def export_combined_report(self):
        """Export combined report to Excel."""
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                title="Save Combined Report",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if filename:
                output_path = self.reporting_service.export_combined_report(filename)
                messagebox.showinfo(
                    "Success",
                    f"Combined report exported successfully!\n\nLocation: {output_path}"
                )
        except ValueError as e:
            messagebox.showwarning("No Data", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export combined report: {e}")