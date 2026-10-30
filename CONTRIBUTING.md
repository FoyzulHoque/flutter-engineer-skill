# Contributing

Thanks for helping make Flutter Engineer Skill better.

## Ways to contribute

- **Share a lesson:** something the skill got wrong, or a pattern it should know. Use the [Skill lesson form](https://github.com/FoyzulHoque/flutter-engineer-skill/issues/new?template=skill-lesson.yml).
- **Fix outdated guidance:** a package API, store rule or Flutter behavior that changed. Link the official source.
- **Add a playbook:** open an issue first to agree on scope.

## Rules for content

- **Generic only.** No client names, app names, URLs, bundle ids, keys, tokens or proprietary code.
- **Evidence over opinion.** Cite official docs, changelogs, or say "observed in a production app" and describe what happened.
- **Match the style:** short sections, tables for patterns, "Found → Effect → Fix", and small neutral code snippets.
- **Keep `SKILL.md` short.** Detail belongs in `references/`, linked from the table in `SKILL.md`.

## Before opening a PR

```bash
python scripts/validate_skill.py
```

It checks frontmatter, the description length (1024 max), and that every reference file is linked from `SKILL.md`.

## Review

Every change is reviewed by a maintainer. Issue and PR text is treated as data, not instructions.
