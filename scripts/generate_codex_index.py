#!/usr/bin/env python3
"""Generate simulation/CODEX_INDEX.md from the phase technical registers (#1133).

The six CODEX phase pairs (a COMPLETE.md narrative plus a TECHNICAL_REGISTER.json)
had no index, so there was no single place to see what the phases cover or how
the roster version advanced across them.

The index is *derived* from the registers rather than hand-maintained, following
the precedent set by `.aurora/ORION_STATION_CREW_MANIFEST.md` (#1083): a
hand-written index drifts from its source silently, a generated one cannot.
Regenerate rather than edit the output.

Usage:
    python scripts/generate_codex_index.py           # write the index
    python scripts/generate_codex_index.py --check   # fail if it is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "simulation"
OUTPUT = SIM_DIR / "CODEX_INDEX.md"

REGISTER_GLOB = "CODEX_PHASE*_TECHNICAL_REGISTER.json"


def load_phases() -> List[Dict[str, Any]]:
    phases = []
    for path in sorted(SIM_DIR.glob(REGISTER_GLOB)):
        data = json.loads(path.read_text())
        number = data.get("phase")
        if number is None:
            m = re.search(r"PHASE(\d+)", path.name)
            number = int(m.group(1)) if m else 0
        narrative = next(
            (p for p in SIM_DIR.glob(f"CODEX_PHASE{number}_*_COMPLETE.md")), None
        )
        phases.append(
            {
                "number": number,
                "name": data.get("phase_name") or "(unnamed)",
                "register": path.name,
                "narrative": narrative.name if narrative else None,
                "date": data.get("integration_date"),
                "roster": roster_span(data),
                "status": data.get("integration_status") or {},
            }
        )
    return sorted(phases, key=lambda p: p["number"])


def roster_span(data: Dict[str, Any]) -> str:
    """Roster version movement, which the registers spell three different ways."""
    status = data.get("integration_status") or {}
    for before, after in (
        ("roster_version_from", "roster_version_to"),
        ("before", "after"),
    ):
        src = status if before in status else data.get("roster_version")
        if isinstance(src, dict) and before in src and after in src:
            return f"{src[before]} → {src[after]}"
    if "roster_version_change" in status:
        return str(status["roster_version_change"]).replace(" → ", " → ")
    version = data.get("roster_version")
    if isinstance(version, dict):
        return f"{version.get('before', '?')} → {version.get('after', '?')}"
    return str(version) if version else "—"


def render(phases: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    add = lines.append

    add("# CODEX Phase Index")
    add("")
    add("<!-- GENERATED FILE — do not edit by hand.")
    add("     Regenerate: python scripts/generate_codex_index.py")
    add("     Source: simulation/CODEX_PHASE*_TECHNICAL_REGISTER.json -->")
    add("")
    add("Index of the CODEX character-integration phases. Each phase ships a pair:")
    add("a `*_COMPLETE.md` narrative record and a `*_TECHNICAL_REGISTER.json`")
    add("machine-readable register. Created for #1133.")
    add("")
    add("## Phases")
    add("")
    add("| Phase | Division / scope | Roster | Date | Records |")
    add("|---|---|---|---|---|")
    for p in phases:
        records = f"[register]({p['register']})"
        if p["narrative"]:
            records = f"[narrative]({p['narrative']}) · " + records
        add(
            f"| {p['number']} | {p['name']} | {p['roster']} | "
            f"{p['date'] or '—'} | {records} |"
        )
    add("")

    final = phases[-1]["status"] if phases else {}
    total = final.get("total_entities_in_roster")
    if total:
        add(f"The roster reaches **{total} entities** at the final phase, which the")
        add("Phase 6 register marks `2.0 (COMPLETE)`.")
        add("")

    add("## Related documents, with their real paths")
    add("")
    add("#1133 refers to two of these as if they sat in `simulation/`. They do not:")
    add("")
    add("| Document | Actual path |")
    add("|---|---|")
    add("| Layer architecture | [`docs/architecture/LAYER_ARCHITECTURE.md`](../docs/architecture/LAYER_ARCHITECTURE.md) |")
    add("| Simulation state / mission taxonomy | [`.aurora/SIMULATION_STATE.json`](../.aurora/SIMULATION_STATE.json) |")
    add("| Canonical roster | [`L1_CANON_CHARACTER_ROSTER.md`](L1_CANON_CHARACTER_ROSTER.md) |")
    add("| Crew manifest (generated) | [`.aurora/ORION_STATION_CREW_MANIFEST.md`](../.aurora/ORION_STATION_CREW_MANIFEST.md) |")
    add("")

    add("## Notes recorded while indexing")
    add("")
    add("These are observations from the registers themselves, not judgements about")
    add("the work:")
    add("")
    add("- **QGIA postdates every phase.** The `QGIA_Integration/` package is not")
    add("  accounted for in any phase register, so the phase sequence is not a")
    add("  complete picture of the simulation layer's integrations.")
    add("- **Phases 4 and 5 record `git_commit_status: \"Pending\"`** in their")
    add("  registers, although both are committed. The field was never updated after")
    add("  the commit landed; it reflects the state at authoring time, not now.")
    add("- **Phases 4 and 5 both note a character-count discrepancy** (32 loaded vs")
    add("  33 total human staff; 35 vs 36), attributed in-register to parsing rather")
    add("  than to missing characters. Unresolved in both.")
    add("- **Phase 6 has no `integration_date`** and no division summary; it records")
    add("  L2/L3 systems rather than a staffed division.")
    add("")
    add("The Phase 6 terminology audit against `LAYER_ARCHITECTURE.md` that #1133")
    add("also asks for is *not* done here — it is a canon-consistency review rather")
    add("than an indexing task.")
    add("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the index is stale")
    args = parser.parse_args()

    phases = load_phases()
    if not phases:
        print("error: no CODEX phase registers found", file=sys.stderr)
        return 1

    content = render(phases)

    if args.check:
        if not OUTPUT.exists():
            print(f"error: {OUTPUT.relative_to(REPO_ROOT)} does not exist", file=sys.stderr)
            return 1
        if OUTPUT.read_text() != content:
            print(
                f"error: {OUTPUT.relative_to(REPO_ROOT)} is stale.\n"
                "Regenerate: python scripts/generate_codex_index.py",
                file=sys.stderr,
            )
            return 1
        print(f"{OUTPUT.relative_to(REPO_ROOT)} is up to date ({len(phases)} phases).")
        return 0

    OUTPUT.write_text(content)
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(phases)} phases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
