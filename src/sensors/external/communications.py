"""External communications sensor — connectivity, latency, auth health."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("external_api_connectivity", MetricUnit.RATIO,
               lambda v: v < 0.95, "external API connectivity < 0.95", default=1.0),
    MetricSpec("latency_p95_exceeded", MetricUnit.RATIO,
               lambda v: v > 0, "network latency above P95 baseline"),
    MetricSpec("tls_auth_health", MetricUnit.RATIO,
               lambda v: v < 1.0, "TLS/auth health degraded", default=1.0),
]


class CommunicationsSensor(ProviderSensor):
    budget_key = "external_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("external.communications", Layer.L1, "communications",
                         METRICS, provider)
