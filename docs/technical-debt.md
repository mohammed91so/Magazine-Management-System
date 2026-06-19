# Technical Debt Report

## Summary

The codebase is structurally solid and several previously high-risk runtime issues have already been fixed. The remaining debt is now concentrated in UX freshness, operational polish, and a few unintegrated capabilities rather than core transactional correctness.

The most relevant remaining debt items are:

- limited direct GUI test coverage
- some restore/backup behavior still depends on best-effort UI refresh
- monitoring and best-seller capabilities exist but are not surfaced to users
- repository/documentation naming still drifts between “Magazine Management System” and “Inventory System”

## Recently Fixed

These items are no longer current debt and should not be treated as open issues:

- combined report export path is fixed
- sale recording is transactional
- runtime SQLite foreign keys are enabled
- submission-path validation is service-owned rather than split across UI/service layers
- automatic page refresh on navigation is implemented through `on_show()`
- products page search/filter is implemented
- backup restore UI is implemented with path validation and strong confirmation

## Confirmed Remaining Issues

### 1. UI Rendering And Interaction Coverage Is Still Light

Severity: medium

Problem:

- the test suite covers helper logic and coordination well
- direct widget rendering and live GUI interactions are still mostly untested

Impact:

- layout regressions, event-binding mistakes, and widget state bugs are more likely to be caught manually than automatically

Why it matters:

- the app is desktop UI-first, so rendering behavior is part of the product, not just presentation

Practical next step:

- add focused tests for more page-level coordination and consider a thin smoke layer around page construction where feasible

### 2. Restore Refresh Is Best-Effort Rather Than Fully State-Rebuilt

Severity: medium

Problem:

- after restore, the app attempts `refresh_all_pages()`
- page refresh works for current page-local data flows, but the app does not fully reconstruct the process state

Impact:

- some edge-case in-memory UI state could remain stale after restore, especially if future pages gain richer local state

Why it matters:

- restore is a recovery workflow, so users need strong confidence that post-restore state is accurate

Practical next step:

- decide whether long-term restore should trigger a controlled app restart instead of best-effort refresh

### 3. Monitoring Exists But Is Not Operationally Surfaced

Severity: low

Problem:

- `utils.monitoring` tracks counters and health-check information
- users and admins cannot view that information in the UI

Impact:

- support and troubleshooting still depend mainly on log inspection

Why it matters:

- health and error counters would improve confidence during backup/restore and other operational workflows

Practical next step:

- expose a lightweight admin/status view or a diagnostics dialog

### 4. Best-Selling Analytics Exist But Are Not Exposed

Severity: low

Problem:

- best-seller analytics are implemented and tested
- no page or report currently surfaces them

Impact:

- the app underuses data it already computes

Why it matters:

- sales insight is valuable from a user perspective and already mostly paid for in code

Practical next step:

- add best-seller cards to the dashboard or include them in reports

### 5. Backup Management Is Safe But Operationally Minimal

Severity: low

Problem:

- backups can now be listed and restored
- there is still no richer operational context such as backup age warnings, backup origin labels, or restore audit visibility in the UI

Impact:

- users can restore safely, but they still have limited context for choosing the right backup under stress

Why it matters:

- recovery UX matters most when users are already under pressure

Practical next step:

- show backup age, clearer naming, and possibly a “created automatically before restore” hint in the backup list

## Dead Code And Low-Value Areas

### Unused Runtime Code

- `database/models.py`
- `utils.helpers.format_date()`
- `utils.helpers.is_expired()`
- `utils.helpers.is_expiring_soon()`
- `utils.helpers.calculate_profit()`
- `utils.helpers.calculate_total_price()`
- `utils.monitoring.log_warning()`
- `utils.monitoring.get_metrics()`
- `utils.monitoring.health_check()`

### Low-Value Or Underused Paths

- `services.analytics_service.get_best_selling_products()` is implemented but not used by production UI
- some backup and monitoring infrastructure remains backend-only from the user perspective

## Documentation And Naming Debt

### Identity Mismatch

Problem:

- the repository and some supporting documents say “Magazine Management System”
- the code, UI, and most runtime docs say “Inventory System”

Impact:

- maintainers and users see inconsistent product identity

Practical next step:

- choose one product name and align repository metadata, docs, packaging, and user-facing strings

### Documentation Drift Risk

Problem:

- the app has moved quickly through several reliability and UX improvements
- docs can become stale unless updated alongside feature work

Impact:

- future contributors may follow obsolete assumptions about refresh, validation, restore, or navigation behavior

Practical next step:

- keep implementation docs part of the acceptance criteria for major UI or workflow changes

## Current Test Coverage Summary

The test suite currently passes with 108 tests and gives strong confidence in:

- validation behavior
- service-layer business logic
- query-layer behavior
- transactional sales
- products filtering helpers
- restore path validation and restore coordination helpers
- navigation helper behavior

Remaining coverage gaps:

- direct GUI rendering behavior
- startup failure paths
- operational failure scenarios in packaging/build/installer flows

## Overall Assessment

The major reliability debt has been reduced significantly. The next worthwhile work is less about fixing broken fundamentals and more about:

1. improving operator confidence after recovery workflows
2. surfacing already-implemented operational insight
3. expanding GUI-focused regression coverage
4. reducing naming/documentation drift
