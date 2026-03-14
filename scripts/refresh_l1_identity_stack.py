#!/usr/bin/env python3
"""Refresh the current L1 + Aurora identity artifact stack from canon sources."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence, Tuple


SUBREPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def build_steps(include_l2_relays: bool, verify: bool) -> List[Tuple[str, Sequence[str]]]:
    steps: List[Tuple[str, Sequence[str]]] = [
        ("Sync L1 human mesh agents", [PYTHON, "scripts/sync_l1_human_mesh_agents.py"]),
        ("Build Aurora identity artifacts", [PYTHON, "scripts/build_aurora_identity_artifacts.py"]),
        ("Build L1 entity ledger", [PYTHON, "scripts/build_l1_entity_ledger.py"]),
    ]
    if include_l2_relays:
        steps.insert(1, ("Sync L2 relay mesh agents", [PYTHON, "scripts/sync_l2_meta_mesh_agents.py"]))
    if verify:
        steps.append(
            (
                "Run focused verification",
                [
                    PYTHON,
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_build_aurora_identity_artifacts.py",
                    "tests/test_mesh_manifest_extensions.py",
                    "tests/test_mesh_router_v1.py",
                ],
            )
        )
    return steps


def run_steps(steps: List[Tuple[str, Sequence[str]]], dry_run: bool) -> int:
    completed = 0
    for label, cmd in steps:
        print(f"== {label} ==")
        print(" ".join(cmd))
        if dry_run:
            continue
        subprocess.run(cmd, cwd=SUBREPO_ROOT, check=True)
        completed += 1
    print(f"completed {completed} refresh steps")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh the current L1 + Aurora identity artifact stack.")
    parser.add_argument("--dry-run", action="store_true", help="Print the refresh plan without writing files.")
    parser.add_argument(
        "--include-l2-relays",
        action="store_true",
        help="Also refresh the L2 relay manifests and memory files.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run the focused identity/mesh verification suite after refresh.",
    )
    args = parser.parse_args()

    steps = build_steps(include_l2_relays=args.include_l2_relays, verify=args.verify)
    return run_steps(steps, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
