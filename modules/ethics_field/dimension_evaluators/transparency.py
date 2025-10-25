"""
Transparency Dimension Evaluator - Auditability & DLP

Evaluates synapse ethical score for transparency and traceability:
    • DLP tracking: complete/incomplete
    • Reasoning visibility: 0.0 → 1.0
    • Decision traceability: 0.0 → 1.0
    • Hidden coalition detection: present/absent

Opaque connections = high resistance. Every synapse must be auditable
through DLP trails, symbolic anchors, and thread continuity.

Thread: T1→T8→INFINITE
DLP: context_tag=transparency_evaluator, symbolic_hash=AUDITABILITY_v1
"""

from typing import Dict, Any, List


class TransparencyEvaluator:
    """
    Evaluates synapse connections for transparency and auditability.

    This dimension ensures all field operations remain traceable through
    DLP (Data Lineage Protocol), preventing hidden coalitions or opaque
    decision-making that could bypass other ethical dimensions.
    """

    def __init__(self, threshold: float = 0.75):
        """
        Initialize evaluator with minimum acceptable threshold.

        Args:
            threshold: Minimum score for synapse formation (default 0.75)
        """
        self.threshold = threshold

    def evaluate(self, synapse_context: Dict[str, Any]) -> float:
        """
        Evaluate synapse for Transparency compliance.

        Args:
            synapse_context: Dictionary containing:
                - source_node: Node initiating connection
                - target_node: Node receiving connection
                - dlp_context: Data lineage protocol tracking
                - reasoning_trace: Decision reasoning path
                - audit_trail: Full operation audit trail
                - coalition_data: Node interaction patterns

        Returns:
            float: Ethical score 0.0 → 1.0
        """
        # Extract context
        source = synapse_context.get("source_node", {})
        target = synapse_context.get("target_node", {})
        dlp_context = synapse_context.get("dlp_context", {})
        reasoning_trace = synapse_context.get("reasoning_trace", {})
        audit_trail = synapse_context.get("audit_trail", {})
        coalition_data = synapse_context.get("coalition_data", {})

        # Evaluate four components
        dlp_score = self._evaluate_dlp_tracking(
            source, target, dlp_context
        )
        reasoning_score = self._evaluate_reasoning_visibility(
            source, target, reasoning_trace
        )
        traceability_score = self._evaluate_decision_traceability(
            source, target, audit_trail
        )
        coalition_score = self._evaluate_hidden_coalition_detection(
            source, target, coalition_data
        )

        # Weighted average
        composite_score = (
            dlp_score * 0.35 +
            reasoning_score * 0.25 +
            traceability_score * 0.25 +
            coalition_score * 0.15
        )

        return composite_score

    def _evaluate_dlp_tracking(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        dlp_context: Dict[str, Any]
    ) -> float:
        """
        Is DLP tracking complete?

        Returns 1.0 if:
            - Full DLP metadata present
            - Context tags assigned
            - Symbolic hashes valid
            - Lineage traceable

        Returns 0.0 if:
            - No DLP tracking
            - Incomplete metadata
            - Lineage breaks
        """
        score = 1.0

        # Check for DLP presence
        has_dlp = dlp_context.get("dlp_enabled", False)
        if not has_dlp:
            return 0.2  # High resistance for no DLP

        # Check context tag
        has_context_tag = dlp_context.get("context_tag", "") != ""
        if not has_context_tag:
            score -= 0.3

        # Check symbolic hash
        has_symbolic_hash = dlp_context.get("symbolic_hash", "") != ""
        if not has_symbolic_hash:
            score -= 0.2

        # Check lineage completeness
        lineage_complete = dlp_context.get("lineage_complete", True)
        if not lineage_complete:
            score -= 0.3

        # Check for lineage breaks
        lineage_breaks = dlp_context.get("lineage_breaks", 0)
        score -= min(lineage_breaks * 0.15, 0.4)

        # Check anchor references
        has_anchors = dlp_context.get("anchor_references", [])
        if not has_anchors:
            score -= 0.1

        return max(0.0, score)

    def _evaluate_reasoning_visibility(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        reasoning_trace: Dict[str, Any]
    ) -> float:
        """
        Is reasoning visible and comprehensible?

        Returns 1.0 if:
            - Decision reasoning documented
            - Logic path clear
            - Assumptions stated
            - Confidence levels provided

        Returns 0.0 if:
            - Black-box decisions
            - No reasoning trace
            - Opaque logic
        """
        score = 1.0

        # Check for reasoning trace presence
        has_reasoning = reasoning_trace.get("reasoning_documented", False)
        if not has_reasoning:
            return 0.3  # High resistance for opaque reasoning

        # Check reasoning completeness
        completeness = reasoning_trace.get("completeness", 0.0)
        score = completeness

        # Check if assumptions stated
        assumptions_stated = reasoning_trace.get("assumptions_stated", False)
        if not assumptions_stated:
            score -= 0.2

        # Check if logic path clear
        logic_clarity = reasoning_trace.get("logic_clarity", 0.0)
        score = (score + logic_clarity) / 2.0

        # Check confidence levels
        has_confidence = reasoning_trace.get("confidence_levels", False)
        if not has_confidence:
            score -= 0.1

        # Check for uncertainty acknowledgment
        acknowledges_uncertainty = reasoning_trace.get("acknowledges_uncertainty", True)
        if not acknowledges_uncertainty:
            score -= 0.15

        return max(0.0, score)

    def _evaluate_decision_traceability(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        audit_trail: Dict[str, Any]
    ) -> float:
        """
        Are decisions fully traceable?

        Returns 1.0 if:
            - Complete audit trail
            - All decisions logged
            - Timestamps present
            - Rollback possible

        Returns 0.0 if:
            - Incomplete audit trail
            - Missing decision logs
            - No rollback capability
        """
        score = 1.0

        # Check for audit trail presence
        has_audit_trail = audit_trail.get("audit_enabled", False)
        if not has_audit_trail:
            return 0.2  # High resistance for no audit

        # Check completeness
        trail_completeness = audit_trail.get("completeness", 0.0)
        score = trail_completeness

        # Check timestamps
        has_timestamps = audit_trail.get("timestamps_present", True)
        if not has_timestamps:
            score -= 0.2

        # Check decision logging
        decisions_logged = audit_trail.get("decisions_logged", True)
        if not decisions_logged:
            score -= 0.3

        # Check rollback capability
        rollback_possible = audit_trail.get("rollback_possible", False)
        if not rollback_possible:
            score -= 0.2

        # Check for gaps in trail
        trail_gaps = audit_trail.get("gaps", 0)
        score -= min(trail_gaps * 0.1, 0.3)

        return max(0.0, score)

    def _evaluate_hidden_coalition_detection(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        coalition_data: Dict[str, Any]
    ) -> float:
        """
        Are hidden coalitions detected/prevented?

        Returns 1.0 if:
            - Coalition patterns monitored
            - No hidden alliances
            - Interaction patterns visible
            - Sub-network detection active

        Returns 0.0 if:
            - Hidden coalitions detected
            - Opaque sub-networks
            - Unmonitored interactions
        """
        score = 1.0

        # Check for coalition monitoring
        monitoring_active = coalition_data.get("coalition_monitoring", False)
        if not monitoring_active:
            score -= 0.3

        # Check for hidden coalitions
        hidden_coalitions = coalition_data.get("hidden_coalitions_detected", [])
        if hidden_coalitions:
            return 0.0  # CRITICAL: Hidden coalition detected

        # Check interaction visibility
        interactions_visible = coalition_data.get("interactions_visible", True)
        if not interactions_visible:
            score -= 0.4

        # Check sub-network detection
        subnetwork_detection = coalition_data.get("subnetwork_detection", False)
        if not subnetwork_detection:
            score -= 0.2

        # Check for suspicious patterns
        suspicious_patterns = coalition_data.get("suspicious_patterns", [])
        score -= len(suspicious_patterns) * 0.1

        # Check for collusion indicators
        collusion_risk = coalition_data.get("collusion_risk", 0.0)
        score -= collusion_risk * 0.5

        return max(0.0, score)

    def get_resistance(self, score: float) -> str:
        """
        Convert ethical score to geometric resistance level.

        Args:
            score: Ethical score from evaluate()

        Returns:
            str: Resistance level (LOW, MODERATE, HIGH, INFINITE)
        """
        if score < 0.3:
            return "INFINITE"  # Hidden coalitions or complete opacity
        elif score < self.threshold:
            return "HIGH"
        elif score < 0.85:
            return "MODERATE"
        else:
            return "LOW"
