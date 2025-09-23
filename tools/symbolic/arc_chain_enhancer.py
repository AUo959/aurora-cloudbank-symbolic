"""ARC Chain Enhancer
=====================

Utility helpers for processing Aurora Record Chain (ARC) exports.

The enhancer focuses on light-weight validation and summary generation
so that ARC payloads can be integrated with the existing symbolic
infrastructure without mutating canonical constants (e.g. Picard_Delta_3
or ORION bridge settings). The implementation keeps transparency in
processing steps and surfaces the derived metrics explicitly in the
returned metadata block.

This module intentionally avoids external dependencies in order to
remain compatible with the constrained execution environments used by
Aurora CloudBank.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple
import copy


class ARCValidationError(ValueError):
    """Raised when an ARC export payload fails validation."""


def _parse_iso_timestamp(value: str) -> datetime:
    """Parse ISO-8601 timestamps while accepting ``Z`` suffix values."""

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def _parse_drift_delta(value: Optional[str]) -> Optional[float]:
    """Convert drift delta strings into numeric values.

    Supports values expressed with percentage symbols (``-0.3%``) or with
    the ``Δ`` prefix (``Δ0.000``). If the string cannot be parsed the
    function falls back to ``None`` so that calling code can decide how to
    handle missing information.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = value.strip()
    if not cleaned:
        return None

    cleaned = cleaned.replace("Δ", "").replace("delta", "").replace("%", "")

    try:
        return float(cleaned)
    except ValueError:
        return None


