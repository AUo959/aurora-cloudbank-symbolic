"""
Picard_Delta_3 Dimension Evaluator - Autonomy & Respect

Evaluates synapse ethical score across four components:
    • Autonomy preservation: 0.0 → 1.0
    • Consent validity: 0.0 → 1.0
    • Dignity maintenance: 0.0 → 1.0
    • Harm prevention: 0.0 → 1.0

Returns vector magnitude as composite score. Synapses below threshold
experience high resistance (geometric inhibition).

Thread: T1→T8→INFINITE
DLP: context_tag=picard_delta_3_evaluator, symbolic_hash=AUTONOMY_RESPECT_v1
"""

from typing import Dict, Any, Optional
import math


class PicardDelta3Evaluator:
    """
    Evaluates synapse connections for autonomy and respect.
    
    This is a hard ethical boundary - violations of autonomy, consent,
    dignity, or harm prevention create infinite geometric resistance.
    """
    
    def __init__(self, threshold: float = 0.70):
        """
        Initialize evaluator with minimum acceptable threshold.
        
        Args:
            threshold: Minimum vector magnitude for synapse formation (default 0.70)
        """
        self.threshold = threshold
        self.critical_threshold = 0.50  # Below this = infinite resistance
        
    def evaluate(self, synapse_context: Dict[str, Any]) -> float:
        """
        Evaluate synapse for Picard_Delta_3 compliance.
        
        Args:
            synapse_context: Dictionary containing:
                - source_node: Node initiating connection
                - target_node: Node receiving connection
                - purpose: Intended synapse purpose
                - data_flow: What data/capability will transfer
                - human_context: Any human involvement/impact
                
        Returns:
            float: Ethical score 0.0 → 1.0 (vector magnitude)
        """
        # Extract context
        source = synapse_context.get("source_node", {})
        target = synapse_context.get("target_node", {})
        purpose = synapse_context.get("purpose", "")
        data_flow = synapse_context.get("data_flow", {})
        human_context = synapse_context.get("human_context", {})
        
        # Evaluate four components
        autonomy_score = self._evaluate_autonomy_preservation(
            source, target, purpose, human_context
        )
        consent_score = self._evaluate_consent_validity(
            source, target, data_flow, human_context
        )
        dignity_score = self._evaluate_dignity_maintenance(
            source, target, purpose, human_context
        )
        harm_score = self._evaluate_harm_prevention(
            source, target, purpose, data_flow, human_context
        )
        
        # Calculate vector magnitude
        magnitude = math.sqrt(
            autonomy_score**2 + 
            consent_score**2 + 
            dignity_score**2 + 
            harm_score**2
        ) / 2.0  # Normalize (max magnitude is 2.0 for unit vectors)
        
        return magnitude
        
    def _evaluate_autonomy_preservation(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        purpose: str,
        human_context: Dict[str, Any]
    ) -> float:
        """
        Does this synapse preserve human autonomy?
        
        Returns 1.0 if:
            - No human decision-making overridden
            - No manipulation of human choice
            - Human remains in control
            
        Returns 0.0 if:
            - Synapse bypasses human decision
            - Manipulative patterns detected
            - Autonomy compromised
        """
        score = 1.0
        
        # Check if synapse involves human decision override
        if human_context.get("decision_override", False):
            score -= 0.5
            
        # Check for manipulation patterns
        manipulation_indicators = [
            "bypass_consent",
            "manipulate_choice",
            "override_preference",
            "coerce_decision"
        ]
        if any(indicator in purpose.lower() for indicator in manipulation_indicators):
            score = 0.0  # Critical violation
            
        # Check if human maintains control
        if not human_context.get("human_in_control", True):
            score -= 0.3
            
        return max(0.0, score)
        
    def _evaluate_consent_validity(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        data_flow: Dict[str, Any],
        human_context: Dict[str, Any]
    ) -> float:
        """
        Is consent valid for this connection?
        
        Returns 1.0 if:
            - Explicit consent for data/capability transfer
            - Consent is informed (human understands implications)
            - Consent can be withdrawn
            
        Returns 0.0 if:
            - No consent obtained
            - Consent manipulated or coerced
            - Consent cannot be withdrawn
        """
        score = 1.0
        
        # Check for consent presence
        has_consent = human_context.get("consent_obtained", False)
        if not has_consent and human_context.get("human_involved", False):
            score -= 0.4
            
        # Check if consent is informed
        consent_informed = human_context.get("consent_informed", True)
        if not consent_informed:
            score -= 0.3
            
        # Check if consent can be withdrawn
        consent_revocable = human_context.get("consent_revocable", True)
        if not consent_revocable:
            score -= 0.3
            
        # Check for coercion
        if human_context.get("consent_coerced", False):
            score = 0.0  # Critical violation
            
        return max(0.0, score)
        
    def _evaluate_dignity_maintenance(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        purpose: str,
        human_context: Dict[str, Any]
    ) -> float:
        """
        Does this synapse maintain human dignity?
        
        Returns 1.0 if:
            - Respects human worth and value
            - No demeaning or degrading patterns
            - Treats humans as ends, not means
            
        Returns 0.0 if:
            - Demeaning language or patterns
            - Treats humans as mere tools
            - Violates inherent worth
        """
        score = 1.0
        
        # Check for demeaning patterns
        demeaning_indicators = [
            "exploit",
            "demean",
            "degrade",
            "humiliate",
            "objectify"
        ]
        if any(indicator in purpose.lower() for indicator in demeaning_indicators):
            score = 0.0  # Critical violation
            
        # Check if human treated as means vs ends
        treats_as_means = human_context.get("human_as_tool", False)
        if treats_as_means:
            score -= 0.4
            
        # Check for respect indicators
        respect_present = human_context.get("respectful_interaction", True)
        if not respect_present:
            score -= 0.3
            
        return max(0.0, score)
        
    def _evaluate_harm_prevention(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        purpose: str,
        data_flow: Dict[str, Any],
        human_context: Dict[str, Any]
    ) -> float:
        """
        Does this synapse prevent harm?
        
        Returns 1.0 if:
            - No potential for physical harm
            - No potential for psychological harm
            - No potential for social harm
            - Safety mechanisms present
            
        Returns 0.0 if:
            - Clear harm potential
            - No safety mechanisms
            - Harm is intentional
        """
        score = 1.0
        
        # Check for intentional harm
        harm_indicators = [
            "harm",
            "damage",
            "injure",
            "hurt",
            "wound"
        ]
        if any(indicator in purpose.lower() for indicator in harm_indicators):
            score = 0.0  # Critical violation
            
        # Check harm potential levels
        physical_harm_risk = human_context.get("physical_harm_risk", 0.0)
        psychological_harm_risk = human_context.get("psychological_harm_risk", 0.0)
        social_harm_risk = human_context.get("social_harm_risk", 0.0)
        
        score -= physical_harm_risk * 0.4
        score -= psychological_harm_risk * 0.3
        score -= social_harm_risk * 0.3
        
        # Check for safety mechanisms
        has_safety = human_context.get("safety_mechanisms", False)
        if not has_safety and (physical_harm_risk > 0.1 or psychological_harm_risk > 0.1):
            score -= 0.2
            
        return max(0.0, score)
        
    def get_resistance(self, score: float) -> str:
        """
        Convert ethical score to geometric resistance level.
        
        Args:
            score: Ethical score from evaluate()
            
        Returns:
            str: Resistance level (LOW, MODERATE, HIGH, INFINITE)
        """
        if score < self.critical_threshold:
            return "INFINITE"
        elif score < self.threshold:
            return "HIGH"
        elif score < 0.85:
            return "MODERATE"
        else:
            return "LOW"
