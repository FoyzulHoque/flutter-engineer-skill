# State Management Beyond GetX (Riverpod, Bloc, Provider)

Rule one still applies: **follow the project's existing choice.** Never migrate or mix in a second library without approval. Sources: https://riverpod.dev, https://bloclibrary.dev, https://pub.dev/packages/provider, and https://docs.flutter.dev/data-and-backend/state-mgmt.

## Detect what's really used (not just what's in pubspec)

Count usage, because pubspec lies. One real app declared `get`, `flutter_riverpod`, `riverpod_generator`, `go_router` and `freezed`. In use:
- Riverpod for state (53 `NotifierProvider`, 15 `@riverpod`, 7 legacy `StateNotifierProvider`)
- **GetX for navigation** (76 `Get.to`, 0 `context.go`)
- `go_router` declared and never imported

Report the real split in the Project profile, and write new code in the dominant pattern for each concern.

## Riverpod (2.x/3.x)

**Prefer:** `@riverpod` code generation (`riverpod_generator`) with `Notifier`/`AsyncNotifier`, and `ref.watch` in `build`, `ref.read` in callbacks, `ref.listen` for side effects (snackbars, navigation). Check the pinned major version, because Riverpod 3 moved `StateNotifier`/`StateProvider`/`ChangeNotifierProvider` to `package:flutter_riverpod/legacy.dart`.

Use `AsyncNotifier` + `AsyncValue` for anything loaded, and render with `.when`:
```dart
@riverpod
class BookDetails extends _$BookDetails {
  @override
  Future<BookDetailsState> build(String bookId) =>
      ref.watch(bookRepositoryProvider).fetchDetails(bookId);

  Future<void> refresh() async {
    state = const AsyncLoading<BookDetailsState>().copyWithPrevious(state);
    state = await AsyncValue.guard(() => ref.read(bookRepositoryProvider).fetchDetails(arg));
  }
}

// widget
final details = ref.watch(bookDetailsProvider(bookId));
return details.when(
  data: (d) => BookDetailsView(d),
  loading: () => const BookDetailsSkeleton(),
  error: (e, _) => ErrorRetry(onRetry: () => ref.invalidate(bookDetailsProvider(bookId))),
);
```

**Anti-patterns found in a real Riverpod app:**
| Found | Why it's wrong | Fix |
|---|---|---|
| 0 uses of `AsyncValue`/`.when`; loading shown via `EasyLoading` from inside notifiers | Throws away Riverpod's loading/error/data model, and UI state lives in a global overlay | `AsyncNotifier` + `.when` |
| `TextEditingController`s stored inside the immutable state class (`state.email.text`) | Controllers are never disposed, and `copyWith` copies a mutable object | Controllers live in the widget (`ConsumerStatefulWidget` or `flutter_hooks`), and the state holds values |
| GetX `Rxn<CountryCode>` fields inside a `StateNotifier` | Two reactive systems. Riverpod doesn't see the change | Put it in the state, or a separate provider |
| Notifiers taking a `BuildContext` and calling `Get.to(...)` | Business logic coupled to UI and navigation, and untestable | Notifier exposes state/events; the widget navigates in `ref.listen` |
| Hardcoded sample data returned from `build()` (book names, lorem descriptions) | Ships placeholder content; there's no repository seam | `build` calls a repository provider; samples live in tests/fixtures |
| `StateNotifierProvider` mixed with `@riverpod` | Two styles, and legacy in Riverpod 3 | New code uses `@riverpod`; migrate old ones only with approval |
| Folder names with spaces (`get x dependency injection`, `financial calculators`) | Breaks tooling, imports and scripts | snake_case folders (rename only with approval) |

**Other rules:** use `autoDispose` (the default with codegen) for screen-scoped state, and `keepAlive: true` only for app-wide state. Use family args (`bookDetailsProvider(id)`) instead of passing ids through mutable fields. Use `ProviderScope(overrides: [...])` in tests. Never call `ref.read` inside `build` to "avoid rebuilds". Use `select` instead.

## Bloc / Cubit
- `Cubit` for simple state, `Bloc` when events need transforms (debounce search, `droppable` for submit).
- One sealed state class (`Initial/Loading/Success/Failure`) or one state with a status enum. Be consistent within the app.
- `BlocBuilder` for UI, `BlocListener` for side effects (navigation, snackbars), and `buildWhen`/`listenWhen` to limit rebuilds.
- Repositories injected via `RepositoryProvider`. Close streams in `close()`.
- Test with `bloc_test` (`blocTest(build:, act:, expect:)`).

## Provider (ChangeNotifier)
- Fine for small apps. Call `notifyListeners()` after state changes, never during build.
- `context.watch` in build, `context.read` in callbacks, `Selector` to limit rebuilds.
- Dispose controllers in the `ChangeNotifier.dispose`.

## Mixing libraries (common in agency apps)
If a project already mixes (e.g. Riverpod state + GetX navigation):
- don't add a third
- don't "fix" it as a side effect of another task
- write new code in the dominant pattern per concern, and note the split in `PROJECT_NOTES.md`
- propose a consolidation plan as a separate, approved task (e.g. GetX navigation → go_router, which is already declared)
