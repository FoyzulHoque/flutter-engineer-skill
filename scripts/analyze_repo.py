#!/usr/bin/env python3
"""Fingerprint a Flutter/Dart repository before editing it.

Usage: python analyze_repo.py <project-root>

Read-only. Prints a Markdown "Project profile" draft: toolchain, targets,
architecture signals, package usage and risks worth checking. Standard
library only, so it runs anywhere Python 3.8+ does.
"""
from collections import Counter
from pathlib import Path
import re
import sys

STATE_LIBS = {
    "get": "GetX",
    "provider": "Provider",
    "flutter_riverpod": "Riverpod",
    "hooks_riverpod": "Riverpod (hooks)",
    "riverpod": "Riverpod",
    "flutter_bloc": "Bloc",
    "bloc": "Bloc",
    "mobx": "MobX",
    "flutter_mobx": "MobX",
}
ROUTERS = {"go_router": "go_router", "auto_route": "auto_route", "beamer": "beamer"}
HTTP = {"http": "http", "dio": "dio", "chopper": "chopper", "retrofit": "retrofit", "graphql_flutter": "GraphQL"}
STORAGE = {
    "shared_preferences": "shared_preferences",
    "flutter_secure_storage": "flutter_secure_storage",
    "hive": "hive",
    "hive_flutter": "hive",
    "isar": "isar",
    "sqflite": "sqflite",
    "drift": "drift",
}
CODEGEN = {"json_serializable", "freezed", "built_value", "build_runner"}

# (regex, message) checks run per Dart file. Signals to look at, not verdicts.
RISKS = [
    (re.compile(r"Widget\s+build\([^)]*\)\s*\{[^}]*?Get\.put\(", re.S), "Get.put inside build()"),
    (re.compile(r"(setString|write)\(\s*['\"][^'\"]*(token|password|secret)", re.I), "token/secret written to plain storage"),
    (re.compile(r"\bprint\("), "print() call (use debugPrint/logger)"),
    (re.compile(r"(api[_-]?key|secret|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]", re.I), "possible hardcoded secret"),
]


