"""
Symbol Integration Index (SII) — v0.3.0, Lotus Protocol §IV extraction.

Integration depth = how many other Symbols would have to change if this one
disappeared, computed as a weighted dependent count over the symbol reference
graph. [FACT: lotus_whitepaper.docx §IV; INFERENCE: formula and thresholds
are this spec's proposal, ASSUMPTION-tagged in src/sensors/constants.py]

Edges source from: concept tag co-occurrence (ConceptResonanceDetector tag
registry), anchor reference chains, relay capsule dependencies. Stdlib-only.

Anchor symbols (EOS_SEED_ORION, Picard_Delta_3) are maximum-depth by
construction: any connection loss involving them classifies as rupture.
"""

from __future__ import annotations

import logging
import statistics
import threading
from collections import defaultdict
from typing import Dict, List, Optional, Set

from src.sensors import ANCHOR_SEED, ETHICS_PROTOCOL
from src.sensors import constants as C
from src.sensors.core.reading_types import (
    IntegrationDepthReading,
    PreSignature,
    WeightedPreSignature,
)
from src.sensors.core.sensor_base import RollingWindow, utcnow

logger = logging.getLogger(__name__)

#: Symbols pinned at maximum depth regardless of observed graph.
PINNED_MAX_DEPTH: Set[str] = {ANCHOR_SEED, ETHICS_PROTOCOL}


class SymbolIntegrationIndex:
    """Maintains the symbol reference graph and computes integration depth."""

    CORE_THRESHOLD = C.SII_CORE_THRESHOLD
    PERIPHERY_THRESHOLD = C.SII_PERIPHERY_THRESHOLD

    def __init__(self):
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        self.depth_history = RollingWindow(C.DEFAULT_OBSERVATION_WINDOW_SECONDS)
        self._lock = threading.Lock()

    # -- graph maintenance -----------------------------------------------------

    def record_reference(self, symbol_id: str, referenced_by: str) -> None:
        with self._lock:
            self.edges[symbol_id].add(referenced_by)

    def remove_reference(self, symbol_id: str, referenced_by: str) -> None:
        """Connection loss — tracked for rupture-candidate detection."""
        with self._lock:
            self.edges.get(symbol_id, set()).discard(referenced_by)

    # -- depth computation -------------------------------------------------------

    def _raw_depth(self, symbol_id: str) -> float:
        direct = self.edges.get(symbol_id, set())
        transitive: Set[str] = set()
        for d in direct:
            transitive |= self.edges.get(d, set())
        transitive -= direct
        return len(direct) + C.SII_TRANSITIVE_WEIGHT * len(transitive)

    def depth(self, symbol_id: str) -> float:
        """Normalized integration depth (0-1 within the current graph).

        Direct dependents weight 1.0; 1-hop transitive dependents weight 0.3.
        Anchor symbols are pinned to 1.0 by construction.
        """
        if symbol_id in PINNED_MAX_DEPTH:
            return 1.0
        with self._lock:
            raw = self._raw_depth(symbol_id)
            max_raw = max(
                (self._raw_depth(s) for s in self.edges), default=1.0
            )
        return raw / max(max_raw, 1.0)

    def snapshot(self) -> IntegrationDepthReading:
        with self._lock:
            symbols = set(self.edges) | PINNED_MAX_DEPTH
        depths = {s: self.depth(s) for s in symbols}
        now = utcnow()

        # Depth deltas vs. window-old snapshot
        history = self.depth_history.items()
        old: Dict[str, float] = history[0]["depths"] if history else {}
        deltas = {s: depths[s] - old.get(s, depths[s]) for s in depths}

        # Rupture candidates: core symbols losing connections rapidly
        rupture = [
            s for s, d in depths.items()
            if d >= self.CORE_THRESHOLD
            and deltas.get(s, 0.0) < -C.SII_RUPTURE_LOSS_RATE
        ]

        reading = IntegrationDepthReading(
            timestamp=now,
            symbol_count=len(depths),
            depths=depths,
            core_symbols=sorted(s for s, d in depths.items()
                                if d >= self.CORE_THRESHOLD),
            peripheral_symbols=sorted(s for s, d in depths.items()
                                      if d < self.PERIPHERY_THRESHOLD),
            median_depth=statistics.median(depths.values()) if depths else 0.0,
            depth_deltas_1h=deltas,
            rupture_candidates=rupture,
        )
        self.depth_history.append({"timestamp": now, "depths": depths})
        return reading

    # -- pre-signature weighting (v0.3.0 classification rules) --------------------

    def weight_presignature(
        self,
        presig: PreSignature,
        symbol_id: Optional[str] = None,
        connection_loss_rate_per_hour: float = 0.0,
        correlated_periphery_count: int = 1,
    ) -> WeightedPreSignature:
        """Apply integration-depth weighting and classify.

        | depth >= 0.8 AND loss > 10%/hr          -> rupture (CRITICAL, bypass trend)
        | 0.2 <= depth < 0.8                       -> drift (standard pipeline)
        | depth < 0.2, isolated                    -> peripheral_noise (advisory)
        | depth < 0.2, >= 5 correlated in window   -> drift (clustered periphery)
        """
        d = self.depth(symbol_id) if symbol_id else 0.5
        if d >= self.CORE_THRESHOLD and \
                connection_loss_rate_per_hour > C.SII_RUPTURE_LOSS_RATE:
            classification = "rupture"
        elif d < self.PERIPHERY_THRESHOLD:
            classification = (
                "drift"
                if correlated_periphery_count >= C.SII_PERIPHERY_CLUSTER_MIN
                else "peripheral_noise"
            )
        else:
            classification = "drift"

        weighted = WeightedPreSignature(
            signature_id=presig.signature_id,
            signature_type=presig.signature_type,
            magnitude=presig.magnitude,
            location=presig.location,
            first_detected=presig.first_detected,
            predicted_impact=presig.predicted_impact,
            depth_weight=d,
            priority=presig.magnitude * (0.3 + 0.7 * d),
            classification=classification,
        )
        if classification == "rupture":
            logger.critical(
                "RUPTURE: %s at %s (depth=%.2f, loss=%.2f/hr) — "
                "bypassing trend analysis; alerting L3 governance",
                presig.signature_type, presig.location, d,
                connection_loss_rate_per_hour,
            )
        return weighted
