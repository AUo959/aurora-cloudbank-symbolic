"""
Institutional Memory Integration - Aurora's Learning System

Anchor: AURORA-ORCHESTRATOR-MEMORY-001
Version: 1.0.0
Team: Orion Station Crew
DLP: CONFIDENTIAL
Ethics: Picard_Delta_3

Aurora's institutional memory for orchestration decisions and outcomes.

This is how Aurora:
- Never forgets (stores every decision and outcome)
- Learns (extracts patterns from history)
- Evolves (improves expertise over time)
- Gets smarter (applies learned wisdom to new decisions)

Canonical Alignment:
- Living Computation: Memory IS identity
- Continuous Learning: Every execution shapes future behavior
- DLP Compliance: Complete audit trail
- Institutional Wisdom: Accumulated knowledge over time
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib


@dataclass
class Pattern:
    """Learned pattern from orchestration history"""
    pattern_id: str
    pattern_type: str  # temporal, load, cost, performance, error
    description: str
    conditions: Dict[str, Any]
    recommended_action: str
    success_rate: float  # 0.0-1.0
    sample_size: int
    discovered_at: str
    last_updated: str
    confidence: float = 0.0  # Derived from success_rate and sample_size

    def __post_init__(self):
        # Calculate confidence: success_rate weighted by sample size
        if self.sample_size > 0:
            # Confidence increases with sample size (up to 20 samples)
            sample_weight = min(self.sample_size / 20.0, 1.0)
            self.confidence = self.success_rate * sample_weight


@dataclass
class OrchestrationMemory:
    """Memory of a single orchestration decision"""
    memory_id: str
    decision_id: str
    execution_id: str
    timestamp: str
    decision: Dict[str, Any]
    outcome: Dict[str, Any]
    system_state_before: Dict[str, Any]
    system_state_after: Optional[Dict[str, Any]] = None
    success: bool = False
    improvement: Dict[str, float] = field(default_factory=dict)
    patterns_applied: List[str] = field(default_factory=list)
    new_patterns_discovered: List[str] = field(default_factory=list)
    dlp_context_tag: str = ""
    symbolic_hash: str = ""

    def __post_init__(self):
        if not self.dlp_context_tag:
            self.dlp_context_tag = f"aurora_orchestration_{self.decision_id}"
        if not self.symbolic_hash:
            self.symbolic_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate symbolic hash for DLP tracking"""
        content = f"{self.decision_id}:{self.execution_id}:{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class InstitutionalMemoryIntegrator:
    """
    Institutional Memory Integration for Aurora's Orchestration

    Manages Aurora's learning and evolution through institutional memory.

    Core Capabilities:
    - Store orchestration outcomes with full context
    - Retrieve similar past decisions
    - Extract patterns from history
    - Track expertise evolution
    - Maintain complete DLP audit trail
    """

    def __init__(self):
        """Initialize institutional memory integrator"""
        self.logger = self._setup_logging()

        # In-memory storage (future: integrate with AuMemManager)
        self.orchestration_memories: Dict[str, OrchestrationMemory] = {}
        self.patterns: Dict[str, Pattern] = {}

        # Expertise tracking
        self.expertise_evolution: Dict[str, List[float]] = {
            'quantum_optimization': [0.85],
            'ai_model_selection': [0.90],
            'memory_management': [0.88],
            'system_breathing': [0.92],
            'general_orchestration': [0.87]
        }

        # Statistics
        self.stats = {
            'total_memories': 0,
            'total_patterns': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'total_improvement_score': 0.0
        }

        self.logger.info("📚 Institutional Memory Integrator initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('InstitutionalMemory')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(asctime)s] INST-MEMORY %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        return logger

    async def store_orchestration_outcome(
        self,
        decision,
        outcome: Dict[str, Any],
        system_state_before: Dict[str, Any],
        system_state_after: Optional[Dict[str, Any]] = None
    ) -> OrchestrationMemory:
        """
        Store orchestration decision and outcome in institutional memory.

        This is how Aurora never forgets - every decision and its outcome
        becomes part of her accumulated wisdom.

        Args:
            decision: Aurora's decision
            outcome: Execution outcome
            system_state_before: System state before execution
            system_state_after: System state after execution

        Returns:
            OrchestrationMemory: Stored memory record
        """
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Create memory record
        memory = OrchestrationMemory(
            memory_id=memory_id,
            decision_id=decision.decision_id,
            execution_id=outcome.execution_id,
            timestamp=datetime.now().isoformat(),
            decision=self._serialize_decision(decision),
            outcome=outcome,
            system_state_before=system_state_before,
            system_state_after=system_state_after,
            success=outcome.success,
            improvement=outcome.improvement
        )

        # Store in memory
        self.orchestration_memories[memory_id] = memory

        # Update statistics
        self.stats['total_memories'] += 1
        if memory.success:
            self.stats['successful_optimizations'] += 1

            # Calculate improvement score
            improvement_score = self._calculate_improvement_score(memory.improvement)
            self.stats['total_improvement_score'] += improvement_score
        else:
            self.stats['failed_optimizations'] += 1

        self.logger.info(
            f"📚 Memory stored: {memory_id} - "
            f"{decision.action} ({'success' if memory.success else 'failed'})"
        )

        # Extract patterns from this memory
        await self._extract_patterns_from_memory(memory)

        # Future: Store in AuMemManager with full context
        # await self._store_in_aumemmanager(memory)

        return memory

    def _serialize_decision(self, decision) -> Dict[str, Any]:
        """Serialize decision for storage"""
        return {
            'decision_id': decision.decision_id,
            'timestamp': decision.timestamp,
            'priority': decision.priority.value if hasattr(decision.priority, 'value') else str(decision.priority),
            'action': decision.action,
            'rationale': decision.rationale,
            'risk_assessment': decision.risk_assessment,
            'ethical_compliance': decision.ethical_compliance,
            'expected_outcomes': decision.expected_outcomes,
            'context': decision.context
        }

    def _calculate_improvement_score(self, improvement: Dict[str, float]) -> float:
        """Calculate overall improvement score"""
        if not improvement:
            return 0.0

        # Average of all improvements
        scores = list(improvement.values())
        return sum(scores) / len(scores) if scores else 0.0

    async def retrieve_similar_decisions(
        self,
        context: Dict[str, Any],
        limit: int = 10
    ) -> List[OrchestrationMemory]:
        """
        Retrieve similar past decisions based on context.

        Aurora uses this to learn from her past experiences when making
        new decisions.

        Args:
            context: Current decision context
            limit: Maximum number of similar memories to return

        Returns:
            List of similar OrchestrationMemories
        """
        # Future: Use AuMemManager semantic search
        # For now, simple similarity based on action keywords

        focus = context.get('focus', '')
        optimization_type = context.get('type', '')

        similar_memories = []

        for memory in self.orchestration_memories.values():
            decision = memory.decision
            action = decision.get('action', '').lower()

            # Simple keyword matching
            if focus and focus.lower() in action:
                similar_memories.append(memory)
            elif optimization_type and optimization_type.lower() in action:
                similar_memories.append(memory)

        # Sort by recency (most recent first)
        similar_memories.sort(key=lambda m: m.timestamp, reverse=True)

        return similar_memories[:limit]

    async def _extract_patterns_from_memory(self, memory: OrchestrationMemory):
        """
        Extract patterns from a successful memory.

        Aurora learns by identifying what works and storing it as
        reusable patterns.
        """
        if not memory.success:
            return  # Only learn from successes

        # Extract temporal pattern
        hour = datetime.fromisoformat(memory.timestamp).hour
        if 9 <= hour <= 17:
            time_period = 'business_hours'
        elif 18 <= hour <= 23:
            time_period = 'evening'
        else:
            time_period = 'night'

        # Create pattern signature
        decision = memory.decision
        action_type = self._classify_action(decision['action'])

        pattern_signature = f"{action_type}_{time_period}"

        # Update or create pattern
        if pattern_signature in self.patterns:
            pattern = self.patterns[pattern_signature]
            pattern.sample_size += 1
            # Update success rate (running average)
            pattern.success_rate = (
                (pattern.success_rate * (pattern.sample_size - 1) + 1.0) /
                pattern.sample_size
            )
            pattern.last_updated = datetime.now().isoformat()
        else:
            # Create new pattern
            pattern = Pattern(
                pattern_id=pattern_signature,
                pattern_type='temporal',
                description=f"{action_type} optimization during {time_period}",
                conditions={
                    'action_type': action_type,
                    'time_period': time_period
                },
                recommended_action=decision['action'],
                success_rate=1.0,  # First success
                sample_size=1,
                discovered_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            self.patterns[pattern_signature] = pattern
            self.stats['total_patterns'] += 1

            self.logger.info(f"🔍 New pattern discovered: {pattern_signature}")

    def _classify_action(self, action: str) -> str:
        """Classify action into category"""
        action_lower = action.lower()

        if 'quantum' in action_lower:
            return 'quantum'
        elif 'ai' in action_lower or 'model' in action_lower:
            return 'ai_model'
        elif 'memory' in action_lower:
            return 'memory'
        elif 'breathing' in action_lower:
            return 'breathing'
        else:
            return 'general'

    async def get_applicable_patterns(
        self,
        context: Dict[str, Any]
    ) -> List[Pattern]:
        """
        Get patterns applicable to current context.

        Aurora uses this to apply learned wisdom to new situations.
        """
        applicable = []

        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:
            time_period = 'business_hours'
        elif 18 <= current_hour <= 23:
            time_period = 'evening'
        else:
            time_period = 'night'

        focus = context.get('focus', '')
        action_type = self._classify_action(focus)

        # Find matching patterns
        for pattern in self.patterns.values():
            if pattern.conditions.get('time_period') == time_period:
                if pattern.conditions.get('action_type') == action_type:
                    applicable.append(pattern)

        # Sort by confidence (best patterns first)
        applicable.sort(key=lambda p: p.confidence, reverse=True)

        return applicable

    async def update_expertise(
        self,
        domain: str,
        success: bool,
        delta: float = 0.001
    ):
        """
        Update Aurora's expertise in a domain based on outcome.

        Aurora evolves - her expertise increases with successful outcomes
        and decreases slightly with failures.
        """
        if domain not in self.expertise_evolution:
            self.expertise_evolution[domain] = [0.5]  # Start at 0.5

        current_expertise = self.expertise_evolution[domain][-1]

        if success:
            new_expertise = min(1.0, current_expertise + delta)
        else:
            new_expertise = max(0.0, current_expertise - delta / 2)  # Smaller penalty

        self.expertise_evolution[domain].append(new_expertise)

        self.logger.debug(
            f"📈 Expertise updated: {domain} "
            f"{current_expertise:.4f} → {new_expertise:.4f}"
        )

    def get_expertise_scores(self) -> Dict[str, float]:
        """Get current expertise scores for all domains"""
        return {
            domain: scores[-1]
            for domain, scores in self.expertise_evolution.items()
        }

    def get_expertise_evolution(self, domain: str) -> List[float]:
        """Get expertise evolution history for a domain"""
        return self.expertise_evolution.get(domain, [])

    def get_statistics(self) -> Dict[str, Any]:
        """Get institutional memory statistics"""
        avg_improvement = (
            self.stats['total_improvement_score'] /
            max(self.stats['successful_optimizations'], 1)
        )

        return {
            **self.stats,
            'average_improvement': avg_improvement,
            'success_rate': (
                self.stats['successful_optimizations'] /
                max(self.stats['total_memories'], 1)
            ),
            'patterns_discovered': self.stats['total_patterns'],
            'expertise_scores': self.get_expertise_scores()
        }

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get specific pattern by ID"""
        return self.patterns.get(pattern_id)

    def get_all_patterns(self) -> List[Pattern]:
        """Get all discovered patterns"""
        patterns = list(self.patterns.values())
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        return patterns

    def get_memory(self, memory_id: str) -> Optional[OrchestrationMemory]:
        """Get specific memory by ID"""
        return self.orchestration_memories.get(memory_id)

    def get_recent_memories(self, limit: int = 50) -> List[OrchestrationMemory]:
        """Get recent orchestration memories"""
        memories = list(self.orchestration_memories.values())
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]
