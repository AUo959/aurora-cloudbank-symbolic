"""Aurora CloudBank – ARC Chain Enhancer.

This module provides analytics and validation helpers for ARC chain exports
captured from GUMAS continuity threads. The implementation keeps Aurora's
symbolic anchors intact while exposing structured accessors that can be used by
higher-level coordination pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ARC_CHAIN_SCHEMA = "ARC_CHAIN_EXPORT_SCHEMA_v1.0"
_TIMESTAMP_Z_SUFFIX = "Z"
_ALLOWED_PROPAGATION_TARGETS: Sequence[str] = ("parent", "sibling", "child", "upstream", "downstream")


class ArcChainValidationError(ValueError):
    """Raised when ARC chain data fails structural validation."""


def _parse_iso8601(timestamp: str) -> datetime:
    """Convert ISO-8601 timestamps (supporting a trailing ``Z``) into ``datetime`` instances."""

    if not timestamp:
        raise ArcChainValidationError("Timestamp value is required for ARC entries.")

    ts_value = timestamp.strip()
    if ts_value.endswith(_TIMESTAMP_Z_SUFFIX):
        ts_value = f"{ts_value[:-1]}+00:00"

    try:
        return datetime.fromisoformat(ts_value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ArcChainValidationError(f"Invalid ARC timestamp: {timestamp}") from exc


def _normalise_drift(raw_value: Optional[str]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    """Normalise drift values into percent and absolute deltas.

    Percent drift returns values in percentage points (e.g. ``-0.3`` for ``-0.3%``).
    Absolute drift captures raw ``Δ`` metrics without unit conversion.
    """

    if raw_value is None:
        return None, None

    cleaned = raw_value.strip()
    if not cleaned:
        return None, None

    if cleaned.startswith("Δ"):
        try:
            return None, Decimal(cleaned[1:])
        except (InvalidOperation, ValueError) as exc:  # pragma: no cover - guard unexpected payloads
            raise ArcChainValidationError(f"Invalid absolute drift value: {raw_value}") from exc

    if cleaned.endswith("%"):
        try:
            return Decimal(cleaned[:-1]), None
        except (InvalidOperation, ValueError) as exc:  # pragma: no cover - guard unexpected payloads
            raise ArcChainValidationError(f"Invalid percent drift value: {raw_value}") from exc

    # Accept numeric strings without modifiers as absolute deltas.
    try:
        return None, Decimal(cleaned)
    except (InvalidOperation, ValueError) as exc:  # pragma: no cover - guard unexpected payloads
        raise ArcChainValidationError(f"Unrecognised drift value: {raw_value}") from exc


@dataclass(frozen=True)
class ArcChainEntry:
    """Representation of a single ARC chain event."""

    arc_type: str
    timestamp: datetime
    initiator: str
    summary: str
    anchor_pair: Tuple[str, str]
    propagate_to: Tuple[str, ...]
    driftlog_raw: Optional[str] = None
    driftlog_percent: Optional[Decimal] = None
    driftlog_absolute: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArcChainEntry":
        anchor_pair = tuple(data.get("anchor_pair", ()))
        if len(anchor_pair) != 2:
            raise ArcChainValidationError("ARC entries must contain an anchor_pair with two elements.")

        propagate_to = tuple(data.get("propagate_to", ()))
        if not propagate_to:
            raise ArcChainValidationError("ARC entries require at least one propagation target.")

        drift_percent, drift_absolute = _normalise_drift(data.get("driftlog_delta"))

        return cls(
            arc_type=data["type"],
            timestamp=_parse_iso8601(data["timestamp"]),
            initiator=data.get("by", "unknown"),
            summary=data.get("summary", ""),
            anchor_pair=(str(anchor_pair[0]), str(anchor_pair[1])),
            propagate_to=tuple(str(target) for target in propagate_to),
            driftlog_raw=data.get("driftlog_delta"),
            driftlog_percent=drift_percent,
            driftlog_absolute=drift_absolute,
        )

    def to_timeline_dict(self) -> Dict[str, Any]:
        """Convert entry into a serialisable timeline dictionary."""

        return {
            "type": self.arc_type,
            "timestamp": self.timestamp.isoformat(),
            "by": self.initiator,
            "summary": self.summary,
            "anchor_pair": list(self.anchor_pair),
            "propagate_to": list(self.propagate_to),
            "driftlog_delta": self.driftlog_raw,
        }


@dataclass(frozen=True)
class ArcClosure:
    """Final ARC closure marker."""

    sealed_by: str
    timestamp: datetime
    summary: str
    archive_ready: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArcClosure":
        if data.get("type") != "CLOSURE_ARC":
            raise ArcChainValidationError("Closure payload must declare type 'CLOSURE_ARC'.")

        return cls(
            sealed_by=data.get("sealed_by", "unknown"),
            timestamp=_parse_iso8601(data["timestamp"]),
            summary=data.get("summary", ""),
            archive_ready=bool(data.get("archive_ready", False)),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialisable representation of the closure marker."""

        return {
            "sealed_by": self.sealed_by,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "archive_ready": self.archive_ready,
        }


