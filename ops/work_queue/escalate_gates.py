#!/usr/bin/env python3
"""escalate_gates.py — decision-gate escalation for the Aurora work queue.

Closes the final roadmap item of issue #1131 ("PAT hails"), per the L1
decision of 2026-07-17: escalation over transports that actually exist —
GitHub issue-comment pings (driven by the CI workflow) and optional
mesh-runtime dispatch where a live mesh exists — honestly renamed
decision-gate escalation. The original PAT-hail wording remains the
aspiration for when a hailing transport lands (the PAT overlay is
read-only today; see docs/api/api_surface_inventory.json).

Usage:
    python ops/work_queue/escalate_gates.py                  # report only
    python ops/work_queue/escalate_gates.py --apply          # bump last_surfaced
    python ops/work_queue/escalate_gates.py --json out.json  # machine output
    python ops/work_queue/escalate_gates.py --mesh           # + mesh dispatch

Semantics:
- A gate escalates when state == "open" and days since
  max(opened, last_surfaced) exceed the threshold (default 3, per #1131).
- Gates with integrity_status == "reconciliation_required" remain open
  authority records but are excluded from automated escalation until their
  stale issue/queue references are reconciled.
- Bumping last_surfaced (--apply) IS the dedup: a gate will not re-escalate
  until the threshold elapses again. escalation_tier is Aurora's field and
  is never modified here.
- Queue items in needs-decision state without a matching open gate are
  reported as registry drift (the gate registry's contract says every
  decision_required item gets a gate).
- Mesh dispatch is best-effort and only meaningful where the mesh store
  lives (operator machine / deployment); in CI the store is ephemeral, so
  the workflow relies on issue-comment pings instead.

Exit codes: 0 = nothing to escalate, 10 = escalations found (and applied,
with --apply), 1 = error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
GATE_REGISTRY = HERE / "gate_registry.json"
QUEUE_JSON = HERE / "queue.json"

DEFAULT_THRESHOLD_DAYS = 3
MESH_ESCALATION_TARGET = "aurora"


def _load(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _is_active_open_gate(gate: Dict[str, Any]) -> bool:
    """Whether a gate may participate in automated escalation and linking."""
    return (
        gate.get("state") == "open"
        and gate.get("integrity_status", "active") == "active"
    )


def find_integrity_holds(registry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Open gates intentionally suspended from automation pending reconciliation."""
    holds = []
    for gate in registry.get("gates", []):
        if gate.get("state") != "open":
            continue
        status = gate.get("integrity_status", "active")
        if status == "active":
            continue
        holds.append({
            "gate_id": gate.get("gate_id"),
            "title": gate.get("title"),
            "integrity_status": status,
            "integrity_note": gate.get("integrity_note"),
            "github_issue": gate.get("github_issue"),
            "queue_item": gate.get("queue_item"),
        })
    return holds


