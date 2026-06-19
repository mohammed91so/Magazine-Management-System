# Inventory System Architecture

## Overview

The application is a desktop inventory and sales management system built with Python, CustomTkinter, and SQLite. It runs as a single local process, stores state primarily in SQLite, and separates responsibilities across four layers:

1. UI layer in `ui/`
2. Service layer in `services/`
3. Data access layer in `database/`
4. Shared infrastructure in `config/` and `utils/`

There are no external APIs in the current implementation. Runtime integrations are:

- SQLite for persistence
- local filesystem access for configuration, logs, backups, and report exports
- Tkinter dialogs for user feedback, confirmation, and file selection
- pandas and openpyxl for Excel generation

## Recent Improvements

- Sales writes are now atomic through a single database transaction.
- SQLite foreign keys are enabled on normal runtime connections.
- Validation and parsing for submission paths now live in services rather than the UI.
- Page lifecycle hooks (`on_show`) and app-level refresh behavior keep views fresher on navigation and restore flows.
- Products page now supports client-side search and status filtering.
- Reports page now includes backup restore management with strict path validation and strong confirmation.
- Sidebar navigation now keeps the active page highlighted persistently.

## Entry Point

The application starts in `main.py`.

Startup sequence:

1. `main.py` installs `handle_global_exception` as `sys.excepthook`.
2. `App`, a `customtkinter.CTk` subclass, is instantiated.
3. `App.__init__()` reads settings and configures the main window title and size.
4. `initialize_db()` runs migrations, creates a startup backup, and prunes old backups.
5. The root layout is created with a sidebar and content area.
6. Four page frames are instantiated once and stored in `self.pages`.
7. Sidebar navigation buttons are created, stored in `self.nav_buttons`, and styled through `update_navigation_state()`.
8. `show_page("dashboard")` triggers the dashboard lifecycle hook, raises the page, and marks its button active.
9. `app.mainloop()` starts the Tk event loop.

## Runtime Architecture

### UI Layer

The UI consists of one root window and four long-lived page frames:

- `App` in `main.py`
- `DashboardPage` in `ui/dashboard.py`
- `ProductsPage` in `ui/products.py`
- `SalesPage` in `ui/sales.py`
- `ReportsPage` in `ui/reports.py`

Navigation is implemented by preloading all pages into the same grid cell and calling `tkraise()` on the selected page. Before a page is raised, `App.show_page()` calls the page’s `on_show()` lifecycle hook when present. After a successful switch it updates the persistent active-state styling for the sidebar buttons.

### Service Layer

The service layer owns business rules, validation orchestration, and submission-path parsing:

- `inventory_service.py` handles product CRUD, stock updates, expiration logic, alerts, and accepts raw UI values for submission fields
- `sales_service.py` handles sales transactions and sales history, including parsing/validating raw quantity input
- `analytics_service.py` aggregates dashboard metrics and best-seller analytics
- `reporting_service.py` exports Excel reports

This layer is the boundary between UI behavior and SQL access.

### Data Access Layer

The database layer is built around SQLite:

- `db.py` provides runtime connections and startup initialization
- `migrations.py` defines and applies schema migrations
- `queries.py` contains SQL for products, sales, dashboard metrics, and transactional sale recording
- `backup.py` manages backup creation, listing, and restoration

Runtime connections now enable SQLite foreign keys consistently.

### Shared Infrastructure

- `config/settings.py` loads environment-backed settings and defines resolved paths
- `utils/logging_config.py` configures application logging
- `utils/monitoring.py` tracks operation/error counters and provides health helpers
- `utils/validators.py` centralizes validation and parsing rules
- `utils/helpers.py` provides formatting helpers used by the UI

## Main Data Flow

### Product Flow

1. The user enters product data in `ProductsPage`.
2. The page passes raw widget values directly to `services.inventory_service.create_product()` or `update_product()`.
3. The service parses and validates name, prices, quantity, and expiration date.
4. The service delegates persistence to `database.queries`.
5. SQLite commits the change.
6. `ProductsPage.refresh()` re-renders the table using the current search/filter state.

### Sales Flow

1. `SalesPage` loads products into a dropdown from `list_products()`.
2. The user selects a product and enters a quantity.
3. The page computes a lightweight client-side preview for total/profit display only.
4. On confirmation, the page calls `services.sales_service.sell_product()` with the raw quantity string.
5. The service parses and validates the quantity, blocks expired products, checks stock, and delegates the atomic write to `queries.record_sale_transaction()`.
6. The page refreshes sales history and the product dropdown.

