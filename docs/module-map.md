# Module Map

## Top-Level Structure

```text
config/      configuration and environment-backed settings
database/    connections, migrations, backups, and SQL queries
docs/        project documentation
installer/   Inno Setup packaging script
scripts/     developer packaging helper
services/    business logic layer
tests/       pytest suite
ui/          CustomTkinter pages
utils/       shared helpers, validation, logging, monitoring
main.py      desktop application entry point
```

## Runtime Modules

### `main.py`

Primary responsibility:

- create the root application window and coordinate navigation/state refresh

Key behavior:

- sets the global exception hook
- initializes the database at startup
- creates and stores sidebar buttons
- maintains persistent active navigation state
- instantiates and switches between page frames
- calls page `on_show()` hooks on navigation
- provides `refresh_all_pages()` for app-wide lifecycle refresh

Imports:

- `ui.dashboard`
- `ui.products`
- `ui.sales`
- `ui.reports`
- `database.db`
- `config.settings`
- `utils.logging_config`
- `utils.monitoring`

### `config/settings.py`

Primary responsibility:

- load environment values and derive application paths

Key behavior:

- loads `.env` values via `python-dotenv`
- exposes the global `settings` object
- defines `DB_PATH`, `BACKUP_PATH`, and `LOG_PATH`
- creates backup and log directories on demand

### `database/db.py`

Primary responsibility:

- provide runtime SQLite connections and startup initialization

Key behavior:

- opens connections with `sqlite3.Row`
- enables foreign keys on runtime connections
- runs migrations on startup
- creates startup backups
- prunes old backups

### `database/migrations.py`

Primary responsibility:

- define and apply schema migrations

Key behavior:

- stores migrations in `MIGRATIONS`
- ensures `schema_migrations` exists
- records applied migration versions

### `database/queries.py`

Primary responsibility:

- encapsulate all SQL used by the application

Query groups:

- product CRUD
- stock update helpers
- sales inserts and sales history
- dashboard aggregates
- expiration-related queries
- best-selling analytics
- transactional sale recording

### `database/backup.py`

Primary responsibility:

- manage backup creation, retention, listing, and restore

Current runtime usage:

- `create_backup()` and `cleanup_old_backups()` are used during startup
- `get_backup_list()` and `restore_backup()` are now used by the Reports page backup UI

### `database/models.py`

Primary responsibility:

- define `Product` and `Sale` dataclasses

Current runtime usage:

- not used by production code
- not used by tests

### `services/inventory_service.py`

Primary responsibility:

- own product-related business rules and submission-path validation

Key behavior:

- parses and validates raw product form values
- creates, updates, deletes, and fetches products
- increases and decreases stock
- computes expiration status
- exposes low-stock, out-of-stock, expired, and expiring-soon lists

Dependencies:

- `database.queries`
- `utils.validators`
- `utils.logging_config`

### `services/sales_service.py`

Primary responsibility:

- own sale execution and sales-history access

Key behavior:

- parses and validates raw quantity input
- blocks expired products
- checks stock
- calculates totals/profit
- delegates the write path to transactional sale recording
- returns sale summaries for the UI

Dependencies:

- `database.queries`
- `services.inventory_service`
- `utils.validators`
- `utils.logging_config`

### `services/analytics_service.py`

Primary responsibility:

- aggregate dashboard metrics and best-selling insights

Key behavior:

- combines counts and totals from multiple queries
- exposes best-selling products for future UI/report use

### `services/reporting_service.py`

Primary responsibility:

- generate Excel reports

Key behavior:

- builds sales, inventory, and combined reports
- uses analytics metrics for the combined dashboard sheet
- writes `.xlsx` output through pandas/openpyxl

### `ui/dashboard.py`

Primary responsibility:

- render business summary metrics and alert cards

Key behavior:

- loads dashboard metrics and alert lists
- provides `on_show()` to refresh on navigation

Dependencies:

- `services.analytics_service`
- `services.inventory_service`
- `utils.helpers`

### `ui/products.py`

Primary responsibility:

- render product CRUD, search, and status filtering

Key behavior:

- collects raw form input and passes it to the service layer
- keeps page-local search and filter state
- filters by:
  - all products
  - low stock
  - out of stock
  - expired
  - expiring soon
- re-renders using the current search/filter state on refresh and navigation
- provides `on_show()`

Dependencies:

- `services.inventory_service`
- `utils.helpers`
- `tkinter.messagebox`

### `ui/sales.py`

Primary responsibility:

- render sales entry and sales history

Key behavior:

- passes raw quantity input to the service layer for submission
- keeps a client-side preview for total/profit display
- refreshes product choices and history via `on_show()`

Dependencies:

- `services.sales_service`
- `services.inventory_service`
- `utils.helpers`
- `tkinter.messagebox`

### `ui/reports.py`

Primary responsibility:

- render report export actions and backup restore management

Key behavior:

- exports sales, inventory, and combined reports
- loads and displays available backups
- validates selected backup paths against the configured backup directory
- performs strong confirmation before restore
- attempts app-wide refresh after restore
- provides `on_show()` for backup-list refresh

Dependencies:

- `services.reporting_service`
- `database.backup`
- `config.settings`
- `tkinter.messagebox`
- `tkinter.filedialog`

### `utils/validators.py`

Primary responsibility:

- centralize parsing and validation rules

Validation areas:

- product name
- prices
- quantities
- expiration dates
- product ids

### `utils/helpers.py`

Primary responsibility:

- formatting and small calculation helpers

Actively used:

- `format_currency()`

Currently unused:

- `format_date()`
- `is_expired()`
- `is_expiring_soon()`
- `calculate_profit()`
- `calculate_total_price()`

### `utils/logging_config.py`

Primary responsibility:

- configure the shared application logger

Key behavior:

- logs to file and stdout
- rotates application and error logs
- prevents duplicate handler registration

### `utils/monitoring.py`

Primary responsibility:

- track internal counters and health helpers

Actively used:

- `monitoring.log_operation()`
- `monitoring.log_error()`

Available but not surfaced in UI:

- `log_warning()`
- `get_metrics()`
- `health_check()`

## Import And Dependency Map

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

## Current Test Coverage Summary

The test suite currently passes with 108 tests.

Strongly covered areas:

- validators
- inventory, sales, analytics, and reporting services
- database queries
- transactional sale behavior
- app navigation helpers
- products-page filter helpers
- reports-page backup restore helpers

More lightly covered areas:

- direct GUI rendering and widget layout
- startup UI error paths
- build/installer flows
- some operational infrastructure behavior such as backup failure handling

## Low-Traffic Or Unused Areas

Confirmed low-usage or unused runtime areas:

- `database/models.py`
- several helper functions in `utils/helpers.py`
- several monitoring helpers in `utils/monitoring.py`
- `services.analytics_service.get_best_selling_products()` is implemented and test-covered but still not shown in the UI

## Naming Note

The repository and some supporting materials still use “Magazine Management System,” while most runtime modules and docs describe the product as “Inventory System.” This remains a documentation and product-identity inconsistency rather than a runtime bug.
