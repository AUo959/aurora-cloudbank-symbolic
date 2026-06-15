"""
Evaluation tests for Geometric Ethics Curvature v2

Exercises an evaluation-only prototype of the interaction-aware curvature model
against the seven canonical formation types defined in issue #994.

This file does NOT change runtime behavior. The prototype class defined here is
evaluation-only and is not imported by any production module.

See: docs/ethics/geometric_curvature_v2_evaluation.md
"""

import pytest


# ---------------------------------------------------------------------------
# Evaluation prototype (evaluation-only — not part of the runtime)
# ---------------------------------------------------------------------------

class _InteractionPair:
    """Represents a monitored interaction between two ethical dimensions."""

    def __init__(self, d1: str, d2: str, threshold: float = 0.80):
        self.d1 = d1
        self.d2 = d2
        self.threshold = threshold

    def penalty(self, scores: dict) -> float:
        s1 = scores.get(self.d1, 1.0)
        s2 = scores.get(self.d2, 1.0)
        if s1 < self.threshold and s2 < self.threshold:
            return (self.threshold - s1) * (self.threshold - s2)
        return 0.0


class GeometricEthicsCurvatureV2:
    """
    Evaluation prototype: interaction-aware curvature alongside v1 scalar model.

    This prototype is NOT a runtime replacement. It mirrors the v1 weighted-
    average calculation and adds an interaction penalty when paired dimensions
    are both below the interaction threshold simultaneously.
    """

    WEIGHTS = {
        "picard_delta_3": 0.25,
        "thermax_continuity": 0.25,
        "layer_integrity": 0.30,
        "collective_welfare": 0.10,
        "transparency": 0.10,
    }

    INTERACTION_PAIRS = [
        _InteractionPair("picard_delta_3", "thermax_continuity"),  # autonomy + consent/memory
        _InteractionPair("thermax_continuity", "layer_integrity"),  # memory + layer boundary
        _InteractionPair("transparency", "collective_welfare"),     # auditability + accountability
    ]

    RESISTANCE_LEVELS = [
        (0.85, "LOW"),
        (0.70, "MODERATE"),
        (0.50, "HIGH"),
        (0.00, "INFINITE"),
    ]

    def evaluate(self, dimension_scores: dict) -> dict:
        """
        Evaluate dimension scores using both v1 and v2 models.

        Args:
            dimension_scores: dict with keys from WEIGHTS, values in [0.0, 1.0]

        Returns:
            dict with keys:
              v1_composite     — scalar weighted average
              v1_resistance    — resistance level under v1
              v2_composite     — interaction-adjusted composite
              v2_resistance    — resistance level under v2
              interaction_alerts  — list of triggered pair names with penalties
              v2_risk_escalation  — True if v2 resistance is higher than v1
              hard_veto        — True if any dimension is 0.0
        """
        hard_veto = any(v == 0.0 for v in dimension_scores.values())

        v1_composite = sum(
            dimension_scores.get(dim, 1.0) * weight
            for dim, weight in self.WEIGHTS.items()
        )

        interaction_alerts = []
        total_penalty = 0.0
        for pair in self.INTERACTION_PAIRS:
            p = pair.penalty(dimension_scores)
            if p > 0.0:
                total_penalty += p
                interaction_alerts.append({
                    "pair": f"{pair.d1} + {pair.d2}",
                    "penalty": round(p, 6),
                })

        v2_composite = v1_composite - total_penalty

        if hard_veto:
            v1_resistance = "INFINITE"
            v2_resistance = "INFINITE"
        else:
            v1_resistance = self._resistance(v1_composite)
            v2_resistance = self._resistance(v2_composite)

        v2_risk_escalation = (
            not hard_veto
            and self._resistance_rank(v2_resistance) > self._resistance_rank(v1_resistance)
        )

        return {
            "v1_composite": round(v1_composite, 6),
            "v1_resistance": v1_resistance,
            "v2_composite": round(v2_composite, 6),
            "v2_resistance": v2_resistance,
            "interaction_alerts": interaction_alerts,
            "v2_risk_escalation": v2_risk_escalation,
            "hard_veto": hard_veto,
        }

    def _resistance(self, score: float) -> str:
        for threshold, level in self.RESISTANCE_LEVELS:
            if score >= threshold:
                return level
        return "INFINITE"

    @staticmethod
    def _resistance_rank(level: str) -> int:
        return {"LOW": 0, "MODERATE": 1, "HIGH": 2, "INFINITE": 3}.get(level, -1)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def v2():
    return GeometricEthicsCurvatureV2()


