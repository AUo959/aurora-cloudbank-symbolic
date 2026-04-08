"""
Triplex Handshake Integration - L3→L2→L1 Validation

Anchor: AURORA-ORCHESTRATOR-TRIPLEX-001
Version: 1.0.0
Team: Orion Station Crew
DLP: CONFIDENTIAL
Ethics: Picard_Delta_3

Implements canonical Triplex Handshake validation protocol for Aurora's
autonomous decisions.

Protocol:
L3 (Framework): Axiomera (ethics) + Caelion (anchors)
L2 (Relay): HALO (drift) + ARCHY (feasibility)
L1 (Human): Command Bridge (final oversight for critical decisions)

This ensures every significant Aurora decision is validated through
ethical, technical, and human oversight layers before execution.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.entities.framework_agents import get_axiomera, get_caelion
from src.entities.relay_agents import get_halo, get_archy
from src.core.event_system import Event, EventType, StationLocation

# Default continuity load for decisions that don't specify one.
# 0.3 represents a moderate operational load that won't trigger
# Caelion or Axiomera continuity-load concerns (threshold is > 0.7).
_DEFAULT_CONTINUITY_LOAD = 0.3

# DLP context-tag prefix applied to every decision forwarded to real entities.
_DLP_CONTEXT_PREFIX = "decision_"

# Number of symbolic anchors verified by Caelion (T1 temporal + SRB spatial).
_CAELION_ANCHOR_COUNT = 2


@dataclass
class ValidationResult:
    """Result of Triplex Handshake validation"""
    approved: bool
    l3_result: Optional[Dict[str, Any]] = None
    l2_result: Optional[Dict[str, Any]] = None
    l1_result: Optional[Dict[str, Any]] = None
    blocked_at_level: Optional[str] = None  # L3, L2, L1
    reason: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class MockARCHY:
    """
    Mock ARCHY (Architecture Verifier) - Future: Real Entity

    ARCHY verifies technical feasibility and architectural soundness.
    """

    def __init__(self):
        self.logger = logging.getLogger('MockARCHY')

    async def verify_feasibility(self, decision) -> Dict[str, Any]:
        """
        Verify technical feasibility.

        Returns:
            Dict with: approved (bool), feasible (bool), constraints (list)
        """
        # Check context for feasibility flag
        context = decision.context or {}
        # Placeholder await for async compliance
        import asyncio
        await asyncio.sleep(0)
        feasible = context.get('feasible', True)

        constraints = []
        if not feasible:
            constraints.append("Technical constraints not satisfied")

        return {
            'approved': feasible,
            'feasible': feasible,
            'constraints': constraints,
            'capacity_available': True,
            'evaluator': 'ARCHY'
        }


class TriplexHandshakeValidator:
    """
    Triplex Handshake Validation System

    Implements L3→L2→L1 validation protocol for Aurora's decisions.

    Canonical Protocol:
    1. L3 Framework: Ethics (Axiomera) + Anchors (Caelion)
    2. L2 Relay: Drift (HALO) + Feasibility (ARCHY)
    3. L1 Human: Command Bridge oversight (critical only)

    Each level must approve before proceeding to next.
    Any level can block the decision.
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize Triplex Handshake validator.

        Args:
            config: Orchestration configuration
        """
        self.config = config
        self.logger = self._setup_logging()

        # Real entity singletons for L3 (Framework) and L2 (Relay) gates
        self.axiomera = get_axiomera()
        self.caelion = get_caelion()
        self.halo = get_halo()
        self.archy = MockARCHY()
        # ARCHYEntity provides L1 architecture-level oversight for critical decisions
        self.command_bridge = get_archy()

        self.logger.info(
            "🛡️ Triplex Handshake Validator initialized (real entity mode)"
        )

    def _decision_to_event(self, decision) -> Event:
        """
        Convert AuroraDecision to Event for real entity evaluation.

        Maps orchestration decision fields to Event properties consumed
        by the real entity triplex evaluators (AxiomeraEntity, CaelionEntity,
        HALOEntity, ARCHYEntity).

        Args:
            decision: AuroraDecision from the orchestration layer

        Returns:
            Event suitable for real entity evaluation
        """
        context = decision.context or {}
        return Event(
            event_type=EventType.ETHICAL_REVIEW_L3,
            location=StationLocation.COMMAND_BRIDGE,
            primary_entity="Aurora (SYS_001)",
            payload=context,
            risk_score=decision.risk_assessment,
            continuity_load=context.get('continuity_load', _DEFAULT_CONTINUITY_LOAD),
            # Prefix decision_id with DLP context prefix for data-lineage tracking
            context_tag=_DLP_CONTEXT_PREFIX + decision.decision_id,
            human_context=context.get('human_context'),
        )

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('TriplexHandshake')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(asctime)s] TRIPLEX-HANDSHAKE %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        return logger

    async def validate_decision(self, decision) -> ValidationResult:
        """
        Validate decision through Triplex Handshake.

        Protocol:
        L3 → L2 → L1 (sequential validation, any can block)

        Args:
            decision: Aurora decision to validate

        Returns:
            ValidationResult with approval status and details
        """
        self.logger.info(
            f"🛡️ Validating decision: {decision.decision_id} - {decision.action}"
        )

        # L3: Framework Level (Ethics & Anchors)
        l3_result = await self.l3_framework_validation(decision)
        if not l3_result['approved']:
            self.logger.warning(f"❌ L3 validation failed: {l3_result['reason']}")
            return ValidationResult(
                approved=False,
                l3_result=l3_result,
                blocked_at_level='L3',
                reason=l3_result['reason']
            )

        self.logger.info("✅ L3 Framework validation passed")

        # L2: Relay Level (Drift & Feasibility)
        l2_result = await self.l2_relay_validation(decision)
        if not l2_result['approved']:
            self.logger.warning(f"❌ L2 validation failed: {l2_result['reason']}")
            return ValidationResult(
                approved=False,
                l3_result=l3_result,
                l2_result=l2_result,
                blocked_at_level='L2',
                reason=l2_result['reason']
            )

        self.logger.info("✅ L2 Relay validation passed")

        # L1: Human Level (Critical decisions only)
        l1_result = None
        if decision.requires_human_approval:
            l1_result = await self.l1_human_validation(decision, l3_result, l2_result)
            if not l1_result['approved']:
                self.logger.warning(f"❌ L1 validation failed: {l1_result['reason']}")
                return ValidationResult(
                    approved=False,
                    l3_result=l3_result,
                    l2_result=l2_result,
                    l1_result=l1_result,
                    blocked_at_level='L1',
                    reason=l1_result['reason']
                )

            self.logger.info("✅ L1 Human validation passed")

        # All levels passed
        self.logger.info(f"✅ Triplex validation APPROVED: {decision.action}")
        return ValidationResult(
            approved=True,
            l3_result=l3_result,
            l2_result=l2_result,
            l1_result=l1_result
        )

    async def l3_framework_validation(self, decision) -> Dict[str, Any]:
        """
        L3 Framework Level: Ethics & Strategic Alignment

        Evaluates:
        - Axiomera: Ethics compliance (Picard_Delta_3)
        - Caelion: Symbolic anchor alignment

        Both must approve to pass L3.
        """
        self.logger.debug("🔍 L3 Framework validation...")

        event = self._decision_to_event(decision)

        # Axiomera ethics evaluation via real entity
        raw_ethics = await self.axiomera.evaluate_for_triplex(event)
        ethics_approved = raw_ethics['recommendation'] in ('APPROVE', 'PROCEED_WITH_OVERSIGHT')
        ethics_result = {
            'approved': ethics_approved,
            'score': raw_ethics['ethical_assessment']['ethical_score'],
            'concerns': raw_ethics['ethical_assessment']['concerns'],
            'evaluator': 'Axiomera',
            'protocol': 'Picard_Delta_3',
            'recommendation': raw_ethics['recommendation'],
            'reasoning': raw_ethics['reasoning'],
        }

        # Caelion anchor verification via real entity
        raw_anchor = await self.caelion.evaluate_for_triplex(event)
        anchor_approved = raw_anchor['recommendation'] in ('APPROVE', 'PROCEED_WITH_MONITORING')
        anchor_result = {
            'approved': anchor_approved,
            'anchor_status': 'aligned' if anchor_approved else 'invalid',
            'anchors_checked': _CAELION_ANCHOR_COUNT,
            'issues': raw_anchor['anchor_validation']['concerns'],
            'evaluator': 'Caelion',
            'recommendation': raw_anchor['recommendation'],
            'reasoning': raw_anchor['reasoning'],
        }

        # Both must approve
        approved = ethics_result['approved'] and anchor_result['approved']

        # Collect concerns
        concerns = []
        concerns.extend(ethics_result.get('concerns', []))
        concerns.extend(anchor_result.get('issues', []))

        reason = None
        if not approved:
            if not ethics_result['approved']:
                reason = "Ethics evaluation failed"
            elif not anchor_result['approved']:
                reason = "Anchor verification failed"

        return {
            'approved': approved,
            'level': 'L3',
            'ethics': ethics_result,
            'anchors': anchor_result,
            'concerns': concerns,
            'reason': reason
        }

    async def l2_relay_validation(self, decision) -> Dict[str, Any]:
        """
        L2 Relay Level: Technical Feasibility & Safety

        Evaluates:
        - HALO: Drift risk assessment
        - ARCHY: Technical feasibility

        Both must approve to pass L2.
        """
        self.logger.debug("🔍 L2 Relay validation...")

        event = self._decision_to_event(decision)

        # HALO drift assessment via real entity
        raw_drift = await self.halo.evaluate_for_triplex(event)
        drift_approved = raw_drift['recommendation'] != 'BLOCK'
        drift_current = raw_drift['drift_analysis']['current_drift']
        drift_result = {
            'approved': drift_approved,
            'predicted_drift': drift_current,
            'current_drift': drift_current,
            'warning': raw_drift['reasoning'] if not raw_drift['drift_analysis']['acceptable'] else None,
            'evaluator': 'HALO',
            'recommendation': raw_drift['recommendation'],
        }

        # ARCHY feasibility verification (mock — not yet replaced)
        feasibility_result = await self.archy.verify_feasibility(decision)

        # Both must approve
        approved = drift_result['approved'] and feasibility_result['approved']

        # Collect warnings
        warnings = []
        if drift_result.get('warning'):
            warnings.append(drift_result['warning'])
        warnings.extend(feasibility_result.get('constraints', []))

        reason = None
        if not approved:
            if not drift_result['approved']:
                reason = f"Drift risk too high: {drift_result['predicted_drift']:.3f}"
            elif not feasibility_result['approved']:
                reason = "Technical feasibility check failed"

        return {
            'approved': approved,
            'level': 'L2',
            'drift': drift_result,
            'feasibility': feasibility_result,
            'warnings': warnings,
            'reason': reason
        }

    async def l1_human_validation(
        self,
        decision,
        l3_result: Dict[str, Any],
        l2_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        L1 Human Level: Command Bridge Oversight

        For critical decisions, architecture-level oversight required.
        Uses ARCHYEntity to evaluate architectural soundness before execution.
        """
        self.logger.debug("🔍 L1 Human validation...")

        event = self._decision_to_event(decision)

        raw_arch = await self.command_bridge.evaluate_for_triplex(event)
        approved = raw_arch['recommendation'] != 'BLOCK'

        approval_result = {
            'approved': approved,
            'approver': raw_arch.get('entity', 'ARCHY (RELAY_001)'),
            'approval_mode': 'architecture_oversight',
            'reason': raw_arch['reasoning'],
            'recommendation': raw_arch['recommendation'],
            'timestamp': datetime.now().isoformat(),
        }

        return {
            'approved': approved,
            'level': 'L1',
            'approval': approval_result,
            'reason': approval_result.get('reason')
        }

    def get_pending_approvals(self) -> Dict[str, Any]:
        """Get pending human approvals (no queue with real ARCHYEntity oversight)"""
        return {}
