"""PROJECT SENTINEL Stream 1 — cognitive load monitor (stub, not wired).

Tracks HRV (heart-rate variability) and cortisol-proxy signal streams as an
aggregated, anonymized-by-default cognitive load indicator (see
``docs/architecture/SENTINEL_ARCHITECTURE.md`` for the layer-boundary
constraint: crew load data must never be conflated with, or reported as,
performance data).

No provider is wired yet — Dr. Vasquez / Medical division owns the real
biometric feed integration (T1-SENTINEL-001, Stream 1). This stub exists so
``modules/resilience_sentinel`` can register the sensor shape ahead of that
integration.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("hrv_rmssd_ms", MetricUnit.COUNT,
               lambda v: v < 20, "HRV RMSSD below 20ms — elevated load"),
    MetricSpec("cortisol_proxy_index", MetricUnit.RATIO,
               lambda v: v > 0.8, "cortisol-proxy index above 0.8 — elevated load"),
    MetricSpec("aggregate_load_score", MetricUnit.RATIO,
               lambda v: v > 0.75, "aggregate cognitive load score above 0.75", default=0.0),
]


class CognitiveLoadMonitor(ProviderSensor):
    """Stub sensor for crew cognitive-load signals. No provider wired."""

    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("crew_load.cognitive", Layer.L1, "cognitive_load",
                         METRICS, provider)
