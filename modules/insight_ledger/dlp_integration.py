"""
Insight Ledger DLP Integration

Integrates Insight Ledger with Aurora's native DLP tracking system.

Anchor: T1-TIL-004
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from modules.insight_ledger.schemas import InsightRecord, InsightType

try:
    from src.core.native_dlp_export import NativeDLPTracker

    DLP_AVAILABLE = True
except ImportError:
    DLP_AVAILABLE = False
    NativeDLPTracker = None


class LedgerDLPIntegration:
    """
    Integration layer between Insight Ledger and DLP tracking.

    Automatically creates DLP records for ledger operations.
    """

    def __init__(self, dlp_tracker: Optional[Any] = None):
        """
        Initialize DLP integration.

        Args:
            dlp_tracker: NativeDLPTracker instance (optional)
        """
        self.dlp_tracker = dlp_tracker
        self.enabled = DLP_AVAILABLE and dlp_tracker is not None

    def track_insight_recorded(
        self,
        entry_id: str,
        insight: InsightRecord,
        entry_hash: str,
        context_tag: Optional[str] = None,
    ) -> Optional[str]:
        """
        Track insight recording in DLP system.

        Args:
            entry_id: Ledger entry identifier
            insight: Insight record that was stored
            entry_hash: Cryptographic hash of entry
            context_tag: Optional DLP context tag

        Returns:
            DLP record ID if tracking succeeded, None otherwise
        """
        if not self.enabled:
            return None

        try:
            dlp_context = context_tag or f"ledger-record-{entry_id}"

            dlp_metadata = {
                "operation": "insight_recorded",
                "entry_id": entry_id,
                "entry_hash": entry_hash,
                "insight_type": insight.insight_type.value,
                "source": insight.source,
                "related_anchor": insight.related_anchor,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            record_id = self.dlp_tracker.create_record(
                context_tag=dlp_context,
                operation="insight_ledger_record",
                metadata=dlp_metadata,
                validation_hash=entry_hash,
            )

            return record_id

        except Exception as e:
            # Silent fail - don't break ledger operations
            print(f"Warning: DLP tracking failed for {entry_id}: {e}")
            return None

    def track_integrity_verification(
        self, verification_result: Dict[str, Any], context_tag: Optional[str] = None
    ) -> Optional[str]:
        """
        Track integrity verification in DLP system.

        Args:
            verification_result: Verification report dict
            context_tag: Optional DLP context tag

        Returns:
            DLP record ID if tracking succeeded, None otherwise
        """
        if not self.enabled:
            return None

        try:
            dlp_context = context_tag or "ledger-verify"

            dlp_metadata = {
                "operation": "integrity_verification",
                "total_entries": verification_result.get("total_entries", 0),
                "verified_entries": verification_result.get("verified_entries", 0),
                "chain_intact": verification_result.get("chain_intact", False),
                "failed_entries": len(verification_result.get("failed_entries", [])),
                "verification_time_ms": verification_result.get("verification_time_ms", 0),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            record_id = self.dlp_tracker.create_record(
                context_tag=dlp_context,
                operation="insight_ledger_verify",
                metadata=dlp_metadata,
            )

            return record_id

        except Exception as e:
            print(f"Warning: DLP tracking failed for verification: {e}")
            return None

    def track_export(
        self, export_path: str, entries_exported: int, context_tag: Optional[str] = None
    ) -> Optional[str]:
        """
        Track ledger export in DLP system.

        Args:
            export_path: Path to export file
            entries_exported: Number of entries exported
            context_tag: Optional DLP context tag

        Returns:
            DLP record ID if tracking succeeded, None otherwise
        """
        if not self.enabled:
            return None

        try:
            dlp_context = context_tag or "ledger-export"

            dlp_metadata = {
                "operation": "ledger_export",
                "export_path": export_path,
                "entries_exported": entries_exported,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            record_id = self.dlp_tracker.create_record(
                context_tag=dlp_context, operation="insight_ledger_export", metadata=dlp_metadata
            )

            return record_id

        except Exception as e:
            print(f"Warning: DLP tracking failed for export: {e}")
            return None


def create_insight_from_dlp_event(
    operation: str, metadata: Dict[str, Any], source: str = "aurora-dlp"
) -> InsightRecord:
    """
    Create an InsightRecord from a DLP event.

    Useful for recording DLP events in the ledger for full auditability.

    Args:
        operation: DLP operation type
        metadata: DLP metadata dictionary
        source: Source system (default: aurora-dlp)

    Returns:
        InsightRecord suitable for ledger recording
    """
    # Map DLP operations to insight types
    operation_type_map = {
        "data_access": InsightType.AUDIT,
        "data_export": InsightType.AUDIT,
        "data_modification": InsightType.AUDIT,
        "security_event": InsightType.ALERT,
        "error": InsightType.ALERT,
        "decision": InsightType.DECISION,
        "analysis": InsightType.ANALYSIS,
    }

    insight_type = operation_type_map.get(operation, InsightType.AUDIT)

    # Determine severity from metadata
    severity = metadata.get("severity", "info")
    if severity not in ("info", "warning", "error", "critical"):
        severity = "info"

    return InsightRecord(
        insight_type=insight_type,
        content=f"DLP Event: {operation}",
        context=metadata,
        source=source,
        tags=["dlp", operation],
        severity=severity,
        related_anchor=metadata.get("anchor", None),
    )


# Global DLP integration instance (initialized by main app)
_dlp_integration: Optional[LedgerDLPIntegration] = None


def get_dlp_integration() -> Optional[LedgerDLPIntegration]:
    """Get the global DLP integration instance."""
    return _dlp_integration


def initialize_dlp_integration(dlp_tracker: Optional[Any] = None) -> LedgerDLPIntegration:
    """
    Initialize the global DLP integration instance.

    Args:
        dlp_tracker: NativeDLPTracker instance

    Returns:
        Initialized DLP integration
    """
    global _dlp_integration
    _dlp_integration = LedgerDLPIntegration(dlp_tracker=dlp_tracker)
    return _dlp_integration
