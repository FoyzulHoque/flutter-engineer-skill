# Flame Games

Primary source: https://docs.flame-engine.org/latest/. Flame's API changes between minor versions, so check the docs for the version in `pubspec.lock`, and the bridge packages' pub.dev pages (`flame_audio`, `flame_forge2d`, `flame_tiled`, `flame_bloc`, `flame_riverpod`).

## Mental model
- `FlameGame` hosts a component tree and runs the game loop: `update(dt)` then `render(canvas)`, every frame.
- Everything is a `Component`: `PositionComponent`, `SpriteComponent`, `SpriteAnimationComponent`, `TextComponent`, etc. Add children with `add()`. Do async asset loading in `onLoad()`.
- The `World` + `CameraComponent` setup is the standard structure in current versions. Game objects go in the world; HUD goes on `camera.viewport`.
- Embed with `GameWidget(game: myGame, overlayBuilderMap: {...})`. Use Flutter overlays for menus, pause, and game-over screens.

## Rules of thumb
- **Scale movement by `dt`** (`position += velocity * dt`). Never assume a frame rate.
- **No allocation in `update()`** on hot paths. Reuse `Vector2`s, use `setFrom`/`setValues`, and pool frequently spawned objects.
- **Collisions:** add `HasCollisionDetection` to the game and hitboxes (`RectangleHitbox`, `CircleHitbox`) to components, then implement `CollisionCallbacks`. Prefer simple hitbox shapes.
- **Input:** `TapCallbacks`, `DragCallbacks`, `KeyboardHandler` / `HasKeyboardHandlerComponents` on the component or game. Check the docs for the current mixin names.
- **Assets:** preload via `images.loadAll` / `Flame.images` in `onLoad`. Declare them in `pubspec.yaml` under `assets/images/`. Use sprite sheets / `SpriteAnimation.fromFrameData` for animations.
- **Audio:** `flame_audio`. Preload short SFX, loop BGM with `FlameAudio.bgm`, and pause on app lifecycle changes.
- **Effects:** `MoveEffect`, `ScaleEffect`, `OpacityEffect` with `EffectController` instead of hand-rolled tweens.
- **Physics:** use `flame_forge2d` only when real rigid-body physics is needed. It changes units (meters) and the camera setup.
- **State:** keep game state in the game or world. Bridge to app state (GetX/Riverpod/Bloc) only at the overlay boundary, or via `flame_bloc` / `flame_riverpod`.
- **Pause/resume:** `pauseEngine()` / `resumeEngine()`, and hook into `AppLifecycleState`.
- **Debug:** `debugMode = true` on the game or a component draws hitboxes and positions.

## Testing
- `flame_test` with `testWithFlameGame` / `testWithGame` for component behavior. Step the game with `game.update(dt)` and assert on state.
- Golden tests are possible but brittle. Prefer logic tests.

## Performance
- Watch component counts, and remove off-screen components (`removeFromParent`).
- Use `SpriteBatch` for many identical sprites.
- Profile in profile mode (`flutter run --profile`) with DevTools, never in debug.
