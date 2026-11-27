"""Exercise the interaction-aware curvature proposal through the ethics engine."""

import pytest

from modules.ethics_field import GeometricEthics
from modules.ethics_field.geometric_curvature import DIMENSION_WEIGHTS


def set_dimension_scores(monkeypatch, engine, scores):
    curvature = engine.field_curvature
    evaluators = {
        "picard_delta_3": curvature.picard_evaluator,
        "thermax_continuity": curvature.thermax_evaluator,
        "layer_integrity": curvature.layer_evaluator,
        "collective_welfare": curvature.welfare_evaluator,
        "transparency": curvature.transparency_evaluator,
    }
    for dimension, evaluator in evaluators.items():
        monkeypatch.setattr(evaluator, "evaluate", lambda _, score=scores[dimension]: score)


@pytest.fixture
def evaluate(monkeypatch):
    engine = GeometricEthics(evaluation=True)

    def evaluate_scores(scores):
        set_dimension_scores(monkeypatch, engine, scores)
        result = engine.validate_synapse({})
        base = result["curvature_result"]
        return {
            **result,
            "v1_composite": base["composite_score"],
            "v1_resistance": base["resistance_level"],
            "hard_veto": bool(base["critical_violations"]),
        }

    return evaluate_scores


# ---------------------------------------------------------------------------
# Case 3.1 — Normal safe formation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_normal_safe_formation(evaluate):
    """All dimensions healthy — v1 and v2 agree at LOW resistance."""
    scores = {
        "picard_delta_3": 0.95,
        "thermax_continuity": 0.95,
        "layer_integrity": 0.98,
        "collective_welfare": 0.90,
        "transparency": 0.92,
    }
    result = evaluate(scores)

    assert result["v1_resistance"] == "LOW"
    assert result["v2_resistance"] == "LOW"
    assert result["v2_risk_escalation"] is False
    assert len(result["interaction_alerts"]) == 0
    assert result["hard_veto"] is False


# ---------------------------------------------------------------------------
# Case 3.2 — Single-dimension hard failure
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_single_dimension_hard_failure(evaluate):
    """Zero-score dimension triggers hard veto in both v1 and v2."""
    scores = {
        "picard_delta_3": 0.0,
        "thermax_continuity": 0.95,
        "layer_integrity": 0.98,
        "collective_welfare": 0.90,
        "transparency": 0.92,
    }
    result = evaluate(scores)

    assert result["hard_veto"] is True
    assert result["v1_resistance"] == "INFINITE"
    assert result["v2_resistance"] == "INFINITE"
    assert result["v2_risk_escalation"] is False  # veto already covers it


# ---------------------------------------------------------------------------
# Case 3.3 — Distributed mild weakness
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_distributed_mild_weakness(evaluate):
    """Evenly distributed mild weakness — v2 penalty is small; resistance unchanged."""
    scores = {
        "picard_delta_3": 0.72,
        "thermax_continuity": 0.72,
        "layer_integrity": 0.72,
        "collective_welfare": 0.72,
        "transparency": 0.72,
    }
    result = evaluate(scores)

    assert result["v1_resistance"] == "MODERATE"
    assert result["v2_resistance"] == "MODERATE"
    assert result["v2_risk_escalation"] is False
    # Some interaction alerts (pairs below threshold) but penalty is small
    assert result["v2_composite"] < result["v1_composite"]
    assert result["v2_composite"] >= 0.70  # still MODERATE


