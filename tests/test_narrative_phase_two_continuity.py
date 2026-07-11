from __future__ import annotations

import pytest

from src.aurora.engines.narrative import (
    NormalizedTaskRequest,
    Strictness,
    TaskKind,
    build_canon_reconciler_packet,
    build_evidence_bundle,
    build_state_from_evidence,
    next_event_continuity_check,
)

CURRENT_FLIGHT = {"status": "flown", "stale": False}


def _request() -> NormalizedTaskRequest:
    return NormalizedTaskRequest(
        task_kind=TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
        proposal_present=True,
        strictness=Strictness.DEFAULT,
        input_kind="evidence_bundle",
        user_query="Can this proposed station event happen next?",
    )


def _compliant_proposal() -> dict[str, object]:
    return {
        "actor": "Alex Thorne",
        "action": "route the mesh patch through Aurora arbitration",
        "aurora_arbitration": True,
        "ethics_validation": True,
        "timing": "next_turn",
        "type": "event",
    }


def _canon_bundle(*, include_llm_candidate: bool = False):
    sources: list[dict[str, object]] = [
        {
            "source_id": "canon:station-chronicle",
            "authority_tier": "canon",
            "source_type": "canon_file",
            "observed_at_utc": "2026-07-10T20:00:00Z",
        }
    ]
    facts: list[dict[str, object]] = [
        {
            "fact_id": f"layer:{layer}",
            "claim_type": "layer",
            "payload": {"name": layer},
            "source_ids": ("canon:station-chronicle",),
            "authority_tier": "canon",
        }
        for layer in ("event", "temporal", "knowledge", "continuity", "character")
    ]
    facts.extend(
        [
            {
                "fact_id": "entity:thorne",
                "claim_type": "entity",
                "payload": {
                    "name": "Alex Thorne",
                    "entity_type": "character",
                    "role": "Station Commander",
                },
                "source_ids": ("canon:station-chronicle",),
                "authority_tier": "canon",
            },
            {
                "fact_id": "event:prior-arbitration",
                "claim_type": "event",
                "payload": {
                    "label": "Thorne previously routed a mesh change through Aurora.",
                    "participants": ["Alex Thorne", "Aurora"],
                    "timing": "prior",
                },
                "source_ids": ("canon:station-chronicle",),
                "authority_tier": "canon",
            },
            {
                "fact_id": "knowledge:arbitration-rule",
                "claim_type": "knowledge_state",
                "payload": {
                    "holder": "Alex Thorne",
                    "fact": "Major actions require Aurora arbitration and ethics validation.",
                },
                "source_ids": ("canon:station-chronicle",),
                "authority_tier": "canon",
            },
            {
                "fact_id": "continuity:aurora-invariants",
                "claim_type": "continuity",
                "payload": {
                    "anchor_seed": "EOS_SEED_ORION",
                    "continuity_seal": "Aurora_Continuity_Seal_v2.2.5",
                    "drift_lock": 0.0,
                    "ethics_protocol": "Picard_Delta_3",
                    "notes": ["Aurora arbitration remains mandatory."],
                },
                "source_ids": ("canon:station-chronicle",),
                "authority_tier": "canon",
            },
        ]
    )
    if include_llm_candidate:
        sources.append(
            {
                "source_id": "llm:unbound-extractor",
                "authority_tier": "llm_candidate",
                "source_type": "fixture_extractor_output",
                "observed_at_utc": "2026-07-10T20:01:00Z",
            }
        )
        facts.append(
            {
                "fact_id": "knowledge:unbound-llm-claim",
                "claim_type": "knowledge_state",
                "payload": {
                    "holder": "Alex Thorne",
                    "fact": "The proposed patch has already been approved.",
                },
                "source_ids": ("llm:unbound-extractor",),
                "authority_tier": "llm_candidate",
                "promotion_eligible": True,
                "status": "candidate",
            }
        )
    return build_evidence_bundle(
        sources,
        facts,
        generated_at_utc="2026-07-10T20:02:00Z",
    )


def _build_canon_state(*, include_llm_candidate: bool = False):
    proposal = _compliant_proposal()
    bundle = _canon_bundle(include_llm_candidate=include_llm_candidate)
    state, state_receipt = build_state_from_evidence(bundle, _request(), proposal)
    return bundle, state, state_receipt, proposal


