# Automatic Repository Analysis

Run this before the first edit in any repo, and again when a task reaches a part of the code you haven't seen. `scripts/analyze_repo.py <root>` automates most of it. This file is the manual fallback and explains what to look for.

## 1. Toolchain and targets
- `pubspec.yaml`: app name (it's the `package:` import prefix), `environment.sdk` and `flutter` constraints, dependencies, dev_dependencies, `flutter:` assets/fonts.
- `pubspec.lock`: the versions actually resolved. Use these when reading docs.
- Platform folders present: `android/`, `ios/`, `web/`, `macos/`, `windows/`, `linux/`. Treat only those as targets.
- `analysis_options.yaml`: lint set (`flutter_lints`, `very_good_analysis`, custom rules) and excluded paths.
- Android: `android/app/build.gradle(.kts)` for `applicationId`, `minSdk`/`targetSdk`, flavors, signing config (*names only*); `AndroidManifest.xml` permissions.
- iOS: `ios/Runner/Info.plist` usage descriptions, `Podfile` platform version, entitlements.
- Build-time config: `--dart-define` / `String.fromEnvironment` usage, `.env` loaders, flavor entry points (`main_dev.dart`).

## 2. Architecture fingerprint
- **Folder layout:** feature-first (`lib/feature(s)/<name>/{controller,view,model,service}`) or layer-first (`lib/{controllers,views,models}`), or clean (`data/domain/presentation`).
- **State management:** imports of `get`, `provider`, `flutter_riverpod`/`hooks_riverpod`, `flutter_bloc`, `mobx`, or plain `setState`/`ValueNotifier`.
- **DI and lifetimes:** `Get.put` / `Get.lazyPut` / `Bindings`, `get_it`, Riverpod providers, `MultiProvider`. *Where* registration happens matters, e.g. inside `build()` versus in bindings or `main()`.
- **Routing:** `GetMaterialApp` + `GetPage`, `go_router`, `auto_route`, or `Navigator` 1.0. Is there one routes file, or are routes ad hoc (`Get.to(() => Page())`)?
- **Networking:** `http`, `dio`, `chopper`, `retrofit`, GraphQL. Find the client class, base URL source, auth header injection, error types, timeout, and refresh-token flow.
- **Models:** hand-written `fromJson`, `json_serializable`, `freezed`, or raw `Map` access in controllers.
- **Persistence:** `shared_preferences`, `flutter_secure_storage`, `hive`, `isar`, `sqflite`/`drift`. Note what is stored where, and flag tokens in plain prefs.
- **Firebase:** `firebase_options.dart`, which `firebase_*` packages, and whether init is guarded.
- **UI system:** theme setup, colour token classes, text-style helpers, responsive helpers (`flutter_screenutil`, `MediaQuery`, `LayoutBuilder`), shared widgets folder, dialog/toast library.
- **Observability:** Crashlytics, Sentry, analytics, logging wrappers.

## 3. Quality signals
- `test/` and `integration_test/`: do they exist, and what's covered?
- Lint suppressions (`// ignore:`), large commented-out blocks, TODO/FIXME density.
- Very large files (>600 lines) that suggest a split.
- Typos in filenames or classes. Note them; don't rename without approval.
- Duplicate implementations of the same thing, such as two text-field widgets or two API helpers.

## 4. Risk scan (report, don't fix unasked)

**Critical, report first** (seen in real repos):
- Signing material tracked in git: `*.jks`, `*.keystore`, `*.pem`, `*.p12`, `key.properties`. Check with `git ls-files`. An `.gitignore` rule added *after* committing doesn't untrack them. Losing control of an upload key means a Play upload-key reset.
- Payment secret keys (`sk_live_`, `sk_test_`, `rk_`) in source *or history* (`git log -p -S sk_`), and any Dart call to `api.stripe.com`.
- Never print the secret values in your report. Show file and line only, redacted.
- Tokens, passwords or PII in `SharedPreferences` or logs.
- Hardcoded secrets or private endpoints in source. Note that some values (Firebase options, Sentry DSN, Clarity id) are designed to ship in the binary and are not secrets.
- `!` on network data; `as` casts on JSON without type checks.
- Controllers created in `build()` or never disposed; `Get.find` without `Get.isRegistered` where registration is conditional.
- `BuildContext` used after `await` without a `mounted` check.
- Unbounded lists without `ListView.builder`; images without sizing/caching.
- Firebase/plugin init that can crash startup if it fails.

## 5. Output: the Project profile

```markdown
**Project profile: <app name>**
- Flutter/Dart: <constraints>, targets: <platforms>
- Structure: <feature-first …>, entry: lib/main.dart
- State/DI: <GetX, controllers registered via …>
- Routing: <…>
- Networking: <client, base URL via --dart-define, error types, refresh flow>
- Persistence: <…>
- Firebase: <products>
- UI system: <theme/tokens/shared widgets/dialog lib>
- Tests: <none / unit / widget / integration>
- Conventions to follow: <3–6 bullets>
- Risks noticed: <bullets, with file refs>
```

Keep it short. It sets the rules for the rest of the task.
