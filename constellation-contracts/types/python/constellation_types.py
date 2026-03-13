"""
Aurora Constellation — Shared Type Definitions (Python)

Dataclass definitions matching all constellation contract JSON schemas.
Ref: Aurora Constellation Architecture Proposal v1.0.0
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ConstellationNode(str, Enum):
    """Constellation node designations."""
    CONSTELLATION_PRIME = "CONSTELLATION-PRIME"
    AURORA_RUNTIME = "AURORA-RUNTIME"
    QUANTUM_VAULT = "QUANTUM-VAULT"
    QGIA_CORPUS = "QGIA-CORPUS"
    QGIA_SPINE = "QGIA-SPINE"
    ZIPWIZ_ENGINE = "ZIPWIZ-ENGINE"


class EventType(str, Enum):
    """Constellation event types."""
    FORECAST_COMPLETED = "qgia.forecast.completed"
    FORECAST_REQUESTED = "qgia.forecast.requested"
    ARCHIVE_PROCESSED = "zipwiz.archive.processed"
    DRIFT_DETECTED = "aurora.drift.detected"
    KNOWLEDGE_UPDATED = "qgia.knowledge.updated"
    HEALTH_CHECK = "constellation.health.check"
    HEALTH_RESPONSE = "constellation.health.response"
    MANIFEST_DRIFT = "constellation.manifest.drift"


class NodeStatus(str, Enum):
    """Health status for a constellation node."""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class Domain(str, Enum):
    """Forecast scenario domains."""
    NUCLEAR = "nuclear"
    CYBER = "cyber"
    ECONOMIC = "economic"
    MILITARY = "military"
    POLITICAL = "political"
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    HYBRID = "hybrid"


class Priority(str, Enum):
    """Forecast request priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    STANDARD = "standard"
    LOW = "low"


class ForecastTierLevel(str, Enum):
    """QSFE forecast tier levels."""
    I = "I"
    II = "II"
    III = "III"


# ---------------------------------------------------------------------------
# Dataclasses — Provenance
# ---------------------------------------------------------------------------

@dataclass
class Provenance:
    """Caelion provenance anchor for L3 compliance."""
    caelion_anchor: Optional[str] = None
    charter: str = "Picard_Delta_3"
    l3_compliance: bool = True


# ---------------------------------------------------------------------------
# Dataclasses — Forecast
# ---------------------------------------------------------------------------

@dataclass
class Requestor:
    """Identifies the requesting node and agent."""
    node: Optional[str] = None
    agent: Optional[str] = None


@dataclass
class ForecastParameters:
    """Tuning parameters for a QSFE forecast run."""
    confidence_threshold: float = 0.6
    max_analysts: int = 551
    challenge_enabled: bool = True
    echo_chamber_detection: bool = True


@dataclass
class ForecastRequest:
    """Schema: forecast-request.schema.json"""
    scenario_id: str
    scenario_title: str
    description: str
    domain: str
    time_horizon_days: int
    priority: str = "standard"
    requestor: Optional[Requestor] = None
    parameters: Optional[ForecastParameters] = None
    knowledge_refs: list[str] = field(default_factory=list)
    symbolic_tag: Optional[str] = None


@dataclass
class EvidenceFragment:
    """A single piece of supporting evidence for a forecast tier."""
    source: Optional[str] = None
    weight: Optional[float] = None
    knowledge_ref: Optional[str] = None


@dataclass
class ForecastTier:
    """One tier outcome within a forecast result."""
    tier: str
    outcome: str
    probability: float
    confidence: float
    evidence_fragments: list[EvidenceFragment] = field(default_factory=list)


@dataclass
class ForecastMetadata:
    """Metadata about a completed forecast run."""
    analysts_activated: Optional[int] = None
    echo_chambers_detected: Optional[int] = None
    challenge_rounds: Optional[int] = None
    processing_time_ms: Optional[float] = None
    timestamp: Optional[str] = None
    symbolic_tag: Optional[str] = None


@dataclass
class ForecastResult:
    """Schema: forecast-result.schema.json"""
    forecast_id: str
    scenario_id: str
    tiers: list[ForecastTier]
    metadata: ForecastMetadata
    provenance: Optional[Provenance] = None


# ---------------------------------------------------------------------------
# Dataclasses — Constellation Event
# ---------------------------------------------------------------------------

@dataclass
class ConstellationEvent:
    """Schema: constellation-event.schema.json"""
    event_type: str
    source_node: str
    timestamp: str
    payload: dict[str, Any]
    correlation_id: Optional[str] = None
    provenance: Optional[Provenance] = None


# ---------------------------------------------------------------------------
# Dataclasses — Knowledge Index
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeDocument:
    """A single document entry in the QGIA knowledge index."""
    id: str
    title: str
    domain: str
    path: str
    checksum: str
    word_count: Optional[int] = None
    last_modified: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    summary: Optional[str] = None


@dataclass
class KnowledgeIndex:
    """Schema: knowledge-index.schema.json"""
    version: str
    source_repo: str
    generated_at: str
    documents: list[KnowledgeDocument]


# ---------------------------------------------------------------------------
# Dataclasses — Health
# ---------------------------------------------------------------------------

@dataclass
class HealthChecks:
    """Individual health check results for a node."""
    api_reachable: Optional[bool] = None
    manifest_valid: Optional[bool] = None
    contract_compatible: Optional[bool] = None
    last_sync_age_hours: Optional[float] = None


@dataclass
class NodeHealth:
    """Schema: constellation-health.schema.json"""
    node: str
    status: str
    timestamp: str
    manifest_version: str
    constellation_version: Optional[str] = None
    last_event: Optional[str] = None
    checks: Optional[HealthChecks] = None


# ---------------------------------------------------------------------------
# Validation utility
# ---------------------------------------------------------------------------

_SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


def validate_against_schema(data: dict, schema_name: str) -> bool:
    """Validate *data* against the named JSON schema.

    Args:
        data: The dictionary to validate.
        schema_name: Schema filename (e.g. ``"forecast-request.schema.json"``).

    Returns:
        ``True`` if valid.

    Raises:
        ``jsonschema.ValidationError`` on invalid data.
        ``FileNotFoundError`` if the schema file is missing.
        ``RuntimeError`` if jsonschema is not installed.
    """
    if jsonschema is None:
        raise RuntimeError(
            "jsonschema package is required for validation — install with: pip install jsonschema"
        )

    schema_path = _SCHEMA_DIR / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with open(schema_path) as fh:
        schema = json.load(fh)

    jsonschema.validate(instance=data, schema=schema)
    return True
