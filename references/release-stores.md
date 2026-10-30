# Release: Google Play and the App Store

Primary sources: https://docs.flutter.dev/deployment/android, https://docs.flutter.dev/deployment/ios, https://developer.android.com/distribute/console, https://developer.apple.com/documentation/ and the App Store Review Guidelines. Store requirements change every year (target SDK, privacy manifests, account-deletion rules), so **check current requirements on these pages before a release.** Don't rely on memory.

**Everything that uploads, submits, promotes a track, or changes signing is an approval gate.** Prepare the build and a checklist; let the user press the button unless they explicitly ask you to.

## Versioning
- `pubspec.yaml` `version: 1.4.2+37` → versionName/CFBundleShortVersionString `1.4.2`, versionCode/CFBundleVersion `37`.
- The build number must increase for every upload to either store. Never reuse one.
- If the app has an in-app update gate, confirm the backend's "latest build" is updated *after* the store build is live, not before.

## Android / Play Console
- Build: `flutter build appbundle --release` (AAB is required for Play). Add `--obfuscate --split-debug-info=build/symbols` if the project uses obfuscation, and keep the symbols.
- Signing: `key.properties` + upload keystore, referenced from Gradle. **Never** commit the keystore or passwords. Play App Signing holds the app signing key.
- Check `applicationId`, `minSdk`, and `targetSdk` against Play's current target-API requirement. Check permissions in `AndroidManifest.xml`, since each sensitive permission needs a Play declaration.
- Play Console items: Data safety form matching actual data collection, content rating, target audience, ads declaration, app access (test login for reviewers), and the account-deletion URL if accounts exist.
- Tracks: internal → closed → open → production, with staged rollout percentages. New personal developer accounts may have mandatory closed-testing requirements, so check the console.
- Upload mapping/symbol files for readable crash reports.

## iOS / App Store Connect
- Build: `flutter build ipa --release` (needs macOS + Xcode), or archive in Xcode. Bundle id, team, and provisioning must match App Store Connect.
- `Info.plist`: a usage description for every permission the app (or any plugin) touches: camera, photos, location, microphone, contacts, tracking. Missing strings cause rejection or crashes.
- Privacy: privacy manifest requirements for the app and SDKs, App Privacy "nutrition label" answers, and the App Tracking Transparency prompt if tracking.
- Capabilities and entitlements: push, Sign in with Apple (required if other third-party social logins are offered), associated domains, background modes.
- Review: provide a demo account, notes for reviewers, and in-app account deletion if sign-up exists. Payments for digital goods must use IAP. Physical goods and services (e.g. food orders) may use external payment.
- TestFlight for internal and external testing before submission.

## Pre-release checklist
- [ ] Release build runs on a real device per platform. Release-mode-only bugs are common: tree-shaking, obfuscation, missing ProGuard/R8 rules.
- [ ] Production base URL / environment via `--dart-define` or flavor, verified in the built app.
- [ ] Crash reporting active in release, with symbols uploaded.
- [ ] Version and build number bumped.
- [ ] Store listing, screenshots, privacy forms and policy URLs current.
- [ ] Rollback plan: staged rollout percentage, ability to halt, server-side feature flags.
- See also `production-checklist.md`.
