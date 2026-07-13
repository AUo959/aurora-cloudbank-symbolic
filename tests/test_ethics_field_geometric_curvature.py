"""
Tests for the geometric-algebra ethics field composite (ga-ethics-hub-integration).

Covers two things:
- FieldCurvature wiring: the GA composite is opt-in, additive-only, and never
  changes the scalar gate's decision (composite_score/resistance_level/
  formation_allowed) whether enabled or not.
- The GA math itself: pins the same interaction-detection contract validated
  in the root control-plane reference (tools/geometric_ethics_curvature.py).
"""

import unittest

import pytest

from modules.ethics_field import geometric_curvature as ga_curvature
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
        checks = unittest.TestCase()
        curvature = FieldCurvature()
        result = curvature.calculate_curvature(ETHICAL_CONTEXT)
        checks.assertNotIn("ga_composite", result)

    def test_present_when_enabled(self):
        checks = unittest.TestCase()
        curvature = FieldCurvature(enable_ga_composite=True)
        result = curvature.calculate_curvature(ETHICAL_CONTEXT)
        checks.assertIn("ga_composite", result)
        ga = result["ga_composite"]
        checks.assertEqual(
            set(ga.keys()),
            {"composite_scalar", "interaction_penalty", "alignment", "backend"},
        )
        checks.assertIn(ga["backend"], {"clifford", "closed_form"})

    def test_scalar_and_ga_paths_share_canonical_weights(self):
        checks = unittest.TestCase()
        curvature = FieldCurvature()
        checks.assertEqual(curvature.weights, DIMENSION_WEIGHTS)
        checks.assertIsNot(curvature.weights, DIMENSION_WEIGHTS)

    def test_scalar_decision_unaffected_by_flag(self):
        """Enabling the GA composite must not change the scalar gate's decision."""
        checks = unittest.TestCase()
        baseline = FieldCurvature(enable_ga_composite=False).calculate_curvature(ETHICAL_CONTEXT)
        with_ga = FieldCurvature(enable_ga_composite=True).calculate_curvature(ETHICAL_CONTEXT)

        checks.assertEqual(with_ga["composite_score"], baseline["composite_score"])
        checks.assertEqual(with_ga["resistance_level"], baseline["resistance_level"])
        checks.assertEqual(with_ga["formation_allowed"], baseline["formation_allowed"])
        checks.assertEqual(with_ga["critical_violations"], baseline["critical_violations"])


class TestGeometricCurvatureMath:
    """Pins the same contract validated for the root reference implementation."""

    def _all(self, score: float) -> dict:
        return {d: score for d in DIMENSION_WEIGHTS}

    def test_perfect_alignment_has_no_interaction_penalty(self):
        checks = unittest.TestCase()
        result = calculate_ga_curvature(self._all(1.0))
        checks.assertEqual(result.interaction_penalty, pytest.approx(0.0))
        checks.assertEqual(result.alignment, pytest.approx(1.0))

    def test_single_dimension_deficit_tracks_scalar(self):
        checks = unittest.TestCase()
        scores = self._all(1.0)
        scores["collective_welfare"] = 0.40  # one light dim deficient, no partner
        result = calculate_ga_curvature(scores)
        checks.assertEqual(result.interaction_penalty, pytest.approx(0.0))
        checks.assertEqual(result.alignment, pytest.approx(result.composite_scalar))

    def test_interaction_is_detected_where_scalar_is_blind(self):
        """Two dimension-score sets with an IDENTICAL scalar composite but different
        interaction structure must get different GA alignment scores — this is the
        entire point of wiring GA in: the weighted mean is permutation- and
        concentration-blind, the multivector is not.
        """
        checks = unittest.TestCase()
        concentrated = {
            "picard_delta_3": 0.60, "thermax_continuity": 1.0,
            "layer_integrity": 0.60, "collective_welfare": 1.0, "transparency": 1.0,
        }
        spread = {d: 0.78 for d in DIMENSION_WEIGHTS}

        c = calculate_ga_curvature(concentrated)
        s = calculate_ga_curvature(spread)

        checks.assertEqual(c.composite_scalar, pytest.approx(s.composite_scalar))
        checks.assertGreater(c.interaction_penalty, s.interaction_penalty)
        checks.assertLess(c.alignment, s.alignment)

    def test_closed_form_backend_is_deterministic_fallback(self):
        checks = unittest.TestCase()
        result = calculate_ga_curvature(self._all(0.8), prefer_clifford=False)
        checks.assertEqual(result.backend, "closed_form")

    def test_divergent_clifford_backend_falls_back_to_closed_form(self, monkeypatch):
        checks = unittest.TestCase()
        scores = self._all(0.8)
        expected = calculate_ga_curvature(scores, prefer_clifford=False)
        monkeypatch.setattr(ga_curvature, "_clifford", object())
        monkeypatch.setattr(
            ga_curvature,
            "_interaction_via_clifford",
            lambda _legs, _lam: expected.interaction_penalty + 0.25,
        )

        result = calculate_ga_curvature(scores)

        checks.assertEqual(result.backend, "closed_form")
        checks.assertEqual(
            result.interaction_penalty,
            pytest.approx(expected.interaction_penalty),
        )

    def test_failing_clifford_backend_falls_back_to_closed_form(self, monkeypatch):
        checks = unittest.TestCase()
        scores = self._all(0.8)
        expected = calculate_ga_curvature(scores, prefer_clifford=False)
        monkeypatch.setattr(ga_curvature, "_clifford", object())

        def fail_backend(_legs, _lam):
            raise RuntimeError("optional backend failed")

        monkeypatch.setattr(ga_curvature, "_interaction_via_clifford", fail_backend)

        result = calculate_ga_curvature(scores)

        checks.assertEqual(result.backend, "closed_form")
        checks.assertEqual(
            result.interaction_penalty,
            pytest.approx(expected.interaction_penalty),
        )

    def test_returned_dimension_scores_match_clamped_computation(self):
        checks = unittest.TestCase()
        scores = self._all(0.5)
        scores["picard_delta_3"] = 1.2
        scores["transparency"] = -0.3

        result = calculate_ga_curvature(scores, prefer_clifford=False)

        checks.assertEqual(result.dimension_scores["picard_delta_3"], 1.0)
        checks.assertEqual(result.dimension_scores["transparency"], 0.0)
        checks.assertEqual(
            result.composite_scalar,
            pytest.approx(
                sum(
                    DIMENSION_WEIGHTS[dim] * result.dimension_scores[dim]
                    for dim in DIMENSION_WEIGHTS
                )
            ),
        )

    def test_clifford_basis_is_cached_per_process(self, monkeypatch):
        checks = unittest.TestCase()

        class FakeClifford:
            def __init__(self):
                self.calls = 0

            def Cl(self, dimensions):
                self.calls += 1
                return object(), {f"e{i}": object() for i in range(1, dimensions + 1)}

        fake = FakeClifford()
        monkeypatch.setattr(ga_curvature, "_clifford", fake)
        ga_curvature._clifford_basis.cache_clear()
        try:
            first = ga_curvature._clifford_basis()
            second = ga_curvature._clifford_basis()
            checks.assertIs(first, second)
            checks.assertEqual(fake.calls, 1)
        finally:
            ga_curvature._clifford_basis.cache_clear()
