# Inventory System - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Dashboard](#dashboard)
5. [Product Management](#product-management)
6. [Sales Management](#sales-management)
7. [Reports](#reports)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

The Inventory System is a desktop application designed to help store owners manage their inventory, track sales, and monitor business performance. This manual will guide you through all features and functionality.

## Installation

### Windows Installer

1. Download `InventorySystem-Setup.exe` from the release page
2. Double-click the installer
3. Follow the installation wizard
4. Launch the application from the Start menu or desktop shortcut

### Manual Installation

1. Ensure Python 3.9+ is installed
2. Download the source code
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Getting Started

When you first launch the application, you will see:

- **Sidebar Navigation**: Access all main features
- **Active Page Highlight**: The current page stays highlighted in the sidebar
- **Dashboard**: Overview of your business metrics
- **Configuration**: Settings are loaded from `.env` file

When you move between pages, the app refreshes the page you open so you see current information.

## Dashboard

The Dashboard provides a real-time overview of your business:

### Metric Cards

- **Total Earnings**: Sum of all sales revenue
- **Total Profit**: Sum of all profit from sales
- **Total Investment**: Current value of inventory
- **Total Products**: Number of unique products
- **Low Stock**: Products below threshold (default: 10)
- **Out of Stock**: Products with zero quantity
- **Expired**: Products past expiration date
- **Expiring Soon**: Products expiring within 7 days

### Alerts Section

Color-coded alerts inform you of critical issues:
- **Red**: Critical (out of stock, expired)
- **Orange**: Warning (low stock, expiring soon)
- **Green**: All clear

### Refresh Button

Click "Refresh Dashboard" to update all metrics and alerts.

## Product Management

### Adding a Product

1. Navigate to the Products page
2. Fill in the form:
   - **Name**: Product name (2-100 characters)
   - **Purchase Price**: Cost per unit (must be non-negative)
   - **Selling Price**: Sale price per unit (must be non-negative)
   - **Quantity**: Initial stock quantity (must be non-negative)
   - **Expiration Date**: Format: YYYY-MM-DD
3. Click "Add Product"
4. Success message confirms addition

### Updating a Product

1. Click "Select" on the product row in the table
2. Form populates with current data
3. Modify desired fields
4. Click "Update Product"
5. Success message confirms update

### Deleting a Product

1. Click "Select" on the product row
2. Click "Delete Product"
3. Confirm deletion in the dialog
4. Product is removed from inventory

### Viewing Products

The table displays:
- ID
- Name
- Purchase Price
- Selling Price
- Quantity
- Expiration Date
- Action button

### Searching Products

Use the search box above the product table to find products by name.

- Search updates as you type
- Search is not case-sensitive
- Search works together with the status filter

### Filtering Products

Use the filter menu above the product table to quickly narrow the list.

Available filters:

- **All**
- **Low stock**
- **Out of stock**
- **Expired**
- **Expiring soon**

You can combine the filter and the search box to find products faster.

### Refreshing the Product List

Click **Refresh** to reload the product table.

Your current search text and selected filter stay active after refresh and when you return to the Products page.

## Sales Management

### Recording a Sale

1. Navigate to the Sales page
2. Select a product from the dropdown
3. Enter quantity to sell
4. Review profit preview:
   - **Total Price**: Selling price × quantity
   - **Profit**: (Selling price - Purchase price) × quantity
5. Click "Complete Sale"
6. Success message shows sale details

### Sales History

The Sales History table shows:
- Product name
- Quantity sold
- Total price
- Profit
- Date of sale

### Sale Restrictions

- Cannot sell expired products
- Cannot sell more than available stock
- Quantity must be greater than zero

## Reports

### Exporting Reports

1. Navigate to the Reports page
2. Choose report type:
   - **Sales Report**: Sales summary with statistics
   - **Inventory Report**: Current inventory snapshot
   - **Combined Report**: Both sales and inventory data
3. Click the export button
4. Choose save location
5. Report is saved as Excel file

### Report Contents

**Sales Report**:
- Sales data sheet: All transactions
- Summary sheet: Total sales, profit, quantity

**Inventory Report**:
- Inventory sheet: All products with calculations
- Summary sheet: Total products, investment, alerts

**Combined Report**:
- Sales sheet
- Inventory sheet
- Dashboard metrics sheet

### Backup Restore Management

The Reports page also includes backup restore tools.

You can:

- view available backups
- refresh the backup list
- select one backup
- restore that backup after confirmation

### Refreshing the Backup List

1. Open the **Reports** page
2. Find the **Backup Restore** section
3. Click **Refresh Backups**

The list will reload and show the available backup files.

### Selecting a Backup

1. In the **Backup Restore** section, review the available backups
2. Each backup shows its date/time and file size when available
3. Click **Select** on the backup you want to use

Only one backup can be selected at a time.

### Restoring a Backup

1. Open the **Reports** page
2. Refresh the backup list if needed
3. Select the backup you want to restore
4. Click **Restore Selected Backup**
5. Read the warning carefully
6. Confirm the restore when asked
7. Confirm again in the final confirmation dialog

### Important Restore Warning

Restoring a backup replaces the current database data.

This means:

- current product, sales, and report data can be replaced by older data
- you should only restore a backup when you are sure it is the correct one

Before the restore happens, the app creates a fresh safety backup of the current database automatically.

### After a Restore

After a successful restore:

- the app refreshes its pages automatically
- the backup list is reloaded

If anything still looks out of date, restart the application to make sure every page shows the restored data correctly.

## Troubleshooting

### Application Won't Start

**Problem**: Application fails to launch

**Solutions**:
1. Check if Python 3.9+ is installed
2. Verify all dependencies are installed
3. Check logs in `logs/` directory
4. Ensure `.env` file exists and is configured

### Database Errors

**Problem**: Database connection or operation errors

**Solutions**:
1. Check if `inventory.db` file exists
2. Verify file permissions
3. Check available disk space
4. Restore from backup if needed

### Backup Issues

**Problem**: Backups not being created

**Solutions**:
1. Verify `backups/` directory exists
2. Check disk space
3. Check log files for errors

### Export Errors

**Problem**: Excel export fails

**Solutions**:
1. Ensure pandas and openpyxl are installed
2. Check if there is data to export
3. Verify write permissions for save location
4. Check available disk space

**Problem**: A restore does not appear to update every page

**Solutions**:
1. Go to another page and return
2. Use page refresh buttons where available
3. Restart the application if anything still looks stale

## FAQ

**Q: Can I change the low stock threshold?**
A: Currently set to 10. This can be modified in the code or future versions.

**Q: What happens if I sell more than available stock?**
A: The system prevents this with an error message.

**Q: Can I sell expired products?**
A: No, the system blocks sales of expired products.

**Q: How often are backups created?**
A: Backups are created automatically on application startup.

**Q: How many backups are retained?**
A: The system keeps the last 30 backups.

**Q: Can I restore from a backup?**
A: Yes. Open the **Reports** page, go to the **Backup Restore** section, refresh the list if needed, select a backup, and confirm the restore. The app creates a safety backup before restoring.

**Q: What should I know before restoring a backup?**
A: Restoring replaces the current database data with the selected backup. Always confirm that you selected the correct backup before continuing.

**Q: What happens after a restore?**
A: The app refreshes its pages automatically. If anything still looks stale, restart the application.

**Q: Is my data secure?**
A: The application uses SQLite with parameterized queries to prevent SQL injection. All inputs are validated.

**Q: Can I use this on multiple computers?**
A: Yes, but each installation has its own database. For multi-user access, a server-based solution would be needed.

**Q: How do I update the application?**
A: Download the new version and install over the existing installation. Your data will be preserved.

## Support

For additional support:
- Check the logs in `logs/` directory
- Review the GitHub issues page
- Contact the development team
