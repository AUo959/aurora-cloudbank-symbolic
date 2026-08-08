#!/usr/bin/env python3
"""Legacy Orion bootstrap compatibility shim.

This module is retained so old references fail safely instead of recreating the
pre-2026 initialization model. It is **not** the canonical L1 INIT path.

Canonical commands:

    python .aurora/init_l1.py preflight
    python .aurora/init_l1.py init --seed 1337

The historical ``SIMULATION_STATE.json`` may still be read for provenance, but
this shim will not save it, route Pilot into station locations, activate the
legacy Primary-8 cache, or declare the legacy state to be live genesis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_runtime import OrionL1Runtime  # noqa: E402

LEGACY_STATE_PATH = Path(__file__).resolve().parent / "SIMULATION_STATE.json"


def load_simulation_state() -> Dict[str, Any]:
    """Read the historical state for provenance/compatibility only."""
    return json.loads(LEGACY_STATE_PATH.read_text(encoding="utf-8"))


def save_simulation_state(state: Dict[str, Any]) -> bool:
    """Refuse legacy state mutation.

    Live run persistence belongs to ``simulation/l1_runtime.py`` and must stay
    outside the repository.
    """
    del state
    return False


def validate_agent_files() -> List[str]:
    """Legacy compatibility surface; the Primary-8 cache is no longer an INIT gate."""
    return []


def route_to_location(keyword: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Reject the old physical-routing model.

    Observation focus is now control-plane instrumentation. It must not mutate a
    Pilot location in L1.
    """
    del state
    return {
        "success": False,
        "deprecated": True,
        "keyword": keyword,
        "pilot_embodied": False,
        "replacement": "OrionL1Runtime.observe(focus)",
        "reason": "Pilot observation is instrumentation, not physical station routing",
    }


def print_simulation_briefing(state: Optional[Dict[str, Any]] = None) -> None:
    """Print the current governed preflight status instead of legacy live state."""
    del state
    report = OrionL1Runtime().preflight()
    print("💠 Aurora L1 compatibility shim: legacy bootstrap retired.")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("Use: python .aurora/init_l1.py init --seed 1337")


def get_character_cache() -> None:
    """Return no legacy cache; live L1 must not bootstrap from the old Primary 8."""
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Deprecated Orion simulation loader")
    parser.add_argument("--route", default=None)
    parser.add_argument("--cache", action="store_true")
    args = parser.parse_args()

    if args.route:
        print(json.dumps(route_to_location(args.route), indent=2, sort_keys=True))
        return 2
    if args.cache:
        print(
            "Legacy Primary-8 cache is retired. Use the canonical roster and L1 runtime contract.",
            file=sys.stderr,
        )
        return 2

    print_simulation_briefing()
    return 0 if OrionL1Runtime().preflight()["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
