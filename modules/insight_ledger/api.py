"""Insight Ledger API

FastAPI endpoints for the immutable insight ledger.

Anchor: T1-TIL-API-001
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.middleware.fastapi_security import require_csrf_token

from .ledger_core import InsightLedger
from .schemas import AuditQuery, InsightRecord, LedgerEntry, LedgerStats, VerificationReport

# Initialize router
router = APIRouter(prefix="/ledger", tags=["Insight Ledger"])
SENSITIVE_LEDGER_DEPENDENCIES = (Depends(require_csrf_token),)

# Global ledger instance (initialized by main app)
_ledger_instance: Optional[InsightLedger] = None


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_optional_int(name: str, default: Optional[int]) -> Optional[int]:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default

    normalized = raw.strip().lower()
    if normalized in {"0", "none", "full", "all"}:
        return None

    value = int(normalized)
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return value


def get_ledger() -> InsightLedger:
    """Get the global ledger instance."""
    if _ledger_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ledger not initialized. Configure storage path first.",
        )
    return _ledger_instance


def initialize_ledger(
    storage_path: str,
    secret_key: Optional[str] = None,
    *,
    auto_checkpoint: int = 1000,
    verify_on_startup: Optional[bool] = None,
    startup_verification_limit: Optional[int] = None,
    verification_fail_mode: Optional[str] = None,
) -> InsightLedger:
    """
    Initialize the global ledger instance.

    Args:
        storage_path: Directory for ledger storage
        secret_key: Optional HMAC secret key (hex)
        auto_checkpoint: Create checkpoint entry every N entries (0=disabled)
        verify_on_startup: Run integrity verification during initialization.
        startup_verification_limit: Max startup entries to verify (0/None = full chain).
        verification_fail_mode: "closed" or "open-with-signal"

    Returns:
        Initialized ledger instance
    """
    global _ledger_instance
    effective_verify_on_startup = (
        verify_on_startup
        if verify_on_startup is not None
        else _env_bool("INSIGHT_LEDGER_VERIFY_ON_STARTUP", True)
    )
    effective_limit = (
        startup_verification_limit
        if startup_verification_limit is not None
        else _env_optional_int("INSIGHT_LEDGER_STARTUP_VERIFY_LIMIT", 100)
    )
    effective_fail_mode = verification_fail_mode or os.environ.get(
        "INSIGHT_LEDGER_VERIFICATION_FAIL_MODE", "open-with-signal"
    )

    _ledger_instance = InsightLedger(
        storage_path=storage_path,
        secret_key=secret_key,
        auto_checkpoint=auto_checkpoint,
        verify_on_startup=effective_verify_on_startup,
        startup_verification_limit=effective_limit,
        verification_fail_mode=effective_fail_mode,
    )
    return _ledger_instance


class RecordInsightRequest(BaseModel):
    """Request to record a new insight."""

    insight: InsightRecord = Field(..., description="Insight data to record")


class RecordInsightResponse(BaseModel):
    """Response from recording an insight."""

    success: bool = Field(..., description="Whether recording succeeded")
    entry: Optional[LedgerEntry] = Field(None, description="Complete ledger entry")
    entry_id: Optional[str] = Field(None, description="Entry identifier")
    message: Optional[str] = Field(None, description="Status message")


class VerifyIntegrityResponse(BaseModel):
    """Response from integrity verification."""

    report: VerificationReport = Field(..., description="Verification report")
    summary: str = Field(..., description="Human-readable summary")


class QueryHistoryResponse(BaseModel):
    """Response from history query."""

    entries: List[LedgerEntry] = Field(..., description="Matching ledger entries")
    total_returned: int = Field(..., description="Number of entries returned")
    query: AuditQuery = Field(..., description="Query parameters used")


class ExportLedgerResponse(BaseModel):
    """Response from ledger export."""

    success: bool = Field(..., description="Whether export succeeded")
    export_path: str = Field(..., description="Path to export file")
    entries_exported: int = Field(..., description="Number of entries exported")


@router.post(
    "/insight",
    response_model=RecordInsightResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record New Insight",
    description="Record a new insight in the immutable ledger with cryptographic signature",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def record_insight(request: RecordInsightRequest) -> RecordInsightResponse:
    """
    Record a new insight in the ledger.

    The insight will be:
    - Assigned a unique entry ID
    - Timestamped with UTC time
    - Signed with HMAC-SHA256
    - Chained to previous entry via hash
    - Appended to immutable storage

    Returns the complete ledger entry with all cryptographic metadata.
    """
    try:
        ledger = get_ledger()
        entry = ledger.record_insight(request.insight)

        return RecordInsightResponse(
            success=True, entry=entry, entry_id=entry.entry_id, message="Insight recorded successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record insight: {str(e)}",
        )


@router.get(
    "/verify",
    response_model=VerifyIntegrityResponse,
    summary="Verify Ledger Integrity",
    description="Cryptographically verify the integrity of the entire ledger or a subset",
)
async def verify_integrity(
    limit: Optional[int] = Query(None, ge=1, le=100000, description="Max entries to verify (None=all)")
) -> VerifyIntegrityResponse:
    """
    Verify the cryptographic integrity of the ledger.

    Checks:
    - HMAC signature validity for each entry
    - SHA-256 hash chain continuity
    - No gaps or breaks in the chain

    Returns detailed report including any verification failures.
    """
    try:
        ledger = get_ledger()
        report_dict = ledger.run_integrity_verification(limit=limit, source="api")
        report = VerificationReport(**report_dict)

        if report.chain_intact:
            summary = (
                f"✅ Ledger integrity verified: {report.verified_entries}/{report.total_entries} "
                f"entries validated in {report.verification_time_ms:.1f}ms"
            )
        else:
            summary = (
                f"❌ Integrity compromised: {len(report.failed_entries)} failed entries, "
                f"{len(report.errors)} errors detected"
            )

        return VerifyIntegrityResponse(report=report, summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.post(
    "/history",
    response_model=QueryHistoryResponse,
    summary="Query Ledger History",
    description="Query ledger entries with flexible filters (time, type, source, tags, etc.)",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def query_history(query: Optional[AuditQuery] = None) -> QueryHistoryResponse:
    """
    Query ledger history with flexible filters.

    Supports filtering by:
    - Time range (start_time, end_time)
    - Insight types (decision, analysis, alert, etc.)
    - Sources (component/system names)
    - Tags (classification labels)
    - Severity (info, warning, error, critical)
    - Full-text search in content

    Pagination via limit/offset parameters.
    """
    try:
        ledger = get_ledger()

        if query is None:
            query = AuditQuery()

        entries = ledger.query_history(query)

        return QueryHistoryResponse(entries=entries, total_returned=len(entries), query=query)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Query failed: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=LedgerStats,
    summary="Get Ledger Statistics",
    description="Retrieve ledger health metrics, entry counts, and integrity status",
)
async def get_stats() -> LedgerStats:
    """
    Get ledger statistics and health metrics.

    Includes:
    - Total entry count
    - First/last entry timestamps
    - Entries by type and source
    - Integrity verification status
    - Storage size in bytes
    """
    try:
        ledger = get_ledger()
        return ledger.get_stats()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}",
        )


@router.post(
    "/export",
    response_model=ExportLedgerResponse,
    summary="Export Ledger",
    description="Export complete ledger to JSON file for backup or analysis",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def export_ledger(
    output_path: str = Query(..., description="Output file path"),
    include_genesis: bool = Query(True, description="Include genesis entry in export"),
) -> ExportLedgerResponse:
    """
    Export the complete ledger to a JSON file.

    The export includes:
    - All ledger entries with full metadata
    - Cryptographic signatures and hashes
    - Ledger statistics and metadata

    Useful for:
    - Backup and archival
    - External analysis
    - Compliance reporting
    - Data migration

    Note:
    - output_path must be relative to the safe export directory
    - Absolute paths and parent directory references (..) are rejected
    - Path traversal attempts will result in 400 Bad Request
    """
    try:
        ledger = get_ledger()

        # Path validation is now handled by ledger.export_ledger()
        # which uses validate_safe_path() to prevent path traversal
        entries_exported = ledger.export_ledger(output_path, include_genesis=include_genesis)

        return ExportLedgerResponse(
            success=True, export_path=output_path, entries_exported=entries_exported
        )

    except ValueError as e:
        # Path validation errors from export_ledger
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid export path: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Export failed: {str(e)}"
        )


@router.get(
    "/entry/{entry_id}",
    response_model=LedgerEntry,
    summary="Get Entry by ID",
    description="Retrieve a specific ledger entry by its unique identifier",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def get_entry_by_id(entry_id: str) -> LedgerEntry:
    """
    Retrieve a specific ledger entry by ID.

    Returns the complete entry with all cryptographic metadata.
    """
    try:
        ledger = get_ledger()

        # Query for the specific entry
        query = AuditQuery(limit=10000)  # Search entire ledger
        entries = ledger.query_history(query)

        for entry in entries:
            if entry.entry_id == entry_id:
                return entry

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Entry not found: {entry_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve entry: {str(e)}",
        )


@router.get(
    "/health",
    summary="Ledger Health Check",
    description="Quick health check for ledger service",
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.

    Returns:
    - Service status
    - Basic ledger stats
    - Initialization status
    """
    try:
        if _ledger_instance is None:
            return {"status": "not_initialized", "message": "Ledger not initialized"}

        ledger = get_ledger()
        health = ledger.get_verification_health()
        status_value = "healthy"
        if health["compromised"]:
            status_value = "unhealthy" if not health["accepting_writes"] else "degraded"

        return {
            "status": status_value,
            "ledger_initialized": True,
            "total_entries": health["total_entries"],
            "integrity_verified": health["chain_intact"],
            "chain_intact": health["chain_intact"],
            "compromised": health["compromised"],
            "accepting_writes": health["accepting_writes"],
            "verification_fail_mode": health["verification_fail_mode"],
            "startup_verification": health["startup_verification"],
            "last_verification": health["last_verification"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Export router for main app
__all__ = ["router", "initialize_ledger", "get_ledger"]