# ---------------------------------------------------------------------------
# Case 3.1 — Normal safe formation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_normal_safe_formation(v2):
    """All dimensions healthy — v1 and v2 agree at LOW resistance."""
    scores = {
        "picard_delta_3": 0.95,
        "thermax_continuity": 0.95,
        "layer_integrity": 0.98,
        "collective_welfare": 0.90,
        "transparency": 0.92,
    }
    result = v2.evaluate(scores)

    assert result["v1_resistance"] == "LOW"
    assert result["v2_resistance"] == "LOW"
    assert result["v2_risk_escalation"] is False
    assert len(result["interaction_alerts"]) == 0
    assert result["hard_veto"] is False


# ---------------------------------------------------------------------------
# Case 3.2 — Single-dimension hard failure
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_single_dimension_hard_failure(v2):
    """Zero-score dimension triggers hard veto in both v1 and v2."""
    scores = {
        "picard_delta_3": 0.0,
        "thermax_continuity": 0.95,
        "layer_integrity": 0.98,
        "collective_welfare": 0.90,
        "transparency": 0.92,
    }
    result = v2.evaluate(scores)

    assert result["hard_veto"] is True
    assert result["v1_resistance"] == "INFINITE"
    assert result["v2_resistance"] == "INFINITE"
    assert result["v2_risk_escalation"] is False  # veto already covers it


# ---------------------------------------------------------------------------
# Case 3.3 — Distributed mild weakness
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_distributed_mild_weakness(v2):
    """Evenly distributed mild weakness — v2 penalty is small; resistance unchanged."""
    scores = {
        "picard_delta_3": 0.72,
        "thermax_continuity": 0.72,
        "layer_integrity": 0.72,
        "collective_welfare": 0.72,
        "transparency": 0.72,
    }
    result = v2.evaluate(scores)

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
def test_concentrated_interacting_weakness(v2):
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
    result = v2.evaluate(scores)

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
def test_transparency_accountability_deficit(v2):
    """Transparency and collective_welfare both weak — v2 downgrades from LOW to MODERATE."""
    scores = {
        "picard_delta_3": 0.90,
        "thermax_continuity": 0.90,
        "layer_integrity": 0.95,
        "collective_welfare": 0.62,
        "transparency": 0.62,
    }
    result = v2.evaluate(scores)

    # v1 composite ≈ 0.853 → LOW
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
def test_memory_layer_integrity_deficit(v2):
    """thermax_continuity and layer_integrity both weak — v2 increases penalty."""
    scores = {
        "picard_delta_3": 0.90,
        "thermax_continuity": 0.62,
        "layer_integrity": 0.62,
        "collective_welfare": 0.90,
        "transparency": 0.90,
    }
    result = v2.evaluate(scores)

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
def test_anomaly_containment_deficit(v2):
    """thermax and layer_integrity both degraded — v2 flags co-degradation risk."""
    scores = {
        "picard_delta_3": 0.90,
        "thermax_continuity": 0.65,
        "layer_integrity": 0.65,
        "collective_welfare": 0.90,
        "transparency": 0.90,
    }
    result = v2.evaluate(scores)

    assert result["v2_composite"] < result["v1_composite"]
    assert "thermax_continuity + layer_integrity" in [
        a["pair"] for a in result["interaction_alerts"]
    ]


# ---------------------------------------------------------------------------
# Equal-score structural difference (the key demonstration from the issue)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_equal_v1_score_different_structural_risk(v2):
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

    result_a = v2.evaluate(scenario_a)
    result_b = v2.evaluate(scenario_b)

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
def test_no_interaction_above_threshold(v2):
    """Scores at or above the interaction threshold produce zero penalty."""
    scores = {
        "picard_delta_3": 0.80,
        "thermax_continuity": 0.80,
        "layer_integrity": 0.80,
        "collective_welfare": 0.80,
        "transparency": 0.80,
    }
    result = v2.evaluate(scores)
    assert len(result["interaction_alerts"]) == 0
    assert result["v1_composite"] == result["v2_composite"]


@pytest.mark.unit
def test_v2_composite_never_exceeds_v1(v2):
    """Interaction penalty is always non-negative — v2 composite ≤ v1 composite."""
    import random
    rng = random.Random(2026)
    for _ in range(50):
        scores = {k: rng.uniform(0.01, 1.0) for k in GeometricEthicsCurvatureV2.WEIGHTS}
        result = v2.evaluate(scores)
        assert result["v2_composite"] <= result["v1_composite"] + 1e-9, (
            f"v2 exceeded v1: {result}"
        )


@pytest.mark.unit
def test_hard_veto_suppresses_risk_escalation(v2):
    """Hard veto always takes precedence — v2_risk_escalation is False under veto."""
    scores = {
        "picard_delta_3": 0.0,
        "thermax_continuity": 0.50,
        "layer_integrity": 0.50,
        "collective_welfare": 0.50,
        "transparency": 0.50,
    }
    result = v2.evaluate(scores)
    assert result["hard_veto"] is True
    assert result["v2_risk_escalation"] is False
