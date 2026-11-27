from copy import deepcopy

import pytest

from modules.qgia import canon_bridge as bridge


@pytest.fixture
def artifacts():
    blobs = {}
    origin = {"repository": "Fixture/Ledger", "commit": "a" * 40}

    def pin(name, payload, layer="L1"):
        content = bridge._canonical(payload)
        blobs[name] = content
        return bridge.Artifact(**origin, path=name, layer=layer, sha256=bridge.hashlib.sha256(content).hexdigest())

    def read(reference):
        return blobs[reference.path]

    return pin, read, blobs, origin


def approved(artifacts, *, decision="approved", axiom_state="clear", ethics_state="clear", replace_forecast=False):
    pin, _, _, origin = artifacts
    evidence = pin("inputs/evidence.json", {"observations": ["Thermal readings are sparse"]})
    prior = pin("inputs/prior.json", {"table": "baseline-1"})
    source = pin("forecast.json", {
        "version": "1.0", "source_system": "QGIA", "source_actor": "forecast-operator",
        "as_of": "2026-07-18T09:00:00Z", "question": "Will the fictional habitat retain service?",
        "horizon": "ten cycles", "region": "Training world", "domain": "maintenance",
        "forecast": {
            "forecast_id": "fixture-forecast", "scenario_id": "habitat-exercise", "timestamp": "2026-07-18T09:00:00Z",
            "tier_assessments": [{
                "tier": 1, "label": "baseline", "scenario_variant": "limited downtime", "probability": 0.6,
                "confidence": 0.7, "confidence_components": {}, "reasoning_chain": [],
                "dissent_count": 0, "key_dissenters": [],
            }],
            "provenance": {}, "echo_chamber_warnings": [], "analyst_participation": {}, "meta": {},
        },
        "calibration": {"window": "fixture only"}, "model": "qsfe-fixture-1",
        "priors": [prior.model_dump()], "evidence": [evidence.model_dump()],
        "unknowns": ["Duration of the sensor outage"], "assumptions": ["The maintenance schedule holds"],
        "axiom_state": axiom_state,
    })
    bound = source.model_copy(update={"sha256": "d" * 64}) if replace_forecast else source
    review = pin("approval.json", {
        "version": "1.0", "decision": decision, "scope": "L2:scenario_seed", "authority": "reviewer",
        "relay_id": "review-relay", "reviewed_at": "2026-07-18T09:10:00Z", "forecast": bound.model_dump(),
        "selected_tiers": [1], "translation_notes": "Translate to the supported fixture for a sensitivity review",
        "constraints": ["Observe aggregate outcomes"], "excluded_interpretations": ["No prediction of real events"],
        "ethics_state": ethics_state,
        "parameters": {"scenario_id": "gumas_canonical_v1", "seed": 42, "turns": 5, "fabric_domain": "union"},
        "engine": {"version": "4.0.0-synth", "commit": "b" * 40},
    })
    policy = bridge.Policy(
        version="1.0", forecast_origins=[origin], mediation_origins=[origin], approvers=["reviewer"],
        relays=["review-relay"], engine_commit="b" * 40,
        current_forecasts={"fixture-forecast": source.sha256},
        gate_origins={gate: [origin] for gate in bridge.REQUIRED_GATES},
    )
    return source, review, policy


def test_mediated_forecast_emits_stable_staging_request_with_evidence(artifacts):
    pin, read, _, _ = artifacts
    source, review, policy = approved(artifacts)
    material = bridge.prepare_material(source, review, policy, read)
    assert material == bridge.prepare_material(source, review, policy, read)
    forecast = material["mediation_evidence"]["forecast"]
    assert forecast["unknowns"] == ["Duration of the sensor outage"]
    assert forecast["assumptions"] == ["The maintenance schedule holds"]
    assert material["mediation_evidence"]["certainty"] == "STAGING"
    seed = pin("staging/seed.json", material["scenario_seed"], layer="L2")
    evidence = pin("staging/evidence.json", material["mediation_evidence"], layer="L2")
    subject = bridge.request_subject(material, seed, evidence, read)
    receipts = {}
    for gate in bridge.REQUIRED_GATES:
        payload = {"receipt_id": gate, "gate": gate, "verdict": "PASS", "subject_sha256": bridge._digest(subject)}
        if gate == "authorization_approval":
            payload.update(decision="approved", authority="reviewer")
        if gate == "final_reconciliation":
            payload["recommendation"] = "STAGING"
        ref = {"receipt_id": gate, "artifact": pin(f"gates/{gate}.json", payload, layer="L2").model_dump()}
        receipts[gate] = {"receipt": ref} if gate == "naming" else ref
    request = bridge.finalize_request(subject, receipts, policy, read)
    assert request == bridge.finalize_request(subject, receipts, policy, read)
    assert request["operation"] == "create_staging_claim"
    assert request["execution_mode"] == "reference"
    assert request["submitter"]["relay_id"] == "review-relay"
    assert request["content_hash"] == bridge._digest({**subject, "gate_receipts": receipts})
    with pytest.raises(bridge.BridgeError, match="only create L2 staging"):
        bridge.finalize_request({**subject, "operation": "request_promotion_review"}, receipts, policy, read)
    corrupt = deepcopy(receipts)
    corrupt["naming"]["receipt"]["receipt_id"] = "other-gate"
    with pytest.raises(bridge.BridgeError, match="does not approve the exact staging subject"):
        bridge.finalize_request(subject, corrupt, policy, read)


@pytest.mark.parametrize(("overrides", "reason"), [
    ({"decision": "pending"}, "mediation is pending"),
    ({"decision": "rejected"}, "mediation is rejected"),
    ({"decision": "partial"}, "mediation is partial"),
    ({"axiom_state": "hold"}, "ethics or axiom hold"),
    ({"ethics_state": "hold"}, "ethics or axiom hold"),
    ({"replace_forecast": True}, "different forecast or evidence hash"),
])
def test_incomplete_or_held_approval_cannot_prepare_a_seed(artifacts, overrides, reason):
    _, read, _, _ = artifacts
    source, review, policy = approved(artifacts, **overrides)
    with pytest.raises(bridge.BridgeError, match=reason):
        bridge.prepare_material(source, review, policy, read)


def test_superseded_forecast_and_altered_source_bytes_fail_closed(artifacts):
    _, read, blobs, _ = artifacts
    source, review, policy = approved(artifacts)
    stale = policy.model_copy(update={"current_forecasts": {}})
    with pytest.raises(bridge.BridgeError, match="superseded or unregistered"):
        bridge.prepare_material(source, review, stale, read)
    blobs["inputs/evidence.json"] += b" "
    with pytest.raises(bridge.BridgeError, match="Artifact digest mismatch"):
        bridge.prepare_material(source, review, policy, read)
