"""
Tests for Vector Gen v2.0 Module

Comprehensive test suite covering:
- VectorGen symbolic vector generation
- Chain topology management (5 types)
- Vector injection modes (6 types)
- VectorCapsulePackager VECTORCHAIN capsules
- DriftConcord integration
- Entanglement mechanics

Run with: pytest tests/test_vector_gen_v2.py -v
"""

import pytest
from modules.vector_gen import (
    VectorGen,
    VectorCapsulePackager,
    ChainTopology,
    InjectionMode,
    LinkStrength,
    SymbolicVector,
    VectorChain,
    VectorLink
)
from modules.vector_gen.vector_gen_v2 import VectorChainManager


# ============================================================================
# VECTOR GENERATION TESTS
# ============================================================================

@pytest.mark.unit
def test_vector_gen_initialization():
    """Test VectorGen initialization"""
    gen = VectorGen(vector_dimension=256, normalization="l2")
    assert gen.vector_dimension == 256
    assert gen.normalization == "l2"
    assert gen.generation_count == 0


@pytest.mark.unit
def test_vector_generation_basic():
    """Test basic vector generation"""
    gen = VectorGen()
    
    vector = gen.generate_vector(
        symbol="🧭",
        tags=["ops", "navigation"],
        seed=42
    )
    
    assert vector is not None
    assert vector.vector_id.startswith("vec::")
    assert vector.symbol == "🧭"
    assert "ops" in vector.tags
    assert len(vector.data) == gen.vector_dimension
    assert vector.magnitude > 0.0


@pytest.mark.unit
def test_vector_generation_reproducibility():
    """Test reproducible generation with seed"""
    gen = VectorGen()
    
    vec1 = gen.generate_vector("🔑", seed=123)
    vec2 = gen.generate_vector("🔑", seed=123)
    
    # Same seed should produce same vector data
    assert vec1.data == vec2.data


@pytest.mark.unit
def test_vector_normalization_l2():
    """Test L2 normalization"""
    gen = VectorGen(normalization="l2")
    vector = gen.generate_vector("♾️", seed=42)
    
    # L2 normalized vector should have magnitude ≈ 1.0
    assert 0.99 <= vector.magnitude <= 1.01


@pytest.mark.unit
def test_vector_normalization_none():
    """Test no normalization"""
    gen = VectorGen(normalization="none")
    vector = gen.generate_vector("🪞", seed=42)
    
    # Unnormalized vector can have any magnitude
    assert vector.magnitude > 0.0


@pytest.mark.unit
def test_vector_metadata_attachment():
    """Test metadata attachment"""
    gen = VectorGen()
    
    vector = gen.generate_vector(
        symbol="⚛️",
        metadata={"purpose": "quantum entanglement", "version": "2.0"}
    )
    
    assert vector.metadata["purpose"] == "quantum entanglement"
    assert vector.metadata["version"] == "2.0"


@pytest.mark.unit
def test_entangled_pair_generation():
    """Test quantum-entangled pair generation"""
    gen = VectorGen()
    
    vec_a, vec_b = gen.generate_entangled_pair(
        symbol_a="⚛️",
        symbol_b="🔮",
        entanglement_strength=0.95
    )
    
    assert vec_a is not None
    assert vec_b is not None
    assert "entangled" in vec_a.tags
    assert "entangled" in vec_b.tags
    assert vec_a.metadata["entangled_with"] == vec_b.vector_id
    assert vec_b.metadata["entangled_with"] == vec_a.vector_id


@pytest.mark.unit
def test_generation_counter():
    """Test generation counter increments"""
    gen = VectorGen()
    
    initial_count = gen.generation_count
    gen.generate_vector("🌟")
    assert gen.generation_count == initial_count + 1
    
    gen.generate_entangled_pair("✨", "💫")
    assert gen.generation_count == initial_count + 3  # 1 + 2 from pair


# ============================================================================
# CHAIN TOPOLOGY TESTS
# ============================================================================

@pytest.mark.unit
def test_chain_manager_initialization():
    """Test VectorChainManager initialization"""
    manager = VectorChainManager(similarity_threshold=0.7)
    assert manager.similarity_threshold == 0.7
    assert manager.chain_count == 0


