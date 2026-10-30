# Flutter Architecture and Project Patterns

## Default feature-first example

```text
lib/
  app/
    app.dart
    routes/
    bindings/
  core/
    config/
    errors/
    network/
    theme/
    utils/
    widgets/
  features/
    profile/
      data/
        datasources/
        models/
        repositories/
      domain/              # include when domain rules/contracts justify it
        entities/
        repositories/
        usecases/
      presentation/
        controllers/
        pages/
        widgets/
test/
  features/
```

This is a reference, not a mandatory rewrite target. Adapt it to the existing project and its scale.

## Dependency direction

Presentation depends on domain abstractions and UI-facing state. Data implements repository contracts. Domain should not import Flutter UI, GetX, HTTP clients, or persistence packages when a clean domain boundary is being used.

For a smaller feature, a page/controller/service/repository split may be sufficient. Add use cases when they represent meaningful business actions or improve testing—not merely to add files.

## GetX responsibilities

- Page/widget: render state and forward user events.
- `GetxController`: presentation state, orchestration, validation, and UI actions.
- Repository: application-facing data contract.
- Data source/API client: HTTP and serialization.
- Model/DTO: parse external payloads and map to internal types where useful.
- Binding/composition root: register dependencies with deliberate lifetimes.

Example shape:

```dart
abstract interface class ProfileRepository {
  Future<Profile> fetchProfile();
}

class ProfileController extends GetxController {
  ProfileController(this._repository);

  final ProfileRepository _repository;
  final isLoading = false.obs;
  final profile = Rxn<Profile>();
  final errorMessage = RxnString();

  Future<void> loadProfile() async {
    isLoading.value = true;
    errorMessage.value = null;

    try {
      profile.value = await _repository.fetchProfile();
    } catch (error, stackTrace) {
      // Send safe diagnostic details to the project's logger.
      errorMessage.value = 'Unable to load profile. Please try again.';
    } finally {
      isLoading.value = false;
    }
  }
}
```

Adapt error types, logging, and UI state to the real application. Avoid showing raw exceptions to users. Use `Obx` only around widgets that read the relevant observables.

## API layering

```text
Page -> Controller/ViewModel -> Repository -> RemoteDataSource -> HTTP client
                                      \-> LocalDataSource (if needed)
```

Keep request/response DTOs aligned with the API contract. Convert transport errors to app-level failures at a consistent boundary. Do not leak raw `DioException`, `http.Response`, or JSON maps throughout the UI.

## Error states

At minimum, distinguish:
- loading
- success with data
- successful empty result
- recoverable network/server failure
- authentication/authorization failure when relevant
- invalid or unexpected response

Avoid using an empty list to represent every possible failure; that makes errors indistinguishable from legitimate empty data.

## Navigation and dependency lifetimes

Use the project's existing routing. For GetX, keep route names centralized if the project does so, use bindings or a consistent registration location, and define whether dependencies are route-scoped or permanent. Ensure controllers and streams are disposed according to their lifecycle.
