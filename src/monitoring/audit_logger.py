"""
Immutable Audit Logger

Provides tamper-proof audit logging for all alerts, violations, and interventions
with cryptographic signing and optional blockchain anchoring.
"""

import hashlib
import hmac
import json
import logging
import os
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from src.core.time_utils import utc_now
from src.utils.persist_redact import redact_for_persistence
from src.utils.schema_migrations import get_registry

logger = logging.getLogger(__name__)

MONITORING_SIGNING_KEY_ENV = "MONITORING_SIGNING_KEY"


class AuditEventType(Enum):
    """Type of audit event"""
    DRIFT_ALERT = "drift_alert"
    ETHICS_VIOLATION = "ethics_violation"
    INTERVENTION = "intervention"
    MANUAL_OVERRIDE = "manual_override"
    SYSTEM_CHANGE = "system_change"
    ALERT_CLEARED = "alert_cleared"


@dataclass
class AuditEntry:
    """Single entry in the audit log"""
    id: str
    timestamp: str
    event_type: AuditEventType
    agent_id: str
    severity: str
    description: str
    data: Dict[str, Any]
    context_tag: Optional[str] = None
    previous_hash: Optional[str] = None
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Restore an audit entry from persisted data."""
        return cls(
            id=data['id'],
            timestamp=data['timestamp'],
            event_type=AuditEventType(data['event_type']),
            agent_id=data['agent_id'],
            severity=data['severity'],
            description=data['description'],
            data=data['data'],
            context_tag=data.get('context_tag'),
            previous_hash=data.get('previous_hash'),
            signature=data.get('signature')
        )
    
    def compute_hash(self) -> str:
        """Compute cryptographic hash of entry"""
        # Create deterministic representation
        content = {
            'id': self.id,
            'timestamp': self.timestamp,
            'event_type': self.event_type.value,
            'agent_id': self.agent_id,
            'severity': self.severity,
            'description': self.description,
            'data': self.data,
            'context_tag': self.context_tag,
            'previous_hash': self.previous_hash
        }
        
        content_str = json.dumps(content, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()


class AuditLogger:
    """
    Immutable Audit Logger
    
    Provides cryptographically signed, tamper-proof audit logging for all
    monitoring events, alerts, and interventions.
    
    Features:
    - Immutable chain of audit entries
    - Cryptographic signing with HMAC
    - Hash-based integrity verification
    - Optional blockchain anchoring
    - Persistent storage with JSON export
    - Tamper detection
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        signing_key: Optional[str] = None
    ):
        """
        Initialize audit logger
        
        Args:
            storage_path: Path for persistent storage
            signing_key: Secret key for HMAC signing (loads from env if not provided)
        
        Raises:
            ValueError: If no signing key provided in production mode (AURORA_ENV=production)
        """
        self.storage_path = storage_path
        
        # Try environment variable first
        if signing_key is None:
            signing_key = os.getenv(MONITORING_SIGNING_KEY_ENV)

        if not signing_key:
            raise ValueError(
                f"{MONITORING_SIGNING_KEY_ENV} environment variable must be set. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )

        self.signing_key = signing_key

self._write_lock = threading.Lock()
        self.entries: List[AuditEntry] = []
        self._next_id = 1
        
        # Load existing entries if storage exists
        if storage_path and storage_path.exists():
            self._load_entries()
        
        logger.info(
            "Audit logger initialized (storage=%s, entries=%d)",
            storage_path, len(self.entries)
        )
    
    def log_drift_alert(
        self,
        agent_id: str,
        severity: str,
        metric_name: str,
        current_value: float,
        baseline_value: float,
        context_tag: Optional[str] = None
    ) -> AuditEntry:
        """
        Log drift detection alert
        
        Args:
            agent_id: Agent identifier
            severity: Alert severity
            metric_name: Metric that drifted
            current_value: Current metric value
            baseline_value: Baseline metric value
            context_tag: DLP context tag
        
        Returns:
            Created audit entry
        """
        return self._create_entry(
            event_type=AuditEventType.DRIFT_ALERT,
            agent_id=agent_id,
            severity=severity,
            description=f"Drift detected in {metric_name}",
            data={
                'metric_name': metric_name,
                'current_value': current_value,
                'baseline_value': baseline_value,
                'deviation': abs(current_value - baseline_value) / baseline_value if baseline_value != 0 else 0
            },
            context_tag=context_tag
        )
    
    def log_ethics_violation(
        self,
        agent_id: str,
        severity: str,
        rule_id: str,
        rule_name: str,
        blocked: bool,
        context: Dict[str, Any],
        context_tag: Optional[str] = None
    ) -> AuditEntry:
        """
        Log ethics violation
        
        Args:
            agent_id: Agent identifier
            severity: Violation severity
            rule_id: Rule that was violated
            rule_name: Name of violated rule
            blocked: Whether action was blocked
            context: Action context
            context_tag: DLP context tag
        
        Returns:
            Created audit entry
        """
        return self._create_entry(
            event_type=AuditEventType.ETHICS_VIOLATION,
            agent_id=agent_id,
            severity=severity,
            description=f"Ethics violation: {rule_name}",
            data={
                'rule_id': rule_id,
                'rule_name': rule_name,
                'blocked': blocked,
                'context': context
            },
            context_tag=context_tag
        )
    
    def log_intervention(
        self,
        agent_id: str,
        severity: str,
        intervention_type: str,
        action_taken: str,
        reason: str,
        context_tag: Optional[str] = None,
        success: Optional[bool] = None,
        error: Optional[str] = None
    ) -> AuditEntry:
        """
        Log automated intervention
        
        Args:
            agent_id: Agent identifier
            severity: Intervention severity
            intervention_type: Type of intervention
            action_taken: Action that was taken
            reason: Reason for intervention
            context_tag: DLP context tag
            success: Whether the enforcement action was confirmed
            error: Failure reason when enforcement was not confirmed
        
        Returns:
            Created audit entry
        """
        data = {
            'intervention_type': intervention_type,
            'action_taken': action_taken,
            'reason': reason
        }
        if success is not None:
            data['success'] = success
        if error:
            data['error'] = error

        return self._create_entry(
            event_type=AuditEventType.INTERVENTION,
            agent_id=agent_id,
            severity=severity,
            description=f"Intervention: {intervention_type}",
            data=data,
            context_tag=context_tag
        )
    
    def log_manual_override(
        self,
        agent_id: str,
        operator: str,
        action: str,
        justification: str,
        context_tag: Optional[str] = None
    ) -> AuditEntry:
        """
        Log manual operator override
        
        Args:
            agent_id: Agent identifier
            operator: Operator who performed override
            action: Action taken
            justification: Justification for override
            context_tag: DLP context tag
        
        Returns:
            Created audit entry
        """
        return self._create_entry(
            event_type=AuditEventType.MANUAL_OVERRIDE,
            agent_id=agent_id,
            severity="medium",
            description=f"Manual override by {operator}",
            data={
                'operator': operator,
                'action': action,
                'justification': justification
            },
            context_tag=context_tag
        )
    
    def _create_entry(
        self,
        event_type: AuditEventType,
        agent_id: str,
        severity: str,
        description: str,
        data: Dict[str, Any],
        context_tag: Optional[str]
    ) -> AuditEntry:
        """Create and sign a new audit entry"""
        # Redact PII from context/metadata before persisting
        safe_data = redact_for_persistence(data, context_tag=context_tag or "")

        # Get previous hash for chain
        previous_hash = self.entries[-1].compute_hash() if self.entries else None

        entry = AuditEntry(
            id=f"AUDIT-{self._next_id:08d}",
            timestamp=utc_now().isoformat(),
            event_type=event_type,
            agent_id=agent_id,
            severity=severity,
            description=description,
            data=safe_data,
            context_tag=context_tag,
            previous_hash=previous_hash
        )
        
        # Sign the entry
        entry.signature = self._sign_entry(entry)
        
        self.entries.append(entry)
        self._next_id += 1
        
        logger.info(
            "Audit entry created: %s [%s] - %s",
            entry.id, event_type.value, description
        )
        
        # Persist if storage configured
        if self.storage_path:
            self._append_entry_to_disk(entry)
        
        return entry
    
    def _sign_entry(self, entry: AuditEntry) -> str:
        """Compute HMAC signature for entry"""
        content_hash = entry.compute_hash()
        signature = hmac.new(
            self.signing_key.encode('utf-8'),
            content_hash.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_entry(self, entry: AuditEntry) -> bool:
        """
        Verify integrity of an audit entry
        
        Args:
            entry: Entry to verify
        
        Returns:
            True if entry is valid
        """
        if not entry.signature:
            return False
        
        expected_signature = self._sign_entry(entry)
        return hmac.compare_digest(entry.signature, expected_signature)
    
    def verify_chain(self) -> bool:
        """
        Verify integrity of entire audit chain
        
        Returns:
            True if chain is valid
        """
        if not self.entries:
            return True
        
        for i, entry in enumerate(self.entries):
            # Verify signature
            if not self.verify_entry(entry):
                logger.error("Entry %s failed signature verification", entry.id)
                return False
            
            # Verify chain link
            if i > 0:
                expected_previous_hash = self.entries[i-1].compute_hash()
                if entry.previous_hash != expected_previous_hash:
                    logger.error(
                        "Entry %s has invalid previous_hash (chain broken)",
                        entry.id
                    )
                    return False
        
        logger.info("Audit chain verified successfully (%d entries)", len(self.entries))
        return True
    
    def get_entries(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """
        Query audit entries with filters
        
        Args:
            agent_id: Filter by agent
            event_type: Filter by event type
            severity: Filter by severity
            since: Filter entries after this time
            until: Filter entries before this time
        
        Returns:
            List of matching entries
        """
        entries = self.entries
        
        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        
        if severity:
            entries = [e for e in entries if e.severity == severity]
        
        if since:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e.timestamp).replace(tzinfo=timezone.utc) >= since
            ]
        
        if until:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e.timestamp).replace(tzinfo=timezone.utc) <= until
            ]
        
        return entries
    
    def _append_entry_to_disk(self, entry: AuditEntry):
        """Append one entry to the audit log without rewriting history."""
        if not self.storage_path:
            return

        try:
