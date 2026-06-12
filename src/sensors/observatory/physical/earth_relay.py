"""Observatory earth-relay sensor — link, integrity, provenance tagging."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("link_active", MetricUnit.RATIO,
               lambda v: v < 1.0, "Earth relay link inactive", default=1.0),
    MetricSpec("data_integrity_verified", MetricUnit.RATIO,
               lambda v: v < 1.0, "science data chain of custody unverified",
               default=1.0),
    MetricSpec("provenance_complete", MetricUnit.RATIO,
               lambda v: v < 1.0, "sim-vs-real source tagging incomplete",
               default=1.0),
]


class EarthRelaySensor(ProviderSensor):
    budget_key = "observatory_physical"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("observatory.earth_relay", Layer.L2, "earth_relay",
                         METRICS, provider)
