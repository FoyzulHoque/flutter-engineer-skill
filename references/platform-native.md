# Native Platform Integration (Android & iOS)

Primary sources: https://docs.flutter.dev/platform-integration/platform-channels, https://docs.flutter.dev/platform-integration/android, https://docs.flutter.dev/platform-integration/ios, https://developer.android.com/guide, https://developer.apple.com/documentation/. Native config changes (manifest, plist, Gradle, Podfile, entitlements, AppDelegate/MainActivity) are approval-gated. Show the diff first.

## When to go native

Check pub.dev first. A maintained plugin usually beats hand-written channel code. Write native code when:
- a platform API has no good plugin (vendor SDKs, OEM features, special hardware)
- heavy work is faster in native libraries: image/video processing, crypto, ML on-device, audio DSP
- you need a native UI view (`PlatformView`) such as maps or vendor widgets

Know what channels *don't* do: a method channel call is async message passing with serialization cost on every call. Native performance comes from **doing the heavy work on the native side in one call** and returning a small result, not from calling native code in a tight loop.

## Choosing the mechanism

| Mechanism | Use for | Notes |
|---|---|---|
| `MethodChannel` | Request/response calls (`getBatteryLevel`, `startScan`) | Simplest; untyped `Map`/`List`/primitives |
| `EventChannel` | Native → Dart streams (sensors, location, download progress) | Dart listens to a `Stream` |
| `BasicMessageChannel` | Custom codec, high-frequency messages | Rarely needed |
| **Pigeon** (`pigeon` package) | Any non-trivial channel API | Generates **type-safe** Dart/Kotlin/Swift code. The recommended default for new channels. |
| `dart:ffi` + `ffigen` | Calling C/C++/Rust libraries **synchronously** with no serialization | The fastest route for compute-heavy code. Works on mobile and desktop. |
| `jnigen` / `swiftgen`/ObjC interop | Calling Java/Kotlin or ObjC/Swift APIs directly from Dart | Newer and evolving. Check the current status on docs.flutter.dev |
| `PlatformView` (`AndroidView` / `UiKitView`) | Embedding native UI | Has a composition cost. Hybrid composition vs texture layer trade-offs |
| `Isolate.run` / `compute` | Heavy *Dart* work (JSON parsing, image decode) | Often enough without going native at all |

Performance rules:
- Batch: one call with a list, rather than 1,000 calls.
- Large binary data: pass a `Uint8List` (it maps to `byte[]` / `FlutterStandardTypedData`), not base64 strings.
- Don't block the platform main thread. Run heavy native work on a background thread/queue, then reply. Use Kotlin coroutines (`Dispatchers.Default`) or `DispatchQueue.global()`, and deliver the result back on the main thread.
- Channel handlers run on the platform main thread by default. Use `TaskQueue` (`makeBackgroundTaskQueue`) for background handling when supported.
- Measure in **profile mode** with DevTools before and after. Don't assume native will be faster.

## MethodChannel example

**Dart**
```dart
class BatteryApi {
  static const _channel = MethodChannel('com.example.app/battery');

  static Future<int?> level() async {
    try {
      return await _channel.invokeMethod<int>('getBatteryLevel');
    } on PlatformException catch (e) {
      debugPrint('battery failed: ${e.code} ${e.message}');
      return null;
    } on MissingPluginException {
      return null; // platform without an implementation (e.g. web)
    }
  }
}
```

**Android: `android/app/src/main/kotlin/.../MainActivity.kt`**
```kotlin
class MainActivity : FlutterActivity() {
    private val channel = "com.example.app/battery"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channel)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "getBatteryLevel" -> {
                        val bm = getSystemService(BATTERY_SERVICE) as BatteryManager
                        result.success(bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY))
                    }
                    else -> result.notImplemented()
                }
            }
    }
}
```

**iOS: `ios/Runner/AppDelegate.swift`**
```swift
@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    let controller = window?.rootViewController as! FlutterViewController
    let channel = FlutterMethodChannel(name: "com.example.app/battery",
                                       binaryMessenger: controller.binaryMessenger)
    channel.setMethodCallHandler { call, result in
      guard call.method == "getBatteryLevel" else { return result(FlutterMethodNotImplemented) }
      UIDevice.current.isBatteryMonitoringEnabled = true
      let level = UIDevice.current.batteryLevel
      level < 0 ? result(FlutterError(code: "UNAVAILABLE", message: "No battery info", details: nil))
                : result(Int(level * 100))
    }
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```
Newer Flutter templates may use an implicit engine / `SceneDelegate` setup. Read the project's actual `AppDelegate.swift` and match its structure, and check docs.flutter.dev for the pinned Flutter version. For anything bigger than a couple of methods, put the code in a **local plugin** (`flutter create --template=plugin`) or use Pigeon, rather than growing `MainActivity`/`AppDelegate`.

