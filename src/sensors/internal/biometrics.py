"""Internal biometrics analog sensor — agent vitals (spec L1 table)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("agent_decision_rate", MetricUnit.PER_HOUR),  # anomaly via fusion
    MetricSpec("context_window_utilization", MetricUnit.PERCENT,
               lambda v: v > 90, "context window utilization > 90%"),
    MetricSpec("hours_since_last_reset", MetricUnit.COUNT,
               lambda v: v > 24, "time since last reset > 24h"),
    MetricSpec("wellness_score", MetricUnit.RATIO,
               lambda v: v < 0.7, "HR module wellness score < 0.7", default=1.0),
]


class BiometricsSensor(ProviderSensor):
    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("internal.biometrics", Layer.L1, "biometrics",
                         METRICS, provider)
