#!/usr/bin/env python3
"""Orion L1 preflight / INIT command.

Examples:
    python .aurora/init_l1.py preflight
    python .aurora/init_l1.py init --seed 1337 --run-root ~/.aurora/l1-runs

Preflight is read-only with respect to run state. INIT creates a tick-zero run
outside the repository; it does not advance the station.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
for import_path in (PROJECT_ROOT, SIMULATION_DIR):
    value = str(import_path)
    if value not in sys.path:
        sys.path.insert(0, value)

from l1_runtime import OrionL1Runtime, PreflightError  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed Orion L1 preflight and INIT")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "preflight",
        help="Validate INIT gates without creating or advancing a run",
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Create a tick-zero advancement-capable L1 run",
    )
    init_parser.add_argument(
        "--seed",
        type=int,
        default=1337,
        help="Deterministic runtime seed",
    )
    init_parser.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="External persistence directory (default: ~/.aurora/l1-runs)",
    )
    init_parser.add_argument(
        "--cloudbank-revision",
        default=None,
        help="Explicit CloudBank 40-character git SHA; otherwise resolve current checkout HEAD",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    runtime = OrionL1Runtime()

    if args.command == "preflight":
        report = runtime.preflight()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["ready"] else 2

    try:
        cloudbank_revision = (
            args.cloudbank_revision or runtime.resolve_cloudbank_revision()
        )
        state = runtime.init_run(
            cloudbank_revision=cloudbank_revision,
            seed=args.seed,
            run_root=args.run_root,
            persist=True,
        )
    except (PreflightError, ValueError, RuntimeError) as exc:
        print(f"INIT BLOCKED: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": "INITIALIZED",
                "run_id": state.manifest.run_id,
                "tick": state.manifest.tick,
                "cloudbank_revision": state.manifest.cloudbank_revision,
                "canonrec_revision": state.manifest.canonrec_revision,
                "seed": state.manifest.seed,
                "active_quarantines": state.manifest.active_quarantines,
                "pilot": state.world_state["pilot"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
