#!/usr/bin/env python3
"""Verify requirements-ci-hashed.txt still covers every declared requirement.

Why this exists
---------------
CI installs with ``--require-hashes -r requirements-ci-hashed.txt``, which
installs *only* what that lock names. If someone adds a package to
``requirements.txt`` or ``requirements-test.txt`` without regenerating the
lock, the install still succeeds — the new package is simply absent — and the
failure surfaces much later as an ``ImportError`` inside an unrelated test.

This turns that into an explicit, early error naming the missing package and
the command that fixes it.

Exit codes:
    0 - every declared requirement is present in the lock
    1 - drift detected (missing packages listed on stderr)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("requirements.txt", "requirements-test.txt")
LOCK = "requirements-ci-hashed.txt"

REGENERATE_CMD = (
    "uv pip compile --universal --generate-hashes --only-binary=:all: "
    "--python-version 3.12 --constraints requirements-hashed.txt "
    "--output-file requirements-ci-hashed.txt requirements.txt requirements-test.txt"
)

# PEP 503 normalisation: runs of -_. collapse to a single -, case-insensitive.
_SEPARATORS = re.compile(r"[-_.]+")


def normalize(name: str) -> str:
    return _SEPARATORS.sub("-", name.strip().lower())


def requirement_name(line: str) -> str | None:
    """Extract the distribution name from a requirements line, or None."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Skip flags (-r, -c, --hash, etc.) and non-name forms.
    if line.startswith("-"):
        return None
    # Strip environment markers, extras, and version specifiers.
    line = line.split(";", 1)[0]
    line = line.split("[", 1)[0]
    name = re.split(r"[=<>!~\s]", line, 1)[0]
    return normalize(name) if name else None


def locked_names(lock_path: Path) -> set[str]:
    names: set[str] = set()
    for raw in lock_path.read_text().splitlines():
        stripped = raw.strip()
        # Lock entries are unindented "name==version \"; hashes are indented.
        if not stripped or stripped.startswith(("#", "-")) or raw[:1].isspace():
            continue
        name = requirement_name(stripped)
        if name:
            names.add(name)
    return names


def find_missing(locked: set[str]) -> list[tuple[str, str]]:
    """Return (source_file, package) for every declared requirement not locked.

    Split out of :func:`main` to keep that function within the complexity
    budget the repository's static analysis enforces.
    """
    missing: list[tuple[str, str]] = []
    for source in SOURCES:
        source_path = REPO_ROOT / source
        if not source_path.exists():
            continue
        for raw in source_path.read_text().splitlines():
            name = requirement_name(raw)
            if name and name not in locked:
                missing.append((source, name))
    return missing


def main() -> int:
    lock_path = REPO_ROOT / LOCK
    if not lock_path.exists():
        print(f"error: {LOCK} not found", file=sys.stderr)
        return 1

    locked = locked_names(lock_path)
    missing = find_missing(locked)

    if missing:
        print(
            f"error: {LOCK} is missing {len(missing)} declared requirement(s).\n"
            "CI installs only what this lock names, so these would be silently\n"
            "absent and surface later as an ImportError.\n",
            file=sys.stderr,
        )
        for source, name in missing:
            print(f"  {name}  (declared in {source})", file=sys.stderr)
        print(f"\nRegenerate with:\n  {REGENERATE_CMD}", file=sys.stderr)
        return 1

    print(f"{LOCK} covers all {len(locked)} locked distributions; no drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
