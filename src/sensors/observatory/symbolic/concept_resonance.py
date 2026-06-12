"""
Concept Resonance Detector — cross-layer concept echo detection.

RQ-1 taxonomy (v0.3.0): tags are namespaced canonical artifacts
``{layer}:{domain}:{concept}`` (e.g. ``L2:faction:galactic_marshals``).
Tags absent from the canonical registry are prefixed ``uncanonized:`` and
quarantined from classification — counted (frequency accumulates toward
later promotion) but always classified ``uncertain``, never ``convergence``
or ``bleed``. New tags auto-enter STAGING on first observation.

Classification rules:
- L2<->L3 resonance: convergence (narrative informs simulation — expected)
- L1<->L2 or L1<->L3: bleed (reality mixing with simulation/narrative)

One-way observation: outputs feed relay governance, never agents.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from src.sensors import constants as C
from src.sensors.core.reading_types import (
    ConceptResonanceReading,
    Layer,
    ResonanceEvent,
    SensorReading,
)
from src.sensors.core.sensor_base import RollingWindow, Sensor, utcnow

logger = logging.getLogger(__name__)

UNCANONIZED_PREFIX = "uncanonized:"


@dataclass
class AgentOutput:
    """Minimal agent-output view the detector consumes."""
    concept_tags: List[str]
    semantic_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConceptResonanceDetector(Sensor):
    """Glyph-tag correlation + semantic hash comparison. No ML required."""

    budget_key = "concept_resonance"

    def __init__(self, canonical_registry: Optional[Set[str]] = None):
        super().__init__("observatory.symbolic.concept_resonance",
                         Layer.L3, "resonance")
        #: RQ-1 seed registries: GUMAS enums, relay/glyph agents, L1 systems.
        self.canonical_registry: Set[str] = set(canonical_registry or set())
        #: Tags observed but not canonized — STAGING queue per RQ-1.
        self.staging_tags: Dict[str, int] = defaultdict(int)
        self.tag_registry: Dict[str, Dict[str, int]] = {}
        self.first_seen: Dict[str, Any] = {}
        self.hash_history = RollingWindow(C.DEFAULT_OBSERVATION_WINDOW_SECONDS)
        self.resonance_threshold = C.RESONANCE_THRESHOLD
        self._lock = threading.Lock()
        #: SII edge feed (set by wiring layer, optional)
        self.sii = None

    # -- ingestion -------------------------------------------------------------

    def _normalize_tag(self, tag: str) -> str:
        """RQ-1 unknown-tag handling: quarantine vocabulary canon hasn't defined."""
        if tag in self.canonical_registry or tag.startswith(UNCANONIZED_PREFIX):
            return tag if tag in self.canonical_registry else tag
        if tag not in self.canonical_registry:
            self.staging_tags[tag] += 1
            return f"{UNCANONIZED_PREFIX}{tag}"
        return tag

    def ingest_output(self, layer: str, output: AgentOutput) -> None:
        """Track concept tags from agent outputs (observation only)."""
        now = utcnow()
        with self._lock:
            for raw in output.concept_tags:
                tag = self._normalize_tag(raw)
                if tag not in self.tag_registry:
                    self.tag_registry[tag] = defaultdict(int)
                    self.first_seen[tag] = now
                self.tag_registry[tag][layer] += 1
                # Feed SII: co-occurring tags reference each other
                if self.sii is not None and not tag.startswith(UNCANONIZED_PREFIX):
                    for other in output.concept_tags:
                        o = self._normalize_tag(other)
                        if o != tag and not o.startswith(UNCANONIZED_PREFIX):
                            self.sii.record_reference(tag, o)
            self.hash_history.append({
                "layer": layer,
                "hash": output.semantic_hash,
                "tags": list(output.concept_tags),
                "timestamp": now,
            })

    # -- detection ---------------------------------------------------------------

    def detect_resonance(self) -> ConceptResonanceReading:
        """Identify concepts appearing across multiple layers."""
        resonances: List[ResonanceEvent] = []
        with self._lock:
            registry = {k: dict(v) for k, v in self.tag_registry.items()}

        for concept, layer_counts in registry.items():
            if len(layer_counts) <= 1:
                continue
            layers = list(layer_counts.keys())
            classification = self._classify_resonance(concept, layers)
            resonances.append(ResonanceEvent(
                event_id=f"res_{concept}_{utcnow().timestamp()}",
                concept=concept,
                source_layer=self._infer_origin(concept, layer_counts),
                echo_locations=layers,
                semantic_similarity=self._calculate_similarity(concept),
                classification=classification,
                first_observed=self.first_seen.get(concept, utcnow()),
                frequency=sum(layer_counts.values()),
            ))

        bleeds = [r for r in resonances if r.classification == "bleed"]
        return ConceptResonanceReading(
            timestamp=utcnow(),
            observation_window_seconds=C.DEFAULT_OBSERVATION_WINDOW_SECONDS,
            resonances=resonances,
            resonance_count=len(resonances),
            narrative_convergences=[r.concept for r in resonances
                                    if r.classification == "convergence"],
            metaphor_bleeds=[r.concept for r in bleeds],
            resonance_intensity=len(resonances) / max(len(registry), 1),
            bleed_risk=len(bleeds) / max(len(resonances), 1),
        )

    def _classify_resonance(self, concept: str, layers: List[str]) -> str:
        """RQ-1: uncanonized tags are always 'uncertain' — quarantined from
        layer-contamination judgments. Otherwise:
        L1 with L2/L3 => bleed; L2 with L3 => convergence."""
        if concept.startswith(UNCANONIZED_PREFIX):
            return "uncertain"
        if "L1" in layers and ("L2" in layers or "L3" in layers):
            return "bleed"
        if "L2" in layers and "L3" in layers:
            return "convergence"
        return "uncertain"

    def _infer_origin(self, concept: str, layer_counts: Dict[str, int]) -> str:
        # RQ-1 namespaced tags carry their origin layer explicitly.
        base = concept[len(UNCANONIZED_PREFIX):] if \
            concept.startswith(UNCANONIZED_PREFIX) else concept
        if ":" in base:
            prefix = base.split(":", 1)[0]
            if prefix in ("L1", "L2", "L3"):
                return prefix
        return max(layer_counts, key=layer_counts.get)

    def _calculate_similarity(self, concept: str) -> float:
        """Fraction of recent hash-history entries containing the concept."""
        items = self.hash_history.items()
        if not items:
            return 0.0
        hits = sum(1 for h in items if concept in h["tags"]
                   or concept.removeprefix(UNCANONIZED_PREFIX) in h["tags"])
        return min(hits / len(items), 1.0)

    # -- Sensor interface -----------------------------------------------------------

    def ingest(self, source: str, payload: Dict[str, Any]) -> None:
        self.ingest_output(
            payload.get("layer", source),
            AgentOutput(
                concept_tags=payload.get("concept_tags", []),
                semantic_hash=payload.get("semantic_hash", ""),
            ),
        )

    def read(self) -> SensorReading:
        r = self.detect_resonance()
        alerts = []
        if r.bleed_risk > C.BLEED_RISK_ALERT:
            alerts.append(f"bleed risk {r.bleed_risk:.2f} > {C.BLEED_RISK_ALERT}")
        return self._reading(
            {"resonance_intensity": r.resonance_intensity,
             "bleed_risk": r.bleed_risk,
             "resonance_count": float(r.resonance_count),
             "staging_tag_count": float(len(self.staging_tags))},
            alerts=alerts,
            metadata={"reading": r},
        )
