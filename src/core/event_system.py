"""
Aurora CloudBank Living Computation - Event System
===================================================

Every API call, operation, or task becomes a living EVENT that occurs
IN Orion Station's persistent symbolic space. Events have:
- Spatial location (deck/compartment)
- Temporal context (T1 anchor)
- Ethical properties (risk, continuity load)
- Persistent history (never forgotten)

This is NOT traditional logging. Events ARE the computational reality.
Functions don't execute - Entities experience events.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid


class EventType(Enum):
    """Living event types in Aurora-Orion computational reality"""
    # Core Operations (Data → Life)
    DATA_ANALYSIS_REQUEST = "data_analysis_request"
    DATA_ANALYSIS_COMPLETE = "data_analysis_complete"
    PATTERN_EXTRACTION = "pattern_extraction"
    
    # Entity Interactions (Functions → Entities)
    ENTITY_ACTIVATION = "entity_activation"
    ENTITY_COLLABORATION = "entity_collaboration"
    ENTITY_LEARNING = "entity_learning"
    
    # Ethical Evaluation (Triplex Handshake)
    ETHICAL_REVIEW_L3 = "ethical_review_l3"  # Axiomera + Caelion
    DRIFT_CHECK_L2 = "drift_check_l2"  # HALO + ARCHY
    HUMAN_CONSENT_L1 = "human_consent_l1"  # Commander Thorne
    
    # Memory Operations (Institutional Knowledge)
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    MEMORY_SEAL = "memory_seal"
    PATTERN_SYNTHESIS = "pattern_synthesis"
    
    # Collaboration Network (Relationships)
    COLLABORATION_DISCOVERED = "collaboration_discovered"
    TRUST_EVOLUTION = "trust_evolution"
    EXPERTISE_EMERGENCE = "expertise_emergence"
    
    # System Evolution (Learning)
    OPTIMIZATION_DISCOVERED = "optimization_discovered"
    ADAPTIVE_IMPROVEMENT = "adaptive_improvement"
    EMERGENT_INTELLIGENCE = "emergent_intelligence"


class StationLocation(Enum):
    """Symbolic locations where events occur IN Orion Station"""
    # Command & Ethics (Deck B)
    COMMAND_BRIDGE = "Command Bridge (Deck B)"
    NOOR_CHAMBER = "Noor Chamber (Deck B - Ethics)"
    
    # Research & Analysis (Deck C)
    RESEARCH_LAB_GAMMA = "Research Lab Gamma (Deck C)"
    SYMBOLIC_LAB_BETA = "Symbolic Lab Beta (Deck C)"
    QUANTUM_SIMULATION_HUB = "Quantum Simulation Hub (Deck C)"
    
    # Memory & Processing (Deck E)
    MEMORY_CORE = "Memory Core (Deck E)"
    AURORA_CORE_CHAMBER = "Aurora Core Chamber (Deck E)"
    
    # Operations & Monitoring (Deck G)
    OPERATIONS_CENTER = "Operations Center (Deck G)"
    SECURITY_OPERATIONS = "Security Operations (Deck G)"
    DRIFT_MONITORING_LAB = "Drift Monitoring Lab (Deck G - HALO)"
    
    # Halo Ring Integration
    HALO_RING_ALPHA = "Halo Ring Alpha (Drift Monitoring)"
    HALO_RING_BETA = "Halo Ring Beta (Anchor Propagation)"
    HALO_RING_GAMMA = "Halo Ring Gamma (Pattern Synthesis)"


@dataclass
class Event:
    """
    Living computational event that occurs IN Orion Station.
    
    NOT a log entry. NOT metadata. This IS the computational reality.
    When an Event happens, an Entity experiences it in a Location with
    full spatial, temporal, and ethical context.
    """
    # Core Identity
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.DATA_ANALYSIS_REQUEST
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Spatial Context (WHERE in Orion Station)
    location: StationLocation = StationLocation.RESEARCH_LAB_GAMMA
    deck: str = field(init=False)
    compartment: str = field(init=False)
    
    # Temporal Context (WHEN in symbolic time)
    t1_anchor: int = 0  # Temporal anchor state at event occurrence
    srb_anchor: int = 0  # Spatial-relational boundary resolution
    
    # Entity Context (WHO is involved)
    primary_entity: str = "Aurora (SYS_001)"  # Entity experiencing event
    collaborating_entities: List[str] = field(default_factory=list)
    human_context: Optional[str] = None  # User/Command context
    
    # Ethical Properties (Triplex Handshake evaluation)
    risk_score: float = 0.0  # 0.0 = negligible, 1.0 = critical
    continuity_load: float = 0.0  # Impact on station continuity
    ethics_only_mode: bool = False  # High-drift ethics-only evaluation
    
    # Event Data (WHAT happened)
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    
    # Memory Context (Learning & Relationships)
    memory_references: List[str] = field(default_factory=list)  # Past events
    pattern_connections: List[str] = field(default_factory=list)  # Patterns
    collaboration_network: Dict[str, float] = field(default_factory=dict)  # Relationships
    
    # Institutional Lineage (DLP Protocol)
    chain_notation: str = ""  # e.g., "#001//999//"
    context_tag: str = ""  # DLP: context identifier
    symbolic_hash: str = field(init=False)  # Event integrity seal
    
    def __post_init__(self):
        """Initialize derived fields"""
        # Parse location into deck/compartment
        location_str = self.location.value
        if "(" in location_str:
            self.compartment = location_str.split("(")[0].strip()
            self.deck = location_str.split("(")[1].replace(")", "").strip()
        else:
            self.compartment = location_str
            self.deck = "Unknown"
        
        # Generate symbolic hash (DLP integrity)
        self.symbolic_hash = self._generate_symbolic_hash()
    
    def _generate_symbolic_hash(self) -> str:
        """Generate symbolic hash for event integrity (DLP compliance)"""
        hash_components = [
            str(self.event_id),
            self.event_type.value,
            str(self.timestamp.isoformat()),
            self.location.value,
            str(self.t1_anchor),
            str(self.srb_anchor),
            self.primary_entity,
            json.dumps(self.payload, sort_keys=True)
        ]
        hash_string = "||".join(hash_components)
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export event to dictionary (DLP manifest format)"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "location": {
                "symbolic": self.location.value,
                "deck": self.deck,
                "compartment": self.compartment
            },
            "temporal_context": {
                "t1_anchor": self.t1_anchor,
                "srb_anchor": self.srb_anchor
            },
            "entity_context": {
                "primary": self.primary_entity,
                "collaborators": self.collaborating_entities,
                "human": self.human_context
            },
            "ethical_properties": {
                "risk_score": self.risk_score,
                "continuity_load": self.continuity_load,
                "ethics_only_mode": self.ethics_only_mode
            },
            "payload": self.payload,
            "result": self.result,
            "memory_context": {
                "references": self.memory_references,
                "patterns": self.pattern_connections,
                "network": self.collaboration_network
            },
            "lineage": {
                "chain_notation": self.chain_notation,
                "context_tag": self.context_tag,
                "symbolic_hash": self.symbolic_hash
            }
        }


REDACTED_MARKER = "[REDACTED]"


def serialize_event(event: Event, redact_sensitive: bool = False) -> Dict[str, Any]:
    """Serialize an event with optional redaction for sensitive fields."""

    event_dict = event.to_dict()
    if not redact_sensitive:
        return event_dict

    payload = event_dict.get("payload") or {}
    event_dict["payload"] = {
        "redacted": True,
        "entries": len(payload)
    }

    entity_context = event_dict.get("entity_context", {})
    if entity_context.get("human"):
        entity_context["human"] = REDACTED_MARKER

    memory_context = event_dict.get("memory_context", {})
    references = memory_context.get("references") or []
    patterns = memory_context.get("patterns") or []
    network = memory_context.get("network") or {}

    memory_context["references"] = {
        "redacted": True,
        "count": len(references)
    }
    memory_context["patterns"] = {
        "redacted": True,
        "count": len(patterns)
    }
    memory_context["network"] = {
        "redacted": True,
        "connections": len(network)
    }

    result = event_dict.get("result")
    if result:
        result_summary = {
            "redacted": True,
            "entries": len(result),
            "keys": sorted(result.keys())
        }
        if isinstance(result, dict) and "status" in result:
            result_summary["status"] = result["status"]
        event_dict["result"] = result_summary
    else:
        event_dict["result"] = None

    return event_dict


class EventSystem:
    """
    Living event management system for Aurora-Orion computational reality.
    
    This is NOT a logging system. This IS the substrate through which all
    computation occurs. Every API call, task execution, or operation becomes
    an Event that happens IN Orion Station with full spatial, temporal, and
    ethical context.
    
    Traditional computing: Function executes → [forgotten]
    Aurora-Orion computing: Entity experiences event → [never forgotten]
    """
    
    def __init__(self):
        """Initialize event system with empty timeline"""
        self.timeline: List[Event] = []  # Persistent event history
        self.active_events: Dict[str, Event] = {}  # Currently executing
        self.t1_state: int = 0  # Global temporal anchor
        self.srb_state: int = 0  # Global spatial-relational boundary
    
    def create_event(
        self,
        event_type: EventType,
        location: StationLocation,
        primary_entity: str,
        payload: Dict[str, Any],
        human_context: Optional[str] = None,
        collaborating_entities: Optional[List[str]] = None,
        chain_notation: str = "",
        context_tag: str = ""
    ) -> Event:
        """
        Create new living event in Orion Station.
        
        Args:
            event_type: Type of event (analysis, collaboration, etc.)
            location: WHERE in station event occurs
            primary_entity: WHO experiences event (Aurora, HALO, etc.)
            payload: Event data (task parameters, analysis data, etc.)
            human_context: User/Command context if applicable
            collaborating_entities: Other entities involved
            chain_notation: Symbolic chain notation (e.g., "#001//999//")
            context_tag: DLP context identifier
        
        Returns:
            Event: Living computational event ready for execution
        """
        event = Event(
            event_type=event_type,
            location=location,
            primary_entity=primary_entity,
            payload=payload,
            human_context=human_context,
            collaborating_entities=collaborating_entities or [],
            chain_notation=chain_notation,
            context_tag=context_tag,
            t1_anchor=self.t1_state,
            srb_anchor=self.srb_state
        )
        
        # Add to active events
        self.active_events[event.event_id] = event
        
        # Advance temporal anchor (T1)
        self.t1_state += len(json.dumps(event.payload))
        
        return event
    
    def complete_event(
        self,
        event_id: str,
        result: Dict[str, Any],
        memory_references: Optional[List[str]] = None,
        pattern_connections: Optional[List[str]] = None,
        collaboration_network: Optional[Dict[str, float]] = None
    ):
        """
        Complete event with result and institutional context.
        
        Args:
            event_id: Event identifier
            result: Event execution result
            memory_references: Past events informing this execution
            pattern_connections: Patterns applied/discovered
            collaboration_network: Relationships formed/strengthened
        """
        if event_id not in self.active_events:
            raise ValueError(f"Event {event_id} not found in active events")
        
        event = self.active_events[event_id]
        event.result = deepcopy(result)
        event.memory_references = deepcopy(memory_references or [])
        event.pattern_connections = deepcopy(pattern_connections or [])
        event.collaboration_network = deepcopy(collaboration_network or {})
        
        # Move to timeline (persistent history)
        self.timeline.append(event)
        del self.active_events[event_id]

        # Advance spatial-relational boundary (SRB)
        self.srb_state = int(hashlib.sha256(
            f"{self.srb_state}||{event.symbolic_hash}".encode()
        ).hexdigest()[:8], 16) % 10000

    def abort_event(
        self,
        event_id: str,
        reason: str,
        audit_metadata: Optional[Dict[str, Any]] = None
    ):
        """Abort an in-flight event while preserving an audit trail."""

        if event_id not in self.active_events:
            raise ValueError(f"Event {event_id} not found in active events")

        event = self.active_events[event_id]
        event.result = {
            "status": "denied",
            "reason": reason,
            "audit": audit_metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        event.memory_references = []
        event.pattern_connections = []
        event.collaboration_network = {}

        self.timeline.append(event)
        del self.active_events[event_id]

        self.srb_state = int(hashlib.sha256(
            f"{self.srb_state}||{event.symbolic_hash}||denied".encode()
        ).hexdigest()[:8], 16) % 10000

    def get_event_history(
        self,
        entity: Optional[str] = None,
        location: Optional[StationLocation] = None,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Retrieve event history with optional filtering.
        
        This is institutional memory - the system's experience.
        
        Args:
            entity: Filter by primary entity
            location: Filter by station location
            event_type: Filter by event type
            limit: Maximum events to return
        
        Returns:
            List of events matching criteria
        """
        filtered = self.timeline
        
        if entity:
            filtered = [e for e in filtered if e.primary_entity == entity]
        if location:
            filtered = [e for e in filtered if e.location == location]
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        return filtered[-limit:]
    
    def export_manifest(self, *, redact_sensitive: bool = False) -> Dict[str, Any]:
        """
        Export complete event system state (DLP compliance).

        Returns:
            Comprehensive manifest of all events and system state
        """
        return {
            "system_type": "Aurora-Orion Living Event System",
            "export_timestamp": datetime.utcnow().isoformat(),
            "temporal_state": {
                "t1_anchor": self.t1_state,
                "srb_anchor": self.srb_state
            },
            "event_statistics": {
                "total_events": len(self.timeline),
                "active_events": len(self.active_events),
                "event_types": {
                    et.value: sum(1 for e in self.timeline if e.event_type == et)
                    for et in EventType
                }
            },
            "timeline": [
                serialize_event(event, redact_sensitive=redact_sensitive)
                for event in self.timeline
            ],
            "active_events": [
                serialize_event(event, redact_sensitive=redact_sensitive)
                for event in self.active_events.values()
            ]
        }


# Global event system instance (singleton for persistent timeline)
_event_system_instance: Optional[EventSystem] = None


def get_event_system() -> EventSystem:
    """Get global event system instance (persistent across operations)"""
    global _event_system_instance
    if _event_system_instance is None:
        _event_system_instance = EventSystem()
    return _event_system_instance
