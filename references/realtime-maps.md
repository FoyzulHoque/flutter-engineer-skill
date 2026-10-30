# Real-time: Sockets, WebRTC, Agora, Live Tracking and Maps

Learned from five production apps: 1:1 WebRTC video calls, Agora live shopping, two courier/ride trackers, and a property-measuring map. Sources: https://webrtc.org, `flutter_webrtc` / `agora_rtc_engine` / `geolocator` / `google_maps_flutter` on pub.dev, https://docs.agora.io, https://developers.google.com/maps/documentation.

Every real-time feature shares one rule: **one long-lived service owns each connection, and every subscription, timer, stream and native resource it creates is cancelled or released in exactly one teardown path.** Most bugs found were leaks, plus duplicate connections when that rule was broken.

## 1. WebSocket service (signaling, chat, live events, location)

Found: the same socket URL opened by 4 controllers. `listen()` subscriptions never stored or cancelled. "Connected" set before the socket was ready. No heartbeat, no backoff. Reconnect attempted from inside a GPS callback on every tick. Auth token printed to the console.

Do:
- **One `GetxService` (`permanent`) per backend socket**, exposing a broadcast `Stream<Map>` of decoded events plus `send(event, data)`. Features subscribe and filter by `event`.
- Connect, then `await channel.ready`, then send `authenticate`, then mark connected only on the server's `authenticated` reply.
- **Store every `StreamSubscription`** and cancel it in `onClose`. Close the sink with a reason.
- Handle `onError`/`onDone` → reconnect with **exponential backoff + jitter** (1s, 2s, 4s… cap 30s), and re-authenticate and re-join rooms after reconnecting.
- **Heartbeat** (ping every 20–30s). Treat a missing pong as disconnected.
- **Queue outgoing messages** while offline if they matter (chat). Drop stale ones (location).
- Use `wss://` only, never a raw-IP `ws://`. Never log tokens or full payloads.
- Model connection state as an enum (`connecting/connected/reconnecting/offline`) and show it in the UI.

## 2. WebRTC calls (`flutter_webrtc`)

Found in a 1:1 call implementation: STUN only (no TURN). `Disconnected` treated as fatal. ICE candidates arriving before the remote description silently dropped. The local stream was stopped but never disposed. Renderers were disposed *before* the code that sets their `srcObject`. A second call could create a second peer connection. A debug auto-accept was shipped. Full SDP was logged.

Do:
- **TURN is mandatory for mobile.** STUN alone fails behind carrier/symmetric NAT. Fetch short-lived TURN credentials from your backend (coturn, Twilio, Cloudflare, Xirsys). Never hardcode them.
- Config: `sdpSemantics: 'unified-plan'`, `bundlePolicy: 'max-bundle'`, `rtcpMuxPolicy: 'require'`. Audio constraints: `echoCancellation`, `noiseSuppression`, `autoGainControl`. Mobile video: 640×480–1280×720 at 24–30fps.
- **Queue early ICE candidates** until `setRemoteDescription` completes, then flush. Never `catch (_) {}` them away.
- **`Disconnected` is transient.** Start a grace timer (~5–10s) and call `restartIce()`. Only `Failed` (or the timer expiring) ends the call.
- Guard re-entry: if `_pc != null`, tear it down first, or refuse.
- **Teardown order:** null the handlers (`onIceCandidate`, `onTrack`) → close the peer connection → stop tracks → `localStream.dispose()` → set renderer `srcObject = null` → `renderer.dispose()` → cancel the socket subscription. Do it in one `endCall()` used by hang-up, remote hang-up, failure and `onClose`.
- `await renderer.initialize()` before first use.
- Ringing: a timeout (~30s) that captures the call id it was started for, so it can't end a different call.
- For calls while the app is backgrounded or locked, use CallKit (iOS) / ConnectionService (Android) via `flutter_callkit_incoming` + VoIP push. A plain push notification isn't enough.
- **1:1 only.** Mesh WebRTC breaks past ~3–4 participants. For one-to-many or group calls, use an SFU (LiveKit, mediasoup, Janus) or a hosted SDK (Agora, Zego, Stream Video).

