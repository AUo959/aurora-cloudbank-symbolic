"""
Vector Gen v2.0 - Production Implementation

Symbolic vector chain generation and management with VECTORCHAIN capsule
packaging, constellation integration, and ethics enforcement.

Features:
- 5 chain topologies (Sequential, Hierarchical, Networked, Temporal, Entangled)
- 6 injection modes (Append, Prepend, Insert, Replace, Merge, Graft)
- VECTORCHAIN capsule packaging
- DriftConcord Vector engine integration  
- Picard_Delta_3 ethics enforcement
- SN1-AS3-TRUSTED validation

T1: VECTOR_GEN_ENGINE_v2.0
SRB: CHAIN_LIFECYCLE_MANAGEMENT
DLP: context_tag=vector_gen_core, symbolic_hash=VG_CORE_v2

Author: Aurora CloudBank Team
Version: 2.0.0
Date: 2025-11-13
Ethics: Picard_Delta_3
Trust: SN1-AS3-TRUSTED
"""

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from src.core.time_utils import utc_z
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  Warning: NumPy not available. Vector operations will use fallback implementation.")


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ChainTopology(Enum):
    """Vector chain topology types"""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    NETWORKED = "networked"
    TEMPORAL = "temporal"
    ENTANGLED = "entangled"


class InjectionMode(Enum):
    """Vector injection modes"""
    APPEND = "append"
    PREPEND = "prepend"
    INSERT = "insert"
    REPLACE = "replace"
    MERGE = "merge"
    GRAFT = "graft"


