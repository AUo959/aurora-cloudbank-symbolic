#!/usr/bin/env python3
"""Audit current docs and CI for stale root requirements-file references."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIREMENTS_REF_RE = re.compile(r"\brequirements(?:-[A-Za-z0-9_]+)?\.txt\b")

DEFAULT_SCAN_PATHS = (
    "CLAUDE.md",
    "README.md",
    "Makefile",
    "docs/DEPENDENCIES.md",
    "docs/guides/VERCEL_DEPLOYMENT.md",
    ".github/QUICK_REFERENCE.md",
    ".github/CODACY_INTEGRATION.md",
    ".github/copilot-instructions.md",
    ".github/chatmodes/code-quality-auditor.md",
    ".github/copilot/modes/code-quality-auditor.md",
    ".github/instructions/aurora-ai-instructions.md",
    ".github/workflows/dependency-validation.yml",
    "scripts/infallible_codespace_init.py",
    "scripts/setup_environment.sh",
    "scripts/validate_dependencies.py",
)


@dataclass(frozen=True)
class MissingReference:
    path: Path
    line_number: int
    reference: str


def root_requirements_files(repo_root: Path) -> set[str]:
    """Return tracked root requirements-file names that exist on disk."""
    return {path.name for path in repo_root.glob("requirements*.txt") if path.is_file()}


def iter_scan_files(repo_root: Path, scan_paths: tuple[str, ...]) -> list[Path]:
    """Return existing files from the configured scan list."""
    files: list[Path] = []
    for raw_path in scan_paths:
        path = repo_root / raw_path
        if path.is_file():
            files.append(path)
    return files


def collect_missing_references(
    repo_root: Path,
    scan_paths: tuple[str, ...] = DEFAULT_SCAN_PATHS,
) -> list[MissingReference]:
    """Find requirements-file references that do not exist at the repo root."""
    existing = root_requirements_files(repo_root)
    missing: list[MissingReference] = []

    for path in iter_scan_files(repo_root, scan_paths):
        relative_path = path.relative_to(repo_root)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for reference in sorted(set(REQUIREMENTS_REF_RE.findall(line))):
                if reference not in existing:
                    missing.append(MissingReference(relative_path, line_number, reference))

    return missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root to audit. Defaults to the parent of scripts/.",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    missing = collect_missing_references(repo_root)

    if missing:
        print("Stale requirements-file references found:")
        for item in missing:
            print(f"- {item.path}:{item.line_number}: {item.reference} does not exist at repo root")
        print("\nUpdate the reference or add the missing requirements file intentionally.")
        return 1

    existing = ", ".join(sorted(root_requirements_files(repo_root)))
    print(f"Requirements inventory references are current: {existing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