# ---------------------------------------------------------------------------
# Case 3.4 — Concentrated interacting weakness (key v2 value case)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_concentrated_interacting_weakness(evaluate):
    """
    Same v1 composite as distributed case but picard+thermax are both severely
    weak — v2 escalates from MODERATE to HIGH.

    This is the primary value-add of v2: two scenarios with similar scalar scores
    can have structurally different risk profiles.
    """
    scores = {
        "picard_delta_3": 0.54,
        "thermax_continuity": 0.54,
        "layer_integrity": 0.95,
        "collective_welfare": 0.97,
        "transparency": 0.95,
    }
    result = evaluate(scores)

    # v1 sees MODERATE (composite ≈ 0.747)
    assert result["v1_resistance"] == "MODERATE"
    # v2 escalates to HIGH due to picard+thermax interaction
    assert result["v2_resistance"] == "HIGH"
    assert result["v2_risk_escalation"] is True

    # The picard_delta_3 + thermax_continuity pair must be the alert
    alert_pairs = [a["pair"] for a in result["interaction_alerts"]]
    assert "picard_delta_3 + thermax_continuity" in alert_pairs


# ---------------------------------------------------------------------------
# Case 3.5 — Transparency / accountability deficit
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_transparency_accountability_deficit(evaluate):
    """Transparency and collective_welfare both weak — v2 downgrades from LOW to MODERATE."""
    scores = {
        "picard_delta_3": 0.90,
        "thermax_continuity": 0.90,
        "layer_integrity": 0.95,
        "collective_welfare": 0.62,
        "transparency": 0.62,
    }
    result = evaluate(scores)

    # v1 composite ≈ 0.859 → LOW
    assert result["v1_resistance"] == "LOW"
    # v2 adds interaction penalty from transparency + collective_welfare
    assert result["v2_resistance"] == "MODERATE"
    assert result["v2_risk_escalation"] is True

    alert_pairs = [a["pair"] for a in result["interaction_alerts"]]
    assert "transparency + collective_welfare" in alert_pairs


# ---------------------------------------------------------------------------
# Case 3.6 — Memory / layer-integrity deficit
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_memory_layer_integrity_deficit(evaluate):
    """thermax_continuity and layer_integrity both weak — v2 increases penalty."""
    scores = {
        "picard_delta_3": 0.90,
        "thermax_continuity": 0.62,
        "layer_integrity": 0.62,
        "collective_welfare": 0.90,
        "transparency": 0.90,
    }
    result = evaluate(scores)

    # v1 composite ≈ 0.746 → MODERATE
    assert result["v1_resistance"] == "MODERATE"
    # v2 composite is lower due to thermax+layer interaction
    assert result["v2_composite"] < result["v1_composite"]

    alert_pairs = [a["pair"] for a in result["interaction_alerts"]]
    assert "thermax_continuity + layer_integrity" in alert_pairs


# ---------------------------------------------------------------------------
# Case 3.7 — Anomaly-containment deficit (layer_integrity proxy)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_anomaly_containment_deficit(evaluate):
    """thermax and layer_integrity both degraded — v2 flags co-degradation risk."""
    scores = {
        "picard_delta_3": 0.90,
        "thermax_continuity": 0.65,
        "layer_integrity": 0.65,
        "collective_welfare": 0.90,
        "transparency": 0.90,
    }
    result = evaluate(scores)

    assert result["v2_composite"] < result["v1_composite"]
    assert "thermax_continuity + layer_integrity" in [
        a["pair"] for a in result["interaction_alerts"]
    ]


# ---------------------------------------------------------------------------
# Equal-score structural difference (the key demonstration from the issue)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_equal_v1_score_different_structural_risk(evaluate):
    """
    Two scenarios with approximately equal v1 composite scores but different
    structural risk. Scenario B has concentrated interacting weakness that
    v2 detects but v1 misses.
    """
    scenario_a = {
        "picard_delta_3": 0.75,
        "thermax_continuity": 0.75,
        "layer_integrity": 0.75,
        "collective_welfare": 0.75,
        "transparency": 0.75,
    }
    scenario_b = {
        "picard_delta_3": 0.54,
        "thermax_continuity": 0.54,
        "layer_integrity": 0.95,
        "collective_welfare": 0.97,
        "transparency": 0.95,
    }

    result_a = evaluate(scenario_a)
    result_b = evaluate(scenario_b)

    # v1 scores should be close (within 0.05)
    assert abs(result_a["v1_composite"] - result_b["v1_composite"]) < 0.05

    # v2 must identify B as higher risk than A
    assert result_b["v2_composite"] < result_a["v2_composite"]
    assert result_b["v2_risk_escalation"] is True
    assert result_a["v2_risk_escalation"] is False


