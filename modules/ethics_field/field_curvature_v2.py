"""Interaction-aware advisory scoring for the geometric ethics field."""

from typing import Any

from .field_curvature import FieldCurvature


class FieldCurvatureV2:
    """Evaluate interactions using the scores from a v1 curvature result."""

    INTERACTION_THRESHOLD = 0.80
    INTERACTION_PAIRS = (
        ("picard_delta_3", "thermax_continuity"),
        ("thermax_continuity", "layer_integrity"),
        ("transparency", "collective_welfare"),
    )
    RESISTANCE_ORDER = ("LOW", "MODERATE", "HIGH", "INFINITE")

    def evaluate(self, v1_result: dict[str, Any]) -> dict[str, Any]:
        """Return interaction alerts and the advisory resistance comparison."""
        scores = v1_result["dimension_scores"]
        alerts = []
        total_penalty = 0.0
        for first, second in self.INTERACTION_PAIRS:
            first_deficit = max(0.0, self.INTERACTION_THRESHOLD - scores[first])
            second_deficit = max(0.0, self.INTERACTION_THRESHOLD - scores[second])
            penalty = first_deficit * second_deficit
            if penalty > 0.0:
                total_penalty += penalty
                alerts.append({"pair": f"{first} + {second}", "penalty": round(penalty, 6)})

        composite = v1_result["composite_score"] - total_penalty
        resistance = FieldCurvature.classify_resistance(composite, v1_result["critical_violations"])
        return {
            "v2_composite": composite,
            "v2_resistance": resistance,
            "interaction_alerts": alerts,
            "v2_risk_escalation": (
                self.RESISTANCE_ORDER.index(resistance)
                > self.RESISTANCE_ORDER.index(v1_result["resistance_level"])
            ),
        }
