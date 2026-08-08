#!/usr/bin/env python3
"""Retired historical Orion state builder.

This file used to rebuild ``.aurora/SIMULATION_STATE.json`` by combining a v1
backup with historical infrastructure fragments. That process hard-coded
physical and population claims that are now explicitly disputed or semantically
untyped, including Earth-Moon L4 and the aggregate value ``81``.

It is retained at its historical path so old automation fails safely and points
to the governed L1 lifecycle instead of silently rewriting tracked state.

Supported live path:

    python .aurora/init_l1.py preflight
    python .aurora/init_l1.py init --seed 1337

Historical inputs remain in the repository for provenance. They are not a live
L1 genesis source.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
LEGACY_STATE_PATH = HERE / "SIMULATION_STATE.json"
BASELINE_PATH = PROJECT_ROOT / "config" / "l1_runtime_baseline.json"


def historical_state_metadata() -> Dict[str, Any]:
    """Return non-causal metadata about the retained historical state."""
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {
        "status": "retired_builder",
        "legacy_state_path": str(LEGACY_STATE_PATH.relative_to(PROJECT_ROOT)),
        "legacy_state_exists": LEGACY_STATE_PATH.is_file(),
        "legacy_state_genesis_authority": baseline["legacy_state"]["genesis_authority"],
        "orbital_locus_status": baseline["orbital_locus"]["status"],
        "historical_current_crew_81": baseline["population"]["historical_aggregate_claims"]["current_crew_81"],
        "replacement": ".aurora/init_l1.py",
    }


def build_canonical_state(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
    """Refuse the obsolete build operation.

    The function remains importable so callers receive a controlled failure
    rather than recreating the old state format.
    """
    raise RuntimeError(
        "historical canonical-state builder is retired; use "
        "`.aurora/init_l1.py preflight` and `.aurora/init_l1.py init`"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Retired historical Orion state builder")
    parser.add_argument(
        "--status",
        action="store_true",
        help="show why this builder is retired without modifying any file",
    )
    args = parser.parse_args()

    if args.status:
        print(json.dumps(historical_state_metadata(), indent=2, sort_keys=True))
        return 0

    print(
        "BLOCKED: .aurora/build_canonical_state.py is retired and will not "
        "rewrite .aurora/SIMULATION_STATE.json.\n"
        "Use `python .aurora/init_l1.py preflight` followed by governed INIT.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
