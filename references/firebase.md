# Firebase with Flutter

Primary sources: https://firebase.google.com/docs/flutter/setup and https://firebase.google.com/docs/<product>. Check each `firebase_*` package's pub.dev changelog for the pinned version. FlutterFire packages are versioned together, so upgrade them as a set.

## Setup facts to verify, not assume
- `flutterfire configure` generates `lib/firebase_options.dart` and platform files (`google-services.json`, `GoogleService-Info.plist`). Firebase *client* config values ship in the app and are not secrets. Service-account JSON and admin keys **are** secrets and must never be in the app repo.
- Initialize once in `main()` with `DefaultFirebaseOptions.currentPlatform`, guarded by try/catch so a misconfiguration doesn't crash launch (see `field-patterns.md`).
- Adding a Firebase product usually means native changes (Gradle plugin for Crashlytics/Perf, iOS capabilities for push). These need approval.

## Products

**Cloud Messaging (FCM)**
- Request permission on iOS/Android 13+ (`POST_NOTIFICATIONS`). Handle denial gracefully.
- iOS needs an APNs key uploaded in the Firebase console plus Push Notifications and Background Modes capabilities. Without them `getToken()` fails or hangs, so never `await` it on the startup path.
- Handle the three states: foreground (`onMessage`, usually shown via `flutter_local_notifications`), background tap (`onMessageOpenedApp`), terminated tap (`getInitialMessage`). Park terminated taps until a navigator exists.
- The background handler must be a top-level function annotated `@pragma('vm:entry-point')`.
- Send the token to the backend after login and on `onTokenRefresh`. Remove it on logout.

**Crashlytics**
- `FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError` (or a non-fatal wrapper) and `PlatformDispatcher.instance.onError` for async errors.
- Disable collection in debug.
- Upload symbols / dSYMs for release builds, or stack traces will be unreadable. Check the Gradle and Xcode build phase setup.
- No PII in custom keys or logs.

**Performance Monitoring**
- Automatic network tracing doesn't see Dart `http`/`dio` traffic. Wrap requests in `HttpMetric` manually if API timing matters.

**Auth**
- Decide whether Firebase Auth is the identity source or the app has its own backend auth. Don't mix them without a clear token exchange.
- Phone auth needs SHA-1/SHA-256 fingerprints (Android) and APNs or reCAPTCHA fallback (iOS).

**Firestore / Realtime Database / Storage**
- Security rules are the real access control. Review `firestore.rules` / `storage.rules`, and never ship `allow read, write: if true`.
- Model reads for cost: use listeners scoped to what's on screen, pagination with `limit` + `startAfterDocument`, and avoid unbounded collection reads.
- Offline persistence is on by default on mobile. Account for pending writes in UI.

**Remote Config / App Check / Analytics**
- Remote Config: defaults in-app, a fetch interval sensible for production, and never gate app launch on a fetch.
- App Check: enable in monitor mode before enforcing. Use the debug provider for emulators.
- Analytics: event names snake_case ≤ 40 chars, no PII in parameters.

## Approval gates specific to Firebase
`firebase deploy` (rules, functions, hosting), changing security rules, enabling enforcement (App Check), deleting projects/apps, and rotating keys all need explicit approval. Show the diff first.
