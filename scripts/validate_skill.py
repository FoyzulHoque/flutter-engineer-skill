#!/usr/bin/env python3
"""Basic local checks for this Claude Skill package."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
skill = ROOT / "SKILL.md"
errors = []

if not skill.exists():
    errors.append("Missing SKILL.md")
else:
    content = skill.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.S)
    if not match:
        errors.append("SKILL.md must start with YAML frontmatter delimited by ---")
    else:
        fields = dict(
            line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
        )
        name = fields.get("name", "").strip()
        description = fields.get("description", "").strip()
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append("name must be lowercase-hyphenated, at most 64 chars")
        if not description:
            errors.append("Frontmatter is missing description")
        elif len(description) > 1024:
            errors.append(f"description is {len(description)} chars; limit is 1024")

    # Every reference file SKILL.md points at must exist, and every reference
    # file must be pointed at (otherwise Claude never reads it).
    linked = set(re.findall(r"`(references/[\w\-]+\.md)`", content))
    on_disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / "references").glob("*.md")}
    for missing in sorted(linked - on_disk):
        errors.append(f"SKILL.md links missing file: {missing}")
    for orphan in sorted(on_disk - linked):
        errors.append(f"Reference not linked from SKILL.md: {orphan}")

for relative in ("scripts/analyze_repo.py", "LESSONS.md"):
    if not (ROOT / relative).is_file():
        errors.append(f"Missing {relative}")

if errors:
    print("Skill validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Skill structure looks good.")
print("Note: this is a structural check, not an official Claude validator.")
