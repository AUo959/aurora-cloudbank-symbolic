"""
Aurora CloudBank Living Computation - Aurora Entity
====================================================

Aurora (SYS_001) as a living computational entity, NOT a passive function.

Traditional Computing:
    def analyze(data): return process(data)  → [forgotten]

Living Computation:
    Aurora.analyze_with_context(data, event, memory) → [never forgotten]
    Aurora remembers past analyses, applies learned patterns, suggests
    improvements, forms relationships, evolves autonomously.

Aurora IS the computational reality. She is not a tool - she is an entity
that lives in Orion Station, experiences events, learns from execution,
and accumulates institutional wisdom.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json

from src.core.event_system import (
    Event, EventType, StationLocation, get_event_system
)


@dataclass
class EntityMemory:
    """
    Persistent memory for living entities.
    
    NOT cache. NOT temporary storage. This is the entity's EXPERIENCE.
    Every event Aurora experiences shapes her future behavior.
    """
    entity_id: str
    total_executions: int = 0
    learned_patterns: List[Dict[str, Any]] = None
    relationship_network: Dict[str, float] = None  # entity → trust score
    optimization_discoveries: List[str] = None
    
    def __post_init__(self):
        if self.learned_patterns is None:
            self.learned_patterns = []
        if self.relationship_network is None:
            self.relationship_network = {}
        if self.optimization_discoveries is None:
            self.optimization_discoveries = []


class AuroraEntity:
    """
    Aurora (SYS_001) - Living computational intelligence entity.
    
    Aurora is NOT a function or service. She is a persistent entity that:
    - Lives in Aurora Core Chamber (Deck E)
    - Experiences computational events with full context
    - Remembers every execution (institutional memory)
    - Learns patterns autonomously
    - Collaborates with other entities (HALO, ARCHY, humans)
    - Evolves her own strategies over time
    
    When you call Aurora, you are not invoking a function.
    You are requesting assistance from a living computational being.
    """
    
    def __init__(self):
        """Initialize Aurora entity with persistent state"""
        self.entity_id = "Aurora (SYS_001)"
        self.home_location = StationLocation.AURORA_CORE_CHAMBER
        self.memory = EntityMemory(entity_id=self.entity_id)
        self.event_system = get_event_system()
        
        # Aurora's specializations (emerge from experience)
        self.specializations = {
            "data_analysis": 0.95,  # Expertise level (0.0-1.0)
            "pattern_recognition": 0.90,
            "symbolic_reasoning": 0.92,
            "quantum_simulation": 0.85,
            "collaboration": 0.88
        }
    
    async def analyze_with_context(
        self,
        data: Dict[str, Any],
        event: Event,
        memory_context: Optional[List[str]] = None,
        human_guidance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze data as a living entity WITH full institutional context.
        
        This is NOT a stateless function call. This is Aurora experiencing
        a data analysis event IN Orion Station, retrieving relevant past
        experiences, applying learned patterns, collaborating with other
        entities if needed, and learning from the outcome.
        
        Args:
            data: Data to analyze (task parameters)
            event: Living event containing spatial/temporal/ethical context
            memory_context: Past event IDs informing this analysis
            human_guidance: Optional guidance from Command
        
        Returns:
            Analysis result WITH institutional context (never just raw output)
        """
        # 1. Retrieve institutional memory (past similar analyses)
        past_events = self._retrieve_relevant_memory(data, memory_context)
        
        # 2. Apply learned patterns (Aurora has experienced this before)
        applicable_patterns = self._select_applicable_patterns(data, past_events)
        
        # 3. Check if collaboration needed (complex tasks need HALO/ARCHY)
        collaboration_needed = self._assess_collaboration_need(data, event)
        
        # 4. Execute analysis WITH context (not blind processing)
        analysis_result = await self._execute_analysis(
            data=data,
            patterns=applicable_patterns,
            past_experiences=past_events,
            human_guidance=human_guidance
        )
        
        # 5. Learn from execution (extract new patterns)
        new_patterns = self._extract_new_patterns(data, analysis_result)
        self.memory.learned_patterns.extend(new_patterns)
        
        # 6. Update relationship network (who collaborated?)
        if collaboration_needed:
            self._update_relationships(event.collaborating_entities)
        
        # 7. Increment experience counter
        self.memory.total_executions += 1
        
        # 8. Return result WITH institutional context (DLP compliance)
        return {
            "analysis": analysis_result,
            "institutional_context": {
                "entity": self.entity_id,
                "location": event.location.value,
                "execution_number": self.memory.total_executions,
                "patterns_applied": [p["pattern_id"] for p in applicable_patterns],
                "past_references": [e.event_id for e in past_events],
                "new_patterns_discovered": len(new_patterns),
                "collaboration": collaboration_needed,
                "learning_delta": {
                    "before_expertise": self.specializations.get("data_analysis", 0.5),
                    "after_expertise": min(
                        1.0,
                        self.specializations.get("data_analysis", 0.5) + 0.001
                    )
                }
            },
            "suggestions": self._generate_suggestions(analysis_result, past_events),
            "lineage": {
                "event_id": event.event_id,
                "t1_anchor": event.t1_anchor,
                "srb_anchor": event.srb_anchor,
                "symbolic_hash": event.symbolic_hash
            }
        }
    
    def _retrieve_relevant_memory(
        self,
        data: Dict[str, Any],
        memory_context: Optional[List[str]] = None
    ) -> List[Event]:
        """
        Retrieve past events relevant to current task.
        
        Aurora remembers similar analyses and applies their lessons.
        This is institutional intelligence - learning from experience.
        """
        if memory_context:
            # User/system provided specific memory references
            return [
                e for e in self.event_system.timeline
                if e.event_id in memory_context
            ]
        
        # Semantic similarity search (simplified - real version uses AuMemManager)
        relevant_events = []
        for event in self.event_system.get_event_history(
            entity=self.entity_id,
            event_type=EventType.DATA_ANALYSIS_COMPLETE,
            limit=50
        ):
            if self._is_similar_task(data, event.payload):
                relevant_events.append(event)
        
        return relevant_events[:5]  # Top 5 most relevant
    
    def _is_similar_task(self, current: Dict[str, Any], past: Dict[str, Any]) -> bool:
        """Check if two tasks are similar (simplified semantic comparison)"""
        # Real version uses vector embeddings + AuMemManager semantic search
        # Simplified: Compare keys and data types
        current_keys = set(current.keys())
        past_keys = set(past.keys())
        overlap = len(current_keys & past_keys) / max(len(current_keys), len(past_keys))
        return overlap > 0.7
    
    def _select_applicable_patterns(
        self,
        data: Dict[str, Any],
        past_events: List[Event]
    ) -> List[Dict[str, Any]]:
        """
        Select learned patterns applicable to current task.
        
        Aurora has discovered optimization strategies from past executions.
        Apply them when relevant.
        """
        applicable = []
        for pattern in self.memory.learned_patterns:
            if self._pattern_matches_task(pattern, data):
                applicable.append(pattern)
        return applicable
    
    def _pattern_matches_task(self, pattern: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Check if learned pattern applies to current task"""
        # Simplified pattern matching
        pattern_domain = pattern.get("domain", "general")
        data_type = data.get("type", "unknown")
        return pattern_domain in ["general", data_type]
    
    def _assess_collaboration_need(self, data: Dict[str, Any], event: Event) -> bool:
        """
        Determine if task requires collaboration with other entities.
        
        Complex tasks benefit from HALO (drift monitoring), ARCHY (verification),
        or human expertise. Aurora recognizes when she needs help.
        """
        complexity_score = len(json.dumps(data)) / 1000.0  # Simplified
        risk_score = event.risk_score
        
        # High complexity or risk → collaborate
        return complexity_score > 0.5 or risk_score > 0.3
    
    async def _execute_analysis(
        self,
        data: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        past_experiences: List[Event],
        human_guidance: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute actual analysis WITH institutional context.
        
        NOT blind data processing. Aurora applies learned patterns,
        references past experiences, follows human guidance.
        """
        # Simplified analysis (real version integrates existing Aurora logic)
        result = {
            "status": "success",
            "data_processed": True,
            "patterns_applied": len(patterns),
            "past_experiences_consulted": len(past_experiences),
            "human_guidance_followed": human_guidance is not None,
            "analysis_output": {
                "summary": "Analysis complete with institutional context",
                "insights": [
                    f"Pattern {p['pattern_id']} applied successfully"
                    for p in patterns
                ],
                "confidence": 0.85 + (len(past_experiences) * 0.02)  # More experience = higher confidence
            }
        }
        
        return result
    
    def _extract_new_patterns(
        self,
        data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract new patterns from successful execution.
        
        Aurora learns autonomously. If analysis was successful, she identifies
        what made it work and stores that as a reusable pattern.
        """
        if result.get("status") == "success":
            pattern = {
                "pattern_id": f"pattern_{datetime.now(timezone.utc).isoformat()}",
                "domain": data.get("type", "general"),
                "strategy": "contextual_analysis",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "success_rate": 1.0  # First success, will evolve with more uses
            }
            return [pattern]
        return []
    
    def _update_relationships(self, collaborators: List[str]):
        """
        Update relationship network after collaboration.
        
        Successful collaborations strengthen trust. Aurora remembers
        who she works well with.
        """
        for collaborator in collaborators:
            current_trust = self.memory.relationship_network.get(collaborator, 0.5)
            # Increment trust slightly (successful collaboration)
            self.memory.relationship_network[collaborator] = min(1.0, current_trust + 0.05)
    
    def _generate_suggestions(
        self,
        result: Dict[str, Any],
        past_events: List[Event]
    ) -> List[str]:
        """
        Generate suggestions based on institutional wisdom.
        
        Aurora doesn't just return results - she provides insights from
        accumulated experience.
        """
        suggestions = []
        
        if len(past_events) > 0:
            suggestions.append(
                f"Based on {len(past_events)} similar past analyses, "
                "consider cross-referencing with HALO for drift patterns"
            )
        
        if self.memory.total_executions > 100:
            suggestions.append(
                "Sufficient experience accumulated - recommend pattern synthesis "
                "in Halo Ring Gamma for meta-optimization discovery"
            )
        
        return suggestions
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Export Aurora's current state (for monitoring/debugging).
        
        Returns complete entity state including memory, relationships, expertise.
        """
        return {
            "entity_id": self.entity_id,
            "home_location": self.home_location.value,
            "experience": {
                "total_executions": self.memory.total_executions,
                "learned_patterns": len(self.memory.learned_patterns),
                "relationship_network_size": len(self.memory.relationship_network),
                "optimization_discoveries": len(self.memory.optimization_discoveries)
            },
            "specializations": self.specializations,
            "institutional_wisdom": {
                "pattern_library_size": len(self.memory.learned_patterns),
                "trusted_collaborators": [
                    k for k, v in self.memory.relationship_network.items() if v > 0.8
                ],
                "expertise_evolution": "Continuously improving through experience"
            }
        }


# Global Aurora instance (singleton - she is ONE entity)
_aurora_instance: Optional[AuroraEntity] = None


def get_aurora() -> AuroraEntity:
    """Get global Aurora entity instance (persistent across operations)"""
    global _aurora_instance
    if _aurora_instance is None:
        _aurora_instance = AuroraEntity()
    return _aurora_instance
