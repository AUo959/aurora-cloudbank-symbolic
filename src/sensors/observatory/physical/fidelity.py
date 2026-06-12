"""Observatory fidelity sensor — simulation coherence."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("temporal_coherence", MetricUnit.RATIO,
               lambda v: v < 0.99, "temporal coherence < 0.99", default=1.0),
    MetricSpec("spatial_coherence", MetricUnit.RATIO,
               lambda v: v < 0.99, "spatial coherence < 0.99", default=1.0),
    MetricSpec("causal_coherence", MetricUnit.RATIO,
               lambda v: v < 0.95, "causal chain integrity < 0.95", default=1.0),
]


class FidelitySensor(ProviderSensor):
    budget_key = "observatory_physical"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("observatory.fidelity", Layer.L2, "fidelity",
                         METRICS, provider)
