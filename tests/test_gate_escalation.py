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
import sys
from datetime import date
from pathlib import Path

import ops.work_queue.sync_queue as sync_queue
from ops.work_queue.escalate_gates import (
    apply_surfacing,
    find_escalations,
    find_integrity_holds,
    find_ungated_decisions,
)
from ops.work_queue.sync_queue import (
    find_gate_coherence_errors,
    render_open_gates_md,
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
    return {
        "registry_authority": "Aurora",
        "last_updated": "2026-07-01",
        "gates": [gate],
    }


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
    assert find_integrity_holds(held) == [
        {
            "gate_id": "GATE-777",
            "title": "Test gate",
            "integrity_status": "reconciliation_required",
            "integrity_note": "Linked issue is closed.",
            "github_issue": 777,
            "queue_item": "Q-0777",
        }
    ]

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
            {
                "id": "sim/decision-x",
                "title": "Needs a call",
                "status": "needs-decision",
            },
            {
                "id": "Q-0777-linked",
                "title": "Gated",
                "status": "needs-decision",
                "github_issue": 777,
            },
            {"id": "ops/normal", "title": "Just open", "status": "open"},
        ]
    }
    drift = find_ungated_decisions(queue, _registry())
    assert [d["id"] for d in drift] == ["sim/decision-x"]


def test_null_gate_refs_do_not_mask_unlinked_decisions():
    registry = _registry(queue_item="sim/known", github_issue=None)
    queue = {
        "active": [
            {
                "id": "sim/unlinked",
                "title": "No issue yet",
                "status": "needs-decision",
            }
        ]
    }

    drift = find_ungated_decisions(queue, registry)
    assert [item["id"] for item in drift] == ["sim/unlinked"]


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


def _projection_queue(*items, completed=None):
    return {
        "_meta": {"last_aurora_review": "2026-07-16T00:36:36Z"},
        "active": list(items),
        "completed": list(completed or []),
    }


def _projection_registry(*gates):
    return {
        "last_updated": "2026-08-03",
        "gates": list(gates),
    }


def _projection_gate(**overrides):
    gate = {
        "gate_id": "GATE-900",
        "queue_item": "Q-0900",
        "github_issue": 900,
        "title": "Projection test gate",
        "state": "open",
        "integrity_status": "active",
        "decision_owner": "operator",
        "closed": None,
        "resolved_by": None,
    }
    gate.update(overrides)
    return gate


def _projection_queue_gate(**overrides):
    item = {
        "id": "Q-0900",
        "title": "Projection test queue item",
        "status": "needs-decision",
        "tags": ["gate"],
        "depends_on": [],
    }
    item.update(overrides)
    return item


def test_gate_projection_uses_registry_authority_and_source_dates():
    queue = _projection_queue(_projection_queue_gate())
    registry = _projection_registry(_projection_gate())

    assert find_gate_coherence_errors(queue, registry) == []
    rendered = render_open_gates_md(queue, registry)

    assert "GATE-900" in rendered
    assert "`active`" in rendered
    assert "Queue review: `2026-07-16T00:36:36Z`" in rendered
    assert "Gate registry updated: `2026-08-03`" in rendered


def test_registry_only_reconciliation_hold_is_visible_and_nonblocking():
    gate = _projection_gate(
        queue_item="Q-missing",
        integrity_status="reconciliation_required",
        integrity_note="Historical queue item is absent; operator review required.",
    )
    queue = _projection_queue()
    registry = _projection_registry(gate)

    assert find_gate_coherence_errors(queue, registry) == []
    rendered = render_open_gates_md(queue, registry)

    assert "GATE-900" in rendered
    assert "`reconciliation_required`" in rendered
    assert "`Q-missing` — missing from queue.json" in rendered
    assert "Historical queue item is absent" in rendered


def test_reconciliation_hold_requires_an_integrity_note():
    registry = _projection_registry(
        _projection_gate(
            queue_item="Q-missing",
            integrity_status="reconciliation_required",
            integrity_note=" ",
        )
    )

    errors = find_gate_coherence_errors(_projection_queue(), registry)

    assert errors == ["GATE-900 requires reconciliation but has no integrity_note"]


def test_missing_active_registry_queue_item_is_a_coherence_error():
    registry = _projection_registry(_projection_gate(queue_item="Q-missing"))

    errors = find_gate_coherence_errors(_projection_queue(), registry)

    assert any("missing queue item Q-missing" in error for error in errors)


def test_queue_gate_without_registry_record_is_a_coherence_error():
    queue = _projection_queue(_projection_queue_gate())

    errors = find_gate_coherence_errors(queue, _projection_registry())

    assert errors == ["queue gate Q-0900 has no canonical gate_registry.json record"]


def test_decision_required_state_without_registry_record_is_a_coherence_error():
    queue = _projection_queue(
        _projection_queue_gate(status=None, state="decision_required", tags=[])
    )

    errors = find_gate_coherence_errors(queue, _projection_registry())

    assert errors == ["queue gate Q-0900 has no canonical gate_registry.json record"]


