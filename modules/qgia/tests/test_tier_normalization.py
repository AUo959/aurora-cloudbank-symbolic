"""Unit tests for QGIA tier probability normalization.

Verifies that the softmax normalization applied in ``_aggregate_to_tiers``
produces a coherent probability distribution: Tier I + Tier II + Tier III
must sum to exactly 1.0 for all valid inputs.

Note: the pre-normalization clamping bands (Tier I ∈ [0.26, 0.85],
Tier II ∈ [0.10, 0.25], Tier III ∈ [0.01, 0.09]) are *inputs* to the
softmax step.  Post-normalization values are not constrained to those
bands; the only guaranteed post-normalization invariant is sum == 1.0.
"""

import pytest

from modules.qgia.forecast_engine import QGIAForecastEngine
from modules.qgia.scenario import (
    european_energy_crisis,
    iran_nuclear_escalation,
    subsaharan_instability,
)


@pytest.fixture(scope="module")
def engine():
    """Instantiate the forecast engine once for all normalization tests."""
    return QGIAForecastEngine(seed=42)


class TestTierProbabilityNormalization:
    """Tier probabilities must form a coherent probability distribution summing to 1.0."""

    @staticmethod
    def _extract_tier_probs(output) -> tuple[float, float, float]:
        """Return (tier_i, tier_ii, tier_iii) probabilities from a ForecastOutput."""
        prob = {t.tier: t.probability for t in output.tier_assessments}
        return prob[1], prob[2], prob[3]

    def test_normalization_low_variance_scenario(self, engine):
        """Low-variance scenario (Iran nuclear escalation): tiers sum to 1.0."""
        output = engine.run_forecast(iran_nuclear_escalation())
        tier_i, tier_ii, tier_iii = self._extract_tier_probs(output)
        assert abs(tier_i + tier_ii + tier_iii - 1.0) < 1e-9

    def test_normalization_high_variance_scenario(self, engine):
        """High-variance scenario (European energy crisis): tiers sum to 1.0."""
        output = engine.run_forecast(european_energy_crisis())
        tier_i, tier_ii, tier_iii = self._extract_tier_probs(output)
        assert abs(tier_i + tier_ii + tier_iii - 1.0) < 1e-9

    def test_normalization_edge_case_scenario(self, engine):
        """Edge-case scenario (Sub-Saharan instability): tiers sum to 1.0."""
        output = engine.run_forecast(subsaharan_instability())
        tier_i, tier_ii, tier_iii = self._extract_tier_probs(output)
        assert abs(tier_i + tier_ii + tier_iii - 1.0) < 1e-9