### Dashboard Flow

1. `DashboardPage.load_metrics()` requests aggregates from `services.analytics_service`.
2. It separately loads alert lists from `services.inventory_service`.
3. Metric cards and alert rows are rebuilt from current database-backed values.
4. `DashboardPage.on_show()` refreshes the dashboard whenever the page becomes active.

### Reporting Flow

1. `ReportsPage` presents export actions and backup management in a single page.
2. Export actions call `ReportingService`, which loads data from queries and analytics services and writes `.xlsx` files.
3. Backup management loads backup files from `database.backup.get_backup_list()`.
4. Before restore, the page validates that the selected path exists, is a file, and resolves inside `settings.BACKUP_PATH`.
5. After two confirmation dialogs, `database.backup.restore_backup()` creates a fresh safety backup and replaces the current database file.
6. On success, `App.refresh_all_pages()` is attempted and the backup list is reloaded; if full refresh fails, the user is told to restart.

## State Management

The application uses simple page-local state plus the database as the primary source of truth.

Key state holders:

- SQLite database
- `App.pages`, `App.nav_buttons`, `App.current_page`, and `App.nav_button_defaults`
- page-scoped state such as `ProductsPage.selected_product_id`, `ProductsPage.selected_filter`, `ProductsPage.search_var`, `SalesPage.selected_product_id`, and `ReportsPage.selected_backup_path`
- global singletons: `settings`, `logger`, and `monitoring`

Implications:

- pages remain mounted for the lifetime of the app
- page activation can refresh data via `on_show()`
- some widget-level state persists across navigation by design, such as product search/filter state

## Database Model

The current schema contains three tables:

- `products`
- `sales`
- `schema_migrations`

Core relationships:

- `sales.product_id` references `products.id`
- deletes on products cascade to dependent sales when foreign keys are enabled
- indexes exist on product name, sales date, and sales product id

## Dependency Overview

High-level dependency graph:

```text
main.py
  -> ui.dashboard
  -> ui.products
  -> ui.sales
  -> ui.reports
  -> database.db
  -> config.settings
  -> utils.logging_config
  -> utils.monitoring

ui.dashboard
  -> services.analytics_service
  -> services.inventory_service
  -> utils.helpers

ui.products
  -> services.inventory_service
  -> utils.helpers

ui.sales
  -> services.sales_service
  -> services.inventory_service
  -> utils.helpers

ui.reports
  -> services.reporting_service
  -> database.backup
  -> config.settings

services.inventory_service
  -> database.queries
  -> utils.validators

services.sales_service
  -> services.inventory_service
  -> database.queries
  -> utils.validators

services.analytics_service
  -> database.queries

services.reporting_service
  -> services.analytics_service
  -> database.queries

database.queries
  -> database.db

database.db
  -> database.migrations
  -> database.backup
  -> config.settings
```

## Operational Behavior

### Logging

Logging is centralized through `utils.logging_config` and writes to:

- `logs/app.log`
- `logs/error.log`

### Backups

Startup behavior:

1. ensure required directories exist
2. create a timestamped database backup
3. keep only the most recent 30 backups

Manual restore behavior:

1. list known backup files from the configured backup directory
2. validate the selected path
3. create a fresh safety backup of the current database
4. copy the selected backup over the active database file
5. attempt app-wide page refresh

### Error Handling

Error handling is layered:

- page-level `try/except` blocks show dialogs
- `App.show_page()` handles lifecycle/navigation failures
- `App.refresh_all_pages()` is best-effort and used after restore
- `sys.excepthook` captures uncaught exceptions and logs them

## Current Test Coverage Summary

The current pytest suite passes with 108 tests and includes focused coverage for:

- validators
- inventory, sales, analytics, and reporting services
- database queries and transactional sale behavior
- navigation lifecycle and app refresh helpers
- products-page search/filter helpers
- reports-page backup validation and restore coordination

Coverage is strong in service/query logic and lightweight page/app coordination helpers. Direct GUI rendering coverage remains limited, and startup/build flows are still lightly tested.

## Architectural Strengths

- Clear separation between UI, service, and query layers
- Service-owned validation for submission paths
- Atomic sale workflow and consistent foreign-key enforcement
- Page lifecycle hooks provide predictable refresh points
- Backup creation, listing, and restore safety checks are integrated
- Focused tests cover core business behavior well

## Architectural Constraints

- Desktop-only, single-user design
- SQLite remains the storage engine and concurrency bottleneck
- GUI rendering itself is not deeply test-covered
- The app still depends on imperative page refreshes rather than a central state model
