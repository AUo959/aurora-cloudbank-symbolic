"""External astronomical sensor — science-mission distributions (informational)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

# Science-mission metrics: no alert thresholds; consumed by fusion/forecast.
METRICS = [
    MetricSpec("inference_distribution_shift", MetricUnit.RATIO),
    MetricSpec("decision_outcome_entropy", MetricUnit.RATIO),
]


class AstronomicalSensor(ProviderSensor):
    budget_key = "external_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("external.astronomical", Layer.L1, "astronomical",
                         METRICS, provider)
