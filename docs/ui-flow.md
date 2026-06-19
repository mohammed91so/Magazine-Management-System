# UI Flow And Window Map

## Window Hierarchy

The application contains one CustomTkinter root window and four top-level page frames. There are no custom `CTkToplevel` windows and no secondary application windows.

Hierarchy:

```text
App (CTk root)
  |- sidebar (CTkFrame)
  |  |- title label
  |  |- Dashboard button
  |  |- Products button
  |  |- Sales button
  |  |- Reports button
  |  `- version label
  `- content (CTkFrame)
     |- DashboardPage (CTkFrame)
     |- ProductsPage (CTkFrame)
     |- SalesPage (CTkFrame)
     `- ReportsPage (CTkFrame)
```

## Root Window: `App`

Defined in `main.py`.

Responsibilities:

- configure the main window title and size
- initialize the database before rendering the UI
- create the sidebar and content layout
- instantiate all page frames once
- store and style sidebar button references
- raise the requested page
- refresh all pages after restore when practical

Layout:

- left column: fixed-width sidebar
- right column: content frame with one active page at a time

Navigation behavior:

- each sidebar button calls `show_page(name)`
- `show_page()`:
  - finds the page in `self.pages`
  - calls `page.on_show()` if present
  - raises the page with `tkraise()`
  - updates persistent active-button styling
- `refresh_all_pages()` iterates every page and calls `on_show()` where available

## Sidebar Navigation State

The sidebar now keeps the active page highlighted even after hover ends.

Current behavior:

- only one sidebar button is active at a time
- the active state updates after a successful page switch
- button references are stored in `self.nav_buttons`
- `self.current_page` tracks the current page key

## Startup Flow

1. `App` is created.
2. Database initialization completes before pages are built.
3. `_setup_layout()` creates `sidebar` and `content`.
4. `_setup_pages()` creates:
   - `DashboardPage(self.content)`
   - `ProductsPage(self.content)`
   - `SalesPage(self.content)`
   - `ReportsPage(self.content)`
5. All pages are gridded into the same content slot.
6. `_setup_navigation()` creates and stores the sidebar buttons.
7. `show_page("dashboard")` refreshes and raises the dashboard first.

If startup fails, the app shows a standard Tk error dialog and exits.

## Page Flow Summary

### Dashboard Page

Defined in `ui/dashboard.py`.

Internal structure:

```text
DashboardPage
  |- title label
  |- metrics_frame
  |  `- 8 metric card frames
  |- alerts_frame
  |  |- alerts title
  |  `- alerts_scroll (CTkScrollableFrame)
  `- refresh button
```

Behavior:

1. `__init__()` builds the page and calls `load_metrics()`.
2. `load_metrics()` refreshes aggregate metrics and alert rows.
3. `on_show()` calls `load_metrics()` whenever the page becomes active.
4. The refresh button reruns `load_metrics()`.

Dialogs:

- no custom windows
- failures are rendered inline as alert rows

### Products Page

Defined in `ui/products.py`.

Internal structure:

```text
ProductsPage
  |- title label
  |- form_frame
  |  |- name label + entry
  |  |- purchase price label + entry
  |  |- selling price label + entry
  |  |- quantity label + entry
  |  `- expiration date label + entry
  |- buttons_frame
  |  |- Add Product button
  |  |- Update Product button
  |  |- Delete Product button
  |  |- Clear Form button
  |  `- Refresh button
  |- filter_frame
  |  |- Search label + entry
  |  `- Filter label + option menu
  `- table_frame (CTkScrollableFrame)
     |- header row
     `- repeated product row frames
