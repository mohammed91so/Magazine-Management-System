# Product Roadmap

## Perspective

This roadmap looks at the current desktop app from a store-owner or clerk perspective rather than a codebase perspective.

Today the app already covers the core loop well:

- add products
- record sales
- watch basic dashboard metrics
- export reports

The main opportunities are improving speed for repeated daily tasks, reducing manual checking, and exposing operational features that already exist behind the scenes.

## High Value / Low Effort Improvements

- Add product search and simple filtering on the Products page.
  Users currently scroll a full list to find an item before updating or deleting it.

- Add sort options for products and sales history.
  Common user needs are sorting by name, quantity, expiration date, newest sales, and highest profit items.

- Make low-stock and expired alerts clickable.
  The dashboard already shows alerts, but users cannot jump directly to the affected items.

- Add a visible "last refreshed" or "last updated" timestamp on dashboard and sales/history views.
  This builds trust that the app is showing current data after navigation or actions.

- Improve empty states for reports, products, and sales.
  Clear messages such as "No products yet" or "No sales recorded yet" reduce confusion for first-time users.

- Add lightweight confirmation details before destructive actions.
  Showing the product name in delete confirmation would make the action feel safer and more professional.

- Add an explicit stock-adjustment action in the UI.
  The service layer already supports increasing and decreasing stock, but users currently have to edit the whole product record to correct stock.

## High Value / Medium Effort Improvements

- Add a dedicated inventory alerts view.
  Users would benefit from a focused list of low-stock, out-of-stock, expired, and expiring-soon items with quick follow-up actions.

- Add richer reporting options.
  Date-range filtering, product-specific sales exports, and summary cards before export would make reports more useful for actual business review.

- Add dashboard insights for top-selling products.
  The app tracks enough data to show best sellers, but users do not currently see that insight in the interface.

- Add backup management in the UI.
  Automatic backups are helpful, but users cannot view available backups, restore one, or confirm backup health from the product experience.

- Add safer sales workflows for busy operators.
  Examples include a clearer sale confirmation summary, stock-left-after-sale visibility, and warnings before selling the last units of an item.

- Add better product list ergonomics for larger inventories.
  Sticky headers, pagination or chunked loading, and clearer row selection feedback would help once the product list grows.

- Add a simple settings or admin screen.
  Even a small surface for report folder defaults, low-stock threshold, and backup visibility would improve daily administration.

## Nice-to-Have Improvements

- Add a sales trends view.
  Weekly or monthly earnings trends would help owners understand performance without exporting to Excel.

- Add product photos or categories.
  These would improve usability for visually scanning inventory, especially in mixed catalogs.

- Add printable summaries or receipt-style sale summaries.
  Useful for shops that want lightweight paper workflows.

- Add keyboard shortcuts for fast data entry.
  This would make the desktop app more efficient for repeat operators.

- Add a compact operator mode.
  A simplified sales-focused layout could help when the app is used primarily at a counter.

- Add onboarding guidance for first-time users.
  A short empty-state checklist such as "Add your first product" and "Record your first sale" would improve first-run experience.

## Features Partly Implemented But Not Exposed In UI

- Backup restore support already exists in code.
  `database.backup.restore_backup()` and `get_backup_list()` provide the core logic, but there is no UI for browsing or restoring backups.

- Monitoring and health-check logic already exists.
  `utils.monitoring` tracks operation counts, errors, warnings, uptime, and health-check status, but none of that is surfaced to users or admins.

- Best-selling product analytics already exist.
  `services.analytics_service.get_best_selling_products()` is implemented and test-covered, but there is no dashboard or report UI exposing it.

- Inventory stock adjustment logic already exists.
  `increase_stock()` and `decrease_stock()` are available in the service layer, but the UI does not provide direct stock-adjustment actions.

- Combined reporting is richer than the UI suggests.
  The combined export already assembles sales, inventory, and dashboard metrics into one workbook, but the interface does not preview or explain that value to users.

- Backup lifecycle management is already active.
  The app creates and prunes backups automatically at startup, but users have no way to see backup history or confirm that protection is working.

## Suggested Delivery Order

1. Product search, sorting, better empty states, and direct stock adjustment.
2. Alert drill-downs, top-seller visibility, and richer report filtering.
3. Backup management and simple admin/health surfaces.
4. Nice-to-have usability polish such as shortcuts, trends, and onboarding.
