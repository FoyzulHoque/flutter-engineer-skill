# Offline-first Data and Sync

For field apps where workers lose signal: create, edit and complete work offline, and sync when back online without losing or duplicating anything. Sources: package pages for `hive_ce`/`hive`, `drift`, `isar`, `connectivity_plus`, `internet_connection_checker_plus`, and https://firebase.google.com/docs/firestore/manage-data/enable-offline.

## What went wrong in a real field-task app (Hive + Firestore)

| Found | Effect |
|---|---|
| Offline completions kept in an **in-memory `List<String>`** | App killed while offline → completions silently lost, and the server never hears about them |
| On every server snapshot: `taskBox.clear()` then write the server list | **Wipes unsynced local edits.** A task completed offline flips back to "pending" when the stream reconnects |
| `connectivity_plus` 7.x returns `List<ConnectivityResult>`, compared with `== ConnectivityResult.none` | Always false. The "offline" branch never runs. It compiles silently (`==` takes `Object`) |
| A new Firestore `.snapshots().listen()` added on every reconnect, never cancelled | Listeners stack. Duplicate writes, memory growth |
| Listener only started if online at launch | Started offline → never gets Firestore's own cache, and shows nothing |
| Hive cache layered on top of Firestore, which already has offline persistence | Two caches that disagree. Pick one source of truth |
| IDs from `DateTime.now().millisecondsSinceEpoch` | Collisions across devices/agents |
| A stream of **all** tasks, with no agent filter | Every agent downloads everyone's work. Data exposure unless rules block it |
| Sync loop with no lock, triggered by both create and reconnect | Concurrent runs, duplicate uploads |
| The only test was the default counter smoke test | Fails, and gives zero coverage of sync |

## Decide the architecture first

| Situation | Recommended |
|---|---|
| Backend is Firestore and data is per-user documents | **Firestore alone.** Its offline persistence *is* the local DB and write queue. Writes apply locally at once and sync later. Don't add Hive on top. Just don't `await` writes in UI flows (they resolve only on server ack). Use `SetOptions(merge: true)`, `FieldValue.serverTimestamp()`, and `snapshots(includeMetadataChanges: true)` to show "pending" via `metadata.hasPendingWrites` |
| REST backend, or complex queries/relations offline | **Local DB as the source of truth + outbox**: `drift` (SQL, migrations, reactive queries) for relational data, or `hive_ce`/`isar` for simple documents. Check the package pages: original `hive` 2.x and `isar` maintenance status vary, and community forks exist |
| Read-only cache of server data | A simple cache with TTL. No outbox needed |

## The local-first + outbox pattern (REST or custom backend)

1. **UI reads only from the local DB** (reactive query/`watch`). It never waits on the network.
2. **Every write is one local transaction**: update the entity *and* append an **outbox** row `{opId (UUID), entity, entityId, op, payload, createdAt, attempts, lastError}`. Persisted, so it survives app kill.
3. A **single `SyncService` (GetxService, permanent)** drains the outbox in order:
   - one run at a time (a `_syncing` flag or `Completer`), triggered by app start, connectivity regain, app resume, a periodic timer (e.g. 5 min), and after a local write
   - send each op with **`opId` as an idempotency key**. The server must ignore duplicates. Delete the outbox row only on success
   - retry with exponential backoff, and park permanently failing ops (4xx validation) with `lastError` for the UI. Never retry them forever, never drop them silently
4. **Pull** changes since a cursor (`updatedAt > lastSync` or a server change token), and **merge per record**:
   - if the local record has pending outbox ops → keep local fields (or field-level merge). Never overwrite pending local changes
   - otherwise → take the server version
   - deletes as tombstones (`deletedAt`), never "clear the box and rewrite"
5. **Conflict policy, written down** and agreed with the user/business: last-write-wins by server `updatedAt` (simple), field-level merge, or server-authoritative status transitions (e.g. "completed" can't revert to "pending"). Status fields usually need the last.
6. **IDs**: client-generated UUID v4 (`uuid` package), so records exist before the server sees them.
7. **Filter by user/agent** on the query *and* enforce it in backend rules (Firestore security rules / API auth).

## Connectivity (don't trust it)
- `connectivity_plus` ≥ 6 returns `List<ConnectivityResult>`. Offline is `results.contains(ConnectivityResult.none)` or the list being empty/only `none`. Check the pinned version's API.
- Connectivity ≠ internet. Wi-Fi without internet, or captive portals, report as connected. Treat it only as a **trigger** to attempt sync. Success or failure of the actual request is the truth. `internet_connection_checker_plus` can confirm, but don't block writes on it.
- Store every `StreamSubscription` and cancel it in `onClose`. Start the listeners once, in the service, not per reconnect.

## UX for offline
- Show sync state per item (synced / pending / failed with retry) and globally ("3 changes waiting to sync").
- Never block a field worker's action on the network. Confirm locally ("Saved. Will sync when online.").
- Proof-of-work offline (photos, signatures, GPS): store files locally, upload via the outbox, and attach the server URL after upload. Keep captured GPS and timestamps from capture time, not upload time.
- Location-gated actions (e.g. "complete within 100m"): validate on device for UX, and re-validate on the server with the captured coordinates.

## Testing (pure functions, no device needed)
- Merge function: local pending + server newer → local kept; no pending → server wins; tombstone handling.
- Outbox: op persisted with entity update; removed only on success; retried with backoff; idempotent replay.
- Connectivity parsing for the pinned `connectivity_plus` API.
- Kill-and-restart scenario: write offline → recreate services → outbox still there → sync succeeds.
- Delete the default counter `widget_test.dart` if the app doesn't have a counter. A failing template test hides real failures.
