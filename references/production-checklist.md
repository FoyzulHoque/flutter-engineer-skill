# Flutter Production Readiness Checklist

## Reliability
- [ ] Loading, empty, success, offline, timeout, and server-error states are handled.
- [ ] Async operations avoid stale results and duplicate submissions where relevant.
- [ ] Resources, controllers, subscriptions, and streams are disposed.
- [ ] Critical business logic has automated tests.
- [ ] Static analysis and tests have been run, or unrun checks are clearly disclosed.

## Security and privacy
- [ ] No secrets or credentials are committed.
- [ ] Tokens and sensitive data are not logged.
- [ ] Authentication and authorization are enforced by the backend, not only hidden in UI.
- [ ] Local storage is appropriate for the sensitivity of its contents.
- [ ] Input is validated on client and server.
- [ ] TLS and platform network settings are configured appropriately.
- [ ] Deep links and external intents are validated.

## UX and accessibility
- [ ] Layout works on supported screen sizes and orientations.
- [ ] Text scaling, keyboard, safe areas, and system insets are handled.
- [ ] Tap targets, semantics, contrast, and focus behavior are considered.
- [ ] Error messages are understandable and actionable.
- [ ] Destructive actions have confirmation or recovery where appropriate.

## Performance
- [ ] No network calls or expensive side effects run inside `build()`.
- [ ] Lists are lazily built and paginated when appropriate.
- [ ] Images are sized/cached appropriately.
- [ ] Unnecessary rebuilds and synchronous heavy work are avoided.
- [ ] Memory and resource lifecycle has been considered.

## Release
- [ ] Bundle identifier/package name, version, and build number are correct.
- [ ] Signing, permissions, entitlements, icons, and launch assets are correct.
- [ ] Environment configuration points to the intended backend.
- [ ] Release-mode build is verified for each intended platform where feasible.
- [ ] Crash reporting, monitoring, rollout, and rollback plans are considered.
- [ ] Store privacy declarations and permission explanations match actual behavior.

A checklist is not proof of compliance. Mark an item complete only after evidence or an explicit review supports it.
