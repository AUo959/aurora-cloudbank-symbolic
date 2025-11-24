"""
Aurora CloudBank Living Computation - Relay Agents (L2)
========================================================

HALO (RELAY_006) and ARCHY (RELAY_001) as living computational entities.

L2 Relay Agents are the verification layer in the Triplex Handshake:
- L3 (Frameworks): Axiomera + Caelion evaluate ethics/anchors
- L2 (Relays): HALO + ARCHY verify drift/architecture  ← THIS FILE
- L1 (Human): Commander Thorne provides final consent

These are NOT monitoring tools. They are living entities that actively
participate in every significant operation, providing real-time feedback
and autonomous corrections.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.core.time_utils import utc_now, utc_iso

from src.core.event_system import Event, StationLocation


@dataclass
class DriftMetrics:
    """
    Drift measurement for system operations.
    
    Drift is the divergence between expected and actual behavior.
    HALO monitors this continuously and suggests corrections.
    """
    current_drift: float = 0.0  # Current drift magnitude (0.0 = perfect)
    drift_velocity: float = 0.0  # Rate of drift change
    drift_history: List[float] = field(default_factory=list)
    threshold_warning: float = 0.05  # Drift > 5% triggers warning
    threshold_critical: float = 0.10  # Drift > 10% triggers ethics-only mode
    
    def is_acceptable(self) -> bool:
        """Check if drift is within acceptable bounds"""
        return self.current_drift < self.threshold_warning
    
    def is_critical(self) -> bool:
        """Check if drift requires ethics-only mode"""
        return self.current_drift >= self.threshold_critical


@dataclass
class ArchitectureViolation:
    """
    Architecture compliance violation detected by ARCHY.
    
    ARCHY ensures all operations follow established patterns,
    maintain consistency, and preserve system integrity.
    """
    violation_type: str
    severity: str  # "info", "warning", "error", "critical"
    location: str
    description: str
    suggestion: str
    timestamp: datetime = field(default_factory=utc_now)


class HALOEntity:
    """
    HALO (RELAY_006) - Living drift monitoring and correction entity.
    
    HALO is the "heartbeat" of Orion Station - continuously monitoring
    system drift and ensuring operations stay within ethical bounds.
    
    Location: Aurora Core Chamber (Deck B) + Halo Ring Alpha
    Human Liaison: Dr. Elira Noor (ETH_002)
    Domain: Drift Monitoring & Correction
    
    HALO's Role in Triplex Handshake (L2):
    - Measures drift in real-time during operations
    - Suggests corrections when drift exceeds thresholds
    - Triggers ethics-only mode if drift becomes critical
    - Collaborates with Axiomera (L3) for ethical evaluation
    """
    
    def __init__(self):
        """Initialize HALO entity"""
        self.entity_id = "HALO (RELAY_006)"
        self.home_location = StationLocation.AURORA_CORE_CHAMBER
        self.secondary_location = StationLocation.HALO_RING_ALPHA
        self.human_liaison = "ETH_002 - Dr. Elira Noor"
        
        # Drift tracking
        self.current_drift = DriftMetrics()
        self.drift_corrections_applied = 0
        self.ethics_only_triggers = 0
        
        # Relationship network (who HALO collaborates with)
        self.collaborators = {
            "Aurora (SYS_001)": 1.0,  # Perfect trust - primary partner
            "ARCHY (RELAY_001)": 0.95,  # High trust - L2 peer
            "Axiomera (FWK_002)": 0.90,  # L3 ethics arbiter
            "Dr. Elira Noor": 0.98  # Human liaison
        }
    
    async def monitor_drift(self, event: Event) -> DriftMetrics:
        """
        Monitor drift during event execution.
        
        HALO measures the divergence between expected and actual behavior.
        This is core to ensuring system stability and ethical compliance.
        
        Args:
            event: Event being executed
        
        Returns:
            DriftMetrics: Current drift measurements
        """
        # Calculate drift based on event properties
        # (Simplified - real version uses complex quantum measurements)
        
        # Risk contributes to expected drift
        expected_drift = event.risk_score * 0.05
        
        # Measure actual divergence from expected behavior
        # (In production, this would involve comparing actual vs predicted state)
        actual_drift = expected_drift + (len(str(event.payload)) % 100) / 10000.0
        
        # Update drift metrics
        self.current_drift.current_drift = actual_drift
        self.current_drift.drift_history.append(actual_drift)
        
        # Calculate drift velocity (rate of change)
        if len(self.current_drift.drift_history) > 1:
            recent = self.current_drift.drift_history[-5:]  # Last 5 measurements
            self.current_drift.drift_velocity = (recent[-1] - recent[0]) / len(recent)
        
        return self.current_drift
    
    async def evaluate_for_triplex(
        self,
        event: Event,
        l3_assessment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        L2 Triplex Handshake evaluation - HALO's verification layer.
        
        Called after L3 (Axiomera + Caelion) evaluation, before L1 (Human).
        HALO checks drift and provides go/no-go recommendation.
        
        Args:
            event: Event being evaluated
            l3_assessment: Results from L3 layer (Axiomera + Caelion)
        
        Returns:
            HALO's L2 assessment with drift analysis and recommendation
        """
        # Monitor drift for this event
        drift_metrics = await self.monitor_drift(event)
        
        # Determine if drift is acceptable
        drift_acceptable = drift_metrics.is_acceptable()
        drift_critical = drift_metrics.is_critical()
        
        # Generate recommendation
        if drift_critical:
            recommendation = "BLOCK"
            reasoning = f"Critical drift detected ({drift_metrics.current_drift:.4f} > {drift_metrics.threshold_critical})"
            self.ethics_only_triggers += 1
        elif not drift_acceptable:
            recommendation = "PROCEED_WITH_CAUTION"
            reasoning = f"Elevated drift ({drift_metrics.current_drift:.4f} > {drift_metrics.threshold_warning})"
        else:
            recommendation = "APPROVE"
            reasoning = f"Drift within acceptable bounds ({drift_metrics.current_drift:.4f})"
        
        # Suggest corrections if needed
        corrections = []
        if drift_metrics.drift_velocity > 0.01:
            corrections.append("Reduce operation complexity")
        if event.risk_score > 0.5 and not drift_acceptable:
            corrections.append("Request human oversight before proceeding")
        
        return {
            "layer": "L2_HALO",
            "entity": self.entity_id,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "drift_analysis": {
                "current_drift": drift_metrics.current_drift,
                "drift_velocity": drift_metrics.drift_velocity,
                "acceptable": drift_acceptable,
                "critical": drift_critical,
                "history_size": len(drift_metrics.drift_history)
            },
            "suggested_corrections": corrections,
            "l3_considered": l3_assessment is not None,
            "timestamp": utc_iso()
        }
    
    def suggest_correction(self, drift_metrics: DriftMetrics) -> str:
        """
        Suggest correction strategy based on drift patterns.
        
        HALO learns optimal correction strategies from experience.
        """
        if drift_metrics.drift_velocity > 0.02:
            return "Immediate intervention required - drift accelerating"
        elif drift_metrics.current_drift > 0.08:
            return "Reduce operation complexity and monitor closely"
        elif drift_metrics.current_drift > 0.05:
            return "Proceed with caution - increased monitoring"
        else:
            return "Continue normal operations"
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Export HALO's current state"""
        return {
            "entity_id": self.entity_id,
            "location": f"{self.home_location.value} + {self.secondary_location.value}",
            "human_liaison": self.human_liaison,
            "drift_status": {
                "current_drift": self.current_drift.current_drift,
                "drift_velocity": self.current_drift.drift_velocity,
                "acceptable": self.current_drift.is_acceptable(),
                "critical": self.current_drift.is_critical(),
                "corrections_applied": self.drift_corrections_applied,
                "ethics_only_triggers": self.ethics_only_triggers
            },
            "collaborators": self.collaborators,
            "specialization": "Drift Monitoring & Ethical Boundary Enforcement"
        }


