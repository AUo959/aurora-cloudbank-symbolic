"""
Data Schemas for Insight Ledger

Pydantic models for insight records, audit queries, and ledger statistics.

Anchor: T1-TIL-001
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class InsightType(str, Enum):
    """Types of insights that can be recorded."""

    DECISION = "decision"  # AI decision with rationale
    ANALYSIS = "analysis"  # Data analysis result
    RECOMMENDATION = "recommendation"  # System recommendation
    PREDICTION = "prediction"  # Predictive model output
    EXPLANATION = "explanation"  # Explanation/reasoning
    AUDIT = "audit"  # Audit trail entry
    ALERT = "alert"  # System alert or warning
    METRIC = "metric"  # Performance or quality metric


class InsightRecord(BaseModel):
    """Schema for recording a new insight."""

    insight_type: InsightType = Field(..., description="Type of insight being recorded")
    content: str = Field(..., min_length=1, max_length=10000, description="Insight content")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Contextual metadata (model, params, etc.)"
    )
    source: str = Field(..., min_length=1, max_length=256, description="Source system or component")
    tags: Optional[List[str]] = Field(default=None, max_items=20, description="Classification tags")
    severity: Optional[str] = Field(
        default="info", pattern="^(info|warning|error|critical)$", description="Severity level"
    )
    related_anchor: Optional[str] = Field(
        default=None, max_length=64, description="Related Aurora anchor (T1/SRB)"
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure tags are unique and trimmed."""
        if v is None:
            return None
        return list(set(tag.strip() for tag in v if tag.strip()))

    class Config:
        json_schema_extra = {
            "example": {
                "insight_type": "decision",
                "content": "Approved user request based on policy compliance check",
                "context": {"policy": "data-access-v2", "user_id": "usr_123"},
                "source": "aurora-access-control",
                "tags": ["access-control", "policy"],
                "severity": "info",
                "related_anchor": "T1-ACC-003",
            }
        }


class AuditQuery(BaseModel):
    """Schema for querying audit history."""

    start_time: Optional[datetime] = Field(default=None, description="Start timestamp (inclusive)")
    end_time: Optional[datetime] = Field(default=None, description="End timestamp (exclusive)")
    insight_types: Optional[List[InsightType]] = Field(
        default=None, description="Filter by insight types"
    )
    sources: Optional[List[str]] = Field(default=None, max_items=50, description="Filter by sources")
    tags: Optional[List[str]] = Field(
        default=None, max_items=20, description="Filter by tags (OR logic)"
    )
    severity: Optional[List[str]] = Field(default=None, max_items=4, description="Filter by severity")
    search_text: Optional[str] = Field(
        default=None, min_length=1, max_length=256, description="Full-text search in content"
    )
    limit: int = Field(default=100, ge=1, le=10000, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Pagination offset")

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure end_time is after start_time."""
        if v is not None and "start_time" in info.data:
            start = info.data["start_time"]
            if start is not None and v <= start:
                raise ValueError("end_time must be after start_time")
        return v


class LedgerEntry(BaseModel):
    """Complete ledger entry (returned from queries)."""

    entry_id: str = Field(..., description="Unique entry identifier")
    timestamp: datetime = Field(..., description="Entry creation timestamp")
    insight_type: InsightType
    content: str
    context: Optional[Dict[str, Any]] = None
    source: str
    tags: Optional[List[str]] = None
    severity: str
    related_anchor: Optional[str] = None
    signature: str = Field(..., description="Cryptographic signature (hex)")
    previous_hash: Optional[str] = Field(default=None, description="Previous entry hash (chain)")
    entry_hash: str = Field(..., description="This entry's hash")

    class Config:
        json_schema_extra = {
            "example": {
                "entry_id": "insight_20240101_120000_abc123",
                "timestamp": "2024-01-01T12:00:00Z",
                "insight_type": "decision",
                "content": "Access granted based on policy compliance",
                "context": {"policy": "data-access-v2"},
                "source": "aurora-access-control",
                "tags": ["access-control"],
                "severity": "info",
                "related_anchor": "T1-ACC-003",
                "signature": "a1b2c3d4...",
                "previous_hash": "9e8f7d6c...",
                "entry_hash": "1a2b3c4d...",
            }
        }


class LedgerStats(BaseModel):
    """Ledger statistics and health metrics."""

    total_entries: int = Field(..., ge=0, description="Total number of entries")
    first_entry_time: Optional[datetime] = Field(default=None, description="Timestamp of first entry")
    last_entry_time: Optional[datetime] = Field(default=None, description="Timestamp of last entry")
    entries_by_type: Dict[str, int] = Field(
        default_factory=dict, description="Entry count by insight type"
    )
    entries_by_source: Dict[str, int] = Field(
        default_factory=dict, description="Entry count by source"
    )
    integrity_verified: bool = Field(..., description="Whether chain integrity is intact")
    ledger_size_bytes: int = Field(..., ge=0, description="Approximate storage size")

    class Config:
        json_schema_extra = {
            "example": {
                "total_entries": 1250,
                "first_entry_time": "2024-01-01T00:00:00Z",
                "last_entry_time": "2024-01-15T18:30:00Z",
                "entries_by_type": {"decision": 450, "analysis": 320, "alert": 480},
                "entries_by_source": {"aurora-access-control": 450, "resilience-sentinel": 800},
                "integrity_verified": True,
                "ledger_size_bytes": 2458000,
            }
        }


class VerificationReport(BaseModel):
    """Report from ledger integrity verification."""

    total_entries: int = Field(..., ge=0)
    verified_entries: int = Field(..., ge=0)
    failed_entries: List[str] = Field(default_factory=list, description="Entry IDs with failures")
    chain_intact: bool = Field(..., description="Whether hash chain is intact")
    verification_time_ms: float = Field(..., ge=0, description="Time taken to verify")
    errors: List[str] = Field(default_factory=list, description="Verification errors")

    class Config:
        json_schema_extra = {
            "example": {
                "total_entries": 1250,
                "verified_entries": 1250,
                "failed_entries": [],
                "chain_intact": True,
                "verification_time_ms": 125.4,
                "errors": [],
            }
        }
