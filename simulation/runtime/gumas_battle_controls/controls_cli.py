#!/usr/bin/env python3
"""Phase-11 entry point: authority preflight, or Run 0 plus Controls A/B/C.

``preflight`` never executes a macrostep. ``execute`` refuses unless the
committed authority grants both capabilities on ``--as-of``. ``--verify``
regenerates the evidence and fails unless it is byte-identical to a
committed evidence file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.gumas_battle_controls import (  # noqa: E402
    CAPABILITY_CONTROLS,
    CAPABILITY_RUN0,
    execute_controls,
    preflight,
    verify_evidence,
)
from simulation.runtime.gumas_battle_controls.identity import canonical_json_bytes  # noqa: E402


def _repo_file(path: Path) -> Path:
    """Resolve a committed input file, refusing anything outside the repository."""
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT.resolve()) or not resolved.is_file():
        raise SystemExit(f"input must be a file inside the repository: {path}")
    return resolved


def _load(path: Path | None):
    if path is None:
        return None
    return json.loads(_repo_file(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "execute"))
    parser.add_argument("--canonrec-root", type=Path)
    parser.add_argument("--authority", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--rendered-out", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    authority = _load(args.authority)
    if args.mode == "preflight":
        result = {cap: preflight(authority, cap, args.as_of) for cap in (CAPABILITY_RUN0, CAPABILITY_CONTROLS)}
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if all(item["authorized"] for item in result.values()) else 3

    for cap in (CAPABILITY_RUN0, CAPABILITY_CONTROLS):
        result = preflight(authority, cap, args.as_of)
        if not result["authorized"]:
            print(json.dumps(result["refusal"], sort_keys=True, indent=2))
            return 3
    if args.canonrec_root is None:
        parser.error("execute requires --canonrec-root")
    evidence = execute_controls(
        args.canonrec_root,
        authority,
        args.as_of,
        workers=args.workers,
        rendered_out=args.rendered_out,
    )
    verify_evidence(evidence)
    data = json.dumps(evidence, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data, encoding="utf-8")
    summary = {
        "all_controls_passed": evidence["all_controls_passed"],
        "evidence_sha256": evidence["evidence_sha256"],
        "run0_terminal_outcome": evidence["run0_receipt"]["terminal_outcome"],
        "run0_macrosteps": evidence["run0_receipt"]["macrosteps_executed"],
    }
    print(json.dumps(summary, sort_keys=True))
    if args.verify:
        committed = _load(args.verify)
        verify_evidence(committed)
        if canonical_json_bytes(committed) != canonical_json_bytes(evidence):
            print("regenerated Phase-11 evidence differs from committed evidence", file=sys.stderr)
            return 4
        print("regenerated Phase-11 evidence is byte-identical to the committed file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
