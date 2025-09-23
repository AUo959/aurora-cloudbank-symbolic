"""Utilities for analyzing ARC chain export payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def _parse_timestamp(value: str) -> datetime:
    """Parse ISO 8601 timestamps with optional trailing Z into aware datetimes."""
    if not value:
        raise ValueError("timestamp value is required")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_drift(value: Optional[str]) -> Optional[float]:
    """Convert drift strings like '-0.3%' or 'Δ0.000' into floats."""
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    cleaned = cleaned.replace("Δ", "")
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]
    cleaned = cleaned.replace("+", "")
    cleaned = cleaned.replace("%", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


@dataclass(eq=True)
class ArcEvent:
    """Single ARC chain event."""

    event_type: str
    timestamp: datetime
    author: str
    summary: str
    anchor_pair: Tuple[Optional[str], Optional[str]]
    propagate_to: Sequence[str]
    drift_delta: Optional[float]
    raw: Dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArcEvent":
        anchor_pair: Iterable[Optional[str]] = data.get("anchor_pair") or (None, None)
        if isinstance(anchor_pair, (list, tuple)):
            values: List[Optional[str]] = list(anchor_pair)[:2]
            while len(values) < 2:
                values.append(None)
            anchor_tuple = (values[0], values[1])
        else:
            anchor_tuple = (None, None)

        return cls(
            event_type=data.get("type", "UNKNOWN"),
            timestamp=_parse_timestamp(data["timestamp"]),
            author=data.get("by", "unknown"),
            summary=data.get("summary", ""),
            anchor_pair=anchor_tuple,
            propagate_to=tuple(data.get("propagate_to", [])),
            drift_delta=_parse_drift(data.get("driftlog_delta")),
            raw=data,
        )


@dataclass(eq=True)
class ArcClosure:
    """Closure metadata for ARC chains."""

    sealed_by: str
    timestamp: datetime
    summary: str
    archive_ready: bool
    raw: Dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArcClosure":
        return cls(
            sealed_by=data.get("sealed_by", "unknown"),
            timestamp=_parse_timestamp(data["timestamp"]),
            summary=data.get("summary", ""),
            archive_ready=bool(data.get("archive_ready", False)),
            raw=data,
        )


class ArcChainProcessor:
    """Parser and analyzer for ARC chain export payloads."""

    EXPECTED_SCHEMA_PREFIX = "ARC_CHAIN_EXPORT_SCHEMA"

    def __init__(self, payload: Dict[str, Any], events: List[ArcEvent], closure: Optional[ArcClosure]):
        self.payload = payload
        self.events = events
        self.closure = closure

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArcChainProcessor":
        schema = data.get("schema", "")
        if not schema.startswith(cls.EXPECTED_SCHEMA_PREFIX):
            raise ValueError(f"Unsupported ARC schema: {schema}")

        arc_chain = data.get("arc_chain", [])
        events = [ArcEvent.from_dict(item) for item in arc_chain]
        closure = ArcClosure.from_dict(data["closure"]) if data.get("closure") else None
        return cls(data, events, closure)

    @classmethod
    def from_file(cls, file_path: Path | str) -> "ArcChainProcessor":
        path = Path(file_path)
        content = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(content)

    def detect_anomalies(self) -> List[str]:
        anomalies: List[str] = []
        if not self.events:
            anomalies.append("no_events_present")
            return anomalies

        sorted_events = sorted(self.events, key=lambda event: event.timestamp)
        if sorted_events != self.events:
            anomalies.append("timeline_out_of_order")

        for event in self.events:
            if not event.anchor_pair[0] or not event.anchor_pair[1]:
                anomalies.append(f"missing_anchor_pair::{event.event_type}")
            if not event.propagate_to:
                anomalies.append(f"missing_propagation_targets::{event.event_type}")
        return anomalies

    def build_summary(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        event_counts: Dict[str, int] = {}
        participants: List[str] = []
        propagation_targets: List[str] = []
        anchor_pairs: List[Tuple[Optional[str], Optional[str]]] = []
        drift_values: List[float] = []

        for event in self.events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
            participants.append(event.author)
            propagation_targets.extend(event.propagate_to)
            anchor_pairs.append(event.anchor_pair)
            if event.drift_delta is not None:
                drift_values.append(event.drift_delta)

        unique_participants = sorted({p for p in participants if p})
        unique_targets = sorted({t for t in propagation_targets if t})
        unique_anchors = sorted({anchor for pair in anchor_pairs for anchor in pair if anchor})

        drift_metrics = {
            "max_delta": max(drift_values) if drift_values else 0.0,
            "min_delta": min(drift_values) if drift_values else 0.0,
            "max_abs_delta": max((abs(value) for value in drift_values), default=0.0),
            "requires_attention": any(abs(value) >= 1.0 for value in drift_values),
        }

        timeline_start = self.events[0].timestamp if self.events else None
        timeline_end = self.events[-1].timestamp if self.events else None

        closure_summary: Dict[str, Any]
        if self.closure:
            closure_summary = {
                "sealed": True,
                "sealed_by": self.closure.sealed_by,
                "timestamp": self.closure.timestamp.isoformat(),
                "summary": self.closure.summary,
                "archive_ready": self.closure.archive_ready,
            }
        else:
            closure_summary = {"sealed": False}

        validation = self.payload.get("validation", {})
        summary = {
            "schema": self.payload.get("schema"),
            "thread_id": self.payload.get("thread_id"),
            "linked_threads": self.payload.get("linked_threads", []),
            "total_events": len(self.events),
            "event_types": event_counts,
            "participants": unique_participants,
            "propagation_targets": unique_targets,
            "anchor_pairs": unique_anchors,
            "timeline": {
                "start": timeline_start.isoformat() if timeline_start else None,
                "end": timeline_end.isoformat() if timeline_end else None,
            },
            "drift_metrics": drift_metrics,
            "closure": closure_summary,
            "validation_passed": bool(validation.get("validation_passed")),
            "signature": self.payload.get("signature"),
            "analysis_generated_at": now,
        }

        anomalies = self.detect_anomalies()
        if anomalies:
            summary["anomalies"] = anomalies

        return summary

    def export_enhanced_payload(self) -> Dict[str, Any]:
        enhanced = dict(self.payload)
        enhanced.setdefault("enhancements", {})
        summary = self.build_summary()
        enhanced["enhancements"]["summary"] = summary
        enhanced["enhancements"]["anomalies"] = summary.get("anomalies", [])
        enhanced["enhancements"]["generated_at"] = datetime.now(timezone.utc).isoformat()
        return enhanced
