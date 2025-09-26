#!/usr/bin/env python3
"""
NEXUS Phase 4: Memory Weaving System
Anchor: T4-MEMORY-WEAVE-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 4.0.0
DLP Tag: MEMORY_CRITICAL

Cross-agent persistent memory with temporal threading
and associative recall networks
"""

import hashlib
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from collections import defaultdict

@dataclass
class Memory:
    """Individual memory unit with full metadata"""
    memory_id: str
    content: Any
    source_agent: str
    timestamp: datetime
    symbolic_anchors: List[str]
    associations: List[str] = field(default_factory=list)
    access_count: int = 0
    decay_rate: float = 0.01
    importance: float = 0.5
    seal: Optional[str] = None

@dataclass 
class MemoryWeave:
    """Interconnected memory structure across agents and time"""
    weave_id: str
    memories: List[Memory]
    agents: List[str]
    temporal_range: Tuple[datetime, datetime]
    cross_references: Dict[str, List[str]]
    consensus_memories: List[str]
    divergent_memories: List[str]
    weave_strength: float
    seal: Optional[str] = None

class MemoryWeavingSystem:
    """
    Revolutionary memory system that weaves individual agent memories
    into a persistent, searchable, and associative collective memory
    """
    
    def __init__(self, anchor: str = "T4-MEMORY-WEAVE-2025"):
        self.anchor = anchor
        self.seed = "EOS_SEED_ORION"
        self.arbiter = "AUo959"
        self.memory_store = {}
        self.agent_memories = defaultdict(list)
        self.memory_weaves = {}
        self.association_graph = defaultdict(set)
        self.temporal_index = defaultdict(list)
        self.compression_enabled = True
        self.max_memory_size = 10 * 1024 * 1024  # 10MB per agent
        
    async def store_memory(self, agent_id: str, content: Any, 
                          importance: float = 0.5,
                          associations: Optional[List[str]] = None) -> Memory:
        """
        Store a memory from an agent with automatic association detection
        
        Args:
            agent_id: Source agent identifier
            content: Memory content
            importance: Memory importance (0-1)
            associations: Optional list of associated memory IDs
            
        Returns:
            Stored Memory object with seal
        """
        
        memory_id = f"MEM-{agent_id}-{datetime.utcnow().timestamp()}"
        
        memory = Memory(
            memory_id=memory_id,
            content=content,
            source_agent=agent_id,
            timestamp=datetime.utcnow(),
            symbolic_anchors=[self.anchor, f"AGENT-{agent_id}"],
            associations=associations or [],
            importance=importance
        )
        
        # Auto-detect associations
        if not associations:
            memory.associations = await self._detect_associations(content, agent_id)
            
        # Compress if needed
        if self.compression_enabled:
            memory.content = self._compress_memory(memory.content)
            
        # Seal memory
        memory.seal = self._seal_memory(memory)
        
        # Store in multiple indices
        self.memory_store[memory_id] = memory
        self.agent_memories[agent_id].append(memory_id)
        
        # Update temporal index
        time_key = memory.timestamp.strftime("%Y%m%d%H")
        self.temporal_index[time_key].append(memory_id)
        
        # Update association graph
        for assoc_id in memory.associations:
            self.association_graph[memory_id].add(assoc_id)
            self.association_graph[assoc_id].add(memory_id)
            
        # Check memory limits
        await self._enforce_memory_limits(agent_id)
        
        return memory
        
    async def weave_memories(self, agent_ids: List[str], 
                            time_window: Optional[timedelta] = None) -> MemoryWeave:
        """
        Weave memories from multiple agents into interconnected structure
        
        Args:
            agent_ids: List of agent IDs to weave memories from
            time_window: Optional time window for memory selection
            
        Returns:
            MemoryWeave object containing interconnected memories
        """
        
        weave_id = f"WEAVE-{datetime.utcnow().timestamp()}"
        
        # Collect memories from agents
        memories_to_weave = []
        for agent_id in agent_ids:
            agent_mems = await self._get_agent_memories(agent_id, time_window)
            memories_to_weave.extend(agent_mems)
            
        if not memories_to_weave:
            raise ValueError("No memories found to weave")
            
        # Sort by timestamp
        memories_to_weave.sort(key=lambda m: m.timestamp)
        
        # Find consensus and divergent memories
        consensus, divergent = await self._find_consensus_divergence(memories_to_weave)
        
        # Build cross-references
        cross_refs = self._build_cross_references(memories_to_weave)
        
        # Calculate weave strength
        weave_strength = self._calculate_weave_strength(
            memories_to_weave, consensus, divergent
        )
        
        # Create weave
        weave = MemoryWeave(
            weave_id=weave_id,
            memories=memories_to_weave,
            agents=agent_ids,
            temporal_range=(
                min(m.timestamp for m in memories_to_weave),
                max(m.timestamp for m in memories_to_weave)
            ),
            cross_references=cross_refs,
            consensus_memories=consensus,
            divergent_memories=divergent,
            weave_strength=weave_strength
        )
        
        # Seal weave
        weave.seal = self._seal_weave(weave)
        
        # Store weave
        self.memory_weaves[weave_id] = weave
        
        return weave
        
    async def recall_associative(self, query: Any, agent_id: Optional[str] = None,
                                max_results: int = 10) -> List[Memory]:
        """
        Recall memories through associative search
        
        Args:
            query: Search query
            agent_id: Optional agent ID to scope search
            max_results: Maximum number of results
            
        Returns:
            List of associated memories ranked by relevance
        """
        
        # Find seed memories matching query
        seed_memories = await self._search_memories(query, agent_id)
        
        if not seed_memories:
            return []
            
        # Expand through associations
        associated = set()
        visited = set()
        to_visit = [m.memory_id for m in seed_memories]
        
        while to_visit and len(associated) < max_results * 2:
            current_id = to_visit.pop(0)
            if current_id in visited:
                continue
                
            visited.add(current_id)
            
            if current_id in self.memory_store:
                associated.add(current_id)
                
                # Add associations to visit
                for assoc_id in self.association_graph[current_id]:
                    if assoc_id not in visited:
                        to_visit.append(assoc_id)
                        
        # Rank by relevance and importance
        ranked_memories = []
        for mem_id in associated:
            memory = self.memory_store[mem_id]
            relevance = await self._calculate_relevance(memory, query)
            ranked_memories.append((relevance * memory.importance, memory))
            
        # Sort by score and return top results
        ranked_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Update access counts
        results = []
        for score, memory in ranked_memories[:max_results]:
            memory.access_count += 1
            results.append(memory)
            
        return results
        
    async def _detect_associations(self, content: Any, agent_id: str) -> List[str]:
        """Auto-detect memory associations"""
        
        associations = []
        content_str = str(content).lower()
        
        # Check recent memories for similarity
        recent_memories = list(self.agent_memories[agent_id][-10:])
        
        for mem_id in recent_memories:
            if mem_id in self.memory_store:
                other_memory = self.memory_store[mem_id]
                other_content = str(other_memory.content).lower()
                
                # Simple similarity check (would use embeddings in production)
                common_words = set(content_str.split()) & set(other_content.split())
                if len(common_words) > 3:
                    associations.append(mem_id)
                    
        return associations[:5]  # Limit associations
        
    def _compress_memory(self, content: Any) -> Any:
        """Compress memory content if needed"""
        
        # For now, just ensure it's JSON serializable
        if isinstance(content, (dict, list)):
            return content
        else:
            return str(content)
            
    async def _enforce_memory_limits(self, agent_id: str):
        """Enforce memory size limits per agent"""
        
        agent_mems = self.agent_memories[agent_id]
        
        # Calculate total size
        total_size = sum(
            len(json.dumps(self.memory_store[m].content, default=str))
            for m in agent_mems if m in self.memory_store
        )
        
        # If over limit, decay old memories
        if total_size > self.max_memory_size:
            # Sort by importance and access count
            memories = [
                self.memory_store[m] for m in agent_mems 
                if m in self.memory_store
            ]
            memories.sort(
                key=lambda m: m.importance * (1 + m.access_count),
                reverse=True
            )
            
            # Remove least important until under limit
            while total_size > self.max_memory_size and len(memories) > 10:
                removed = memories.pop()
                del self.memory_store[removed.memory_id]
                agent_mems.remove(removed.memory_id)
                
                total_size -= len(json.dumps(removed.content, default=str))
                
    async def _get_agent_memories(self, agent_id: str, 
                                 time_window: Optional[timedelta]) -> List[Memory]:
        """Get memories for an agent within time window"""
        
        memories = []
        cutoff_time = None
        
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            
        for mem_id in self.agent_memories[agent_id]:
            if mem_id in self.memory_store:
                memory = self.memory_store[mem_id]
                if not cutoff_time or memory.timestamp >= cutoff_time:
                    memories.append(memory)
                    
        return memories
        
    async def _find_consensus_divergence(self, 
                                        memories: List[Memory]) -> Tuple[List[str], List[str]]:
        """Find consensus and divergent memories"""
        
        consensus = []
        divergent = []
        
        # Group by content similarity
        content_groups = defaultdict(list)
        
        for memory in memories:
            # Hash content for grouping
            content_hash = hashlib.sha256(
                str(memory.content).encode()
            ).hexdigest()[:8]
            content_groups[content_hash].append(memory.memory_id)
            
        # Identify consensus (multiple agents same memory)
        for group_hash, mem_ids in content_groups.items():
            unique_agents = set(
                self.memory_store[m].source_agent 
                for m in mem_ids if m in self.memory_store
            )
            
            if len(unique_agents) > 1:
                consensus.extend(mem_ids)
            elif len(mem_ids) == 1:
                divergent.extend(mem_ids)
                
        return consensus, divergent
        
    def _build_cross_references(self, memories: List[Memory]) -> Dict[str, List[str]]:
        """Build cross-reference map for memories"""
        
        cross_refs = defaultdict(list)
        
        for memory in memories:
            # Add all associations as cross-references
            for assoc_id in memory.associations:
                cross_refs[memory.memory_id].append(assoc_id)
                cross_refs[assoc_id].append(memory.memory_id)
                
        # Remove duplicates
        for mem_id in cross_refs:
            cross_refs[mem_id] = list(set(cross_refs[mem_id]))
            
        return dict(cross_refs)
        
    def _calculate_weave_strength(self, memories: List[Memory],
                                 consensus: List[str],
                                 divergent: List[str]) -> float:
        """Calculate strength of memory weave"""
        
        if not memories:
            return 0.0
            
        # Factors: consensus ratio, association density, importance
        consensus_ratio = len(consensus) / len(memories)
        
        total_associations = sum(len(m.associations) for m in memories)
        association_density = total_associations / len(memories)
        
        avg_importance = np.mean([m.importance for m in memories])
        
        # Weighted combination
        strength = (
            0.4 * consensus_ratio +
            0.3 * min(1.0, association_density / 5) +
            0.3 * avg_importance
        )
        
        return min(1.0, strength)
        
    async def _search_memories(self, query: Any, 
                              agent_id: Optional[str]) -> List[Memory]:
        """Search memories matching query"""
        
        results = []
        query_str = str(query).lower()
        
        # Search in specified agent or all
        if agent_id:
            search_mems = [
                self.memory_store[m] 
                for m in self.agent_memories[agent_id]
                if m in self.memory_store
            ]
        else:
            search_mems = list(self.memory_store.values())
            
        for memory in search_mems:
            content_str = str(memory.content).lower()
            if query_str in content_str:
                results.append(memory)
                
        return results[:20]  # Limit initial results
        
    async def _calculate_relevance(self, memory: Memory, query: Any) -> float:
        """Calculate relevance of memory to query"""
        
        query_str = str(query).lower()
        content_str = str(memory.content).lower()
        
        # Simple word overlap (would use embeddings in production)
        query_words = set(query_str.split())
        content_words = set(content_str.split())
        
        if not query_words:
            return 0.0
            
        overlap = len(query_words & content_words)
        relevance = overlap / len(query_words)
        
        # Boost for recent memories
        age_days = (datetime.utcnow() - memory.timestamp).days
        recency_boost = 1.0 / (1.0 + age_days * 0.1)
        
        return relevance * recency_boost
        
    def _seal_memory(self, memory: Memory) -> str:
        """Seal memory with SHA256"""
        
        memory_data = {
            "memory_id": memory.memory_id,
            "content_hash": hashlib.sha256(str(memory.content).encode()).hexdigest(),
            "source_agent": memory.source_agent,
            "timestamp": memory.timestamp.isoformat(),
            "importance": memory.importance
        }
        
        return hashlib.sha256(
            json.dumps(memory_data, sort_keys=True).encode()
        ).hexdigest()
        
    def _seal_weave(self, weave: MemoryWeave) -> str:
        """Seal memory weave with SHA256"""
        
        weave_data = {
            "weave_id": weave.weave_id,
            "memory_count": len(weave.memories),
            "agents": weave.agents,
            "temporal_range": [
                weave.temporal_range[0].isoformat(),
                weave.temporal_range[1].isoformat()
            ],
            "weave_strength": weave.weave_strength
        }
        
        return hashlib.sha256(
            json.dumps(weave_data, sort_keys=True).encode()
        ).hexdigest()
        
    def export_memory_manifest(self) -> Dict:
        """Export complete memory system manifest"""
        
        manifest = {
            "manifest_version": "4.0.0",
            "anchor": self.anchor,
            "seed": self.seed,
            "arbiter": self.arbiter,
            "export_time": datetime.utcnow().isoformat(),
            "team": "Aurora Core",
            "memory_stats": {
                "total_memories": len(self.memory_store),
                "total_agents": len(self.agent_memories),
                "total_weaves": len(self.memory_weaves),
                "total_associations": sum(
                    len(assocs) for assocs in self.association_graph.values()
                ) // 2,  # Divide by 2 for bidirectional
                "memory_size_bytes": sum(
                    len(json.dumps(m.content, default=str))
                    for m in self.memory_store.values()
                )
            },
            "compression_enabled": self.compression_enabled,
            "max_memory_per_agent": self.max_memory_size,
            "dlp_classification": "MEMORY_CRITICAL"
        }
        
        # Seal manifest
        manifest_hash = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest()
        
        manifest["seal"] = manifest_hash
        
        return manifest

# Module initialization
memory_weaver = MemoryWeavingSystem()

def get_memory_weaver() -> MemoryWeavingSystem:
    """Get singleton memory weaver instance"""
    return memory_weaver