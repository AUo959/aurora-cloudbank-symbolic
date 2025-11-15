"""
Quantum Forge v3.0 Module - Complete Quantum-Symbolic System

Advanced quantum-symbolic agent generation with full quantum computing integration,
entanglement networks, memory coherence, and system-wide orchestration.

Features (v3.0):
- Quantum Bridge Integration: Agent ↔ quantum state conversion (99% fidelity)
- Entanglement Networks: Zero-latency multi-agent coordination
- Quantum Memory Enhancement: Self-healing memory with coherence tracking
- System Flow Orchestration: Adaptive system breathing across all modules
- Ethics-Aware Operations: Quantum-level safety enforcement
- Topology Optimization: Quantum-optimal architecture mapping
- Joy-Driven Evolution: Genetic algorithms with creativity emergence

T1: QUANTUM_FORGE_INIT_v3.0
SRB: MODULE_BOUNDARY_QUANTUM_ENHANCED
DLP: context_tag=qf_init_v3, symbolic_hash=QF_INIT_v3
"""

from enum import Enum


class NetworkTopology(Enum):
    """Network topology types for quantum entanglement networks"""
    STAR = "star"
    MESH = "mesh"
    RING = "ring"
    TREE = "tree"


# Core v2.0 components
from modules.quantum_forge.quantum_forge_v2 import (
    QuantumForge,
    GUMAS_Thermax,
    Aurora_Core_Flowstate,
    EthicsLevel,
    FlowstateMode,
    InterventionType,
    SymbolicMemoryNode,
    QuantumAgent,
    QuantumState,
    SymbolicLayer
)

# v3.0 Quantum Integration
from modules.quantum_forge.quantum_integration import (
    QuantumForgeIntegration,
    AgentQuantumState,
    QuantumIntegrationError,
    get_quantum_integration,
    reset_quantum_integration
)

# v3.0 Entanglement Networks
from modules.quantum_forge.entanglement_network import (
    EntanglementNetwork,
    EntanglementLink,
    EntanglementCluster,
    get_entanglement_network,
    reset_entanglement_network
)

# v3.0 Quantum Memory Enhancement
from modules.quantum_forge.quantum_memory_enhancer import (
    QuantumMemoryEnhancer,
    QuantumMemoryMetadata,
    get_quantum_memory_enhancer,
    reset_quantum_memory_enhancer
)

# Aliases for backward compatibility
get_memory_enhancer = get_quantum_memory_enhancer

# System Flow Orchestration (Phase 4)
from modules.quantum_forge.system_flow_orchestrator import (
    SystemFlowOrchestrator,
    ModuleFlowState,
    SystemPhase,
    SystemFlowMetrics,
    get_system_flow_orchestrator,
)

# Aliases for backward compatibility
get_system_orchestrator = get_system_flow_orchestrator

# Ethics-Aware Quantum Operations (Phase 5)
from modules.quantum_forge.ethics_quantum_gates import (
    EthicsAwareQuantumGate,
    GateRiskLevel,
    get_ethics_quantum_gate,
)

# Constellation Topology Mapping (Phase 6)
from modules.quantum_forge.constellation_topology_mapper import (
    ConstellationTopologyMapper,
    ModuleNode,
    ModuleType,
    QuantumLink,
    TopologyMapping,
    TopologyMetric,
    get_topology_mapper,
)

# NetworkTopology enum defined above - no need for alias

# Joy-Infused Evolution (Phase 7)
from modules.quantum_forge.joy_evolution_engine import (
    JoyEvolutionEngine,
    AgentGenome,
    EvolutionParameters,
    GenerationStats,
    get_joy_evolution_engine,
)

__version__ = "3.0.0"

__all__ = [
    # Core v2.0
    "QuantumForge",
    "GUMAS_Thermax",
    "Aurora_Core_Flowstate",
    "EthicsLevel",
    "FlowstateMode",
    "InterventionType",
    "SymbolicMemoryNode",
    "QuantumAgent",
    "QuantumState",
    "SymbolicLayer",
    
    # Quantum Integration
    "QuantumForgeIntegration",
    "AgentQuantumState",
    "QuantumIntegrationError",
    "get_quantum_integration",
    "reset_quantum_integration",
    
    # Entanglement Networks
    "EntanglementNetwork",
    "EntanglementLink",
    "EntanglementCluster",
    "get_entanglement_network",
    "reset_entanglement_network",
    
    # Quantum Memory
    "QuantumMemoryEnhancer",
    "QuantumMemoryMetadata",
    "get_quantum_memory_enhancer",
    "reset_quantum_memory_enhancer",
    "get_memory_enhancer",  # Alias
    
    
    # System Orchestration
    "SystemFlowOrchestrator",
    "SystemPhase",
    "ModuleFlowState",
    "SystemFlowMetrics",
    "get_system_flow_orchestrator",
    "get_system_orchestrator",  # Alias
    
    # Ethics Operations
    "EthicsAwareQuantumGate",
    "GateRiskLevel",
    "get_ethics_quantum_gate",
    
    # Constellation Topology
    "ConstellationTopologyMapper",
    "ModuleNode",
    "ModuleType",
    "QuantumLink",
    "TopologyMapping",
    "TopologyMetric",
    "get_topology_mapper",
    "NetworkTopology",  # Alias
    
    # Joy Evolution
    "JoyEvolutionEngine",
    "AgentGenome",
    "EvolutionParameters",
    "GenerationStats",
    "get_joy_evolution_engine",
]

__version__ = "3.0.0"
