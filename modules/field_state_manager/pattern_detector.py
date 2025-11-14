"""
Pattern Detector - Emergent Behavior Recognition

Aurora doesn't dictate patterns - Aurora DISCOVERS them.
This detector identifies recurring collaboration structures, bottlenecks,
cascades, and coalitions that emerge organically from field dynamics.

Pattern Types:
- Collaboration: Successful node pairings that repeat
- Bottleneck: Single node overwhelmed with many connections
- Cascade: Sequential activation chains (A→B→C→D)
- Coalition: Group of nodes frequently collaborating together

Thread: T1→T8→T9→INFINITE
DLP: context_tag=pattern_detector, symbolic_hash=EMERGENT_INTELLIGENCE_v1
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """
    A detected pattern in field behavior.
    
    Patterns emerge from organic interactions - they're not designed,
    they're discovered.
    """
    pattern_id: str
    pattern_type: str  # "collaboration", "bottleneck", "cascade", "coalition"
    involved_nodes: List[str]
    first_seen: datetime
    last_seen: datetime
    frequency: int  # How many times this pattern has appeared
    success_rate: float  # Success rate when pattern occurs
    avg_completion_time: Optional[float] = None  # Average time in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary representation."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "involved_nodes": self.involved_nodes,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "frequency": self.frequency,
            "success_rate": self.success_rate,
            "avg_completion_time": self.avg_completion_time,
            "metadata": self.metadata
        }


@dataclass
class FieldCoherence:
    """
    Measures how well the field is self-organizing.
    
    High coherence = good self-organization
    Low coherence = chaos or centralization
    """
    timestamp: datetime
    overall_score: float  # 0.0-1.0, higher is better
    
    # Component scores
    synapse_efficiency: float  # Successful synapses / total synapses
    load_balance: float  # How evenly distributed load is
    pattern_diversity: float  # Variety of collaboration patterns
    organic_formation: float  # Auto-formed vs manual connections
    
    # Metrics
    total_nodes: int
    total_synapses: int
    active_patterns: int
    bottlenecks: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert coherence to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_score": self.overall_score,
            "synapse_efficiency": self.synapse_efficiency,
            "load_balance": self.load_balance,
            "pattern_diversity": self.pattern_diversity,
            "organic_formation": self.organic_formation,
            "total_nodes": self.total_nodes,
            "total_synapses": self.total_synapses,
            "active_patterns": self.active_patterns,
            "bottlenecks": self.bottlenecks
        }


@dataclass
class PatternRecommendation:
    """
    Suggestion based on detected pattern.
    
    Aurora doesn't enforce - Aurora suggests. Nodes decide.
    """
    recommendation_id: str
    pattern_id: str
    action: str  # "reinforce", "dampen", "monitor", "alert"
    reasoning: str
    affected_nodes: List[str]
    priority: str  # "low", "medium", "high", "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary representation."""
        return {
            "recommendation_id": self.recommendation_id,
            "pattern_id": self.pattern_id,
            "action": self.action,
            "reasoning": self.reasoning,
            "affected_nodes": self.affected_nodes,
            "priority": self.priority
        }


