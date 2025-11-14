"""
Node State - Individual Node Tracking

Each node in the field maintains its state: capabilities, needs, health.
Nodes are autonomous - they broadcast needs and offer capabilities organically.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=node_state, symbolic_hash=FIELD_NODE_v1
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Dict, List, Optional


@dataclass
class Capability:
    """A capability a node can provide."""
    name: str
    strength: float = 1.0  # 0.0 → 1.0 proficiency
    availability: float = 1.0  # 0.0 → 1.0 current capacity
    success_rate: float = 1.0  # Historical success
    
    def can_fulfill(self, threshold: float = 0.5) -> bool:
        """Can this capability fulfill a request?"""
        return (self.strength * self.availability * self.success_rate) >= threshold


@dataclass
class Need:
    """A need broadcast by a node."""
    need_id: str
    description: str
    urgency: float  # 0.0 → 1.0
    required_capabilities: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def is_urgent(self, threshold: float = 0.7) -> bool:
        """Is this need urgent?"""
        return self.urgency >= threshold


@dataclass
class SynapseConnection:
    """Active connection to another node."""
    target_node_id: str
    weight: float  # 0.0 → 1.0 connection strength
    last_used: datetime = field(default_factory=lambda: datetime.now(UTC))
    success_count: int = 0
    failure_count: int = 0
    ethical_score: float = 1.0
    
    def success_rate(self) -> float:
        """Calculate success rate of this synapse."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 1.0
    
    def record_usage(self, success: bool):
        """Record synapse usage and adjust weight."""
        self.last_used = datetime.now(UTC)
        if success:
            self.success_count += 1
            self.weight = min(1.0, self.weight + 0.1)  # Strengthen
        else:
            self.failure_count += 1
            self.weight = max(0.0, self.weight - 0.05)  # Weaken


@dataclass
class NodeHealth:
    """Node health metrics."""
    responsiveness: float = 1.0  # 0.0 → 1.0
    load: float = 0.0  # 0.0 → 1.0 capacity used
    uptime: float = 1.0  # percentage
    
    def is_healthy(self, threshold: float = 0.7) -> bool:
        """Is node healthy enough to form new synapses?"""
        return (self.responsiveness >= threshold and 
                self.load < 0.9 and 
                self.uptime >= threshold)


class NodeState:
    """
    Complete state for a single node in the field.
    
    Nodes are autonomous entities with capabilities they offer
    and needs they broadcast. Synapses form organically based
    on capability matching and ethical validation.
    """
    
    def __init__(
        self,
        node_id: str,
        node_type: str = "agent",
        layer: str = "L1"
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.layer = layer
        
        # Core state
        self.capabilities: Dict[str, Capability] = {}
        self.current_needs: List[Need] = []
        self.active_synapses: Dict[str, SynapseConnection] = {}
        self.health = NodeHealth()
        self.last_update = datetime.now(UTC)
        
    def add_capability(
        self,
        name: str,
        strength: float = 1.0,
        availability: float = 1.0
    ) -> Capability:
        """Add a capability this node can provide."""
        capability = Capability(
            name=name,
            strength=strength,
            availability=availability
        )
        self.capabilities[name] = capability
        self.last_update = datetime.now(UTC)
        return capability
    
    def broadcast_need(
        self,
        need_id: str,
        description: str,
        urgency: float,
        required_capabilities: List[str]
    ) -> Need:
        """Broadcast a need into the field."""
        need = Need(
            need_id=need_id,
            description=description,
            urgency=urgency,
            required_capabilities=required_capabilities
        )
        self.current_needs.append(need)
        self.last_update = datetime.now(UTC)
        return need
    
    def fulfill_need(self, need_id: str):
        """Mark a need as fulfilled and remove it."""
        self.current_needs = [n for n in self.current_needs if n.need_id != need_id]
        self.last_update = datetime.now(UTC)
    
    def form_synapse(
        self,
        target_node_id: str,
        initial_weight: float = 0.3,
        ethical_score: float = 1.0
    ) -> SynapseConnection:
        """Form a new synapse to another node."""
        synapse = SynapseConnection(
            target_node_id=target_node_id,
            weight=initial_weight,
            ethical_score=ethical_score
        )
        self.active_synapses[target_node_id] = synapse
        self.last_update = datetime.now(UTC)
        return synapse
    
    def prune_synapse(self, target_node_id: str):
        """Remove a synapse that has decayed too much."""
        if target_node_id in self.active_synapses:
            del self.active_synapses[target_node_id]
            self.last_update = datetime.now(UTC)
    
    def get_synapse(self, target_node_id: str) -> Optional[SynapseConnection]:
        """Get synapse to specific node if exists."""
        return self.active_synapses.get(target_node_id)
    
    def decay_synapses(self, decay_rate: float = 0.01):
        """Apply natural decay to unused synapses."""
        now = datetime.now(UTC)
        pruned = []
        
        for target_id, synapse in self.active_synapses.items():
            # Check time since last use
            hours_since_use = (now - synapse.last_used).total_seconds() / 3600
            
            if hours_since_use >= 1.0:
                # Apply decay
                synapse.weight = max(0.0, synapse.weight - decay_rate)
                
                # Prune if too weak
                if synapse.weight < 0.1:
                    pruned.append(target_id)
        
        # Remove pruned synapses
        for target_id in pruned:
            self.prune_synapse(target_id)
    
    def can_match_capabilities(
        self,
        required: List[str],
        threshold: float = 0.5
    ) -> bool:
        """Can this node fulfill the required capabilities?"""
        for cap_name in required:
            if cap_name not in self.capabilities:
                return False
            if not self.capabilities[cap_name].can_fulfill(threshold):
                return False
        return True
    
    def calculate_match_score(
        self,
        required: List[str],
        urgency: float = 0.5
    ) -> float:
        """Calculate how well this node matches required capabilities."""
        if not required:
            return 0.0
        
        matched_strength = 0.0
        for cap_name in required:
            if cap_name in self.capabilities:
                cap = self.capabilities[cap_name]
                matched_strength += (cap.strength * cap.availability * cap.success_rate)
        
        # Average match strength weighted by urgency and health
        avg_match = matched_strength / len(required)
        return avg_match * self.health.responsiveness * (0.5 + 0.5 * urgency)
    
    def to_dict(self) -> Dict:
        """Export node state to dictionary."""
        return {
            "node_id": self.node_id,
            "type": self.node_type,
            "layer": self.layer,
            "capabilities": {
                name: {
                    "strength": cap.strength,
                    "availability": cap.availability,
                    "success_rate": cap.success_rate
                }
                for name, cap in self.capabilities.items()
            },
            "current_needs": [
                {
                    "need_id": need.need_id,
                    "description": need.description,
                    "urgency": need.urgency,
                    "required_capabilities": need.required_capabilities,
                    "timestamp": need.timestamp.isoformat()
                }
                for need in self.current_needs
            ],
            "active_synapses": {
                target_id: {
                    "weight": synapse.weight,
                    "last_used": synapse.last_used.isoformat(),
                    "success_count": synapse.success_count,
                    "failure_count": synapse.failure_count,
                    "ethical_score": synapse.ethical_score,
                    "success_rate": synapse.success_rate()
                }
                for target_id, synapse in self.active_synapses.items()
            },
            "health": {
                "responsiveness": self.health.responsiveness,
                "load": self.health.load,
                "uptime": self.health.uptime
            },
            "last_update": self.last_update.isoformat()
        }
