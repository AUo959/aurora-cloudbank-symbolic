"""Observatory reality-anchor sensor — EOS_SEED_ORION chain verification.

Anchor symbols are maximum-depth by construction (v0.3.0 §Effect on alert
economics): any failure here is rupture-class. Never decimated.
Booleans are encoded 1.0 (true) / 0.0 (false).
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from src.sensors import ANCHOR_SEED
from src.sensors.core.reading_types import Layer, MetricUnit
from src.sensors.core.sensor_base import MetricSpec, ProviderSensor

METRICS = [
    MetricSpec("anchor_chain_valid", MetricUnit.RATIO,
               lambda v: v < 1.0, f"{ANCHOR_SEED} verification FAILED", default=1.0),
    MetricSpec("l1_reality_confidence", MetricUnit.RATIO,
               lambda v: v < 0.99, "L1 reality confidence < 0.99", default=1.0),
    MetricSpec("custody_chain_complete", MetricUnit.RATIO,
               lambda v: v < 1.0, "state custody chain incomplete", default=1.0),
]


class RealityAnchorSensor(ProviderSensor):
    budget_key = "observatory_physical"

    def __init__(self, provider: Optional[Callable[[], Dict[str, float]]] = None):
        super().__init__("observatory.reality_anchor", Layer.L2, "reality_anchor",
                         METRICS, provider)
        self.critical = True
