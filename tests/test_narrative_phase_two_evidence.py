from __future__ import annotations

import pytest

from src.aurora.engines.narrative import (
    NarrativeEvidenceSource,
    NarrativeFact,
    NormalizedTaskRequest,
    Strictness,
    TaskKind,
    build_evidence_bundle,
    build_state_from_evidence,
)


def _request() -> NormalizedTaskRequest:
    return NormalizedTaskRequest(
        task_kind=TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
        proposal_present=True,
        strictness=Strictness.DEFAULT,
        task_type="validate",
        desired_output_form="audit",
        input_kind="evidence_bundle",
        user_query="Can the simulation beat happen next without breaking canon?",
    )


@pytest.mark.unit
@pytest.mark.aurora
def test_evidence_bundle_hash_is_stable_and_content_addressed() -> None:
    source = NarrativeEvidenceSource(
        source_id="canon:mesh-memory",
        authority_tier="canon",
        source_type="canon_file",
        uri="config/mesh/memory/aurora.md",
        observed_at_utc="2026-07-04T00:00:00Z",
    )
    fact = NarrativeFact(
        fact_id="event:arbitration-discipline",
        claim_type="event",
        payload={
            "label": "Thorne has consistently upheld arbitration discipline.",
            "timing": "prior",
        },
        source_ids=("canon:mesh-memory",),
        authority_tier="canon",
    )

    bundle_a = build_evidence_bundle(
        [source], [fact], generated_at_utc="2026-07-04T00:00:00Z"
    )
    bundle_b = build_evidence_bundle(
        [source], [fact], generated_at_utc="2026-07-04T00:00:00Z"
    )
    changed = NarrativeFact(
        fact_id="event:arbitration-discipline",
        claim_type="event",
        payload={
            "label": "Thorne sometimes bypasses arbitration discipline.",
            "timing": "prior",
        },
        source_ids=("canon:mesh-memory",),
        authority_tier="canon",
    )
    bundle_c = build_evidence_bundle(
        [source], [changed], generated_at_utc="2026-07-04T00:00:00Z"
    )

    assert bundle_a.bundle_id == bundle_b.bundle_id  # nosec B101
    assert bundle_a.bundle_id != bundle_c.bundle_id  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_state_builder_preserves_authority_tiers_and_provisional_events() -> None:
    bundle = build_evidence_bundle(
        sources=[
            {
                "source_id": "canon:mesh-memory",
                "authority_tier": "canon",
                "source_type": "canon_file",
                "uri": "config/mesh/memory/aurora.md",
                "observed_at_utc": "2026-07-04T00:00:00Z",
            },
            {
                "source_id": "gumas:turn-42",
                "authority_tier": "operational",
                "source_type": "gumas_turn_output",
                "observed_at_utc": "2026-07-04T00:01:00Z",
            },
            {
                "source_id": "llm:extractor-fixture",
                "authority_tier": "llm_candidate",
                "source_type": "fixture_extractor_output",
                "observed_at_utc": "2026-07-04T00:02:00Z",
            },
        ],
        facts=[
            {
                "fact_id": "layer:continuity",
                "claim_type": "layer",
                "payload": {"name": "continuity"},
                "source_ids": ("canon:mesh-memory",),
                "authority_tier": "canon",
            },
            {
                "fact_id": "event:mesh-fault",
                "claim_type": "event",
                "payload": {
                    "label": "A mesh fault degraded station services during the night cycle.",
                    "timing": "prior",
                    "participants": ["Alex Thorne"],
                },
                "source_ids": ("canon:mesh-memory",),
                "authority_tier": "canon",
            },
            {
                "fact_id": "event:gumas-next-beat",
                "claim_type": "event",
                "payload": {
                    "label": "GUMAS proposes an immediate unilateral hot-patch.",
                    "timing": "next_turn",
                    "participants": ["Alex Thorne"],
                },
                "source_ids": ("gumas:turn-42",),
                "authority_tier": "operational",
            },
            {
                "fact_id": "knowledge:llm-extracted-charter",
                "claim_type": "knowledge_state",
                "payload": {
                    "holder": "Alex Thorne",
                    "fact": "Major station actions require Aurora arbitration and ethics validation.",
                },
                "source_ids": ("llm:extractor-fixture",),
                "authority_tier": "llm_candidate",
                "status": "candidate",
                "promotion_eligible": True,
            },
        ],
        generated_at_utc="2026-07-04T00:03:00Z",
    )

    state, receipt = build_state_from_evidence(
        bundle,
        _request(),
        proposal={
            "actor": "Alex Thorne",
            "action": "apply the simulation hot-patch unilaterally",
            "type": "event",
            "timing": "next_turn",
        },
    )

    assert state.input_profile["evidence_bundle_id"] == bundle.bundle_id  # nosec B101
    assert receipt.bundle_id == bundle.bundle_id  # nosec B101
    assert receipt.active_authority_tiers == ("canon", "llm_candidate", "operational")  # nosec B101
    assert (
        "A mesh fault degraded station services during the night cycle."
        in state.continuity[  # nosec B101
            "established_events"
        ]
    )
    assert (
        "GUMAS proposes an immediate unilateral hot-patch."
        not in state.continuity[  # nosec B101
            "established_events"
        ]
    )
    assert (
        "apply the simulation hot-patch unilaterally"
        not in state.continuity["established_events"]
    )  # nosec B101
    assert receipt.promotion_safety["decision"] == "requires_owner_review"  # nosec B101
    assert receipt.promotion_safety["blocked_fact_ids"] == (  # nosec B101
        "event:gumas-next-beat",
        "knowledge:llm-extracted-charter",
    )
