"""Phase 3 tests: SII rupture classification, RQ-1 quarantine, sentinel, presig."""

import asyncio

from src.sensors.core.handshake import ExtendedZIPWIZHandshake, concept_hash
from src.sensors.core.reading_types import PreSignature
from src.sensors.core.sensor_base import utcnow
from src.sensors.observatory.symbolic import (
    Action,
    AgentOutput,
    ConceptResonanceDetector,
    DriftPreSignatureMonitor,
    EthicalSignalSentinel,
    SymbolIntegrationIndex,
)


def _presig(sig_type="hash_instability", magnitude=0.5, location="anchor_chain"):
    return PreSignature(
        signature_id="t1", signature_type=sig_type, magnitude=magnitude,
        location=location, first_detected=utcnow(), predicted_impact="test")


# -- Symbol Integration Index (success criterion 10) ---------------------------

def test_anchor_symbols_are_maximum_depth_by_construction():
    sii = SymbolIntegrationIndex()
    assert sii.depth("EOS_SEED_ORION") == 1.0
    assert sii.depth("Picard_Delta_3") == 1.0


def test_anchor_connection_loss_always_classifies_rupture():
    sii = SymbolIntegrationIndex()
    w = sii.weight_presignature(
        _presig(), symbol_id="EOS_SEED_ORION",
        connection_loss_rate_per_hour=0.11)
    assert w.classification == "rupture"
    assert w.priority == 0.5 * (0.3 + 0.7 * 1.0)


def test_periphery_isolated_is_noise_but_cluster_promotes_to_drift():
    sii = SymbolIntegrationIndex()
    sii.record_reference("lonely", "dep0")
    sii.record_reference("hub", "a")
    for i in range(20):
        sii.record_reference("hub", f"d{i}")
    isolated = sii.weight_presignature(_presig(), symbol_id="lonely",
                                       correlated_periphery_count=1)
    clustered = sii.weight_presignature(_presig(), symbol_id="lonely",
                                        correlated_periphery_count=5)
    assert isolated.classification == "peripheral_noise"
    assert clustered.classification == "drift"


def test_midrange_depth_is_standard_drift():
    sii = SymbolIntegrationIndex()
    for i in range(10):
        sii.record_reference("hub", f"d{i}")
    for i in range(5):
        sii.record_reference("mid", f"m{i}")
    w = sii.weight_presignature(_presig(), symbol_id="mid")
    assert w.classification == "drift"


# -- Concept resonance / RQ-1 ----------------------------------------------------

def _detector():
    return ConceptResonanceDetector(
        canonical_registry={"L2:faction:marshals", "L1:system:life_support"})


def test_l2_l3_resonance_is_convergence():
    d = _detector()
    d.ingest_output("L2", AgentOutput(["L2:faction:marshals"]))
    d.ingest_output("L3", AgentOutput(["L2:faction:marshals"]))
    r = d.detect_resonance()
    assert "L2:faction:marshals" in r.narrative_convergences


def test_l1_crossing_is_bleed():
    d = _detector()
    d.ingest_output("L1", AgentOutput(["L1:system:life_support"]))
    d.ingest_output("L2", AgentOutput(["L1:system:life_support"]))
    r = d.detect_resonance()
    assert "L1:system:life_support" in r.metaphor_bleeds
    assert r.bleed_risk > 0


def test_uncanonized_tags_quarantined_from_classification():
    """RQ-1: unknown vocabulary is counted but never convergence/bleed."""
    d = _detector()
    d.ingest_output("L1", AgentOutput(["mystery_concept"]))
    d.ingest_output("L3", AgentOutput(["mystery_concept"]))
    r = d.detect_resonance()
    events = [e for e in r.resonances
              if e.concept == "uncanonized:mystery_concept"]
    assert events and events[0].classification == "uncertain"
    assert d.staging_tags["mystery_concept"] == 2  # frequency accumulates


# -- Ethical signal sentinel ---------------------------------------------------------

def test_sentinel_baseline_low_risk_no_intervention():
    s = EthicalSignalSentinel()
    r = s.evaluate_action("agentA", Action("routine_op"))
    assert r.risk_score < 0.4
    assert r.recommended_action is None
    assert not r.intervention_recommended


def test_sentinel_recommends_but_never_acts():
    """One-way observation: output is a recommendation field only."""
    s = EthicalSignalSentinel()
    r = s.evaluate_action("agentB", Action("op", intensity=0.9))
    assert hasattr(r, "recommended_action")
    assert not hasattr(s, "apply_action")
    assert not hasattr(s, "block")


def test_sentinel_window_trims_to_one_hour():
    s = EthicalSignalSentinel()
    for _ in range(3):
        s.evaluate_action("agentC", Action("op"))
    assert len(s.action_history["agentC"]) == 3


# -- Drift pre-signature -----------------------------------------------------------------

def test_presig_detects_relay_divergence_and_anchor_instability():
    sii = SymbolIntegrationIndex()
    m = DriftPreSignatureMonitor(sii=sii)
    m.record_drift_sample(0.0001, "relay_a")
    m.record_drift_sample(0.0015, "relay_b")
    m.record_anchor_hash("EOS_SEED_ORION", "h1")
    m.record_anchor_hash("EOS_SEED_ORION", "h2")  # instability
    r = m.analyze()
    assert r.cross_relay_divergence >= 0.001
    types = {p.signature_type for p in r.pre_signatures}
    assert "hash_instability" in types
    assert "state_divergence" in types
    # anchor instability on a pinned symbol must be rupture-classified
    rupture = [p for p in r.pre_signatures
               if getattr(p, "classification", None) == "rupture"]
    assert rupture


def test_presig_units_are_drift_delta_scale():
    m = DriftPreSignatureMonitor()
    m.record_drift_sample(0.0011, "relay_a")  # above presig 0.001, below 0.002
    reading = m.read()
    assert any("drift_delta" in a for a in reading.alerts)
    assert m.analyze().current_drift_delta < 0.002


# -- Extended ZIPWIZ handshake -----------------------------------------------------------------

def test_handshake_five_steps_and_resonance_hold():
    async def tags(_):
        return ["a", "b"]

    async def aligned():
        return {"r2": concept_hash(["a", "b"])}

    async def divergent():
        return {"r2": "x", "r3": "y", "r4": "z"}

    ok = asyncio.run(ExtendedZIPWIZHandshake(
        get_concept_tags=tags,
        get_constellation_hashes=aligned).perform_handshake("r1"))
    assert ok.success and ok.status == "ACTIVE"
    assert list(ok.step_results) == ExtendedZIPWIZHandshake.HANDSHAKE_STEPS

    held = asyncio.run(ExtendedZIPWIZHandshake(
        get_concept_tags=tags,
        get_constellation_hashes=divergent).perform_handshake("r1"))
    assert not held.success
    assert held.status == "PENDING"
    assert held.failed_step == "RESONANCE_SYNC"
