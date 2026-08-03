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
        narrative = next(SIM_DIR.glob(f"CODEX_PHASE{number}_*_COMPLETE.md"), None)
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


def _pair(source: Any, before: str, after: str) -> str | None:
    """Return "X → Y" when *source* is a mapping carrying both keys."""
    if isinstance(source, dict) and before in source and after in source:
        return f"{source[before]} → {source[after]}"
    return None


def roster_span(data: Dict[str, Any]) -> str:
    """Roster version movement, which the registers spell three different ways.

    Phases 1-2 use integration_status.roster_version_from/to, phase 3 uses
    integration_status.roster_version_change, phases 4-5 use
    roster_version.before/after. Missing a shape yields "—", which
    test_roster_span_handles_every_register_shape treats as a failure.
    """
    status = data.get("integration_status") or {}
    version = data.get("roster_version")

    for source, before, after in (
        (status, "roster_version_from", "roster_version_to"),
        (version, "before", "after"),
        (status, "before", "after"),
    ):
        found = _pair(source, before, after)
        if found:
            return found

    if "roster_version_change" in status:
        return str(status["roster_version_change"])
    return str(version) if version else "—"


def _phase_table(phases: List[Dict[str, Any]]) -> List[str]:
    rows = [
        "## Phases",
        "",
        "| Phase | Division / scope | Roster | Date | Records |",
        "| --- | --- | --- | --- | --- |",
    ]
    for phase in phases:
        records = f"[register]({phase['register']})"
        if phase["narrative"]:
            records = f"[narrative]({phase['narrative']}) · " + records
        rows.append(
            f"| {phase['number']} | {phase['name']} | {phase['roster']} | "
            f"{phase['date'] or '—'} | {records} |"
        )
    rows.append("")

    final = phases[-1]["status"] if phases else {}
    total = final.get("total_entities_in_roster")
    if total:
        rows += [
            f"The roster reaches **{total} entities** at the final phase, which the",
            "Phase 6 register marks `2.0 (COMPLETE)`.",
            "",
        ]
    return rows


def _related_documents() -> List[str]:
    return [
        "## Related documents, with their real paths",
        "",
        "Issue #1133 refers to two of these as if they sat in `simulation/`. They do not:",
        "",
        "| Document | Actual path |",
        "| --- | --- |",
        "| Layer architecture | [`docs/architecture/LAYER_ARCHITECTURE.md`]"
        "(../docs/architecture/LAYER_ARCHITECTURE.md) |",
        "| Simulation state / mission taxonomy | [`.aurora/SIMULATION_STATE.json`]"
        "(../.aurora/SIMULATION_STATE.json) |",
        "| Canonical roster | [`L1_CANON_CHARACTER_ROSTER.md`](L1_CANON_CHARACTER_ROSTER.md) |",
        "| Crew manifest (generated) | [`.aurora/ORION_STATION_CREW_MANIFEST.md`]"
        "(../.aurora/ORION_STATION_CREW_MANIFEST.md) |",
        "",
    ]


def _indexing_notes() -> List[str]:
    return [
        "## Notes recorded while indexing",
        "",
        "These are observations from the registers themselves, not judgements about",
        "the work:",
        "",
        "- **QGIA postdates every phase.** The `QGIA_Integration/` package is not",
        "  accounted for in any phase register, so the phase sequence is not a",
        "  complete picture of the simulation layer's integrations.",
        '- **Phases 4 and 5 record `git_commit_status: "Pending"`** in their',
        "  registers, although both are committed. The field was never updated after",
        "  the commit landed; it reflects the state at authoring time, not now.",
        "- **Phases 4 and 5 both note a character-count discrepancy** (32 loaded vs",
        "  33 total human staff; 35 vs 36), attributed in-register to parsing rather",
        "  than to missing characters. Unresolved in both.",
        "- **Phase 6 has no `integration_date`** and no division summary; it records",
        "  L2/L3 systems rather than a staffed division.",
        "",
        "The Phase 6 terminology audit against `LAYER_ARCHITECTURE.md` that #1133",
        "also asks for is *not* done here — it is a canon-consistency review rather",
        "than an indexing task.",
        "",
    ]


def render(phases: List[Dict[str, Any]]) -> str:
    header = [
        "# CODEX Phase Index",
        "",
        "<!-- GENERATED FILE — do not edit by hand.",
        "     Regenerate: python scripts/generate_codex_index.py",
        "     Source: simulation/CODEX_PHASE*_TECHNICAL_REGISTER.json -->",
        "",
        "Index of the CODEX character-integration phases. Each phase ships a pair:",
        "a `*_COMPLETE.md` narrative record and a `*_TECHNICAL_REGISTER.json`",
        "machine-readable register. Created for #1133.",
        "",
    ]
    return "\n".join(
        header + _phase_table(phases) + _related_documents() + _indexing_notes()
    )


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
