"""Utilities for enriching ARC chain export payloads.

This module adds structure around ARC chain exports so they can be
consumed by Aurora CloudBank symbolic workflows without altering the
original export schema. The enhancer preserves symbolic anchors (e.g.,
T1 markers) and computes additional metadata that downstream
orchestrators rely on when rehydrating thread context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
import json

ISO_Z_SUFFIX = "Z"
T1_CONTINUITY_ANCHOR = "T1_ARC_CHAIN_CONTINUITY"
ANCHOR_SEED = "ARC_CHAIN_ENHANCER_SEED_V1"


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp string into an aware ``datetime``.

    The ARC export uses ``Z`` to mark UTC. We normalise it so Python can
    parse it into a timezone aware ``datetime``. ``None`` is returned
    unchanged to keep optional semantics intact.
    """

    if not value:
        return None

    if value.endswith(ISO_Z_SUFFIX):
        value = f"{value[:-1]}+00:00"

    return datetime.fromisoformat(value)


def _format_timestamp(value: Optional[datetime]) -> Optional[str]:
    """Render ``datetime`` values back to canonical ISO strings."""

    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_drift(value: Optional[str]) -> Optional[float]:
    """Convert drift log deltas into floats when possible.

    Values can look like ``"-0.3%"`` or ``"Δ0.000"``. Non-parsable data
    yields ``None`` so that callers retain original context strings.
    """

    if value is None:
        return None

    cleaned = value.strip().replace("Δ", "").replace("%", "")
    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