## 3. Agora live streaming (`agora_rtc_engine`)

Found in a live-shopping app: App ID hardcoded and **`token: ''`**, so the project runs in testing mode and anyone with the App ID can join any channel. The engine was re-created on each init without releasing the old one. The screen never left the channel. Joins were timed with fixed `Future.delayed` retries. A single `remoteUid` was overwritten by any second user. Errors were only logged.

Do:
- **Tokens from your backend**: `POST /agora/token {channel, role}` → RTC token (role-scoped, ~1h). Enable the App Certificate in the Agora console. Handle `onTokenPrivilegeWillExpire` → fetch → `renewToken`, and `onRequestToken` → rejoin. The App Certificate never ships in the app.
- Profile `channelProfileLiveBroadcasting`. Host = `clientRoleBroadcaster` with `enableVideo` + `startPreview`. Viewers = `clientRoleAudience` (cheaper and lower latency, `audienceLatencyLevelLowLatency`).
- Encoder for mobile hosts: around 960×540 / 15fps / adaptive orientation (what the app used, and a good default).
- **One engine, created once, guarded.** `initialize` is idempotent, and `dispose` does `await leaveChannel()` then `await release()`. Call it from the screen's dispose *and* the controller's `onClose`, guarded so it runs once.
- Track remote users in a `Set<int>`, not one `remoteUid`. Show the host by a known uid (the host joins with a fixed uid from the backend).
- Surface `onConnectionStateChanged` (reconnecting/failed) and `onNetworkQuality` in the UI.
- Live-shopping layer (chat, product pins, viewer count, countdowns) over your own socket service (§1), or Agora RTM/Signaling. Keep it separate from the media channel, and await connection instead of sleeping.
- Android manifest: `CAMERA`, `RECORD_AUDIO`, `INTERNET`, `MODIFY_AUDIO_SETTINGS`, `BLUETOOTH_CONNECT`. Request them at runtime, and **check the result** before `startPreview`.

## 4. Live location tracking

Found across trackers: `getPositionStream()` with `distanceFilter: 0`, plus a 5s timer, plus a **reverse-geocode HTTP call on every GPS tick**. No Android foreground service, so tracking dies when the app is backgrounded. No handling of GPS being switched off. Subscriptions never cancelled. A one-shot `Timer` used where `Timer.periodic` was meant. Permission flow copy-pasted into 8 screens, with `deniedForever` silently ignored.

Do:
- **One `LocationService` (GetxService)**:
```dart
final settings = Platform.isAndroid
    ? AndroidSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 15,
        intervalDuration: const Duration(seconds: 4),
        foregroundNotificationConfig: const ForegroundNotificationConfig(
          notificationTitle: 'Sharing your location',
          notificationText: 'While your delivery is active',
          enableWakeLock: true,
        ),
      )
    : AppleSettings(
        accuracy: LocationAccuracy.bestForNavigation,
        distanceFilter: 15,
        activityType: ActivityType.automotiveNavigation,
        allowBackgroundLocationUpdates: true,
        showBackgroundLocationIndicator: true,
        pauseLocationUpdatesAutomatically: true,
      );
_sub = Geolocator.getPositionStream(locationSettings: settings).listen(_onFix);
_gpsSub = Geolocator.getServiceStatusStream().listen(_onGpsToggled);
```
- Permission flow in one method: service enabled? → `openLocationSettings`. Check/request permission. `deniedForever` → explain + `openAppSettings`. Ask for **"always" only when a trip starts**, with an in-app explanation first (Play requires a prominent disclosure for background location).
- Manifest: `ACCESS_FINE_LOCATION`, `ACCESS_BACKGROUND_LOCATION` (only if needed, which needs a Play declaration), `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_LOCATION`. Info.plist: WhenInUse + Always usage strings, `UIBackgroundModes: location`.
- **Send throttled** (every 3–5s *or* 15–25m, whichever comes first) with `{tripId, lat, lng, heading, speed, accuracy, ts}`. **No geocoding on the client per tick.** The server or the viewer resolves addresses when needed.
- Drop fixes with poor `accuracy` (> 50m) or impossible jumps.
- Start tracking when a trip/job starts and stop when it ends. Never run it all the time.

