#!/usr/bin/env python3
"""Fail when tracked paths contain case-folded component collisions."""

from __future__ import annotations

import argparse
import sys
from pathlib import PurePosixPath


def tracked_paths(raw_paths: bytes) -> list[str]:
    """Parse NUL-delimited paths produced by ``git ls-files -z``."""
    return [path for path in raw_paths.decode("utf-8").split("\0") if path]


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


def git_tracked_paths() -> bytes:
    """Return NUL-delimited tracked paths from Git's index without a subprocess."""
    from git import Repo

    repo = Repo(".", search_parent_directories=True)
    tracked = sorted(path for path, stage in repo.index.entries if stage == 0)
    return b"\0".join(path.encode("utf-8") for path in tracked) + b"\0"


def main(raw_paths: bytes | None = None, *, from_git: bool = False) -> int:
    if raw_paths is None:
        if from_git:
            try:
                raw_paths = git_tracked_paths()
            except (ImportError, OSError) as exc:
                print(f"ERROR: could not list tracked paths: {exc}", file=sys.stderr)
                return 2
        else:
            raw_paths = sys.stdin.buffer.read()
    paths = tracked_paths(raw_paths)
    if not paths:
        print("ERROR: no tracked paths received on standard input.", file=sys.stderr)
        return 2

    collisions = find_casefold_collisions(paths)
    if not collisions:
        print(f"OK: {len(paths)} tracked paths have unique case-folded components.")
        return 0

    print(
        "ERROR: tracked paths contain case-folded component collisions:",
        file=sys.stderr,
    )
    for spellings in collisions.values():
        print(f"  {' <> '.join(spellings)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--git-ls-files",
        action="store_true",
        help="read tracked paths directly from git instead of standard input",
    )
    args = parser.parse_args()
    raise SystemExit(main(from_git=args.git_ls_files))