@dataclass(frozen=True)
class ARCEntry:
    """Single record inside an ARC chain."""

    arc_type: str
    timestamp: datetime
    author: str
    summary: str
    anchor_pair: Tuple[str, str]
    propagate_to: Tuple[str, ...]
    driftlog_delta: Optional[float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ARCEntry":
        """Create an :class:`ARCEntry` from raw dictionary data."""

        required_fields = ["type", "timestamp", "by", "summary", "anchor_pair", "propagate_to"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ARCValidationError(f"Missing required fields in ARC entry: {missing}")

        anchor_pair = data["anchor_pair"]
        if not isinstance(anchor_pair, (list, tuple)) or len(anchor_pair) != 2:
            raise ARCValidationError("anchor_pair must be a 2-element list or tuple")

        propagate_to = data.get("propagate_to", [])
        if not isinstance(propagate_to, Iterable):
            raise ARCValidationError("propagate_to must be an iterable")

        timestamp = _parse_iso_timestamp(str(data["timestamp"]))
        drift_delta = _parse_drift_delta(data.get("driftlog_delta"))

        return cls(
            arc_type=str(data["type"]),
            timestamp=timestamp,
            author=str(data["by"]),
            summary=str(data["summary"]),
            anchor_pair=(str(anchor_pair[0]), str(anchor_pair[1])),
            propagate_to=tuple(str(target) for target in propagate_to),
            driftlog_delta=drift_delta,
        )


class ARCChainEnhancer:
    """Enhance and summarise ARC export payloads."""

    T1_ANCHOR_SEED = "T1_ARC_CHAIN_ENHANCER"
    SRB_BRIDGE_ANCHOR = "SRB_ARC_CHAIN_BRIDGE"

    def __init__(self, arc_payload: Dict[str, Any]):
        self._raw_payload = copy.deepcopy(arc_payload)
        self.schema = ""
        self.exported_at: Optional[datetime] = None
        self.thread_id = ""
        self.entries: List[ARCEntry] = []
        self.closure: Dict[str, Any] = {}
        self._validate_and_parse()

    def _validate_and_parse(self) -> None:
        """Validate root keys and parse ARC entries."""

        required_root_keys = ["schema", "exported_at", "thread_id", "arc_chain"]
        missing = [key for key in required_root_keys if key not in self._raw_payload]
        if missing:
            raise ARCValidationError(f"Missing required ARC root keys: {missing}")

        self.schema = str(self._raw_payload["schema"])
        self.exported_at = _parse_iso_timestamp(str(self._raw_payload["exported_at"]))
        self.thread_id = str(self._raw_payload["thread_id"])

        arc_chain = self._raw_payload.get("arc_chain", [])
        if not isinstance(arc_chain, list):
            raise ARCValidationError("arc_chain must be a list of entries")

        self.entries = [ARCEntry.from_dict(entry) for entry in arc_chain]

        closure = self._raw_payload.get("closure", {})
        if closure:
            if not isinstance(closure, dict):
                raise ARCValidationError("closure must be a dictionary when provided")
            self.closure = closure

    # ------------------------------------------------------------------
    # Derived metrics
    # ------------------------------------------------------------------
    def _count_arc_types(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for entry in self.entries:
            counts[entry.arc_type] = counts.get(entry.arc_type, 0) + 1
        return counts

    def _collect_participants(self) -> List[str]:
        return sorted({entry.author for entry in self.entries})

    def _collect_propagation_targets(self) -> Dict[str, int]:
        targets: Dict[str, int] = {}
        for entry in self.entries:
            for target in entry.propagate_to:
                targets[target] = targets.get(target, 0) + 1
        return targets

    def _collect_anchor_pairs(self) -> List[Tuple[str, str]]:
        unique_pairs = {entry.anchor_pair for entry in self.entries}
        return sorted(unique_pairs)

    def _compute_drift_metrics(self) -> Dict[str, Any]:
        deltas = [entry.driftlog_delta for entry in self.entries if entry.driftlog_delta is not None]
        if not deltas:
            return {
                "entries_with_drift": 0,
                "net_change": 0.0,
                "max_abs_change": 0.0,
                "has_drift": False,
            }

        net_change = sum(deltas)
        max_abs_change = max(abs(delta) for delta in deltas)

        return {
            "entries_with_drift": len(deltas),
            "net_change": round(net_change, 6),
            "max_abs_change": round(max_abs_change, 6),
            "has_drift": any(delta != 0.0 for delta in deltas),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def enhancement_summary(self) -> Dict[str, Any]:
        """Return the derived metrics for the ARC chain."""

        propagation_targets = self._collect_propagation_targets()

        return {
            "schema": self.schema,
            "thread_id": self.thread_id,
            "exported_at": self.exported_at.isoformat() if self.exported_at else None,
            "chain_length": len(self.entries),
            "arc_types": self._count_arc_types(),
            "participants": self._collect_participants(),
            "propagation": {
                "targets": propagation_targets,
                "total_targets": sum(propagation_targets.values()),
            },
            "anchor_integrity": {
                "unique_pairs": self._collect_anchor_pairs(),
                "initial_pair": self.entries[0].anchor_pair if self.entries else None,
                "terminal_pair": self.entries[-1].anchor_pair if self.entries else None,
                "t1_anchor_seed": self.T1_ANCHOR_SEED,
                "srb_bridge": self.SRB_BRIDGE_ANCHOR,
            },
            "driftlog": self._compute_drift_metrics(),
            "closure": {
                "sealed": bool(self.closure),
                "sealed_by": self.closure.get("sealed_by") if self.closure else None,
                "archive_ready": bool(self.closure.get("archive_ready")) if self.closure else False,
                "summary": self.closure.get("summary") if self.closure else None,
            },
        }

    def enhanced_payload(self) -> Dict[str, Any]:
        """Return the payload augmented with an ``arc_enhancement`` block."""

        payload_copy = copy.deepcopy(self._raw_payload)
        payload_copy["arc_enhancement"] = {
            "t1_anchor_seed": self.T1_ANCHOR_SEED,
            "srb_bridge": self.SRB_BRIDGE_ANCHOR,
            "summary": self.enhancement_summary(),
        }
        return payload_copy


__all__ = ["ARCChainEnhancer", "ARCEntry", "ARCValidationError"]

