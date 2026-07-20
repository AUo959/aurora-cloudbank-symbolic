"""
Tests for ops/work_queue/escalate_gates.py — the final #1131 roadmap item
(decision-gate escalation, per the 2026-07-17 L1 decision).

Pure-function coverage, stdlib only, so queue-validation.yml can run this
with --noconftest alongside the other work-queue suites: aging math and
threshold boundary, the last_surfaced dedup contract, undated-gate
surfacing, ungated needs-decision drift detection, and apply semantics
(escalation_tier is Aurora's field and must never change here).
"""

import json
from datetime import date
from pathlib import Path

from ops.work_queue.escalate_gates import (
    apply_surfacing,
    find_escalations,
    find_integrity_holds,
    find_ungated_decisions,
)

TODAY = date(2026, 7, 18)


def _registry(**gate_overrides):
    gate = {
        "gate_id": "GATE-777",
        "queue_item": "Q-0777",
        "github_issue": 777,
        "title": "Test gate",
        "state": "open",
        "decision_owner": "operator",
        "opened": "2026-07-01",
        "last_surfaced": "2026-07-01",
        "escalation_tier": 1,
        "blocks_queue_items": ["Q-0778"],
    }
    gate.update(gate_overrides)
    return {"registry_authority": "Aurora", "last_updated": "2026-07-01", "gates": [gate]}


def test_aged_open_gate_escalates():
    escalations = find_escalations(_registry(), threshold_days=3, today=TODAY)
    assert len(escalations) == 1
    gate = escalations[0]
    assert gate["gate_id"] == "GATE-777"
    assert gate["days_since_surfaced"] == 17
    assert gate["github_issue"] == 777


def test_threshold_boundary_is_strictly_greater_than():
    # Surfaced exactly threshold days ago -> NOT escalated (age == threshold)
    at_threshold = _registry(last_surfaced="2026-07-15")
    assert find_escalations(at_threshold, threshold_days=3, today=TODAY) == []
    # One day older -> escalated
    past_threshold = _registry(last_surfaced="2026-07-14")
    assert len(find_escalations(past_threshold, threshold_days=3, today=TODAY)) == 1


def test_recently_surfaced_gate_is_deduped():
    fresh = _registry(last_surfaced="2026-07-17")
    assert find_escalations(fresh, threshold_days=3, today=TODAY) == []


def test_last_surfaced_wins_over_opened():
    """An old gate re-surfaced recently must not re-escalate."""
    resurfaced = _registry(opened="2026-06-01", last_surfaced="2026-07-16")
    assert find_escalations(resurfaced, threshold_days=3, today=TODAY) == []


def test_resolved_gates_never_escalate():
    resolved = _registry(state="resolved")
    assert find_escalations(resolved, threshold_days=3, today=TODAY) == []


def test_integrity_hold_suspends_escalation_and_link_authority():
    held = _registry(
        integrity_status="reconciliation_required",
        integrity_note="Linked issue is closed.",
    )
    assert find_escalations(held, threshold_days=3, today=TODAY) == []
    assert find_integrity_holds(held) == [{
        "gate_id": "GATE-777",
        "title": "Test gate",
        "integrity_status": "reconciliation_required",
        "integrity_note": "Linked issue is closed.",
        "github_issue": 777,
        "queue_item": "Q-0777",
    }]

    queue = {
        "active": [
            {
                "id": "Q-0777",
                "title": "Still needs a valid gate",
                "status": "needs-decision",
            }
        ]
    }
    assert [item["id"] for item in find_ungated_decisions(queue, held)] == ["Q-0777"]


def test_undated_open_gate_always_surfaces():
    """Silence must not hide an undated gate."""
    undated = _registry(opened=None, last_surfaced=None)
    escalations = find_escalations(undated, threshold_days=3, today=TODAY)
    assert len(escalations) == 1
    assert escalations[0]["days_since_surfaced"] is None


def test_apply_bumps_last_surfaced_but_never_tier():
    registry = _registry()
    escalations = find_escalations(registry, threshold_days=3, today=TODAY)
    apply_surfacing(registry, escalations, today=TODAY)

    gate = registry["gates"][0]
    assert gate["last_surfaced"] == "2026-07-18"
    assert gate["escalation_tier"] == 1, "escalation_tier is Aurora's field"
    assert registry["last_updated"] == "2026-07-18"
    # Post-bump, the same gate no longer escalates: dedup holds
    assert find_escalations(registry, threshold_days=3, today=TODAY) == []


def test_ungated_needs_decision_items_are_reported_as_drift():
    queue = {
        "active": [
            {"id": "sim/decision-x", "title": "Needs a call", "status": "needs-decision"},
            {"id": "Q-0777-linked", "title": "Gated", "status": "needs-decision",
             "github_issue": 777},
            {"id": "ops/normal", "title": "Just open", "status": "open"},
        ]
    }
    drift = find_ungated_decisions(queue, _registry())
    assert [d["id"] for d in drift] == ["sim/decision-x"]


def test_live_registry_and_queue_parse_and_report_cleanly():
    """The real files must be consumable by the escalation core."""
    work_queue = Path(__file__).resolve().parent.parent / "ops" / "work_queue"
    registry = json.loads((work_queue / "gate_registry.json").read_text())
    queue = json.loads((work_queue / "queue.json").read_text())

    escalations = find_escalations(registry, threshold_days=3, today=TODAY)
    drift = find_ungated_decisions(queue, registry)
    holds = find_integrity_holds(registry)
    # No exceptions and structurally sound output is the contract here;
    # actual counts are live data and will change over time.
    for gate in escalations:
        assert gate["gate_id"]
    for item in drift:
        assert item["id"]
    for gate in holds:
        assert gate["gate_id"]
        assert gate["integrity_status"] != "active"
