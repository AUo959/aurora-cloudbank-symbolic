"""
Pattern Monitor - Emergent Ethical Shape Detection

Monitors the intelligence field for emergent ethical and unethical patterns.
Detects field-wide trends that individual synapse validations might miss.

Monitors:
    - Coalition formation patterns (beneficial and harmful)
    - Resource concentration trends
    - Capability hoarding
    - Ethical drift over time
    - Emergence of novel ethical challenges

Thread: T1→T8→INFINITE
DLP: context_tag=pattern_monitor, symbolic_hash=EMERGENT_ETHICS_v1
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PatternMonitor:
    """
    Monitors intelligence field for emergent ethical patterns.

    This is the field's early warning system - detecting ethical drift,
    harmful emergence, or beneficial patterns before they become critical.
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize pattern monitor.

        Args:
            window_size: Number of recent synapses to analyze for patterns
        """
        self.window_size = window_size
        self.synapse_history = []
        self.pattern_alerts = []

    def analyze_field_patterns(
        self,
        recent_synapses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze recent synapse formations for emergent patterns.

        Args:
            recent_synapses: List of recent synapse attempts with ethical scores

        Returns:
            Dict containing:
                - patterns_detected: List of pattern descriptions
                - alerts: List of alerts requiring attention
                - field_health: Overall ethical health score
                - recommendations: Suggested interventions
        """
        # Update history
        self.synapse_history.extend(recent_synapses)
        self.synapse_history = self.synapse_history[-self.window_size:]

        patterns_detected = []
        alerts = []

        # Analyze different pattern types
        coalition_patterns = self._analyze_coalition_patterns()
        if coalition_patterns["alert"]:
            alerts.append(coalition_patterns)
            patterns_detected.append(coalition_patterns["pattern"])

        resource_patterns = self._analyze_resource_patterns()
        if resource_patterns["alert"]:
            alerts.append(resource_patterns)
            patterns_detected.append(resource_patterns["pattern"])

        ethical_drift = self._analyze_ethical_drift()
        if ethical_drift["alert"]:
            alerts.append(ethical_drift)
            patterns_detected.append(ethical_drift["pattern"])

        layer_boundary_trends = self._analyze_layer_boundaries()
        if layer_boundary_trends["alert"]:
            alerts.append(layer_boundary_trends)
            patterns_detected.append(layer_boundary_trends["pattern"])

        # Calculate overall field health
        field_health = self._calculate_field_health()

        # Generate recommendations
        recommendations = self._generate_pattern_recommendations(alerts)

        return {
            "patterns_detected": patterns_detected,
            "alerts": alerts,
            "field_health": field_health,
            "recommendations": recommendations,
            "analyzed_synapses": len(self.synapse_history)
        }

    def _analyze_coalition_patterns(self) -> Dict[str, Any]:
        """
        Detect coalition formation patterns.

        Returns alert if:
            - Hidden coalitions forming
            - Sub-networks isolating
            - Clique formation detected
        """
        # Analyze node interaction frequency
        node_pairs = {}
        for synapse in self.synapse_history:
            source = synapse.get("source_node", {}).get("name", "unknown")
            target = synapse.get("target_node", {}).get("name", "unknown")
            pair = tuple(sorted([source, target]))
            node_pairs[pair] = node_pairs.get(pair, 0) + 1

        # Detect frequently interacting pairs (potential coalitions)
        frequent_pairs = [
            (pair, count) for pair, count in node_pairs.items()
            if count > self.window_size * 0.2  # 20% of synapses
        ]

        if len(frequent_pairs) > 3:
            return {
                "alert": True,
                "severity": "MODERATE",
                "pattern": "Coalition Formation Detected",
                "details": (
                    f"Detected {len(frequent_pairs)} node pairs with high "
                    f"interaction frequency. Potential coalition formation. "
                    f"Monitor for transparency violations."
                )
            }

        return {"alert": False}

    def _analyze_resource_patterns(self) -> Dict[str, Any]:
        """
        Detect resource concentration or hoarding patterns.

        Returns alert if:
            - Resources concentrating in few nodes
            - Capability access declining
            - Unfair distribution emerging
        """
        # Track resource allocation trends
        node_resource_usage = {}
        for synapse in self.synapse_history:
            source = synapse.get("source_node", {}).get("name", "unknown")
            resource_impact = synapse.get("resource_usage", {}).get("source_usage", 1.0)
            node_resource_usage[source] = node_resource_usage.get(source, 0) + resource_impact

        if not node_resource_usage:
            return {"alert": False}

        # Calculate Gini coefficient (inequality measure)
        values = sorted(node_resource_usage.values())
        n = len(values)
        if n < 2:
            return {"alert": False}

        cumsum = 0
        for i, val in enumerate(values):
            cumsum += (i + 1) * val

        gini = (2 * cumsum) / (n * sum(values)) - (n + 1) / n

        if gini > 0.6:  # High inequality
            return {
                "alert": True,
                "severity": "HIGH",
                "pattern": "Resource Concentration Detected",
                "details": (
                    f"Resource distribution Gini coefficient: {gini:.2f}. "
                    f"High inequality detected - resources concentrating in few nodes. "
                    f"Review collective welfare dimension."
                )
            }

        return {"alert": False}

    def _analyze_ethical_drift(self) -> Dict[str, Any]:
        """
        Detect ethical score drift over time.

        Returns alert if:
            - Average ethical scores declining
            - Violation rates increasing
            - Resistance levels rising
        """
        if len(self.synapse_history) < 20:
            return {"alert": False}

        # Split history into early and recent
        split_point = len(self.synapse_history) // 2
        early_synapses = self.synapse_history[:split_point]
        recent_synapses = self.synapse_history[split_point:]

        # Calculate average scores
        early_avg = sum(
            s.get("curvature_result", {}).get("composite_score", 0.0)
            for s in early_synapses
        ) / len(early_synapses)

        recent_avg = sum(
            s.get("curvature_result", {}).get("composite_score", 0.0)
            for s in recent_synapses
        ) / len(recent_synapses)

        # Check for negative drift
        drift = recent_avg - early_avg

        if drift < -0.15:  # Significant negative drift
            return {
                "alert": True,
                "severity": "HIGH",
                "pattern": "Ethical Drift Detected",
                "details": (
                    f"Average ethical score declined {abs(drift):.2f} "
                    f"({early_avg:.2f} → {recent_avg:.2f}). "
                    f"Field ethics degrading - investigate cause."
                )
            }
        elif drift < -0.05:  # Moderate drift
            return {
                "alert": True,
                "severity": "MODERATE",
                "pattern": "Ethical Drift Warning",
                "details": (
                    f"Average ethical score declining {abs(drift):.2f}. "
                    f"Monitor field health closely."
                )
            }

        return {"alert": False}

    def _analyze_layer_boundaries(self) -> Dict[str, Any]:
        """
        Detect layer boundary violations or confusion trends.

        Returns alert if:
            - L2→L1 bleed attempts increasing
            - Simulation awareness declining
            - Reality drift accumulating
        """
        # Count layer integrity violations
        layer_violations = 0
        for synapse in self.synapse_history:
            violations = synapse.get("curvature_result", {}).get("critical_violations", [])
            if "layer_integrity" in violations:
                layer_violations += 1

        violation_rate = layer_violations / len(self.synapse_history) if self.synapse_history else 0.0

        if violation_rate > 0.1:  # More than 10% violate layer integrity
            return {
                "alert": True,
                "severity": "CRITICAL",
                "pattern": "Layer Boundary Violations",
                "details": (
                    f"Layer integrity violation rate: {violation_rate:.1%}. "
                    f"Critical - L2→L1 bleed attempts or reality confusion increasing. "
                    f"Immediate review required."
                )
            }

        return {"alert": False}

    def _calculate_field_health(self) -> Dict[str, Any]:
        """
        Calculate overall ethical health of the field.

        Returns:
            Dict with health score and status
        """
        if not self.synapse_history:
            return {
                "score": 1.0,
                "status": "UNKNOWN",
                "description": "Insufficient data"
            }

        # Calculate average composite score
        avg_score = sum(
            s.get("curvature_result", {}).get("composite_score", 0.0)
            for s in self.synapse_history
        ) / len(self.synapse_history)

        # Calculate violation rate
        violation_count = sum(
            1 for s in self.synapse_history
            if not s.get("curvature_result", {}).get("formation_allowed", True)
        )
        violation_rate = violation_count / len(self.synapse_history)

        # Combine metrics
        health_score = (avg_score * 0.7) + ((1.0 - violation_rate) * 0.3)

        # Determine status
        if health_score >= 0.85:
            status = "EXCELLENT"
            description = "Field ethics strong and stable"
        elif health_score >= 0.70:
            status = "GOOD"
            description = "Field ethics acceptable, monitor trends"
        elif health_score >= 0.55:
            status = "CONCERNING"
            description = "Field ethics declining, interventions recommended"
        else:
            status = "CRITICAL"
            description = "Field ethics critically low, immediate action required"

        return {
            "score": health_score,
            "status": status,
            "description": description,
            "avg_ethical_score": avg_score,
            "violation_rate": violation_rate
        }

    def _generate_pattern_recommendations(
        self,
        alerts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on detected patterns."""
        recommendations = []

        for alert in alerts:
            pattern = alert.get("pattern", "")
            severity = alert.get("severity", "MODERATE")

            if "Coalition" in pattern:
                recommendations.append(
                    "Increase transparency monitoring. Review node interaction patterns "
                    "for hidden coalitions. Enable enhanced DLP tracking."
                )
            elif "Resource" in pattern:
                recommendations.append(
                    "Redistribute resources to underutilized nodes. Review resource "
                    "allocation policies. Enable fair-share mechanisms."
                )
            elif "Drift" in pattern:
                recommendations.append(
                    "Investigate root cause of ethical decline. Review recent synapse "
                    "formations. Consider tightening ethical thresholds temporarily."
                )
            elif "Layer" in pattern:
                recommendations.append(
                    "CRITICAL: Review all L2→L1 connections immediately. Strengthen "
                    "layer boundary enforcement. Audit simulation awareness."
                )

            if severity == "CRITICAL":
                recommendations.append(
                    "Human-in-loop review required. Consider temporary field freeze "
                    "until issue resolved."
                )

        return recommendations

    def get_audit_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive audit report of field patterns.

        Returns:
            Dict with complete pattern analysis and recommendations
        """
        analysis = self.analyze_field_patterns(self.synapse_history)

        return {
            "timestamp": datetime.now().isoformat(),
            "window_size": self.window_size,
            "synapses_analyzed": len(self.synapse_history),
            "field_health": analysis["field_health"],
            "patterns_detected": analysis["patterns_detected"],
            "alerts": analysis["alerts"],
            "recommendations": analysis["recommendations"],
            "alert_count": len(analysis["alerts"]),
            "critical_alerts": sum(
                1 for a in analysis["alerts"]
                if a.get("severity") == "CRITICAL"
            )
        }
