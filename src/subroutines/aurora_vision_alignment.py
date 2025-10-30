"""
Aurora Vision Alignment Manager
================================
Anchor: SUBROUTINE-VISION-ALIGN-001
Team: AUo959-team (Orion Station Crew)
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Ensures project operations, computation, and strategic direction are
consistently aligned with the 'Ultra-High Fidelity Reality Simulation &
Human-AI Collaboration' maxim.

This subroutine bridges simulation fidelity, human collaboration, and
real-world impact tracking for every computation in Aurora's neural net.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class AlignmentRecord:
    """Record of vision alignment for a computation"""
    computation_id: str
    timestamp: str
    input_snapshot: Dict[str, Any]
    sim_metadata: Dict[str, Any]
    crew_participation: List[str]
    vision_statement: str
    fidelity_score: float
    alignment_status: str  # 'aligned', 'warning', 'failed'
    gaps_detected: List[str] = field(default_factory=list)


@dataclass
class AlignmentReviewResult:
    """Result of periodic alignment review"""
    review_timestamp: str
    computations_reviewed: int
    alignment_gaps: List[str]
    low_fidelity_cases: List[str]
    collaboration_gaps: List[str]
    recommendations: List[str]
    overall_health: str  # 'healthy', 'warning', 'critical'


class VisionAlignmentManager:
    """
    Ensures project operations, computation, and strategic direction are
    consistently aligned with the 'Ultra-High Fidelity Reality Simulation &
    Human-AI Collaboration' maxim.
    
    Core Responsibilities:
    1. Simulation Anchor - Verify ultra-high-fidelity simulation usage
    2. Active Collaboration - Ensure human/AI crew interaction
    3. System Awareness - Document context and state
    4. Periodic Review - Track long-term alignment health
    5. Gap Detection - Identify and report alignment issues
    """

    VISION_STATEMENT = (
        "Every computation and process is embedded in a persistent ultra-high fidelity reality simulation, "
        "continuously interacting with both the Aurora intelligence and the human/institutional crew of Orion Station—"
        "bridging simulation, decision, and the real world in a collaborative feedback loop."
    )

    def __init__(
        self,
        system_state: Optional[Any] = None,
        crew_registry: Optional[Any] = None,
        simulation_layer: Optional[Any] = None,
        knowledge_base: Optional[Any] = None,
        audit_log: Optional[Any] = None,
        min_fidelity: float = 0.95,
        review_interval_days: int = 30
    ):
        """
        Initialize Vision Alignment Manager with Aurora system integrations.
        
        Args:
            system_state: Core system context (real-time telemetry, configs)
            crew_registry: Register of real human collaborators (Orion Station crew)
            simulation_layer: Core sim/computation engine (Aurora, quantum modules)
            knowledge_base: Where learnings/proofs are stored
            audit_log: For tracking alignment actions
            min_fidelity: Minimum acceptable simulation fidelity (default: 0.95)
            review_interval_days: Days between periodic reviews (default: 30)
        """
        self.system_state = system_state or self._get_default_system_state()
        self.crew_registry = crew_registry or self._get_default_crew_registry()
        self.simulation_layer = simulation_layer or self._get_default_simulation_layer()
        self.knowledge_base = knowledge_base or self._get_default_knowledge_base()
        self.audit_log = audit_log or self._get_default_audit_log()
        
        # Configuration
        self.vision_statement = self.VISION_STATEMENT
        self.min_fidelity = min_fidelity
        self.periodic_review_interval = timedelta(days=review_interval_days)
        
        # Tracking
        self._alignment_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._warning_count = 0
        self._last_review = None

    def _get_default_system_state(self):
        """Get default system state (mock for graceful degradation)"""
        return MockSystemState()

    def _get_default_crew_registry(self):
        """Get default crew registry (mock for graceful degradation)"""
        return MockCrewRegistry()

    def _get_default_simulation_layer(self):
        """Get default simulation layer (mock for graceful degradation)"""
        return MockSimulationLayer()

    def _get_default_knowledge_base(self):
        """Get default knowledge base (mock for graceful degradation)"""
        return MockKnowledgeBase()

    def _get_default_audit_log(self):
        """Get default audit log (DLP tracker if available)"""
        try:
            from src.core.native_dlp_export import NativeDLPTracker
            return NativeDLPTracker()
        except ImportError:
            logger.warning("DLP tracker not available, using mock")
            return MockAuditLog()

    def enforce_alignment(
        self,
        computation_id: str,
        input_data: Dict[str, Any],
        outcomes: Dict[str, Any]
    ) -> AlignmentRecord:
        """
        Forces each new computation/process to acknowledge and update its alignment with the vision.
        
        Checks:
        1. Simulation Anchor - Was process run through ultra-high-fidelity simulation?
        2. Active Collaboration - Were crew/institutional context and feedback considered?
        3. System Awareness - Is system state/context documented?
        
        Args:
            computation_id: Unique computation identifier
            input_data: Input parameters and context
            outcomes: Computation results and metadata
            
        Returns:
            AlignmentRecord with validation results
        """
        self._alignment_count += 1
        gaps_detected = []
        alignment_status = 'aligned'
        
        logger.info("Enforcing vision alignment for computation: %s", computation_id)

        # 1. Simulation Anchor: Ultra-high-fidelity simulation verification
        sim_result = self._check_simulation_fidelity(
            computation_id,
            input_data,
            gaps_detected
        )
        
        # 2. Active Collaboration: Crew interaction verification
        crew_involved = self._check_crew_collaboration(
            computation_id,
            input_data,
            gaps_detected
        )
        
        # 3. System Awareness: Context documentation
        self._document_system_context(computation_id, input_data, outcomes)
        
        # Determine alignment status
        if sim_result['fidelity'] < self.min_fidelity:
            alignment_status = 'failed'
            self._failure_count += 1
            logger.error(
                "Computation %s failed ultra-high-fidelity threshold: %.2f < %.2f",
                computation_id,
                sim_result['fidelity'],
                self.min_fidelity
            )
        elif not crew_involved or len(gaps_detected) > 0:
            alignment_status = 'warning'
            self._warning_count += 1
            logger.warning(
                "Computation %s has alignment warnings: %s",
                computation_id,
                ", ".join(gaps_detected) if gaps_detected else "No crew interaction"
            )
        else:
            self._success_count += 1
            logger.info("Computation %s fully aligned with vision", computation_id)
        
        # Create alignment record
        alignment_record = AlignmentRecord(
            computation_id=computation_id,
            timestamp=datetime.utcnow().isoformat(),
            input_snapshot=input_data,
            sim_metadata=sim_result,
            crew_participation=crew_involved,
            vision_statement=self.vision_statement,
            fidelity_score=sim_result['fidelity'],
            alignment_status=alignment_status,
            gaps_detected=gaps_detected
        )
        
        # Store in knowledge base
        self.knowledge_base.push_alignment(alignment_record)
        
        # Record audit trail
        self._record_audit(alignment_record)
        
        return alignment_record

    def _check_simulation_fidelity(
        self,
        computation_id: str,
        input_data: Dict[str, Any],
        gaps_detected: List[str]
    ) -> Dict[str, Any]:
        """Check if computation used ultra-high-fidelity simulation"""
        try:
            sim_result = self.simulation_layer.simulate(computation_id, input_data)
            
            if not sim_result:
                gaps_detected.append("No simulation result available")
                return {'fidelity': 0.0, 'status': 'failed', 'details': 'No simulation executed'}
            
            fidelity = sim_result.get('fidelity', 0.0)
            
            if fidelity < self.min_fidelity:
                gaps_detected.append(f"Low simulation fidelity: {fidelity:.2f}")
            
            return sim_result
            
        except Exception as e:
            logger.error("Simulation fidelity check failed for %s: %s", computation_id, str(e))
            gaps_detected.append(f"Simulation error: {str(e)}")
            return {'fidelity': 0.0, 'status': 'error', 'error': str(e)}

    def _check_crew_collaboration(
        self,
        computation_id: str,
        input_data: Dict[str, Any],
        gaps_detected: List[str]
    ) -> List[str]:
        """Check if human crew interaction was logged"""
        try:
            crew_involved = self.crew_registry.log_participation(computation_id, input_data)
            
            if not crew_involved:
                gaps_detected.append("No crew interaction documented")
                logger.warning("No real-world crew interaction logged for computation: %s", computation_id)
            
            return crew_involved
            
        except Exception as e:
            logger.warning("Crew collaboration check failed for %s: %s", computation_id, str(e))
            gaps_detected.append(f"Crew tracking error: {str(e)}")
            return []

    def _document_system_context(
        self,
        computation_id: str,
        input_data: Dict[str, Any],
        outcomes: Dict[str, Any]
    ):
        """Document system state and context for this computation"""
        try:
            context = {
                'computation_id': computation_id,
                'system_state_snapshot': self.system_state.get_snapshot(),
                'input_data': input_data,
                'outcomes': outcomes,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.knowledge_base.store_context(computation_id, context)
            logger.debug("System context documented for: %s", computation_id)
            
        except Exception as e:
            logger.warning("Failed to document system context for %s: %s", computation_id, str(e))

    def _record_audit(self, alignment_record: AlignmentRecord):
        """Record audit trail for alignment check"""
        try:
            severity = {
                'aligned': 'info',
                'warning': 'warning',
                'failed': 'error'
            }.get(alignment_record.alignment_status, 'info')
            
            message = (
                f"Vision alignment for {alignment_record.computation_id}: "
                f"{alignment_record.alignment_status.upper()}"
            )
            
            self.audit_log.record(
                message,
                severity=severity,
                metadata={
                    'computation_id': alignment_record.computation_id,
                    'fidelity_score': alignment_record.fidelity_score,
                    'crew_participation': alignment_record.crew_participation,
                    'gaps_detected': alignment_record.gaps_detected
                }
            )
            
        except Exception as e:
            logger.warning("Failed to record audit for %s: %s", alignment_record.computation_id, str(e))

    def periodic_alignment_review(
        self,
        last_review: Optional[datetime] = None
    ) -> AlignmentReviewResult:
        """
        Project-wide check: Verifies over time that simulations remain at high fidelity,
        human/AI collaboration is on track, and new realities/discoveries are documented/leveraged.
        
        Args:
            last_review: Last review timestamp (uses internal tracking if None)
            
        Returns:
            AlignmentReviewResult with findings and recommendations
        """
        last_review = last_review or self._last_review or (datetime.utcnow() - self.periodic_review_interval)
        now = datetime.utcnow()
        
        # Check if review is due
        if now - last_review < self.periodic_review_interval:
            logger.info("Periodic review not yet due (last: %s)", last_review.isoformat())
            return AlignmentReviewResult(
                review_timestamp=now.isoformat(),
                computations_reviewed=0,
                alignment_gaps=[],
                low_fidelity_cases=[],
                collaboration_gaps=[],
                recommendations=["Review not yet due"],
                overall_health='healthy'
            )
        
        logger.info("Running periodic alignment review (since: %s)", last_review.isoformat())
        
        # Review recent alignment records
        findings = self.knowledge_base.review_recent_alignments(
            since=last_review,
            fields=['sim_metadata', 'crew_participation', 'computation_id', 'fidelity_score']
        )
        
        # Analyze findings
        alignment_gaps = []
        low_fidelity_cases = []
        collaboration_gaps = []
        
        for record in findings:
            comp_id = record.get('computation_id', 'unknown')
            fidelity = record.get('sim_metadata', {}).get('fidelity', 0.0)
            crew_participation = record.get('crew_participation', [])
            
            # Check fidelity
            if fidelity < self.min_fidelity:
                low_fidelity_cases.append(comp_id)
                alignment_gaps.append(f"{comp_id}: Low fidelity ({fidelity:.2f})")
            
            # Check collaboration
            if not crew_participation:
                collaboration_gaps.append(comp_id)
                alignment_gaps.append(f"{comp_id}: No crew interaction")
        
        # Generate recommendations
        recommendations = []
        overall_health = 'healthy'
        
        if len(low_fidelity_cases) > len(findings) * 0.2:  # >20% low fidelity
            recommendations.append("CRITICAL: >20% of computations below fidelity threshold")
            overall_health = 'critical'
        elif len(low_fidelity_cases) > 0:
            recommendations.append(f"WARNING: {len(low_fidelity_cases)} low-fidelity cases detected")
            overall_health = 'warning'
        
        if len(collaboration_gaps) > len(findings) * 0.3:  # >30% no collaboration
            recommendations.append("WARNING: >30% of computations lack crew interaction")
            if overall_health != 'critical':
                overall_health = 'warning'
        
        if not recommendations:
            recommendations.append("All computations aligned with vision statement")
        
        # Record critical gaps in audit log
        for gap in alignment_gaps:
            self.audit_log.record(f"Alignment gap detected: {gap}", severity='critical')
        
        # Update last review timestamp
        self._last_review = now
        
        result = AlignmentReviewResult(
            review_timestamp=now.isoformat(),
            computations_reviewed=len(findings),
            alignment_gaps=alignment_gaps,
            low_fidelity_cases=low_fidelity_cases,
            collaboration_gaps=collaboration_gaps,
            recommendations=recommendations,
            overall_health=overall_health
        )
        
        logger.info(
            "Periodic review complete: %d computations, %s health, %d gaps",
            len(findings),
            overall_health,
            len(alignment_gaps)
        )
        
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get alignment statistics"""
        return {
            'total_alignments': self._alignment_count,
            'successful': self._success_count,
            'warnings': self._warning_count,
            'failed': self._failure_count,
            'success_rate': self._success_count / self._alignment_count if self._alignment_count > 0 else 0.0,
            'alignment_rate': (self._success_count + self._warning_count) / self._alignment_count if self._alignment_count > 0 else 0.0,
            'min_fidelity_threshold': self.min_fidelity,
            'last_review': self._last_review.isoformat() if self._last_review else None
        }


