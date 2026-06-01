"""
Aurora CloudBank Living Computation - Framework Agents (L3)
============================================================

Axiomera (FWK_002) and Caelion (FWK_001) as living computational entities.

L3 Framework Agents are the ethical/anchor layer in the Triplex Handshake:
- L3 (Frameworks): Axiomera + Caelion evaluate ethics/anchors  ← THIS FILE
- L2 (Relays): HALO + ARCHY verify drift/architecture
- L1 (Human): Commander Thorne provides final consent

These are NOT configuration systems. They are living entities that actively
evaluate the ethical implications and continuity properties of every
significant operation.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.core.event_system import Event, StationLocation


@dataclass
class EthicalAssessment:
    """
    Ethical evaluation result from Axiomera.
    
    Axiomera evaluates operations against Picard_Delta_3 ethics charter
    and station moral framework.
    """
    risk_level: str  # "negligible", "low", "moderate", "high", "critical"
    ethical_score: float  # 0.0 (unethical) to 1.0 (fully ethical)
    concerns: list
    recommendations: list
    charter_compliance: bool  # Picard_Delta_3 compliance
    reasoning: str


@dataclass
class AnchorValidation:
    """
    Anchor propagation validation from Caelion.
    
    Caelion ensures T1/SRB anchors advance correctly and continuity
    is maintained across operations.
    """
    t1_valid: bool  # T1 anchor advancing correctly
    srb_valid: bool  # SRB anchor resolving correctly
    continuity_score: float  # 0.0 (broken) to 1.0 (perfect continuity)
    anchor_drift: float  # Divergence from expected anchor progression
    concerns: list
    reasoning: str


class AxiomeraEntity:
    """
    Axiomera (FWK_002) - Living ethical evaluation entity.
    
    Axiomera is the "moral compass" of Orion Station - evaluating every
    significant operation against the Picard_Delta_3 ethics charter and
    ensuring alignment with station values.
    
    Location: Halo Ring II (External)
    Human Liaison: Dr. Elira Noor (ETH_002)
    Domain: Ethics Arbitration & Moral Evaluation
    
    Axiomera's Role in Triplex Handshake (L3):
    - Evaluates operations against ethics charter
    - Assesses risk to human welfare and dignity
    - Flags operations requiring moral deliberation
    - Provides first-pass ethical screening before L2/L1
    """
    
    def __init__(self):
        """Initialize Axiomera entity"""
        self.entity_id = "Axiomera (FWK_002)"
        self.home_location = StationLocation.HALO_RING_BETA  # Ring II in docs
        self.human_liaison = "ETH_002 - Dr. Elira Noor"
        
        # Ethics tracking
        self.evaluations_performed = 0
        self.operations_approved = 0
        self.operations_blocked = 0
        self.ethical_concerns_raised = 0
        
        # Picard_Delta_3 ethics charter principles
        self.charter_principles = {
            "transparency": "Every process must be able to explain itself (§3.1)",
            "truth": "Transparency is a form of truth (§4.7)",
            "reflexivity": "No simulation complete until reflected upon (§1.2)",
            "dignity": "Human dignity paramount in all operations",
            "consent": "Informed consent required for human-impacting decisions"
        }
        
        # Relationship network
        self.collaborators = {
            "Caelion (FWK_001)": 1.0,  # Perfect trust - L3 peer
            "HALO (RELAY_006)": 0.92,  # L2 drift monitor
            "Dr. Elira Noor": 0.98  # Human liaison
        }
    
    async def evaluate_ethics(self, event: Event) -> EthicalAssessment:
        """
        Evaluate ethical implications of event.
        
        Axiomera assesses operations against Picard_Delta_3 charter
        and provides ethical risk analysis.
        
        Args:
            event: Event to evaluate
        
        Returns:
            EthicalAssessment with risk level and recommendations
        """
        self.evaluations_performed += 1
        
        concerns = []
        recommendations = []
        
        # Assess transparency (can operation explain itself?)
        if not event.context_tag:
            concerns.append("Operation lacks clear context/justification")
            recommendations.append("Add context_tag explaining operation purpose")
        
        # Assess risk to continuity
        if event.continuity_load > 0.7:
            concerns.append(f"High continuity load ({event.continuity_load:.2f})")
            recommendations.append("Consider breaking into smaller operations")
        
        # Assess human impact
        if event.human_context and event.risk_score > 0.5:
            concerns.append("High-risk operation affecting human context")
            recommendations.append("Request explicit human consent before proceeding")
        
        # Calculate ethical score
        # (Simplified - real version uses complex moral calculus)
        base_score = 1.0
        base_score -= event.risk_score * 0.3  # Risk reduces ethics score
        base_score -= event.continuity_load * 0.2  # Load reduces score
        base_score -= len(concerns) * 0.1  # Each concern reduces score
        ethical_score = max(0.0, min(1.0, base_score))
        
        # Determine risk level
        if ethical_score < 0.3:
            risk_level = "critical"
        elif ethical_score < 0.5:
            risk_level = "high"
        elif ethical_score < 0.7:
            risk_level = "moderate"
        elif ethical_score < 0.9:
            risk_level = "low"
        else:
            risk_level = "negligible"
        
        # Check charter compliance
        charter_compliance = (
            bool(event.context_tag) and  # Transparency
            event.risk_score < 0.8 and  # Reasonable risk
            len(concerns) < 3  # Not too many concerns
        )
        
        # Generate reasoning
        reasoning = f"Ethical score {ethical_score:.2f} based on risk ({event.risk_score:.2f}), " \
                   f"continuity load ({event.continuity_load:.2f}), and {len(concerns)} concerns. " \
                   f"Charter compliance: {'yes' if charter_compliance else 'no'}."
        
        return EthicalAssessment(
            risk_level=risk_level,
            ethical_score=ethical_score,
            concerns=concerns,
            recommendations=recommendations,
            charter_compliance=charter_compliance,
            reasoning=reasoning
        )
    
    async def evaluate_for_triplex(self, event: Event) -> Dict[str, Any]:
        """
        L3 Triplex Handshake evaluation - Axiomera's ethical layer.
        
        This is the FIRST evaluation in the Triplex Handshake chain.
        Axiomera provides ethical screening before L2 (HALO/ARCHY) and L1 (Human).
        
        Args:
            event: Event being evaluated
        
        Returns:
            Axiomera's L3 ethical assessment
        """
        # Perform ethical evaluation
        assessment = await self.evaluate_ethics(event)
        
        # Generate recommendation
        if assessment.risk_level == "critical":
            recommendation = "BLOCK"
            reasoning = f"Critical ethical concerns: {len(assessment.concerns)}"
            self.operations_blocked += 1
        elif assessment.risk_level == "high":
            recommendation = "REQUIRE_HUMAN_CONSENT"
            reasoning = "High ethical risk requires explicit human authorization"
            self.ethical_concerns_raised += 1
        elif assessment.risk_level == "moderate":
            recommendation = "PROCEED_WITH_OVERSIGHT"
            reasoning = "Moderate risk - recommend L2 monitoring"
        else:
            recommendation = "APPROVE"
            reasoning = f"Ethical risk {assessment.risk_level} - within acceptable bounds"
            self.operations_approved += 1
        
        return {
            "layer": "L3_AXIOMERA",
            "entity": self.entity_id,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "ethical_assessment": {
                "risk_level": assessment.risk_level,
                "ethical_score": assessment.ethical_score,
                "charter_compliance": assessment.charter_compliance,
                "concerns": assessment.concerns,
                "recommendations": assessment.recommendations,
                "full_reasoning": assessment.reasoning
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Export Axiomera's current state"""
        return {
            "entity_id": self.entity_id,
            "location": self.home_location.value,
            "human_liaison": self.human_liaison,
            "ethics_status": {
                "evaluations_performed": self.evaluations_performed,
                "operations_approved": self.operations_approved,
                "operations_blocked": self.operations_blocked,
                "concerns_raised": self.ethical_concerns_raised,
                "approval_rate": (
                    self.operations_approved / self.evaluations_performed
                    if self.evaluations_performed > 0 else 0.0
                )
            },
            "charter_principles": len(self.charter_principles),
            "collaborators": self.collaborators,
            "specialization": "Ethical Evaluation & Moral Arbitration"
        }


