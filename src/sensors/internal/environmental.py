"""Internal environmental sensor — platform metrics (spec L1 table)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("memory_pressure", MetricUnit.PERCENT,
               lambda v: v > 85, "memory pressure > 85%"),
    MetricSpec("available_compute", MetricUnit.PERCENT,
               lambda v: v < 20, "available compute < 20%", default=100.0),
    MetricSpec("cpu_thermal_max", MetricUnit.CELSIUS,
               lambda v: v > 80, "CPU thermal > 80C", default=40.0),
    MetricSpec("security_threat_density", MetricUnit.PER_HOUR,
               lambda v: v > 600, "security threats > 10 events/min"),
]


class EnvironmentalSensor(ProviderSensor):
    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("internal.environmental", Layer.L1, "environmental",
                         METRICS, provider)
