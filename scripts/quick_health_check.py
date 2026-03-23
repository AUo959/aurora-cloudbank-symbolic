#!/usr/bin/env python3
"""Quick repository health check.

Preserves a simple operator-facing report while making branch counting
robust for repositories that do not have remote refs configured.
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from typing import Iterable, List


def _parse_branches(raw_output: str) -> List[str]:
    """Return normalized branch names from git output."""

    return [
        branch.strip()
        for branch in raw_output.strip().splitlines()
        if branch.strip()
        and not branch.startswith("origin/HEAD")
        and branch.strip() != "origin"
    ]


def _list_git_branches(command: Iterable[str]) -> List[str]:
    """Run a git branch command and return parsed branches."""

    result = subprocess.run(list(command), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    return _parse_branches(result.stdout)


def _get_branch_count() -> int:
    """Count remote branches, falling back to local branches when needed."""

    remote_branches = _list_git_branches(["git", "branch", "-r", "--format=%(refname:short)"])
    if remote_branches:
        return len(remote_branches)

    local_branches = _list_git_branches(["git", "branch", "--format=%(refname:short)"])
    return len(local_branches)


def quick_health_check() -> None:
    """Print a lightweight repository branch-health summary."""

    print("🩺 Quick Repository Health Check")

    try:
        branch_count = _get_branch_count()
        print(f"   🌳 Current branches: {branch_count}")

        if branch_count <= 30:
            print("   💚 Status: EXCELLENT (maintaining gains!)")
        elif branch_count <= 35:
            print("   🟡 Status: GOOD (minor growth)")
        elif branch_count <= 45:
            print("   🟠 Status: FAIR (needs attention)")
        else:
            print("   🔴 Status: CRITICAL (requires immediate action)")

        print(f"   📅 Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as exc:
        print(f"   💥 Error: {exc}")


if __name__ == "__main__":
    quick_health_check()