def find_escalations(
    registry: Dict[str, Any],
    threshold_days: int = DEFAULT_THRESHOLD_DAYS,
    today: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Open gates whose last surfacing is older than the threshold."""
    today = today or _today()
    escalations: List[Dict[str, Any]] = []
    for gate in registry.get("gates", []):
        if not _is_active_open_gate(gate):
            continue
        baseline_candidates = [
            _parse_date(gate.get("opened")),
            _parse_date(gate.get("last_surfaced")),
        ]
        baselines = [d for d in baseline_candidates if d is not None]
        if not baselines:
            # Undated open gate: always surface — silence must not hide it.
            age_days = None
        else:
            age_days = (today - max(baselines)).days
            if age_days <= threshold_days:
                continue
        escalations.append({
            "gate_id": gate.get("gate_id"),
            "title": gate.get("title"),
            "github_issue": gate.get("github_issue"),
            "decision_owner": gate.get("decision_owner"),
            "escalation_tier": gate.get("escalation_tier"),
            "opened": gate.get("opened"),
            "last_surfaced": gate.get("last_surfaced"),
            "days_since_surfaced": age_days,
            "blocks_queue_items": gate.get("blocks_queue_items", []),
        })
    return escalations


def _open_gate_refs(registry: Dict[str, Any]) -> tuple[set, set]:
    """(queue_item ids, github issue numbers) referenced by open gates."""
    open_gates = [g for g in registry.get("gates", []) if _is_active_open_gate(g)]
    gated_items = {
        gate["queue_item"] for gate in open_gates
        if gate.get("queue_item") is not None
    }
    gated_issues = {
        gate["github_issue"] for gate in open_gates
        if gate.get("github_issue") is not None
    }
    return gated_items, gated_issues


def _needs_decision(item: Dict[str, Any]) -> Optional[str]:
    status = item.get("status") or item.get("state")
    return status if status in ("needs-decision", "decision_required") else None


def find_ungated_decisions(
    queue: Dict[str, Any], registry: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """needs-decision queue items with no matching open gate (registry drift)."""
    gated_items, gated_issues = _open_gate_refs(registry)
    drift = []
    for item in queue.get("active", []):
        status = _needs_decision(item)
        if status is None:
            continue
        github_issue = item.get("github_issue")
        if (
            item.get("id") in gated_items
            or github_issue is not None and github_issue in gated_issues
        ):
            continue
        drift.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "github_issue": item.get("github_issue"),
            "status": status,
        })
    return drift


def apply_surfacing(
    registry: Dict[str, Any],
    escalations: List[Dict[str, Any]],
    today: Optional[date] = None,
) -> None:
    """Bump last_surfaced for escalated gates (the dedup mechanism)."""
    today_iso = (today or _today()).isoformat()
    escalated_ids = {e["gate_id"] for e in escalations}
    for gate in registry.get("gates", []):
        if gate.get("gate_id") in escalated_ids:
            gate["last_surfaced"] = today_iso
    registry["last_updated"] = today_iso


def dispatch_mesh(escalations: List[Dict[str, Any]]) -> bool:
    """Best-effort mesh notification; returns True only on confirmed dispatch."""
    try:
        from src.mesh.models import MeshMessageRequest
        from src.mesh.runtime import MeshRuntime

        runtime = MeshRuntime(HERE.parents[1])
        summary = "; ".join(
            f"{e['gate_id']} ({e['title']}, {e['days_since_surfaced'] if e['days_since_surfaced'] is not None else '?'}d)"
            for e in escalations
        )
        import asyncio

        result = asyncio.run(runtime.send_message(MeshMessageRequest(
            content=f"Decision-gate escalation: {len(escalations)} gate(s) awaiting "
                    f"operator decision beyond threshold — {summary}",
            to=MESH_ESCALATION_TARGET,
            sender_id="queue_escalation",
            sender_name="Queue Escalation",
            type="direct",
        )))
        return bool(result.get("success"))
    except Exception as exc:
        print(f"mesh dispatch unavailable ({exc}) — relying on issue pings", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--threshold-days", type=int, default=DEFAULT_THRESHOLD_DAYS)
    parser.add_argument("--apply", action="store_true",
                        help="Bump last_surfaced on escalated gates (writes registry)")
    parser.add_argument("--json", type=Path, default=None,
                        help="Write machine-readable escalation report to this path")
    parser.add_argument("--mesh", action="store_true",
                        help="Also attempt mesh-runtime dispatch (best-effort)")
    args = parser.parse_args()

    registry = _load(GATE_REGISTRY)
    queue = _load(QUEUE_JSON)

    escalations = find_escalations(registry, args.threshold_days)
    drift = find_ungated_decisions(queue, registry)
    integrity_holds = find_integrity_holds(registry)

    _print_findings(escalations, drift, integrity_holds)
    _write_report(args, escalations, drift, integrity_holds)

    if not escalations and not drift:
        if integrity_holds:
            print(
                "No gates past threshold; no registry drift; "
                f"{len(integrity_holds)} integrity hold(s) reported."
            )
        else:
            print("No gates past threshold; no registry drift.")
        return 0

    _finalize(args, registry, escalations)
    return 10


def _print_findings(
    escalations: List[Dict[str, Any]],
    drift: List[Dict[str, Any]],
    integrity_holds: List[Dict[str, Any]],
) -> None:
    for item in escalations:
        age = item["days_since_surfaced"]
        print(f"ESCALATE {item['gate_id']} (tier {item['escalation_tier']}, "
              f"{age if age is not None else 'undated'}d, issue #{item['github_issue']}): {item['title']}")
    for item in drift:
        print(f"DRIFT ungated needs-decision item: {item['id']} — {item['title']}")
    for gate in integrity_holds:
        print(
            f"HOLD {gate['gate_id']} ({gate['integrity_status']}): "
            f"{gate['integrity_note'] or gate['title']}"
        )


def _write_report(
    args,
    escalations: List[Dict[str, Any]],
    drift: List[Dict[str, Any]],
    integrity_holds: List[Dict[str, Any]],
) -> None:
    if not args.json:
        return
    report = {
        "generated": _today().isoformat(),
        "threshold_days": args.threshold_days,
        "escalations": escalations,
        "ungated_decisions": drift,
        "integrity_holds": integrity_holds,
    }
    args.json.write_text(json.dumps(report, indent=2) + "\n")


def _finalize(args, registry: Dict[str, Any], escalations: List[Dict[str, Any]]) -> None:
    if not escalations:
        return
    if args.mesh:
        dispatch_mesh(escalations)
    if args.apply:
        apply_surfacing(registry, escalations)
        GATE_REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")
        print(f"last_surfaced bumped for {len(escalations)} gate(s).")


if __name__ == "__main__":
    sys.exit(main())
