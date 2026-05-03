"""Tests for bounded QGIA tier probability normalization."""

import numpy as np
import pytest

from modules.qgia.config import TIER_PROBABILITY_BOUNDS
from modules.qgia.forecast_engine import QGIAForecastEngine
from modules.qgia.scenario import (
    european_energy_crisis,
    iran_nuclear_escalation,
    subsaharan_instability,
)


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
    if abs(sum(probabilities) - 1.0) >= 1e-9:
        pytest.fail(f"Tier probabilities sum to {sum(probabilities):.12f}")

    bounds = [TIER_PROBABILITY_BOUNDS[tier] for tier in (1, 2, 3)]
    for probability, (lower_bound, upper_bound) in zip(probabilities, bounds):
        if not lower_bound <= probability <= upper_bound:
            pytest.fail(
                f"Tier probability {probability:.12f} outside "
                f"[{lower_bound:.2f}, {upper_bound:.2f}]"
            )


@pytest.mark.parametrize(
    "scenario_fn",
    [
        iran_nuclear_escalation,
        european_energy_crisis,
        subsaharan_instability,
    ],
)
def test_tier_probabilities_are_bounded_normalized(engine, scenario_fn):
    """Tier probabilities sum to 1.0 while staying inside configured bounds."""
    output = engine.run_forecast(scenario_fn())
    _check_bounded_simplex(_extract_tier_probabilities(output))


@pytest.mark.parametrize(
    "raw_probabilities",
    [
        np.array([0.26, 0.10, 0.01], dtype=float),
        np.array([0.85, 0.25, 0.09], dtype=float),
        np.array([0.26, 0.25, 0.09], dtype=float),
    ],
)
def test_bounded_projection_handles_sum_and_clipping_edges(raw_probabilities):
    """Projection handles raw sums below one, above one, and capped alternatives."""
    probabilities = QGIAForecastEngine._project_to_bounded_simplex(raw_probabilities)
    _check_bounded_simplex(probabilities)
