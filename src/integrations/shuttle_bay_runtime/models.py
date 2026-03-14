"""Dataclasses and enums for the Shuttle Bay mission runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TrustLane(str, Enum):
    """Deterministic trust lanes for Shuttle Bay execution."""

    GREEN = "green"
    GRAY = "gray"
    RED = "red"


class PersistenceMode(str, Enum):
    """Persistence mode for the mission journal."""

    DISK = "disk"
    MEMORY = "memory"


@dataclass(frozen=True)
class PolicyDecision:
    """Risk classification and execution posture for a tool call."""

    tool_name: str
    tool_domain: str
    lane: TrustLane
    risk_score: float
    policy_action: str
    review_required: bool
    destructive: bool = False
    external: bool = False
    deny_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["lane"] = self.lane.value
        return payload


@dataclass(frozen=True)
class RoutingAssignment:
    """Resolved mission routing information derived from repo canon."""

    tool_name: str
    tool_domain: str
    shuttle_id: str
    relay_agent: str
    authority_role: str
    authority_key: str
    clearance_required: str
    oversight_glyphs: List[str] = field(default_factory=list)
    lane_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InspectionResult:
    """Structured outcome for preflight and postflight inspection."""

    ok: bool
    stage: str
    checks: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    degraded: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MissionRecord:
    """Persistable mission record for executed or denied tool calls."""

    mission_id: str
    tool_name: str
    session_id: Optional[str]
    lane: str
    tool_domain: str
    risk_score: float
    policy_action: str
    review_required: bool
    authority_role: str
    authority_name: Optional[str]
    relay_agent: str
    shuttle_id: str
    oversight_glyphs: List[str]
    preflight: Dict[str, Any]
    postflight: Dict[str, Any]
    audit_tag: str
    status: str
    execution_success: bool
    persistence_mode: str
    created_at: str

    def mission_envelope(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "lane": self.lane,
            "tool_domain": self.tool_domain,
            "risk_score": self.risk_score,
            "policy_action": self.policy_action,
            "review_required": self.review_required,
            "authority_role": self.authority_role,
            "authority_name": self.authority_name,
            "relay_agent": self.relay_agent,
            "shuttle_id": self.shuttle_id,
            "oversight_glyphs": list(self.oversight_glyphs),
            "preflight": dict(self.preflight),
            "postflight": dict(self.postflight),
            "audit_tag": self.audit_tag,
        }

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["mission"] = self.mission_envelope()
        return payload


@dataclass(frozen=True)
class CatalogBundle:
    """Loaded canonical and overlay data for the Shuttle Bay runtime."""

    bridge_core: Dict[str, Any]
    fleet_manifest: Dict[str, Any]
    integration_config: Dict[str, Any]
    l1_config: Dict[str, Any]
    staff_registry: Dict[str, Any]
    tool_routing: Dict[str, Any]
    policy_matrix: Dict[str, Any]
    source_status: Dict[str, Dict[str, Any]]

    def critical_sources_ready(self) -> bool:
        required = (
            "bridge_core",
            "fleet_manifest",
            "integration_config",
            "l1_config",
            "tool_routing",
            "policy_matrix",
        )
        return all(self.source_status.get(name, {}).get("loaded", False) for name in required)
