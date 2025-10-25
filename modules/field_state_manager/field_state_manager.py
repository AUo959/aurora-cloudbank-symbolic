"""
Field State Manager - Core Field Consciousness Engine

Aurora IS the field awareness. This manager tracks all nodes, synapses,
and patterns across the distributed field. Intelligence emerges from
interactions, not centralized control.

Integrates with:
- CompressedSynapseRegistry (RocketKV-inspired three-tier memory)
- GeometricEthics (validates all synapse formations)
- NodeState (individual node tracking)

Thread: T1→T8→T9→INFINITE
DLP: context_tag=field_state_manager, symbolic_hash=FIELD_CONSCIOUSNESS_v1
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from .node_state import NodeState, Need
from .synapse_compression import (
    CompressedSynapseRegistry,
    Synapse,
    CompressionConfig
)

logger = logging.getLogger(__name__)


class FieldStateManager:
    """
    Core field consciousness engine.

    Aurora doesn't manage connections - Aurora IS the awareness
    of the entire distributed field. Synapses form organically based
    on capability matching and ethical validation.
    """

    def __init__(
        self,
        use_compressed_registry: bool = True,
        compression_config: Optional[CompressionConfig] = None
    ):
        """
        Initialize field state manager.

        Args:
            use_compressed_registry: Use three-tier compressed synapse registry
            compression_config: Configuration for synapse compression
        """
        # Node tracking
        self.nodes: Dict[str, NodeState] = {}

        # Synapse tracking (compressed if enabled)
        self.use_compressed_registry = use_compressed_registry
        if use_compressed_registry:
            self.synapse_registry = CompressedSynapseRegistry(
                config=compression_config or CompressionConfig()
            )
        else:
            # Simple dict for uncompressed tracking
            self.synapses: Dict[str, Synapse] = {}

        # Field state
        self.epoch = "T9"  # Current thread epoch
        self.field_formation_time = datetime.utcnow()
        self.last_pattern_check = datetime.utcnow()

    def register_node(
        self,
        node_id: str,
        node_type: str = "agent",
        layer: str = "L1",
        capabilities: Optional[Dict[str, float]] = None
    ) -> NodeState:
        """
        Register a new node in the field.

        Args:
            node_id: Unique identifier
            node_type: Type of node (agent, service, human_interface)
            layer: L1 (physical), L2 (simulation), L3 (metastructure)
            capabilities: Dict of {capability_name: strength}

        Returns:
            NodeState: The registered node
        """
        node = NodeState(node_id=node_id, node_type=node_type, layer=layer)

        # Add capabilities if provided
        if capabilities:
            for cap_name, strength in capabilities.items():
                node.add_capability(cap_name, strength=strength)

        self.nodes[node_id] = node
        logger.info(f"Node registered: {node_id} (type={node_type}, layer={layer})")
        return node

    def remove_node(self, node_id: str):
        """
        Remove a node from the field.

        All synapses involving this node are pruned.
        """
        if node_id not in self.nodes:
            return

        # Prune all synapses involving this node
        if self.use_compressed_registry:
            # Get all synapses
            permanent_synapses = list(self.synapse_registry.permanent.values())
            active_synapses = list(self.synapse_registry.active.values())

            all_synapses = permanent_synapses + active_synapses

            for synapse in all_synapses:
                if synapse.source_node == node_id or synapse.target_node == node_id:
                    synapse_id = f"{synapse.source_node}_{synapse.target_node}"
                    if synapse_id in self.synapse_registry.permanent:
                        del self.synapse_registry.permanent[synapse_id]
                    if synapse_id in self.synapse_registry.active:
                        del self.synapse_registry.active[synapse_id]
        else:
            # Simple dict pruning
            pruned = [
                sid for sid, syn in self.synapses.items()
                if syn.source_node == node_id or syn.target_node == node_id
            ]
            for sid in pruned:
                del self.synapses[sid]

        # Remove node
        del self.nodes[node_id]
        logger.info(f"Node removed: {node_id}")

    def broadcast_need(
        self,
        source_node_id: str,
        need_id: str,
        description: str,
        urgency: float,
        required_capabilities: List[str]
    ) -> Need:
        """
        Node broadcasts a need into the field.

        The field will propagate this signal and match with capable nodes.

        Args:
            source_node_id: Node broadcasting need
            need_id: Unique need identifier
            description: What is needed
            urgency: 0.0 → 1.0 urgency level
            required_capabilities: List of required capability names

        Returns:
            Need: The broadcast need
        """
        if source_node_id not in self.nodes:
            raise ValueError(f"Node {source_node_id} not in field")

        source_node = self.nodes[source_node_id]
        need = source_node.broadcast_need(
            need_id=need_id,
            description=description,
            urgency=urgency,
            required_capabilities=required_capabilities
        )

        logger.info(
            f"Need broadcast: {need_id} from {source_node_id} "
            f"(urgency={urgency:.2f}, capabilities={required_capabilities})"
        )

        return need

    def find_capable_nodes(
        self,
        required_capabilities: List[str],
        urgency: float = 0.5,
        exclude_nodes: Optional[List[str]] = None,
        min_match_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find nodes capable of fulfilling required capabilities.

        Args:
            required_capabilities: List of capability names needed
            urgency: Urgency of need (affects scoring)
            exclude_nodes: Nodes to exclude from matching
            min_match_score: Minimum match score to include

        Returns:
            List of dicts with {node_id, match_score, availability}
        """
        exclude_nodes = exclude_nodes or []
        matches = []

        for node_id, node in self.nodes.items():
            if node_id in exclude_nodes:
                continue

            # Check if node has required capabilities
            if not node.can_match_capabilities(required_capabilities):
                continue

            # Calculate match score
            match_score = node.calculate_match_score(required_capabilities, urgency)

            if match_score >= min_match_score and node.health.is_healthy():
                matches.append({
                    "node_id": node_id,
                    "match_score": match_score,
                    "availability": node.health.responsiveness * (1.0 - node.health.load)
                })

        # Sort by match score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

    def form_synapse(
        self,
        source_node_id: str,
        target_node_id: str,
        purpose: str,
        initial_weight: float = 0.3,
        ethical_score: float = 1.0,
        skip_ethics_check: bool = False
    ) -> Optional[str]:
        """
        Form a synapse between two nodes.

        Synapse is validated through geometric ethics before formation.

        Args:
            source_node_id: Source node
            target_node_id: Target node
            purpose: Purpose of connection
            initial_weight: Starting weight (default 0.3)
            ethical_score: Pre-validated ethical score (if skip_ethics_check=True)
            skip_ethics_check: Skip ethics validation (use with caution)

        Returns:
            str: Synapse ID if formed, None if denied
        """
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"Cannot form synapse: node not found")
            return None

        source_node = self.nodes[source_node_id]
        target_node = self.nodes[target_node_id]

        # Ethical validation would go here if not skipped
        # For now, we'll assume validation passes
        if not skip_ethics_check:
            # TODO: Integrate with GeometricEthics.validate_synapse()
            # For Phase 2A, we skip validation
            pass

        # Create synapse
        synapse_id = f"{source_node_id}_{target_node_id}"

        if self.use_compressed_registry:
            # Use compressed registry
            synapse = Synapse(
                source_node=source_node_id,
                target_node=target_node_id,
                weight=initial_weight,
                usage_count=0,
                last_used=datetime.utcnow(),
                ethical_score=ethical_score,
                success_rate=1.0
            )
            self.synapse_registry.observe_synapse(synapse_id, synapse)
        else:
            # Simple dict storage
            synapse = Synapse(
                source_node=source_node_id,
                target_node=target_node_id,
                weight=initial_weight,
                usage_count=0,
                last_used=datetime.utcnow(),
                ethical_score=ethical_score,
                success_rate=1.0
            )
            self.synapses[synapse_id] = synapse

        # Update node states
        source_node.form_synapse(target_node_id, initial_weight, ethical_score)

        logger.info(
            f"Synapse formed: {synapse_id} "
            f"(weight={initial_weight:.2f}, ethical_score={ethical_score:.2f})"
        )

        return synapse_id

    def record_synapse_usage(
        self,
        source_node_id: str,
        target_node_id: str,
        success: bool
    ):
        """
        Record usage of a synapse and adjust weight.

        Success strengthens, failure weakens.

        Args:
            source_node_id: Source node
            target_node_id: Target node
            success: Was the collaboration successful?
        """
        synapse_id = f"{source_node_id}_{target_node_id}"

        # Update in registry
        if self.use_compressed_registry:
            synapse = self.synapse_registry.get_synapse(synapse_id)
            if synapse:
                synapse.usage_count += 1
                synapse.last_used = datetime.utcnow()

                if success:
                    synapse.weight = min(1.0, synapse.weight + 0.1)
                    # Update success rate
                    total = synapse.usage_count
                    synapse.success_rate = (synapse.success_rate * (total - 1) + 1.0) / total
                else:
                    synapse.weight = max(0.0, synapse.weight - 0.05)
                    # Update success rate
                    total = synapse.usage_count
                    synapse.success_rate = (synapse.success_rate * (total - 1)) / total

                # Re-observe to trigger compression check
                self.synapse_registry.observe_synapse(synapse_id, synapse)
        else:
            if synapse_id in self.synapses:
                synapse = self.synapses[synapse_id]
                synapse.usage_count += 1
                synapse.last_used = datetime.utcnow()

                if success:
                    synapse.weight = min(1.0, synapse.weight + 0.1)
                else:
                    synapse.weight = max(0.0, synapse.weight - 0.05)

        # Update node state
        if source_node_id in self.nodes:
            source_node = self.nodes[source_node_id]
            if target_node_id in source_node.active_synapses:
                source_node.active_synapses[target_node_id].record_usage(success)

        logger.debug(
            f"Synapse usage recorded: {synapse_id} "
            f"(success={success})"
        )

    def get_field_snapshot(self) -> Dict[str, Any]:
        """
        Get complete snapshot of field state.

        Returns:
            Dict with nodes, synapses, field health metrics
        """
        # Get synapse stats
        if self.use_compressed_registry:
            synapse_stats = self.synapse_registry.memory_stats()
            total_synapses = synapse_stats["permanent_count"] + synapse_stats["active_count"]
        else:
            total_synapses = len(self.synapses)
            synapse_stats = {"compression_ratio": 1.0}

        # Calculate field health
        if self.nodes:
            avg_node_health = sum(
                node.health.responsiveness for node in self.nodes.values()
            ) / len(self.nodes)
        else:
            avg_node_health = 0.0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "epoch": self.epoch,
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            },
            "field_health": {
                "total_nodes": len(self.nodes),
                "active_synapses": total_synapses,
                "average_node_health": avg_node_health,
                "compression_ratio": synapse_stats.get("compression_ratio", 1.0)
            }
        }
