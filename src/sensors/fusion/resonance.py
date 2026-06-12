"""Cross-Layer Resonance Calculator — pairwise layer sync measurement."""

from __future__ import annotations

from statistics import harmonic_mean
from typing import Dict, List, Optional

from src.sensors.core.reading_types import ResonanceReading
from src.sensors.core.sensor_base import utcnow


class CrossLayerResonanceCalculator:
    """Computes pairwise and system resonance from layer activity signatures.

    Pairwise resonance compares per-layer normalized signal vectors (cosine
    over shared keys); the system score is the harmonic mean, which punishes
    any single desynchronized pair.
    """

    def __init__(self, dissonance_threshold: float = 0.5):
        self.dissonance_threshold = dissonance_threshold
        self._layer_state: Dict[str, Dict[str, float]] = {}

    def update_layer(self, layer: str, signature: Dict[str, float]) -> None:
        self._layer_state[layer] = dict(signature)

    def _pair(self, a: str, b: str) -> float:
        sa, sb = self._layer_state.get(a), self._layer_state.get(b)
        if not sa or not sb:
            return 1.0  # absent evidence: assume sync, fusion will refine
        keys = set(sa) & set(sb)
        if not keys:
            return 1.0
        num = sum(sa[k] * sb[k] for k in keys)
        da = sum(v * v for v in sa.values()) ** 0.5
        db = sum(v * v for v in sb.values()) ** 0.5
        if da == 0 or db == 0:
            return 1.0
        return max(0.0, min(num / (da * db), 1.0))

    def calculate(self) -> ResonanceReading:
        l1l2 = self._pair("L1", "L2")
        l2l3 = self._pair("L2", "L3")
        l1l3 = self._pair("L1", "L3")
        pairs = {"L1-L2": l1l2, "L2-L3": l2l3, "L1-L3": l1l3}
        positives = [max(v, 1e-9) for v in pairs.values()]
        system = harmonic_mean(positives)

        dissonant: List[str] = [k for k, v in pairs.items()
                                if v < self.dissonance_threshold]
        severity = (1.0 - min(pairs.values())) if dissonant else 0.0

        return ResonanceReading(
            timestamp=utcnow(),
            l1_l2_resonance=l1l2,
            l2_l3_resonance=l2l3,
            l1_l3_resonance=l1l3,
            system_resonance=system,
            dissonance_detected=bool(dissonant),
            dissonance_locations=dissonant,
            dissonance_severity=severity,
        )
