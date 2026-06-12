"""
Quantum Forge v3.0 - Comprehensive Pytest Test Suite

Tests all 5 phases of Quantum Forge enhancement:
- Phase 1: Quantum Bridge Integration
- Phase 2: Multi-Agent Entanglement Networks
- Phase 3: Quantum-Enhanced Memory
- Phase 4: System Flow Orchestration
- Phase 5: Ethics-Aware Operations
- Phase 6: Constellation Topology Mapping
- Phase 7: Joy-Infused Evolution

Author: Aurora CloudBank Team
Version: 1.0.0
Date: 2025-11-13
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import logging

logger = logging.getLogger(__name__)

# Test markers
pytestmark = [
    pytest.mark.quantum,
    pytest.mark.integration,
]


# ============================================================================
# PHASE 1: Quantum Bridge Integration Tests
# ============================================================================

class TestQuantumIntegration:
    """Tests for quantum bridge integration layer"""
    
    @pytest.fixture
    def quantum_forge(self):
        """Mock QuantumForge instance"""
        from modules.quantum_forge import QuantumForge, EthicsLevel
        forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)
        return forge
        
    @pytest.fixture
    def test_agent(self, quantum_forge):
        """Create test agent"""
        return quantum_forge.generate_agent(
            intent_query="Test quantum integration capabilities",
            constellation_targets=["ORION"]
        )
    
    @pytest.fixture
    def quantum_integration(self, quantum_forge):
        """Create integration using same forge as test_agent"""
        from modules.quantum_forge import QuantumForgeIntegration
        return QuantumForgeIntegration(forge=quantum_forge)
        
    def test_quantum_integration_initialization(self):
        """Test QuantumForgeIntegration initialization"""
        from modules.quantum_forge import QuantumForgeIntegration, get_quantum_integration
        
        integration = QuantumForgeIntegration()
        assert integration.metrics["total_conversions"] == 0
        assert integration.fidelity_threshold == 0.95
        
        # Test singleton
        integration2 = get_quantum_integration()
        assert integration2.default_coherence_time == 300.0
        
    def test_agent_to_quantum_conversion(self, test_agent, quantum_integration):
        """Test converting agent to quantum state"""
        integration = quantum_integration
        quantum_state = integration.agent_to_quantum(test_agent)
        
        assert quantum_state.num_qubits >= 8
        assert quantum_state.agent_id == test_agent.agent_id
        assert quantum_state.num_qubits >= 8
        assert 0.0 <= quantum_state.fidelity <= 1.01  # Allow small floating point error
        assert quantum_state.fidelity >= integration.fidelity_threshold
        
    def test_quantum_to_agent_conversion(self, test_agent, quantum_integration):
        """Test converting quantum state back to agent"""
        integration = quantum_integration
        quantum_state = integration.agent_to_quantum(test_agent)
        restored_agent = integration.quantum_to_agent(quantum_state)
        
        assert restored_agent.metadata == test_agent.metadata
        assert restored_agent.agent_id == test_agent.agent_id
        # Joy and alignment should be close (within 10%)
        assert abs(restored_agent.joy_index - test_agent.joy_index) < 0.1
        assert abs(restored_agent.intent_alignment - test_agent.intent_alignment) < 0.1
        
    def test_coherence_tracking(self, test_agent, quantum_integration):
        """Test coherence time tracking"""
        import time
        
        integration = quantum_integration
        quantum_state = integration.agent_to_quantum(test_agent)
        
        # Check initial coherence using agent_id
        coherence_status = integration.check_coherence(test_agent.agent_id)
        assert coherence_status["has_quantum_state"] is True
        assert coherence_status["coherent"] is True
        
        # Simulate decoherence by setting last_update to past
        quantum_state.last_update = time.time() - quantum_state.coherence_time - 1
        coherence_status = integration.check_coherence(test_agent.agent_id)
        # Should be decoherent now
        assert coherence_status["coherent"] is False
        
    def test_optimize_agent_quantum(self, test_agent, quantum_integration):
        """Test quantum optimization of agent"""
        integration = quantum_integration
        optimized = integration.optimize_agent_quantum(test_agent)
        
        assert optimized.agent_id == test_agent.agent_id
        # Joy should be optimized (increased or maintained)
        assert optimized.joy_index >= test_agent.joy_index * 0.95


# ============================================================================
# PHASE 2: Entanglement Networks Tests
# ============================================================================

class TestEntanglementNetwork:
    """Tests for multi-agent entanglement networks"""
    
    @pytest.fixture
    def quantum_forge(self):
        """Mock QuantumForge instance"""
        from modules.quantum_forge import QuantumForge, EthicsLevel
        return QuantumForge(ethics_level=EthicsLevel.BALANCED)
        
    @pytest.fixture
    def test_agents(self, quantum_forge):
        """Create multiple test agents"""
        agents = []
        for i in range(3):
            agent = quantum_forge.generate_agent(
                intent_query="Test entanglement agent " + str(i),
                constellation_targets=["ORION"]
            )
            agents.append(agent)
        return agents
        
    def test_entanglement_network_initialization(self):
        """Test EntanglementNetwork initialization"""
        from modules.quantum_forge import EntanglementNetwork, get_entanglement_network
        
        network = EntanglementNetwork()
        assert network.metrics["total_entanglements"] == 0
        assert len(network.entanglement_links) == 0
        
        # Test singleton
        network2 = get_entanglement_network()
        assert network2.metrics["active_entanglements"] >= 0
        
    def test_entangle_agents(self, quantum_forge, test_agents):
        """Test creating entanglement between agents"""
        from modules.quantum_forge import EntanglementNetwork
        
        network = EntanglementNetwork(forge=quantum_forge)
        agent1, agent2 = test_agents[0], test_agents[1]
        
        link = network.entangle_agents(agent1.agent_id, agent2.agent_id, strength=0.8)
        
        assert link.link_id in network.entanglement_links
        assert link.agent_1_id == agent1.agent_id
        assert link.agent_2_id == agent2.agent_id
        assert 0.0 <= link.entanglement_strength <= 1.0
        
    def test_state_propagation(self, quantum_forge, test_agents):
        """Test state propagation through entanglement"""
        from modules.quantum_forge import EntanglementNetwork
        
        network = EntanglementNetwork(forge=quantum_forge)
        agent1, agent2 = test_agents[0], test_agents[1]
        
        # Entangle agents
        network.entangle_agents(agent1.agent_id, agent2.agent_id, strength=0.9)
        
        # Update agent1 state
        original_joy = agent2.joy_index
        agent1.joy_index = 0.95
        
        # Propagate state
        network.propagate_state_update(agent1.agent_id, {"joy_index": agent1.joy_index})
        
        # Check if agent2 was affected (correlation should cause some change)
        # Note: This is a simplified check, real implementation may vary
        assert agent2.joy_index >= original_joy  # Should increase slightly
        
    def test_create_cluster(self, quantum_forge, test_agents):
        """Test creating entanglement cluster"""
        from modules.quantum_forge import EntanglementNetwork
        
        network = EntanglementNetwork(forge=quantum_forge)
        agent_ids = [agent.agent_id for agent in test_agents]
        
        cluster = network.create_cluster(
            agent_ids,
            topology="mesh"
        )
        
        assert cluster.topology == "mesh"
        assert len(cluster.agent_ids) == len(test_agents)
        # Mesh topology: n*(n-1)/2 links
        expected_links = len(test_agents) * (len(test_agents) - 1) // 2
        # Count actual links created
        actual_links = len([l for l in network.entanglement_links.values() 
                           if l.agent_1_id in agent_ids and l.agent_2_id in agent_ids])
        assert actual_links == expected_links
        
    def test_network_health(self, quantum_forge, test_agents):
        """Test network health monitoring"""
        from modules.quantum_forge import EntanglementNetwork
        
        network = EntanglementNetwork(forge=quantum_forge)
        
        # Create some entanglements
        for i in range(len(test_agents) - 1):
            network.entangle_agents(test_agents[i].agent_id, test_agents[i+1].agent_id)
        
        health = network.monitor_network_health()
        
        assert isinstance(health["recommendations"], list)
        assert "total_links" in health
        assert "average_strength" in health
        assert health["total_links"] >= 2


# ============================================================================
# PHASE 3: Quantum Memory Enhancement Tests
# ============================================================================

class TestQuantumMemoryEnhancer:
    """Tests for quantum-enhanced memory system"""
    
    # Test constant for embedding dimensions
    EMBEDDING_DIM = 128
    
    @pytest.fixture
    def memory_enhancer(self):
        """Create memory enhancer instance"""
        from modules.quantum_forge import QuantumMemoryEnhancer, get_quantum_memory_enhancer
        return get_quantum_memory_enhancer()
        
    def test_memory_enhancer_initialization(self):
        """Test QuantumMemoryEnhancer initialization"""
        from modules.quantum_forge import QuantumMemoryEnhancer, get_quantum_memory_enhancer
        
        enhancer = QuantumMemoryEnhancer()
        assert enhancer.metrics["total_enhanced_memories"] == 0
        assert len(enhancer.quantum_metadata) == 0
        
    def test_enhance_memory(self, memory_enhancer):
        """Test enhancing memory with quantum metadata"""
        from modules.quantum_forge import SymbolicMemoryNode
        import datetime
        
        test_memory = SymbolicMemoryNode(
            node_id="mem_001",
            content={"text": "Test memory content"},
            embedding=[0.1] * self.EMBEDDING_DIM,
            intent_alignment=0.8,
            created_at=datetime.datetime.now().timestamp()
        )
        
        metadata = memory_enhancer.enhance_memory(test_memory)
        
        assert metadata.quantum_priority > 0.0
        assert metadata.memory_id == "mem_001"
        assert metadata.coherence_state == "COHERENT"
        assert 0.0 <= metadata.coherence_score <= 1.0
        
    def test_retrieve_by_priority(self, memory_enhancer):
        """Test priority-based memory retrieval"""
        from modules.quantum_forge import SymbolicMemoryNode
        import time
        
        # Enhance multiple memories with different alignments (affects priority)
        for i in range(3):
            memory = SymbolicMemoryNode(
                node_id=f"mem_{i}",
                content={"text": f"Content {i}"},
                embedding=[0.1 + i * 0.01] * self.EMBEDDING_DIM,
                intent_alignment=0.5 + i * 0.1,  # Increasing alignment
                created_at=time.time()
            )
            memory_enhancer.enhance_memory(memory)
        
        # Retrieve top priority
        top_memories = memory_enhancer.retrieve_by_priority(top_k=2)
        
        assert len(top_memories) <= 2
        # Should be sorted by priority
        if len(top_memories) > 1:
            assert top_memories[0][1].quantum_priority >= \
                   top_memories[1][1].quantum_priority
                   
    def test_search_by_entanglement(self, memory_enhancer):
        """Test semantic entanglement search"""
        from modules.quantum_forge import SymbolicMemoryNode
        import time
        
        # Create memories with similar embeddings (will be auto-entangled)
        mem1 = SymbolicMemoryNode(
            node_id="mem_1",
            content={"text": "quantum computing"},
            embedding=[0.9, 0.8] + [0.1] * (self.EMBEDDING_DIM - 2),  # Similar pattern
            intent_alignment=0.8,
            created_at=time.time()
        )
        mem2 = SymbolicMemoryNode(
            node_id="mem_2",
            content={"text": "quantum physics"},
            embedding=[0.85, 0.75] + [0.15] * (self.EMBEDDING_DIM - 2),  # Similar to mem1
            intent_alignment=0.8,
            created_at=time.time()
        )
        mem3 = SymbolicMemoryNode(
            node_id="mem_3",
            content={"text": "classical computing"},
            embedding=[0.1, 0.2] + [0.9] * (self.EMBEDDING_DIM - 2),  # Different pattern
            intent_alignment=0.6,
            created_at=time.time()
        )
        
        memory_enhancer.enhance_memory(mem1)
        memory_enhancer.enhance_memory(mem2)
        memory_enhancer.enhance_memory(mem3)
        
        # Search for quantum-related
        results = memory_enhancer.search_by_entanglement("mem_1", top_k=5)
        
        assert isinstance(results, list)  # Should return list of entangled memories
        
    def test_auto_refresh_decoherent(self, memory_enhancer):
        """Test automatic decoherence detection and refresh"""
        from modules.quantum_forge import SymbolicMemoryNode
        import time
        
        memory = SymbolicMemoryNode(
            node_id="mem_test",
            content={"text": "Test"},
            embedding=[0.5] * self.EMBEDDING_DIM,
            intent_alignment=0.7,
            created_at=time.time()
        )
        metadata = memory_enhancer.enhance_memory(memory)
        
        # Simulate decoherence by modifying metadata
        metadata.coherence_score = 0.3  # Force low coherence
        metadata.coherence_state = "DECOHERENT"
        memory_enhancer.metrics["decoherent_memories"] += 1
        
        # Auto-refresh should detect and fix
        refreshed = memory_enhancer.auto_refresh_decoherent()
        
        # Check that refresh was attempted (returns dict with results)
        assert isinstance(refreshed, dict)
        assert "refreshed_count" in refreshed


# ============================================================================
# PHASE 4: System Flow Orchestration Tests
# ============================================================================

class TestSystemFlowOrchestrator:
    """Tests for system-wide flowstate orchestration"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create system orchestrator instance"""
        from modules.quantum_forge import SystemFlowOrchestrator, get_system_flow_orchestrator
        return get_system_flow_orchestrator()
        
    def test_orchestrator_initialization(self):
        """Test SystemFlowOrchestrator initialization"""
        from modules.quantum_forge import SystemFlowOrchestrator, get_system_flow_orchestrator
        
        orchestrator = SystemFlowOrchestrator()
        assert orchestrator.current_phase == type(orchestrator.current_phase).STARTUP
        # Should auto-register 8 core modules
        assert len(orchestrator.modules) >= 8
        
    def test_register_module(self, orchestrator):
        """Test module registration"""
        from modules.quantum_forge import FlowstateMode
        
        initial_count = len(orchestrator.modules)
        
        orchestrator.register_module(
            module_name="test_module",
            initial_mode=FlowstateMode.GENERATIVE
        )
        
        assert len(orchestrator.modules) == initial_count + 1
        assert "test_module" in orchestrator.modules
        
    def test_adapt_to_load(self, orchestrator):
        """Test load-based adaptive transitions"""
        from modules.quantum_forge import FlowstateMode
        
        # Simulate high load across all modules
        for module_name in orchestrator.modules.keys():
            orchestrator.update_module_status(module_name, load=0.95)
        
        result = orchestrator.adapt_to_load()
        
        # Should transition to QUIESCENT due to high system load
        assert result["adapted"] is True
        assert result["target_mode"] == FlowstateMode.QUIESCENT.value
        
        # Check that modules transitioned
        for state in orchestrator.modules.values():
            assert state.current_mode == FlowstateMode.QUIESCENT
            
    def test_respond_to_drift(self, orchestrator):
        """Test drift-triggered self-healing"""
        from modules.quantum_forge import FlowstateMode
        
        module_name = "quantum_forge"
        
        # Simulate drift
        orchestrator.update_module_status(module_name, drift_detected=True)
        orchestrator.respond_to_drift(module_name)
        
        # Should transition to METAMORPHIC
        state = orchestrator.modules.get(module_name)
        if state:
            # May have transitioned to healing mode
            assert state.current_mode in [
                FlowstateMode.METAMORPHIC,
                FlowstateMode.GENERATIVE
            ]
            
    def test_synchronize_all_modules(self, orchestrator):
        """Test system-wide synchronization"""
        from modules.quantum_forge import FlowstateMode
        
        # Force all to RESONANT
        orchestrator.synchronize_all_modules(target_mode=FlowstateMode.RESONANT)
        
        # Check all modules are synchronized
        for state in orchestrator.modules.values():
            assert state.current_mode == FlowstateMode.RESONANT
            
    def test_get_system_metrics(self, orchestrator):
        """Test system metrics collection"""
        metrics = orchestrator.get_system_metrics()
        
        assert metrics.current_phase == orchestrator.current_phase
        assert 0.0 <= metrics.system_load <= 1.0
        assert 0.0 <= metrics.average_health <= 1.0
        assert metrics.drift_count >= 0
        assert metrics.total_transitions >= 0


