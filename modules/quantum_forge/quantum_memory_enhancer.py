"""
Quantum Memory Enhancer v1.0

Integrates quantum coherence tracking with AuMemManager for self-healing memory.
Automatic decoherence detection, priority-based retrieval, and quantum semantic search.

Features:
- Quantum coherence metadata for memories
- Automatic coherence monitoring and restoration
- Priority retrieval based on quantum state
- Entanglement-based semantic similarity
- Temporal consistency with T1 anchors

T1: QUANTUM_MEMORY_v1.0
SRB: AUMEM_QUANTUM_INTEGRATION
DLP: context_tag=quantum_memory_enhance, symbolic_hash=QME_v1

Author: Aurora CloudBank Team
Version: 1.0.0
Date: 2025-11-13
Ethics: GUMAS_Thermax, Memory_Safe
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from modules.quantum_forge.quantum_forge_v2 import QuantumForge, SymbolicMemoryNode
from modules.quantum_forge.quantum_integration import QuantumForgeIntegration

logger = logging.getLogger(__name__)


@dataclass
class QuantumMemoryMetadata:
    """Quantum-enhanced metadata for memory entries"""
    memory_id: str
    coherence_state: str  # "COHERENT", "DECOHERENT", "REFRESHING"
    coherence_score: float  # 0.0 - 1.0
    decoherence_rate: float
    last_access: float
    access_count: int
    quantum_priority: float  # Computed from coherence + access patterns
    entangled_memories: List[str]  # IDs of semantically entangled memories
    
    
class QuantumMemoryEnhancer:
    """
    Quantum enhancement layer for Aurora memory systems
    
    Adds quantum coherence tracking, automatic restoration,
    and entanglement-based semantic search to memory management.
    """
    
    def __init__(
        self,
        forge: Optional[QuantumForge] = None,
        integration: Optional[QuantumForgeIntegration] = None,
        coherence_threshold: float = 0.7,
        refresh_interval: float = 300.0
    ):
        """
        Initialize quantum memory enhancer
        
        Args:
            forge: QuantumForge instance
            integration: QuantumForgeIntegration instance
            coherence_threshold: Minimum coherence for active memories
            refresh_interval: Auto-refresh interval in seconds
        """
        self.forge = forge or QuantumForge()
        self.integration = integration or QuantumForgeIntegration(forge=self.forge)
        self.coherence_threshold = coherence_threshold
        self.refresh_interval = refresh_interval
        
        # Track quantum metadata for memories
        self.quantum_metadata: Dict[str, QuantumMemoryMetadata] = {}
        
        # Track semantic entanglement between memories
        self.semantic_entanglements: Dict[str, List[str]] = {}
        
        # Metrics
        self.metrics = {
            "total_enhanced_memories": 0,
            "coherent_memories": 0,
            "decoherent_memories": 0,
            "auto_refreshes": 0,
            "entanglements_created": 0
        }
        
        logger.info("🧠 Quantum Memory Enhancer initialized")
        logger.info(f"   Coherence threshold: {coherence_threshold}")
        logger.info(f"   Refresh interval: {refresh_interval}s")
        
    def enhance_memory(
        self,
        memory_node: SymbolicMemoryNode,
        aumem_integration: bool = False
    ) -> QuantumMemoryMetadata:
        """
        Add quantum enhancement to memory node
        
        Args:
            memory_node: SymbolicMemoryNode to enhance
            aumem_integration: Whether to integrate with AuMemManager
            
        Returns:
            QuantumMemoryMetadata with coherence tracking
        """
        memory_id = memory_node.node_id
        
        logger.info(f"✨ Enhancing memory with quantum metadata: {memory_id}")
        
        # Calculate initial coherence score from intent alignment
        coherence_score = memory_node.intent_alignment
        
        # Calculate decoherence rate based on content complexity
        if HAS_NUMPY:
            embedding_variance = float(np.var(memory_node.embedding))
        else:
            mean_val = sum(memory_node.embedding) / len(memory_node.embedding)
            embedding_variance = sum((x - mean_val) ** 2 for x in memory_node.embedding) / len(memory_node.embedding)
            
        # Higher variance = faster decoherence
        decoherence_rate = min(0.01, embedding_variance * 0.001)
        
        # Create quantum metadata
        metadata = QuantumMemoryMetadata(
            memory_id=memory_id,
            coherence_state="COHERENT",
            coherence_score=coherence_score,
            decoherence_rate=decoherence_rate,
            last_access=time.time(),
            access_count=0,
            quantum_priority=self._calculate_priority(coherence_score, 0),
            entangled_memories=[]
        )
        
        # Store metadata
        self.quantum_metadata[memory_id] = metadata
        
        # Update metrics
        self.metrics["total_enhanced_memories"] += 1
        self.metrics["coherent_memories"] += 1
        
        # Find and create semantic entanglements
        self._create_semantic_entanglements(memory_node)
        
        logger.info(
            f"✅ Memory enhanced: {memory_id} "
            f"(coherence: {coherence_score:.4f}, decoherence_rate: {decoherence_rate:.6f})"
        )
        
        return metadata
        
    def retrieve_by_priority(
        self,
        top_k: int = 10,
        min_coherence: Optional[float] = None
    ) -> List[Tuple[str, QuantumMemoryMetadata]]:
        """
        Retrieve memories by quantum priority
        
        Args:
            top_k: Number of top memories to retrieve
            min_coherence: Minimum coherence threshold (uses default if None)
            
        Returns:
            List of (memory_id, metadata) tuples sorted by priority
        """
        min_coh = min_coherence or self.coherence_threshold
        
        # Filter by coherence
        valid_memories = [
            (mem_id, meta) for mem_id, meta in self.quantum_metadata.items()
            if meta.coherence_score >= min_coh
        ]
        
        # Sort by quantum priority (descending)
        valid_memories.sort(key=lambda x: x[1].quantum_priority, reverse=True)
        
        return valid_memories[:top_k]
        
    def search_by_entanglement(
        self,
        query_memory_id: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Search for semantically entangled memories
        
        Args:
            query_memory_id: Memory to find entanglements for
            top_k: Number of results to return
            
        Returns:
            List of (memory_id, entanglement_strength) tuples
        """
        if query_memory_id not in self.quantum_metadata:
            return []
            
        entangled = self.semantic_entanglements.get(query_memory_id, [])
        
        # Calculate entanglement strengths
        results = []
        for target_id in entangled:
            if target_id in self.quantum_metadata:
                # Strength based on coherence correlation
                query_coh = self.quantum_metadata[query_memory_id].coherence_score
                target_coh = self.quantum_metadata[target_id].coherence_score
                
                # Higher when both have similar coherence
                strength = 1.0 - abs(query_coh - target_coh)
                results.append((target_id, strength))
        
        # Sort by strength
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
        
    def monitor_coherence(self) -> Dict[str, Any]:
        """
        Monitor coherence across all enhanced memories
        
        Returns:
            Dict with coherence diagnostics
        """
        current_time = time.time()
        
        coherent = []
        decoherent = []
        needs_refresh = []
        
        for memory_id, metadata in self.quantum_metadata.items():
            # Calculate current coherence accounting for decay
            elapsed = current_time - metadata.last_access
            decay = metadata.decoherence_rate * elapsed
            current_coherence = max(0.0, metadata.coherence_score - decay)
            
            # Update metadata
            metadata.coherence_score = current_coherence
            
            # Categorize
            if current_coherence >= self.coherence_threshold:
                coherent.append(memory_id)
                metadata.coherence_state = "COHERENT"
            else:
                decoherent.append(memory_id)
                metadata.coherence_state = "DECOHERENT"
                
            # Check if needs refresh
            if elapsed > self.refresh_interval:
                needs_refresh.append(memory_id)
        
        # Update metrics
        self.metrics["coherent_memories"] = len(coherent)
        self.metrics["decoherent_memories"] = len(decoherent)
        
        return {
            "total_memories": len(self.quantum_metadata),
            "coherent": len(coherent),
            "decoherent": len(decoherent),
            "needs_refresh": len(needs_refresh),
            "average_coherence": sum(
                m.coherence_score for m in self.quantum_metadata.values()
            ) / len(self.quantum_metadata) if self.quantum_metadata else 0.0,
            "refresh_candidates": needs_refresh[:10]  # Top 10
        }
        
    def auto_refresh_decoherent(
        self,
        max_refreshes: int = 10
    ) -> Dict[str, Any]:
        """
        Automatically refresh decoherent memories
        
        Args:
            max_refreshes: Maximum number of memories to refresh
            
        Returns:
            Dict with refresh results
        """
        logger.info(f"🔄 Starting auto-refresh (max: {max_refreshes})")
        
        # Find decoherent memories
        decoherent = [
            (mem_id, meta) for mem_id, meta in self.quantum_metadata.items()
            if meta.coherence_state == "DECOHERENT"
        ]
        
        # Sort by priority (refresh most important first)
        decoherent.sort(key=lambda x: x[1].quantum_priority, reverse=True)
        
        refreshed = []
        failed = []
        
        for memory_id, metadata in decoherent[:max_refreshes]:
            try:
                metadata.coherence_state = "REFRESHING"
                
                # Get memory node from forge
                if memory_id in self.forge.memory_nodes:
                    memory_node = self.forge.memory_nodes[memory_id]
                    
                    # Recalculate embedding and coherence
                    content_str = json.dumps(memory_node.content, sort_keys=True)
                    hash_val = int(hashlib.sha256(content_str.encode()).hexdigest()[:16], 16)
                    
                    if HAS_NUMPY:
                        np.random.seed(hash_val % (2**32))
                        new_embedding = np.random.randn(self.forge.vector_dimension).tolist()
                    else:
                        import random
                        random.seed(hash_val % (2**32))
                        new_embedding = [random.gauss(0, 1) for _ in range(self.forge.vector_dimension)]
                    
                    # Update memory node
                    memory_node.embedding = new_embedding
                    
                    # Restore coherence
                    metadata.coherence_score = memory_node.intent_alignment
                    metadata.last_access = time.time()
                    metadata.coherence_state = "COHERENT"
                    
                    refreshed.append(memory_id)
                    logger.info(f"   ✅ Refreshed: {memory_id}")
                    
            except Exception as e:
                failed.append((memory_id, str(e)))
                metadata.coherence_state = "DECOHERENT"
                logger.error(f"   ❌ Failed to refresh {memory_id}: {e}")
        
        # Update metrics
        self.metrics["auto_refreshes"] += len(refreshed)
        self.metrics["coherent_memories"] += len(refreshed)
        self.metrics["decoherent_memories"] -= len(refreshed)
        
        logger.info(
            f"✅ Auto-refresh complete: {len(refreshed)} succeeded, "
            f"{len(failed)} failed"
        )
        
        return {
            "refreshed_count": len(refreshed),
            "failed_count": len(failed),
            "refreshed_ids": refreshed,
            "failed": failed,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_memory_health(self, memory_id: str) -> Dict[str, Any]:
        """Get detailed health status for specific memory"""
        if memory_id not in self.quantum_metadata:
            return {
                "memory_id": memory_id,
                "enhanced": False
            }
            
        metadata = self.quantum_metadata[memory_id]
        current_time = time.time()
        
        elapsed = current_time - metadata.last_access
        time_until_refresh = max(0, self.refresh_interval - elapsed)
        
        return {
            "memory_id": memory_id,
            "enhanced": True,
            "coherence_state": metadata.coherence_state,
            "coherence_score": metadata.coherence_score,
            "decoherence_rate": metadata.decoherence_rate,
            "quantum_priority": metadata.quantum_priority,
            "access_count": metadata.access_count,
            "time_since_access": elapsed,
            "time_until_refresh": time_until_refresh,
            "needs_refresh": elapsed > self.refresh_interval,
            "entangled_count": len(metadata.entangled_memories)
        }
        
    def export_quantum_memory_manifest(self) -> Dict[str, Any]:
        """Export complete quantum memory enhancement manifest"""
        manifest = {
            "manifest_version": "1.0.0",
            "component": "quantum_memory_enhancer",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self.metrics,
            "coherence_monitoring": self.monitor_coherence(),
            "enhanced_memories": [
                {
                    "memory_id": mem_id,
                    "coherence": meta.coherence_score,
                    "state": meta.coherence_state,
                    "priority": meta.quantum_priority,
                    "entanglements": len(meta.entangled_memories)
                }
                for mem_id, meta in self.quantum_metadata.items()
            ][:50],  # Top 50
            "semantic_entanglement_graph": {
                "total_nodes": len(self.semantic_entanglements),
                "total_edges": sum(len(v) for v in self.semantic_entanglements.values()),
                "average_degree": sum(len(v) for v in self.semantic_entanglements.values()) / len(self.semantic_entanglements)
                if self.semantic_entanglements else 0.0
            },
            "dlp_tag": "quantum_memory_enhance_v1"
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
    
    def _calculate_priority(self, coherence: float, access_count: int) -> float:
        """Calculate quantum priority score"""
        # Priority = coherence * (1 + log(1 + access_count))
        import math
        access_factor = 1.0 + math.log(1.0 + access_count)
        return coherence * access_factor
        
    def _create_semantic_entanglements(self, memory_node: SymbolicMemoryNode):
        """Find and create semantic entanglements with existing memories"""
        memory_id = memory_node.node_id
        
        # Find semantically similar memories via embedding similarity
        if not self.forge.memory_nodes:
            return
            
        similarities = []
        for other_id, other_node in self.forge.memory_nodes.items():
            if other_id == memory_id:
                continue
                
            # Calculate cosine similarity
            if HAS_NUMPY:
                vec1 = np.array(memory_node.embedding)
                vec2 = np.array(other_node.embedding)
                similarity = float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
            else:
                dot_product = sum(a * b for a, b in zip(memory_node.embedding, other_node.embedding))
                norm1 = sum(x ** 2 for x in memory_node.embedding) ** 0.5
                norm2 = sum(x ** 2 for x in other_node.embedding) ** 0.5
                similarity = dot_product / (norm1 * norm2) if norm1 * norm2 > 0 else 0.0
                
            if similarity > 0.7:  # Threshold for entanglement
                similarities.append((other_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Create entanglements with top-k similar memories
        entangled_ids = [other_id for other_id, _ in similarities[:5]]
        
        # Store bidirectional entanglements
        self.semantic_entanglements[memory_id] = entangled_ids
        for other_id in entangled_ids:
            if other_id not in self.semantic_entanglements:
                self.semantic_entanglements[other_id] = []
            if memory_id not in self.semantic_entanglements[other_id]:
                self.semantic_entanglements[other_id].append(memory_id)
        
        # Update metadata
        if memory_id in self.quantum_metadata:
            self.quantum_metadata[memory_id].entangled_memories = entangled_ids
            
        self.metrics["entanglements_created"] += len(entangled_ids)
        
        logger.info(f"   🔗 Created {len(entangled_ids)} semantic entanglements")


# ============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

_quantum_memory_enhancer: Optional[QuantumMemoryEnhancer] = None


def get_quantum_memory_enhancer(**kwargs) -> QuantumMemoryEnhancer:
    """Get or create global quantum memory enhancer instance"""
    global _quantum_memory_enhancer
    
    if _quantum_memory_enhancer is None:
        _quantum_memory_enhancer = QuantumMemoryEnhancer(**kwargs)
        
    return _quantum_memory_enhancer


def reset_quantum_memory_enhancer():
    """Reset global quantum memory enhancer instance"""
    global _quantum_memory_enhancer
    _quantum_memory_enhancer = None
