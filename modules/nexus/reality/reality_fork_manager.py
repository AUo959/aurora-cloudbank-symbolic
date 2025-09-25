#!/usr/bin/env python3
"""
NEXUS Phase 5: Reality Fork Manager
Anchor: T5-REALITY-FORK-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 5.0.0
DLP Tag: REALITY_FORK_OK

Revolutionary reality fork management system for branch-based reality
management with consensus protocols and quantum coherence preservation.
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from pathlib import Path

class RealityForkType(Enum):
    """Types of reality forks"""
    EXPLORATORY = "exploratory"      # Safe exploration fork
    EXPERIMENTAL = "experimental"    # High-risk experimentation
    CONSENSUS = "consensus"          # Multi-agent consensus building
    QUANTUM = "quantum"              # Quantum superposition reality
    TEMPORAL = "temporal"            # Temporal experimentation
    ROLLBACK = "rollback"            # Emergency rollback point

class ForkStatus(Enum):
    """Status of reality forks"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    CONVERGING = "converging"
    MERGED = "merged"
    COLLAPSED = "collapsed"
    QUARANTINED = "quarantined"

@dataclass
class RealityFork:
    """Represents a reality fork with quantum coherence"""
    
    fork_id: str
    fork_type: RealityForkType
    status: ForkStatus
    parent_reality: Optional[str]
    branch_point: datetime
    forked_by: str
    
    # Fork characteristics
    reality_state: Dict[str, Any] = field(default_factory=dict)
    quantum_coherence: float = 1.0
    consensus_level: float = 0.0
    stability_index: float = 1.0
    
    # Participants and consensus
    participating_agents: Set[str] = field(default_factory=set)
    consensus_votes: Dict[str, float] = field(default_factory=dict)
    
    # Fork metadata
    description: str = ""
    experiment_parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    # Quantum entanglement with other forks
    entangled_forks: Set[str] = field(default_factory=set)
    quantum_signature: str = field(default="")
    
    def __post_init__(self):
        if not self.quantum_signature:
            # Generate quantum signature based on fork properties
            signature_data = f"{self.fork_id}{self.fork_type.value}{self.branch_point.isoformat()}"
            self.quantum_signature = hashlib.sha256(signature_data.encode()).hexdigest()[:24]

@dataclass
class ConsensusMeasurement:
    """Represents a consensus measurement across reality forks"""
    
    measurement_id: str
    measured_at: datetime
    participating_forks: Set[str]
    consensus_matrix: Dict[str, Dict[str, float]]
    quantum_entanglement: float
    stability_metric: float
    convergence_probability: float