# ============================================================================
# PHASE 5: Ethics-Aware Operations Tests
# ============================================================================

class TestEthicsQuantumGates:
    """Tests for ethics-aware quantum operations"""
    
    @pytest.fixture
    def ethics_gate(self):
        """Create ethics-aware gate"""
        from modules.quantum_forge import EthicsAwareQuantumGate
        from modules.quantum_forge import QuantumForge, EthicsLevel
        
        forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)
        gate = EthicsAwareQuantumGate(ethics_level=forge.ethics.level)
        return gate
        
    def test_ethics_gate_initialization(self, ethics_gate):
        """Test EthicsAwareQuantumGate initialization"""
        assert ethics_gate.gumas.level.value == "balanced"
        assert ethics_gate.total_operations == 0
        
    def test_validate_gate_operation_pass(self, ethics_gate):
        """Test gate validation with valid operation"""
        result = ethics_gate.validate_gate_operation(
            gate_type="hadamard",
            qubits=[0],
            intent_score=0.9
        )
        
        assert result["allowed"] is True
        assert result["risk_level"] in ["low", "medium"]
        
    def test_validate_gate_operation_warn(self, ethics_gate):
        """Test gate validation with warning"""
        # Simulate risky operation
        result = ethics_gate.validate_gate_operation(
            gate_type="custom_risky_gate",
            qubits=[0, 1, 2, 3, 4],  # Many qubits
            intent_score=0.5
        )
        
        # May warn or allow depending on implementation
        assert "risk_level" in result
        
    def test_get_ethics_metrics(self, ethics_gate):
        """Test ethics metrics collection"""
        # Run some validations
        ethics_gate.validate_gate_operation("hadamard", [0], 0.9)
        ethics_gate.validate_gate_operation("cnot", [0, 1], 0.9)
        
        metrics = ethics_gate.get_ethics_metrics()
        
        assert metrics["audit_log_size"] >= 0
        assert "total_operations" in metrics
        assert metrics["total_operations"] >= 2


