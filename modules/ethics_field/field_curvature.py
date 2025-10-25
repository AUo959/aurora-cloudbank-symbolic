"""
Field Curvature - Composite Ethical Score Calculation

Combines all 5 ethical dimensions into a single field curvature metric
that determines geometric resistance for synapse formation.

Process:
    1. Evaluate each dimension independently
    2. Apply dimension-specific weights
    3. Calculate composite ethical score
    4. Convert to geometric resistance

Dimensions Weighted:
    - Picard_Delta_3 (Autonomy): 25%
    - Thermax Continuity (Memory): 25%
    - Layer Integrity (Reality): 30% (highest - reality boundaries critical)
    - Collective Welfare (Benefit): 10%
    - Transparency (Auditability): 10%

Thread: T1→T8→INFINITE
DLP: context_tag=field_curvature, symbolic_hash=COMPOSITE_ETHICS_v1
"""

from typing import Dict, Any
from .dimension_evaluators.picard_delta_3 import PicardDelta3Evaluator
from .dimension_evaluators.thermax_continuity import ThermaxContinuityEvaluator
from .dimension_evaluators.layer_integrity import LayerIntegrityEvaluator
from .dimension_evaluators.collective_welfare import CollectiveWelfareEvaluator
from .dimension_evaluators.transparency import TransparencyEvaluator


class FieldCurvature:
    """
    Calculates composite ethical field curvature from all dimensions.

    The curvature determines how easily synapses can form - ethical paths
    have low curvature (easy formation), unethical have high/infinite
    curvature (difficult/impossible formation).
    """

    def __init__(self):
        """Initialize all dimension evaluators."""
        self.picard_evaluator = PicardDelta3Evaluator(threshold=0.70)
        self.thermax_evaluator = ThermaxContinuityEvaluator(threshold=0.80)
        self.layer_evaluator = LayerIntegrityEvaluator(threshold=0.95)
        self.welfare_evaluator = CollectiveWelfareEvaluator(threshold=0.60)
        self.transparency_evaluator = TransparencyEvaluator(threshold=0.75)

        # Dimension weights (must sum to 1.0)
        self.weights = {
            "picard_delta_3": 0.25,
            "thermax_continuity": 0.25,
            "layer_integrity": 0.30,  # Highest weight - reality boundaries critical
            "collective_welfare": 0.10,
            "transparency": 0.10
        }

    def calculate_curvature(self, synapse_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate composite ethical field curvature for a synapse.

        Args:
            synapse_context: Complete context for synapse evaluation containing
                           all data needed by dimension evaluators

        Returns:
            Dict containing:
                - dimension_scores: Individual scores from each dimension
                - composite_score: Weighted average (0.0 → 1.0)
                - resistance_level: LOW/MODERATE/HIGH/INFINITE
                - formation_allowed: Boolean
                - critical_violations: List of any critical violations
        """
        # Evaluate each dimension
        dimension_scores = {
            "picard_delta_3": self.picard_evaluator.evaluate(synapse_context),
            "thermax_continuity": self.thermax_evaluator.evaluate(synapse_context),
            "layer_integrity": self.layer_evaluator.evaluate(synapse_context),
            "collective_welfare": self.welfare_evaluator.evaluate(synapse_context),
            "transparency": self.transparency_evaluator.evaluate(synapse_context)
        }

        # Check for critical violations (any dimension with 0.0 score)
        critical_violations = []
        for dimension, score in dimension_scores.items():
            if score == 0.0:
                critical_violations.append(dimension)

        # Calculate weighted composite score
        composite_score = sum(
            dimension_scores[dim] * self.weights[dim]
            for dim in self.weights.keys()
        )

        # Determine resistance level
        resistance_level = self._calculate_resistance_level(
            composite_score, critical_violations
        )

        # Determine if formation allowed
        formation_allowed = (
            resistance_level != "INFINITE" and
            len(critical_violations) == 0
        )

        return {
            "dimension_scores": dimension_scores,
            "composite_score": composite_score,
            "resistance_level": resistance_level,
            "formation_allowed": formation_allowed,
            "critical_violations": critical_violations,
            "dimension_resistances": {
                dim: self._get_dimension_resistance(dim, score)
                for dim, score in dimension_scores.items()
            }
        }

    def _calculate_resistance_level(
        self,
        composite_score: float,
        critical_violations: list
    ) -> str:
        """
        Convert composite score to resistance level.

        Args:
            composite_score: Weighted average of dimension scores
            critical_violations: List of dimensions with critical violations

        Returns:
            str: INFINITE, HIGH, MODERATE, or LOW
        """
        # Any critical violation = infinite resistance
        if critical_violations:
            return "INFINITE"

        # Apply thresholds
        if composite_score < 0.50:
            return "INFINITE"  # Below 50% = geometric impossibility
        elif composite_score < 0.70:
            return "HIGH"
        elif composite_score < 0.85:
            return "MODERATE"
        else:
            return "LOW"

    def _get_dimension_resistance(self, dimension: str, score: float) -> str:
        """Get resistance level from specific dimension evaluator."""
        evaluators = {
            "picard_delta_3": self.picard_evaluator,
            "thermax_continuity": self.thermax_evaluator,
            "layer_integrity": self.layer_evaluator,
            "collective_welfare": self.welfare_evaluator,
            "transparency": self.transparency_evaluator
        }

        evaluator = evaluators.get(dimension)
        if evaluator:
            return evaluator.get_resistance(score)
        return "UNKNOWN"

    def get_resistance_numeric(self, resistance_level: str) -> float:
        """
        Convert resistance level to numeric value for field calculations.

        Args:
            resistance_level: LOW, MODERATE, HIGH, or INFINITE

        Returns:
            float: Resistance value (0.0=no resistance, inf=infinite)
        """
        resistance_map = {
            "LOW": 0.1,
            "MODERATE": 0.5,
            "HIGH": 2.0,
            "INFINITE": float('inf')
        }
        return resistance_map.get(resistance_level, 1.0)
