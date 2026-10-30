# API Integration, Debugging, and Testing Playbook

## API checklist
- Confirm method, URL, path/query parameters, request headers, body schema, auth rules, expected status codes, and response examples.
- Set connection/receive timeouts appropriate to the operation.
- Parse JSON defensively and validate required fields.
- Map HTTP and transport errors into stable application-level failures.
- Handle 204/no-content and empty bodies where the API permits them.
- Avoid leaking tokens, passwords, PII, or complete sensitive payloads into logs.
- Test success, malformed payload, timeout, offline, 401/403, 404, 422, 429, and 5xx behavior as relevant.
- For retries, use bounded retries and only retry operations that are safe to repeat; use idempotency keys for supported payment or mutation workflows.
- For file uploads, test file size/type validation, multipart field names, progress if needed, and server-side error messages.

## Debugging checklist
- Reproduce with exact steps and record expected vs actual behavior.
- Read the first relevant exception and stack frame; don't focus only on the final generic error.
- Inspect null values, type casts, JSON key names, list/object mismatches, async races, duplicate taps, stale requests, and lifecycle disposal.
- For GetX improper-use errors, check whether an `Obx`/`GetX` builder actually reads an observable within its scope and avoid wrapping unrelated widgets.
- For missing UI updates, identify the state source and verify the correct update mechanism (`.obs` + `Obx`, or `GetBuilder` + `update()`) is being used consistently.
- For Android/iOS-only failures, inspect permissions, manifest/plist entries, signing, entitlements, network policy, and plugin platform support.
- Make a focused change and add a regression test where practical.

## Test examples to consider
- Model/DTO parsing for valid, partial, null, and malformed payloads.
- Repository maps transport responses/errors into domain results correctly.
- Controller transitions loading -> success and loading -> error.
- Empty data produces a useful empty state.
- Double submit is prevented for non-repeatable operations.
- Widget displays loading, error, empty, and populated states.
- Navigation and auth/session expiration behavior.
- Critical user journeys via integration tests.

## Making untestable flows testable (pattern from production)

Most GetX apps have zero tests because the logic lives inside controllers tied to GPS, cameras, the network and `Get`. Don't wait for a full architecture: **extract each decision into a pure top-level function** in its own file next to the controller, and unit-test that.

```dart
// controller/clock_fallback.dart: no Flutter, no Get, no I/O
bool isShiftLocationMissing({dynamic data, String? message}) {
  final code = data is Map ? data['code'] : null;
  if (code == 'SHIFT_LOCATION_MISSING') return true;
  return (message ?? '').toLowerCase().contains('no location set');
}
```
- The controller calls it; the test needs no emulator, GPS fix or mock server.
- Write the test **from the bug**: a doc comment explains the dead end the user hit, then one test per rule, plus a test that the rule does **not** fire on a genuine rejection (don't mask real errors).
- **Match the API error `code` first, and fall back to message text** for older API builds that don't send codes. Test both paths and the null/non-map body.
- Good extraction targets: retry/fallback rules, "can continue" checks for multi-step forms, status → label/colour mapping, date/time formatting, price maths, permission decision trees, update/patch gate decisions.
- Every bug fix adds at least one such test, so the suite grows from real failures.

## Commands
Run only commands suitable for the current repository and environment.

```bash
dart format .
flutter analyze
flutter test
flutter test test/path/to/focused_test.dart
flutter test integration_test
```

A command may fail because of environment setup or unrelated pre-existing issues. Report the actual outcome and separate existing failures from failures introduced by a change.