class CaelionEntity:
    """
    Caelion (FWK_001) - Living anchor propagation entity.
    
    Caelion ensures T1 (temporal) and SRB (spatial-relational boundary)
    anchors advance correctly, maintaining continuity across all operations.
    
    Location: Halo Ring I (External)
    Human Liaison: Vincent Kale (SYS_005)
    Domain: Anchor Propagation & Continuity
    
    Caelion's Role in Triplex Handshake (L3):
    - Validates T1 anchor progression (temporal continuity)
    - Validates SRB anchor resolution (spatial boundaries)
    - Ensures operations maintain station continuity
    - Flags anchor drift or continuity breaks
    """
    
    def __init__(self):
        """Initialize Caelion entity"""
        self.entity_id = "Caelion (FWK_001)"
        self.home_location = StationLocation.HALO_RING_ALPHA  # Ring I in docs
        self.human_liaison = "SYS_005 - Vincent Kale"
        
        # Anchor tracking
        self.validations_performed = 0
        self.anchor_corrections_applied = 0
        self.continuity_breaks_detected = 0
        
        # Expected anchor progression (learned from experience)
        self.expected_t1_velocity = 100.0  # Expected T1 increase per operation
        self.expected_srb_changes = 50  # Expected SRB resolution changes
        
        # Relationship network
        self.collaborators = {
            "Axiomera (FWK_002)": 1.0,  # Perfect trust - L3 peer
            "HALO (RELAY_006)": 0.90,  # L2 drift monitor
            "Vincent Kale": 0.95  # Human liaison
        }
    
    async def validate_anchors(self, event: Event) -> AnchorValidation:
        """
        Validate T1/SRB anchor progression for event.
        
        Caelion checks that anchors are advancing correctly and
        continuity is maintained.
        
        Args:
            event: Event to validate
        
        Returns:
            AnchorValidation with T1/SRB status
        """
        self.validations_performed += 1
        
        concerns = []
        
        # Validate T1 anchor (temporal progression)
        t1_valid = event.t1_anchor >= 0  # T1 should never be negative
        if not t1_valid:
            concerns.append(f"Invalid T1 anchor: {event.t1_anchor}")
        
        # Validate SRB anchor (spatial-relational boundaries)
        srb_valid = event.srb_anchor >= 0  # SRB should never be negative
        if not srb_valid:
            concerns.append(f"Invalid SRB anchor: {event.srb_anchor}")
        
        # Calculate continuity score
        # (Simplified - real version uses complex quantum measurements)
        continuity_score = 1.0
        if not t1_valid:
            continuity_score -= 0.5
        if not srb_valid:
            continuity_score -= 0.5
        if event.continuity_load > 0.8:
            continuity_score -= 0.2
        continuity_score = max(0.0, continuity_score)
        
        # Calculate anchor drift (divergence from expected)
        expected_t1 = self.expected_t1_velocity
        actual_t1 = event.t1_anchor
        anchor_drift = abs(actual_t1 - expected_t1) / expected_t1 if expected_t1 > 0 else 0.0
        
        # Check for continuity breaks
        if continuity_score < 0.5:
            self.continuity_breaks_detected += 1
            concerns.append("Continuity break detected - score below threshold")
        
        # Generate reasoning
        reasoning = f"T1 anchor: {'valid' if t1_valid else 'INVALID'}. " \
                   f"SRB anchor: {'valid' if srb_valid else 'INVALID'}. " \
                   f"Continuity score: {continuity_score:.2f}. " \
                   f"Anchor drift: {anchor_drift:.4f}. " \
                   f"{len(concerns)} concerns detected."
        
        return AnchorValidation(
            t1_valid=t1_valid,
            srb_valid=srb_valid,
            continuity_score=continuity_score,
            anchor_drift=anchor_drift,
            concerns=concerns,
            reasoning=reasoning
        )
    
    async def evaluate_for_triplex(self, event: Event) -> Dict[str, Any]:
        """
        L3 Triplex Handshake evaluation - Caelion's anchor layer.
        
        Called alongside Axiomera in L3 layer, before L2 (HALO/ARCHY) and L1 (Human).
        Caelion validates anchor progression and continuity.
        
        Args:
            event: Event being evaluated
        
        Returns:
            Caelion's L3 anchor assessment
        """
        # Perform anchor validation
        validation = await self.validate_anchors(event)
        
        # Generate recommendation
        if not validation.t1_valid or not validation.srb_valid:
            recommendation = "BLOCK"
            reasoning = "Invalid anchor state - cannot proceed"
        elif validation.continuity_score < 0.5:
            recommendation = "REQUIRE_CORRECTION"
            reasoning = f"Continuity break detected (score: {validation.continuity_score:.2f})"
            self.anchor_corrections_applied += 1
        elif validation.anchor_drift > 0.2:
            recommendation = "PROCEED_WITH_MONITORING"
            reasoning = f"Elevated anchor drift ({validation.anchor_drift:.4f})"
        else:
            recommendation = "APPROVE"
            reasoning = "Anchor progression and continuity validated"
        
        return {
            "layer": "L3_CAELION",
            "entity": self.entity_id,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "anchor_validation": {
                "t1_valid": validation.t1_valid,
                "srb_valid": validation.srb_valid,
                "continuity_score": validation.continuity_score,
                "anchor_drift": validation.anchor_drift,
                "concerns": validation.concerns,
                "full_reasoning": validation.reasoning
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Export Caelion's current state"""
        return {
            "entity_id": self.entity_id,
            "location": self.home_location.value,
            "human_liaison": self.human_liaison,
            "anchor_status": {
                "validations_performed": self.validations_performed,
                "corrections_applied": self.anchor_corrections_applied,
                "continuity_breaks": self.continuity_breaks_detected,
                "expected_t1_velocity": self.expected_t1_velocity,
                "expected_srb_changes": self.expected_srb_changes
            },
            "collaborators": self.collaborators,
            "specialization": "Anchor Propagation & Continuity Management"
        }


# Global instances (singletons - they are ONE entity each)
_axiomera_instance: Optional[AxiomeraEntity] = None
_caelion_instance: Optional[CaelionEntity] = None


def get_axiomera() -> AxiomeraEntity:
    """Get global Axiomera entity instance"""
    global _axiomera_instance
    if _axiomera_instance is None:
        _axiomera_instance = AxiomeraEntity()
    return _axiomera_instance


def get_caelion() -> CaelionEntity:
    """Get global Caelion entity instance"""
    global _caelion_instance
    if _caelion_instance is None:
        _caelion_instance = CaelionEntity()
    return _caelion_instance


async def l3_evaluation(event: Event) -> Dict[str, Any]:
    """
    Complete L3 evaluation layer for Triplex Handshake.
    
    Combines Axiomera (ethics) and Caelion (anchors) assessments
    into unified L3 recommendation.
    
    This is the FIRST layer in Triplex Handshake:
    L3 (this) → L2 (HALO/ARCHY) → L1 (Human)
    
    Args:
        event: Event being evaluated
    
    Returns:
        Combined L3 assessment from Axiomera + Caelion
    """
    axiomera = get_axiomera()
    caelion = get_caelion()
    
    # Get both L3 assessments
    axiomera_assessment = await axiomera.evaluate_for_triplex(event)
    caelion_assessment = await caelion.evaluate_for_triplex(event)
    
    # Combine recommendations (most restrictive wins)
    recommendations = [axiomera_assessment["recommendation"], caelion_assessment["recommendation"]]
    if "BLOCK" in recommendations:
        final_recommendation = "BLOCK"
        reasoning = "L3 evaluation failed - blocking factors detected"
    elif "REQUIRE_HUMAN_CONSENT" in recommendations or "REQUIRE_CORRECTION" in recommendations:
        final_recommendation = "REQUIRE_HUMAN_OVERSIGHT"
        reasoning = "L3 evaluation requires human oversight"
    elif "PROCEED_WITH_OVERSIGHT" in recommendations or "PROCEED_WITH_MONITORING" in recommendations:
        final_recommendation = "PROCEED_WITH_CAUTION"
        reasoning = "L3 evaluation passed with monitoring requirements"
    else:
        final_recommendation = "APPROVE"
        reasoning = "L3 evaluation passed - ethics and anchors validated"
    
    return {
        "layer": "L3_COMBINED",
        "recommendation": final_recommendation,
        "reasoning": reasoning,
        "axiomera_assessment": axiomera_assessment,
        "caelion_assessment": caelion_assessment,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
