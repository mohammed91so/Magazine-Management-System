"""
Reports page with Excel export functionality.

Features:
- Export sales reports
- Export inventory reports
- Export combined reports
- Backup restore management
- Error handling for export failures
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from datetime import datetime

from config.settings import settings
from database.backup import get_backup_list, restore_backup
from services.reporting_service import ReportingService


class ReportsPage(ctk.CTkFrame):
    """Reports page with Excel export functionality."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)
        
        self.reporting_service = ReportingService()
        self.available_backups = []
        self.selected_backup_path = None
        self.backup_row_frames = {}
        
        self._setup_ui()
        self._load_backups()
    
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

        # Backup management
        self.backup_frame = ctk.CTkFrame(self)
        self.backup_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.backup_title = ctk.CTkLabel(
            self.backup_frame,
            text="Backup Restore",
            font=("Arial", 20, "bold")
        )
        self.backup_title.pack(anchor="w", padx=20, pady=(20, 5))

        self.backup_warning = ctk.CTkLabel(
            self.backup_frame,
            text="Warning: Restoring a backup replaces the current database data.",
            font=("Arial", 11),
            text_color="#DC143C"
        )
        self.backup_warning.pack(anchor="w", padx=20, pady=(0, 10))

        self.backup_actions_frame = ctk.CTkFrame(self.backup_frame)
        self.backup_actions_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.refresh_backups_btn = ctk.CTkButton(
            self.backup_actions_frame,
            text="Refresh Backups",
            command=self.refresh_backups
        )
        self.refresh_backups_btn.pack(side="left", padx=5, pady=10)

        self.restore_backup_btn = ctk.CTkButton(
            self.backup_actions_frame,
            text="Restore Selected Backup",
            command=self.restore_selected_backup,
            fg_color="#DC143C"
        )
        self.restore_backup_btn.pack(side="right", padx=5, pady=10)

        self.backup_list_frame = ctk.CTkScrollableFrame(self.backup_frame, height=220)
        self.backup_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def on_show(self):
        """Refresh backup list when the page becomes visible."""
        self.refresh_backups()

    def _load_backups(self):
        """Load available backup files and render the list."""
        self.available_backups = get_backup_list()
        if self.selected_backup_path not in self.available_backups:
            self.selected_backup_path = None
        self._render_backups()

    def _format_size(self, size_bytes):
        """Format a file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _build_backup_display_item(self, backup_path: Path):
        """Build display metadata for a backup path."""
        try:
            stat_result = backup_path.stat()
            timestamp = datetime.fromtimestamp(stat_result.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size_text = self._format_size(stat_result.st_size)
        except OSError:
            timestamp = backup_path.name
            size_text = "Size unavailable"

        return {
            "path": backup_path,
            "timestamp": timestamp,
            "size": size_text,
            "label": f"{timestamp}  |  {size_text}"
        }

    def _render_backups(self):
        """Render the available backups list."""
        self.backup_row_frames = {}
        for widget in self.backup_list_frame.winfo_children():
            widget.destroy()

        if not self.available_backups:
            empty_label = ctk.CTkLabel(
                self.backup_list_frame,
                text="No backups available.",
                font=("Arial", 12),
                text_color="gray"
            )
            empty_label.pack(anchor="w", padx=10, pady=10)
            return

        for backup_path in self.available_backups:
            display_item = self._build_backup_display_item(backup_path)
            row = ctk.CTkFrame(self.backup_list_frame)
            row.pack(fill="x", pady=4)

            row_label = ctk.CTkLabel(
                row,
                text=display_item["label"],
                font=("Arial", 12)
            )
            row_label.pack(side="left", padx=10, pady=10)

            select_button = ctk.CTkButton(
                row,
                text="Selected" if backup_path == self.selected_backup_path else "Select",
                width=90,
                command=lambda path=backup_path: self._select_backup(path),
                fg_color="#2E8B57" if backup_path == self.selected_backup_path else None
            )
            select_button.pack(side="right", padx=10, pady=10)
            self.backup_row_frames[backup_path] = {
                "frame": row,
                "button": select_button,
                "label": row_label,
            }

    def _select_backup(self, backup_path: Path):
        """Select a backup and rerender selection state."""
        self.selected_backup_path = backup_path
        self._render_backups()

    def _is_within_backup_dir(self, selected_path: Path, backup_dir: Path):
        """Check whether a path resolves inside the configured backup directory."""
        try:
            return selected_path.is_relative_to(backup_dir)
        except AttributeError:
            return backup_dir == selected_path or backup_dir in selected_path.parents

    def _validate_selected_backup(self, backup_path: Path) -> Path:
        """Validate the selected backup exists and is inside the backup directory."""
        if backup_path is None:
            raise ValueError("Please select a backup to restore")

        resolved_backup_dir = settings.BACKUP_PATH.resolve()
        resolved_selected_path = Path(backup_path).resolve()

        if not resolved_selected_path.exists():
            raise ValueError("Selected backup file does not exist")

        if not resolved_selected_path.is_file():
            raise ValueError("Selected backup path is not a file")

        if not self._is_within_backup_dir(resolved_selected_path, resolved_backup_dir):
            raise ValueError("Selected backup must be inside the configured backup directory")

        return resolved_selected_path

    def refresh_backups(self):
        """Reload available backups from disk."""
        try:
            self._load_backups()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load backups: {e}")

    def restore_selected_backup(self):
        """Restore the selected backup after validation and strong confirmation."""
        try:
            backup_path = self._validate_selected_backup(self.selected_backup_path)
        except ValueError as e:
            messagebox.showwarning("Restore Blocked", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate selected backup: {e}")
            return

        confirm_warning = messagebox.askyesno(
            "Confirm Restore",
            "Restoring a backup will replace the current database data.\n\nDo you want to continue?"
        )
        if not confirm_warning:
            return

        final_confirm = messagebox.askyesno(
            "Final Confirmation",
            f"Restore backup:\n{backup_path.name}\n\n"
            "A fresh safety backup of the current database will be created first.\n\n"
            "Proceed with restore?"
        )
        if not final_confirm:
            return

        try:
            restore_backup(backup_path)

            refresh_warning = None
            app = self.winfo_toplevel()
            refresh_all_pages = getattr(app, "refresh_all_pages", None)
            if callable(refresh_all_pages):
                try:
                    refresh_all_pages()
                except Exception:
                    refresh_warning = (
                        "The backup was restored successfully, but some open views may still be stale. "
                        "Please restart the application."
                    )
            else:
                refresh_warning = (
                    "The backup was restored successfully. Please restart the application "
                    "to ensure all views reflect the restored data."
                )

            self.refresh_backups()

            if refresh_warning:
                messagebox.showwarning(
                    "Restore Completed",
                    f"Backup restored successfully.\n\n{refresh_warning}"
                )
            else:
                messagebox.showinfo(
                    "Restore Completed",
                    "Backup restored successfully.\n\n"
                    "A fresh safety backup was created before restore, and the app views were refreshed."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {e}")
    
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
