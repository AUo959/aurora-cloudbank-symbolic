#!/usr/bin/env python3
"""Dry-run-first ZIP archive helper for repository cleanup."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

DEFAULT_THRESHOLD_MB = 50


def find_candidates(root: Path, threshold_bytes: int) -> list[Path]:
    candidates = []
    for path in root.iterdir():
        if path.is_file() and path.suffix.lower() == ".zip" and path.stat().st_size >= threshold_bytes:
            candidates.append(path)
    return sorted(candidates, key=lambda candidate: candidate.stat().st_size, reverse=True)


def format_size_mb(path: Path) -> str:
    return f"{path.stat().st_size / (1024 * 1024):.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive large ZIP files with a dry-run-first workflow")
    parser.add_argument("--root", default=".", help="Directory to scan (non-recursive)")
    parser.add_argument("--archive-dir", default="archive", help="Directory used for archived ZIP files")
    parser.add_argument("--threshold-mb", type=int, default=DEFAULT_THRESHOLD_MB, help="Minimum ZIP size to match")
    parser.add_argument("--execute", action="store_true", help="Move matching ZIP files into the archive directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Scan root is not a directory: {root}")
        return 1

    archive_dir = Path(args.archive_dir)
    if not archive_dir.is_absolute():
        archive_dir = root / archive_dir

    candidates = find_candidates(root, args.threshold_mb * 1024 * 1024)
    if not candidates:
        print(f"No ZIP files >= {args.threshold_mb} MB found in {root}")
        return 0

    print(f"Found {len(candidates)} ZIP file(s) >= {args.threshold_mb} MB in {root}:")
    for candidate in candidates:
        print(f" - {candidate.name} ({format_size_mb(candidate)} MB) -> {archive_dir / candidate.name}")

    if not args.execute:
        print("Dry run only. Re-run with --execute to move these files.")
        return 0

    archive_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    skipped = 0
    for candidate in candidates:
        target = archive_dir / candidate.name
        if target.exists():
            print(f"Skipping {candidate.name}: target already exists at {target}")
            skipped += 1
            continue
        shutil.move(str(candidate), str(target))
        print(f"Moved {candidate.name} -> {target}")
        moved += 1

    print(f"Archive pass complete. moved={moved} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
