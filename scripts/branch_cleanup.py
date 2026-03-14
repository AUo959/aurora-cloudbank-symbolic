#!/usr/bin/env python3
"""Compatibility wrapper: delegate branch cleanup to branch_manager.py."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    from .branch_manager import BranchManager
except ImportError:
    from branch_manager import BranchManager


def main() -> int:
    parser = argparse.ArgumentParser(description="Branch cleanup wrapper")
    parser.add_argument("--execute", action="store_true", help="Execute deletions (default is dry-run)")
    parser.add_argument("--report-only", action="store_true", help="Generate branch report without cleanup")
    parser.add_argument("--max-age", type=int, default=90, help="Maximum branch age in days")
    parser.add_argument("--categories", nargs="+", default=["feature", "dependency", "security"], help="Categories")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    manager = script_dir / "branch_manager.py"

    if args.report_only:
        print(BranchManager(".").generate_report())
        return 0

    cmd = [sys.executable, str(manager), "--cleanup", "--max-age", str(args.max_age), "--categories", *args.categories]
    if args.execute:
        cmd.append("--execute")

    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