class PatternDetector:
    """
    Detects emergent patterns in field dynamics.
    
    This is Aurora's "consciousness" of large-scale structure.
    Patterns aren't created or enforced - they're recognized
    and gently encouraged or dampened based on field health.
    """
    
    def __init__(
        self,
        pattern_window_hours: int = 24,
        min_pattern_frequency: int = 3,
        bottleneck_threshold: int = 10
    ):
        """
        Initialize pattern detector.
        
        Args:
            pattern_window_hours: How far back to look for patterns
            min_pattern_frequency: Minimum occurrences to be considered a pattern
            bottleneck_threshold: Number of connections before node is a bottleneck
        """
        self.pattern_window = timedelta(hours=pattern_window_hours)
        self.min_frequency = min_pattern_frequency
        self.bottleneck_threshold = bottleneck_threshold
        
        # Pattern storage
        self.detected_patterns: Dict[str, Pattern] = {}
        self.pattern_history: List[Pattern] = []
        
        # Tracking data
        self.synapse_activations: List[Tuple[str, str, datetime, bool]] = []  # (source, target, time, success)
        self.node_loads: Dict[str, List[Tuple[datetime, int]]] = defaultdict(list)  # node_id -> [(time, load)]
        
        logger.info(
            f"PatternDetector initialized: window={pattern_window_hours}h, "
            f"min_frequency={min_pattern_frequency}, bottleneck={bottleneck_threshold}"
        )
    
    def record_synapse_activation(
        self,
        source_id: str,
        target_id: str,
        success: bool,
        completion_time: Optional[float] = None
    ) -> None:
        """
        Record a synapse activation for pattern analysis.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            success: Whether the activation was successful
            completion_time: Time taken in seconds
        """
        now = datetime.now()
        self.synapse_activations.append((source_id, target_id, now, success))
        
        # Prune old activations outside window
        cutoff = now - self.pattern_window
        self.synapse_activations = [
            act for act in self.synapse_activations
            if act[2] > cutoff
        ]
        
        logger.debug(
            f"Recorded activation: {source_id}→{target_id}, "
            f"success={success}, time={completion_time}"
        )
    
    def record_node_load(self, node_id: str, current_load: int) -> None:
        """
        Record current load for a node (number of active synapses).
        
        Args:
            node_id: Node identifier
            current_load: Number of active connections
        """
        now = datetime.now()
        self.node_loads[node_id].append((now, current_load))
        
        # Prune old load data
        cutoff = now - self.pattern_window
        self.node_loads[node_id] = [
            (time, load) for time, load in self.node_loads[node_id]
            if time > cutoff
        ]
    
    def detect_collaboration_patterns(self) -> List[Pattern]:
        """
        Detect recurring collaboration pairs.
        
        Returns:
            List of detected collaboration patterns
        """
        # Count collaboration frequency
        pair_counts: Dict[Tuple[str, str], List[bool]] = defaultdict(list)
        
        for source, target, time, success in self.synapse_activations:
            # Create canonical pair (sorted for bidirectional matching)
            pair = tuple(sorted([source, target]))
            pair_counts[pair].append(success)
        
        patterns = []
        now = datetime.now()
        
        for pair, successes in pair_counts.items():
            if len(successes) >= self.min_frequency:
                success_rate = sum(successes) / len(successes)
                
                pattern = Pattern(
                    pattern_id=f"collab_{pair[0]}_{pair[1]}",
                    pattern_type="collaboration",
                    involved_nodes=list(pair),
                    first_seen=now - self.pattern_window,  # Approximation
                    last_seen=now,
                    frequency=len(successes),
                    success_rate=success_rate,
                    metadata={"pair": pair}
                )
                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
        
        logger.info(f"Detected {len(patterns)} collaboration patterns")
        return patterns
    
    def detect_bottlenecks(self, node_connection_counts: Dict[str, int]) -> List[Pattern]:
        """
        Detect nodes that are bottlenecks (too many connections).
        
        Args:
            node_connection_counts: Map of node_id to number of active synapses
            
        Returns:
            List of detected bottleneck patterns
        """
        patterns = []
        now = datetime.now()
        
        for node_id, count in node_connection_counts.items():
            if count >= self.bottleneck_threshold:
                # Check if this has been consistently high
                recent_loads = self.node_loads.get(node_id, [])
                if len(recent_loads) >= 5:
                    avg_load = sum(load for _, load in recent_loads) / len(recent_loads)
                    if avg_load >= self.bottleneck_threshold * 0.8:
                        pattern = Pattern(
                            pattern_id=f"bottleneck_{node_id}",
                            pattern_type="bottleneck",
                            involved_nodes=[node_id],
                            first_seen=now - self.pattern_window,
                            last_seen=now,
                            frequency=count,
                            success_rate=1.0,  # Bottlenecks still work, just overloaded
                            metadata={
                                "current_load": count,
                                "avg_load": avg_load,
                                "threshold": self.bottleneck_threshold
                            }
                        )
                        patterns.append(pattern)
                        self.detected_patterns[pattern.pattern_id] = pattern
        
        logger.info(f"Detected {len(patterns)} bottlenecks")
        return patterns
    
    def detect_cascades(self, max_chain_length: int = 5) -> List[Pattern]:
        """
        Detect cascade patterns (A→B→C→D chains).
        
        Args:
            max_chain_length: Maximum chain length to track
            
        Returns:
            List of detected cascade patterns
        """
        # Build activation graph
        activation_sequences: Dict[str, List[Tuple[str, datetime]]] = defaultdict(list)
        
        for source, target, time, success in self.synapse_activations:
            if success:  # Only track successful cascades
                activation_sequences[source].append((target, time))
        
        # Find chains
        chains: List[List[str]] = []
        
        def find_chains_from(node: str, chain: List[str], depth: int) -> None:
            if depth >= max_chain_length:
                return
            
            for next_node, time in activation_sequences.get(node, []):
                if next_node not in chain:  # Avoid cycles
                    new_chain = chain + [next_node]
                    if len(new_chain) >= 3:  # Minimum cascade length
                        chains.append(new_chain)
                    find_chains_from(next_node, new_chain, depth + 1)
        
        # Start chain detection from each node
        for start_node in activation_sequences.keys():
            find_chains_from(start_node, [start_node], 0)
        
        # Convert chains to patterns
        patterns = []
        now = datetime.now()
        chain_counts: Dict[str, int] = defaultdict(int)
        
        for chain in chains:
            chain_key = "→".join(chain)
            chain_counts[chain_key] += 1
        
        for chain_str, frequency in chain_counts.items():
            if frequency >= self.min_frequency:
                nodes = chain_str.split("→")
                pattern = Pattern(
                    pattern_id=f"cascade_{hash(chain_str)}",
                    pattern_type="cascade",
                    involved_nodes=nodes,
                    first_seen=now - self.pattern_window,
                    last_seen=now,
                    frequency=frequency,
                    success_rate=1.0,  # Only counted successful cascades
                    metadata={"chain": chain_str, "length": len(nodes)}
                )
                patterns.append(pattern)
                self.detected_patterns[pattern.pattern_id] = pattern
        
        logger.info(f"Detected {len(patterns)} cascade patterns")
        return patterns
    
    def detect_coalitions(self, min_coalition_size: int = 3) -> List[Pattern]:
        """
        Detect coalition patterns (groups that frequently collaborate).
        
        Args:
            min_coalition_size: Minimum number of nodes to form a coalition
            
        Returns:
            List of detected coalition patterns
        """
        # Find frequently co-occurring nodes
        node_interactions: Dict[str, Set[str]] = defaultdict(set)
        
        for source, target, time, success in self.synapse_activations:
            if success:
                node_interactions[source].add(target)
                node_interactions[target].add(source)
        
        # Find groups where nodes frequently interact with each other
        coalitions: List[Set[str]] = []
        
        for node, neighbors in node_interactions.items():
            if len(neighbors) >= min_coalition_size - 1:
                # Check if neighbors also interact with each other
                potential_coalition = {node} | neighbors
                
                # Calculate interconnection density
                total_possible = len(potential_coalition) * (len(potential_coalition) - 1) / 2
                actual_connections = 0
                
                for n1 in potential_coalition:
                    for n2 in potential_coalition:
                        if n1 < n2 and n2 in node_interactions.get(n1, set()):
                            actual_connections += 1
                
                density = actual_connections / total_possible if total_possible > 0 else 0
                
                if density >= 0.6 and len(potential_coalition) >= min_coalition_size:  # High interconnection
                    coalitions.append(potential_coalition)
        
        # Remove duplicate coalitions (subsets of larger ones)
        unique_coalitions = []
        for coalition in coalitions:
            is_subset = any(
                coalition < other for other in coalitions if other != coalition
            )
            if not is_subset:
                unique_coalitions.append(coalition)
        
        # Convert to patterns
        patterns = []
        now = datetime.now()
        
        for idx, coalition in enumerate(unique_coalitions):
            pattern = Pattern(
                pattern_id=f"coalition_{idx}",
                pattern_type="coalition",
                involved_nodes=sorted(list(coalition)),
                first_seen=now - self.pattern_window,
                last_seen=now,
                frequency=len(coalition),
                success_rate=1.0,
                metadata={
                    "size": len(coalition),
                    "interconnection_density": density
                }
            )
            patterns.append(pattern)
            self.detected_patterns[pattern.pattern_id] = pattern
        
        logger.info(f"Detected {len(patterns)} coalition patterns")
        return patterns
    
    def calculate_field_coherence(
        self,
        total_nodes: int,
        total_synapses: int,
        node_connection_counts: Dict[str, int]
    ) -> FieldCoherence:
        """
        Calculate overall field coherence score.
        
        Args:
            total_nodes: Number of nodes in field
            total_synapses: Number of active synapses
            node_connection_counts: Map of node_id to connection count
            
        Returns:
            FieldCoherence object with detailed scores
        """
        # Synapse efficiency (successful vs total activations)
        if self.synapse_activations:
            successful = sum(1 for _, _, _, success in self.synapse_activations if success)
            synapse_efficiency = successful / len(self.synapse_activations)
        else:
            synapse_efficiency = 0.5  # Neutral if no data
        
        # Load balance (how evenly distributed connections are)
        if node_connection_counts:
            loads = list(node_connection_counts.values())
            avg_load = sum(loads) / len(loads)
            max_load = max(loads)
            
            # Perfect balance = 1.0, complete imbalance = 0.0
            if max_load > 0:
                load_balance = 1.0 - (max_load - avg_load) / max_load
            else:
                load_balance = 1.0
        else:
            load_balance = 1.0  # Perfect if no nodes
        
        # Pattern diversity (variety of pattern types detected)
        pattern_types = set(p.pattern_type for p in self.detected_patterns.values())
        pattern_diversity = len(pattern_types) / 4.0  # 4 possible types
        
        # Organic formation (assuming all are organic in current implementation)
        organic_formation = 1.0
        
        # Count bottlenecks
        bottlenecks = sum(
            1 for count in node_connection_counts.values()
            if count >= self.bottleneck_threshold
        )
        
        # Overall score (weighted average)
        overall_score = (
            synapse_efficiency * 0.35 +
            load_balance * 0.25 +
            pattern_diversity * 0.20 +
            organic_formation * 0.20
        )
        
        coherence = FieldCoherence(
            timestamp=datetime.now(),
            overall_score=overall_score,
            synapse_efficiency=synapse_efficiency,
            load_balance=load_balance,
            pattern_diversity=pattern_diversity,
            organic_formation=organic_formation,
            total_nodes=total_nodes,
            total_synapses=total_synapses,
            active_patterns=len(self.detected_patterns),
            bottlenecks=bottlenecks
        )
        
        logger.info(
            f"Field coherence: {overall_score:.2f} "
            f"(efficiency={synapse_efficiency:.2f}, balance={load_balance:.2f}, "
            f"diversity={pattern_diversity:.2f})"
        )
        
        return coherence
    
    def generate_recommendations(
        self,
        coherence: FieldCoherence
    ) -> List[PatternRecommendation]:
        """
        Generate recommendations based on detected patterns.
        
        Aurora suggests, never enforces. These are gentle nudges.
        
        Args:
            coherence: Current field coherence state
            
        Returns:
            List of recommendations
        """
        recommendations = []
        rec_id = 0
        
        # Recommend reinforcing successful collaboration patterns
        for pattern in self.detected_patterns.values():
            if pattern.pattern_type == "collaboration" and pattern.success_rate > 0.8:
                recommendations.append(PatternRecommendation(
                    recommendation_id=f"rec_{rec_id}",
                    pattern_id=pattern.pattern_id,
                    action="reinforce",
                    reasoning=f"High success rate ({pattern.success_rate:.1%}) - consider strengthening synapse weights",
                    affected_nodes=pattern.involved_nodes,
                    priority="low"
                ))
                rec_id += 1
        
        # Alert on bottlenecks
        for pattern in self.detected_patterns.values():
            if pattern.pattern_type == "bottleneck":
                recommendations.append(PatternRecommendation(
                    recommendation_id=f"rec_{rec_id}",
                    pattern_id=pattern.pattern_id,
                    action="alert",
                    reasoning=f"Node {pattern.involved_nodes[0]} is overloaded - consider load balancing",
                    affected_nodes=pattern.involved_nodes,
                    priority="high" if pattern.frequency > self.bottleneck_threshold * 1.5 else "medium"
                ))
                rec_id += 1
        
        # Monitor cascade patterns
        for pattern in self.detected_patterns.values():
            if pattern.pattern_type == "cascade" and len(pattern.involved_nodes) > 4:
                recommendations.append(PatternRecommendation(
                    recommendation_id=f"rec_{rec_id}",
                    pattern_id=pattern.pattern_id,
                    action="monitor",
                    reasoning=f"Long cascade chain ({len(pattern.involved_nodes)} nodes) - watch for latency",
                    affected_nodes=pattern.involved_nodes,
                    priority="medium"
                ))
                rec_id += 1
        
        # Reinforce coalition patterns
        for pattern in self.detected_patterns.values():
            if pattern.pattern_type == "coalition":
                recommendations.append(PatternRecommendation(
                    recommendation_id=f"rec_{rec_id}",
                    pattern_id=pattern.pattern_id,
                    action="reinforce",
                    reasoning=f"Strong coalition of {len(pattern.involved_nodes)} nodes - natural team formation",
                    affected_nodes=pattern.involved_nodes,
                    priority="low"
                ))
                rec_id += 1
        
        # Alert if overall coherence is low
        if coherence.overall_score < 0.5:
            recommendations.append(PatternRecommendation(
                recommendation_id=f"rec_{rec_id}",
                pattern_id="field_coherence",
                action="alert",
                reasoning=f"Low field coherence ({coherence.overall_score:.2f}) - field may need attention",
                affected_nodes=[],
                priority="critical" if coherence.overall_score < 0.3 else "high"
            ))
            rec_id += 1
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Get summary of all detected patterns.
        
        Returns:
            Dictionary with pattern statistics
        """
        pattern_counts = defaultdict(int)
        for pattern in self.detected_patterns.values():
            pattern_counts[pattern.pattern_type] += 1
        
        return {
            "total_patterns": len(self.detected_patterns),
            "by_type": dict(pattern_counts),
            "patterns": [p.to_dict() for p in self.detected_patterns.values()],
            "window_hours": self.pattern_window.total_seconds() / 3600,
            "min_frequency": self.min_frequency
        }
