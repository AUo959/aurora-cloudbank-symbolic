"""External deep-space sensor — long-horizon trend analysis (24h+)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("trend_pattern_break", MetricUnit.RATIO,
               lambda v: v > 0, "24h+ trend pattern break"),
    MetricSpec("systemic_drift_precursor_sigma", MetricUnit.RATIO,
               lambda v: v > 2, "systemic drift precursor > 2 sigma"),
    MetricSpec("new_failure_modes", MetricUnit.COUNT,
               lambda v: v > 0, "emerging failure mode detected"),
]


class DeepSpaceSensor(ProviderSensor):
    budget_key = "external_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("external.deep_space", Layer.L1, "deep_space",
                         METRICS, provider)
