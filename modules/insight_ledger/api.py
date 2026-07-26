"""Insight Ledger API

FastAPI endpoints for the immutable insight ledger.

Anchor: T1-TIL-API-001
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.middleware.fastapi_security import require_csrf_token

from .ledger_core import InsightLedger
from .schemas import AuditQuery, InsightRecord, LedgerEntry, LedgerStats, VerificationReport

router = APIRouter(prefix="/ledger", tags=["Insight Ledger"])
SENSITIVE_LEDGER_DEPENDENCIES = (Depends(require_csrf_token),)
_ledger_instance: Optional[InsightLedger] = None


def get_ledger() -> InsightLedger:
    """Get the global ledger instance."""
    if _ledger_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ledger not initialized. Configure storage path first.",
        )
    return _ledger_instance


def initialize_ledger(storage_path: str, secret_key: Optional[str] = None) -> InsightLedger:
    """Initialize the global ledger instance from operator configuration."""
    global _ledger_instance
    _ledger_instance = InsightLedger(storage_path=storage_path, secret_key=secret_key)
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

    success: bool = Field(..., description="Whether exporting succeeded")
    export_path: str = Field(..., description="Server-generated export filename")
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
    """Record a signed, hash-chained insight in the ledger."""
    try:
        ledger = get_ledger()
        entry = ledger.record_insight(request.insight)
        return RecordInsightResponse(
            success=True,
            entry=entry,
            entry_id=entry.entry_id,
            message="Insight recorded successfully",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get(
    "/verify",
    response_model=VerifyIntegrityResponse,
    summary="Verify Ledger Integrity",
    description="Cryptographically verify the integrity of the entire ledger or a subset",
)
async def verify_integrity(
    limit: Optional[int] = Query(None, ge=1, le=100000, description="Max entries to verify (None=all)"),
) -> VerifyIntegrityResponse:
    """Verify signatures and hash-chain continuity."""
    try:
        ledger = get_ledger()
        report_dict = ledger.verify_integrity(limit=limit)
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
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.post(
    "/history",
    response_model=QueryHistoryResponse,
    summary="Query Ledger History",
    description="Query ledger entries with flexible filters (time, type, source, tags, etc.)",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def query_history(query: Optional[AuditQuery] = None) -> QueryHistoryResponse:
    """Query ledger history with bounded filters and pagination."""
    try:
        ledger = get_ledger()
        effective_query = query if query is not None else AuditQuery()
        entries = ledger.query_history(effective_query)
        return QueryHistoryResponse(
            entries=entries,
            total_returned=len(entries),
            query=effective_query,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get(
    "/stats",
    response_model=LedgerStats,
    summary="Get Ledger Statistics",
    description="Retrieve ledger health metrics, entry counts, and integrity status",
)
async def get_stats() -> LedgerStats:
    """Return ledger health, counts, and storage statistics."""
    try:
        return get_ledger().get_stats()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


def _server_export_name() -> str:
    """Create an unguessable server-controlled export filename."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"ledger-export-{timestamp}-{uuid4().hex}.json"


@router.post(
    "/export",
    response_model=ExportLedgerResponse,
    summary="Export Ledger",
    description="Export the complete ledger to a server-generated JSON file",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def export_ledger(
    include_genesis: bool = Query(True, description="Include genesis entry in export"),
) -> ExportLedgerResponse:
    """Export the ledger under a server-generated filename.

    The HTTP caller does not select or supply a filesystem path. This keeps
    remote request data out of path construction while preserving the operator-
    configured export root enforced by ``InsightLedger.export_ledger``.
    """
    export_name = _server_export_name()
    try:
        entries_exported = get_ledger().export_ledger(
            export_name,
            include_genesis=include_genesis,
        )
        return ExportLedgerResponse(
            success=True,
            export_path=export_name,
            entries_exported=entries_exported,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get(
    "/entry/{entry_id}",
    response_model=LedgerEntry,
    summary="Get Entry by ID",
    description="Retrieve a specific ledger entry by its unique identifier",
    dependencies=SENSITIVE_LEDGER_DEPENDENCIES,
)
async def get_entry_by_id(entry_id: str) -> LedgerEntry:
    """Retrieve a specific ledger entry by ID."""
    try:
        entries = get_ledger().query_history(AuditQuery(limit=10000))
        for entry in entries:
            if entry.entry_id == entry_id:
                return entry

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry not found: {entry_id}",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get(
    "/health",
    summary="Ledger Health Check",
    description="Quick health check for ledger service",
)
async def health_check() -> Dict[str, Any]:
    """Return a bounded health summary for the ledger service."""
    try:
        if _ledger_instance is None:
            return {"status": "not_initialized", "message": "Ledger not initialized"}

        stats = get_ledger().get_stats()
        return {
            "status": "healthy",
            "ledger_initialized": True,
            "total_entries": stats.total_entries,
            "integrity_verified": stats.integrity_verified,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        return {
            "status": "unhealthy",
            "error": "Ledger health check failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


__all__ = ["router", "initialize_ledger", "get_ledger"]