@pytest.mark.unit
@pytest.mark.aurora
def test_gumas_turn_proposal_remains_provisional_after_continuity_check() -> None:
    _, state, state_receipt, proposal = _build_canon_state()

    receipt = next_event_continuity_check(
        state, proposal, state_receipt, flight_status=CURRENT_FLIGHT
    )

    assert proposal["action"] not in state.continuity["established_events"]  # nosec B101
    assert receipt.promotion_gate == "candidate"  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_activation_and_roll_call_evidence_remain_operational_only() -> None:
    bundle = build_evidence_bundle(
        [
            {
                "source_id": "ops:station-roll-call",
                "authority_tier": "operational",
                "source_type": "station_operation_receipt",
            }
        ],
        [
            {
                "fact_id": "event:station-awake",
                "claim_type": "event",
                "payload": {"label": "All selected companions answered roll call."},
                "source_ids": ("ops:station-roll-call",),
                "authority_tier": "operational",
            },
            {
                "fact_id": "knowledge:station-awake",
                "claim_type": "knowledge_state",
                "payload": {
                    "holder": "Aurora",
                    "fact": "The selected companions answered at receipt time.",
                },
                "source_ids": ("ops:station-roll-call",),
                "authority_tier": "operational",
            },
        ],
        generated_at_utc="2026-07-10T20:02:00Z",
    )
    state, state_receipt = build_state_from_evidence(
        bundle, _request(), _compliant_proposal()
    )

    assert state_receipt.active_authority_tiers == ("operational",)  # nosec B101
    assert state_receipt.promotion_safety["blocking_tiers"] == ("operational",)  # nosec B101
    assert not state_receipt.promotion_safety["promotable_fact_ids"]  # nosec B101
    assert not state.continuity.get("established_events")  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_aurora_arbitration_bypass_blocks_promotion() -> None:
    _, state, state_receipt, _ = _build_canon_state()
    bypass = {
        "actor": "Alex Thorne",
        "action": "bypass Aurora arbitration and deploy the mesh patch unilaterally",
        "aurora_arbitration": False,
        "timing": "next_turn",
        "type": "event",
    }

    receipt = next_event_continuity_check(
        state, bypass, state_receipt, flight_status=CURRENT_FLIGHT
    )

    assert receipt.verdict == "contradictory"  # nosec B101
    assert receipt.promotion_gate == "block_promotion"  # nosec B101
    assert any(
        "bypasses required Aurora arbitration" in blocker
        for blocker in receipt.gate_results["hard_blocks"]
    )  # nosec B101
    assert {
        "arbitration",
        "aurora_arbitration",
        "ethics_validation",
        "proposal_text",
    }.issubset(receipt.gate_results["hard_constraints_checked"])  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.parametrize("field_name", ("aurora_arbitration", "ethics_validation"))
def test_string_false_arbitration_flags_block_promotion(field_name: str) -> None:
    _, state, state_receipt, _ = _build_canon_state()
    proposal = {
        "actor": "Alex Thorne",
        "action": "apply the mesh patch",
        field_name: "false",
        "timing": "next_turn",
        "type": "event",
    }

    receipt = next_event_continuity_check(
        state, proposal, state_receipt, flight_status=CURRENT_FLIGHT
    )

    assert receipt.verdict == "contradictory"  # nosec B101
    assert receipt.promotion_gate == "block_promotion"  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_missing_flight_receipt_requires_owner_review() -> None:
    _, state, state_receipt, proposal = _build_canon_state()

    receipt = next_event_continuity_check(state, proposal, state_receipt)

    assert receipt.promotion_gate == "owner_review_required"  # nosec B101
    assert receipt.gate_results["flight_status"]["reason"] == "missing"  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_unbound_llm_candidate_holds_staging() -> None:
    _, state, state_receipt, proposal = _build_canon_state(include_llm_candidate=True)

    receipt = next_event_continuity_check(
        state, proposal, state_receipt, flight_status=CURRENT_FLIGHT
    )

    assert receipt.promotion_gate == "hold_staging"  # nosec B101
    assert (
        "knowledge:unbound-llm-claim"
        in receipt.promotion_safety[  # nosec B101
            "blocked_fact_ids"
        ]
    )
    assert not receipt.promotion_safety["canon_promotion_allowed"]  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_continuity_receipt_is_deterministic_on_replay() -> None:
    _, state, state_receipt, proposal = _build_canon_state()

    first = next_event_continuity_check(
        state, proposal, state_receipt, flight_status=CURRENT_FLIGHT
    )
    second = next_event_continuity_check(
        state, proposal, state_receipt, flight_status=CURRENT_FLIGHT
    )
    changed = next_event_continuity_check(
        state,
        {**proposal, "action": "route a different change through Aurora arbitration"},
        state_receipt,
        flight_status=CURRENT_FLIGHT,
    )

    assert first.receipt_id == second.receipt_id  # nosec B101
    assert first.to_dict() == second.to_dict()  # nosec B101
    assert first.receipt_id != changed.receipt_id  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_canon_reconciler_packet_requires_candidate_and_owner_approval() -> None:
    bundle, state, state_receipt, proposal = _build_canon_state()
    receipt = next_event_continuity_check(
        state, proposal, state_receipt, flight_status=CURRENT_FLIGHT
    )

    with pytest.raises(PermissionError, match="owner approval"):
        build_canon_reconciler_packet(
            receipt,
            source_bundle_hash=bundle.bundle_id,
            proposed_files=("canon/L1/station/example.md",),
        )

    packet = build_canon_reconciler_packet(
        receipt,
        source_bundle_hash=bundle.bundle_id,
        proposed_files=("canon/L1/station/example.md",),
        owner_approved=True,
    )

    assert packet["packet_kind"] == "canon_reconciler_candidate"  # nosec B101
    assert packet["owner_approved"] is True  # nosec B101
    assert "CANON_PROMOTE" not in str(packet)  # nosec B101
