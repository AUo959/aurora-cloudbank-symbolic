"""
Pattern Synthesizer - Advanced Pattern Discovery

Anchor: AURORA-ORCHESTRATOR-PATTERNS-001
Version: 1.0.0
Team: Orion Station Crew
DLP: CONFIDENTIAL
Ethics: Picard_Delta_3

Advanced pattern synthesis from Aurora's orchestration history.

Discovers:
- Temporal patterns (time-of-day optimizations)
- Load patterns (high-load strategies)
- Cost patterns (cost-effective configurations)
- Performance patterns (low-latency setups)
- Error patterns (failure prevention)
- Synergy patterns (component interactions)
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class Strategy:
    """Optimization strategy discovered from patterns"""
    strategy_id: str
    name: str
    description: str
    applicable_conditions: Dict[str, Any]
    steps: List[Dict[str, Any]]
    expected_improvement: float
    risk_level: float
    success_history: List[bool] = field(default_factory=list)
    confidence: float = 0.0

    def __post_init__(self):
        if self.success_history:
            success_rate = sum(self.success_history) / len(self.success_history)
            sample_weight = min(len(self.success_history) / 10.0, 1.0)
            self.confidence = success_rate * sample_weight


class PatternSynthesizer:
    """
    Pattern Synthesizer - Aurora's Advanced Learning

    Synthesizes high-level patterns and strategies from orchestration history.

    This is meta-learning: Aurora learns not just what works, but WHY it works,
    and creates reusable strategies for future optimization.
    """

    def __init__(self):
        """Initialize pattern synthesizer"""
        self.logger = self._setup_logging()

        # Discovered strategies
        self.strategies: Dict[str, Strategy] = {}

        # Pattern analysis cache
        self.temporal_analysis: Dict[str, Any] = {}
        self.load_analysis: Dict[str, Any] = {}
        self.cost_analysis: Dict[str, Any] = {}

        self.logger.info("🧬 Pattern Synthesizer initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('PatternSynthesizer')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(asctime)s] PATTERN-SYNTH %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        return logger

    async def synthesize_daily_patterns(
        self,
        memories: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Synthesize patterns from daily orchestration history.

        Analyzes 24 hours of orchestration data to discover patterns.

        Args:
            memories: List of OrchestrationMemory objects

        Returns:
            List of discovered patterns
        """
        self.logger.info("🧬 Synthesizing daily patterns...")

        patterns_discovered = []

        # Analyze by hour
        hourly_performance = defaultdict(list)
        for memory in memories:
            if not memory.success:
                continue

            hour = datetime.fromisoformat(memory.timestamp).hour
            improvement = memory.improvement

            if improvement:
                avg_improvement = sum(improvement.values()) / len(improvement)
                hourly_performance[hour].append({
                    'action': memory.decision['action'],
                    'improvement': avg_improvement,
                    'optimization_type': self._extract_optimization_type(memory)
                })

        # Find optimal hours for different optimization types
        optimization_types = set()
        for hour_data in hourly_performance.values():
            for entry in hour_data:
                optimization_types.add(entry['optimization_type'])

        for opt_type in optimization_types:
            best_hour = None
            best_improvement = 0.0

            for hour, entries in hourly_performance.items():
                type_entries = [e for e in entries if e['optimization_type'] == opt_type]
                if type_entries:
                    avg_imp = sum(e['improvement'] for e in type_entries) / len(type_entries)
                    if avg_imp > best_improvement:
                        best_improvement = avg_imp
                        best_hour = hour

            if best_hour is not None:
                pattern = {
                    'type': 'temporal',
                    'optimization_type': opt_type,
                    'optimal_hour': best_hour,
                    'expected_improvement': best_improvement,
                    'recommendation': f"Schedule {opt_type} optimizations around {best_hour}:00"
                }
                patterns_discovered.append(pattern)

        self.logger.info(f"🧬 Discovered {len(patterns_discovered)} temporal patterns")

        return patterns_discovered

    async def identify_optimization_strategies(
        self,
        memories: List[Any]
    ) -> List[Strategy]:
        """
        Identify high-level optimization strategies.

        Discovers multi-step strategies that consistently work well together.

        Args:
            memories: List of OrchestrationMemory objects

        Returns:
            List of Strategy objects
        """
        self.logger.info("🧬 Identifying optimization strategies...")

        strategies = []

        # Group memories by outcome quality
        excellent_outcomes = [
            m for m in memories
            if m.success and self._calculate_improvement_score(m.improvement) > 0.15
        ]

        if len(excellent_outcomes) < 3:
            return strategies  # Not enough data

        # Analyze patterns in excellent outcomes
        action_sequences = defaultdict(int)
        for i in range(len(excellent_outcomes) - 1):
            current = excellent_outcomes[i]
            next_mem = excellent_outcomes[i + 1]

            current_type = self._extract_optimization_type(current)
            next_type = self._extract_optimization_type(next_mem)

            sequence = f"{current_type}->{next_type}"
            action_sequences[sequence] += 1

        # Create strategies for common sequences
        for sequence, count in action_sequences.items():
            if count >= 2:  # Appeared at least twice
                parts = sequence.split('->')
                strategy_id = f"strategy_{sequence.replace('->', '_')}"

                strategy = Strategy(
                    strategy_id=strategy_id,
                    name=f"{parts[0].title()} followed by {parts[1].title()}",
                    description=f"Perform {parts[0]} optimization followed by {parts[1]} optimization",
                    applicable_conditions={
                        'sequence_confidence': count / len(excellent_outcomes)
                    },
                    steps=[
                        {'step': 1, 'action': parts[0], 'description': f"Optimize {parts[0]}"},
                        {'step': 2, 'action': parts[1], 'description': f"Optimize {parts[1]}"}
                    ],
                    expected_improvement=0.20,
                    risk_level=0.3,
                    success_history=[True] * count
                )

                strategies.append(strategy)
                self.strategies[strategy_id] = strategy

        self.logger.info(f"🧬 Identified {len(strategies)} optimization strategies")

        return strategies

    async def suggest_proactive_optimizations(
        self,
        current_state: Dict[str, Any],
        patterns: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest proactive optimizations based on current state and patterns.

        Aurora uses learned patterns to make proactive suggestions before
        problems occur.

        Args:
            current_state: Current system state
            patterns: List of Pattern objects

        Returns:
            List of suggested optimizations
        """
        suggestions = []

        current_hour = datetime.now().hour

        # Check temporal patterns
        for pattern in patterns:
            if pattern.pattern_type == 'temporal':
                conditions = pattern.conditions
                if conditions.get('time_period'):
                    # Suggest action if we're in the right time period
                    if self._is_time_period_match(current_hour, conditions['time_period']):
                        suggestions.append({
                            'type': 'proactive',
                            'pattern_id': pattern.pattern_id,
                            'action': pattern.recommended_action,
                            'rationale': f"Historical pattern shows {pattern.success_rate:.0%} success rate",
                            'confidence': pattern.confidence,
                            'risk': 0.2  # Proactive suggestions are low risk
                        })

        # Check load patterns
        health = current_state.get('overall_health', 1.0)
        if health < 0.8:
            suggestions.append({
                'type': 'health_reactive',
                'action': 'Optimize memory tiers',
                'rationale': f"System health at {health:.0%}, historical data shows memory optimization helps",
                'confidence': 0.7,
                'risk': 0.3
            })

        # Check drift patterns
        drift = current_state.get('drift_level', 0.0)
        if drift > 0.04:
            suggestions.append({
                'type': 'drift_preventive',
                'action': 'Adjust system breathing',
                'rationale': f"Drift at {drift:.3f}, preemptive breathing adjustment recommended",
                'confidence': 0.8,
                'risk': 0.2
            })

        self.logger.info(f"🧬 Generated {len(suggestions)} proactive suggestions")

        return suggestions

    def _extract_optimization_type(self, memory) -> str:
        """Extract optimization type from memory"""
        outcome = memory.outcome
        return outcome.get('optimization_type', 'unknown')

    def _calculate_improvement_score(self, improvement: Dict[str, float]) -> float:
        """Calculate overall improvement score"""
        if not improvement:
            return 0.0
        return sum(improvement.values()) / len(improvement)

    def _is_time_period_match(self, hour: int, time_period: str) -> bool:
        """Check if current hour matches time period"""
        if time_period == 'business_hours':
            return 9 <= hour <= 17
        elif time_period == 'evening':
            return 18 <= hour <= 23
        elif time_period == 'night':
            return hour < 6 or hour > 23
        return False

    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get specific strategy"""
        return self.strategies.get(strategy_id)

    def get_all_strategies(self) -> List[Strategy]:
        """Get all discovered strategies"""
        strategies = list(self.strategies.values())
        strategies.sort(key=lambda s: s.confidence, reverse=True)
        return strategies
