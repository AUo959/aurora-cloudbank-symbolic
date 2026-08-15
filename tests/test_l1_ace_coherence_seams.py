from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
if str(SIMULATION_DIR) not in sys.path:
    sys.path.insert(0, str(SIMULATION_DIR))

from l1_embodiment import (  # noqa: E402
    ACE_SEAM_CALLER_REF,
    ACE_SEAM_TRIGGER_POLICY_REF,
    assess_embodiment_readiness,
    build_ace_coherence_seams,
)


def _registry() -> dict[str, object]:
    return json.loads(
        (PROJECT_ROOT / "config" / "l1_embodiment_registry.json").read_text(
            encoding="utf-8"
        )
    )


@pytest.mark.unit
def test_mcp_canonical_location_gap_emits_autonomic_ace_seam() -> None:
    registry = _registry()

    seams = build_ace_coherence_seams(registry)

    assert len(seams) == 1
    seam = seams[0]
    assert seam["record_type"] == "ace_coherence_seam"
    assert seam["target_engine"] == "ACE"
    assert seam["invocation_mode"] == "autonomic"
    assert seam["caller"] == {
        "kind": "system",
        "caller_ref": ACE_SEAM_CALLER_REF,
    }
    assert seam["trigger"]["kind"] == "coherence_seam"
    assert seam["trigger"]["seam_ref"] == "L1-EMB-MCP-SHUTTLE-BAY:canonical_location"
    assert seam["trigger"]["trigger_policy_ref"] == ACE_SEAM_TRIGGER_POLICY_REF
    assert seam["query_kind"] == "facility_topology"
    assert seam["requested_output"] == "canonical_location"
    assert seam["subject"]["entity_type"] == "facility"
    assert seam["subject"]["subject_ref"] == "L1-EMB-MCP-SHUTTLE-BAY"
    assert seam["constraints"] == {
        "specialist_first": True,
        "inspectable": True,
        "activation_authority": False,
        "runtime_mutation_allowed": False,
        "canon_materialization_authority": False,
        "experiment_advance_allowed": False,
    }


@pytest.mark.unit
def test_seam_production_is_read_only_and_deterministic() -> None:
    registry = _registry()
    before = copy.deepcopy(registry)

    first = build_ace_coherence_seams(registry)
    second = build_ace_coherence_seams(registry)

    assert registry == before
    assert first == second


@pytest.mark.unit
def test_canonical_location_no_longer_emits_a_seam() -> None:
    registry = _registry()
    mcp = next(
        item
        for item in registry["embodiments"]
        if item["embodiment_id"] == "L1-EMB-MCP-SHUTTLE-BAY"
    )
    mcp["location"] = "Non-rotating core docking complex"
    mcp["location_certainty"] = "CANON"

    assert build_ace_coherence_seams(registry) == []


@pytest.mark.unit
def test_unsupported_authority_and_provider_gaps_are_not_silently_sent_to_ace() -> None:
    registry = _registry()
    mcp = next(
        item
        for item in registry["embodiments"]
        if item["embodiment_id"] == "L1-EMB-MCP-SHUTTLE-BAY"
    )
    mcp["blockers"].remove("canonical_location")

    assert build_ace_coherence_seams(registry) == []


@pytest.mark.unit
def test_preflight_readiness_surfaces_seams_without_changing_resume_authority() -> None:
    report = assess_embodiment_readiness(_registry())

    assert report["ready"] is False
    assert report["ace_coherence_seam_count"] == 1
    assert report["ace_coherence_seams"][0]["trigger"]["seam_ref"].endswith(
        ":canonical_location"
    )
