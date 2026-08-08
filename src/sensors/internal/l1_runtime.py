"""Ledger-bound sensor for the governed Orion L1 runtime."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor


METRICS = [
    MetricSpec("tick", MetricUnit.COUNT),
    MetricSpec("station_cycle_minute", MetricUnit.COUNT),
    MetricSpec("event_count", MetricUnit.COUNT),
    MetricSpec("queued_communication_count", MetricUnit.COUNT),
    MetricSpec("delivered_communication_count", MetricUnit.COUNT),
    MetricSpec("station_response_count", MetricUnit.COUNT),
    MetricSpec("character_action_count", MetricUnit.COUNT),
]


class L1RuntimeSensor(ProviderSensor):
    """Expose persisted run-ledger counters without claiming physical telemetry."""

    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__(
            "internal.l1_runtime",
            Layer.L1,
            "l1_runtime",
            METRICS,
            provider,
        )