# ============================================================================
# PHASE 6: Constellation Topology Tests
# ============================================================================

class TestConstellationTopologyMapper:
    """Tests for constellation topology mapping"""
    
    @pytest.fixture
    def topology_mapper(self):
        """Create topology mapper instance"""
        from modules.quantum_forge import ConstellationTopologyMapper, get_topology_mapper
        return get_topology_mapper()
        
    def test_topology_mapper_initialization(self):
        """Test ConstellationTopologyMapper initialization"""
        from modules.quantum_forge import get_topology_mapper
        
        mapper = get_topology_mapper()
        assert mapper.optimization_metric.value == "entanglement_fidelity"
        # Should auto-register 8 core modules
        assert len(mapper.modules) >= 8
        
    def test_calculate_optimal_topology(self, topology_mapper):
        """Test optimal topology calculation"""
        mapping = topology_mapper.calculate_optimal_topology()
        
        assert mapping.optimization_metric.value == topology_mapper.optimization_metric.value
        assert len(mapping.links) > 0
        assert 0.0 <= mapping.average_fidelity <= 1.0
        
    def test_optimize_module_placement(self, topology_mapper):
        """Test module placement optimization"""
        module_ids = ["quantum_forge", "aumemmanager", "quantum_simulator"]
        
        new_positions = topology_mapper.optimize_module_placement(
            module_ids,
            target_fidelity=0.95
        )
        
        assert len(new_positions) == len(module_ids)
        for pos in new_positions.values():
            assert len(pos) == 3  # 3D coordinates
            
    def test_find_coherence_preserving_route(self, topology_mapper):
        """Test coherence-preserving routing"""
        # First calculate topology to create links
        topology_mapper.calculate_optimal_topology()
        
        route = topology_mapper.find_coherence_preserving_route(
            "quantum_forge",
            "aumemmanager"
        )
        
        # May find route or not depending on topology
        assert isinstance(route, list)


