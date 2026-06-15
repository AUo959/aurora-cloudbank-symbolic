"""Governed lifecycle policy for Quantum Agent Forge spawns.

This module wraps the existing Quantum Forge engine with route-first lifecycle
decisions. It does not spawn agents directly; it records when spawning is
allowed, bounded, transparent, and eligible for retention review.

Thread: T1->T8->T9->INFINITE
DLP: context_tag=quantum_forge_lifecycle, symbolic_hash=QAFP_v1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Sequence
import uuid


ANCHOR = "EOS_SEED_ORION"
ETHICS_CLEARANCE = "Picard_Delta_3"


class ForgeRouteDecision(Enum):
    ROUTE_TO_DEPARTMENT = "route_to_department"
    INSTANTIATE_FROM_SPEC = "instantiate_from_spec"
    HANDLE_DIRECTLY = "handle_directly"
    SPAWN_QUANTUM_AGENT = "spawn_quantum_agent"


class RetentionOutcome(Enum):
    STORE_AS_SPEC = "spec"
    PROMOTE_TO_MODULE = "module"
    ARCHIVE = "archive"
    DISCARD = "discard"


class ForgeScope(Enum):
    SINGLE_TASK = "single_task"
    BOUNDED_MULTI_STEP = "bounded_multi_step"


@dataclass(frozen=True)
class ForgeTaskRequest:
    task_id: str
    task_class: str
    required_capabilities: Sequence[str]
    domain_tags: Sequence[str] = field(default_factory=list)
    risk_level: float = 0.0
    output_summary: str = ""


@dataclass(frozen=True)
class StandingCoverage:
    department: Optional[str] = None
    prior_spec_id: Optional[str] = None
    direct_competency: bool = False
    direct_handler: Optional[str] = None


@dataclass(frozen=True)
class ForgeAuthorization:
    authorized: bool
    route_decision: ForgeRouteDecision
    reason: str
    allowed_capabilities: List[str] = field(default_factory=list)
    denied_capabilities: List[str] = field(default_factory=list)
    pilot_acknowledged: bool = False


@dataclass
class ForgeLifecycleRecord:
    forge_id: str
    task_id: str
    task_class: str
    capabilities: List[str]
    domain_tags: List[str]
    scope: ForgeScope
    temporary: bool = True
    active: bool = True
    pilot_informed: bool = True
    anchor: str = ANCHOR
    ethics_clearance: str = ETHICS_CLEARANCE
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dissolved_at: Optional[str] = None
    execution_log: List[Dict[str, str]] = field(default_factory=list)
    retention_required: bool = False


@dataclass(frozen=True)
class RetentionReview:
    forge_id: str
    outcome: RetentionOutcome
    rationale: str
    output_summary: str
    task_class: str
    capabilities: List[str]
    domain_tags: List[str]
    spec_id: Optional[str] = None
    promoted_to: Optional[str] = None
    pilot_override: bool = False
    anchor: str = ANCHOR
    ethics_clearance: str = ETHICS_CLEARANCE

    def to_spec_record(self) -> Dict[str, object]:
        return {
            "spec_id": self.spec_id,
            "forge_id": self.forge_id,
            "created": datetime.now(timezone.utc).isoformat(),
            "task_class": self.task_class,
            "capabilities": list(self.capabilities),
            "domain_tags": list(self.domain_tags),
            "output_summary": self.output_summary,
            "retention_rationale": self.rationale,
            "retention_decision": self.outcome.value,
            "promoted_to": self.promoted_to,
            "anchor": self.anchor,
            "ethics_clearance": self.ethics_clearance,
        }


@dataclass(frozen=True)
class RetentionCriteria:
    novel_concept: bool = False
    resolves_design_problem: bool = False
    reusable: bool = False
    module_candidate: bool = False
    pilot_override: Optional[RetentionOutcome] = None


def _stable_capabilities(capabilities: Sequence[str]) -> List[str]:
    deduped: List[str] = []
    seen = set()
    for capability in capabilities:
        normalized = capability.strip()
        if normalized and normalized not in seen:
            deduped.append(normalized)
            seen.add(normalized)
    return deduped


def _route_for_coverage(coverage: StandingCoverage) -> ForgeRouteDecision:
    route_checks = (
        (coverage.department, ForgeRouteDecision.ROUTE_TO_DEPARTMENT),
        (coverage.prior_spec_id, ForgeRouteDecision.INSTANTIATE_FROM_SPEC),
        (coverage.direct_competency, ForgeRouteDecision.HANDLE_DIRECTLY),
    )
    return next(
        (decision for has_coverage, decision in route_checks if has_coverage),
        ForgeRouteDecision.SPAWN_QUANTUM_AGENT,
    )


def _spawn_denial_authorization(
    request: ForgeTaskRequest,
    route_decision: ForgeRouteDecision,
    capabilities: List[str],
    high_risk_threshold: float,
    pilot_acknowledged: bool,
) -> Optional[ForgeAuthorization]:
    if route_decision is not ForgeRouteDecision.SPAWN_QUANTUM_AGENT:
        return ForgeAuthorization(
            authorized=False,
            route_decision=route_decision,
            reason="existing coverage prevents a new quantum agent spawn",
            allowed_capabilities=capabilities,
            pilot_acknowledged=pilot_acknowledged,
        )
    if not capabilities:
        return ForgeAuthorization(
            authorized=False,
            route_decision=route_decision,
            reason="spawn requires an enumerated capability set",
            pilot_acknowledged=pilot_acknowledged,
        )
    if request.risk_level >= high_risk_threshold and not pilot_acknowledged:
        return ForgeAuthorization(
            authorized=False,
            route_decision=route_decision,
            reason="high-risk quantum agent spawn requires pilot acknowledgment",
            denied_capabilities=capabilities,
            pilot_acknowledged=False,
        )
    return None


def _validate_spawn_authorization(authorization: ForgeAuthorization) -> None:
    if not authorization.authorized:
        raise ValueError(f"Cannot record unauthorized spawn: {authorization.reason}")
    if authorization.route_decision is not ForgeRouteDecision.SPAWN_QUANTUM_AGENT:
        raise ValueError("Cannot record spawn for a non-spawn route decision")


def _new_capabilities(record: ForgeLifecycleRecord, requested_capabilities: Sequence[str]) -> List[str]:
    return [
        capability
        for capability in _stable_capabilities(requested_capabilities)
        if capability not in record.capabilities
    ]


def _select_retention_outcome(criteria: RetentionCriteria) -> RetentionOutcome:
    if criteria.pilot_override is not None:
        return criteria.pilot_override
    if criteria.module_candidate:
        return RetentionOutcome.PROMOTE_TO_MODULE
    if criteria.novel_concept or criteria.resolves_design_problem:
        return RetentionOutcome.STORE_AS_SPEC
    if criteria.reusable:
        return RetentionOutcome.ARCHIVE
    return RetentionOutcome.DISCARD


def _spec_id_for_outcome(outcome: RetentionOutcome) -> Optional[str]:
    if outcome in {RetentionOutcome.STORE_AS_SPEC, RetentionOutcome.PROMOTE_TO_MODULE}:
        return f"spec-{uuid.uuid4().hex}"
    return None


class QuantumAgentForgePolicy:
    def __init__(self, high_risk_threshold: float = 0.70) -> None:
        self.high_risk_threshold = high_risk_threshold
        self.lifecycle_records: Dict[str, ForgeLifecycleRecord] = {}

    def evaluate_route(
        self,
        request: ForgeTaskRequest,
        coverage: Optional[StandingCoverage] = None,
    ) -> ForgeRouteDecision:
        coverage = coverage or StandingCoverage()
        return _route_for_coverage(coverage)

    def authorize_spawn(
        self,
        request: ForgeTaskRequest,
        coverage: Optional[StandingCoverage] = None,
        pilot_acknowledged: bool = False,
    ) -> ForgeAuthorization:
        route_decision = self.evaluate_route(request, coverage)
        capabilities = _stable_capabilities(request.required_capabilities)
        denial = _spawn_denial_authorization(
            request=request,
            route_decision=route_decision,
            capabilities=capabilities,
            high_risk_threshold=self.high_risk_threshold,
            pilot_acknowledged=pilot_acknowledged,
        )
        if denial is not None:
            return denial
        return ForgeAuthorization(
            authorized=True,
            route_decision=route_decision,
            reason="quantum agent spawn authorized as last-resort coverage",
            allowed_capabilities=capabilities,
            pilot_acknowledged=pilot_acknowledged,
        )

    def record_spawn(
        self,
        request: ForgeTaskRequest,
        authorization: ForgeAuthorization,
        scope: ForgeScope = ForgeScope.SINGLE_TASK,
        forge_id: Optional[str] = None,
    ) -> ForgeLifecycleRecord:
        _validate_spawn_authorization(authorization)

        record = ForgeLifecycleRecord(
            forge_id=forge_id or f"forge-{uuid.uuid4().hex}",
            task_id=request.task_id,
            task_class=request.task_class,
            capabilities=list(authorization.allowed_capabilities),
            domain_tags=list(request.domain_tags),
            scope=scope,
            execution_log=[
                {
                    "event": "spawn_recorded",
                    "reason": authorization.reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        )
        self.lifecycle_records[record.forge_id] = record
        return record

    def request_capability_expansion(
        self,
        forge_id: str,
        requested_capabilities: Sequence[str],
        aurora_authorized: bool = False,
    ) -> ForgeAuthorization:
        record = self.lifecycle_records[forge_id]
        requested = _new_capabilities(record, requested_capabilities)
        if not requested:
            return ForgeAuthorization(
                authorized=True,
                route_decision=ForgeRouteDecision.SPAWN_QUANTUM_AGENT,
                reason="no new capabilities requested",
                allowed_capabilities=list(record.capabilities),
            )
        if not aurora_authorized:
            return ForgeAuthorization(
                authorized=False,
                route_decision=ForgeRouteDecision.SPAWN_QUANTUM_AGENT,
                reason="capability expansion requires Aurora authorization",
                allowed_capabilities=list(record.capabilities),
                denied_capabilities=requested,
            )

        record.capabilities.extend(requested)
        record.execution_log.append(
            {
                "event": "capability_expansion_authorized",
                "capabilities": ",".join(requested),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return ForgeAuthorization(
            authorized=True,
            route_decision=ForgeRouteDecision.SPAWN_QUANTUM_AGENT,
            reason="capability expansion authorized by Aurora",
            allowed_capabilities=list(record.capabilities),
        )

    def dissolve(
        self,
        forge_id: str,
        retention_required: bool = False,
        log_summary: str = "",
    ) -> ForgeLifecycleRecord:
        record = self.lifecycle_records[forge_id]
        record.active = False
        record.retention_required = retention_required
        record.dissolved_at = datetime.now(timezone.utc).isoformat()
        record.execution_log.append(
            {
                "event": "dissolved",
                "summary": log_summary,
                "retention_required": str(retention_required).lower(),
                "timestamp": record.dissolved_at,
            }
        )
        return record

    def review_retention(
        self,
        forge_id: str,
        output_summary: str,
        rationale: str,
        criteria: Optional[RetentionCriteria] = None,
        promoted_to: Optional[str] = None,
    ) -> RetentionReview:
        record = self.lifecycle_records[forge_id]
        criteria = criteria or RetentionCriteria()
        outcome = _select_retention_outcome(criteria)

        review = RetentionReview(
            forge_id=forge_id,
            outcome=outcome,
            rationale=rationale,
            output_summary=output_summary,
            task_class=record.task_class,
            capabilities=list(record.capabilities),
            domain_tags=list(record.domain_tags),
            spec_id=_spec_id_for_outcome(outcome),
            promoted_to=promoted_to if outcome is RetentionOutcome.PROMOTE_TO_MODULE else None,
            pilot_override=criteria.pilot_override is not None,
        )
        record.execution_log.append(
            {
                "event": "retention_review",
                "outcome": review.outcome.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return review


__all__ = [
    "ForgeAuthorization",
    "ForgeLifecycleRecord",
    "ForgeRouteDecision",
    "ForgeScope",
    "ForgeTaskRequest",
    "QuantumAgentForgePolicy",
    "RetentionCriteria",
    "RetentionOutcome",
    "RetentionReview",
    "StandingCoverage",
]