class RealityForkManager:
    """Revolutionary reality fork management system"""
    
    def __init__(self):
        self.anchor = "T5-REALITY-FORK-2025"
        self.seed = "EOS_SEED_ORION"
        
        # Reality fork tracking
        self.active_forks: Dict[str, RealityFork] = {}
        self.fork_history: List[RealityFork] = []
        self.consensus_measurements: List[ConsensusMeasurement] = []
        
        # Base reality state
        self.base_reality_id = "BASE-REALITY-NEXUS"
        self.current_reality = self.base_reality_id
        
        # Fork management
        self.max_concurrent_forks = 10
        self.quantum_coherence_threshold = 0.3
        self.consensus_threshold = 0.75
        
        # Quantum entanglement tracking
        self.entanglement_matrix: Dict[str, Dict[str, float]] = {}
        
        print(f"🌌 Reality Fork Manager initialized")
        print(f"   Anchor: {self.anchor}")
        print(f"   Base Reality: {self.base_reality_id}")
        
    async def create_reality_fork(
        self,
        fork_type: RealityForkType,
        forked_by: str,
        description: str = "",
        experiment_parameters: Dict[str, Any] = None,
        parent_reality: str = None
    ) -> RealityFork:
        """Create a new reality fork"""
        
        if len(self.active_forks) >= self.max_concurrent_forks:
            raise RuntimeError(f"Maximum concurrent forks ({self.max_concurrent_forks}) reached")
            
        fork_id = f"FORK-{fork_type.value.upper()}-{uuid.uuid4().hex[:8]}"
        parent = parent_reality or self.current_reality
        
        fork = RealityFork(
            fork_id=fork_id,
            fork_type=fork_type,
            status=ForkStatus.INITIALIZING,
            parent_reality=parent,
            branch_point=datetime.utcnow(),
            forked_by=forked_by,
            description=description,
            experiment_parameters=experiment_parameters or {}
        )
        
        # Initialize reality state from parent
        if parent in self.active_forks:
            parent_fork = self.active_forks[parent]
            fork.reality_state = parent_fork.reality_state.copy()
        else:
            # Initialize from base reality
            fork.reality_state = {
                "symbolic_anchors": ["T1-NEXUS-INIT", "T2-MULTIAGENT", "T3-QUANTUM", "T4-MEMORY-WEAVE"],
                "agent_count": 10,
                "quantum_coherence": 1.0,
                "entropy_level": 0.05,
                "consensus_protocol": "active"
            }
            
        # Add fork to active tracking
        self.active_forks[fork_id] = fork
        fork.status = ForkStatus.ACTIVE
        
        print(f"🔀 Reality fork created: {fork_id}")
        print(f"   Type: {fork_type.value}")
        print(f"   Forked by: {forked_by}")
        print(f"   Parent: {parent}")
        
        return fork
        
    async def join_reality_fork(self, fork_id: str, agent_id: str) -> bool:
        """Join an agent to a reality fork"""
        
        if fork_id not in self.active_forks:
            return False
            
        fork = self.active_forks[fork_id]
        fork.participating_agents.add(agent_id)
        fork.last_update = datetime.utcnow()
        
        print(f"👥 Agent {agent_id} joined fork {fork_id}")
        return True
        
    async def update_fork_state(
        self,
        fork_id: str,
        state_updates: Dict[str, Any],
        agent_id: str
    ) -> bool:
        """Update the state of a reality fork"""
        
        if fork_id not in self.active_forks:
            return False
            
        fork = self.active_forks[fork_id]
        
        # Apply state updates
        for key, value in state_updates.items():
            fork.reality_state[key] = value
            
        # Update quantum coherence based on changes
        coherence_impact = self._calculate_coherence_impact(state_updates)
        fork.quantum_coherence = max(0.0, fork.quantum_coherence - coherence_impact)
        
        # Update stability index
        fork.stability_index = self._calculate_stability_index(fork)
        
        fork.last_update = datetime.utcnow()
        
        print(f"🔄 Fork {fork_id} state updated by {agent_id}")
        print(f"   Quantum coherence: {fork.quantum_coherence:.3f}")
        print(f"   Stability index: {fork.stability_index:.3f}")
        
        return True
        
    async def measure_consensus(self, fork_ids: List[str]) -> ConsensusMeasurement:
        """Measure consensus across multiple reality forks"""
        
        measurement_id = f"CONSENSUS-{uuid.uuid4().hex[:8]}"
        consensus_matrix = {}
        participating_forks = set(fork_ids)
        
        # Calculate pairwise consensus between forks
        for fork_id in fork_ids:
            if fork_id not in self.active_forks:
                continue
                
            consensus_matrix[fork_id] = {}
            fork = self.active_forks[fork_id]
            
            for other_fork_id in fork_ids:
                if other_fork_id == fork_id or other_fork_id not in self.active_forks:
                    continue
                    
                other_fork = self.active_forks[other_fork_id]
                consensus_score = self._calculate_reality_consensus(fork, other_fork)
                consensus_matrix[fork_id][other_fork_id] = consensus_score
                
        # Calculate quantum entanglement
        quantum_entanglement = self._calculate_quantum_entanglement(fork_ids)
        
        # Calculate stability metric
        stability_metric = self._calculate_multi_fork_stability(fork_ids)
        
        # Calculate convergence probability
        convergence_probability = self._calculate_convergence_probability(consensus_matrix)
        
        measurement = ConsensusMeasurement(
            measurement_id=measurement_id,
            measured_at=datetime.utcnow(),
            participating_forks=participating_forks,
            consensus_matrix=consensus_matrix,
            quantum_entanglement=quantum_entanglement,
            stability_metric=stability_metric,
            convergence_probability=convergence_probability
        )
        
        self.consensus_measurements.append(measurement)
        
        print(f"📊 Consensus measured: {measurement_id}")
        print(f"   Participating forks: {len(participating_forks)}")
        print(f"   Quantum entanglement: {quantum_entanglement:.3f}")
        print(f"   Convergence probability: {convergence_probability:.3f}")
        
        return measurement
        
    async def merge_reality_forks(
        self,
        fork_ids: List[str],
        merge_strategy: str = "consensus"
    ) -> Optional[RealityFork]:
        """Merge multiple reality forks into a unified reality"""
        
        if not fork_ids or len(fork_ids) < 2:
            return None
            
        # Validate all forks exist and are mergeable
        forks_to_merge = []
        for fork_id in fork_ids:
            if fork_id not in self.active_forks:
                print(f"❌ Fork {fork_id} not found for merge")
                return None
            forks_to_merge.append(self.active_forks[fork_id])
            
        # Measure consensus before merge
        consensus = await self.measure_consensus(fork_ids)
        
        if consensus.convergence_probability < self.consensus_threshold:
            print(f"⚠️ Convergence probability {consensus.convergence_probability:.3f} below threshold {self.consensus_threshold}")
            # Option to force merge or abort
            
        # Create merged reality fork
        merged_fork = await self.create_reality_fork(
            fork_type=RealityForkType.CONSENSUS,
            forked_by="reality_fork_manager",
            description=f"Merged from {len(fork_ids)} forks using {merge_strategy} strategy",
            experiment_parameters={
                "merge_strategy": merge_strategy,
                "source_forks": fork_ids,
                "consensus_measurement": consensus.measurement_id
            }
        )
        
        # Apply merge strategy
        if merge_strategy == "consensus":
            merged_state = self._merge_by_consensus(forks_to_merge, consensus)
        elif merge_strategy == "quantum_weighted":
            merged_state = self._merge_by_quantum_weights(forks_to_merge)
        else:
            merged_state = self._merge_by_majority(forks_to_merge)
            
        merged_fork.reality_state.update(merged_state)
        
        # Update participating agents
        for fork in forks_to_merge:
            merged_fork.participating_agents.update(fork.participating_agents)
            
        # Collapse source forks
        for fork_id in fork_ids:
            await self.collapse_reality_fork(fork_id, "merged")
            
        print(f"🔗 Reality forks merged: {merged_fork.fork_id}")
        print(f"   Source forks: {len(fork_ids)}")
        print(f"   Participating agents: {len(merged_fork.participating_agents)}")
        
        return merged_fork
        
    async def collapse_reality_fork(self, fork_id: str, reason: str = "manual") -> bool:
        """Collapse a reality fork"""
        
        if fork_id not in self.active_forks:
            return False
            
        fork = self.active_forks[fork_id]
        fork.status = ForkStatus.COLLAPSED
        
        # Move to history
        self.fork_history.append(fork)
        del self.active_forks[fork_id]
        
        print(f"💥 Reality fork collapsed: {fork_id} ({reason})")
        return True
        
    def _calculate_coherence_impact(self, state_updates: Dict[str, Any]) -> float:
        """Calculate quantum coherence impact of state changes"""
        # Simplified coherence calculation
        impact = 0.0
        for key, value in state_updates.items():
            if isinstance(value, (int, float)):
                impact += abs(value) * 0.01
            else:
                impact += 0.05
        return min(impact, 0.5)  # Cap at 50% coherence loss
        
    def _calculate_stability_index(self, fork: RealityFork) -> float:
        """Calculate fork stability index"""
        base_stability = fork.quantum_coherence
        
        # Factor in consensus level
        consensus_factor = fork.consensus_level * 0.3
        
        # Factor in time since creation
        time_factor = max(0.1, 1.0 - (datetime.utcnow() - fork.created_at).total_seconds() / 3600)
        
        return min(1.0, base_stability + consensus_factor * time_factor)
        
    def _calculate_reality_consensus(self, fork1: RealityFork, fork2: RealityFork) -> float:
        """Calculate consensus score between two reality forks"""
        if not fork1.reality_state or not fork2.reality_state:
            return 0.0
            
        common_keys = set(fork1.reality_state.keys()) & set(fork2.reality_state.keys())
        if not common_keys:
            return 0.0
            
        consensus_score = 0.0
        for key in common_keys:
            val1, val2 = fork1.reality_state[key], fork2.reality_state[key]
            
            if val1 == val2:
                consensus_score += 1.0
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                diff = abs(val1 - val2)
                max_val = max(abs(val1), abs(val2), 1.0)
                similarity = max(0.0, 1.0 - diff / max_val)
                consensus_score += similarity
            else:
                # String or other type similarity (simplified)
                consensus_score += 0.5 if str(val1).lower() in str(val2).lower() else 0.0
                
        return consensus_score / len(common_keys)
        
    def _calculate_quantum_entanglement(self, fork_ids: List[str]) -> float:
        """Calculate quantum entanglement between forks"""
        if len(fork_ids) < 2:
            return 0.0
            
        entanglement_sum = 0.0
        pairs = 0
        
        for i, fork_id1 in enumerate(fork_ids):
            for fork_id2 in fork_ids[i+1:]:
                if fork_id1 in self.active_forks and fork_id2 in self.active_forks:
                    fork1 = self.active_forks[fork_id1]
                    fork2 = self.active_forks[fork_id2]
                    
                    # Calculate entanglement based on shared agents and coherence
                    shared_agents = fork1.participating_agents & fork2.participating_agents
                    agent_entanglement = len(shared_agents) / max(len(fork1.participating_agents | fork2.participating_agents), 1)
                    coherence_entanglement = (fork1.quantum_coherence * fork2.quantum_coherence) ** 0.5
                    
                    entanglement = (agent_entanglement + coherence_entanglement) / 2
                    entanglement_sum += entanglement
                    pairs += 1
                    
        return entanglement_sum / max(pairs, 1)
        
    def _calculate_multi_fork_stability(self, fork_ids: List[str]) -> float:
        """Calculate overall stability across multiple forks"""
        if not fork_ids:
            return 0.0
            
        stability_sum = 0.0
        valid_forks = 0
        
        for fork_id in fork_ids:
            if fork_id in self.active_forks:
                stability_sum += self.active_forks[fork_id].stability_index
                valid_forks += 1
                
        return stability_sum / max(valid_forks, 1)
        
    def _calculate_convergence_probability(self, consensus_matrix: Dict[str, Dict[str, float]]) -> float:
        """Calculate probability of successful convergence"""
        if not consensus_matrix:
            return 0.0
            
        consensus_scores = []
        for fork_id, scores in consensus_matrix.items():
            if scores:
                avg_score = sum(scores.values()) / len(scores)
                consensus_scores.append(avg_score)
                
        if not consensus_scores:
            return 0.0
            
        overall_consensus = sum(consensus_scores) / len(consensus_scores)
        
        # Apply sigmoid function for probability
        import math
        probability = 1 / (1 + math.exp(-5 * (overall_consensus - 0.5)))
        
        return probability
        
    def _merge_by_consensus(self, forks: List[RealityFork], consensus: ConsensusMeasurement) -> Dict[str, Any]:
        """Merge fork states using consensus weights"""
        merged_state = {}
        
        # Collect all keys from all forks
        all_keys = set()
        for fork in forks:
            all_keys.update(fork.reality_state.keys())
            
        # For each key, determine consensus value
        for key in all_keys:
            values = []
            weights = []
            
            for fork in forks:
                if key in fork.reality_state:
                    values.append(fork.reality_state[key])
                    # Weight by fork stability and consensus
                    weight = fork.stability_index * (1 + fork.consensus_level)
                    weights.append(weight)
                    
            if values:
                if all(isinstance(v, (int, float)) for v in values):
                    # Weighted average for numerical values
                    total_weight = sum(weights)
                    merged_value = sum(v * w for v, w in zip(values, weights)) / total_weight
                    merged_state[key] = merged_value
                else:
                    # Most common value for non-numerical
                    value_counts = {}
                    for v, w in zip(values, weights):
                        value_counts[str(v)] = value_counts.get(str(v), 0) + w
                    merged_state[key] = max(value_counts, key=value_counts.get)
                    
        return merged_state
        
    def _merge_by_quantum_weights(self, forks: List[RealityFork]) -> Dict[str, Any]:
        """Merge fork states using quantum coherence weights"""
        merged_state = {}
        
        all_keys = set()
        for fork in forks:
            all_keys.update(fork.reality_state.keys())
            
        for key in all_keys:
            values = []
            weights = []
            
            for fork in forks:
                if key in fork.reality_state:
                    values.append(fork.reality_state[key])
                    weights.append(fork.quantum_coherence)
                    
            if values and weights:
                total_weight = sum(weights)
                if total_weight > 0:
                    if all(isinstance(v, (int, float)) for v in values):
                        merged_value = sum(v * w for v, w in zip(values, weights)) / total_weight
                        merged_state[key] = merged_value
                    else:
                        # Quantum-weighted selection
                        import random
                        selected_value = random.choices(values, weights=weights, k=1)[0]
                        merged_state[key] = selected_value
                        
        return merged_state
        
    def _merge_by_majority(self, forks: List[RealityFork]) -> Dict[str, Any]:
        """Merge fork states using majority rule"""
        merged_state = {}
        
        all_keys = set()
        for fork in forks:
            all_keys.update(fork.reality_state.keys())
            
        for key in all_keys:
            values = []
            for fork in forks:
                if key in fork.reality_state:
                    values.append(fork.reality_state[key])
                    
            if values:
                if all(isinstance(v, (int, float)) for v in values):
                    # Average for numerical values
                    merged_state[key] = sum(values) / len(values)
                else:
                    # Most frequent for non-numerical
                    value_counts = {}
                    for v in values:
                        value_counts[str(v)] = value_counts.get(str(v), 0) + 1
                    merged_state[key] = max(value_counts, key=value_counts.get)
                    
        return merged_state
        
    def export_reality_manifest(self) -> Dict[str, Any]:
        """Export complete reality fork manifest"""
        
        manifest = {
            "anchor": self.anchor,
            "seed": self.seed,
            "timestamp": datetime.utcnow().isoformat(),
            "base_reality": self.base_reality_id,
            "current_reality": self.current_reality,
            
            "fork_stats": {
                "active_forks": len(self.active_forks),
                "total_history": len(self.fork_history),
                "consensus_measurements": len(self.consensus_measurements)
            },
            
            "active_forks": {
                fork_id: {
                    "fork_type": fork.fork_type.value,
                    "status": fork.status.value,
                    "quantum_coherence": fork.quantum_coherence,
                    "stability_index": fork.stability_index,
                    "participating_agents": len(fork.participating_agents),
                    "created_at": fork.created_at.isoformat(),
                    "quantum_signature": fork.quantum_signature
                }
                for fork_id, fork in self.active_forks.items()
            },
            
            "recent_consensus": [
                {
                    "measurement_id": cm.measurement_id,
                    "measured_at": cm.measured_at.isoformat(),
                    "participating_forks": len(cm.participating_forks),
                    "quantum_entanglement": cm.quantum_entanglement,
                    "convergence_probability": cm.convergence_probability
                }
                for cm in self.consensus_measurements[-5:]
            ]
        }
        
        # Generate manifest seal
        manifest_json = json.dumps(manifest, sort_keys=True, default=str)
        manifest["seal"] = hashlib.sha256(manifest_json.encode()).hexdigest()
        
        return manifest

# Global reality fork manager instance
_reality_fork_manager = None

def get_reality_fork_manager() -> RealityForkManager:
    """Get the global reality fork manager instance"""
    global _reality_fork_manager
    if _reality_fork_manager is None:
        _reality_fork_manager = RealityForkManager()
    return _reality_fork_manager