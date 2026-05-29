#!/usr/bin/env python3
"""
Print the current test inventory: file count and test-function count.

README.md and CLAUDE.md should not carry static "1,030+ tests" / "109 test
files" claims. Run this script and use its output (or pipe it into a docs
regenerator) so that documentation matches reality.

Usage:
    python scripts/test_inventory.py
    python scripts/test_inventory.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"
_TEST_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+test_", re.MULTILINE)


def collect() -> dict[str, int | str]:
    if not TESTS_DIR.exists():
        return {"file_count": 0, "function_count": 0, "as_of": date.today().isoformat()}
    file_paths = list(TESTS_DIR.rglob("test_*.py"))
    function_count = 0
    for path in file_paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        function_count += sum(1 for _ in _TEST_DEF_RE.finditer(text))
    return {
        "file_count": len(file_paths),
        "function_count": function_count,
        "as_of": date.today().isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()
    inv = collect()
    if args.json:
        print(json.dumps(inv, indent=2))
    else:
        print(f"Test files:     {inv['file_count']}")
        print(f"Test functions: {inv['function_count']}")
        print(f"As of:          {inv['as_of']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