```

Behavior:

1. `__init__()` sets `selected_product_id`, `selected_filter`, and `search_var`.
2. `refresh()` loads products for the active filter, applies the current search text, and re-renders rows.
3. `on_show()` calls `refresh()` so the page stays current on navigation.
4. Search filters rows by product name as the user types.
5. Filter options are:
   - `All`
   - `Low stock`
   - `Out of stock`
   - `Expired`
   - `Expiring soon`
6. Add/update/delete still use the form and preserve the current search/filter state after refresh.

Dialogs:

- success dialogs for add/update/delete
- warning dialog if update/delete is attempted without selection
- confirmation dialog before deletion
- error dialogs for load or mutation failures

### Sales Page

Defined in `ui/sales.py`.

Internal structure:

```text
SalesPage
  |- title label
  |- form_frame
  |  |- product label
  |  |- product dropdown
  |  |- quantity label
  |  `- quantity entry
  |- preview_frame
  |  |- total price label
  |  `- profit label
  |- Complete Sale button
  |- Refresh button
  |- history label
  `- history_frame (CTkScrollableFrame)
     |- header row
     `- repeated sales row frames
```

Behavior:

1. `__init__()` builds the page, loads products, and loads history.
2. `refresh_products()` reloads the dropdown from current inventory.
3. `refresh_history()` rebuilds the sales history table.
4. `on_show()` refreshes both product options and history on navigation.
5. `sell()` passes the raw quantity string to the service layer.
6. `update_preview()` remains a client-side preview helper and is not the source of submission validation.

Dialogs:

- warning if no product is selected
- success dialog after sale completion
- validation or general error dialogs on failure

### Reports Page

Defined in `ui/reports.py`.

Internal structure:

```text
ReportsPage
  |- title label
  |- description label
  |- reports_frame
  |  |- Export Sales Report button
  |  |- Export Inventory Report button
  |  |- Export Combined Report button
  |  `- info label
  `- backup_frame
     |- backup title
     |- restore warning label
     |- backup_actions_frame
     |  |- Refresh Backups button
     |  `- Restore Selected Backup button
     `- backup_list_frame (CTkScrollableFrame)
        `- backup rows or empty-state label
```

Behavior:

1. `__init__()` creates `ReportingService`, initializes backup state, builds the UI, and loads backups.
2. Export actions still open save-file dialogs and delegate Excel generation to `ReportingService`.
3. Backup management loads files from the configured backup directory.
4. Backup rows show timestamp and file size when available.
5. Only one backup can be selected at a time.
6. `on_show()` reloads the backup list.
7. `restore_selected_backup()`:
   - blocks when no backup is selected
   - validates the selected path exists, is a file, and resolves inside `settings.BACKUP_PATH`
   - shows two confirmation dialogs
   - calls `restore_backup()`
   - attempts `refresh_all_pages()`
   - reloads backups and shows success or restart-required messaging

Dialogs:

- save-file dialogs for exports
- success/warning/error dialogs for export actions
- warning dialogs for restore preconditions and restore-completed-with-restart-needed
- error dialogs for backup load, validation, or restore failures

## Automatic Refresh Behavior

The app now uses page lifecycle hooks to refresh data on navigation.

Current hooks:

- `DashboardPage.on_show()` -> `load_metrics()`
- `ProductsPage.on_show()` -> `refresh()`
- `SalesPage.on_show()` -> `refresh_products()` and `refresh_history()`
- `ReportsPage.on_show()` -> `refresh_backups()`

Additionally:

- `App.refresh_all_pages()` calls all available `on_show()` hooks and is used after a successful backup restore
- `ProductsPage` preserves search/filter state when refreshed

## Non-CustomTkinter Dialog Map

The app relies on standard Tk dialogs for transactional feedback.

Dialog usage by area:

- `main.py`: startup, navigation, and fatal error dialogs
- `ui/products.py`: success, warning, delete confirmation, and error dialogs
- `ui/sales.py`: warning, success, and error dialogs
- `ui/reports.py`: save-file dialogs, export feedback, restore confirmations, and restore feedback

## UI Flow Observations

- The dashboard remains the default landing page.
- Navigation is still simple and static, but it now has persistent active-state feedback.
- Products is the richest management surface, combining CRUD with client-side search and filters.
- Reports is now both an export surface and an operational recovery surface for backups.
- The UI remains a single-window management console, with lifecycle refreshes improving freshness without redesigning navigation.