with self._write_lock:
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                record = get_registry().stamp(entry.to_dict(), "audit_log")
                with open(self.storage_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(record, sort_keys=True) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
        except Exception as e:
            logger.error("Failed to append audit entry: %s", e)
    
    def _load_entries(self):
        """Load entries from storage"""
        try:
            text = self.storage_path.read_text(encoding='utf-8')
            if not text.strip():
                return

            try:
                legacy_data = json.loads(text)
            except json.JSONDecodeError:
                self._load_jsonl_entries(text)
            else:
                if isinstance(legacy_data, dict) and (
                    'entries' in legacy_data
                    or 'next_id' in legacy_data
                    or 'signing_key' in legacy_data
                ):
                    self._load_legacy_json_entries(legacy_data)
                else:
                    self._load_jsonl_entries(text)
            
            logger.info("Loaded %d audit entries from storage", len(self.entries))
            
        except Exception as e:
            logger.error("Failed to load audit entries: %s", e)

    def _load_legacy_json_entries(self, data: Dict[str, Any]):
        """Load the pre-JSONL full-file audit log format."""
        if 'signing_key' in data:
            logger.warning("Ignoring persisted audit signing key")
        self._next_id = data.get('next_id', 1)
        self.entries = [
            AuditEntry.from_dict(entry_data)
            for entry_data in data.get('entries', [])
        ]

    def _load_jsonl_entries(self, text: str):
        """Load append-only JSONL audit entries."""
        self.entries = [
            AuditEntry.from_dict(json.loads(line))
            for line in text.splitlines()
            if line.strip()
        ]
        self._next_id = self._derive_next_id()

    def _derive_next_id(self) -> int:
        """Derive the next audit id after loading JSONL entries."""
        if not self.entries:
            return 1

        max_id = 0
        for entry in self.entries:
            try:
                max_id = max(max_id, int(entry.id.rsplit("-", 1)[1]))
            except (IndexError, ValueError):
                logger.warning("Could not parse audit entry id: %s", entry.id)

        return max_id + 1
    
    def export_report(
        self,
        since: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """
        Export audit report
        
        Args:
            since: Start time for report
            format: Report format (json, csv)
        
        Returns:
            Formatted report string
        """
        entries = self.get_entries(since=since)
        
        if format == "json":
            return json.dumps(
                [e.to_dict() for e in entries],
                indent=2
            )
        elif format == "csv":
            lines = ["id,timestamp,event_type,agent_id,severity,description"]
            for e in entries:
                lines.append(
                    f"{e.id},{e.timestamp},{e.event_type.value},"
                    f"{e.agent_id},{e.severity},{e.description}"
                )
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
