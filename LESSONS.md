# Skill Lessons

Reusable lessons captured while using this skill. See `references/learning-loop.md` for the process. Entries move from **Proposed** to **Adopted** only with the user's approval.

## Proposed

_None yet._

## Adopted

### 2026-10-30: Optional services must never block launch
- Context: production GetX app where Firebase init failed on iOS before APNs was configured.
- Lesson: wrap Firebase and other optional SDK init in try/catch, pass a `ready` flag downstream, and make reporters no-ops until ready.
- Source: observed in a shipped app; https://firebase.google.com/docs/flutter/setup
- Target file: references/field-patterns.md

### 2026-10-30: Distinguish "refresh rejected" from "refresh unreachable"
- Context: users were signed out after one dropped request during token renewal.
- Lesson: only a server rejection of the refresh token ends the session. A network failure during refresh keeps the session and surfaces a connection error.
- Source: observed in a shipped app
- Target file: references/field-patterns.md

### 2026-10-30: Update gates must fail open
- Context: in-app forced-update checks.
- Lesson: every error path resolves to "no update". A wrongly blocked user can't open the app to get the fix.
- Source: observed in a shipped app
- Target file: references/field-patterns.md
