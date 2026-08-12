#!/usr/bin/env python3
"""Declaration gate: every tracked root object must be declared.

Aurora's complexity is the substrate (issue #1504); the failure mode this
guard prevents is UNDECLARED growth — root objects entering the tree without
registering in the declared set. Declared complexity is navigable; undeclared
complexity is drift.

Two checks, both symmetric (the registry must equal reality):

  1. Root allowlist: every tracked root-level file or directory must appear in
     config/root_registry.yaml. New root objects are welcome — declare them.
  2. Dependency-file set: tracked root files matching requirements*.txt or
     requirements*.lock must exactly match the registry's dependency_files.

Reads NUL-separated tracked paths on stdin (portable, no GitPython):

    git ls-files -z | python scripts/check_root_declaration.py

Exits 0 when the declared set matches the tracked set, 1 with a diff-style
report otherwise. Modeled on scripts/check_casefold_collisions.py (#1488).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REGISTRY_PATH = Path("config/root_registry.yaml")
DEPENDENCY_FILE_RE = re.compile(r"requirements[^/]*\.(?:txt|lock)")


def load_registry(path: Path) -> dict[str, set[str]]:
    """Load the registry. Prefers PyYAML; falls back to a strict mini-parser
    for the flat 'section: / - "entry"' shape so CI needs no extra deps."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return {
            section: set(data.get(section) or [])
            for section in ("root_objects", "dependency_files")
        }
    except ImportError:
        pass

    sections: dict[str, set[str]] = {"root_objects": set(), "dependency_files": set()}
    current: str | None = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        section_match = re.match(r"^(\w+):\s*$", line)
        if section_match:
            current = section_match.group(1)
            continue
        entry_match = re.match(r'^\s+-\s+"?([^"#]+?)"?\s*$', line)
        if entry_match and current in sections:
            sections[current].add(entry_match.group(1))
    return sections


def root_objects_of(tracked_paths: list[str]) -> set[str]:
    return {p.split("/", 1)[0] for p in tracked_paths if p}


def dependency_files_of(root_names: set[str]) -> set[str]:
    return {n for n in root_names if DEPENDENCY_FILE_RE.fullmatch(n)}


def check(tracked_paths: list[str], registry: dict[str, set[str]]) -> list[str]:
    """Return a list of violation reports (empty when declared == tracked)."""
    actual_roots = root_objects_of(tracked_paths)
    declared_roots = registry["root_objects"]
    violations: list[str] = []

    undeclared = sorted(actual_roots - declared_roots)
    if undeclared:
        violations.append(
            "UNDECLARED root objects (declare in config/root_registry.yaml "
            "with their purpose, or remove them):\n  - " + "\n  - ".join(undeclared)
        )

    stale = sorted(declared_roots - actual_roots)
    if stale:
        violations.append(
            "STALE declarations (registry lists objects no longer tracked; "
            "remove the declaration or restore the object):\n  - " + "\n  - ".join(stale)
        )

    actual_deps = dependency_files_of(actual_roots)
    declared_deps = registry["dependency_files"]
    new_deps = sorted(actual_deps - declared_deps)
    if new_deps:
        violations.append(
            "UNDECLARED dependency files (new dependency surfaces require an "
            "exemption: declare the file and its role in config/root_registry.yaml):\n  - "
            + "\n  - ".join(new_deps)
        )
    stale_deps = sorted(declared_deps - actual_deps)
    if stale_deps:
        violations.append(
            "STALE dependency-file declarations (declared but not tracked):\n  - "
            + "\n  - ".join(stale_deps)
        )

    return violations


def main() -> int:
    raw = sys.stdin.buffer.read()
    tracked = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
    registry = load_registry(REGISTRY_PATH)
    violations = check(tracked, registry)
    if not violations:
        print(
            f"root declaration gate: OK "
            f"({len(root_objects_of(tracked))} root objects, "
            f"{len(registry['dependency_files'])} declared dependency files)"
        )
        return 0
    print("root declaration gate: FAILED\n")
    for report in violations:
        print(report + "\n")
    print(
        "Complexity is the substrate; declaration is the contract. "
        "Register new root objects in config/root_registry.yaml."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
