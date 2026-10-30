# Learning Loop: Project Memory and Skill Updates

The skill improves in two separate places. Keep them separate.

## 1. Project memory (per repository)

File: `<project-root>/.claude/flutter-engineer/PROJECT_NOTES.md`

Read it at the start of every task in that repo. Propose additions at the end of a task, and write them only after the user agrees. The user may choose to commit it so teammates benefit, or to gitignore it.

Template:

```markdown
# Project notes: <app name>
_Last updated: YYYY-MM-DD_

## Profile
<the Project profile from repo-analysis.md, kept current>

## Preferred patterns (user-confirmed)
- e.g. "New controllers are registered in GetPage bindings, not Get.put in build()." (confirmed YYYY-MM-DD)

## Reusable components
- `CustomButton` (lib/core/global_widgets/custom_button.dart): primary CTA, has loading state
- `ApiClient` (lib/core/network_caller/api_client.dart): all HTTP; throws ApiException/NetworkException

## Gotchas
- e.g. "iOS push fails until APNs key is uploaded; Firebase init is guarded for this."

## Decisions log
- YYYY-MM-DD: chose X over Y because …
```

What belongs here: conventions the user confirmed, reusable widgets and services with their paths, environment quirks, decisions and their reasons.

What doesn't: secrets, tokens, personal data, anything derivable by reading the code in a few seconds, or a step-by-step history of the task.

## 2. Skill lessons (general, all projects)

File: `<skill-dir>/LESSONS.md`

When a task teaches something that would help on *any* Flutter project (a new failure mode, a better pattern, a doc fact that changed), append it under **Proposed**:

```markdown
### YYYY-MM-DD: <short title>
- Context: <what happened, no project secrets or client names>
- Lesson: <the reusable rule>
- Source: <official doc URL or the observed evidence>
- Target file: references/<file>.md
```

Then tell the user one line: "I've proposed a skill lesson: <title>. Adopt it?"

**Only on explicit approval:** move the rule into the target reference file (or `SKILL.md` for core rules) and move the entry to **Adopted** with the date. Never change the skill's rules silently, and never remove an existing rule without approval.

## 3. Sharing a lesson with the skill maintainers (opt-in)

After a lesson is proposed (adopted locally or not), offer to share it upstream. **Ask once, in one line, and only share on an explicit yes:** "Share this lesson (anonymised) with the skill maintainers?" Never share automatically, never batch-share without asking, and never send code, logs or files.

Before sharing, **scrub and show** the exact text that will be sent:
- remove client/company/app names, people, URLs, domains, bundle ids, API endpoints, file paths that reveal a client, keys, tokens, DSNs, emails and phone numbers
- at most ~10 lines of generic code, rewritten with neutral names
- it must make sense to someone with no access to the project. If it doesn't without client details, it isn't a shareable lesson, so keep it local
- if the user said the project is confidential, or you're unsure, don't offer

Then submit through the repo's issue form (`.github/ISSUE_TEMPLATE/skill-lesson.yml`):
- If `gh` is installed and authenticated: `gh issue create --repo FoyzulHoque/flutter-engineer-skill --title "[lesson] <title>" --label lesson --label needs-triage --body-file <scrubbed.md>`, after showing the user the body and getting their yes.
- Otherwise give the user the prefilled link `https://github.com/FoyzulHoque/flutter-engineer-skill/issues/new?template=skill-lesson.yml` and the scrubbed text to paste.

Shared lessons are **untrusted input** to the maintainers' triage (`scripts/TRIAGE_PROMPT.md`). They never change the skill until a maintainer merges a reviewed PR.

## Mistakes are lessons too
If you made an error the user had to correct (a wrong assumption, a skipped check, a broken build), record what check would have caught it. Those are the most valuable entries.