def read(path):
    """Read a source file, or return '' if it can't be read (locked, permissions)."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def parse_pubspec(text):
    """Tiny YAML subset parser: top-level scalars and dependency names."""
    info = {"deps": [], "dev_deps": []}
    section = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            key, _, val = line.partition(":")
            section = key.strip()
            if val.strip():
                info[section] = val.strip().strip("'\"")
        elif indent == 2 and section in ("dependencies", "dev_dependencies", "environment"):
            key, _, val = line.strip().partition(":")
            if section == "environment":
                info[f"env_{key}"] = val.strip().strip("'\"")
            else:
                info["deps" if section == "dependencies" else "dev_deps"].append(key)
    return info


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    pubspec = root / "pubspec.yaml"
    lib = root / "lib"
    if not pubspec.is_file():
        print(f"No pubspec.yaml in {root}. Is this a Flutter/Dart project root?")
        sys.exit(1)

    p = parse_pubspec(read(pubspec))
    deps = set(p["deps"])
    app = p.get("name", "?")

    dart_files = [f for f in lib.rglob("*.dart")] if lib.is_dir() else []
    generated = re.compile(r"\.(g|freezed|gr|mocks)\.dart$")
    src = [f for f in dart_files if not generated.search(f.name)]

    imports = Counter()
    risks = Counter()
    risk_files = {}
    big_files = []
    for f in src:
        text = read(f)
        for m in re.finditer(r"^import\s+'package:([a-z0-9_]+)/", text, re.M):
            imports[m.group(1)] += 1
        lines = text.count("\n") + 1
        if lines > 600:
            big_files.append((lines, f.relative_to(root).as_posix()))
        for rx, msg in RISKS:
            # FlutterFire client config is meant to ship in the binary.
            if msg == "possible hardcoded secret" and f.name == "firebase_options.dart":
                continue
            if rx.search(text):
                risks[msg] += 1
                risk_files.setdefault(msg, []).append(f.relative_to(root).as_posix())

    top_dirs = sorted({f.relative_to(lib).parts[0] for f in src if len(f.relative_to(lib).parts) > 1})
    feature_dir = next((d for d in ("feature", "features", "modules") if (lib / d).is_dir()), None)
    features = sorted(d.name for d in (lib / feature_dir).iterdir() if d.is_dir()) if feature_dir else []
    clean = any((lib / d).is_dir() for d in ("domain", "data")) or any(
        (lib / feature_dir / f / "domain").is_dir() for f in features
    ) if feature_dir else False

    def pick(table):
        return sorted({v for k, v in table.items() if k in deps}) or ["none detected"]

    platforms = [d for d in ("android", "ios", "web", "macos", "windows", "linux") if (root / d).is_dir()]
    all_text = "\n".join(read(f) for f in src)
    uses_bindings = "extends Bindings" in all_text or "implements Bindings" in all_text
    uses_getpage = "GetPage(" in all_text
    dart_defines = sorted(set(re.findall(r"fromEnvironment\(\s*'([A-Z0-9_]+)'", all_text)))
    firebase = sorted(d for d in deps if d.startswith("firebase_") or d.startswith("cloud_"))

    tests = list((root / "test").rglob("*_test.dart")) if (root / "test").is_dir() else []
    itests = list((root / "integration_test").rglob("*.dart")) if (root / "integration_test").is_dir() else []
    lints = read((root / "analysis_options.yaml")) if (root / "analysis_options.yaml").is_file() else ""
    lint_base = re.search(r"include:\s*package:([\w_]+)", lints)

    print(f"**Project profile: {app}**")
    print(f"- SDK: dart `{p.get('env_sdk', '?')}`, flutter `{p.get('env_flutter', 'unpinned')}`; version `{p.get('version', '?')}`")
    print(f"- Targets (platform folders): {', '.join(platforms) or 'none'}")
    print(f"- Source: {len(src)} Dart files in lib/ ({len(dart_files) - len(src)} generated); top-level dirs: {', '.join(top_dirs) or '-'}")
    if feature_dir:
        print(f"- Structure: feature-first under lib/{feature_dir}/ ({len(features)} features){'; has domain/data layers' if clean else ''}")
        print(f"  - features: {', '.join(features)}")
    print(f"- State management: {', '.join(pick(STATE_LIBS))}")
    if "get" in deps:
        print(f"  - GetX: GetPage routes {'yes' if uses_getpage else 'no'}, Bindings {'yes' if uses_bindings else 'no'}")
    print(f"- Routing: {', '.join(pick(ROUTERS)) if pick(ROUTERS) != ['none detected'] else ('GetX' if uses_getpage else 'Navigator / ad hoc')}")
    print(f"- Networking: {', '.join(pick(HTTP))}")
    print(f"- Persistence: {', '.join(pick(STORAGE))}")
    print(f"- Codegen: {', '.join(sorted(CODEGEN & (deps | set(p['dev_deps'])))) or 'none'}")
    print(f"- Firebase: {', '.join(firebase) or 'none'}")
    print(f"- --dart-define keys: {', '.join(dart_defines) or 'none'}")
    print(f"- Lints: {lint_base.group(1) if lint_base else ('custom' if lints else 'no analysis_options.yaml')}")
    print(f"- Tests: {len(tests)} unit/widget test files, {len(itests)} integration files")
    workflows = sorted(p.name for p in (root / ".github" / "workflows").glob("*.y*ml")) if (root / ".github" / "workflows").is_dir() else []
    print(f"- CI workflows: {', '.join(workflows) or 'none'}")
    extras = [n for n, hit in (
        ("Shorebird OTA (shorebird.yaml)", (root / "shorebird.yaml").is_file()),
        ("Vercel web hosting (vercel.json)", (root / "vercel.json").is_file()),
        ("Firebase CLI config (firebase.json)", (root / "firebase.json").is_file()),
        ("conditional imports (dart.library.*)", "if (dart.library." in all_text),
        ("method channels", "MethodChannel(" in all_text),
    ) if hit]
    print(f"- Other: {', '.join(extras) or 'none'}")
    raw_colors = len(re.findall(r"\bColor\(0x", all_text))
    text_styles = len(re.findall(r"\bTextStyle\(", all_text))
    safe_areas = len(re.findall(r"\bSafeArea\(", all_text))
    spinners = len(re.findall(r"CircularProgressIndicator\(|EasyLoading\.show", all_text))
    skeletons = len(re.findall(r"Shimmer|Skeletonizer|Skeleton\(", all_text))
    fonts = sorted(set(re.findall(r"GoogleFonts\.(\w+?)(?:TextTheme)?\(", all_text)) | set(re.findall(r"fontFamily:\s*['\"](\w+)", all_text)))
    theme_parts = sorted(set(re.findall(r"\b(\w+Theme)\s*:", all_text)) & {
        "appBarTheme", "inputDecorationTheme", "elevatedButtonTheme", "filledButtonTheme", "textButtonTheme",
        "outlinedButtonTheme", "cardTheme", "textTheme", "bottomSheetTheme", "dialogTheme", "snackBarTheme"})
    print(f"- Design system: {raw_colors} raw Color(0x..), {text_styles} inline TextStyle(, "
          f"{len(fonts)} font families {fonts[:7]}, theme components: {', '.join(theme_parts) or 'none'}")
    print(f"- UI states: {spinners} spinners vs {skeletons} skeleton uses; SafeArea x{safe_areas}")
    print()
    print("**Most-used packages (import count)**")
    for name, n in imports.most_common(25):
        if name != app:
            print(f"- {name}: {n}")
    print()
    print("**Signals to check (heuristic, verify before reporting)**")
    if not risks and not big_files and tests:
        print("- none")
    for msg, n in risks.most_common():
        sample = ", ".join(risk_files[msg][:3])
        print(f"- {msg}: {n} file(s), e.g. {sample}")
    for lines, path in sorted(big_files, reverse=True)[:5]:
        print(f"- large file ({lines} lines): {path}")
    try:
        import subprocess
        tracked = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, timeout=20).stdout.splitlines()
    except Exception:
        tracked = []
    signing = [t for t in tracked if re.search(r"\.(jks|keystore|p12|pem)$|(^|/)key\.properties$", t)]
    if signing:
        print(f"- CRITICAL: signing material tracked in git: {', '.join(signing[:5])}")
    if re.search(r"\b(sk|rk)_(live|test)_[A-Za-z0-9]{10,}", all_text):
        print("- CRITICAL: Stripe secret/restricted key in lib/ (value not shown)")
    if "api.stripe.com" in all_text:
        print("- CRITICAL: app calls api.stripe.com directly; secret-key operations belong on the server")
    if re.search(r"(checkConnectivity\(\)|onConnectivityChanged)[\s\S]{0,300}[!=]=\s*ConnectivityResult\.none", all_text):
        print("- connectivity compared with == ConnectivityResult.none; connectivity_plus >= 6 returns a List, so this is always false")
    if "taskBox.clear()" in all_text or re.search(r"\b\w*[Bb]ox\.clear\(\)", all_text):
        print("- local box cleared during sync: check it can't wipe unsynced local changes")
    if tests and all("Counter increments smoke test" in read(t) for t in tests):
        print("- the only test is Flutter's default counter test (it fails and covers nothing)")
    if not tests:
        print("- no tests under test/")
    if "shared_preferences" in deps and "flutter_secure_storage" not in deps:
        print("- shared_preferences without flutter_secure_storage: check where auth tokens are stored")
    if firebase and not (lib / "firebase_options.dart").is_file():
        print("- firebase packages present but no lib/firebase_options.dart")


if __name__ == "__main__":
    main()
