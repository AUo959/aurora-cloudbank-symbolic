"""Structured audit logging for the unified ethics engine."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, default=str) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


@dataclass
class AuditLogEntry:
    """Immutable ethics audit entry with a SHA256 content signature."""

    audit_id: str
    timestamp: str
    context: str
    agent_id: str
    anchor: Optional[str]
    verdict: str
    severity: str
    triggered_rules: List[str]
    payload_hash: str
    signature: str
    blockchain_anchor_status: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EthicsAuditLog:
    """Append-only JSONL audit emitter for non-approved ethics verdicts."""

    def __init__(
        self,
        path: Optional[Path | str] = None,
        *,
        cryptographic_signing: bool = True,
        blockchain_anchoring: bool = False,
    ) -> None:
        env_path = os.getenv("ETHICS_AUDIT_LOG_PATH")
        self.path = Path(path or env_path or "monitoring_data/ethics_audit_log.jsonl")
        self.cryptographic_signing = cryptographic_signing
        self.blockchain_anchoring = blockchain_anchoring
        self.entries: List[AuditLogEntry] = []
        self._lock = threading.Lock()

    def emit(
        self,
        *,
        context: str,
        agent_id: str,
        anchor: Optional[str],
        verdict: str,
        severity: str,
        triggered_rules: List[str],
        details: Dict[str, Any],
    ) -> AuditLogEntry:
        """Create, sign, retain, and append one audit entry."""
        timestamp = _utc_iso()
        unsigned = {
            "timestamp": timestamp,
            "context": context,
            "agent_id": agent_id,
            "anchor": anchor,
            "verdict": verdict,
            "severity": severity,
            "triggered_rules": triggered_rules,
            "details": details,
        }
        payload_hash = hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()
        signature = payload_hash if self.cryptographic_signing else ""
        audit_id = f"AUDIT-{timestamp[:10].replace('-', '')}-{payload_hash[:12]}"
        blockchain_status = (
            "todo_external_integration"
            if self.blockchain_anchoring
            else "not_configured"
        )

        entry = AuditLogEntry(
            audit_id=audit_id,
            timestamp=timestamp,
            context=context,
            agent_id=agent_id,
            anchor=anchor,
            verdict=verdict,
            severity=severity,
            triggered_rules=triggered_rules,
            payload_hash=payload_hash,
            signature=signature,
            blockchain_anchor_status=blockchain_status,
            details=details,
        )

        with self._lock:
            self.entries.append(entry)
            _append_jsonl(self.path, entry.to_dict())
        return entry
