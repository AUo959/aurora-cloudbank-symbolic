"""Phase 4 tests: predictor + RQ-2 lifecycle, oscillation + regulator
exclusion (success criterion 12), resonance calc, certification chain."""

from src.sensors.core.data_bus import TOPIC_REGULATOR_MARKER, SensorDataBus
from src.sensors.core.reading_types import PrecursorPattern
from src.sensors.fusion import (
    CoherenceCertifier,
    CrossLayerResonanceCalculator,
    FusionPredictor,
    OscillationHealthMonitor,
    RegulatorMarkerConsumer,
)


# -- Fusion predictor --------------------------------------------------------

def test_pattern_match_produces_afs_scoreable_forecast():
    p = FusionPredictor()
    p.ingest({"grid_integrity": 0.99, "bleed_events": 1})
    forecasts = p.forecast()
    assert forecasts
    f = forecasts[0]
    assert f.anomaly_type == "containment"
    assert f.recommended_intervention == "REINFORCE_BOUNDARY"
    assert f.intervention_urgency == "immediate"
    # v0.3.0 AFS alignment fields:
    assert f.resolution_criteria
    lo, hi = f.confidence_interval
    assert 0.0 <= lo <= f.probability <= hi <= 1.0


def test_no_match_no_forecast():
    p = FusionPredictor()
    p.ingest({"grid_integrity": 1.0})
    assert p.forecast() == []


def test_drift_extrapolation_forecast():
    p = FusionPredictor()
    p.ingest({"current_drift_delta": 0.0015, "drift_velocity": 0.001,
              "drift_threshold": 0.002})
    forecasts = [f for f in p.forecast() if f.pattern_matched is None]
    assert forecasts
    assert forecasts[0].anomaly_type == "drift"
    assert forecasts[0].predicted_eta_seconds <= 3600


def test_rq2_pattern_lifecycle_gates_promotion_on_precision():
    p = FusionPredictor()
    cand = PrecursorPattern(
        pattern_id="new_pattern", anomaly_type="drift",
        signals=["drift_velocity > 0.0005"], confidence=0.6,
        typical_eta_seconds=600)
    staged = p.stage_pattern(cand, incident_id="INC-42", author="travis")
    assert staged.status == "staged"
    assert staged.pattern_hash
    assert staged.provenance["incident_id"] == "INC-42"
    # staged patterns never fire
    p.ingest({"drift_velocity": 0.001})
    assert all(f.pattern_matched != "new_pattern" for f in p.forecast())
    # precision below 0.7 is denied
    try:
        p.promote_pattern("new_pattern", backtest_precision=0.5, occurrences=12)
        raise AssertionError("promotion should be denied")
    except ValueError:
        pass
    promoted = p.promote_pattern("new_pattern", backtest_precision=0.8,
                                 occurrences=5)
    assert promoted.status == "live"
    assert promoted.low_n is True  # < 10 occurrences flagged


# -- Oscillation health -------------------------------------------------------------

def _hunt(monitor, n=10, magnitude=0.5, target=None):
    for i in range(n):
        monitor.record_correction(
            "micro", "positive" if i % 2 == 0 else "negative",
            magnitude, drift_before=0.001, drift_after=0.001, target=target)


def test_hunting_detected_without_regulator_context():
    m = OscillationHealthMonitor()
    _hunt(m)
    r = m.analyze()
    assert not r.oscillation_healthy
    assert r.oscillation_risk == "high"
    assert "Hunting" in r.diagnosis


def test_regulator_marked_perturbations_excluded_from_hunting():
    """Success criterion 12: zero false hunting alerts on regulator activity."""
    bus = SensorDataBus()
    consumer = RegulatorMarkerConsumer(bus)
    m = OscillationHealthMonitor(consumer)
    bus.publish(TOPIC_REGULATOR_MARKER,
                {"tick": 1, "target": "doctrine", "magnitude": 0.5})
    _hunt(m, target="doctrine")  # all regulator-intentional
    r = m.analyze()
    assert r.regulator_share == 1.0
    assert "Hunting" not in r.diagnosis


def test_diverging_corrections_flagged():
    m = OscillationHealthMonitor()
    for i in range(6):
        m.record_correction("micro", "positive", 0.1 * (i + 1),
                            drift_before=0.001, drift_after=0.0015)
    r = m.analyze()
    assert r.magnitude_trend == "growing"
    assert r.oscillation_risk == "high"


# -- Cross-layer resonance ------------------------------------------------------------------

def test_resonance_dissonance_detection():
    c = CrossLayerResonanceCalculator()
    c.update_layer("L1", {"a": 1.0, "b": 0.0})
    c.update_layer("L2", {"a": 0.0, "b": 1.0})  # orthogonal => dissonant
    c.update_layer("L3", {"a": 1.0, "b": 0.0})
    r = c.calculate()
    assert r.dissonance_detected
    assert "L1-L2" in r.dissonance_locations
    assert r.system_resonance < 0.5


# -- Coherence certification -----------------------------------------------------------------

def test_certification_chains_and_blocks_on_rupture():
    cert = CoherenceCertifier()
    c1 = cert.certify(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, anchor_verified=True)
    assert c1.system_coherent
    assert c1.previous_certification_id is None
    assert c1.anchor_id == "EOS_SEED_ORION"
    assert c1.ethics_protocol == "Picard_Delta_3"

    c2 = cert.certify(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, anchor_verified=True,
                      rupture_candidates=["L2:faction:marshals"])
    assert not c2.system_coherent
    assert any("rupture" in b for b in c2.blocking_issues)
    assert c2.previous_certification_id == c1.certification_id  # custody chain
    assert c2.verification_hash != c1.verification_hash


def test_certification_blocks_on_unverified_anchor():
    cert = CoherenceCertifier()
    c = cert.certify(1.0, 1.0, 1.0, 1.0, 1.0, 0.0, anchor_verified=False)
    assert not c.system_coherent
    assert any("EOS_SEED_ORION" in b for b in c.blocking_issues)
