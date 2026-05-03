"""Tests for bounded QGIA tier probability normalization."""

from unittest import TestCase

import pytest

from modules.qgia.forecast_engine import QGIAForecastEngine
from modules.qgia.scenario import (
    european_energy_crisis,
    iran_nuclear_escalation,
    subsaharan_instability,
)


_CHECK = TestCase()


@pytest.fixture(scope="module")
def engine():
    """Instantiate the forecast engine once for normalization tests."""
    return QGIAForecastEngine(seed=42)


def _extract_tier_probabilities(output) -> tuple[float, float, float]:
    """Return tier probabilities ordered as Tier I, Tier II, Tier III."""
    probabilities = {tier.tier: tier.probability for tier in output.tier_assessments}
    return probabilities[1], probabilities[2], probabilities[3]


def _check_bounded_simplex(probabilities: tuple[float, float, float]) -> None:
    """Check final tier probabilities against sum and band invariants."""
    lower_bounds = (0.26, 0.10, 0.01)
    upper_bounds = (0.85, 0.25, 0.09)

    _CHECK.assertLess(abs(sum(probabilities) - 1.0), 1e-9)
    for probability, lower_bound, upper_bound in zip(probabilities, lower_bounds, upper_bounds):
        _CHECK.assertGreaterEqual(probability, lower_bound)
        _CHECK.assertLessEqual(probability, upper_bound)


@pytest.mark.parametrize(
    "scenario_fn",
    [
        iran_nuclear_escalation,
        european_energy_crisis,
        subsaharan_instability,
    ],
)
def test_tier_probabilities_are_bounded_normalized(engine, scenario_fn):
    """Tier probabilities sum to 1.0 while staying inside documented bands."""
    output = engine.run_forecast(scenario_fn())
    _check_bounded_simplex(_extract_tier_probabilities(output))