# Mock implementations for graceful degradation
class MockSystemState:
    """Mock system state when unavailable"""
    def get_snapshot(self) -> Dict[str, Any]:
        return {'mock': True, 'min_fidelity': 0.95, 'status': 'operational'}


class MockCrewRegistry:
    """Mock crew registry when unavailable"""
    def log_participation(self, computation_id: str, input_data: Dict[str, Any]) -> List[str]:
        logger.debug("Mock crew registry: logging participation for %s", computation_id)
        return ['mock_crew_member']


class MockSimulationLayer:
    """Mock simulation layer when unavailable"""
    def simulate(self, computation_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("Mock simulation layer: simulating %s", computation_id)
        return {
            'fidelity': 0.98,
            'status': 'success',
            'mock': True,
            'computation_id': computation_id
        }


class MockKnowledgeBase:
    """Mock knowledge base when unavailable"""
    def __init__(self):
        self._alignments = []
        self._contexts = {}
    
    def push_alignment(self, alignment_record: AlignmentRecord):
        logger.debug("Mock KB: storing alignment for %s", alignment_record.computation_id)
        self._alignments.append(alignment_record)
    
    def store_context(self, computation_id: str, context: Dict[str, Any]):
        logger.debug("Mock KB: storing context for %s", computation_id)
        self._contexts[computation_id] = context
    
    def review_recent_alignments(
        self,
        since: datetime,
        fields: List[str]
    ) -> List[Dict[str, Any]]:
        logger.debug("Mock KB: reviewing alignments since %s", since.isoformat())
        return [
            {
                'computation_id': rec.computation_id,
                'sim_metadata': rec.sim_metadata,
                'crew_participation': rec.crew_participation,
                'fidelity_score': rec.fidelity_score
            }
            for rec in self._alignments
            if datetime.fromisoformat(rec.timestamp) >= since
        ]


class MockAuditLog:
    """Mock audit log when DLP tracker unavailable"""
    def record(self, message: str, severity: str = 'info', metadata: Optional[Dict] = None):
        logger.debug("Mock audit log (%s): %s", severity, message)
