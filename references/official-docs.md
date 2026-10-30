# Official Documentation Map

These are the primary sources. Prefer them over memory, blog posts or Stack Overflow whenever behavior could depend on a version, platform or policy. When you cite a fact, name the page you got it from.

## How to look things up

1. **Pin the version first.** Read `pubspec.yaml` (constraints) and `pubspec.lock` (resolved versions), plus `flutter --version` if you can run it. Docs for a newer version can be wrong for this project.
2. **Go to the narrowest source.** Use the package's own pub.dev page for package APIs. For framework widgets use the Flutter API reference. For store rules use the store's console help.
3. **Read the changelog for migrations.** Breaking changes live in `CHANGELOG.md` on pub.dev (the "Changelog" tab) and in Flutter's "Breaking changes" page.
4. **If you can't fetch the page**, say so and give the user the URL. Don't present remembered details as verified.

## Source by question

| Question | Where to look |
|---|---|
| Install, set up, platform requirements | https://docs.flutter.dev/get-started |
| Widget/class API, constructor params | https://api.flutter.dev (linked from https://docs.flutter.dev) |
| Layout, constraints, overflow errors | https://docs.flutter.dev/ui/layout and https://docs.flutter.dev/ui/layout/constraints |
| State management options | https://docs.flutter.dev/data-and-backend/state-mgmt |
| Networking, JSON, serialization | https://docs.flutter.dev/data-and-backend/networking and https://docs.flutter.dev/data-and-backend/serialization/json |
| Navigation and deep links | https://docs.flutter.dev/ui/navigation |
| Platform channels, native integration | https://docs.flutter.dev/platform-integration |
| Web / desktop specifics | https://docs.flutter.dev/platform-integration/web, `/windows`, `/macos`, `/linux` |
| Performance, jank, DevTools | https://docs.flutter.dev/perf and https://docs.flutter.dev/tools/devtools |
| Testing (unit, widget, integration) | https://docs.flutter.dev/testing |
| Common errors explained | https://docs.flutter.dev/testing/common-errors |
| Breaking changes / migration guides | https://docs.flutter.dev/release/breaking-changes |
| Build and release Android | https://docs.flutter.dev/deployment/android |
| Build and release iOS | https://docs.flutter.dev/deployment/ios |
| Accessibility, i18n | https://docs.flutter.dev/ui/accessibility-and-internationalization |
| Project overview, showcase, news | https://flutter.dev |
| Any package: API, platforms, version, changelog | https://pub.dev/packages/<name> (tabs: Readme, Changelog, Example, Versions, Scores) |
| Comparing packages | pub.dev scores: likes, pub points, popularity, "Flutter Favorite", verified publisher, last publish date, platform badges |
| Firebase product overview | https://firebase.google.com |
| FlutterFire setup (`flutterfire configure`) | https://firebase.google.com/docs/flutter/setup |
| Specific Firebase products | https://firebase.google.com/docs/<product> (e.g. `cloud-messaging`, `crashlytics`, `perf-mon`, `auth`, `firestore`, `remote-config`, `app-check`) |
| Firebase security rules | https://firebase.google.com/docs/rules |
| Google Play publishing, tracks, policy | https://developer.android.com/distribute/console |
| Android target SDK, permissions, manifest | https://developer.android.com/guide and https://developer.android.com/google/play/requirements/target-sdk |
| iOS frameworks, entitlements, Info.plist keys | https://developer.apple.com/documentation/ |
| App Store review and submission | https://developer.apple.com/app-store/review/guidelines/ and App Store Connect help |
| Flame engine (games) | https://docs.flame-engine.org/latest/ |
| Method channels, Pigeon | https://docs.flutter.dev/platform-integration/platform-channels |
| FFI / native C libraries | https://docs.flutter.dev/platform-integration/android/c-interop and `/ios/c-interop` |
| Subscriptions and IAP via RevenueCat | https://www.revenuecat.com/docs/welcome/overview (+ `purchases_flutter` on pub.dev) |
| Stripe payments, PaymentSheet, webhooks | https://docs.stripe.com/ (+ `flutter_stripe` on pub.dev) |
| Google Play Billing | https://developer.android.com/google/play/billing |
| Google Pay | https://developers.google.com/pay |
| Apple Pay / StoreKit | https://developer.apple.com/documentation/passkit and https://developer.apple.com/documentation/storekit |

## Evaluating a new package (before asking to add it)

Check on pub.dev and report:
- platforms supported (match the project's targets, including web if built)
- latest version, publish date, and whether it's compatible with the project's Dart SDK constraint
- publisher (verified?), pub points, maintenance activity, open issues for blockers
- native setup required (Gradle, Podfile, Info.plist, AndroidManifest)
- whether the project already has something that does the job

Adding a package needs approval (it's a dependency change).
