"""Observatory boundary sensor — real/simulated line clarity."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("boundary_clarity", MetricUnit.RATIO,
               lambda v: v < 0.99, "real/simulated boundary clarity < 0.99",
               default=1.0),
    MetricSpec("l2_to_l1_references", MetricUnit.COUNT,
               lambda v: v > 0, "unexpected L2->L1 reference (simulated referencing real)"),
    MetricSpec("state_provenance", MetricUnit.RATIO,
               lambda v: v < 0.99, "state provenance traceability < 0.99",
               default=1.0),
]


class BoundarySensor(ProviderSensor):
    budget_key = "observatory_physical"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("observatory.boundary", Layer.L2, "boundary",
                         METRICS, provider)
        self.critical = True
