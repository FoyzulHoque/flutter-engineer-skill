# Multi-file Feature Implementation

## Build in dependency order

Create or change files bottom-up so each layer compiles against the one beneath it:

1. **Contract.** Confirm the API/Firebase/platform contract: endpoints, request and response shapes, error codes. Add endpoint constants to the project's endpoints file.
2. **Models.** Typed models with defensive `fromJson` (or the project's codegen). Include `toJson` only if it's sent.
3. **Service / repository / data source.** Use the project's existing API client. Map transport errors to the project's error type. Don't invent a second client.
4. **Controller / state.** Observable state, actions, loading/empty/error handling, double-submit guards, cancellation of stale requests.
5. **Widgets / views.** Compose from shared widgets and tokens. Feature-private widgets go in `view/widget/`.
6. **Wiring.** Routes, DI registration/bindings, nav entry points, deep links, notification routing.
7. **Platform config** (only if needed): permissions in `AndroidManifest.xml` / `Info.plist`, Gradle/Podfile changes. These need approval.
8. **Tests:** model parsing, controller transitions, a widget test for each state.

After each layer, run `flutter analyze` on the changed files. Don't pile five layers of errors together.

## Dependency awareness checklist

Before editing a shared file, find everything that depends on it (`grep -rn "ClassName\|methodName" lib test`) and list who is affected.
- Changing a model field: update every `fromJson` consumer and every view that reads it.
- Changing a shared widget's constructor: update all call sites or add an optional parameter with a safe default.
- Changing an API client method signature: this touches every feature. It needs approval and should be done in one coordinated change.
- Changing a controller registered `permanent` or found across features with `Get.find`: check every `Get.find<ThatController>()`.
- Renaming files or routes: update imports, route tables, deep-link handlers and notification routers.

## Consistency rules
- Put new files where siblings live, and name them like siblings (`<feature>_controller.dart`, `<feature>_view.dart`).
- Reuse the project's colour/text-style/spacing tokens. If the project defines per-feature colour classes, follow that pattern instead of hardcoding colours.
- Reuse the project's dialog/toast/loader mechanism (e.g. `SmartDialog`, `Get.snackbar`, a custom sheet).
- Use the same import style the project uses (`package:<app>/…` is typical).
- Mirror the project's comment style. Many production codebases document the *why* in doc comments. Match density, don't over- or under-comment.

## State model for any async screen

```dart
final loading = false.obs;
final error = RxnString();
final items = <Item>[].obs;

bool get isEmpty => !loading.value && error.value == null && items.isEmpty;
```

Render in this order: first load (spinner) → error with retry → empty state → data (with pull-to-refresh). Keep already-loaded data visible during a refresh, and keep it on a refresh error (show a snackbar instead of wiping the list).

## Non-idempotent actions (place order, pay, submit form)
- Guard with an `isSubmitting` flag, and disable the button while it's true.
- Send an idempotency key if the backend supports one.
- On timeout, don't auto-retry a payment. Check the order or payment status first.

## Done means
- Analyzer clean on changed files (or pre-existing issues called out).
- Tests added or updated and run.
- Every state (loading/empty/error/data/offline) reachable and rendered.
- No new secrets, no stray debug prints of PII, no commented-out dead code left behind.
