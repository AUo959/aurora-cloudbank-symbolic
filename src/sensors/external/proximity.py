"""External proximity sensor — request/error clustering (spec L1 env table)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("request_pattern_anomaly", MetricUnit.RATIO,
               lambda v: v > 0.5, "incoming request pattern anomaly"),
    MetricSpec("new_error_clusters", MetricUnit.COUNT,
               lambda v: v > 0, "new error/exception cluster detected"),
    MetricSpec("contention_forecast", MetricUnit.RATIO,
               lambda v: v > 0.3, "resource contention forecast > 0.3"),
]


class ProximitySensor(ProviderSensor):
    budget_key = "external_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("external.proximity", Layer.L1, "proximity",
                         METRICS, provider)