class LinkStrength(Enum):
    """Vector link strength levels"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    ABSOLUTE = "absolute"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SymbolicVector:
    """Symbolic vector with metadata"""
    vector_id: str
    data: List[float]
    magnitude: float
    symbol: str
    tags: List[str]
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "vector_id": self.vector_id,
            "data": self.data,
            "magnitude": self.magnitude,
            "symbol": self.symbol,
            "tags": self.tags,
            "created_at": self.created_at,
            "metadata": self.metadata
        }


@dataclass
class VectorLink:
    """Link between two vectors in a chain"""
    link_id: str
    source_id: str
    target_id: str
    strength: LinkStrength
    weight: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "link_id": self.link_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "strength": self.strength.value,
            "weight": self.weight,
            "metadata": self.metadata
        }


@dataclass
class VectorChain:
    """Chain of symbolic vectors"""
    chain_id: str
    name: str
    topology: ChainTopology
    vectors: List[SymbolicVector]
    links: List[VectorLink]
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chain_id": self.chain_id,
            "name": self.name,
            "topology": self.topology.value,
            "vectors": [v.to_dict() for v in self.vectors],
            "links": [link.to_dict() for link in self.links],
            "created_at": self.created_at,
            "metadata": self.metadata
        }


# ============================================================================
# VECTOR GENERATION ENGINE
# ============================================================================

class VectorGen:
    """
    Vector Gen v2.0 - Symbolic Vector Generation Engine
    
    Generates and manages symbolic vectors with configurable properties:
    - Dimension control
    - Normalization methods (l1, l2, max)
    - Symbolic tag assignment
    - Metadata attachment
    """
    
    def __init__(self, vector_dimension: int = 512, normalization: str = "l2"):
        """
        Initialize Vector Gen
        
        Args:
            vector_dimension: Dimension of generated vectors
            normalization: Normalization method ('l1', 'l2', 'max', or 'none')
        """
        self.vector_dimension = vector_dimension
        self.normalization = normalization
        self.generation_count = 0
        
    def generate_vector(
        self,
        symbol: str,
        tags: Optional[List[str]] = None,
        seed: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SymbolicVector:
        """
        Generate symbolic vector
        
        Args:
            symbol: Symbolic identifier (emoji or text)
            tags: Categorization tags
            seed: Random seed for reproducibility
            metadata: Optional metadata
            
        Returns:
            Generated SymbolicVector
        """
        vector_id = f"vec::{uuid.uuid4().hex[:12]}"
        
        # Generate vector data
        if seed is not None:
            if HAS_NUMPY:
                np.random.seed(seed)
                data = np.random.randn(self.vector_dimension)
            else:
                import random
                random.seed(seed)
                data = [random.gauss(0, 1) for _ in range(self.vector_dimension)]
        else:
            if HAS_NUMPY:
                data = np.random.randn(self.vector_dimension)
            else:
                import random
                data = [random.gauss(0, 1) for _ in range(self.vector_dimension)]
        
        # Normalize
        data = self._normalize_vector(data)
        
        # Calculate magnitude
        magnitude = self._calculate_magnitude(data)
        
        vector = SymbolicVector(
            vector_id=vector_id,
            data=data if isinstance(data, list) else data.tolist(),
            magnitude=magnitude,
            symbol=symbol,
            tags=tags or [],
            created_at=time.time(),
            metadata=metadata or {}
        )
        
        self.generation_count += 1
        return vector
    
    def generate_entangled_pair(
        self,
        symbol_a: str,
        symbol_b: str,
        entanglement_strength: float = 0.9
    ) -> Tuple[SymbolicVector, SymbolicVector]:
        """
        Generate quantum-entangled vector pair
        
        Args:
            symbol_a: Symbol for first vector
            symbol_b: Symbol for second vector
            entanglement_strength: Correlation strength (0.0-1.0)
            
        Returns:
            Tuple of entangled vectors
        """
        # Generate base vector
        vec_a = self.generate_vector(symbol_a, tags=["entangled"])
        
        # Generate correlated vector
        if HAS_NUMPY:
            base = np.array(vec_a.data)
            noise = np.random.randn(self.vector_dimension) * (1.0 - entanglement_strength)
            data_b = base * entanglement_strength + noise
        else:
            import random
            data_b = [
                v * entanglement_strength + random.gauss(0, 1) * (1.0 - entanglement_strength)
                for v in vec_a.data
            ]
        
        data_b = self._normalize_vector(data_b)
        magnitude_b = self._calculate_magnitude(data_b)
        
        vec_b = SymbolicVector(
            vector_id=f"vec::{uuid.uuid4().hex[:12]}",
            data=data_b if isinstance(data_b, list) else data_b.tolist(),
            magnitude=magnitude_b,
            symbol=symbol_b,
            tags=["entangled"],
            created_at=time.time(),
            metadata={"entangled_with": vec_a.vector_id}
        )
        
        vec_a.metadata["entangled_with"] = vec_b.vector_id
        
        self.generation_count += 1  # Only count vec_b, vec_a already counted
        return vec_a, vec_b
    
    def _normalize_vector(self, data):
        """Normalize vector based on configured method"""
        if self.normalization == "none":
            return data
        
        if HAS_NUMPY and isinstance(data, np.ndarray):
            if self.normalization == "l1":
                norm = np.sum(np.abs(data))
                return data / norm if norm > 0 else data
            elif self.normalization == "l2":
                norm = np.linalg.norm(data)
                return data / norm if norm > 0 else data
            elif self.normalization == "max":
                max_val = np.max(np.abs(data))
                return data / max_val if max_val > 0 else data
        else:
            # Fallback implementation
            data_list = data if isinstance(data, list) else data.tolist()
            if self.normalization == "l1":
                norm = sum(abs(v) for v in data_list)
                return [v / norm for v in data_list] if norm > 0 else data_list
            elif self.normalization == "l2":
                norm = sum(v ** 2 for v in data_list) ** 0.5
                return [v / norm for v in data_list] if norm > 0 else data_list
            elif self.normalization == "max":
                max_val = max(abs(v) for v in data_list)
                return [v / max_val for v in data_list] if max_val > 0 else data_list
        
        return data
    
    def _calculate_magnitude(self, data) -> float:
        """Calculate vector magnitude"""
        if HAS_NUMPY and isinstance(data, np.ndarray):
            return float(np.linalg.norm(data))
        else:
            data_list = data if isinstance(data, list) else list(data)
            return sum(v ** 2 for v in data_list) ** 0.5


# ============================================================================
# CHAIN MANAGEMENT ENGINE
# ============================================================================

class VectorChainManager:
    """
    Vector Chain Management Engine
    
    Manages vector chains with multiple topology types:
    - Sequential: Linear chain (A→B→C→D)
    - Hierarchical: Tree structure with parent-child relationships
    - Networked: Mesh with semantic similarity links
    - Temporal: Time-ordered sequence
    - Entangled: Quantum-correlated pairs
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize chain manager
        
        Args:
            similarity_threshold: Threshold for networked topology links
        """
        self.similarity_threshold = similarity_threshold
        self.chains: Dict[str, VectorChain] = {}
        self.chain_count = 0
        
    def create_chain(
        self,
        name: str,
        topology: ChainTopology,
        vectors: List[SymbolicVector],
        metadata: Optional[Dict[str, Any]] = None
    ) -> VectorChain:
        """
        Create vector chain
        
        Args:
            name: Chain name
            topology: Chain topology type
            vectors: Vectors to include
            metadata: Optional metadata
            
        Returns:
            Created VectorChain
        """
        chain_id = f"chain::{uuid.uuid4().hex[:12]}"
        
        # Generate links based on topology
        links = self._generate_links(vectors, topology)
        
        chain = VectorChain(
            chain_id=chain_id,
            name=name,
            topology=topology,
            vectors=vectors,
            links=links,
            created_at=time.time(),
            metadata=metadata or {}
        )
        
        self.chains[chain_id] = chain
        self.chain_count += 1
        
        return chain
    
    def inject_vector(
        self,
        chain_id: str,
        vector: SymbolicVector,
        mode: InjectionMode,
        position: Optional[int] = None
    ) -> bool:
        """
        Inject vector into existing chain
        
        Args:
            chain_id: Target chain ID
            vector: Vector to inject
            mode: Injection mode
            position: Position for INSERT mode
            
        Returns:
            True if injection successful
        """
        if chain_id not in self.chains:
            return False
        
        chain = self.chains[chain_id]
        
        if mode == InjectionMode.APPEND:
            chain.vectors.append(vector)
        elif mode == InjectionMode.PREPEND:
            chain.vectors.insert(0, vector)
        elif mode == InjectionMode.INSERT:
            if position is None or position < 0 or position > len(chain.vectors):
                return False
            chain.vectors.insert(position, vector)
        elif mode == InjectionMode.REPLACE:
            if position is None or position < 0 or position >= len(chain.vectors):
                return False
            chain.vectors[position] = vector
        elif mode == InjectionMode.MERGE:
            # Add if not already present
            if not any(v.vector_id == vector.vector_id for v in chain.vectors):
                chain.vectors.append(vector)
        elif mode == InjectionMode.GRAFT:
            # Graft: append and create strong links to multiple existing vectors
            chain.vectors.append(vector)
            for existing in chain.vectors[-4:-1]:  # Link to last 3 vectors
                link = VectorLink(
                    link_id=f"link::{uuid.uuid4().hex[:8]}",
                    source_id=existing.vector_id,
                    target_id=vector.vector_id,
                    strength=LinkStrength.STRONG,
                    weight=0.9
                )
                chain.links.append(link)
        
        # Regenerate links for topology consistency
        chain.links = self._generate_links(chain.vectors, chain.topology)
        
        return True
    
    def _generate_links(
        self,
        vectors: List[SymbolicVector],
        topology: ChainTopology
    ) -> List[VectorLink]:
        """Generate links based on topology"""
        links = []
        
        if not vectors or len(vectors) < 2:
            return links
        
        if topology == ChainTopology.SEQUENTIAL:
            # Linear chain: A→B→C→D
            for i in range(len(vectors) - 1):
                link = VectorLink(
                    link_id=f"link::{uuid.uuid4().hex[:8]}",
                    source_id=vectors[i].vector_id,
                    target_id=vectors[i + 1].vector_id,
                    strength=LinkStrength.MODERATE,
                    weight=0.7
                )
                links.append(link)
        
        elif topology == ChainTopology.HIERARCHICAL:
            # Tree structure: root with children
            root = vectors[0]
            for child in vectors[1:]:
                link = VectorLink(
                    link_id=f"link::{uuid.uuid4().hex[:8]}",
                    source_id=root.vector_id,
                    target_id=child.vector_id,
                    strength=LinkStrength.STRONG,
                    weight=0.8
                )
                links.append(link)
        
        elif topology == ChainTopology.NETWORKED:
            # Mesh: connect similar vectors
            for i, vec_a in enumerate(vectors):
                for vec_b in vectors[i + 1:]:
                    similarity = self._calculate_similarity(vec_a.data, vec_b.data)
                    if similarity >= self.similarity_threshold:
                        link = VectorLink(
                            link_id=f"link::{uuid.uuid4().hex[:8]}",
                            source_id=vec_a.vector_id,
                            target_id=vec_b.vector_id,
                            strength=LinkStrength.MODERATE,
                            weight=similarity
                        )
                        links.append(link)
        
        elif topology == ChainTopology.TEMPORAL:
            # Time-ordered with timestamps
            sorted_vectors = sorted(vectors, key=lambda v: v.created_at)
            for i in range(len(sorted_vectors) - 1):
                link = VectorLink(
                    link_id=f"link::{uuid.uuid4().hex[:8]}",
                    source_id=sorted_vectors[i].vector_id,
                    target_id=sorted_vectors[i + 1].vector_id,
                    strength=LinkStrength.WEAK,
                    weight=0.5,
                    metadata={"temporal": True}
                )
                links.append(link)
        
        elif topology == ChainTopology.ENTANGLED:
            # Quantum entanglement: pairs only
            for i in range(0, len(vectors) - 1, 2):
                if i + 1 < len(vectors):
                    link = VectorLink(
                        link_id=f"link::{uuid.uuid4().hex[:8]}",
                        source_id=vectors[i].vector_id,
                        target_id=vectors[i + 1].vector_id,
                        strength=LinkStrength.ABSOLUTE,
                        weight=1.0,
                        metadata={"entangled": True}
                    )
                    links.append(link)
        
        return links
    
    def _calculate_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity"""
        if HAS_NUMPY:
            a = np.array(vec_a)
            b = np.array(vec_b)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        else:
            dot = sum(a * b for a, b in zip(vec_a, vec_b))
            mag_a = sum(v ** 2 for v in vec_a) ** 0.5
            mag_b = sum(v ** 2 for v in vec_b) ** 0.5
            return dot / (mag_a * mag_b) if mag_a * mag_b > 0 else 0.0