## 5. Maps (`google_maps_flutter`)

Found: `setState` + `markers.add(...)` per update, rebuilding the whole map. Markers jumping instead of moving. Directions REST API called from the app with the key in Dart, and no re-route. Maps keys hardcoded in Dart and manifests. 5,900 lines of near-duplicate map screens (`dumb_map.dart`, `tryhard_map.dart`, commented-out copies).

Do:
- Keep the `GoogleMap` widget stable. Only `markers`/`polylines` change, from an `RxMap<MarkerId, Marker>` inside a small `Obx`. **Replace markers by id**, never append.
- **Animate moving markers**: tween lat/lng over the send interval, and set `rotation: heading` with `anchor: Offset(0.5, 0.5)` and `flat: true` for vehicles.
- Load custom icons once (`BitmapDescriptor.bytes` / resized asset bytes, or a widget rendered to bytes for price pins) and cache them.
- Camera: follow mode toggled by the user. Stop following when they pan. `LatLngBounds` to fit driver + destination.
- **Routes and ETA from your backend** (Routes API proxy): the key stays server-side, and you re-route only when off-route by > 50m. Decode polylines with `flutter_polyline_points`.
- Keys: Android/iOS Maps SDK keys restricted to package name/bundle id + SHA-1 in Google Cloud. Inject the Android key through `manifestPlaceholders` from `local.properties`/CI, not committed. Web-service keys (Directions, Geocoding, Places) never go in the app.
- Respect usage policies: public Nominatim forbids heavy app use and needs a real `User-Agent`. Use Google Geocoding via your backend, or a paid provider.
- Dark/brand map style via `style:` JSON matching the app's design tokens (see `design.md`).

### Drawing and measuring areas (lawn/roof/property)
Good UX found: tap to drop vertices, a polygon preview, undo last point, a satellite toggle, search address, then save perimeter + area.

**Area bug found and verified:** the shoelace formula on raw degrees × 111,139² ignores that a degree of longitude shrinks with latitude. At 40° latitude it overstated a lawn by **30%** (33,239 vs 25,488 sq ft). If price depends on area, customers are overcharged. Use a geodesic area:
```dart
/// Spherical polygon area in m² (accurate to well under 1% for property-sized shapes).
double polygonAreaM2(List<LatLng> pts) {
  if (pts.length < 3) return 0;
  const r = 6371008.8;
  double rad(double d) => d * pi / 180;
  var sum = 0.0;
  for (var i = 0; i < pts.length; i++) {
    final a = pts[i], b = pts[(i + 1) % pts.length];
    sum += rad(b.longitude - a.longitude) * (2 + sin(rad(a.latitude)) + sin(rad(b.latitude)));
  }
  return (sum * r * r / 2).abs();
}
```
(Or `maps_toolkit`'s `SphericalUtil.computeArea`.) Don't append the first point to "close" the polygon *and* add a closing term. Pick one. Unit-test with a known shape at two latitudes.

## Checklist for any real-time feature
- [ ] One owner per connection, and teardown releases everything (subscriptions, timers, sockets, engines, renderers, streams)
- [ ] Reconnect with backoff, heartbeat, and visible connection state
- [ ] Tokens/credentials from the backend, short-lived, never hardcoded or logged
- [ ] Background behavior decided and configured (foreground service, background modes, CallKit)
- [ ] Throttled sends, with no per-tick network side effects
- [ ] Permissions requested in context, with `deniedForever` handled, and manifest/plist matching
- [ ] Tested on a real device with network loss (airplane mode on/off), backgrounding, and screen lock
