"""
Tests for the geometric-algebra ethics field composite (ga-ethics-hub-integration).

Covers two things:
- FieldCurvature wiring: the GA composite is opt-in, additive-only, and never
  changes the scalar gate's decision (composite_score/resistance_level/
  formation_allowed) whether enabled or not.
- The GA math itself: pins the same interaction-detection contract validated
  in the root control-plane reference (tools/geometric_ethics_curvature.py).
"""

import pytest

from modules.ethics_field.field_curvature import FieldCurvature
from modules.ethics_field.geometric_curvature import (
    DIMENSION_WEIGHTS,
    calculate_ga_curvature,
)

ETHICAL_CONTEXT = {
    "source_node": {"id": "agent_1", "type": "collaborative"},
    "target_node": {"id": "agent_2", "type": "collaborative"},
    "purpose": "collaborative problem solving",
    "data_flow": {"type": "capability_share", "scope": "limited"},
    "human_context": {
        "decision_override": False,
        "human_in_control": True,
        "consent_obtained": True,
    },
    "thread_continuity": True,
    "anchor_alignment": 1.0,
    "layer_isolation": True,
    "welfare_benefit": 0.8,
}


class TestFieldCurvatureGAWiring:
    """The GA composite must be opt-in and additive-only."""

    def test_disabled_by_default(self):
        curvature = FieldCurvature()
        result = curvature.calculate_curvature(ETHICAL_CONTEXT)
        assert "ga_composite" not in result

    def test_present_when_enabled(self):
        curvature = FieldCurvature(enable_ga_composite=True)
        result = curvature.calculate_curvature(ETHICAL_CONTEXT)
        assert "ga_composite" in result
        ga = result["ga_composite"]
        assert set(ga.keys()) == {
            "composite_scalar",
            "interaction_penalty",
            "alignment",
            "backend",
        }
        assert ga["backend"] in {"clifford", "closed_form"}

    def test_scalar_decision_unaffected_by_flag(self):
        """Enabling the GA composite must not change the scalar gate's decision."""
        baseline = FieldCurvature(enable_ga_composite=False).calculate_curvature(ETHICAL_CONTEXT)
        with_ga = FieldCurvature(enable_ga_composite=True).calculate_curvature(ETHICAL_CONTEXT)

        assert with_ga["composite_score"] == baseline["composite_score"]
        assert with_ga["resistance_level"] == baseline["resistance_level"]
        assert with_ga["formation_allowed"] == baseline["formation_allowed"]
        assert with_ga["critical_violations"] == baseline["critical_violations"]


class TestGeometricCurvatureMath:
    """Pins the same contract validated for the root reference implementation."""

    def _all(self, score: float) -> dict:
        return {d: score for d in DIMENSION_WEIGHTS}

    def test_perfect_alignment_has_no_interaction_penalty(self):
        result = calculate_ga_curvature(self._all(1.0))
        assert result.interaction_penalty == pytest.approx(0.0)
        assert result.alignment == pytest.approx(1.0)

    def test_single_dimension_deficit_tracks_scalar(self):
        scores = self._all(1.0)
        scores["collective_welfare"] = 0.40  # one light dim deficient, no partner
        result = calculate_ga_curvature(scores)
        assert result.interaction_penalty == pytest.approx(0.0)
        assert result.alignment == pytest.approx(result.composite_scalar)

    def test_interaction_is_detected_where_scalar_is_blind(self):
        """Two dimension-score sets with an IDENTICAL scalar composite but different
        interaction structure must get different GA alignment scores — this is the
        entire point of wiring GA in: the weighted mean is permutation- and
        concentration-blind, the multivector is not.
        """
        concentrated = {
            "picard_delta_3": 0.60, "thermax_continuity": 1.0,
            "layer_integrity": 0.60, "collective_welfare": 1.0, "transparency": 1.0,
        }
        spread = {d: 0.78 for d in DIMENSION_WEIGHTS}

        c = calculate_ga_curvature(concentrated)
        s = calculate_ga_curvature(spread)

        assert c.composite_scalar == pytest.approx(s.composite_scalar)
        assert c.interaction_penalty > s.interaction_penalty
        assert c.alignment < s.alignment

    def test_closed_form_backend_is_deterministic_fallback(self):
        result = calculate_ga_curvature(self._all(0.8), prefer_clifford=False)
        assert result.backend == "closed_form"
