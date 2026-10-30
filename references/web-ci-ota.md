# Web Target, CI/CD and Over-the-Air Patches

Learned from a production GetX app that ships one codebase to Android, iOS and web, deploys web from CI, and patches mobile with Shorebird. Sources: https://docs.flutter.dev/platform-integration/web, https://docs.flutter.dev/deployment/web, https://docs.shorebird.dev.

## One codebase on web

**Keep `dart:io` out of shared code.** A single import of `dart:io` (`File`, `Platform`, `HttpClient`) breaks the web build. Use a conditional export shim:
```dart
// lib/core/platform/io_shim.dart
export 'io_shim_stub.dart' if (dart.library.io) 'io_shim_io.dart';
```
`io_shim_io.dart` re-exports `dart:io`. The stub defines the same API surface the app uses (`File.exists() → false`, `Platform.isIOS → false`). Then import the shim everywhere instead of `dart:io`. The same `if (dart.library.io)` trick works per widget (e.g. a local photo preview with an `Image.file` vs `Image.network` implementation).

**Guard platform-only calls with `kIsWeb`.** It's a compile-time constant, so web-only code is tree-shaken out of mobile builds and vice versa. Method channels: `if (kIsWeb) return;` before `invokeMethod`.

**Phone-first app on a desktop browser:** wrap the app in a `WebShell` that, on wide viewports, centers it at a max width (~480) on a neutral background. Keep the **same widget tree shape** in both branches (always `LayoutBuilder → Center → SizedBox`), because swapping tree structure on resize causes element assertion errors during GetX navigation.

**Features that are mobile-only by product choice** (e.g. chat with no web push): show a body-level `MobileOnlyNotice` with store links instead of a broken half-feature. The caller keeps its own Scaffold/AppBar so it still reads as the feature tapped. Hardcode the store URLs, since this screen must render without an API.

**Web plugin check:** before using a plugin on web, confirm the web badge on pub.dev. Push needs a VAPID key + service worker. Camera, file system, background location and SMS autofill differ or don't exist.

## Hosting (SPA)

Static hosts need a rewrite of all paths to `index.html` so deep links and refreshes work. For Vercel, put `vercel.json` in the build output with `framework: null`, a no-op `buildCommand` (otherwise Vercel auto-detects a framework and fails), and `rewrites: [{ "source": "/(.*)", "destination": "/index.html" }]`.

## CI/CD

- `subosito/flutter-action` with `channel: stable` and `cache: true`, then `flutter pub get`.
- **Pass `--dart-define` values explicitly in CI** even when code has prod defaults, so a changed default can never ship a prod build pointing at dev.
- `concurrency: { group: deploy-web-prod, cancel-in-progress: true }`, so only one prod deploy runs and the newest push wins.
- Secrets (`VERCEL_TOKEN`, signing keys, store credentials) live in CI secrets, never in the repo or workflow file.
- Add a check job before deploy: `flutter analyze` + `flutter test`. A deploy workflow without them ships regressions.
- Creating or changing deploy workflows is approval-gated, because it publishes.

## Shorebird over-the-air patches

What patches can and can't do:
- **Can:** change Dart code in an already-released build.
- **Can't:** change native code, plugins, `AndroidManifest`/`Info.plist`, assets, or **icon glyphs**. Release builds tree-shake icon fonts, so an `Icons.x` not used in the store release renders blank in a patch. In patched code, use only icons already present in the shipped release, or ship a new store build.
- A downloaded patch applies on the **next app start**. There's no hot swap.

A safe patch gate (the pattern that worked):
- `auto_update: false` in `shorebird.yaml`, so the app decides when to download.
- Construct `ShorebirdUpdater` **lazily and after the first frame**. Its constructor makes a synchronous FFI call that can block, and a synchronous hang can't be timed out.
- `if (kIsWeb || !updater.isAvailable) return none;`, since there's no Shorebird engine on web, in debug, or in plain `flutter build`.
- Bounded timeouts: a short check (~5s, overlapped with the splash), a longer download (~30s). On timeout, let the user in and retry next launch.
- **Fail open, and cap the lockout.** A non-dismissible "restart to update" dialog must stop blocking after N consecutive launches (e.g. 3). Otherwise a patch that never applies locks users out forever, and you can't patch the patcher. Store the counter under its own key so logout's `clearAll()` doesn't reset it.
- Non-dismissible dialogs need **both** `barrierDismissible: false` and `PopScope(canPop: false)`. Without the second, the Android back gesture still closes it.
- Coordinate with any store force-update gate so two blocking dialogs never collide.

`shorebird release` / `shorebird patch` publish to users. They're approval-gated like store uploads.
