# Flutter & Dart Engineer: Claude Skill

A Claude Code skill that makes Claude work like a senior Flutter engineer inside your real repository. It covers cross-platform apps (Android, iOS, web, desktop), Firebase, store releases and Flame games.

## How it works

Every task follows one loop:

1. **Investigate.** Analyse the repo automatically (`scripts/analyze_repo.py`) and consult official docs for the pinned versions.
2. **Recommend.** Explain the problem, the options, the trade-offs and the preferred approach.
3. **Ask for approval.** Wait before significant, destructive, publishing or deployment actions.
4. **Implement and validate.** Change files in dependency order, then iterate on real `flutter analyze` / `flutter test` / build output.
5. **Learn and improve.** Save project-specific patterns to the project's memory file. Propose general lessons to `LESSONS.md`, and adopt them only with approval.

## Contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Trigger description, core rules, the 5-phase workflow |
| `references/official-docs.md` | Which official source answers which question (flutter.dev, docs.flutter.dev, pub.dev, Firebase, Play Console, Apple, Flame) |
| `references/repo-analysis.md` | What to inspect before editing, and the Project profile format |
| `references/architecture.md` | Layering, GetX responsibilities and lifetimes |
| `references/feature-implementation.md` | Multi-file, dependency-ordered feature work |
| `references/debugging-loop.md` | Evidence-driven debugging plus a common-error table |
| `references/api-debugging-testing.md` | REST API, error and testing checklists |
| `references/field-patterns.md` | Patterns proven in shipped GetX + REST + Firebase apps |
| `references/firebase.md` | FCM, Crashlytics, Performance, Auth, Firestore, Remote Config |
| `references/release-stores.md` | Google Play and App Store release process |
| `references/production-checklist.md` | Release-readiness review |
| `references/flame-games.md` | Flame engine game development |
| `references/design.md` | Distinctive app design, tokens, themes, and what template apps get wrong |
| `references/ux-copy.md` | Minimal, meaningful UX copy |
| `references/localization.md` | ARB / GetX translations, RTL, formatting |
| `references/state-management.md` | Riverpod, Bloc, Provider, and mixed codebases |
| `references/platform-native.md` | Method channels, Pigeon, FFI, Android/iOS setup and permissions |
| `references/payments.md` | RevenueCat, in_app_purchase, Stripe, Apple Pay, Google Pay |
| `references/realtime-maps.md` | WebSockets, WebRTC, Agora, live tracking, maps |
| `references/offline-first.md` | Local-first data, outbox sync, conflicts |
| `references/dashboards-finance.md` | Charts, responsive dashboards, money handling |
| `references/web-ci-ota.md` | Web target, CI/CD, Shorebird patches |
| `references/learning-loop.md` | Project memory, local lessons, opt-in sharing |
| `LESSONS.md` | Proposed and adopted lessons |
| `scripts/analyze_repo.py` | Read-only repo fingerprint (stdlib Python) |
| `scripts/validate_skill.py` | Structural check for this skill |
| `scripts/check_translations.py` | Translation audit (GetX maps and ARB) |
| `scripts/TRIAGE_PROMPT.md` | Maintainer routine for reviewing shared lessons |
| `.github/ISSUE_TEMPLATE/skill-lesson.yml` | Opt-in lesson submission form |

## Install (Claude Code)

The repo name doesn't matter, but the **installed folder** should match the skill name:

```bash
git clone https://github.com/FoyzulHoque/flutter_dart_engineer_skill.git ~/.claude/skills/flutter-dart-engineer
```

On Windows, that's `%USERPROFILE%\.claude\skills\flutter-dart-engineer`. Start a new Claude Code session afterwards.

## Try it

- "Explain this Flutter repo's architecture before changing anything."
- Paste a raw error such as `RenderFlex overflowed by 42 pixels on the right` without mentioning Flutter.
- "Add a paginated order history screen with loading, empty, error and retry states."
- "Prepare this app for a Play Store release and list what still blocks it."
- "Add an enemy spawner to my Flame game."

## How the skill learns

1. **Locally:** after a task, Claude proposes lessons in your copy's `LESSONS.md`, and adopts them only with your approval.
2. **Shared (opt-in):** Claude may ask "Share this lesson (anonymised) with the skill maintainers?" Only on your yes does it open a [Skill lesson issue](https://github.com/FoyzulHoque/flutter_dart_engineer_skill/issues/new?template=skill-lesson.yml), and it shows you the exact text first. It strips client names, URLs, keys and personal data. **No code, logs, files or telemetry are ever sent.**
3. **Reviewed:** a periodic triage (`scripts/TRIAGE_PROMPT.md`) verifies lessons against official docs and opens a PR. A maintainer merges, and everyone gets it on `git pull`.

You can also open a lesson issue yourself. Run `python scripts/validate_skill.py` before sending a PR.