def test_decision_required_state_matches_open_registry_gate():
    queue = _projection_queue(
        _projection_queue_gate(status=None, state="decision_required", tags=[])
    )
    registry = _projection_registry(_projection_gate())

    assert find_gate_coherence_errors(queue, registry) == []


def test_state_gate_marker_is_not_masked_by_legacy_status():
    queue = _projection_queue(
        _projection_queue_gate(status="open", state="decision_required", tags=[])
    )

    errors = find_gate_coherence_errors(queue, _projection_registry())

    assert errors == ["queue gate Q-0900 has no canonical gate_registry.json record"]


def test_state_gate_marker_takes_precedence_for_open_registry_gate():
    queue = _projection_queue(
        _projection_queue_gate(status="open", state="decision_required", tags=[])
    )
    registry = _projection_registry(_projection_gate())

    assert find_gate_coherence_errors(queue, registry) == []
    rendered = render_open_gates_md(queue, registry)
    assert "`decision_required`" in rendered


def test_open_registry_gate_rejects_non_decision_queue_status():
    queue = _projection_queue(_projection_queue_gate(status="open", tags=[]))
    registry = _projection_registry(_projection_gate())

    errors = find_gate_coherence_errors(queue, registry)

    assert errors == [
        "GATE-900 is open while queue item Q-0900 has non-decision status open"
    ]


def test_duplicate_queue_item_id_is_a_coherence_error():
    queue = _projection_queue(
        _projection_queue_gate(),
        completed=[_projection_queue_gate(status="done")],
    )
    registry = _projection_registry(_projection_gate())

    errors = find_gate_coherence_errors(queue, registry)

    assert errors == ["duplicate queue item id Q-0900 appears in active, completed"]


def test_completed_queue_gate_without_registry_record_is_a_coherence_error():
    queue = _projection_queue(completed=[_projection_queue_gate(status="done")])

    errors = find_gate_coherence_errors(queue, _projection_registry())

    assert errors == ["queue gate Q-0900 has no canonical gate_registry.json record"]


def test_matching_issue_number_does_not_mask_queue_item_mismatch():
    queue = _projection_queue(_projection_queue_gate(id="Q-other", github_issue=900))
    registry = _projection_registry(
        _projection_gate(
            queue_item="Q-missing",
            integrity_status="reconciliation_required",
            integrity_note="Historical item is absent.",
        )
    )

    errors = find_gate_coherence_errors(queue, registry)

    assert errors == ["queue gate Q-other has no canonical gate_registry.json record"]


def test_resolved_registry_gate_cannot_leave_queue_decision_open():
    queue = _projection_queue(_projection_queue_gate())
    registry = _projection_registry(
        _projection_gate(
            state="resolved",
            closed="2026-08-03",
            resolved_by="operator",
        )
    )

    errors = find_gate_coherence_errors(queue, registry)

    assert any("resolved while queue item Q-0900" in error for error in errors)
    assert any("Q-0900 remains needs-decision" in error for error in errors)


def test_resolved_gate_with_done_queue_item_is_not_rendered_open():
    queue = _projection_queue(_projection_queue_gate(status="done"))
    registry = _projection_registry(
        _projection_gate(
            state="resolved",
            closed="2026-08-03",
            resolved_by="operator",
        )
    )

    assert find_gate_coherence_errors(queue, registry) == []
    rendered = render_open_gates_md(queue, registry)
    assert "GATE-900" not in rendered


def test_open_gate_cannot_reference_completed_queue_item():
    queue = _projection_queue(completed=[_projection_queue_gate(status="done")])
    registry = _projection_registry(_projection_gate())

    errors = find_gate_coherence_errors(queue, registry)

    assert errors == ["GATE-900 is open while queue item Q-0900 is done"]


def test_resolved_gate_can_reference_completed_queue_item():
    queue = _projection_queue(completed=[_projection_queue_gate(status="done")])
    registry = _projection_registry(
        _projection_gate(
            state="resolved",
            closed="2026-08-03",
            resolved_by="operator",
        )
    )

    assert find_gate_coherence_errors(queue, registry) == []


def test_check_mode_returns_nonzero_for_cross_source_divergence(monkeypatch):
    queue = _projection_queue(_projection_queue_gate())
    registry = _projection_registry()
    monkeypatch.setattr(sync_queue, "load_queue", lambda: queue)
    monkeypatch.setattr(sync_queue, "load_gate_registry", lambda: registry)
    monkeypatch.setattr(sys, "argv", ["sync_queue.py", "--check"])

    assert sync_queue.main() == 1


def test_live_registry_queue_and_projection_are_coherent():
    work_queue = Path(__file__).resolve().parent.parent / "ops" / "work_queue"
    registry = json.loads((work_queue / "gate_registry.json").read_text())
    queue = json.loads((work_queue / "queue.json").read_text())

    assert find_gate_coherence_errors(queue, registry) == []
    rendered = render_open_gates_md(queue, registry)
    for gate in registry["gates"]:
        if gate["state"] == "open":
            assert gate["gate_id"] in rendered
