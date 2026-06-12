"""Internal operational sensor — service/resource health (spec L1 table)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("min_dependency_health", MetricUnit.RATIO,
               lambda v: v < 0.9, "service dependency health < 0.9", default=1.0),
    MetricSpec("min_resource_pool", MetricUnit.PERCENT,
               lambda v: v < 20, "resource pool < 20%", default=100.0),
    MetricSpec("fleet_bridge_deviation", MetricUnit.RATIO,
               lambda v: v > 0, "fleet bridge status deviation"),
]


class OperationalSensor(ProviderSensor):
    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("internal.operational", Layer.L1, "operational",
                         METRICS, provider)
