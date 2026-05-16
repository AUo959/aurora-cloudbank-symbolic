"""RESETCORE restore handler for reflective autonomy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml

try:
    from .capsule_linter import CapsuleLinter
    from .reflective_autonomy_loop import ReflectiveAutonomyLoop
except ImportError:  # pragma: no cover - direct script execution fallback
    from capsule_linter import CapsuleLinter
    from reflective_autonomy_loop import ReflectiveAutonomyLoop

MODULE_ROOT = Path(__file__).resolve().parent
DEFAULT_GOVERNANCE_PATH = MODULE_ROOT / "loom_governance_system.yaml"


def load_governance_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the RESETCORE governance capsule descriptor."""
    path = Path(config_path) if config_path else DEFAULT_GOVERNANCE_PATH
    with open(path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError("Governance config root must be a mapping.")
    return config


def build_resetcore_plan(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return the declared RESETCORE restore sequence."""
    governance_config = config or load_governance_config()
    resetcore = governance_config.get("resetcore", {})
    return {
        "command": resetcore.get("command", "RESETCORE"),
        "handler": resetcore.get("handler"),
        "purpose": resetcore.get("purpose"),
        "sequence": list(resetcore.get("sequence", [])),
        "ethics_protocol": governance_config.get("governance", {}).get("ethics_protocol"),
        "anchor_seed": governance_config.get("system_identity", {}).get("anchor_seed"),
    }


def run_resetcore(
    config_path: Optional[Path] = None,
    audit_log_path: Optional[Path] = None,
    payload_files: Optional[Iterable[Path]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Run or preview the RESETCORE reflective autonomy restore sequence."""
    config = load_governance_config(config_path)
    plan = build_resetcore_plan(config)
    linter = CapsuleLinter()
    audit_path = Path(audit_log_path) if audit_log_path else None
    loop = ReflectiveAutonomyLoop(linter=linter, audit_log_path=None if dry_run else audit_path)
    receipt = loop.run_cycle(payload_files=payload_files).to_dict()
    return {
        "resetcore": plan,
        "dry_run": dry_run,
        "receipt": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RESETCORE reflective autonomy restore.")
    parser.add_argument("--config", type=Path, default=DEFAULT_GOVERNANCE_PATH)
    parser.add_argument("--audit-log", type=Path, default=Path(".loom/reflect/autonomy_audit_log.txt"))
    parser.add_argument("--execute", action="store_true", help="Write the audit receipt.")
    args = parser.parse_args()

    result = run_resetcore(
        config_path=args.config,
        audit_log_path=args.audit_log,
        dry_run=not args.execute,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_resetcore_plan", "load_governance_config", "run_resetcore"]