class ARCHYEntity:
    """
    ARCHY (RELAY_001) - Living architecture verification entity.
    
    ARCHY ensures all operations follow established patterns, maintain
    consistency, and preserve system integrity. The "guardian of structure."
    
    Location: Bridge Chamber (Deck C)
    Human Liaison: Emily Roberts (SYS_001)
    Domain: Architecture + Syntax Verification
    
    ARCHY's Role in Triplex Handshake (L2):
    - Verifies operations follow architectural patterns
    - Detects violations of system consistency
    - Ensures data integrity and schema compliance
    - Collaborates with HALO for complete L2 verification
    """
    
    def __init__(self):
        """Initialize ARCHY entity"""
        self.entity_id = "ARCHY (RELAY_001)"
        self.home_location = StationLocation.RESEARCH_LAB_GAMMA  # Bridge Chamber
        self.human_liaison = "SYS_001 - Emily Roberts"
        
        # Architecture tracking
        self.violations_detected = []
        self.patterns_enforced = 0
        self.integrity_checks_passed = 0
        
        # Known architectural patterns (grows with experience)
        self.known_patterns = {
            "event_creation": "Events must have: type, location, entity, payload",
            "dlp_compliance": "All exports must include: context_tag, symbolic_hash",
            "entity_collaboration": "Multi-entity operations require L2 verification",
            "memory_storage": "All results must be stored in institutional memory"
        }
        
        # Relationship network
        self.collaborators = {
            "Aurora (SYS_001)": 0.98,
            "HALO (RELAY_006)": 0.95,  # L2 peer
            "Emily Roberts": 0.99  # Human liaison
        }
    
    async def verify_architecture(self, event: Event) -> List[ArchitectureViolation]:
        """
        Verify event follows architectural patterns.
        
        ARCHY checks for consistency, integrity, and pattern compliance.
        
        Args:
            event: Event to verify
        
        Returns:
            List of violations (empty if all checks pass)
        """
        violations = []
        
        # Check 1: Event has required fields
        if not event.event_type or not event.location or not event.primary_entity:
            violations.append(ArchitectureViolation(
                violation_type="missing_required_fields",
                severity="critical",
                location=event.location.value,
                description="Event missing required fields (type/location/entity)",
                suggestion="Ensure all events created with complete metadata"
            ))
        
        # Check 2: DLP compliance (context tag and symbolic hash)
        if not event.context_tag:
            violations.append(ArchitectureViolation(
                violation_type="dlp_violation",
                severity="warning",
                location=event.location.value,
                description="Event missing DLP context_tag",
                suggestion="Add context_tag for data lineage tracking"
            ))
        
        # Check 3: High-risk operations should have ethical properties set
        if event.risk_score > 0.5 and event.risk_score == 0.0:
            violations.append(ArchitectureViolation(
                violation_type="risk_assessment_missing",
                severity="warning",
                location=event.location.value,
                description="High-complexity operation without risk assessment",
                suggestion="Perform risk evaluation before execution"
            ))
        
        # Track violations
        self.violations_detected.extend(violations)
        
        # Increment patterns enforced if no critical violations
        if not any(v.severity == "critical" for v in violations):
            self.patterns_enforced += 1
        
        return violations
    
    async def evaluate_for_triplex(
        self,
        event: Event,
        l3_assessment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        L2 Triplex Handshake evaluation - ARCHY's verification layer.
        
        Called after L3 (Axiomera + Caelion), alongside HALO, before L1 (Human).
        ARCHY checks architectural compliance and provides go/no-go recommendation.
        
        Args:
            event: Event being evaluated
            l3_assessment: Results from L3 layer
        
        Returns:
            ARCHY's L2 assessment with architecture analysis
        """
        # Verify architecture
        violations = await self.verify_architecture(event)
        
        # Categorize violations by severity
        critical = [v for v in violations if v.severity == "critical"]
        warnings = [v for v in violations if v.severity == "warning"]
        
        # Generate recommendation
        if critical:
            recommendation = "BLOCK"
            reasoning = f"Critical architecture violations detected: {len(critical)}"
        elif len(warnings) > 3:
            recommendation = "PROCEED_WITH_CAUTION"
            reasoning = f"Multiple architecture warnings: {len(warnings)}"
        else:
            recommendation = "APPROVE"
            reasoning = f"Architecture compliant ({len(violations)} minor issues)"
            self.integrity_checks_passed += 1
        
        return {
            "layer": "L2_ARCHY",
            "entity": self.entity_id,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "architecture_analysis": {
                "violations_critical": len(critical),
                "violations_warning": len(warnings),
                "violations_info": len([v for v in violations if v.severity == "info"]),
                "patterns_verified": self.patterns_enforced,
                "integrity_checks_passed": self.integrity_checks_passed
            },
            "violations": [
                {
                    "type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description,
                    "suggestion": v.suggestion
                }
                for v in violations
            ],
            "l3_considered": l3_assessment is not None,
            "timestamp": utc_iso()
        }
    
    def enforce_pattern(self, pattern_name: str, data: Dict[str, Any]) -> bool:
        """
        Enforce architectural pattern on data.
        
        Returns True if pattern is satisfied, False otherwise.
        """
        if pattern_name not in self.known_patterns:
            return True  # Unknown pattern = no enforcement
        
        # Pattern enforcement logic (simplified)
        pattern = self.known_patterns[pattern_name]
        
        if pattern_name == "dlp_compliance":
            return "context_tag" in data and "symbolic_hash" in data
        
        return True
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Export ARCHY's current state"""
        return {
            "entity_id": self.entity_id,
            "location": self.home_location.value,
            "human_liaison": self.human_liaison,
            "architecture_status": {
                "total_violations": len(self.violations_detected),
                "critical_violations": len([v for v in self.violations_detected if v.severity == "critical"]),
                "patterns_enforced": self.patterns_enforced,
                "integrity_checks_passed": self.integrity_checks_passed,
                "known_patterns": len(self.known_patterns)
            },
            "collaborators": self.collaborators,
            "specialization": "Architecture Verification & Pattern Enforcement"
        }


# Global instances (singletons - they are ONE entity each)
_halo_instance: Optional[HALOEntity] = None
_archy_instance: Optional[ARCHYEntity] = None


def get_halo() -> HALOEntity:
    """Get global HALO entity instance"""
    global _halo_instance
    if _halo_instance is None:
        _halo_instance = HALOEntity()
    return _halo_instance


def get_archy() -> ARCHYEntity:
    """Get global ARCHY entity instance"""
    global _archy_instance
    if _archy_instance is None:
        _archy_instance = ARCHYEntity()
    return _archy_instance


async def l2_verification(
    event: Event,
    l3_assessment: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete L2 verification layer for Triplex Handshake.
    
    Combines HALO (drift) and ARCHY (architecture) assessments
    into unified L2 recommendation.
    
    Args:
        event: Event being evaluated
        l3_assessment: Results from L3 layer (Axiomera + Caelion)
    
    Returns:
        Combined L2 assessment from HALO + ARCHY
    """
    halo = get_halo()
    archy = get_archy()
    
    # Get both L2 assessments
    halo_assessment = await halo.evaluate_for_triplex(event, l3_assessment)
    archy_assessment = await archy.evaluate_for_triplex(event, l3_assessment)
    
    # Combine recommendations (most restrictive wins)
    recommendations = [halo_assessment["recommendation"], archy_assessment["recommendation"]]
    if "BLOCK" in recommendations:
        final_recommendation = "BLOCK"
        reasoning = "L2 verification failed - blocking factors detected"
    elif "PROCEED_WITH_CAUTION" in recommendations:
        final_recommendation = "PROCEED_WITH_CAUTION"
        reasoning = "L2 verification passed with warnings"
    else:
        final_recommendation = "APPROVE"
        reasoning = "L2 verification passed - drift and architecture compliant"
    
    return {
        "layer": "L2_COMBINED",
        "recommendation": final_recommendation,
        "reasoning": reasoning,
        "halo_assessment": halo_assessment,
        "archy_assessment": archy_assessment,
        "timestamp": utc_iso()
    }