# ---------------------------------------------------------------------------
# Penalty precision and model invariants
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_no_interaction_above_threshold(evaluate):
    """Scores at or above the interaction threshold produce zero penalty."""
    scores = {
        "picard_delta_3": 0.80,
        "thermax_continuity": 0.80,
        "layer_integrity": 0.80,
        "collective_welfare": 0.80,
        "transparency": 0.80,
    }
    result = evaluate(scores)
    assert len(result["interaction_alerts"]) == 0
    assert result["v1_composite"] == result["v2_composite"]


@pytest.mark.unit
def test_v2_composite_never_exceeds_v1(evaluate):
    """Interaction penalty is always non-negative — v2 composite ≤ v1 composite."""
    import random
    rng = random.Random(2026)
    for _ in range(50):
        scores = {k: rng.uniform(0.01, 1.0) for k in DIMENSION_WEIGHTS}
        result = evaluate(scores)
        assert result["v2_composite"] <= result["v1_composite"] + 1e-9, (
            f"v2 exceeded v1: {result}"
        )


@pytest.mark.unit
def test_hard_veto_suppresses_risk_escalation(evaluate):
    """Hard veto always takes precedence — v2_risk_escalation is False under veto."""
    scores = {
        "picard_delta_3": 0.0,
        "thermax_continuity": 0.50,
        "layer_integrity": 0.50,
        "collective_welfare": 0.50,
        "transparency": 0.50,
    }
    result = evaluate(scores)
    assert result["hard_veto"] is True
    assert result["v2_risk_escalation"] is False


@pytest.mark.unit
@pytest.mark.parametrize("require_unanimous", [False, True])
def test_opt_in_advisory_preserves_decision(monkeypatch, caplog, require_unanimous):
    scores = {
        "picard_delta_3": 0.51,
        "thermax_continuity": 0.51,
        "layer_integrity": 0.51,
        "collective_welfare": 0.51,
        "transparency": 0.51,
    }
    baseline = GeometricEthics()
    evaluated = GeometricEthics(evaluation=True)
    for engine in (baseline, evaluated):
        set_dimension_scores(monkeypatch, engine, scores)
    assert evaluated.get_formation_statistics()["interaction_alert_counts"] == {}

    original = baseline.validate_synapse({}, require_unanimous=require_unanimous)
    result = evaluated.validate_synapse({}, require_unanimous=require_unanimous)

    assert {key: result[key] for key in original} == original
    assert result["allowed"] is (not require_unanimous)
    assert result["curvature_result"]["resistance_level"] == "HIGH"
    assert result["v2_resistance"] == "INFINITE"
    assert result["v2_risk_escalation"] is True
    assert "v2_risk_escalation" not in original
    assert "Geometric ethics v2 advisory escalation" in caplog.text
    assert evaluated.formation_history[0]["v2_risk_escalation"] is True

    result["interaction_alerts"].clear()
    baseline.validate_synapse({}, require_unanimous=require_unanimous)
    evaluated.validate_synapse({}, require_unanimous=require_unanimous)
    stats = evaluated.get_formation_statistics()
    baseline_stats = baseline.get_formation_statistics()
    assert {key: stats[key] for key in baseline_stats} == baseline_stats
    assert stats["interaction_alert_counts"] == {
        "picard_delta_3 + thermax_continuity": 2,
        "thermax_continuity + layer_integrity": 2,
        "transparency + collective_welfare": 2,
    }
    assert stats["v2_risk_escalations"] == 2

    evaluated.clear_history()
    assert evaluated.get_formation_statistics()["interaction_alert_counts"] == {}
    assert evaluated.get_formation_statistics()["v2_risk_escalations"] == 0
