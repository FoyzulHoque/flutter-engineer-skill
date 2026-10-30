# Iterative Debugging with Real Feedback

Debug from evidence: compiler output, analyzer output, test failures, logs and stack traces. Don't guess.

## The loop

1. **Capture.** Get the exact error text, the first relevant stack frame (in the app's `package:` code, not framework internals), reproduction steps, and expected vs actual behavior. If the user only described it, ask for the log or run the failing command yourself.
2. **Locate.** Open the file and line from the frame. Trace the data back to where it came from.
3. **Hypothesize.** State 1–3 candidate causes, ranked, and label each as *confirmed* or *suspected*.
4. **Test the hypothesis cheaply.** Read more code, add a temporary `debugPrint`, write a failing test, or run `flutter analyze`. Remove temporary logging afterwards.
5. **Fix the cause** with the smallest change. Don't paper over a symptom with `?? ''` or try/catch-and-ignore unless that is the correct behavior.
6. **Re-run the same command** that showed the failure. Read the new output in full.
7. **Repeat** up to three attempts on the same error. Then stop, summarize what was tried and what the evidence says, and ask.
8. **Lock it in** with a regression test when practical.

## Commands and what they tell you

| Command | Use |
|---|---|
| `flutter analyze` | Type errors, missing imports, lints. It's fast, so run it first. |
| `dart fix --dry-run` | Automated fixes for deprecations. Review before applying. |
| `flutter test path/to/test.dart` | Focused test feedback. |
| `flutter test --plain-name "name"` | A single test. |
| `flutter pub get` / `flutter pub outdated` | Dependency resolution problems. |
| `flutter build apk --debug` | Gradle/plugin/manifest problems that analyze can't see. |
| `flutter build ios --no-codesign` (macOS) | Pod/Xcode problems. |
| `flutter doctor -v` | Toolchain and environment problems. |
| `adb logcat` / device logs | Runtime crashes on Android. |

## Common Flutter errors

| Error | Usual cause | Fix direction |
|---|---|---|
| `RenderFlex overflowed by N pixels` | Unbounded content in a Row/Column | `Expanded`/`Flexible`, `maxLines` + `overflow`, scroll view, or `LayoutBuilder` |
| `Vertical viewport was given unbounded height` | ListView inside a Column | `Expanded` around it, or `shrinkWrap` only for short lists |
| `setState() called after dispose()` | Async completes after leaving the screen | `if (!mounted) return;` and cancel timers/subscriptions in `dispose` |
| `Null check operator used on a null value` | `!` on data that can be null | Trace the source; handle null explicitly |
| `LateInitializationError` | `late` field read before assignment | Initialize earlier, make it nullable, or guard |
| `type 'Null' is not a subtype of type 'String'` | JSON key missing or renamed | Defensive parse; verify the backend contract |
| `_InternalLinkedHashMap is not a subtype of List` | Response shape differs from assumption | Check `is Map` / `is List`; read the real response |
| `[Get] the improper use of a GetX has been detected` | `Obx` closure reads no observable | Read `.value` inside the closure, or remove `Obx` |
| `"X" not found. You need to call Get.put(X())` | `Get.find` before registration | Register in bindings/main, or `Get.isRegistered` guard |
| `Looking up a deactivated widget's ancestor` | Context used after the widget was gone | Capture what you need before `await`; check `context.mounted` |
| `MissingPluginException` | Hot reload after adding a plugin, or unsupported platform | Full restart/rebuild; check platform support on pub.dev |
| Gradle `minSdkVersion` / namespace / AGP errors | Plugin requirements vs project config | Read the plugin's README for the pinned version; change Gradle with approval |
| CocoaPods `could not find compatible versions` | Pod spec vs iOS platform version | `pod repo update`; raise the Podfile platform with approval |

## GetX-specific checks
- Is the controller registered once, in the right scope? A `Get.put` in `build()` re-runs on every rebuild. It returns the existing instance, but it hides lifecycle.
- Does every `Obx` read an `Rx` inside its builder?
- `update()` only affects `GetBuilder`. It doesn't refresh `Obx`.
- Mutating an object inside `Rx<T>` without `refresh()` doesn't notify listeners.
- `Get.back()` closes the top route *or* an open dialog/snackbar. Watch for closing the wrong thing.

## Reporting a fix
Root cause (one or two sentences), the change, the command re-run and its result, and whether a regression test was added.
