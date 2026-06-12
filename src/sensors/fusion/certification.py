"""
Coherence Certification — the final, auditable verdict with chain of custody.

v0.3.0: symbolic_coherence consumes the Symbol Integration Index — rupture
candidates are blocking issues by construction.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from src.sensors import ANCHOR_SEED, ETHICS_PROTOCOL
from src.sensors.core.reading_types import CoherenceCertification
from src.sensors.core.sensor_base import utcnow


class CoherenceCertifier:
    """Aggregates component scores into a certified, hash-chained verdict."""

    def __init__(self, certified_by: str = "aurora.sensor_array.v0_3_0"):
        self.certified_by = certified_by
        self._previous_id: Optional[str] = None

    def certify(
        self,
        structural: float,
        operational: float,
        symbolic: float,
        temporal: float,
        layer_resonance: float,
        reality_grounding: float,
        anchor_verified: bool,
        blocking_issues: Optional[List[str]] = None,
        advisory_issues: Optional[List[str]] = None,
        rupture_candidates: Optional[List[str]] = None,
    ) -> CoherenceCertification:
        blocking = list(blocking_issues or [])
        advisory = list(advisory_issues or [])

        # v0.3.0: core-symbol rupture is always blocking.
        for symbol in rupture_candidates or []:
            blocking.append(f"rupture candidate: {symbol}")
        if not anchor_verified:
            blocking.append(f"{ANCHOR_SEED} anchor chain not verified")

        scores = {
            "structural": structural,
            "operational": operational,
            "symbolic": symbolic,
            "temporal": temporal,
            "layer_resonance": layer_resonance,
            "reality_grounding": reality_grounding,
        }
        coherent = not blocking and all(v >= 0.9 for v in scores.values())
        confidence = min(scores.values()) if scores else 0.0

        now = utcnow()
        cert_id = f"cert_{now.strftime('%Y%m%dT%H%M%S%f')}"
        payload: Dict[str, Any] = {
            "certification_id": cert_id,
            "timestamp": now.isoformat(),
            "scores": scores,
            "coherent": coherent,
            "blocking": blocking,
            "previous": self._previous_id,
            "anchor": ANCHOR_SEED,
            "ethics": ETHICS_PROTOCOL,
        }
        verification_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        cert = CoherenceCertification(
            timestamp=now,
            certification_id=cert_id,
            system_coherent=coherent,
            confidence=confidence,
            structural_coherence=structural,
            operational_coherence=operational,
            symbolic_coherence=symbolic,
            temporal_coherence=temporal,
            layer_resonance=layer_resonance,
            reality_grounding=reality_grounding,
            anchor_verified=anchor_verified,
            anchor_id=ANCHOR_SEED,
            ethics_protocol=ETHICS_PROTOCOL,
            blocking_issues=blocking,
            advisory_issues=advisory,
            certified_by=self.certified_by,
            verification_hash=verification_hash,
            previous_certification_id=self._previous_id,
        )
        self._previous_id = cert_id   # chain of custody
        return cert
