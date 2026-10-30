# Dashboards, Charts and Money

From reviewing ~15 chart-heavy apps (analytics, finance calculators, habit trackers). Sources: `fl_chart` on pub.dev (check the pinned version's API), and `intl` `NumberFormat`.

## Charts (`fl_chart`)

Found: touch disabled (`LineTouchData(enabled: false)`), so users can't read values. `Colors.purple` hardcoded for series. `maxY = max(a, b) * 1.2` with `horizontalInterval: maxY / 4`, which **breaks when all values are 0** (interval 0 asserts or hangs). Gradients hardcoded outside the theme. Only one app handled loading → empty → data.

Do:
- **Guard empty and zero data:** if there are no points or all values are zero, render an empty state ("No spending this week"), not a chart. Clamp `maxY` to at least 1 and `interval > 0`.
- **Touch on**, with tooltips showing the formatted value + label (`getTooltipItems`). Tooltip and axis text from the theme's text styles.
- **Series colours from tokens** (`AppColors.chart1…n`, or derived from the `ColorScheme`). Make them distinguishable for colour-blind users, and add a legend or direct labels. Never rely on colour alone.
- **Axis labels formatted** with `NumberFormat.compact()` ("1.2K", "3M") and dates with `DateFormat`. Show fewer labels on small screens (`reservedSize`, `interval`).
- Animate on first load only (`duration`). Don't re-animate on every rebuild.
- Wrap each chart in its own widget, and rebuild only when its data changes (`Obx`/`select` around the chart, not the screen).
- Big numbers first: KPI tiles (value, delta, period) above charts, and tabular figures (`FontFeature.tabularFigures()`) for aligned numbers.

## Responsive dashboards (tablet, web, desktop)
- `LayoutBuilder` breakpoints (e.g. < 600 one column, 600–1024 two, > 1024 three or a side nav), not `MediaQuery.size` checks scattered through widgets.
- Use `NavigationRail`/a side nav on wide screens and a bottom nav on phones.
- Tables: `DataTable` for small data, `data_table_2`/`TableView` (two_dimensional_scrollables) for large data with sticky headers. Paginate server-side.
- Phone-first apps on web: constrain width (see `web-ci-ota.md`, `WebShell`).

## Money and financial apps

Found in a finance-calculator app: amounts as `double`, formatted by hand (`"\$${v.toStringAsFixed(0)}"`, hand-rolled "k" suffixes). 58 `toStringAsFixed` calls versus 1 `NumberFormat.currency`. A hardcoded `$` symbol. No disclaimers. No secure storage or app lock, even though it displays net worth and debts.

Do:
- **Never store or compute money in `double`.** Use integer minor units (cents as `int`) or `Decimal` (`decimal` package) for sums, interest and splits. Round once, at the end, with a stated rule (banker's vs half-up). Doubles are OK only for chart *display*.
- **Format with `NumberFormat.currency(locale:, symbol:/name:)`** or `NumberFormat.simpleCurrency`, and `NumberFormat.compactCurrency` for tight spaces. Never `"\$" + toStringAsFixed`. Currency and locale come from the user's settings/account.
- Percentages: `NumberFormat.percentPattern()`. Show the rate's precision explicitly (e.g. 6.24% p.a.).
- Calculators: unit-test the formulas (repayment, LVR, DTI, compound interest) against known worked examples. Pure functions, no widgets (see the testing pattern in `api-debugging-testing.md`).
- Inputs: numeric keyboard, a currency input formatter, and validation messages that state the range ("Enter an amount between $1,000 and $5,000,000").
- **Compliance copy:** calculators that give estimates need a short disclaimer ("Estimate only, not financial advice"). Check the client's jurisdiction requirements (e.g. AU general advice warning). Ask, don't invent legal text.
- **Sensitive data:** tokens in `flutter_secure_storage`, an optional biometric app lock (`local_auth`), hiding content in the app switcher / blocking screenshots on sensitive screens (check the package's current platform support), auto-logout on inactivity if required, and no amounts or account numbers in logs or analytics.
- Wallet/crypto apps: never store seed phrases or private keys in plain prefs, and never log them. Treat key management as an approval-gated, security-reviewed area.
