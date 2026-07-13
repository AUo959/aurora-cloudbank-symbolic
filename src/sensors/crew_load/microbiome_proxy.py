"""PROJECT SENTINEL Stream 1 — microbiome-correlated cognitive proxy (stub).

Placeholder for Dr. Ren Feldman's longitudinal microbiome-correlated
cognitive state research. No dataset, model, or provider exists yet; this
stub only reserves the metric name and unit so future integration doesn't
require touching ``CognitiveLoadMonitor`` or its callers.

Layer-boundary constraint (see SENTINEL_ARCHITECTURE.md): this signal is
research-stage and must not gate, score, or otherwise feed any
performance-evaluation surface.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("microbiome_cognitive_proxy_index", MetricUnit.RATIO,
               default=0.0),  # no alert threshold — research-stage, advisory only
]


class MicrobiomeProxySensor(ProviderSensor):
    """Stub sensor reserving the microbiome-cognitive-proxy metric shape."""

    budget_key = "internal_sensor"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("crew_load.microbiome_proxy", Layer.L1, "cognitive_load",
                         METRICS, provider)
