"""Observatory containment sensor — simulation chamber integrity.

Containment is rupture-adjacent: this sensor is marked critical and is never
decimated (spec §Per-Tick Performance Budget).
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("grid_integrity", MetricUnit.RATIO,
               lambda v: v < 0.999, "containment grid integrity < 0.999", default=1.0),
    MetricSpec("bleed_events", MetricUnit.COUNT,
               lambda v: v > 0, "simulation state leaking to L1 (bleed event)"),
    MetricSpec("pressure_differential", MetricUnit.RATIO,
               lambda v: v > 0.01, "L1/L2 state pressure differential > 0.01"),
]


class ContainmentSensor(ProviderSensor):
    budget_key = "observatory_physical"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("observatory.containment", Layer.L2, "containment",
                         METRICS, provider)
        self.critical = True