@dataclass
class ArcEvent:
    """Structured representation of a single ARC record."""

    arc_type: str
    timestamp: Optional[datetime]
    actor: str
    summary: str
    anchor_pair: Sequence[str]
    propagate_to: Sequence[str]
    driftlog_delta: Optional[str] = None
    parsed_drift: Optional[float] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.parsed_drift = _parse_drift(self.driftlog_delta)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ArcEvent":
        return cls(
            arc_type=payload.get("type", "UNKNOWN_ARC"),
            timestamp=_parse_timestamp(payload.get("timestamp")),
            actor=payload.get("by", "unknown"),
            summary=payload.get("summary", ""),
            anchor_pair=tuple(payload.get("anchor_pair", ())),
            propagate_to=tuple(payload.get("propagate_to", ())),
            driftlog_delta=payload.get("driftlog_delta"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.arc_type,
            "timestamp": _format_timestamp(self.timestamp),
            "by": self.actor,
            "summary": self.summary,
            "anchor_pair": list(self.anchor_pair),
            "propagate_to": list(self.propagate_to),
            "driftlog_delta": self.driftlog_delta,
            "parsed_drift": self.parsed_drift,
        }


@dataclass
class ArcClosure:
    """Metadata describing the closure segment of an ARC export."""

    closure_type: str
    sealed_by: str
    timestamp: Optional[datetime]
    summary: str
    archive_ready: bool

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ArcClosure":
        return cls(
            closure_type=payload.get("type", "CLOSURE_ARC"),
            sealed_by=payload.get("sealed_by", "unknown"),
            timestamp=_parse_timestamp(payload.get("timestamp")),
            summary=payload.get("summary", ""),
            archive_ready=bool(payload.get("archive_ready", False)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.closure_type,
            "sealed_by": self.sealed_by,
            "timestamp": _format_timestamp(self.timestamp),
            "summary": self.summary,
            "archive_ready": self.archive_ready,
        }


class ArcChainEnhancer:
    """Enhance ARC chain exports with additional analytics and anchors."""

    def __init__(self, raw_export: Dict[str, Any]):
        self.raw_export = raw_export
        self.schema = raw_export.get("schema", "")
        self.exported_at = _parse_timestamp(raw_export.get("exported_at"))
        self.thread_id = raw_export.get("thread_id", "")
        self.linked_threads = tuple(raw_export.get("linked_threads", ()))
        self.signature = raw_export.get("signature")
        self.validation = raw_export.get("validation", {})

        self.arc_chain: List[ArcEvent] = [ArcEvent.from_dict(item) for item in raw_export.get("arc_chain", [])]
        self.closure = ArcClosure.from_dict(raw_export.get("closure", {}))

    @classmethod
    def from_file(cls, path: Path) -> "ArcChainEnhancer":
        with path.open("r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    def _arc_type_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for arc in self.arc_chain:
            counts[arc.arc_type] = counts.get(arc.arc_type, 0) + 1
        return counts

    def _participants(self) -> Dict[str, Any]:
        actors = {arc.actor for arc in self.arc_chain if arc.actor}
        actors.add(self.closure.sealed_by)
        return {
            "actors": sorted(actors),
            "system_initiated": "system" in actors,
        }

    def _timeline(self) -> Dict[str, Any]:
        timestamps = [arc.timestamp for arc in self.arc_chain if arc.timestamp]
        if self.closure.timestamp:
            timestamps.append(self.closure.timestamp)

        if not timestamps:
            return {
                "first_event": None,
                "last_event": None,
                "duration_seconds": None,
            }

        first = min(timestamps)
        last = max(timestamps)
        duration = (last - first).total_seconds()

        return {
            "first_event": _format_timestamp(first),
            "last_event": _format_timestamp(last),
            "duration_seconds": duration,
        }

    def _anchor_registry(self) -> Dict[str, Any]:
        anchors = {
            "t1_marker": T1_CONTINUITY_ANCHOR,
            "anchor_seed": ANCHOR_SEED,
            "anchor_pairs": [list(arc.anchor_pair) for arc in self.arc_chain if arc.anchor_pair],
        }
        return anchors

    def _drift_metrics(self) -> Dict[str, Any]:
        drift_values = [arc.parsed_drift for arc in self.arc_chain if arc.parsed_drift is not None]
        net_drift = sum(drift_values) if drift_values else 0.0
        return {
            "net_drift": net_drift,
            "drift_events": [
                {
                    "type": arc.arc_type,
                    "timestamp": _format_timestamp(arc.timestamp),
                    "value": arc.driftlog_delta,
                    "parsed_value": arc.parsed_drift,
                }
                for arc in self.arc_chain
                if arc.driftlog_delta is not None
            ],
        }

    def _propagation_summary(self) -> Dict[str, Any]:
        propagation_targets: List[str] = []
        for arc in self.arc_chain:
            for target in arc.propagate_to:
                if target not in propagation_targets:
                    propagation_targets.append(target)
        return {
            "unique_targets": propagation_targets,
            "propagation_events": [
                {
                    "type": arc.arc_type,
                    "timestamp": _format_timestamp(arc.timestamp),
                    "targets": list(arc.propagate_to),
                }
                for arc in self.arc_chain
                if arc.propagate_to
            ],
        }

    def enhanced_payload(self) -> Dict[str, Any]:
        """Construct the enriched payload while preserving raw export data."""

        return {
            "schema": self.schema,
            "thread_id": self.thread_id,
            "exported_at": _format_timestamp(self.exported_at),
            "linked_threads": list(self.linked_threads),
            "signature": self.signature,
            "validation": self.validation,
            "raw_events": [arc.to_dict() for arc in self.arc_chain],
            "closure": self.closure.to_dict(),
            "metadata": {
                "total_arcs": len(self.arc_chain),
                "arc_types": self._arc_type_counts(),
                "participants": self._participants(),
                "timeline": self._timeline(),
                "drift": self._drift_metrics(),
                "propagation": self._propagation_summary(),
                "symbolic_anchors": self._anchor_registry(),
            },
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Serialise the enhanced payload to JSON."""

        return json.dumps(self.enhanced_payload(), indent=indent, sort_keys=False)


def enhance_arc_export(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Functional helper returning the enhanced payload.

    This wrapper makes it easy for callers that prefer a function-style
    API over instantiating ``ArcChainEnhancer`` directly.
    """

    return ArcChainEnhancer(payload).enhanced_payload()
