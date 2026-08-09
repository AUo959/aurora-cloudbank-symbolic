#!/usr/bin/env python3
"""Fail when tracked paths contain case-folded component collisions."""

from __future__ import annotations

import shutil

# Fixed Git command; no user-controlled executable or arguments.
import subprocess  # nosec B404
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]


def tracked_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    """Return Git-tracked paths without relying on checkout casing."""
    git_executable = shutil.which("git")
    if git_executable is None:
        raise RuntimeError("git executable not found")
    # Absolute executable plus fixed arguments; no shell or user input.
    output = subprocess.check_output(  # nosec B603
        [git_executable, "ls-files", "-z"], cwd=repo_root, text=True
    )
    return [path for path in output.split("\0") if path]


def find_casefold_collisions(paths: list[str]) -> dict[str, list[str]]:
    """Group path components that differ only by Unicode-aware casing."""
    prefixes: dict[str, set[str]] = {}
    for path in paths:
        parts = PurePosixPath(path).parts
        for depth in range(1, len(parts) + 1):
            prefix = "/".join(parts[:depth])
            prefixes.setdefault(prefix.casefold(), set()).add(prefix)

    return {
        key: sorted(spellings)
        for key, spellings in prefixes.items()
        if len(spellings) > 1
    }


def main() -> int:
    paths = tracked_paths()
    collisions = find_casefold_collisions(paths)
    if not collisions:
        print(f"OK: {len(paths)} tracked paths have unique case-folded components.")
        return 0

    print("ERROR: tracked paths contain case-folded component collisions:")
    for spellings in collisions.values():
        print(f"  {' <> '.join(spellings)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
