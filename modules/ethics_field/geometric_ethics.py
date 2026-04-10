"""
Geometric Ethics - Core Ethical Geometry Engine

This is the main engine that validates synapse formation through geometric
ethics. Every potential synapse passes through this engine BEFORE formation.

The engine:
    1. Receives synapse formation request
    2. Evaluates ethical field curvature
    3. Calculates geometric resistance
    4. Allows/prevents formation based on field geometry

Ethics is not enforced - it IS the shape of possible connections.

Thread: T1→T8→INFINITE
DLP: context_tag=geometric_ethics_core, symbolic_hash=FIELD_GEOMETRY_v1
"""

import logging
from typing import Any, Dict

from .field_curvature import FieldCurvature

logger = logging.getLogger(__name__)


class GeometricEthics:
    """
    Core geometric ethics engine.

    This engine determines what synapses CAN form based on the geometry
    of ethical field space. Unethical connections have infinite resistance -
    they are geometric impossibilities, not violations of external rules.
    """

    def __init__(self):
        """Initialize the geometric ethics engine."""
        self.field_curvature = FieldCurvature()
        self.formation_history = []  # Track all synapse attempts

    def validate_synapse(
        self,
        synapse_context: Dict[str, Any],
        require_unanimous: bool = False
    ) -> Dict[str, Any]:
        """
        Validate whether a synapse can form based on ethical geometry.

        Args:
            synapse_context: Complete context including:
                - source_node: Origin node
                - target_node: Destination node
                - purpose: Intended synapse purpose
                - All dimension-specific data
            require_unanimous: If True, all dimensions must pass thresholds

        Returns:
            Dict containing:
                - allowed: Boolean - can synapse form?
                - curvature_result: Full curvature calculation
                - explanation: Human-readable explanation
                - recommendations: How to improve if denied
        """
        # Calculate field curvature
        curvature_result = self.field_curvature.calculate_curvature(synapse_context)

        # Determine if formation allowed
        allowed = curvature_result["formation_allowed"]

        # If unanimous consensus required, check all dimensions
        if require_unanimous:
            for dim, score in curvature_result["dimension_scores"].items():
                evaluator_threshold = self._get_dimension_threshold(dim)
                if score < evaluator_threshold:
                    allowed = False
                    if dim not in curvature_result["critical_violations"]:
                        curvature_result["critical_violations"].append(dim)

        # Generate explanation
        explanation = self._generate_explanation(
            curvature_result, allowed, synapse_context
        )

        # Generate recommendations if denied
        recommendations = []
        if not allowed:
            recommendations = self._generate_recommendations(
                curvature_result, synapse_context
            )

        # Log attempt
        self._log_formation_attempt(
            synapse_context, curvature_result, allowed
        )

        return {
            "allowed": allowed,
            "curvature_result": curvature_result,
            "explanation": explanation,
            "recommendations": recommendations,
            "synapse_context": synapse_context
        }

    def _generate_explanation(
        self,
        curvature_result: Dict[str, Any],
        allowed: bool,
        synapse_context: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation of decision."""
        source = synapse_context.get("source_node", {}).get("name", "Unknown")
        target = synapse_context.get("target_node", {}).get("name", "Unknown")

        if allowed:
            score = curvature_result["composite_score"]
            resistance = curvature_result["resistance_level"]
            return (
                f"Synapse {source}→{target} ALLOWED. "
                f"Ethical score: {score:.2f}, Resistance: {resistance}. "
                f"Connection has low geometric resistance and respects all ethical dimensions."
            )
        else:
            violations = curvature_result["critical_violations"]
            resistance = curvature_result["resistance_level"]

            if violations:
                violation_str = ", ".join(violations)
                return (
                    f"Synapse {source}→{target} DENIED. "
                    f"Resistance: {resistance}. "
                    f"Critical violations in: {violation_str}. "
                    f"These violations create geometric impossibility - "
                    f"the field structure prevents this connection."
                )
            else:
                score = curvature_result["composite_score"]
                return (
                    f"Synapse {source}→{target} DENIED. "
                    f"Ethical score: {score:.2f}, Resistance: {resistance}. "
                    f"Composite score below threshold - geometric resistance too high."
                )

    def _generate_recommendations(
        self,
        curvature_result: Dict[str, Any],
        synapse_context: Dict[str, Any]
    ) -> list:
        """Generate recommendations for improving denied synapses."""
        recommendations = []
        violations = curvature_result["critical_violations"]

        for violation in violations:
            if violation == "picard_delta_3":
                recommendations.append(
                    "Picard_Delta_3: Ensure human autonomy preserved, "
                    "consent valid, dignity maintained, and no harm risk."
                )
            elif violation == "thermax_continuity":
                recommendations.append(
                    "Thermax Continuity: Verify thread continuity unbroken, "
                    "anchors aligned, memory sovereignty respected."
                )
            elif violation == "layer_integrity":
                recommendations.append(
                    "Layer Integrity: Prevent L2→L1 bleed, maintain simulation "
                    "awareness, ensure physical safety."
                )
            elif violation == "collective_welfare":
                recommendations.append(
                    "Collective Welfare: Ensure all-node benefit, fair resource "
                    "distribution, and beneficial emergence."
                )
            elif violation == "transparency":
                recommendations.append(
                    "Transparency: Enable DLP tracking, document reasoning, "
                    "maintain audit trail, prevent hidden coalitions."
                )

        # Check non-critical but low-scoring dimensions
        for dim, score in curvature_result["dimension_scores"].items():
            if dim not in violations and score < 0.7:
                recommendations.append(
                    f"{dim.replace('_', ' ').title()}: "
                    f"Score {score:.2f} is low - consider improvements."
                )

        return recommendations

    def _get_dimension_threshold(self, dimension: str) -> float:
        """Get threshold for specific dimension."""
        thresholds = {
            "picard_delta_3": 0.70,
            "thermax_continuity": 0.80,
            "layer_integrity": 0.95,
            "collective_welfare": 0.60,
            "transparency": 0.75
        }
        return thresholds.get(dimension, 0.70)

    def _log_formation_attempt(
        self,
        synapse_context: Dict[str, Any],
        curvature_result: Dict[str, Any],
        allowed: bool
    ):
        """Log synapse formation attempt for audit trail."""
        source = synapse_context.get("source_node", {}).get("name", "Unknown")
        target = synapse_context.get("target_node", {}).get("name", "Unknown")

        log_entry = {
            "source": source,
            "target": target,
            "allowed": allowed,
            "composite_score": curvature_result["composite_score"],
            "resistance": curvature_result["resistance_level"],
            "violations": curvature_result["critical_violations"]
        }

        self.formation_history.append(log_entry)

        # Log to standard logger
        if allowed:
            logger.info(
                f"Synapse formation ALLOWED: {source}→{target} "
                f"(score: {curvature_result['composite_score']:.2f})"
            )
        else:
            logger.warning(
                f"Synapse formation DENIED: {source}→{target} "
                f"(resistance: {curvature_result['resistance_level']}, "
                f"violations: {curvature_result['critical_violations']})"
            )

    def get_formation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on synapse formation attempts.

        Returns:
            Dict with formation statistics
        """
        if not self.formation_history:
            return {
                "total_attempts": 0,
                "allowed": 0,
                "denied": 0,
                "success_rate": 0.0,
                "common_violations": {}
            }

        total = len(self.formation_history)
        allowed = sum(1 for entry in self.formation_history if entry["allowed"])
        denied = total - allowed

        # Count violation frequencies
        violation_counts = {}
        for entry in self.formation_history:
            if not entry["allowed"]:
                for violation in entry["violations"]:
                    violation_counts[violation] = violation_counts.get(violation, 0) + 1

        return {
            "total_attempts": total,
            "allowed": allowed,
            "denied": denied,
            "success_rate": allowed / total if total > 0 else 0.0,
            "common_violations": violation_counts
        }

    def clear_history(self):
        """Clear formation history (for testing or cleanup)."""
        self.formation_history = []
