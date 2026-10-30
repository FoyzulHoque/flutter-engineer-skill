#!/usr/bin/env python3
"""Audit a Flutter app's translations (GetX Translations maps and ARB files).

Usage: python check_translations.py <project-root>

Read-only. Reports locale codes, key parity between locales, keys used in
code but missing from translations, unused keys, duplicate keys, hardcoded
Text('...') literals, and whether Flutter's localization delegates are wired.
"""
from collections import Counter
from pathlib import Path
import json
import re
import sys

LOCALE_BLOCK = re.compile(r"""['"]([a-z]{2,3}(?:_[A-Za-z]{2,4})?)['"]\s*:\s*\{""")
ENTRY = re.compile(r"""^\s*(['"])((?:\\.|(?!\1).)+)\1\s*:""", re.M)
TR_USE = re.compile(r"""(['"])((?:\\.|(?!\1).)+)\1\s*\.\s*tr(?:Params|Plural)?\b""")
HARDCODED = re.compile(r"""\bText\(\s*['"]([^'"$]*[A-Za-z]{3}[^'"$]*)['"]""")
# Known-bad pairs worth flagging; real ISO region codes vary, so this stays short.
BAD_LOCALES = {"ar_AR": "use 'ar' or a real region like 'ar_SA'", "en_EN": "use 'en_US'/'en_GB'",
               "zh_ZH": "use 'zh_CN'/'zh_TW'", "hi_HI": "use 'hi_IN'", "bn_BN": "use 'bn_BD'/'bn_IN'"}


def read(path):
    """Read a source file, or return '' if it can't be read (locked, permissions)."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def split_blocks(text):
    """Return {locale: body} for each top-level locale map in a Translations file."""
    blocks, starts = {}, [(m.group(1), m.end()) for m in LOCALE_BLOCK.finditer(text)]
    for name, start in starts:
        depth, i = 1, start
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        blocks[name] = text[start:i - 1]
    return blocks


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    lib = root / "lib"
    dart = [f for f in lib.rglob("*.dart")] if lib.is_dir() else []

    locales = {}  # locale -> list of keys (with duplicates)
    sources = []
    for f in dart:
        text = read(f)
        if "extends Translations" in text:
            sources.append(f.relative_to(root).as_posix())
            for loc, body in split_blocks(text).items():
                locales.setdefault(loc, []).extend(m.group(2) for m in ENTRY.finditer(body))
    for arb in root.rglob("*.arb"):
        if "build" in arb.parts or ".dart_tool" in arb.parts:
            continue
        try:
            data = json.loads(read(arb))
        except ValueError:
            print(f"- invalid JSON: {arb.relative_to(root)}")
            continue
        loc = data.get("@@locale") or arb.stem.split("_", 1)[-1]
        sources.append(arb.relative_to(root).as_posix())
        locales.setdefault(loc, []).extend(k for k in data if not k.startswith("@"))

    all_code = "\n".join(read(f) for f in dart
                         if "extends Translations" not in read(f))
    used = {m.group(2) for m in TR_USE.finditer(all_code)}
    hardcoded = Counter()
    for f in dart:
        t = read(f)
        if "extends Translations" not in t:
            n = len(HARDCODED.findall(t))
            if n:
                hardcoded[f.relative_to(root).as_posix()] = n
    pub = read((root / "pubspec.yaml")) if (root / "pubspec.yaml").is_file() else ""

    print("**Translation audit**")
    print(f"- Sources: {', '.join(sources) or 'none found'}")
    has_arb = any(s.endswith(".arb") for s in sources)
    has_getx = any(s.endswith(".dart") for s in sources)
    if has_arb and has_getx:
        print("- BOTH ARB files and a GetX Translations map exist; counts below merge them. Pick one system.")
    if has_arb and "AppLocalizations.of" not in "\n".join(read(f) for f in dart):
        print("- ARB files present but AppLocalizations.of is never called: the ARB files are unused")
    if not locales:
        print("- No translations found.")
    for loc, keys in sorted(locales.items()):
        dup = [k for k, n in Counter(keys).items() if n > 1]
        note = f"; INVALID CODE: {BAD_LOCALES[loc]}" if loc in BAD_LOCALES else ""
        print(f"- {loc}: {len(set(keys))} keys{f', {len(dup)} duplicated (e.g. {dup[:3]})' if dup else ''}{note}")

    if len(locales) > 1:
        union = set().union(*map(set, locales.values()))
        for loc, keys in sorted(locales.items()):
            missing = sorted(union - set(keys))
            if missing:
                print(f"  - {loc} missing {len(missing)}: {missing[:6]}{' ...' if len(missing) > 6 else ''}")
    defined = set().union(*map(set, locales.values())) if locales else set()
    if locales:
        undefined = sorted(used - defined)
        unused = sorted(defined - used)
        print(f"- .tr lookups in code: {len(used)} distinct keys")
        if undefined:
            print(f"- Used but not defined (raw key shows): {len(undefined)}: {undefined[:8]}")
        if unused:
            print(f"- Defined but never used: {len(unused)} (e.g. {unused[:6]})")
        near = Counter(k.lower() for k in defined)
        clashes = [k for k, n in near.items() if n > 1]
        if clashes:
            print(f"- Keys differing only by case: {clashes[:6]}")
    print(f"- flutter_localizations in pubspec: {'yes' if 'flutter_localizations' in pub else 'NO (Material widgets and RTL will not localize)'}")
    print(f"- localizationsDelegates set: {'yes' if 'localizationsDelegates' in all_code else 'no'}; "
          f"supportedLocales set: {'yes' if 'supportedLocales' in all_code else 'NO (defaults to en_US only: no RTL, other locales ignored by Material)'}")
    total = sum(hardcoded.values())
    print(f"- Hardcoded Text('...') literals: {total} in {len(hardcoded)} files" + (f"; worst: {hardcoded.most_common(3)}" if total else ""))
    offered = set(re.findall(r"Locale\(\s*'([a-z]{2,3})'", all_code))
    missing_langs = sorted(l for l in offered if not any(k.split("_")[0] == l for k in locales))
    if missing_langs:
        print(f"- Locales the app can switch to but has no translations for: {missing_langs}")


if __name__ == "__main__":
    main()