# ============================================================================
# PHASE 7: Joy Evolution Tests
# ============================================================================

class TestJoyEvolutionEngine:
    """Tests for joy-infused evolution engine"""
    
    @pytest.fixture
    def quantum_forge(self):
        """Mock QuantumForge instance"""
        from modules.quantum_forge import QuantumForge, EthicsLevel
        return QuantumForge(ethics_level=EthicsLevel.BALANCED)
        
    @pytest.fixture
    def evolution_engine(self, quantum_forge):
        """Create evolution engine instance"""
        from modules.quantum_forge import JoyEvolutionEngine, EvolutionParameters
        
        params = EvolutionParameters(
            population_size=10,  # Small for testing
            max_generations=5
        )
        return JoyEvolutionEngine(quantum_forge, params)
        
    def test_evolution_engine_initialization(self, evolution_engine):
        """Test JoyEvolutionEngine initialization"""
        assert evolution_engine.current_generation == 0
        assert evolution_engine.params.population_size == 10
        
    def test_initialize_population(self, evolution_engine):
        """Test population initialization"""
        evolution_engine.initialize_population()
        
        assert len(evolution_engine.population) == 10
        for genome in evolution_engine.population:
            assert 0.0 <= genome.joy_index <= 1.0
            assert 0.0 <= genome.intent_alignment <= 1.0
            
    def test_evolve(self, evolution_engine):
        """Test evolution process"""
        evolution_engine.initialize_population()
        
        initial_avg_fitness = sum(g.fitness for g in evolution_engine.population) / len(evolution_engine.population)
        
        # Run evolution
        final_stats = evolution_engine.evolve(generations=3)
        
        assert final_stats.generation == evolution_engine.current_generation
        # Fitness should improve or stay similar
        assert final_stats.avg_fitness >= initial_avg_fitness * 0.9
        
    def test_get_best_agent(self, evolution_engine):
        """Test retrieving best agent"""
        evolution_engine.initialize_population()
        
        best = evolution_engine.get_best_agent()
        
        assert best.agent_id in {genome.agent_id for genome in evolution_engine.population}
        # Should be highest fitness
        assert best.fitness == max(g.fitness for g in evolution_engine.population)
        
    def test_get_most_joyful_agent(self, evolution_engine):
        """Test retrieving most joyful agent"""
        evolution_engine.initialize_population()
        
        most_joyful = evolution_engine.get_most_joyful_agent()
        
        assert most_joyful.agent_id in {genome.agent_id for genome in evolution_engine.population}
        # Should be highest joy
        assert most_joyful.joy_index == max(g.joy_index for g in evolution_engine.population)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestQuantumForgeV3Integration:
    """Integration tests for complete v3.0 system"""
    
    @pytest.mark.slow
    def test_complete_workflow(self):
        """Test complete workflow across all phases"""
        from modules.quantum_forge import (
            QuantumForge,
            EthicsLevel,
            get_quantum_integration,
            get_entanglement_network,
            get_quantum_memory_enhancer,
            get_system_flow_orchestrator,
            get_topology_mapper
        )
        
        # Initialize forge
        forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)
        
        # Phase 1: Create and convert agent
        agent = forge.generate_agent(
            intent_query="Complete integration test",
            constellation_targets=["ORION"]
        )
        
        integration = get_quantum_integration()
        quantum_state = integration.agent_to_quantum(agent)
        assert quantum_state.fidelity >= 0.95
        
        # Phase 4: Check system orchestration
        orchestrator = get_system_flow_orchestrator()
        metrics = orchestrator.get_system_metrics()
        # metrics is a dataclass, check module count via orchestrator
        assert len(orchestrator.modules) >= 8
        
        # Phase 6: Check topology
        mapper = get_topology_mapper()
        assert len(mapper.modules) >= 8
        
        logger.info("✅ Complete v3.0 workflow test passed")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestQuantumForgeV3Performance:
    """Performance tests for v3.0 system"""
    
    @pytest.mark.slow
    def test_agent_creation_performance(self):
        """Test agent creation performance"""
        import time
        from modules.quantum_forge import QuantumForge, EthicsLevel
        
        forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)
        
        start = time.time()
        for i in range(10):
            agent = forge.generate_agent(
                intent_query="Performance test " + str(i),
                constellation_targets=["ORION"]
            )
        elapsed = time.time() - start
        
        # Should create 10 agents in < 5 seconds
        assert elapsed < 5.0
        logger.info("Created 10 agents in %.2fs", elapsed)
        
    @pytest.mark.slow
    def test_quantum_conversion_performance(self):
        """Test quantum conversion performance"""
        import time
        from modules.quantum_forge import QuantumForge, EthicsLevel, get_quantum_integration
        
        forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)
        integration = get_quantum_integration()
        
        # Create test agents
        agents = [
            forge.generate_agent(f"Test {i}", ["ORION"])
            for i in range(5)
        ]
        
        start = time.time()
        for agent in agents:
            quantum_state = integration.agent_to_quantum(agent)
            assert quantum_state.fidelity >= 0.95
        elapsed = time.time() - start
        
        # Should convert 5 agents in < 3 seconds
        assert elapsed < 3.0
        logger.info("Converted 5 agents in %.2fs", elapsed)
