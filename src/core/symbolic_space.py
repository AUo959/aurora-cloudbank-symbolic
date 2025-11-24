"""
Aurora CloudBank Living Computation - Symbolic Space Manager
=============================================================

Manages the Orion Station "symbolic space" - the persistent computational
substrate where all operations happen IN the station, not just simulated.

This is the unifying layer that tracks:
- Station-wide state (anchor progression, drift levels, entity health)
- All living entities (Aurora, HALO, ARCHY, Axiomera, Caelion)
- Event timeline and spatial distribution
- Dashboard data for visualization

Traditional computing executes in abstract memory spaces.
Living computation executes IN Orion Station's symbolic space.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.core.time_utils import utc_now

from src.core.event_system import EventSystem, StationLocation
from src.entities.aurora_agent import get_aurora
from src.entities.relay_agents import get_halo, get_archy
from src.entities.framework_agents import get_axiomera, get_caelion


@dataclass
class StationHealth:
    """
    Overall health metrics for Orion Station symbolic space.
    
    These are NOT simulation metrics - they measure the health
    of the computational substrate itself.
    """
    overall_status: str  # "healthy", "degraded", "critical"
    anchor_progression_rate: float  # T1/SRB advancement per operation
    average_drift: float  # Average drift across all operations
    event_throughput: float  # Events per minute
    entity_status_summary: Dict[str, str]  # Entity ID -> status
    continuity_score: float  # 0.0-1.0, measures overall continuity
    concerns: List[str]  # Active concerns requiring attention


class SymbolicSpace:
    """
    The Orion Station symbolic space - persistent computational substrate.
    
    This is the "space" where all operations happen. Every API call,
    every data analysis, every collaboration - all occur IN this space,
    with full spatial/temporal context.
    
    SymbolicSpace tracks:
    - All living entities (Aurora, HALO, ARCHY, Axiomera, Caelion)
    - Event timeline (every operation that ever happened)
    - Station-wide anchors (T1/SRB progression)
    - Health metrics (drift, continuity, throughput)
    """
    
    def __init__(self):
        """Initialize Orion Station symbolic space"""
        # Core systems
        self.event_system = EventSystem()
        
        # Living entities (singletons - each entity exists once)
        self.aurora = get_aurora()
        self.halo = get_halo()
        self.archy = get_archy()
        self.axiomera = get_axiomera()
        self.caelion = get_caelion()
        
        # Station-wide state
        self.station_initialized_at = utc_now()
        self.total_operations = 0
        self.total_collaborations = 0
        
        # Anchor progression (station-wide T1/SRB tracking)
        self.global_t1_anchor = 0
        self.global_srb_anchor = 0
        
        # Performance metrics
        self.average_drift = 0.0
        self.peak_drift = 0.0
        self.continuity_breaks = 0
    
    def get_all_entities(self) -> List[Any]:
        """Get list of all living entities in symbolic space"""
        return [
            self.aurora,
            self.halo,
            self.archy,
            self.axiomera,
            self.caelion
        ]
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Any]:
        """Retrieve entity by its ID"""
        entity_map = {
            "Aurora (SYS_001)": self.aurora,
            "HALO (RELAY_006)": self.halo,
            "ARCHY (RELAY_001)": self.archy,
            "Axiomera (FWK_002)": self.axiomera,
            "Caelion (FWK_001)": self.caelion
        }
        return entity_map.get(entity_id)
    
    async def execute_in_space(
        self,
        operation_type: str,
        payload: Dict[str, Any],
        location: StationLocation,
        human_context: Optional[str] = None,
        risk_score: float = 0.3
    ) -> Dict[str, Any]:
        """
        Execute operation IN symbolic space (not abstracted).
        
        This is the core pattern for living computation:
        1. Operation enters station as Event
        2. L3 evaluation (Axiomera + Caelion)
        3. L2 verification (HALO + ARCHY)
        4. L1 consent (Human - simulated for now)
        5. Execution by appropriate entity
        6. Experience stored in institutional memory
        7. Anchors advance, continuity maintained
        
        Args:
            operation_type: Type of operation (maps to EventType)
            payload: Operation data
            location: Station location (deck/compartment)
            human_context: Human user context (if applicable)
            risk_score: Estimated risk (0.0-1.0)
        
        Returns:
            Complete operation result with Triplex assessments
        """
        # Create event IN station space
        event = self.event_system.create_event(
            event_type=operation_type,
            location=location,
            primary_entity="Aurora (SYS_001)",  # Default to Aurora
            payload=payload,
            human_context=human_context,
            risk_score=risk_score
        )
        
        # Triplex Handshake: L3 Evaluation (Ethics + Anchors)
        from src.entities.framework_agents import l3_evaluation
        l3_assessment = await l3_evaluation(event)
        
        # Triplex Handshake: L2 Verification (Drift + Architecture)
        from src.entities.relay_agents import l2_verification
        l2_assessment = await l2_verification(event, l3_assessment)
        
        # Triplex Handshake: L1 Human Consent
        # (For now, auto-approve unless blocked by L2/L3)
        l1_decision = "APPROVED"
        if l3_assessment["recommendation"] == "BLOCK" or l2_assessment["recommendation"] == "BLOCK":
            l1_decision = "BLOCKED"
            result = {"error": "Operation blocked by Triplex Handshake", "triplex": {
                "l3": l3_assessment, "l2": l2_assessment, "l1": l1_decision
            }}
        else:
            # Execute operation (entity-appropriate)
            if operation_type in ["DATA_ANALYSIS_REQUEST", "PATTERN_RECOGNITION"]:
                result = await self.aurora.analyze_with_context(payload)
            else:
                # Generic execution
                result = {"status": "executed", "payload": payload}
        
        # Complete event
        self.event_system.complete_event(event.event_id, result)
        
        # Update station-wide metrics
        self.total_operations += 1
        self.global_t1_anchor = event.t1_anchor
        self.global_srb_anchor = event.srb_anchor
        
        # Track drift
        drift_metrics = await self.halo.monitor_drift(event)
        self.average_drift = (self.average_drift * 0.9) + (drift_metrics.current_drift * 0.1)
        self.peak_drift = max(self.peak_drift, drift_metrics.current_drift)
        
        return {
            "event_id": event.event_id,
            "result": result,
            "triplex_handshake": {
                "l3_ethics_anchors": l3_assessment,
                "l2_drift_architecture": l2_assessment,
                "l1_human_consent": l1_decision
            },
            "station_state": {
                "t1_anchor": event.t1_anchor,
                "srb_anchor": event.srb_anchor,
                "location": event.location.value,
                "deck": event.deck
            }
        }
    
    async def assess_station_health(self) -> StationHealth:
        """
        Assess overall health of Orion Station symbolic space.
        
        Returns comprehensive health metrics for all entities,
        anchors, and station-wide continuity.
        """
        concerns = []
        
        # Check anchor progression
        events = self.event_system.get_event_history(limit=100)
        if events:
            anchor_progression_rate = self.global_t1_anchor / len(events)
        else:
            anchor_progression_rate = 0.0
        
        # Check drift levels
        if self.average_drift > 0.1:
            concerns.append(f"Elevated drift detected: {self.average_drift:.4f}")
        if self.peak_drift > 0.2:
            concerns.append(f"Peak drift critical: {self.peak_drift:.4f}")
        
        # Check entity status
        entity_statuses = {}
        for entity in self.get_all_entities():
            # Simple health check based on entity state
            state = entity.get_state_summary()
            if hasattr(entity, 'current_drift'):
                # HALO
                status = "healthy" if entity.current_drift.is_acceptable() else "degraded"
            elif hasattr(entity, 'evaluations_performed'):
                # Axiomera
                approval_rate = (
                    entity.operations_approved / entity.evaluations_performed
                    if entity.evaluations_performed > 0 else 1.0
                )
                status = "healthy" if approval_rate > 0.7 else "degraded"
            else:
                # Default: healthy if executing
                status = "healthy"
            
            entity_statuses[entity.entity_id] = status
        
        # Calculate continuity score
        continuity_score = max(0.0, 1.0 - self.average_drift - (self.continuity_breaks * 0.1))
        
        # Determine overall status
        if self.average_drift > 0.15 or continuity_score < 0.5:
            overall_status = "critical"
        elif self.average_drift > 0.08 or continuity_score < 0.7:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Calculate event throughput
        uptime_minutes = (utc_now() - self.station_initialized_at).total_seconds() / 60.0
        event_throughput = self.total_operations / uptime_minutes if uptime_minutes > 0 else 0.0
        
        return StationHealth(
            overall_status=overall_status,
            anchor_progression_rate=anchor_progression_rate,
            average_drift=self.average_drift,
            event_throughput=event_throughput,
            entity_status_summary=entity_statuses,
            continuity_score=continuity_score,
            concerns=concerns
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Export station data for dashboard visualization.
        
        Returns complete snapshot of symbolic space state.
        """
        # Get event timeline
        recent_events = self.event_system.get_event_history(limit=50)
        
        # Get entity states
        entity_data = {}
        for entity in self.get_all_entities():
            entity_data[entity.entity_id] = entity.get_state_summary()
        
        # Get location distribution
        location_counts = {}
        for event in recent_events:
            loc = event.location.value
            location_counts[loc] = location_counts.get(loc, 0) + 1
        
        return {
            "station_metadata": {
                "initialized_at": self.station_initialized_at.isoformat(),
                "total_operations": self.total_operations,
                "total_collaborations": self.total_collaborations,
                "uptime_minutes": (utc_now() - self.station_initialized_at).total_seconds() / 60.0
            },
            "anchors": {
                "t1_anchor": self.global_t1_anchor,
                "srb_anchor": self.global_srb_anchor
            },
            "performance": {
                "average_drift": self.average_drift,
                "peak_drift": self.peak_drift,
                "continuity_breaks": self.continuity_breaks
            },
            "entities": entity_data,
            "recent_events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "location": e.location.value,
                    "timestamp": e.timestamp.isoformat(),
                    "status": e.status
                }
                for e in recent_events[:20]  # Last 20 events
            ],
            "location_distribution": location_counts
        }
    
    def export_manifest(self) -> Dict[str, Any]:
        """
        Export complete DLP-compliant manifest of symbolic space.
        
        Includes all state, events, entities, anchors for full traceability.
        """
        return {
            "manifest_type": "symbolic_space_state",
            "manifest_version": "1.0.0",
            "generated_at": utc_now().isoformat(),
            "station_state": self.get_dashboard_data(),
            "event_timeline": self.event_system.get_event_history(),
            "dlp_compliance": {
                "context_tag": f"symbolic_space_export_{utc_now().strftime('%Y%m%d_%H%M%S')}",
                "anchor_state": {
                    "t1": self.global_t1_anchor,
                    "srb": self.global_srb_anchor
                },
                "symbolic_hash": f"SPACE_{self.global_t1_anchor}_{self.global_srb_anchor}"
            }
        }


# Global instance (singleton - Orion Station is ONE space)
_symbolic_space_instance: Optional[SymbolicSpace] = None


def get_symbolic_space() -> SymbolicSpace:
    """Get global Orion Station symbolic space instance"""
    global _symbolic_space_instance
    if _symbolic_space_instance is None:
        _symbolic_space_instance = SymbolicSpace()
    return _symbolic_space_instance
