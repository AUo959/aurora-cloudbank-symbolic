#!/usr/bin/env python3
"""Warn on shallow test assertions without blocking commits."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SHALLOW_PATTERNS = (
    re.compile(r"\bassert\b.*\bis\s+not\s+None\b"),
    re.compile(r"\bassert\s+hasattr\s*\("),
)
ESCAPE_HATCH = "# noqa: shallow-ok"


def iter_candidate_files(args: list[str]) -> list[Path]:
    if args:
        return [Path(arg) for arg in args if Path(arg).suffix == ".py" and "tests" in Path(arg).parts]
    return sorted(Path("tests").rglob("*.py"))


def find_matches(path: Path) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return matches

    for line_no, line in enumerate(lines, start=1):
        if ESCAPE_HATCH in line:
            continue
        if any(pattern.search(line) for pattern in SHALLOW_PATTERNS):
            matches.append((line_no, line.strip()))
    return matches


def main(argv: list[str]) -> int:
    candidates = iter_candidate_files(argv[1:])
    findings: list[tuple[Path, int, str]] = []

    for path in candidates:
        findings.extend((path, line_no, line) for line_no, line in find_matches(path))

    if findings:
        print("WARNING: shallow test assertions detected (non-blocking):", file=sys.stderr)
        for path, line_no, line in findings:
            print(f"  {path}:{line_no}: {line}", file=sys.stderr)
        print("Use a behavior assertion or add '# noqa: shallow-ok' for rare smoke-test exceptions.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
