"""Internal structural sensor.

v0.3.0: ``contract_violations`` is canonically sourced from
``SimulationSubsystem.validate_state`` self-reports (spec §SimulationSubsystem
Validation Hook) — no new validation logic lives in the sensor layer. Until
the Forge refactor merges, the provider may aggregate any violation-list
source; the sensor only counts.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("schema_integrity", MetricUnit.RATIO,
               lambda v: v < 0.95, "schema integrity < 0.95", default=1.0),
    MetricSpec("contract_violations", MetricUnit.COUNT,
               lambda v: v > 0, "subsystem contract violations present"),
    MetricSpec("layer_boundary_health", MetricUnit.RATIO,
               lambda v: v < 0.99, "L1/L2/L3 boundary health < 0.99", default=1.0),
    MetricSpec("service_load_stddev", MetricUnit.PERCENT,
               lambda v: v > 15, "service load imbalance: std dev > 15%"),
]


class StructuralSensor(ProviderSensor):
    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("internal.structural", Layer.L1, "structural",
                         METRICS, provider)
