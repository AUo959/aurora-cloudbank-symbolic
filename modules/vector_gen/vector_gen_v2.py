#!/usr/bin/env python3
"""
🔗 VECTOR GEN v2.0 - Advanced Symbolic Vector Chain Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enterprise-grade vector generation and symbolic chain management system

Module Type: Vector Generation & Chain Management
Engine: DriftConcord Vector v2.0
Status: PRODUCTION
Integration: ZIPWIZ, BridgeAgent, Quantum Forge
Ethics: Picard_Delta_3 Protocol
Version: 2.0.0
Date: 2025-11-12
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import hashlib
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import uuid


# ═══════════════════════════════════════════════════════════════════════════════
# CORE ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class VectorChainType(Enum):
    """Types of symbolic vector chains"""
    SEQUENTIAL = "sequential"           # Linear chain
    HIERARCHICAL = "hierarchical"       # Tree structure
    NETWORKED = "networked"             # Graph structure
    TEMPORAL = "temporal"               # Time-based progression
    ENTANGLED = "entangled"             # Quantum-style connections


class ChainLinkStrength(Enum):
    """Strength of connections between vectors"""
    WEAK = 0.3
    MODERATE = 0.6
    STRONG = 0.9
    ABSOLUTE = 1.0


class VectorInjectionMode(Enum):
    """How vectors are injected into the chain"""
    APPEND = "append"               # Add to end
    PREPEND = "prepend"             # Add to beginning
    INSERT = "insert"               # Insert at position
    REPLACE = "replace"             # Replace existing
    MERGE = "merge"                 # Merge with existing
    GRAFT = "graft"                 # Modular grafting


class ConstellationTarget(Enum):
    """Target constellation systems"""
    ORION = "ORION"
    ZIPWIZ = "ZIPWIZ"
    BRIDGE_AGENT = "BridgeAgent"
    QUANTUM_FORGE = "QuantumForge"
    DRIFT_CONCORD = "DriftConcord"


# ═══════════════════════════════════════════════════════════════════════════════
# CORE DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SymbolicVector:
    """Enhanced symbolic vector with full metadata"""
    vector_id: str
    vector: np.ndarray
    symbolic_tag: str
    dimension: int
    magnitude: float
    phase: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "vector_id": self.vector_id,
            "vector": self.vector.tolist(),
            "symbolic_tag": self.symbolic_tag,
            "dimension": self.dimension,
            "magnitude": float(self.magnitude),
            "phase": float(self.phase),
            "metadata": self.metadata,
            "creation_timestamp": self.creation_timestamp
        }


@dataclass
class ChainLink:
    """Link in a symbolic vector chain"""
    link_id: str
    source_vector: SymbolicVector
    target_vector: SymbolicVector
    strength: ChainLinkStrength
    relationship: str
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "link_id": self.link_id,
            "source_vector_id": self.source_vector.vector_id,
            "target_vector_id": self.target_vector.vector_id,
            "strength": self.strength.value,
            "relationship": self.relationship,
            "bidirectional": self.bidirectional,
            "metadata": self.metadata
        }


@dataclass
class VectorChain:
    """Symbolic vector chain structure"""
    chain_id: str
    chain_type: VectorChainType
    vectors: List[SymbolicVector]
    links: List[ChainLink]
    constellation_target: ConstellationTarget
    ethics_protocol: str = "Picard_Delta_3"
    trust_anchor: str = "SN1-AS3-TRUSTED"
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "chain_id": self.chain_id,
            "chain_type": self.chain_type.value,
            "vectors": [v.to_dict() for v in self.vectors],
            "links": [l.to_dict() for l in self.links],
            "constellation_target": self.constellation_target.value,
            "ethics_protocol": self.ethics_protocol,
            "trust_anchor": self.trust_anchor,
            "metadata": self.metadata,
            "creation_timestamp": self.creation_timestamp
        }


@dataclass
class VectorCapsule:
    """VECTORCHAIN capsule for deployment"""
    capsule_id: str
    chain: VectorChain
    thread: str
    glyphcard_uri: str
    vector_engine: str = "DriftConcord::Vector"
    status: str = "registered"
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "capsule_id": self.capsule_id,
            "chain": self.chain.to_dict(),
            "thread": self.thread,
            "glyphcard_uri": self.glyphcard_uri,
            "ethics_protocol": self.chain.ethics_protocol,
            "trust_anchor": self.chain.trust_anchor,
            "vector_engine": self.vector_engine,
            "timestamp_utc": self.timestamp_utc,
            "status": self.status,
            "purpose": "Replayable symbolic vector chain for constellation integration"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOLIC VECTOR GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SymbolicVectorGenerator:
    """
    Advanced symbolic vector generation engine
    Integrates with Quantum Forge and DriftConcord systems
    """
    
    def __init__(self, default_dimension: int = 512):
        self.default_dimension = default_dimension
        self.generation_history: List[Dict[str, Any]] = []
        self.vector_registry: Dict[str, SymbolicVector] = {}
        
    def generate_vector(self,
                       symbolic_tag: str,
                       seed: Optional[str] = None,
                       dimension: Optional[int] = None,
                       normalization: str = "l2") -> SymbolicVector:
        """
        Generate symbolic vector from tag
        
        Args:
            symbolic_tag: Symbolic identifier/emoji/concept
            seed: Optional seed for reproducibility
            dimension: Vector dimension (defaults to self.default_dimension)
            normalization: Normalization method ('l2', 'l1', 'max', or None)
        """
        dim = dimension or self.default_dimension
        
        # Generate deterministic vector from tag
        hash_input = seed or symbolic_tag
        hash_val = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        
        # Generate base vector
        vector = np.random.randn(dim)
        
        # Apply tag-specific transformations
        if "🧭" in symbolic_tag:  # Navigation/operations
            vector = np.fft.fft(vector).real
        elif "🔑" in symbolic_tag:  # Key/critical
            vector = np.abs(vector) * np.sign(vector)
        elif "♾️" in symbolic_tag:  # Infinite/recursive
            vector = np.tanh(vector) * 2
        elif "🪞" in symbolic_tag:  # Reflection/mirror
            vector = np.flip(vector)
        
        # Normalize
        if normalization == "l2":
            vector = vector / (np.linalg.norm(vector) + 1e-10)
        elif normalization == "l1":
            vector = vector / (np.sum(np.abs(vector)) + 1e-10)
        elif normalization == "max":
            vector = vector / (np.max(np.abs(vector)) + 1e-10)
        
        # Calculate properties
        magnitude = float(np.linalg.norm(vector))
        phase = float(np.angle(np.sum(vector * np.exp(2j * np.pi * np.arange(dim) / dim))))
        
        # Create vector object
        vector_id = hashlib.sha256(f"{symbolic_tag}:{hash_input}".encode()).hexdigest()[:16]
        
        symbolic_vector = SymbolicVector(
            vector_id=vector_id,
            vector=vector,
            symbolic_tag=symbolic_tag,
            dimension=dim,
            magnitude=magnitude,
            phase=phase,
            metadata={
                "seed": hash_input,
                "normalization": normalization,
                "generation_method": "symbolic_tag_transform"
            }
        )
        
        # Register
        self.vector_registry[vector_id] = symbolic_vector
        
        # Log generation
        self.generation_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "vector_id": vector_id,
            "symbolic_tag": symbolic_tag,
            "dimension": dim
        })
        
        return symbolic_vector
    
    def generate_operational_vectors(self,
                                    operations: List[Dict[str, str]]) -> List[SymbolicVector]:
        """
        Generate vectors for operational contexts
        
        Args:
            operations: List of dicts with 'tag', 'id', and 'text' keys
        """
        vectors = []
        
        for op in operations:
            vector = self.generate_vector(
                symbolic_tag=op.get("tag", "🔗"),
                seed=op.get("id", "") + op.get("text", ""),
                dimension=self.default_dimension
            )
            
            vector.metadata.update({
                "operation_id": op.get("id", ""),
                "operation_text": op.get("text", ""),
                "operation_type": "operational_vector"
            })
            
            vectors.append(vector)
        
        return vectors
    
    def generate_entangled_pair(self,
                               tag_a: str,
                               tag_b: str) -> Tuple[SymbolicVector, SymbolicVector]:
        """Generate quantum-entangled vector pair"""
        # Generate first vector
        vec_a = self.generate_vector(tag_a)
        
        # Generate entangled partner using quantum-inspired transformation
        entangled_data = vec_a.vector.copy()
        entangled_data = np.fft.fft(entangled_data).real
        entangled_data = entangled_data / (np.linalg.norm(entangled_data) + 1e-10)
        
        vec_b_id = hashlib.sha256(f"entangled:{tag_b}:{vec_a.vector_id}".encode()).hexdigest()[:16]
        
        vec_b = SymbolicVector(
            vector_id=vec_b_id,
            vector=entangled_data,
            symbolic_tag=tag_b,
            dimension=vec_a.dimension,
            magnitude=float(np.linalg.norm(entangled_data)),
            phase=float(np.angle(np.sum(entangled_data))),
            metadata={
                "entangled_with": vec_a.vector_id,
                "entanglement_type": "quantum_fft",
                "generation_method": "entangled_pair"
            }
        )
        
        # Register
        self.vector_registry[vec_b.vector_id] = vec_b
        
        # Update vec_a metadata
        vec_a.metadata["entangled_with"] = vec_b.vector_id
        
        return vec_a, vec_b


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR CHAIN BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

class VectorChainBuilder:
    """
    Build and manage symbolic vector chains
    Implements various chain topologies and connection patterns
    """
    
    def __init__(self, generator: SymbolicVectorGenerator):
        self.generator = generator
        self.chains: Dict[str, VectorChain] = {}
        self.chain_history: List[Dict[str, Any]] = []
        
    def create_chain(self,
                    chain_type: VectorChainType,
                    constellation_target: ConstellationTarget,
                    chain_name: Optional[str] = None) -> VectorChain:
        """Create new vector chain"""
        chain_id = chain_name or f"CHAIN_{uuid.uuid4().hex[:16]}"
        
        chain = VectorChain(
            chain_id=chain_id,
            chain_type=chain_type,
            vectors=[],
            links=[],
            constellation_target=constellation_target,
            metadata={
                "builder_version": "2.0.0",
                "chain_name": chain_name
            }
        )
        
        self.chains[chain_id] = chain
        
        self.chain_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "create_chain",
            "chain_id": chain_id,
            "chain_type": chain_type.value
        })
        
        return chain
    
    def inject_vector(self,
                     chain_id: str,
                     vector: SymbolicVector,
                     mode: VectorInjectionMode = VectorInjectionMode.APPEND,
                     position: Optional[int] = None) -> bool:
        """Inject vector into chain"""
        if chain_id not in self.chains:
            return False
        
        chain = self.chains[chain_id]
        
        if mode == VectorInjectionMode.APPEND:
            chain.vectors.append(vector)
        elif mode == VectorInjectionMode.PREPEND:
            chain.vectors.insert(0, vector)
        elif mode == VectorInjectionMode.INSERT and position is not None:
            chain.vectors.insert(position, vector)
        elif mode == VectorInjectionMode.REPLACE and position is not None:
            if 0 <= position < len(chain.vectors):
                chain.vectors[position] = vector
        elif mode == VectorInjectionMode.MERGE:
            # Merge with last vector if exists
            if chain.vectors:
                last_vec = chain.vectors[-1]
                merged = (last_vec.vector + vector.vector) / 2
                merged = merged / (np.linalg.norm(merged) + 1e-10)
                
                merged_vec = SymbolicVector(
                    vector_id=f"merged_{last_vec.vector_id[:8]}_{vector.vector_id[:8]}",
                    vector=merged,
                    symbolic_tag=f"{last_vec.symbolic_tag}+{vector.symbolic_tag}",
                    dimension=vector.dimension,
                    magnitude=float(np.linalg.norm(merged)),
                    phase=float(np.angle(np.sum(merged))),
                    metadata={
                        "merged_from": [last_vec.vector_id, vector.vector_id],
                        "merge_method": "average"
                    }
                )
                chain.vectors[-1] = merged_vec
            else:
                chain.vectors.append(vector)
        
        self.chain_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "inject_vector",
            "chain_id": chain_id,
            "vector_id": vector.vector_id,
            "mode": mode.value
        })
        
        return True
    
    def create_link(self,
                   chain_id: str,
                   source_idx: int,
                   target_idx: int,
                   relationship: str,
                   strength: ChainLinkStrength = ChainLinkStrength.STRONG,
                   bidirectional: bool = False) -> Optional[ChainLink]:
        """Create link between vectors in chain"""
        if chain_id not in self.chains:
            return None
        
        chain = self.chains[chain_id]
        
        if not (0 <= source_idx < len(chain.vectors) and 
                0 <= target_idx < len(chain.vectors)):
            return None
        
        source_vec = chain.vectors[source_idx]
        target_vec = chain.vectors[target_idx]
        
        link_id = hashlib.sha256(
            f"{source_vec.vector_id}:{target_vec.vector_id}:{relationship}".encode()
        ).hexdigest()[:16]
        
        link = ChainLink(
            link_id=link_id,
            source_vector=source_vec,
            target_vector=target_vec,
            strength=strength,
            relationship=relationship,
            bidirectional=bidirectional,
            metadata={
                "source_idx": source_idx,
                "target_idx": target_idx
            }
        )
        
        chain.links.append(link)
        
        self.chain_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "create_link",
            "chain_id": chain_id,
            "link_id": link_id
        })
        
        return link
    
    def auto_link_sequential(self,
                            chain_id: str,
                            strength: ChainLinkStrength = ChainLinkStrength.STRONG) -> int:
        """Auto-create sequential links in chain"""
        if chain_id not in self.chains:
            return 0
        
        chain = self.chains[chain_id]
        links_created = 0
        
        for i in range(len(chain.vectors) - 1):
            self.create_link(
                chain_id=chain_id,
                source_idx=i,
                target_idx=i + 1,
                relationship="sequential_next",
                strength=strength,
                bidirectional=False
            )
            links_created += 1
        
        return links_created
    
    def auto_link_hierarchical(self,
                              chain_id: str,
                              branching_factor: int = 2) -> int:
        """Auto-create hierarchical (tree) links"""
        if chain_id not in self.chains:
            return 0
        
        chain = self.chains[chain_id]
        links_created = 0
        
        for i in range(len(chain.vectors)):
            for j in range(branching_factor):
                child_idx = i * branching_factor + j + 1
                if child_idx < len(chain.vectors):
                    self.create_link(
                        chain_id=chain_id,
                        source_idx=i,
                        target_idx=child_idx,
                        relationship="parent_child",
                        strength=ChainLinkStrength.STRONG,
                        bidirectional=False
                    )
                    links_created += 1
        
        return links_created
    
    def auto_link_networked(self,
                           chain_id: str,
                           similarity_threshold: float = 0.7) -> int:
        """Auto-create networked links based on vector similarity"""
        if chain_id not in self.chains:
            return 0
        
        chain = self.chains[chain_id]
        links_created = 0
        
        for i in range(len(chain.vectors)):
            for j in range(i + 1, len(chain.vectors)):
                vec_i = chain.vectors[i]
                vec_j = chain.vectors[j]
                
                # Calculate similarity
                similarity = np.dot(vec_i.vector, vec_j.vector) / (
                    np.linalg.norm(vec_i.vector) * np.linalg.norm(vec_j.vector) + 1e-10
                )
                
                if similarity >= similarity_threshold:
                    strength = ChainLinkStrength.STRONG if similarity > 0.9 else ChainLinkStrength.MODERATE
                    
                    self.create_link(
                        chain_id=chain_id,
                        source_idx=i,
                        target_idx=j,
                        relationship="semantic_similarity",
                        strength=strength,
                        bidirectional=True
                    )
                    links_created += 1
        
        return links_created
    
    def build_from_operational_vectors(self,
                                      operations: List[Dict[str, str]],
                                      constellation_target: ConstellationTarget,
                                      chain_name: Optional[str] = None) -> VectorChain:
        """Build chain from operational vector specifications"""
        # Generate vectors
        vectors = self.generator.generate_operational_vectors(operations)
        
        # Create chain
        chain = self.create_chain(
            chain_type=VectorChainType.SEQUENTIAL,
            constellation_target=constellation_target,
            chain_name=chain_name
        )
        
        # Inject vectors
        for vector in vectors:
            self.inject_vector(chain.chain_id, vector, VectorInjectionMode.APPEND)
        
        # Auto-link
        self.auto_link_sequential(chain.chain_id)
        
        return chain


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR CAPSULE PACKAGER
# ═══════════════════════════════════════════════════════════════════════════════

class VectorCapsulePackager:
    """
    Package vector chains into VECTORCHAIN capsules
    Ready for deployment to constellation systems
    """
    
    def __init__(self):
        self.capsules: Dict[str, VectorCapsule] = {}
        self.packaging_history: List[Dict[str, Any]] = []
        
    def package_chain(self,
                     chain: VectorChain,
                     thread_name: str,
                     glyphcard_base: str = "aurora://reliquary/GUI_HABITAT") -> VectorCapsule:
        """Package chain into deployable capsule"""
        capsule_id = f"VECTORCHAIN::{chain.constellation_target.value}::{chain.chain_id}"
        
        glyphcard_uri = f"{glyphcard_base}::{chain.constellation_target.value}Portal::MemoryView"
        
        capsule = VectorCapsule(
            capsule_id=capsule_id,
            chain=chain,
            thread=thread_name,
            glyphcard_uri=glyphcard_uri
        )
        
        self.capsules[capsule_id] = capsule
        
        self.packaging_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "package_chain",
            "capsule_id": capsule_id,
            "chain_id": chain.chain_id
        })
        
        return capsule
    
    def export_capsule(self, capsule_id: str, filepath: str) -> bool:
        """Export capsule to JSON file"""
        if capsule_id not in self.capsules:
            return False
        
        capsule = self.capsules[capsule_id]
        
        with open(filepath, 'w') as f:
            json.dump(capsule.to_dict(), f, indent=2)
        
        return True
    
    def create_deployment_registry(self, capsule_id: str) -> Dict[str, Any]:
        """Create deployment registry entry"""
        if capsule_id not in self.capsules:
            return {}
        
        capsule = self.capsules[capsule_id]
        
        return {
            "capsule_id": capsule_id,
            "thread": capsule.thread,
            "glyphcard_uri": capsule.glyphcard_uri,
            "ethics_protocol": capsule.chain.ethics_protocol,
            "trust_anchor": capsule.chain.trust_anchor,
            "vector_engine": capsule.vector_engine,
            "timestamp_utc": capsule.timestamp_utc,
            "status": capsule.status,
            "purpose": "Replayable symbolic vector chain for constellation integration",
            "chain_stats": {
                "vectors": len(capsule.chain.vectors),
                "links": len(capsule.chain.links),
                "chain_type": capsule.chain.chain_type.value
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE & DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def demonstration():
    """Comprehensive demonstration of Vector Gen v2.0"""
    print("🔗 VECTOR GEN v2.0 - Advanced Demonstration")
    print("═" * 70)
    
    # Initialize systems
    generator = SymbolicVectorGenerator(default_dimension=512)
    builder = VectorChainBuilder(generator)
    packager = VectorCapsulePackager()
    
    print("\n1. Generating Symbolic Vectors...")
    
    # Generate operational vectors (from original QUANTUM_FORGE data)
    operations = [
        {
            "tag": "🧭",
            "id": "vector::ops.alex_thorne_meeting",
            "text": "BridgeAgent expansion discussion with use-case anchor"
        },
        {
            "tag": "🔑",
            "id": "vector::ops.hr_initiative",
            "text": "Symbolic skill-matching for new roles with QUANTUM_FORGE"
        },
        {
            "tag": "♾️",
            "id": "vector::eng.bindings.carmen_flash",
            "text": "ZIPWIZ recursive bug: symbolic mitosis in port map"
        },
        {
            "tag": "🪞",
            "id": "vector::reflex.elira_noor_sync",
            "text": "Agent reflection: creating vs. discovering patterns"
        }
    ]
    
    vectors = generator.generate_operational_vectors(operations)
    print(f"   ✓ Generated {len(vectors)} operational vectors")
    for v in vectors:
        print(f"      - {v.symbolic_tag} | ID: {v.vector_id} | Magnitude: {v.magnitude:.3f}")
    
    print("\n2. Building Sequential Chain...")
    chain = builder.build_from_operational_vectors(
        operations=operations,
        constellation_target=ConstellationTarget.ZIPWIZ,
        chain_name="ZIPWIZ_Operational_Vector_Chain_v2"
    )
    print(f"   ✓ Chain Created: {chain.chain_id}")
    print(f"   ✓ Vectors: {len(chain.vectors)}")
    print(f"   ✓ Links: {len(chain.links)}")
    
    print("\n3. Creating Networked Chain...")
    networked_chain = builder.create_chain(
        chain_type=VectorChainType.NETWORKED,
        constellation_target=ConstellationTarget.BRIDGE_AGENT,
        chain_name="BridgeAgent_Network_v2"
    )
    
    # Add vectors
    for v in vectors:
        builder.inject_vector(networked_chain.chain_id, v)
    
    # Create network links
    links_created = builder.auto_link_networked(
        networked_chain.chain_id,
        similarity_threshold=0.6
    )
    print(f"   ✓ Networked Chain: {networked_chain.chain_id}")
    print(f"   ✓ Network Links Created: {links_created}")
    
    print("\n4. Generating Entangled Vector Pair...")
    vec_a, vec_b = generator.generate_entangled_pair("🌀 Quantum State A", "🌊 Quantum State B")
    print(f"   ✓ Vector A: {vec_a.vector_id}")
    print(f"   ✓ Vector B: {vec_b.vector_id}")
    print(f"   ✓ Entanglement: {vec_a.metadata.get('entangled_with', 'none')}")
    
    # Create entangled chain
    entangled_chain = builder.create_chain(
        chain_type=VectorChainType.ENTANGLED,
        constellation_target=ConstellationTarget.QUANTUM_FORGE,
        chain_name="Quantum_Entangled_Pair_v2"
    )
    builder.inject_vector(entangled_chain.chain_id, vec_a)
    builder.inject_vector(entangled_chain.chain_id, vec_b)
    builder.create_link(
        entangled_chain.chain_id,
        source_idx=0,
        target_idx=1,
        relationship="quantum_entanglement",
        strength=ChainLinkStrength.ABSOLUTE,
        bidirectional=True
    )
    
    print("\n5. Packaging Capsules...")
    
    # Package main chain
    capsule_zipwiz = packager.package_chain(
        chain=chain,
        thread_name="Thread_VectorGen::ZIPWIZ_Operational_v2",
        glyphcard_base="aurora://reliquary/GUI_HABITAT"
    )
    print(f"   ✓ ZIPWIZ Capsule: {capsule_zipwiz.capsule_id}")
    
    # Package networked chain
    capsule_bridge = packager.package_chain(
        chain=networked_chain,
        thread_name="Thread_VectorGen::BridgeAgent_Network_v2",
        glyphcard_base="aurora://reliquary/GUI_HABITAT"
    )
    print(f"   ✓ BridgeAgent Capsule: {capsule_bridge.capsule_id}")
    
    # Package entangled chain
    capsule_quantum = packager.package_chain(
        chain=entangled_chain,
        thread_name="Thread_VectorGen::Quantum_Entangled_v2",
        glyphcard_base="aurora://reliquary/GUI_HABITAT"
    )
    print(f"   ✓ Quantum Capsule: {capsule_quantum.capsule_id}")
    
    print("\n6. Creating Deployment Registries...")
    registry_zipwiz = packager.create_deployment_registry(capsule_zipwiz.capsule_id)
    registry_bridge = packager.create_deployment_registry(capsule_bridge.capsule_id)
    registry_quantum = packager.create_deployment_registry(capsule_quantum.capsule_id)
    
    print(f"   ✓ ZIPWIZ Registry: {registry_zipwiz['chain_stats']['vectors']} vectors, "
          f"{registry_zipwiz['chain_stats']['links']} links")
    print(f"   ✓ BridgeAgent Registry: {registry_bridge['chain_stats']['vectors']} vectors, "
          f"{registry_bridge['chain_stats']['links']} links")
    print(f"   ✓ Quantum Registry: {registry_quantum['chain_stats']['vectors']} vectors, "
          f"{registry_quantum['chain_stats']['links']} links")
    
    print("\n" + "═" * 70)
    print("✨ Demonstration Complete")
    
    return {
        "generator": generator,
        "builder": builder,
        "packager": packager,
        "capsules": {
            "zipwiz": capsule_zipwiz,
            "bridge": capsule_bridge,
            "quantum": capsule_quantum
        },
        "registries": {
            "zipwiz": registry_zipwiz,
            "bridge": registry_bridge,
            "quantum": registry_quantum
        }
    }


if __name__ == "__main__":
    results = demonstration()
    
    # Export capsules
    packager = results["packager"]
    
    for name, capsule in results["capsules"].items():
        filepath = f"/home/claude/quantum_forge_advanced/capsule_{name}_v2.json"
        packager.export_capsule(capsule.capsule_id, filepath)
        print(f"📦 Exported: capsule_{name}_v2.json")
    
    # Export all registries
    with open("/home/claude/quantum_forge_advanced/deployment_registries_v2.json", "w") as f:
        json.dump(results["registries"], f, indent=2)
    
    print("\n📋 Deployment registries exported")