@dataclass
class ArcChainEnhancer:
    """Utility class that augments ARC chain exports with validation and analytics."""

    payload: Dict[str, Any]
    schema: str = field(init=False)
    exported_at: datetime = field(init=False)
    thread_id: str = field(init=False)
    linked_threads: Tuple[str, ...] = field(init=False)
    entries: Tuple[ArcChainEntry, ...] = field(init=False)
    closure: Optional[ArcClosure] = field(init=False)

    def __post_init__(self) -> None:
        self.schema = self.payload.get("schema", "")
        if self.schema != ARC_CHAIN_SCHEMA:
            raise ArcChainValidationError(
                f"Unsupported ARC schema '{self.schema}'. Expected '{ARC_CHAIN_SCHEMA}'."
            )

        self.exported_at = _parse_iso8601(self.payload.get("exported_at", ""))
        self.thread_id = self.payload.get("thread_id", "")
        self.linked_threads = tuple(self.payload.get("linked_threads", ()))
        self.entries = tuple(ArcChainEntry.from_dict(item) for item in self.payload.get("arc_chain", []))
        if not self.entries:
            raise ArcChainValidationError("ARC chain exports require at least one entry.")

        closure_payload = self.payload.get("closure")
        self.closure = ArcClosure.from_dict(closure_payload) if closure_payload else None

    def validate_anchor_sequence(self) -> bool:
        """Ensure anchor pairs form a contiguous chain."""

        if not self.entries:
            return False

        for first, second in zip(self.entries, self.entries[1:]):
            if first.anchor_pair[1] != second.anchor_pair[0]:
                return False

        return True

    def validate_propagation_targets(self) -> bool:
        """Verify propagation targets are non-empty and within the allowed vocabulary when applicable."""

        for entry in self.entries:
            if not entry.propagate_to:
                return False

            for target in entry.propagate_to:
                if target not in _ALLOWED_PROPAGATION_TARGETS:
                    # Allow forward-compatibility by accepting unknown targets that follow the naming convention.
                    if not target.islower() or "_" in target:
                        return False

        return True

    def calculate_drift_metrics(self) -> Dict[str, Any]:
        """Aggregate drift metrics across the chain."""

        percent_total = Decimal("0")
        percent_entries = 0
        absolute_total = Decimal("0")
        absolute_entries = 0

        for entry in self.entries:
            if entry.driftlog_percent is not None:
                percent_total += entry.driftlog_percent
                percent_entries += 1
            if entry.driftlog_absolute is not None:
                absolute_total += entry.driftlog_absolute
                absolute_entries += 1

        return {
            "entries_with_percent": percent_entries,
            "cumulative_percent": percent_total if percent_entries else Decimal("0"),
            "entries_with_absolute": absolute_entries,
            "cumulative_absolute": absolute_total if absolute_entries else Decimal("0"),
        }

    def build_anchor_sequence(self) -> List[str]:
        """Return the sequential list of anchors across the chain."""

        if not self.entries:
            return []

        sequence: List[str] = [self.entries[0].anchor_pair[0]]
        for entry in self.entries:
            sequence.append(entry.anchor_pair[1])

        return sequence

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run validation checks returning a structured diagnostics payload."""

        return {
            "schema_valid": self.schema == ARC_CHAIN_SCHEMA,
            "anchor_continuity": self.validate_anchor_sequence(),
            "propagation_targets_valid": self.validate_propagation_targets(),
            "closure_present": self.closure is not None,
        }

    def generate_summary(self) -> Dict[str, Any]:
        """Create a high-level summary containing anchors, drift metrics, and timeline details."""

        summary = {
            "schema": self.schema,
            "thread_id": self.thread_id,
            "linked_threads": list(self.linked_threads),
            "exported_at": self.exported_at.isoformat(),
            "total_entries": len(self.entries),
            "anchor_chain_integrity": self.validate_anchor_sequence(),
            "anchor_sequence": self.build_anchor_sequence(),
            "drift": self.calculate_drift_metrics(),
            "timeline": [entry.to_timeline_dict() for entry in self.entries],
            "diagnostics": self.run_diagnostics(),
        }

        if self.closure:
            summary["closure"] = self.closure.to_dict()

        return summary


__all__ = ["ArcChainEnhancer", "ArcChainValidationError", "ARC_CHAIN_SCHEMA"]
