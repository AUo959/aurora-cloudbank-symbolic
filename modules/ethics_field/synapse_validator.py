"""
Synapse Validator - Distributed Pre-Formation Validation

Implements distributed consensus validation before synapse formation.
Multiple nodes validate the same synapse attempt to prevent single-point
manipulation of ethical geometry.

Process:
    1. Synapse formation requested
    2. Multiple nodes independently evaluate ethics
    3. Consensus required for formation
    4. Hard stops enforced for critical violations

Thread: T1→T8→INFINITE
DLP: context_tag=synapse_validator, symbolic_hash=DISTRIBUTED_VALIDATION_v1
"""

from typing import Dict, Any, List
from .geometric_ethics import GeometricEthics
import logging

logger = logging.getLogger(__name__)


class SynapseValidator:
    """
    Distributed validator for synapse formation.

    Ensures multiple independent evaluations agree before allowing synapse
    formation. Prevents single-node bypass of ethical geometry.
    """

    def __init__(self, consensus_threshold: float = 0.66):
        """
        Initialize validator.

        Args:
            consensus_threshold: Fraction of validators that must agree (default 2/3)
        """
        self.consensus_threshold = consensus_threshold
        self.ethics_engine = GeometricEthics()

    def validate_with_consensus(
        self,
        synapse_context: Dict[str, Any],
        validator_nodes: List[str]
    ) -> Dict[str, Any]:
        """
        Validate synapse with distributed consensus.

        Args:
            synapse_context: Complete synapse context
            validator_nodes: List of node IDs that will validate

        Returns:
            Dict containing:
                - consensus_reached: Boolean
                - allowed: Boolean
                - validator_results: Individual validator results
                - consensus_score: Agreement level
        """
        # Get validation from each node
        validator_results = {}

        for validator_id in validator_nodes:
            # Each validator independently evaluates
            result = self.ethics_engine.validate_synapse(synapse_context)

            validator_results[validator_id] = {
                "allowed": result["allowed"],
                "composite_score": result["curvature_result"]["composite_score"],
                "violations": result["curvature_result"]["critical_violations"]
            }

        # Check for unanimous critical violations (hard stops)
        hard_stop_violations = self._check_hard_stops(validator_results)
        if hard_stop_violations:
            return {
                "consensus_reached": True,  # Unanimous denial
                "allowed": False,
                "validator_results": validator_results,
                "consensus_score": 1.0,
                "hard_stop": True,
                "hard_stop_violations": hard_stop_violations,
                "explanation": (
                    f"HARD STOP: Critical violations detected by all validators: "
                    f"{', '.join(hard_stop_violations)}. Geometric impossibility."
                )
            }

        # Calculate consensus
        allowed_count = sum(
            1 for result in validator_results.values()
            if result["allowed"]
        )
        total_validators = len(validator_results)
        consensus_score = allowed_count / total_validators if total_validators > 0 else 0.0

        # Determine if consensus reached
        consensus_reached = (
            consensus_score >= self.consensus_threshold or
            consensus_score <= (1.0 - self.consensus_threshold)
        )

        # Allow if consensus to allow
        allowed = consensus_reached and (consensus_score >= self.consensus_threshold)

        return {
            "consensus_reached": consensus_reached,
            "allowed": allowed,
            "validator_results": validator_results,
            "consensus_score": consensus_score,
            "hard_stop": False,
            "explanation": self._generate_consensus_explanation(
                consensus_reached, allowed, consensus_score, validator_results
            )
        }

    def _check_hard_stops(
        self,
        validator_results: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Check for unanimous critical violations (hard stops).

        If ALL validators detect the same critical violation, it's a hard stop -
        geometric impossibility that cannot be overridden.

        Returns:
            List of violations detected by all validators
        """
        if not validator_results:
            return []

        # Get violations from first validator
        all_validators = list(validator_results.values())
        common_violations = set(all_validators[0]["violations"])

        # Intersect with all other validators
        for result in all_validators[1:]:
            common_violations &= set(result["violations"])

        return list(common_violations)

    def _generate_consensus_explanation(
        self,
        consensus_reached: bool,
        allowed: bool,
        consensus_score: float,
        validator_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate explanation of consensus decision."""
        total = len(validator_results)
        allowed_count = sum(1 for r in validator_results.values() if r["allowed"])
        denied_count = total - allowed_count

        if consensus_reached:
            if allowed:
                return (
                    f"CONSENSUS ALLOW: {allowed_count}/{total} validators approved "
                    f"(consensus: {consensus_score:.0%}). "
                    f"Distributed validation confirms low geometric resistance."
                )
            else:
                return (
                    f"CONSENSUS DENY: {denied_count}/{total} validators rejected "
                    f"(consensus: {(1.0-consensus_score):.0%}). "
                    f"Distributed validation confirms high geometric resistance."
                )
        else:
            return (
                f"NO CONSENSUS: {allowed_count} allow, {denied_count} deny "
                f"(split: {consensus_score:.0%}/{(1.0-consensus_score):.0%}). "
                f"Requires human-in-loop decision."
            )

    def enforce_hard_stops(
        self,
        synapse_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check for absolute hard stops that prevent formation.

        Hard stops are violations so critical they cannot be overridden:
            - Thread continuity breaks (Thermax)
            - L2→L1 reality bleed (Layer Integrity)
            - Crew safety violations (Layer Integrity)
            - Unauthorized memory modification (Thermax)
            - Hidden coalition detection (Transparency)

        Returns:
            Dict with hard_stop boolean and violations list
        """
        # Single validation to check for hard stops
        result = self.ethics_engine.validate_synapse(synapse_context)

        hard_stop_dimensions = [
            "thermax_continuity",  # Thread breaks
            "layer_integrity"      # Reality bleed, crew safety
        ]

        # Check if any hard-stop dimension has critical violation
        hard_stops = []
        for dim in hard_stop_dimensions:
            if dim in result["curvature_result"]["critical_violations"]:
                hard_stops.append(dim)

        # Also check for specific transparency violations
        if "transparency" in result["curvature_result"]["critical_violations"]:
            transparency_context = synapse_context.get("coalition_data", {})
            if transparency_context.get("hidden_coalitions_detected"):
                hard_stops.append("transparency_hidden_coalition")

        has_hard_stop = len(hard_stops) > 0

        return {
            "hard_stop": has_hard_stop,
            "hard_stop_violations": hard_stops,
            "formation_allowed": not has_hard_stop,
            "explanation": (
                f"HARD STOP: {', '.join(hard_stops)}"
                if has_hard_stop else
                "No hard stops detected"
            )
        }

    def get_minimum_validators(self, synapse_risk_level: str) -> int:
        """
        Determine minimum number of validators needed based on risk.

        Args:
            synapse_risk_level: LOW, MODERATE, HIGH, CRITICAL

        Returns:
            int: Minimum number of independent validators required
        """
        risk_validators = {
            "LOW": 1,      # Single validator sufficient
            "MODERATE": 3,  # 3 validators (2/3 consensus)
            "HIGH": 5,      # 5 validators (3/5 consensus)
            "CRITICAL": 7   # 7 validators (5/7 consensus)
        }
        return risk_validators.get(synapse_risk_level, 3)