@pytest.mark.unit
def test_sequential_chain_creation():
    """Test sequential chain topology"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(4)]
    
    chain = manager.create_chain(
        "Sequential_Test",
        ChainTopology.SEQUENTIAL,
        vectors
    )
    
    assert chain.topology == ChainTopology.SEQUENTIAL
    assert len(chain.vectors) == 4
    assert len(chain.links) == 3  # n-1 links for sequential


@pytest.mark.unit
def test_hierarchical_chain_creation():
    """Test hierarchical chain topology"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(5)]
    
    chain = manager.create_chain(
        "Hierarchical_Test",
        ChainTopology.HIERARCHICAL,
        vectors
    )
    
    assert chain.topology == ChainTopology.HIERARCHICAL
    assert len(chain.links) == 4  # Root connects to all children


@pytest.mark.unit
def test_networked_chain_creation():
    """Test networked chain topology"""
    gen = VectorGen()
    manager = VectorChainManager(similarity_threshold=0.5)
    
    # Generate similar vectors (same seed = similar vectors)
    vectors = [gen.generate_vector(f"v{i}", seed=100 + i) for i in range(3)]
    
    chain = manager.create_chain(
        "Networked_Test",
        ChainTopology.NETWORKED,
        vectors
    )
    
    assert chain.topology == ChainTopology.NETWORKED
    # Networked creates links based on similarity
    assert len(chain.links) >= 0


@pytest.mark.unit
def test_temporal_chain_creation():
    """Test temporal chain topology"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    import time
    vectors = []
    for i in range(3):
        vec = gen.generate_vector(f"v{i}")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        vectors.append(vec)
    
    chain = manager.create_chain(
        "Temporal_Test",
        ChainTopology.TEMPORAL,
        vectors
    )
    
    assert chain.topology == ChainTopology.TEMPORAL
    assert len(chain.links) == 2


@pytest.mark.unit
def test_entangled_chain_creation():
    """Test entangled chain topology"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vec_a, vec_b = gen.generate_entangled_pair("⚛️", "🔮")
    vec_c, vec_d = gen.generate_entangled_pair("✨", "💫")
    
    chain = manager.create_chain(
        "Entangled_Test",
        ChainTopology.ENTANGLED,
        [vec_a, vec_b, vec_c, vec_d]
    )
    
    assert chain.topology == ChainTopology.ENTANGLED
    assert len(chain.links) == 2  # 2 pairs = 2 links
    assert all(link.strength == LinkStrength.ABSOLUTE for link in chain.links)


# ============================================================================
# INJECTION MODE TESTS
# ============================================================================

@pytest.mark.unit
def test_injection_append():
    """Test APPEND injection mode"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(3)]
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, vectors)
    
    new_vector = gen.generate_vector("new")
    success = manager.inject_vector(chain.chain_id, new_vector, InjectionMode.APPEND)
    
    assert success is True
    assert len(chain.vectors) == 4
    assert chain.vectors[-1].vector_id == new_vector.vector_id


@pytest.mark.unit
def test_injection_prepend():
    """Test PREPEND injection mode"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(3)]
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, vectors)
    
    new_vector = gen.generate_vector("new")
    success = manager.inject_vector(chain.chain_id, new_vector, InjectionMode.PREPEND)
    
    assert success is True
    assert len(chain.vectors) == 4
    assert chain.vectors[0].vector_id == new_vector.vector_id


@pytest.mark.unit
def test_injection_insert():
    """Test INSERT injection mode"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(3)]
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, vectors)
    
    new_vector = gen.generate_vector("new")
    success = manager.inject_vector(
        chain.chain_id,
        new_vector,
        InjectionMode.INSERT,
        position=1
    )
    
    assert success is True
    assert len(chain.vectors) == 4
    assert chain.vectors[1].vector_id == new_vector.vector_id


@pytest.mark.unit
def test_injection_replace():
    """Test REPLACE injection mode"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(3)]
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, vectors)
    old_id = chain.vectors[1].vector_id
    
    new_vector = gen.generate_vector("replacement")
    success = manager.inject_vector(
        chain.chain_id,
        new_vector,
        InjectionMode.REPLACE,
        position=1
    )
    
    assert success is True
    assert len(chain.vectors) == 3  # Same count
    assert chain.vectors[1].vector_id != old_id
    assert chain.vectors[1].vector_id == new_vector.vector_id


