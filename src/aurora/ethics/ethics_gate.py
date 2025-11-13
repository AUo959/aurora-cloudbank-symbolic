"""
Ethics Gate Core Module

Provides centralized ethics evaluation wrapping GUMAS API with DLP tracking,
anchor protocols, and structured logging.

DLP: ethics_gate_core_v1
Anchors: T1, SRB, EOS_SEED_ORION, Picard_Delta_3
Symbolic tags: ETHICS_GATE_CORE, GUMAS_INTEGRATION, PICARD_DELTA_3_READY
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.core.native_dlp_export import NativeDLPTracker

logger = logging.getLogger(__name__)


@dataclass
class EthicsVerdict:
    """
    Normalized ethics evaluation verdict.

    Attributes:
        allowed: Whether the action is permitted
        score: Numeric ethics score (0.0-1.0, higher is more ethical)
        reason: Human-readable explanation
        engine: Source engine (e.g., "gumas", "picard_delta_3")
        timestamp: ISO timestamp of evaluation
        dlp_tag_id: DLP tag tracking this evaluation
    """
    allowed: bool
    score: float
    reason: str
    engine: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dlp_tag_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "allowed": self.allowed,
            "score": self.score,
            "reason": self.reason,
            "engine": self.engine,
            "timestamp": self.timestamp,
            "dlp_tag_id": self.dlp_tag_id
        }


class EthicsViolation(Exception):
    """
    Exception raised when an action is blocked by ethics evaluation.

    Attributes:
        message: Error message
        verdict: The EthicsVerdict that triggered the block
    """

    def __init__(self, message: str, verdict: EthicsVerdict):
        super().__init__(message)
        self.message = message
        self.verdict = verdict


class GUMASEthicsClient:
    """
    Thin adapter around GUMAS Ethics HTTP API.

    This client provides a simple interface to the existing GUMAS ethics
    evaluation service without deep coupling to the implementation.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize GUMAS client.

        Args:
            base_url: Base URL for the GUMAS API (default: local dev server)
        """
        self.base_url = base_url.rstrip("/")
        self._http_client = None

    async def evaluate(self, action: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate action against GUMAS ethics rules.

        Args:
            action: Action details with type, parameters, etc.
            context: Optional context information (caller, route, etc.)

        Returns:
            Raw GUMAS API response with compliant, should_block, violations, etc.

        Raises:
            Exception: If GUMAS API is unavailable or returns error
        """
        try:
            # Lazy import to avoid circular dependencies
            import httpx

            # Construct request payload
            agent_id = context.get("agent_id", "system") if context else "system"
            action_type = action.get("type", "unknown_action")
            parameters = {k: v for k, v in action.items() if k != "type"}
            context_tag = context.get("context_tag") if context else None

            request_payload = {
                "agent_id": agent_id,
                "action_type": action_type,
                "parameters": parameters,
                "context_tag": context_tag
            }

            # Call GUMAS API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/gumas/evaluate",
                    json=request_payload
                )
                response.raise_for_status()
                return response.json()

        except ImportError as e:
            logger.error("httpx not available for GUMAS client: %s", e)
            # Return safe default (deny)
            return {
                "compliant": False,
                "should_block": True,
                "violations": [{
                    "severity": "critical",
                    "description": "Ethics evaluation unavailable - httpx not installed",
                    "rule_name": "SAFETY_FALLBACK"
                }],
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error("GUMAS evaluation failed: %s", e)
            # Return safe default (deny)
            return {
                "compliant": False,
                "should_block": True,
                "violations": [{
                    "severity": "critical",
                    "description": f"Ethics evaluation error: {str(e)}",
                    "rule_name": "SAFETY_FALLBACK"
                }],
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            }


class EthicsGate:
    """
    Central ethics gate for evaluating actions and commands.

    Wraps GUMAS ethics API and prepares for future Picard_Delta_3 integration.
    Provides consistent ethics enforcement with DLP tracking and structured logging.

    Usage:
        client = GUMASEthicsClient()
        gate = EthicsGate(client, threshold=0.7)

        verdict = await gate.evaluate(
            action={"type": "delete_node", "node_id": "123", "layer": "L2"},
            context={"agent_id": "admin", "route": "/api/nodes/delete"}
        )

        if not verdict.allowed:
            raise EthicsViolation("Action blocked by ethics gate", verdict)
    """

    def __init__(
        self,
        client: GUMASEthicsClient,
        threshold: float = 0.7,
        dlp_tracker: Optional[NativeDLPTracker] = None
    ):
        """
        Initialize ethics gate.

        Args:
            client: GUMAS client for ethics evaluation
            threshold: Minimum score for approval (0.0-1.0, default 0.7)
            dlp_tracker: DLP tracker for lineage (creates new if None)
        """
        self.client = client
        self.threshold = threshold
        self.dlp_tracker = dlp_tracker or NativeDLPTracker()

        logger.info(
            "Ethics gate initialized (threshold=%.2f)",
            threshold,
            extra={
                "anchors": ["EOS_SEED_ORION", "Picard_Delta_3"],
                "aurora_module": "ethics_gate"
            }
        )

    async def evaluate(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> EthicsVerdict:
        """
        Evaluate action through ethics gate.

        This is the main entry point for ethics evaluation. It:
        1. Calls GUMAS API through the client
        2. Normalizes response into EthicsVerdict
        3. Generates DLP tag for tracking
        4. Logs evaluation with anchors

        Args:
            action: Action to evaluate with type and parameters
            context: Optional context (agent_id, route, source, etc.)

        Returns:
            EthicsVerdict with allowed, score, reason, etc.
        """
        start_time = time.time()

        try:
            # Call GUMAS API
            response = await self.client.evaluate(action, context)

            # Extract ethics score and reason
            compliant = response.get("compliant", False)
            should_block = response.get("should_block", True)
            violations = response.get("violations", [])

            # Calculate score (inverse of severity)
            # compliant with no violations = 1.0
            # critical violations = 0.0
            # medium violations = 0.5
            if compliant and not violations:
                score = 1.0
                reason = "Action complies with all ethics rules"
            else:
                # Score based on worst violation severity
                severities = {v.get("severity", "high") for v in violations}
                if "critical" in severities:
                    score = 0.0
                elif "high" in severities:
                    score = 0.3
                elif "medium" in severities:
                    score = 0.5
                else:
                    score = 0.7

                # Construct reason from violations
                violation_descriptions = [
                    f"{v.get('rule_name', 'UNKNOWN')}: {v.get('description', 'No description')}"
                    for v in violations[:3]  # Limit to first 3
                ]
                reason = "; ".join(violation_descriptions)
                if len(violations) > 3:
                    reason += f" (and {len(violations) - 3} more)"

            # Determine if allowed
            allowed = score >= self.threshold and not should_block

            # Create DLP tag for this evaluation
            dlp_tag_id = await self._create_dlp_tag(action, context, score, allowed, reason)

            # Create verdict
            verdict = EthicsVerdict(
                allowed=allowed,
                score=score,
                reason=reason,
                engine="gumas",
                dlp_tag_id=dlp_tag_id
            )

            # Log evaluation with structured data
            duration = time.time() - start_time
            logger.info(
                "Ethics evaluation: %s (score=%.2f, allowed=%s, duration=%.3fs)",
                action.get("type", "unknown"),
                score,
                allowed,
                duration,
                extra={
                    "anchors": ["EOS_SEED_ORION", "Picard_Delta_3"],
                    "ethics_verdict": verdict.to_dict(),
                    "action_type": action.get("type"),
                    "context": context,
                    "aurora_module": "ethics_gate"
                }
            )

            return verdict

        except Exception as e:
            logger.error(
                "Ethics evaluation failed: %s",
                e,
                extra={
                    "anchors": ["EOS_SEED_ORION", "Picard_Delta_3"],
                    "action": action,
                    "context": context,
                    "aurora_module": "ethics_gate"
                },
                exc_info=True
            )

            # Return safe default (deny)
            verdict = EthicsVerdict(
                allowed=False,
                score=0.0,
                reason=f"Ethics evaluation error: {str(e)}",
                engine="gumas"
            )
            return verdict

    async def _create_dlp_tag(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        score: float,
        allowed: bool,
        reason: str
    ) -> str:
        """
        Create DLP tag for ethics evaluation.

        Tags include anchor protocols and symbolic patterns as required.

        Args:
            action: Action that was evaluated
            context: Context of evaluation
            score: Ethics score
            allowed: Whether action was allowed
            reason: Evaluation reason

        Returns:
            DLP tag ID
        """
        # Create base tag
        tag_id = self.dlp_tracker.create_tag(
            operation="ethics_gate_evaluate",
            data={
                "action": action,
                "context": context,
                "score": score,
                "allowed": allowed,
                "reason": reason
            },
            tag_id=f"ethics::gate::evaluation::{int(time.time() * 1000)}"
        )

        # Get tag and enrich with Aurora/GUMAS fields
        tag = self.dlp_tracker.tags[tag_id]

        # Add anchor protocols (required by spec)
        tag.add_anchor_protocol("EOS_SEED_ORION")
        tag.add_anchor_protocol("Picard_Delta_3")

        # Add T1/SRB anchors (required by spec)
        tag.add_t1_srb_anchor("T1")
        tag.add_t1_srb_anchor("SRB")

        # Add symbolic patterns (required by spec)
        tag.set_symbolic_pattern(
            "ethics_context",
            {
                "action_type": action.get("type", "unknown"),
                "source": context.get("source", "unknown") if context else "unknown",
                "agent_id": context.get("agent_id", "system") if context else "system",
                "score": score,
                "allowed": allowed
            }
        )

        # Add metadata
        tag.metadata.update({
            "ethics_engine": "gumas",
            "threshold": self.threshold,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        return tag_id