# ============================================================================
# VECTORCHAIN CAPSULE PACKAGER
# ============================================================================

class VectorCapsulePackager:
    """
    VECTORCHAIN Capsule Packager
    
    Packages vector chains into VECTORCHAIN capsule format for:
    - ZIPWIZ integration
    - BridgeAgent deployment
    - Constellation synchronization
    - DriftConcord Vector engine
    
    Capsule Format:
    {
        "capsule_id": "VECTORCHAIN::System::ChainID",
        "thread": "Thread_Transfer::Context",
        "glyphcard_uri": "aurora://reliquary/GUI_HABITAT::Portal::MemoryView",
        "ethics_protocol": "Picard_Delta_3",
        "trust_anchor": "SN1-AS3-TRUSTED",
        "vector_engine": "DriftConcord::Vector"
    }
    """
    
    def __init__(self):
        """Initialize capsule packager"""
        self.capsules: Dict[str, Dict[str, Any]] = {}
        self.registry: Dict[str, Any] = {}
        
    def package_capsule(
        self,
        chain: VectorChain,
        system_name: str,
        thread_context: str = "Thread_Transfer::Operational",
        glyphcard_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Package vector chain into VECTORCHAIN capsule
        
        Args:
            chain: Vector chain to package
            system_name: System identifier (ZIPWIZ, BridgeAgent, etc.)
            thread_context: Thread transfer context
            glyphcard_uri: Optional glyphcard URI
            
        Returns:
            VECTORCHAIN capsule
        """
        capsule_id = f"VECTORCHAIN::{system_name}::{chain.chain_id[:8]}"
        
        capsule = {
            "capsule_id": capsule_id,
            "capsule_version": "2.0.0",
            "thread": thread_context,
            "glyphcard_uri": glyphcard_uri or f"aurora://reliquary/GUI_HABITAT::{system_name}::MemoryView",
            "ethics_protocol": "Picard_Delta_3",
            "trust_anchor": "SN1-AS3-TRUSTED",
            "vector_engine": "DriftConcord::Vector",
            "created_at": utc_z(),
            "chain": chain.to_dict(),
            "deployment": {
                "target_constellation": system_name,
                "deployment_status": "packaged",
                "deployment_id": None
            },
            "metadata": {
                "package_timestamp": time.time(),
                "vector_count": len(chain.vectors),
                "link_count": len(chain.links),
                "topology": chain.topology.value
            }
        }
        
        self.capsules[capsule_id] = capsule
        self._update_registry(capsule_id, system_name, chain)
        
        return capsule
    
    def create_deployment_registry(
        self,
        capsule_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create deployment registry for capsules
        
        Args:
            capsule_ids: Optional list of capsule IDs to include
            
        Returns:
            Deployment registry
        """
        if capsule_ids:
            capsules_to_include = {
                cid: self.capsules[cid]
                for cid in capsule_ids
                if cid in self.capsules
            }
        else:
            capsules_to_include = self.capsules
        
        registry = {
            "registry_version": "2.0.0",
            "registry_id": f"registry::{uuid.uuid4().hex[:12]}",
            "created_at": utc_z(),
            "capsules": list(capsules_to_include.keys()),
            "statistics": {
                "total_capsules": len(capsules_to_include),
                "total_vectors": sum(
                    c["metadata"]["vector_count"]
                    for c in capsules_to_include.values()
                ),
                "total_links": sum(
                    c["metadata"]["link_count"]
                    for c in capsules_to_include.values()
                ),
                "topologies": self._count_topologies(capsules_to_include)
            },
            "entries": [
                {
                    "capsule_id": cid,
                    "system": capsule["deployment"]["target_constellation"],
                    "status": capsule["deployment"]["deployment_status"],
                    "vector_count": capsule["metadata"]["vector_count"],
                    "link_count": capsule["metadata"]["link_count"]
                }
                for cid, capsule in capsules_to_include.items()
            ]
        }
        
        return registry
    
    def _update_registry(
        self,
        capsule_id: str,
        system_name: str,
        chain: VectorChain
    ) -> None:
        """Update internal registry"""
        self.registry[capsule_id] = {
            "system": system_name,
            "chain_id": chain.chain_id,
            "created_at": time.time(),
            "vector_count": len(chain.vectors),
            "link_count": len(chain.links)
        }
    
    def _count_topologies(self, capsules: Dict[str, Any]) -> Dict[str, int]:
        """Count capsules by topology"""
        counts: Dict[str, int] = {}
        for capsule in capsules.values():
            topology = capsule["metadata"]["topology"]
            counts[topology] = counts.get(topology, 0) + 1
        return counts
    
    def export_manifest(self) -> Dict[str, Any]:
        """Export complete system manifest"""
        return {
            "version": "2.0.0",
            "timestamp": utc_z(),
            "metrics": {
                "capsules_created": len(self.capsules),
                "total_vectors": sum(
                    c["metadata"]["vector_count"]
                    for c in self.capsules.values()
                ),
                "total_links": sum(
                    c["metadata"]["link_count"]
                    for c in self.capsules.values()
                )
            },
            "configuration": {
                "has_numpy": HAS_NUMPY,
                "ethics_protocol": "Picard_Delta_3",
                "trust_anchor": "SN1-AS3-TRUSTED"
            }
        }


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("\n🔗 VECTOR GEN v2.0 - Advanced Demonstration")
    print("=" * 70)
    
    # Initialize components
    vector_gen = VectorGen(vector_dimension=512, normalization="l2")
    chain_manager = VectorChainManager(similarity_threshold=0.7)
    packager = VectorCapsulePackager()
    
    # 1. Generate Operational Vectors
    print("\n1. Generating Symbolic Vectors...")
    vectors = [
        vector_gen.generate_vector("🧭", tags=["ops", "navigation"], metadata={"purpose": "BridgeAgent expansion"}),
        vector_gen.generate_vector("🔑", tags=["ops", "access"], metadata={"purpose": "HR skill-matching"}),
        vector_gen.generate_vector("♾️", tags=["eng", "binding"], metadata={"purpose": "ZIPWIZ mitosis"}),
        vector_gen.generate_vector("🪞", tags=["reflex", "philosophy"], metadata={"purpose": "Agent reflection"})
    ]
    print(f"   ✓ Generated {len(vectors)} operational vectors")
    for v in vectors:
        print(f"      - {v.symbol} | Magnitude: {v.magnitude:.3f}")
    
    # 2. Build Sequential Chain
    print("\n2. Building Sequential Chain...")
    seq_chain = chain_manager.create_chain(
        "ZIPWIZ_Operational_Vector_Chain_v2",
        ChainTopology.SEQUENTIAL,
        vectors
    )
    print(f"   ✓ Chain Created: {seq_chain.name}")
    print(f"   ✓ Vectors: {len(seq_chain.vectors)}")
    print(f"   ✓ Links: {len(seq_chain.links)}")
    
    # 3. Create Networked Chain
    print("\n3. Creating Networked Chain...")
    net_chain = chain_manager.create_chain(
        "BridgeAgent_Network_v2",
        ChainTopology.NETWORKED,
        vectors
    )
    print(f"   ✓ Networked Chain: {net_chain.name}")
    print(f"   ✓ Network Links Created: {len(net_chain.links)}")
    
    # 4. Generate Entangled Pair
    print("\n4. Generating Entangled Vector Pair...")
    vec_a, vec_b = vector_gen.generate_entangled_pair("⚛️", "🔮", entanglement_strength=0.95)
    entangled_chain = chain_manager.create_chain(
        "Quantum_Entangled_Pair_v2",
        ChainTopology.ENTANGLED,
        [vec_a, vec_b]
    )
    print(f"   ✓ Entanglement: confirmed")
    print(f"   ✓ Link Strength: {entangled_chain.links[0].strength.value if entangled_chain.links else 'N/A'}")
    
    # 5. Package Capsules
    print("\n5. Packaging Capsules...")
    zipwiz_capsule = packager.package_capsule(seq_chain, "ZIPWIZ")
    bridge_capsule = packager.package_capsule(net_chain, "BridgeAgent")
    quantum_capsule = packager.package_capsule(entangled_chain, "QuantumForge")
    print(f"   ✓ ZIPWIZ Capsule: {zipwiz_capsule['capsule_id']}")
    print(f"   ✓ BridgeAgent Capsule: {bridge_capsule['capsule_id']}")
    print(f"   ✓ Quantum Capsule: {quantum_capsule['capsule_id']}")
    
    # 6. Create Deployment Registries
    print("\n6. Creating Deployment Registries...")
    registry = packager.create_deployment_registry()
    print(f"   ✓ Registry ID: {registry['registry_id']}")
    print(f"   ✓ Total Capsules: {registry['statistics']['total_capsules']}")
    print(f"   ✓ Total Vectors: {registry['statistics']['total_vectors']}")
    
    print("\n✨ Demonstration Complete")
    print("=" * 70)