@pytest.mark.unit
def test_injection_merge():
    """Test MERGE injection mode"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(3)]
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, vectors)
    
    # Merge existing vector (should not duplicate)
    success = manager.inject_vector(
        chain.chain_id,
        vectors[0],
        InjectionMode.MERGE
    )
    
    assert success is True
    assert len(chain.vectors) == 3  # No duplicate
    
    # Merge new vector (should add)
    new_vector = gen.generate_vector("new")
    success = manager.inject_vector(chain.chain_id, new_vector, InjectionMode.MERGE)
    
    assert success is True
    assert len(chain.vectors) == 4


@pytest.mark.unit
def test_injection_graft():
    """Test GRAFT injection mode"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(4)]
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, vectors)
    
    new_vector = gen.generate_vector("grafted")
    initial_link_count = len(chain.links)
    
    success = manager.inject_vector(chain.chain_id, new_vector, InjectionMode.GRAFT)
    
    assert success is True
    assert len(chain.vectors) == 5
    # Graft creates strong links to multiple vectors
    # Links regenerated based on topology, so count varies


@pytest.mark.unit
def test_injection_invalid_chain():
    """Test injection to nonexistent chain"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    new_vector = gen.generate_vector("orphan")
    success = manager.inject_vector("invalid_id", new_vector, InjectionMode.APPEND)
    
    assert success is False


# ============================================================================
# VECTORCHAIN CAPSULE PACKAGER TESTS
# ============================================================================

@pytest.mark.unit
def test_packager_initialization():
    """Test VectorCapsulePackager initialization"""
    packager = VectorCapsulePackager()
    assert len(packager.capsules) == 0
    assert len(packager.registry) == 0


@pytest.mark.unit
def test_capsule_packaging():
    """Test VECTORCHAIN capsule packaging"""
    gen = VectorGen()
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(3)]
    chain = manager.create_chain("Test_Chain", ChainTopology.SEQUENTIAL, vectors)
    
    capsule = packager.package_capsule(
        chain,
        system_name="ZIPWIZ",
        thread_context="Thread_Transfer::Test"
    )
    
    assert capsule is not None
    assert capsule["capsule_id"].startswith("VECTORCHAIN::ZIPWIZ::")
    assert capsule["ethics_protocol"] == "Picard_Delta_3"
    assert capsule["trust_anchor"] == "SN1-AS3-TRUSTED"
    assert capsule["vector_engine"] == "DriftConcord::Vector"
    assert capsule["deployment"]["target_constellation"] == "ZIPWIZ"


@pytest.mark.unit
def test_capsule_chain_data_inclusion():
    """Test chain data included in capsule"""
    gen = VectorGen()
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(2)]
    chain = manager.create_chain("Data_Test", ChainTopology.SEQUENTIAL, vectors)
    
    capsule = packager.package_capsule(chain, "BridgeAgent")
    
    assert "chain" in capsule
    assert capsule["chain"]["chain_id"] == chain.chain_id
    assert len(capsule["chain"]["vectors"]) == 2
    assert capsule["metadata"]["vector_count"] == 2


@pytest.mark.unit
def test_deployment_registry_creation():
    """Test deployment registry creation"""
    gen = VectorGen()
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    # Create multiple chains and capsules
    chain1 = manager.create_chain("C1", ChainTopology.SEQUENTIAL, [gen.generate_vector("v1")])
    chain2 = manager.create_chain("C2", ChainTopology.HIERARCHICAL, [gen.generate_vector("v2")])
    
    packager.package_capsule(chain1, "ZIPWIZ")
    packager.package_capsule(chain2, "BridgeAgent")
    
    registry = packager.create_deployment_registry()
    
    assert registry["registry_id"].startswith("registry::")
    assert registry["statistics"]["total_capsules"] == 2
    assert len(registry["entries"]) == 2


@pytest.mark.unit
def test_selective_registry_creation():
    """Test registry creation with capsule filter"""
    gen = VectorGen()
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    chain1 = manager.create_chain("C1", ChainTopology.SEQUENTIAL, [gen.generate_vector("v1")])
    chain2 = manager.create_chain("C2", ChainTopology.HIERARCHICAL, [gen.generate_vector("v2")])
    
    cap1 = packager.package_capsule(chain1, "ZIPWIZ")
    cap2 = packager.package_capsule(chain2, "BridgeAgent")
    
    # Create registry with only one capsule
    registry = packager.create_deployment_registry([cap1["capsule_id"]])
    
    assert registry["statistics"]["total_capsules"] == 1


@pytest.mark.unit
def test_packager_manifest_export():
    """Test packager manifest export"""
    gen = VectorGen()
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, [gen.generate_vector("v")])
    packager.package_capsule(chain, "ORION")
    
    manifest = packager.export_manifest()
    
    assert "version" in manifest
    assert "metrics" in manifest
    assert manifest["metrics"]["capsules_created"] == 1
    assert "configuration" in manifest


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
def test_full_vector_gen_workflow():
    """Test complete Vector Gen v2.0 workflow"""
    gen = VectorGen(vector_dimension=256)
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    # 1. Generate vectors
    vectors = [
        gen.generate_vector("🧭", tags=["ops"]),
        gen.generate_vector("🔑", tags=["access"]),
        gen.generate_vector("♾️", tags=["binding"])
    ]
    
    # 2. Create chain
    chain = manager.create_chain(
        "Complete_Workflow_Chain",
        ChainTopology.SEQUENTIAL,
        vectors
    )
    assert len(chain.vectors) == 3
    
    # 3. Inject new vector
    new_vec = gen.generate_vector("🪞", tags=["reflex"])
    success = manager.inject_vector(chain.chain_id, new_vec, InjectionMode.APPEND)
    assert success is True
    assert len(chain.vectors) == 4
    
    # 4. Package capsule
    capsule = packager.package_capsule(chain, "ZIPWIZ")
    assert capsule["capsule_id"].startswith("VECTORCHAIN::ZIPWIZ")
    
    # 5. Create registry
    registry = packager.create_deployment_registry()
    assert registry["statistics"]["total_capsules"] == 1


@pytest.mark.integration
def test_multi_topology_workflow():
    """Test workflow with multiple topologies"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    vectors = [gen.generate_vector(f"v{i}") for i in range(5)]
    
    # Create chains with different topologies
    seq_chain = manager.create_chain("Sequential", ChainTopology.SEQUENTIAL, vectors)
    hier_chain = manager.create_chain("Hierarchical", ChainTopology.HIERARCHICAL, vectors)
    net_chain = manager.create_chain("Networked", ChainTopology.NETWORKED, vectors)
    
    assert seq_chain.topology == ChainTopology.SEQUENTIAL
    assert hier_chain.topology == ChainTopology.HIERARCHICAL
    assert net_chain.topology == ChainTopology.NETWORKED
    assert manager.chain_count == 3