Rules: always call `result` exactly once, return `notImplemented()` for unknown methods, use stable channel names prefixed with the app id, and map native errors to `PlatformException` codes the Dart side handles.

## Android project map

| File | What lives there |
|---|---|
| `android/app/src/main/AndroidManifest.xml` | Permissions, `<application>` attrs, activities, intent filters (deep links), services, receivers, `<queries>` for package visibility, FileProvider, meta-data (e.g. Maps API key placeholder) |
| `android/app/build.gradle(.kts)` | `namespace`, `applicationId`, `minSdk`/`targetSdk`/`compileSdk`, flavors, signing configs, R8/ProGuard, `manifestPlaceholders` |
| `android/settings.gradle(.kts)` / `android/build.gradle(.kts)` | Plugin versions (AGP, Kotlin, google-services, crashlytics) |
| `android/gradle.properties` | JVM args, AndroidX flags |
| `android/app/src/main/res/` | Icons, launch theme, `network_security_config.xml`, `values/strings.xml` |
| `android/app/proguard-rules.pro` | Keep rules for reflection-based SDKs (release-only crashes) |
| `MainActivity.kt` | `FlutterActivity` / `FlutterFragmentActivity` (required by e.g. `local_auth` and some payment SDKs), method channels |

Permissions:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/> <!-- Android 13+ runtime -->
<uses-feature android:name="android.hardware.camera" android:required="false"/>
```
- Declaring in the manifest is not enough for *dangerous* permissions: request them at runtime (`permission_handler`, or the plugin's own API), handle denied/permanently-denied, and link to settings.
- Only declare what you use. Every sensitive permission (location in background, SMS, call log, all-files access, exact alarms) needs a Play Console declaration and a justification.
- Storage: scoped storage since Android 10, and granular media permissions (`READ_MEDIA_IMAGES`) since 13, plus the photo picker. Prefer the picker over broad permissions.
- Check the current `targetSdk` requirement and its behavior changes on developer.android.com before raising it.

## iOS project map

| File | What lives there |
|---|---|
| `ios/Runner/Info.plist` | Usage-description strings, URL schemes, `LSApplicationQueriesSchemes`, background modes, ATS exceptions, display name |
| `ios/Runner/AppDelegate.swift` | App lifecycle, push registration hooks, method channels |
| `ios/Runner/Runner.entitlements` | Push (`aps-environment`), Associated Domains (universal links), Apple Pay merchant ids, Sign in with Apple, App Groups |
| `ios/Podfile` | `platform :ios, 'X.0'`, `post_install` build settings (e.g. permission_handler macros) |
| `ios/Runner.xcodeproj` | Bundle id, team, signing, capabilities. Prefer changing these in Xcode |
| `ios/Runner/PrivacyInfo.xcprivacy` | Privacy manifest (required-reason APIs, tracking domains) |

Permission strings (missing ones **crash** the app when the API is touched, or get it rejected):
```xml
<key>NSCameraUsageDescription</key>
<string>Scan QR codes at the counter.</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>Show stores near you.</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Choose a profile photo.</string>
<key>NSMicrophoneUsageDescription</key>
<string>Talk to the voice assistant.</string>
```
- Write specific, honest purpose strings. Vague ones ("needs access") get rejected.
- `permission_handler` on iOS needs the matching `PERMISSION_*=1` macros in the Podfile `post_install`. Check its README for the pinned version.
- Push needs the capability + APNs key in Firebase/your provider + `UIBackgroundModes: remote-notification` if handling silent pushes.
- Universal links: Associated Domains entitlement + `apple-app-site-association` on the server. Android App Links: an `autoVerify` intent filter + `assetlinks.json`.

## Verification
- Android config: `flutter build apk --debug`, then run on a device with the permission flow exercised (grant, deny, deny forever).
- iOS config (macOS only): `flutter build ios --no-codesign`, then run on a device/simulator and hit every API that needs a usage string.
- Release mode on both platforms. R8 and missing keep rules only break in release.
