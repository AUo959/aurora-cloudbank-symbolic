"""
Quantum Forge Entanglement Network v1.0

Multi-agent quantum entanglement for zero-latency coordination.
Creates quantum-correlated agent clusters for distributed intelligence.

Features:
- Agent-agent entanglement creation
- Entanglement network topology management
- Collective state updates via quantum correlation
- Network health monitoring
- Automatic entanglement refresh

T1: QUANTUM_ENTANGLEMENT_v1.0
SRB: MULTI_AGENT_COORDINATION
DLP: context_tag=qforge_entanglement, symbolic_hash=QFENT_v1

Author: Aurora CloudBank Team
Version: 1.0.0
Date: 2025-11-13
Ethics: GUMAS_Thermax, Entanglement_Safe
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from modules.quantum_forge.quantum_forge_v2 import QuantumAgent, QuantumForge
from modules.quantum_forge.quantum_integration import QuantumForgeIntegration
from modules.nexus.quantum.quantum_bridge import QuantumSymbolicBridge

logger = logging.getLogger(__name__)


@dataclass
class EntanglementLink:
    """Represents quantum entanglement between two agents"""
    link_id: str
    agent_1_id: str
    agent_2_id: str
    entanglement_strength: float  # 0.0 - 1.0
    bell_fidelity: float
    created_at: float
    last_refresh: float
    correlation_history: List[float] = field(default_factory=list)
    
    def get_age(self) -> float:
        """Get entanglement age in seconds"""
        return time.time() - self.created_at
        
    def needs_refresh(self, max_age: float = 600.0) -> bool:
        """Check if entanglement needs refresh"""
        return self.get_age() > max_age or self.entanglement_strength < 0.5
        
    # Backward compatibility properties for tests
    @property
    def agent1_id(self) -> str:
        """Alias for agent_1_id"""
        return self.agent_1_id

    @property
    def agent2_id(self) -> str:
        """Alias for agent_2_id"""
        return self.agent_2_id
        
    @property
    def correlation(self) -> float:
        """Alias for entanglement_strength"""
        return self.entanglement_strength


@dataclass
class EntanglementCluster:
    """Represents a cluster of mutually entangled agents"""
    cluster_id: str
    agent_ids: Set[str]
    topology: str  # "star", "mesh", "ring", "tree"
    collective_coherence: float
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def link_count(self) -> int:
        """Calculate expected number of entanglement links based on topology"""
        n = len(self.agent_ids)
        
        # Handle both NetworkTopology enum and string values
        topology_str = self.topology
        if hasattr(self.topology, 'value'):
            topology_str = self.topology.value
            
        if topology_str == "mesh":
            # Fully connected: n*(n-1)/2 links
            return n * (n - 1) // 2
        elif topology_str == "star":
            # Hub-and-spoke: n-1 links (hub to each spoke)
            return n - 1
        elif topology_str == "ring":
            # Circular: n links (each agent to next)
            return n
        elif topology_str == "tree":
            # Binary tree: n-1 links (tree structure)
            return n - 1
        else:
            return 0


class EntanglementNetwork:
    """
    Manages quantum entanglement network across multiple agents
    
    Creates and maintains entanglement links for zero-latency
    coordination and collective intelligence emergence.
    """
    
    def __init__(
        self,
        forge: Optional[QuantumForge] = None,
        integration: Optional[QuantumForgeIntegration] = None,
        bridge: Optional[QuantumSymbolicBridge] = None
    ):
        """
        Initialize entanglement network
        
        Args:
            forge: QuantumForge instance
            integration: QuantumForgeIntegration instance
            bridge: QuantumSymbolicBridge instance
        """
        self.forge = forge or QuantumForge()
        
        # Initialize integration first (it may create its own bridge)
        self.integration = integration or QuantumForgeIntegration(forge=self.forge)
        
        # Use provided bridge, or integration's bridge, or create new one
        # Priority: provided bridge > integration's bridge > new bridge
        if bridge:
            self.bridge = bridge
        elif hasattr(self.integration, 'bridge') and self.integration.bridge:
            self.bridge = self.integration.bridge
        else:
            self.bridge = QuantumSymbolicBridge()
        
        # Track entanglement links
        self.entanglement_links: Dict[str, EntanglementLink] = {}
        
        # Track clusters
        self.clusters: Dict[str, EntanglementCluster] = {}
        
        # Network metrics
        self.metrics = {
            "total_entanglements": 0,
            "active_entanglements": 0,
            "total_clusters": 0,
            "average_entanglement_strength": 0.0,
            "total_state_updates": 0
        }
        
        logger.info("🕸️  Entanglement Network initialized")
    
    @property
    def links(self) -> Dict[str, EntanglementLink]:
        """Backward compatibility property for entanglement links"""
        return self.entanglement_links
        
    def entangle_agents(
        self,
        agent_1_id,  # Union[str, QuantumAgent]
        agent_2_id,  # Union[str, QuantumAgent]
        strength: float = 0.95
    ) -> EntanglementLink:
        """
        Create quantum entanglement between two agents

        Args:
            agent_1_id: First agent ID (str) or QuantumAgent object
            agent_2_id: Second agent ID (str) or QuantumAgent object
            strength: Target entanglement strength (0.0-1.0)

        Returns:
            EntanglementLink representing the connection

        Raises:
            ValueError: If agents don't exist or already entangled
        """
        # Extract agent IDs if QuantumAgent objects are passed
        if hasattr(agent_1_id, 'agent_id'):
            # It's a QuantumAgent object - auto-register it and extract ID
            self.forge.agents[agent_1_id.agent_id] = agent_1_id
            agent_1_id = agent_1_id.agent_id
        if hasattr(agent_2_id, 'agent_id'):
            # It's a QuantumAgent object - auto-register it and extract ID
            self.forge.agents[agent_2_id.agent_id] = agent_2_id
            agent_2_id = agent_2_id.agent_id
            
        # Validate agents exist
        if agent_1_id not in self.forge.agents:
            raise ValueError(f"Agent not found: {agent_1_id}")
        if agent_2_id not in self.forge.agents:
            raise ValueError(f"Agent not found: {agent_2_id}")
            
        # Check if already entangled
        existing_link = self._find_link(agent_1_id, agent_2_id)
        if existing_link:
            logger.info(f"⚠️  Agents already entangled, refreshing: {existing_link.link_id}")
            return self.refresh_entanglement(existing_link.link_id)
        
        logger.info(f"🔗 Creating entanglement: {agent_1_id[:8]}... ↔ {agent_2_id[:8]}...")
        
        # Convert both agents to quantum states
        agent_1_qstate = self.integration.agent_to_quantum(self.forge.agents[agent_1_id])
        agent_2_qstate = self.integration.agent_to_quantum(self.forge.agents[agent_2_id])
        
        # Create entanglement via bridge
        entanglement_data = self.bridge.create_entanglement(
            agent_1_qstate.quantum_state.state_id,
            agent_2_qstate.quantum_state.state_id
        )
        
        # Create entanglement link
        link_id = f"ENT-{agent_1_id[:6]}-{agent_2_id[:6]}-{int(time.time())}"
        
        link = EntanglementLink(
            link_id=link_id,
            agent_1_id=agent_1_id,
            agent_2_id=agent_2_id,
            entanglement_strength=min(strength, entanglement_data["bell_fidelity"]),
            bell_fidelity=entanglement_data["bell_fidelity"],
            created_at=time.time(),
            last_refresh=time.time()
        )
        
        # Store link
        self.entanglement_links[link_id] = link
        
        # Update metrics
        self.metrics["total_entanglements"] += 1
        self.metrics["active_entanglements"] = len(self.entanglement_links)
        self._update_average_strength()
        
        logger.info(
            f"✅ Entanglement created: {link_id} "
            f"(strength: {link.entanglement_strength:.4f}, "
            f"bell_fidelity: {link.bell_fidelity:.4f})"
        )
        
        return link
        
    def propagate_state_update(
        self,
        source_agent_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Propagate state update across entangled agents
        
        When one agent changes, all entangled agents receive correlated updates.
        
        Args:
            source_agent_id: Agent initiating the update
            update_data: Update information to propagate
            
        Returns:
            Dict with propagation results
        """
        logger.info(f"📡 Propagating state update from {source_agent_id[:8]}...")
        
        # Find all entangled agents
        entangled_agents = self._get_entangled_agents(source_agent_id)
        
        if not entangled_agents:
            logger.info("   No entangled agents found")
            return {
                "source": source_agent_id,
                "affected_agents": [],
                "propagation_count": 0
            }
        
        # Propagate to entangled agents
        affected = []
        for target_id, link in entangled_agents:
            # Calculate correlation strength
            correlation = link.entanglement_strength
            
            # Apply correlated update (scaled by entanglement strength)
            if target_id in self.forge.agents:
                target_agent = self.forge.agents[target_id]
                
                # Update intent alignment (correlated with source)
                if HAS_NUMPY:
                    noise = np.random.randn() * 0.01 * correlation
                else:
                    import random
                    noise = random.gauss(0, 0.01) * correlation
                    
                target_agent.intent_alignment = min(
                    1.0,
                    max(0.0, target_agent.intent_alignment + noise)
                )
                
                affected.append({
                    "agent_id": target_id,
                    "correlation": correlation,
                    "new_alignment": target_agent.intent_alignment
                })
                
                # Track correlation
                link.correlation_history.append(correlation)
                if len(link.correlation_history) > 100:
                    link.correlation_history = link.correlation_history[-100:]
        
        # Update metrics
        self.metrics["total_state_updates"] += 1
        
        logger.info(
            f"✅ State propagated to {len(affected)} entangled agents "
            f"(avg correlation: {np.mean([a['correlation'] for a in affected]):.4f})"
            if HAS_NUMPY else
            f"✅ State propagated to {len(affected)} entangled agents"
        )
        
        return {
            "source": source_agent_id,
            "affected_agents": affected,
            "propagation_count": len(affected),
            "update_data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def create_cluster(
        self,
        agent_ids: List[str],
        topology: str = "mesh",
        cluster_id: Optional[str] = None
    ) -> EntanglementCluster:
        """
        Create entangled cluster with specified topology
        
        Args:
            agent_ids: List of agent IDs to include
            topology: "star", "mesh", "ring", or "tree"
            cluster_id: Optional custom cluster ID
            
        Returns:
            EntanglementCluster representing the group
        """
        if len(agent_ids) < 2:
            raise ValueError("Cluster requires at least 2 agents")
            
        cluster_id = cluster_id or f"CLUSTER-{int(time.time())}"
        
        # Handle both NetworkTopology enum and string values
        if hasattr(topology, 'value'):
            topology_str = topology.value
        else:
            topology_str = topology
        
        logger.info(
            f"🌐 Creating {topology} cluster: {cluster_id} "
            f"({len(agent_ids)} agents)"
        )
        
        # Create entanglements based on topology
        if topology_str == "mesh":
            # Fully connected: entangle all pairs
            for i, agent_1 in enumerate(agent_ids):
                for agent_2 in agent_ids[i+1:]:
                    self.entangle_agents(agent_1, agent_2)
                    
        elif topology_str == "star":
            # Hub-and-spoke: entangle first agent with all others
            hub = agent_ids[0]
            for agent in agent_ids[1:]:
                self.entangle_agents(hub, agent)
                
        elif topology_str == "ring":
            # Circular: entangle sequential pairs
            for i in range(len(agent_ids)):
                agent_1 = agent_ids[i]
                agent_2 = agent_ids[(i + 1) % len(agent_ids)]
                self.entangle_agents(agent_1, agent_2)
                
        elif topology_str == "tree":
            # Binary tree: entangle hierarchically
            for i in range(len(agent_ids)):
                left_child = 2 * i + 1
                right_child = 2 * i + 2
                if left_child < len(agent_ids):
                    self.entangle_agents(agent_ids[i], agent_ids[left_child])
                if right_child < len(agent_ids):
                    self.entangle_agents(agent_ids[i], agent_ids[right_child])
        else:
            raise ValueError(f"Unknown topology: {topology_str}")
        
        # Calculate collective coherence
        collective_coherence = self._calculate_cluster_coherence(agent_ids)
        
        # Create cluster
        cluster = EntanglementCluster(
            cluster_id=cluster_id,
            agent_ids=set(agent_ids),
            topology=topology,
            collective_coherence=collective_coherence,
            created_at=time.time()
        )
        
        self.clusters[cluster_id] = cluster
        self.metrics["total_clusters"] += 1
        
        logger.info(
            f"✅ Cluster created: {cluster_id} "
            f"(coherence: {collective_coherence:.4f})"
        )
        
        return cluster
        
    def refresh_entanglement(self, link_id: str) -> EntanglementLink:
        """
        Refresh entanglement to restore strength
        
        Args:
            link_id: Entanglement link ID to refresh
            
        Returns:
            Refreshed EntanglementLink
        """
        if link_id not in self.entanglement_links:
            raise ValueError(f"Entanglement not found: {link_id}")
            
        link = self.entanglement_links[link_id]
        
        logger.info(f"🔄 Refreshing entanglement: {link_id}")
        
        # Refresh quantum states of both agents
        self.integration.refresh_coherence(link.agent_1_id)
        self.integration.refresh_coherence(link.agent_2_id)
        
        # Recreate entanglement
        agent_1_qstate = self.integration.agent_quantum_states[link.agent_1_id]
        agent_2_qstate = self.integration.agent_quantum_states[link.agent_2_id]
        
        new_entanglement = self.bridge.create_entanglement(
            agent_1_qstate.quantum_state.state_id,
            agent_2_qstate.quantum_state.state_id
        )
        
        # Update link
        link.entanglement_strength = new_entanglement["bell_fidelity"]
        link.bell_fidelity = new_entanglement["bell_fidelity"]
        link.last_refresh = time.time()
        
        self._update_average_strength()
        
        logger.info(
            f"✅ Entanglement refreshed: {link_id} "
            f"(new strength: {link.entanglement_strength:.4f})"
        )
        
        return link
        
    def monitor_network_health(self) -> Dict[str, Any]:
        """
        Monitor overall network health and return diagnostics
        
        Returns:
            Dict with health metrics and recommendations
        """
        total_links = len(self.entanglement_links)
        weak_links = [
            link for link in self.entanglement_links.values()
            if link.entanglement_strength < 0.7
        ]
        expired_links = [
            link for link in self.entanglement_links.values()
            if link.needs_refresh()
        ]
        
        health = {
            "total_links": total_links,
            "weak_links": len(weak_links),
            "expired_links": len(expired_links),
            "total_clusters": len(self.clusters),
            "average_strength": self.metrics["average_entanglement_strength"],
            "recommendations": []
        }
        
        # Generate recommendations
        if len(weak_links) > total_links * 0.3:
            health["recommendations"].append(
                "⚠️  >30% of links are weak. Consider network-wide refresh."
            )
            
        if len(expired_links) > 0:
            health["recommendations"].append(
                f"🔄 {len(expired_links)} links need refresh"
            )
            
        if health["average_strength"] < 0.8:
            health["recommendations"].append(
                "📉 Average strength below 0.8. Network performance may be degraded."
            )
        
        return health
        
    def get_network_topology(self) -> Dict[str, Any]:
        """Get complete network topology visualization data"""
        nodes = []
        edges = []
        
        # Collect all unique agents
        agent_ids = set()
        for link in self.entanglement_links.values():
            agent_ids.add(link.agent_1_id)
            agent_ids.add(link.agent_2_id)
        
        # Create nodes
        for agent_id in agent_ids:
            if agent_id in self.forge.agents:
                agent = self.forge.agents[agent_id]
                nodes.append({
                    "id": agent_id,
                    "label": agent_id[:8],
                    "intent_alignment": agent.intent_alignment,
                    "constellation_bindings": agent.constellation_bindings
                })
        
        # Create edges
        for link in self.entanglement_links.values():
            edges.append({
                "source": link.agent_1_id,
                "target": link.agent_2_id,
                "strength": link.entanglement_strength,
                "fidelity": link.bell_fidelity,
                "age": link.get_age()
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "clusters": [
                {
                    "id": cluster_id,
                    "topology": cluster.topology,
                    "size": len(cluster.agent_ids),
                    "coherence": cluster.collective_coherence
                }
                for cluster_id, cluster in self.clusters.items()
            ],
            "metrics": self.metrics
        }
        
    def export_network_manifest(self) -> Dict[str, Any]:
        """Export complete network manifest"""
        manifest = {
            "manifest_version": "1.0.0",
            "component": "entanglement_network",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.metrics,
            "links": [
                {
                    "link_id": link.link_id,
                    "agents": [link.agent_1_id, link.agent_2_id],
                    "strength": link.entanglement_strength,
                    "age": link.get_age()
                }
                for link in self.entanglement_links.values()
            ],
            "clusters": [
                {
                    "cluster_id": cluster_id,
                    "agent_count": len(cluster.agent_ids),
                    "topology": cluster.topology,
                    "coherence": cluster.collective_coherence
                }
                for cluster_id, cluster in self.clusters.items()
            ],
            "health": self.monitor_network_health(),
            "dlp_tag": "qforge_entanglement_v1"
        }
        
        # Seal manifest
        manifest_hash = hashlib.sha256(
            json.dumps(manifest, sort_keys=True, default=str).encode()
        ).hexdigest()
        manifest["seal"] = manifest_hash
        
        return manifest
        
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _find_link(self, agent_1_id: str, agent_2_id: str) -> Optional[EntanglementLink]:
        """Find existing link between two agents"""
        for link in self.entanglement_links.values():
            if (link.agent_1_id == agent_1_id and link.agent_2_id == agent_2_id) or \
               (link.agent_1_id == agent_2_id and link.agent_2_id == agent_1_id):
                return link
        return None
        
    def _get_entangled_agents(self, agent_id: str) -> List[Tuple[str, EntanglementLink]]:
        """Get all agents entangled with given agent"""
        entangled = []
        for link in self.entanglement_links.values():
            if link.agent_1_id == agent_id:
                entangled.append((link.agent_2_id, link))
            elif link.agent_2_id == agent_id:
                entangled.append((link.agent_1_id, link))
        return entangled
        
    def _calculate_cluster_coherence(self, agent_ids: List[str]) -> float:
        """Calculate collective coherence for cluster"""
        if not agent_ids:
            return 0.0
            
        # Average intent alignment of all agents
        alignments = []
        for agent_id in agent_ids:
            if agent_id in self.forge.agents:
                alignments.append(self.forge.agents[agent_id].intent_alignment)
        
        if not alignments:
            return 0.0
            
        if HAS_NUMPY:
            return float(np.mean(alignments))
        else:
            return sum(alignments) / len(alignments)
        
    def _update_average_strength(self):
        """Update average entanglement strength metric"""
        if not self.entanglement_links:
            self.metrics["average_entanglement_strength"] = 0.0
            return
            
        strengths = [link.entanglement_strength for link in self.entanglement_links.values()]
        
        if HAS_NUMPY:
            avg = float(np.mean(strengths))
        else:
            avg = sum(strengths) / len(strengths)
            
        self.metrics["average_entanglement_strength"] = avg


# ============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

_entanglement_network: Optional[EntanglementNetwork] = None


def get_entanglement_network(**kwargs) -> EntanglementNetwork:
    """Get or create global entanglement network instance"""
    global _entanglement_network
    
    if _entanglement_network is None:
        _entanglement_network = EntanglementNetwork(**kwargs)
        
    return _entanglement_network


def reset_entanglement_network():
    """Reset global entanglement network instance"""
    global _entanglement_network
    _entanglement_network = None