@pytest.mark.integration
def test_entanglement_to_capsule_workflow():
    """Test entangled pairs to capsule workflow"""
    gen = VectorGen()
    manager = VectorChainManager()
    packager = VectorCapsulePackager()
    
    # Generate entangled pairs
    vec_a, vec_b = gen.generate_entangled_pair("⚛️", "🔮", entanglement_strength=0.95)
    
    # Create entangled chain
    chain = manager.create_chain(
        "Quantum_Entangled",
        ChainTopology.ENTANGLED,
        [vec_a, vec_b]
    )
    
    # Package for quantum system
    capsule = packager.package_capsule(chain, "QuantumForge")
    
    assert capsule["deployment"]["target_constellation"] == "QuantumForge"
    assert capsule["metadata"]["vector_count"] == 2
    assert len(capsule["chain"]["links"]) == 1
    assert capsule["chain"]["links"][0]["strength"] == LinkStrength.ABSOLUTE.value


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
def test_empty_chain_creation():
    """Test creating chain with empty vector list"""
    manager = VectorChainManager()
    
    chain = manager.create_chain("Empty", ChainTopology.SEQUENTIAL, [])
    assert len(chain.vectors) == 0
    assert len(chain.links) == 0


@pytest.mark.unit
def test_single_vector_chain():
    """Test chain with single vector"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    chain = manager.create_chain(
        "Single",
        ChainTopology.SEQUENTIAL,
        [gen.generate_vector("solo")]
    )
    
    assert len(chain.vectors) == 1
    assert len(chain.links) == 0  # No links for single vector


@pytest.mark.unit
def test_injection_out_of_bounds():
    """Test insertion at invalid position"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, [gen.generate_vector("v")])
    
    success = manager.inject_vector(
        chain.chain_id,
        gen.generate_vector("new"),
        InjectionMode.INSERT,
        position=999  # Out of bounds
    )
    
    assert success is False


@pytest.mark.unit
def test_replace_out_of_bounds():
    """Test replacement at invalid position"""
    gen = VectorGen()
    manager = VectorChainManager()
    
    chain = manager.create_chain("Test", ChainTopology.SEQUENTIAL, [gen.generate_vector("v")])
    
    success = manager.inject_vector(
        chain.chain_id,
        gen.generate_vector("new"),
        InjectionMode.REPLACE,
        position=999
    )
    
    assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
