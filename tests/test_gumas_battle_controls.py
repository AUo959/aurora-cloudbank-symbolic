"""Phase-11 controls harness, authority preflight, and doctrine-bridge tests.

Synthetic tests run everywhere. Tests marked with the pinned-CanonRec fixture
run only when ``GUMAS_CANONREC_ROOT`` names a checkout at the pinned commit.
No test here executes a full battle.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path

import pytest

from simulation.runtime.gumas_battle_controls import (
    CAPABILITY_CONTROLS,
    CAPABILITY_RUN0,
    Phase11Error,
    check_input_deltas,
    derive_documents,
    preflight,
    require,
    seal_authority,
)
from simulation.runtime.gumas_battle_controls.authority import expected_scope
from simulation.runtime.gumas_battle_controls.constants import (
    AUTHORITY_SCHEMA,
    PHASE11_CONTRACT_ID,
    VARIANT_CLASS,
    VARIANT_CONTROL,
    VARIANT_POLITY,
)
from simulation.runtime.gumas_battle_controls.identity import json_diff_paths
from simulation.runtime.gumas_battle_orchestrator import (
    Phase9Error,
    authority_doctrine_binding,
    execute_macrostep,
    initialize_run_context,
)
from simulation.runtime.gumas_command_policy.coefficients import DOCTRINE_KEYS
from simulation.runtime.gumas_command_policy.policy import apply_doctrine, decide, normalize_doctrine
from simulation.runtime.gumas_damage_disposition.normalization import normalize_phase6_receipt

import tests.test_gumas_battle_orchestrator as phase9_fixture

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
NEUTRAL = {key: 500 for key in DOCTRINE_KEYS}


def _authority(**overrides):
    record = {
        "schema": AUTHORITY_SCHEMA,
        "authority_id": "AUTH-test",
        "phase11_contract_id": PHASE11_CONTRACT_ID,
        "granted_by": {"owner": "test-owner"},
        "granted_on": "2026-11-01",
        "expires_on": "2026-12-31",
        "evidence": [{"kind": "test_fixture"}],
        "capabilities": [CAPABILITY_CONTROLS, CAPABILITY_RUN0],
        "scope": expected_scope(),
        "canon_promotion_authorized": False,
        "publication_authorized": False,
    }
    record.update(overrides)
    return seal_authority(record)


# --------------------------------------------------------------------------
# Authority preflight


def test_valid_authority_grants_each_capability():
    authority = _authority()
    for capability in (CAPABILITY_CONTROLS, CAPABILITY_RUN0):
        result = preflight(authority, capability, "2026-11-28")
        assert result["authorized"] is True
        assert result["authority_sha256"] == authority["authority_sha256"]


@pytest.mark.parametrize(
    ("authority", "capability", "as_of", "reason"),
    [
        (None, CAPABILITY_RUN0, "2026-11-28", "absent"),
        (_authority(), CAPABILITY_RUN0, "2027-01-01", "expired"),
        (_authority(), CAPABILITY_RUN0, "2026-10-31", "not yet in effect"),
        (_authority(capabilities=[CAPABILITY_CONTROLS]), CAPABILITY_RUN0, "2026-11-28", "lacks capability"),
        (_authority(capabilities=[CAPABILITY_RUN0]), CAPABILITY_CONTROLS, "2026-11-28", "lacks capability"),
        (_authority(scope={**expected_scope(), "baseline_version": "9.9"}), CAPABILITY_RUN0, "2026-11-28", "scope"),
        (_authority(canon_promotion_authorized=True), CAPABILITY_RUN0, "2026-11-28", "canon promotion"),
        (_authority(evidence=[]), CAPABILITY_RUN0, "2026-11-28", "owner evidence"),
        (_authority(), "run_anything", "2026-11-28", "unknown capability"),
        (_authority(), CAPABILITY_RUN0, "not-a-date", "ISO date"),
    ],
)
def test_preflight_refuses_and_discloses_nothing(authority, capability, as_of, reason):
    result = preflight(authority, capability, as_of)
    assert result["authorized"] is False
    refusal = result["refusal"]
    assert reason in refusal["reason"]
    assert refusal["refused"] is True
    assert refusal["macrosteps_executed"] == 0
    assert refusal["outcome_disclosed"] is False
    assert refusal["run0_executed"] is False
    with pytest.raises(Phase11Error):
        require(authority, capability, as_of)


def test_tampered_authority_is_refused():
    authority = _authority()
    authority["expires_on"] = "2099-01-01"
    result = preflight(authority, CAPABILITY_RUN0, "2026-11-28")
    assert result["authorized"] is False
    assert "hash mismatch" in result["refusal"]["reason"]


def test_control_and_run0_capabilities_are_separate():
    controls_only = _authority(capabilities=[CAPABILITY_CONTROLS])
    assert preflight(controls_only, CAPABILITY_CONTROLS, "2026-11-28")["authorized"] is True
    assert preflight(controls_only, CAPABILITY_RUN0, "2026-11-28")["authorized"] is False


# --------------------------------------------------------------------------
# Allowed / forbidden input deltas


def _documents(variant):
    baseline, calibration, source_set = derive_documents(variant)
    return {"baseline": baseline, "calibration": calibration, "source_set": source_set}


def test_control_variant_has_no_input_delta():
    assert check_input_deltas(VARIANT_CONTROL, _documents(VARIANT_CONTROL)) == {
        "baseline": [],
        "calibration": [],
        "source_set": [],
    }


def test_class_substitution_changes_only_declared_paths():
    observed = check_input_deltas(VARIANT_CLASS, _documents(VARIANT_CLASS))
    assert observed["source_set"] == []
    assert all(path.startswith("/fleet_template/composition") for path in observed["baseline"])
    assert observed["calibration"] == ["/identity_mapping/baseline_class_to_canonrec/CLASS-BASTION-01"]
    composition = _documents(VARIANT_CLASS)["baseline"]["fleet_template"]["composition"]
    assert sum(int(item["count"]) for item in composition) == 19


def test_polity_substitution_changes_only_declared_paths():
    observed = check_input_deltas(VARIANT_POLITY, _documents(VARIANT_POLITY))
    assert observed["baseline"] == []
    assert observed["calibration"] == ["/identity_mapping/organization_id"]
    assert all(path.startswith("/sources") for path in observed["source_set"])


@pytest.mark.parametrize("variant", [VARIANT_CONTROL, VARIANT_CLASS, VARIANT_POLITY])
def test_forbidden_input_delta_fails_closed(variant):
    documents = _documents(variant)
    documents["baseline"]["determinism"]["seed_u64"] = 1
    with pytest.raises(Phase11Error, match="forbidden"):
        check_input_deltas(variant, documents)


def test_substitution_without_effect_fails_closed():
    unchanged = _documents(VARIANT_CONTROL)
    with pytest.raises(Phase11Error, match="no input delta"):
        check_input_deltas(VARIANT_CLASS, unchanged)


def test_json_diff_paths_reports_leaf_paths():
    assert json_diff_paths({"a": {"b": 1, "c": 2}}, {"a": {"b": 1, "c": 3}, "d": 0}) == ["/a/c", "/d"]


def test_engine_sources_do_not_special_case_variants():
    tokens = ("class_substitution", "polity_substitution", "cls_bastion", "org_union_naval_forces", "loyalist")
    engine_dirs = (
        "gumas_command_policy",
        "gumas_movement_geometry",
        "gumas_sensing_weapons",
        "gumas_damage_disposition",
        "gumas_morale_resolution",
        "gumas_battle_orchestrator",
        "gumas_factual_reporter",
    )
    for directory in engine_dirs:
        for path in sorted((ROOT / "simulation/runtime" / directory).glob("*.py")):
            if path.name.endswith("_smoke.py") or path.name == "test_support.py":
                continue
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                assert token not in text, f"{path.name} special-cases {token}"


# --------------------------------------------------------------------------
# Phase-4 authority-doctrine bridge


def _team():
    return phase9_fixture._baseline()["sides"]["loyalist"]["command_team"]


def _decide(doctrine=None):
    return decide(
        _team(),
        {},
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity={"baseline_id": "x", "baseline_version": "1"},
        doctrine=doctrine,
    )


def test_neutral_doctrine_leaves_commander_and_orders_unchanged():
    plain, neutral = _decide(), _decide(NEUTRAL)
    assert "authority_doctrine" not in plain
    assert neutral["authority_doctrine"]["commander_attribute_deltas_q1000"] == {
        key: 0 for key in neutral["authority_doctrine"]["commander_attribute_deltas_q1000"]
    }
    assert neutral["orders"] == plain["orders"]
    assert neutral["command_team_numeric"] == plain["command_team_numeric"]


def test_doctrine_conditions_commander_and_is_recorded():
    aggressive = {**NEUTRAL, "aggression": 800, "risk_tolerance": 800}
    receipt = _decide(aggressive)
    block = receipt["authority_doctrine"]
    commander = receipt["command_team_numeric"]["commander"]["attributes_q1000"]
    assert commander["aggression"] == block["unconditioned_commander_q1000"]["aggression"] + 300
    assert commander["casualty_aversion"] < block["unconditioned_commander_q1000"]["casualty_aversion"]
    assert block["doctrine_q1000"] == aggressive
    assert receipt == _decide(dict(reversed(list(aggressive.items()))))


def test_doctrine_is_clamped_and_validated():
    extreme = {key: 1000 for key in DOCTRINE_KEYS}
    fields = _decide()["command_team_numeric"]["commander"]["attributes_q1000"]
    adjusted, _ = apply_doctrine({k: 990 for k in fields}, extreme)
    assert all(0 <= value <= 1000 for value in adjusted.values())
    with pytest.raises(ValueError):
        normalize_doctrine({**NEUTRAL, "extra": 1})
    with pytest.raises(TypeError):
        normalize_doctrine({**NEUTRAL, "aggression": 0.5})
    with pytest.raises(ValueError):
        normalize_doctrine({**NEUTRAL, "aggression": 1001})


# --------------------------------------------------------------------------
# Phase-9 continuation regression and doctrine binding


def _close_range_run(monkeypatch):
    original = phase9_fixture._t0_vessel

    def close(index, side, fleet):
        vessel = original(index, side, fleet)
        sign = -1 if side == "loyalist" else 1
        vessel["position_m"] = [sign * 700_000, index * 10_000, 2_000_000]
        return vessel

    monkeypatch.setattr(phase9_fixture, "_t0_vessel", close)
    return phase9_fixture._synthetic_run()


def test_second_macrostep_accepts_semantic_normalized_phase6_identity(monkeypatch):
    baseline, _, state, context = _close_range_run(monkeypatch)
    first = execute_macrostep(state, baseline, context)
    raw = first["phase6_receipt"]
    normalized = normalize_phase6_receipt(raw)["phase6_receipt_sha256"]
    # The regression only bites when list order makes the two identities differ.
    assert raw["phase6_receipt_sha256"] != normalized
    assert first["committed_state"]["last_phase6_receipt_sha256"] == normalized
    second = execute_macrostep(first["committed_state"], baseline, context, first["checkpoint"])
    third = execute_macrostep(second["committed_state"], baseline, context, second["checkpoint"])
    assert third["ledger_entry"]["macrostep_index"] == 3
    assert third["ledger_entry"]["previous_ledger_entry_sha256"] == second["ledger_entry"]["ledger_entry_sha256"]


def test_prior_phase7_binding_to_normalized_phase6_is_checked(monkeypatch):
    baseline, _, state, context = _close_range_run(monkeypatch)
    first = execute_macrostep(state, baseline, context)
    checkpoint = copy.deepcopy(first["checkpoint"])
    checkpoint["phase7_receipt"]["phase6_receipt_sha256"] = "0" * 64
    checkpoint["phase7_receipt"]["phase7_receipt_sha256"] = phase9_fixture.hash_without_field(
        checkpoint["phase7_receipt"], "phase7_receipt_sha256"
    )
    with pytest.raises(Phase9Error):
        execute_macrostep(first["committed_state"], baseline, context, checkpoint)


def _binding(authority_id="synthetic-organization", doctrine=None):
    return {
        "authority_id": authority_id,
        "authority_resolution_sha256": "a" * 64,
        "manifest_sha256": "b" * 64,
        "doctrine_q1000": dict(doctrine or NEUTRAL),
    }


def test_run_context_binds_doctrine_and_phase4_consumes_it():
    baseline, t0, state, _ = phase9_fixture._synthetic_run()
    bindings = {side: _binding(doctrine={**NEUTRAL, "aggression": 800}) for side in baseline["sides"]}
    context = initialize_run_context(t0, state, baseline, authority_doctrine_by_side=bindings)
    plain = initialize_run_context(t0, state, baseline)
    assert context["run_identity_sha256"] != plain["run_identity_sha256"]
    result = execute_macrostep(state, baseline, context)
    for decision in result["decisions_by_fleet"].values():
        assert decision["authority_doctrine"]["doctrine_q1000"]["aggression"] == 800


@pytest.mark.parametrize(
    "mutate",
    [
        lambda b: b.pop("rebel"),
        lambda b: b["rebel"].update(authority_id="other-organization"),
        lambda b: b["rebel"]["doctrine_q1000"].update(aggression=2000),
        lambda b: b["rebel"].update(extra=1),
    ],
)
def test_invalid_doctrine_binding_fails_closed(mutate):
    baseline, t0, state, _ = phase9_fixture._synthetic_run()
    bindings = {side: _binding() for side in baseline["sides"]}
    mutate(bindings)
    with pytest.raises(Phase9Error):
        initialize_run_context(t0, state, baseline, authority_doctrine_by_side=bindings)


def test_authority_doctrine_binding_requires_resolved_authority():
    with pytest.raises(Phase9Error):
        authority_doctrine_binding({"manifest_sha256": "c" * 64})


# --------------------------------------------------------------------------
# Real pinned CanonRec (input resolution only; no battle executes)

CANONREC_ROOT = os.environ.get("GUMAS_CANONREC_ROOT")
needs_canonrec = pytest.mark.skipif(not CANONREC_ROOT, reason="GUMAS_CANONREC_ROOT not set")


@needs_canonrec
def test_real_variants_resolve_with_declared_deltas_only():
    from simulation.runtime.gumas_battle_controls import resolve_inputs
    from simulation.runtime.gumas_acceptance_fixture import EXPECTED_T0_SHA256

    control = resolve_inputs(Path(CANONREC_ROOT), VARIANT_CONTROL)
    klass = resolve_inputs(Path(CANONREC_ROOT), VARIANT_CLASS)
    polity = resolve_inputs(Path(CANONREC_ROOT), VARIANT_POLITY)
    assert control.t0["t0_sha256"] == EXPECTED_T0_SHA256
    assert len({control.t0["t0_sha256"], klass.t0["t0_sha256"], polity.t0["t0_sha256"]}) == 3
    assert klass.manifest["authority"] == control.manifest["authority"]
    assert polity.manifest["authority"]["authority_id"] == "org_union_naval_forces"
    control_roster = {e["class_id"]: e for e in control.manifest["roster"]}
    for entry in polity.manifest["roster"]:
        expected = control_roster[entry["class_id"]]["resolved"]["capability_vector"]
        assert entry["resolved"]["capability_vector"] == expected
    assert (
        polity.run_context["authority_doctrine_by_side"]
        != control.run_context["authority_doctrine_by_side"]
    )
    assert {e["class_id"]: e["count"] for e in klass.manifest["roster"]}["cls_bastion"] == 1
