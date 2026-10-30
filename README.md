# Flutter Engineer Skill

**A Claude Code skill that works like a senior Flutter engineer inside your real repository.**

It reads your codebase before touching it, checks official docs for the versions you actually use, asks before risky changes, and proves its work with real `flutter analyze` and `flutter test` output.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d97757)
![Flutter](https://img.shields.io/badge/Flutter-Android%20·%20iOS%20·%20Web%20·%20Desktop-02569B?logo=flutter)

---

## Why it exists

AI coding assistants write Flutter that compiles but doesn't ship: generic purple UIs, secret keys in the app, controllers that leak, translations that silently fall back to English, payment flows that store reviewers would reject.

This skill was built by reviewing **70+ production Flutter apps** (delivery, dating, live shopping, field service, finance, booking, social) and turning every recurring mistake into a check, and every good pattern into a playbook.

## What it does

Every task follows one loop:

1. **Investigate.** Profiles the repo (`scripts/analyze_repo.py`): SDKs, state management, routing, networking, Firebase, design tokens, tests, and critical risks. Then reads the official docs for your pinned versions.
2. **Recommend.** Root cause or requirements, 1–3 options with trade-offs, and a file-by-file plan in dependency order.
3. **Ask.** Stops for approval before multi-file changes, new dependencies, deletes, payments, auth, publishing or deploying.
4. **Implement and validate.** Follows your project's conventions, then iterates on real analyzer, test and build output, and reports exactly what was and wasn't verified.
5. **Learn.** Saves your preferred patterns per project, and proposes general lessons that only become rules with your approval.

## What it knows

| Area | Highlights |
|---|---|
| Architecture | GetX, Riverpod, Bloc, Provider, and mixed codebases; feature-first structure; testable pure-function extraction |
| Design | Theme-first tokens, avoiding generic "AI" UI, rebrand method, skeleton/empty/error/offline states |
| UX copy | Minimal, specific, action-led text; error and empty-state patterns |
| Localization | ARB / `gen_l10n` and GetX `.tr`, RTL, plurals, currency and date formatting |
| Payments | RevenueCat, `in_app_purchase` with receipt verification, Stripe PaymentSheet, Apple Pay, Google Pay, store policy |
| Real-time | WebSockets, WebRTC (TURN, ICE restart, teardown), Agora live streaming with tokens |
| Location and maps | Background tracking that survives Android, throttling, animated markers, geodesic area measuring |
| Offline-first | Local DB + outbox sync, conflict rules, connectivity pitfalls |
| Native | Method channels, Pigeon, FFI, AndroidManifest, Info.plist, AppDelegate, Gradle, Podfile |
| Ship | Firebase, Play Console, App Store, web on Vercel, CI, Shorebird code push |
| Games | Flame engine essentials |

It also flags what reviewers miss. In the apps reviewed, it found Stripe secret keys shipped inside the app, signing keystores committed to git, offline work lost on app restart, and an area calculation overcharging customers by 30%.

## Install

**macOS / Linux**
```bash
git clone https://github.com/FoyzulHoque/flutter-engineer-skill.git ~/.claude/skills/flutter-engineer
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/FoyzulHoque/flutter-engineer-skill.git "$env:USERPROFILE\.claude\skills\flutter-engineer"
```

Start a new Claude Code session. To update later, run `git pull` in that folder.

## Try it

Open Claude Code in any Flutter project and try:

- `Explain this repo's architecture before changing anything.`
- Paste a raw error, like `A RenderFlex overflowed by 42 pixels on the right.`
- `Add an order history screen with loading, empty, error and retry states.`
- `Audit this app for release to the Play Store and App Store.`
- `Restyle the app to match our brand website.`

## Tools included

| Script | What it does |
|---|---|
| `scripts/analyze_repo.py <project>` | Read-only project profile: stack, structure, design-system metrics, and critical security findings |
| `scripts/check_translations.py <project>` | Translation audit: key parity, missing and unused keys, hardcoded strings, RTL setup |
| `scripts/validate_skill.py` | Structural check for the skill itself |

Python 3.8+, standard library only.

## How it learns (privacy first)

1. **Locally:** lessons go to your copy's `LESSONS.md`, and are adopted only when you approve.
2. **Shared, opt-in:** Claude may ask *"Share this lesson (anonymised) with the maintainers?"* Only on your yes, and after showing you the exact text, it opens a [lesson issue](https://github.com/FoyzulHoque/flutter-engineer-skill/issues/new?template=skill-lesson.yml) with client names, URLs, keys and personal data removed. **No code, logs, files or telemetry are ever sent.**
3. **Reviewed:** lessons are verified against official docs (`scripts/TRIAGE_PROMPT.md`) and merged by a maintainer. Everyone gets them on `git pull`.

## Contributing

Lessons, corrections and new playbooks are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache 2.0](LICENSE) © 2026 Foyzul Hoque
