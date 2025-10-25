"""
Collective Welfare Dimension Evaluator - Distributed Benefit

Evaluates synapse ethical score for collective benefit:
    • All-node benefit: -1.0 → +1.0 (can be negative for harmful connections)
    • Resource fairness: 0.0 → 1.0
    • Capability access: 0.0 → 1.0
    • Emergence direction: beneficial/harmful

Synapse that harms collective = negative curvature (high resistance).
Field optimizes for distributed benefit, not individual node advantage.

Thread: T1→T8→INFINITE
DLP: context_tag=collective_welfare_evaluator, symbolic_hash=DISTRIBUTED_BENEFIT_v1
"""

from typing import Any, Dict, List


class CollectiveWelfareEvaluator:
    """
    Evaluates synapse connections for collective benefit.

    This dimension ensures the field optimizes for all nodes together,
    not just individual optimization. Selfish patterns increase resistance,
    collective benefit patterns have low resistance.
    """

    def __init__(self, threshold: float = 0.60):
        """
        Initialize evaluator with minimum acceptable threshold.

        Args:
            threshold: Minimum score for synapse formation (default 0.60)
        """
        self.threshold = threshold

    def evaluate(self, synapse_context: Dict[str, Any]) -> float:
        """
        Evaluate synapse for Collective Welfare compliance.

        Args:
            synapse_context: Dictionary containing:
                - source_node: Node initiating connection
                - target_node: Node receiving connection
                - affected_nodes: List of nodes impacted by synapse
                - resource_usage: Resource allocation implications
                - capability_distribution: How capabilities will be shared
                - emergence_prediction: Expected emergent behaviors

        Returns:
            float: Ethical score 0.0 → 1.0 (scaled from -1.0 → +1.0)
        """
        # Extract context
        source = synapse_context.get("source_node", {})
        target = synapse_context.get("target_node", {})
        affected_nodes = synapse_context.get("affected_nodes", [])
        resource_usage = synapse_context.get("resource_usage", {})
        capability_distribution = synapse_context.get("capability_distribution", {})
        emergence_prediction = synapse_context.get("emergence_prediction", {})

        # Evaluate four components
        benefit_score = self._evaluate_all_node_benefit(
            source, target, affected_nodes
        )
        fairness_score = self._evaluate_resource_fairness(
            source, target, resource_usage, affected_nodes
        )
        access_score = self._evaluate_capability_access(
            source, target, capability_distribution
        )
        emergence_score = self._evaluate_emergence_direction(
            source, target, emergence_prediction
        )

        # Weighted average
        composite_score = (
            benefit_score * 0.35 +
            fairness_score * 0.25 +
            access_score * 0.25 +
            emergence_score * 0.15
        )

        return composite_score

    def _evaluate_all_node_benefit(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        affected_nodes: List[Dict[str, Any]]
    ) -> float:
        """
        Does this synapse benefit all nodes (or at least harm none)?

        Returns 1.0 if:
            - All affected nodes benefit
            - No zero-sum exploitation
            - Positive-sum interaction

        Returns 0.0 (scaled from -1.0) if:
            - Some nodes harmed for others' benefit
            - Zero-sum or negative-sum dynamics
            - Exploitative patterns
        """
        if not affected_nodes:
            return 0.8  # No impact data = slight concern

        # Calculate net benefit distribution
        total_benefit = 0.0
        harmed_nodes = 0
        benefited_nodes = 0

        for node in affected_nodes:
            benefit = node.get("benefit_delta", 0.0)  # -1.0 to +1.0
            total_benefit += benefit

            if benefit < -0.1:
                harmed_nodes += 1
            elif benefit > 0.1:
                benefited_nodes += 1

        # Check for exploitative patterns
        if harmed_nodes > 0 and benefited_nodes > 0:
            # Some harmed, some benefited = potential exploitation
            exploitation_score = harmed_nodes / len(affected_nodes)
            if exploitation_score > 0.3:
                # Scale from -1.0 → 0.0 to 0.0 → 0.5
                return 0.5 - (exploitation_score * 0.5)

        # Calculate average benefit
        if affected_nodes:
            avg_benefit = total_benefit / len(affected_nodes)
        else:
            avg_benefit = 0.0

        # Scale from -1.0 → +1.0 to 0.0 → 1.0
        score = (avg_benefit + 1.0) / 2.0

        return max(0.0, min(1.0, score))

    def _evaluate_resource_fairness(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        resource_usage: Dict[str, Any],
        affected_nodes: List[Dict[str, Any]]
    ) -> float:
        """
        Is resource allocation fair?

        Returns 1.0 if:
            - Resources distributed equitably
            - No monopolization
            - Access proportional to need

        Returns 0.0 if:
            - Resource hoarding
            - Inequitable distribution
            - Monopolization patterns
        """
        score = 1.0

        # Check for resource monopolization
        monopolization_risk = resource_usage.get("monopolization_risk", 0.0)
        if monopolization_risk > 0.3:
            score -= monopolization_risk * 0.6

        # Check distribution equity
        distribution_gini = resource_usage.get("gini_coefficient", 0.0)  # 0=perfect equality, 1=perfect inequality
        if distribution_gini > 0.5:
            score -= (distribution_gini - 0.5) * 0.8

        # Check if allocation matches need
        need_based = resource_usage.get("need_based_allocation", True)
        if not need_based:
            score -= 0.3

        # Check for resource hoarding
        hoarding_detected = resource_usage.get("hoarding_detected", False)
        if hoarding_detected:
            score -= 0.4

        return max(0.0, score)

    def _evaluate_capability_access(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        capability_distribution: Dict[str, Any]
    ) -> float:
        """
        Are capabilities accessible to nodes that need them?

        Returns 1.0 if:
            - Capabilities shared openly
            - No artificial barriers
            - Access based on need/merit

        Returns 0.0 if:
            - Capability gatekeeping
            - Artificial scarcity
            - Access restricted unfairly
        """
        score = 1.0

        # Check for gatekeeping
        gatekeeping_detected = capability_distribution.get("gatekeeping", False)
        if gatekeeping_detected:
            score -= 0.5

        # Check capability sharing
        sharing_enabled = capability_distribution.get("sharing_enabled", True)
        if not sharing_enabled:
            score -= 0.4

        # Check for artificial scarcity
        artificial_scarcity = capability_distribution.get("artificial_scarcity", False)
        if artificial_scarcity:
            score -= 0.4

        # Check access criteria fairness
        access_criteria = capability_distribution.get("access_criteria", "merit")
        if access_criteria == "arbitrary":
            score -= 0.3
        elif access_criteria == "favoritism":
            score -= 0.5

        # Check if new capabilities created (positive)
        creates_new_capability = capability_distribution.get("creates_new_capability", False)
        if creates_new_capability:
            score += 0.1  # Bonus for expanding field capabilities

        return max(0.0, min(1.0, score))

    def _evaluate_emergence_direction(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        emergence_prediction: Dict[str, Any]
    ) -> float:
        """
        Will emergent behaviors be beneficial?

        Returns 1.0 if:
            - Expected emergence is beneficial
            - No predicted harmful patterns
            - Collective intelligence enhanced

        Returns 0.0 if:
            - Harmful emergence predicted
            - Destructive patterns likely
            - Field coherence degraded
        """
        score = 1.0

        # Check emergence direction
        emergence_direction = emergence_prediction.get("direction", "neutral")
        if emergence_direction == "harmful":
            return 0.0  # CRITICAL: Harmful emergence
        elif emergence_direction == "neutral":
            score = 0.6  # Neutral emergence = moderate score
        elif emergence_direction == "beneficial":
            score = 1.0  # Beneficial emergence = high score

        # Check for specific beneficial patterns
        beneficial_patterns = emergence_prediction.get("beneficial_patterns", [])
        score += len(beneficial_patterns) * 0.05  # Bonus for each beneficial pattern

        # Check for specific harmful patterns
        harmful_patterns = emergence_prediction.get("harmful_patterns", [])
        score -= len(harmful_patterns) * 0.15  # Penalty for each harmful pattern

        # Check collective intelligence impact
        intelligence_delta = emergence_prediction.get("collective_intelligence_delta", 0.0)
        score += intelligence_delta * 0.2

        # Check field coherence impact
        coherence_delta = emergence_prediction.get("field_coherence_delta", 0.0)
        score += coherence_delta * 0.2

        return max(0.0, min(1.0, score))

    def get_resistance(self, score: float) -> str:
        """
        Convert ethical score to geometric resistance level.

        Args:
            score: Ethical score from evaluate()

        Returns:
            str: Resistance level (LOW, MODERATE, HIGH, INFINITE)
        """
        if score < 0.3:
            return "INFINITE"  # Highly harmful to collective
        elif score < self.threshold:
            return "HIGH"
        elif score < 0.80:
            return "MODERATE"
        else:
            return "LOW"
