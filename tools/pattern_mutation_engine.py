"""
🧬 Aurora CloudBank Pattern Mutation Engine

Evolutionary algorithm for exploring symbolic pattern variations
with T1/SRB anchor tracking and cultural ethics validation.

Features:
- Genetic algorithm-based pattern evolution
- Fitness function customization
- Complete DLP tracking
- Cultural sensitivity validation (CASK)
- T1/SRB anchor lineage preservation
"""

import hashlib
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class Pattern:
    """Symbolic pattern with metadata"""
    sequence: str
    generation: int
    fitness_score: float
    parent_hash: Optional[str]
    t1_state: int
    srb_resolution: int
    cultural_score: float
    pattern_hash: str


class T1Anchor:
    """Temporal T1 anchor for tracking evolution"""
    def __init__(self):
        self.state = 0

    def advance(self, data: str) -> int:
        """Advance T1 temporal state"""
        self.state += len(str(data))
        return self.state

    def export(self) -> dict:
        """Export T1 anchor state"""
        return {"type": "T1", "state": self.state}


class SRBAnchor:
    """Spatial-Relational Boundary anchor"""
    def __init__(self):
        self.resolution = 0

    def resolve(self, boundary: str) -> int:
        """Resolve SRB boundary"""
        self.resolution += hash(str(boundary)) % 1000
        return self.resolution

    def export(self) -> dict:
        """Export SRB anchor state"""
        return {"type": "SRB", "resolution": self.resolution}


class PatternMutationEngine:
    """
    Evolutionary pattern mutation engine with Aurora symbolic anchoring
    """

    def __init__(self, anchor_seed: str = "MUTATION_ENGINE_001"):
        self.anchor_seed = anchor_seed
        self.t1 = T1Anchor()
        self.srb = SRBAnchor()
        self.generation_history: List[List[Pattern]] = []
        self.best_pattern: Optional[Pattern] = None

        # Fitness function registry
        self.fitness_functions = {
            "compactness": self._fitness_compactness,
            "diversity": self._fitness_diversity,
            "balance": self._fitness_balance,
            "complexity": self._fitness_complexity,
            "cultural_harmony": self._fitness_cultural_harmony,
        }

        # Mutation operators
        self.mutation_operators = [
            self._mutate_insert,
            self._mutate_delete,
            self._mutate_swap,
            self._mutate_duplicate,
            self._mutate_reverse,
        ]

    def _compute_pattern_hash(self, pattern: str, generation: int) -> str:
        """Compute SHA-256 hash for pattern"""
        data = f"{pattern}:{generation}:{self.anchor_seed}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _compute_cultural_score(self, pattern: str) -> float:
        """
        Compute cultural sensitivity score (mock CASK integration)
        Real implementation would use modules.cask
        """
        # Mock scoring based on pattern characteristics
        score = 0.5  # baseline
        
        # Patterns with balanced structure score higher
        if pattern.count("0") == pattern.count("9"):
            score += 0.2
        
        # Shorter patterns are more culturally neutral
        if len(pattern) < 20:
            score += 0.15
        
        # Patterns without extreme repetition
        max_repeat = max((pattern.count(c) for c in set(pattern)), default=1)
        if max_repeat < len(pattern) * 0.4:
            score += 0.15
        
        return min(1.0, score)

    def _fitness_compactness(self, pattern: str) -> float:
        """Fitness function: favor shorter, more compact patterns"""
        base_length = 20
        penalty = max(0, len(pattern) - base_length) * 0.05
        return max(0.0, 1.0 - penalty)

    def _fitness_diversity(self, pattern: str) -> float:
        """Fitness function: favor diverse character usage"""
        unique_chars = len(set(pattern))
        return min(1.0, unique_chars / 10.0)

    def _fitness_balance(self, pattern: str) -> float:
        """Fitness function: favor balanced patterns"""
        if not pattern:
            return 0.0
        
        # Count digit frequencies
        freqs = {}
        for char in pattern:
            freqs[char] = freqs.get(char, 0) + 1
        
        # Calculate variance from uniform distribution
        expected = len(pattern) / max(1, len(freqs))
        variance = sum((freq - expected) ** 2 for freq in freqs.values()) / max(1, len(freqs))
        
        # Lower variance = better balance
        return max(0.0, 1.0 - (variance / (len(pattern) ** 2)))

    def _fitness_complexity(self, pattern: str) -> float:
        """Fitness function: favor complex patterns"""
        if len(pattern) < 2:
            return 0.0
        
        # Measure entropy as complexity proxy
        freqs = {}
        for char in pattern:
            freqs[char] = freqs.get(char, 0) + 1
        
        entropy = 0.0
        for freq in freqs.values():
            prob = freq / len(pattern)
            if prob > 0:
                entropy -= prob * (prob ** 0.5)  # Simplified entropy
        
        return min(1.0, entropy)

    def _fitness_cultural_harmony(self, pattern: str) -> float:
        """Fitness function: cultural sensitivity score"""
        return self._compute_cultural_score(pattern)

    def _mutate_insert(self, pattern: str) -> str:
        """Insert random digit at random position"""
        if not pattern:
            return str(random.randint(0, 9))
        pos = random.randint(0, len(pattern))
        digit = str(random.randint(0, 9))
        return pattern[:pos] + digit + pattern[pos:]

    def _mutate_delete(self, pattern: str) -> str:
        """Delete random character"""
        if len(pattern) <= 1:
            return pattern
        pos = random.randint(0, len(pattern) - 1)
        return pattern[:pos] + pattern[pos + 1:]

    def _mutate_swap(self, pattern: str) -> str:
        """Swap two adjacent characters"""
        if len(pattern) < 2:
            return pattern
        pos = random.randint(0, len(pattern) - 2)
        chars = list(pattern)
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
        return ''.join(chars)

    def _mutate_duplicate(self, pattern: str) -> str:
        """Duplicate a random substring"""
        if not pattern:
            return pattern
        start = random.randint(0, len(pattern) - 1)
        end = random.randint(start + 1, min(start + 4, len(pattern)))
        substring = pattern[start:end]
        pos = random.randint(0, len(pattern))
        return pattern[:pos] + substring + pattern[pos:]

    def _mutate_reverse(self, pattern: str) -> str:
        """Reverse a random substring"""
        if len(pattern) < 2:
            return pattern
        start = random.randint(0, len(pattern) - 2)
        end = random.randint(start + 2, len(pattern))
        return pattern[:start] + pattern[start:end][::-1] + pattern[end:]

    def create_pattern(
        self,
        sequence: str,
        generation: int,
        parent_hash: Optional[str] = None
    ) -> Pattern:
        """Create a pattern with full metadata"""
        pattern_hash = self._compute_pattern_hash(sequence, generation)
        
        return Pattern(
            sequence=sequence,
            generation=generation,
            fitness_score=0.0,  # Will be computed later
            parent_hash=parent_hash,
            t1_state=self.t1.advance(sequence),
            srb_resolution=self.srb.resolve(f"gen_{generation}_{pattern_hash}"),
            cultural_score=self._compute_cultural_score(sequence),
            pattern_hash=pattern_hash
        )

    def evaluate_fitness(
        self,
        pattern: Pattern,
        fitness_fn: str = "compactness"
    ) -> float:
        """Evaluate pattern fitness using specified function"""
        if fitness_fn not in self.fitness_functions:
            raise ValueError(f"Unknown fitness function: {fitness_fn}")
        
        fitness_func = self.fitness_functions[fitness_fn]
        score = fitness_func(pattern.sequence)
        
        # Boost score based on cultural sensitivity
        score = score * (0.7 + 0.3 * pattern.cultural_score)
        
        return score

    def mutate(self, pattern: Pattern) -> Pattern:
        """Apply random mutation to pattern"""
        operator = random.choice(self.mutation_operators)
        new_sequence = operator(pattern.sequence)
        
        new_pattern = self.create_pattern(
            sequence=new_sequence,
            generation=pattern.generation + 1,
            parent_hash=pattern.pattern_hash
        )
        
        return new_pattern

    def evolve(
        self,
        initial_pattern: str,
        generations: int,
        population_size: int = 10,
        mutation_rate: float = 0.8,
        elite_size: int = 2,
        fitness_fn: str = "compactness"
    ) -> Dict[str, Any]:
        """
        Run evolutionary algorithm to find optimal pattern variations
        
        Args:
            initial_pattern: Starting pattern sequence
            generations: Number of generations to evolve
            population_size: Size of population per generation
            mutation_rate: Probability of mutation (0.0-1.0)
            elite_size: Number of top patterns to preserve each generation
            fitness_fn: Fitness function name
            
        Returns:
            Evolution results with full DLP tracking
        """
        # Initialize population
        population = [
            self.create_pattern(initial_pattern, 0)
            for _ in range(population_size)
        ]
        
        # Evaluate initial fitness
        for p in population:
            p.fitness_score = self.evaluate_fitness(p, fitness_fn)
        
        self.generation_history.append(population)
        
        # Evolve through generations
        for gen in range(1, generations + 1):
            # Sort by fitness
            population.sort(key=lambda p: p.fitness_score, reverse=True)
            
            # Track best pattern
            if not self.best_pattern or population[0].fitness_score > self.best_pattern.fitness_score:
                self.best_pattern = population[0]
            
            # Create next generation
            next_gen = []
            
            # Elitism: preserve top patterns
            next_gen.extend(population[:elite_size])
            
            # Generate offspring through mutation
            while len(next_gen) < population_size:
                # Select parent (tournament selection)
                parent = max(random.sample(population, 3), key=lambda p: p.fitness_score)
                
                # Apply mutation with probability
                if random.random() < mutation_rate:
                    child = self.mutate(parent)
                else:
                    child = self.create_pattern(parent.sequence, gen, parent.pattern_hash)
                
                # Evaluate child fitness
                child.fitness_score = self.evaluate_fitness(child, fitness_fn)
                next_gen.append(child)
            
            population = next_gen
            self.generation_history.append(population)
        
        # Generate results
        final_population = self.generation_history[-1]
        final_population.sort(key=lambda p: p.fitness_score, reverse=True)
        
        return self._create_results(
            initial_pattern=initial_pattern,
            final_population=final_population,
            fitness_fn=fitness_fn,
            generations=generations
        )

    def _create_results(
        self,
        initial_pattern: str,
        final_population: List[Pattern],
        fitness_fn: str,
        generations: int
    ) -> Dict[str, Any]:
        """Create comprehensive results with DLP tracking"""
        return {
            "success": True,
            "initial_pattern": initial_pattern,
            "best_pattern": {
                "sequence": self.best_pattern.sequence,
                "fitness_score": self.best_pattern.fitness_score,
                "generation": self.best_pattern.generation,
                "cultural_score": self.best_pattern.cultural_score,
                "pattern_hash": self.best_pattern.pattern_hash,
            },
            "top_5_patterns": [
                {
                    "sequence": p.sequence,
                    "fitness_score": p.fitness_score,
                    "cultural_score": p.cultural_score,
                    "generation": p.generation,
                }
                for p in final_population[:5]
            ],
            "evolution_stats": {
                "total_generations": generations,
                "patterns_evaluated": len(self.generation_history) * len(final_population),
                "fitness_improvement": (
                    self.best_pattern.fitness_score - 
                    self.generation_history[0][0].fitness_score
                ),
                "cultural_score_avg": sum(p.cultural_score for p in final_population) / len(final_population),
            },
            "metadata": {
                "anchor_seed": self.anchor_seed,
                "t1_anchor": self.t1.export(),
                "srb_anchor": self.srb.export(),
                "fitness_function": fitness_fn,
                "context_tag": "pattern_mutation_engine",
                "timestamp": datetime.now().isoformat(),
                "dlp_hash": self._compute_dlp_hash(),
            }
        }

    def _compute_dlp_hash(self) -> str:
        """Compute DLP tracking hash"""
        data = f"{self.anchor_seed}:{self.t1.state}:{self.srb.resolution}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def export_lineage(self, pattern_hash: str) -> List[Dict[str, Any]]:
        """Export complete lineage of a pattern through all generations"""
        lineage = []
        current_hash = pattern_hash
        
        # Search backwards through generations
        for gen_idx in range(len(self.generation_history) - 1, -1, -1):
            generation = self.generation_history[gen_idx]
            for pattern in generation:
                if pattern.pattern_hash == current_hash:
                    lineage.insert(0, {
                        "generation": pattern.generation,
                        "sequence": pattern.sequence,
                        "fitness_score": pattern.fitness_score,
                        "cultural_score": pattern.cultural_score,
                        "pattern_hash": pattern.pattern_hash,
                        "parent_hash": pattern.parent_hash,
                    })
                    current_hash = pattern.parent_hash
                    if current_hash is None:
                        return lineage
        
        return lineage


def demo_pattern_mutation():
    """Demonstration of Pattern Mutation Engine"""
    print("🧬 Aurora CloudBank Pattern Mutation Engine Demo")
    print("=" * 60)
    print()
    
    # Initialize engine
    engine = PatternMutationEngine(anchor_seed="DEMO_001")
    
    # Run evolution with different fitness functions
    fitness_functions = ["compactness", "diversity", "balance", "cultural_harmony"]
    
    for fitness_fn in fitness_functions:
        print(f"🔬 Evolving with fitness function: {fitness_fn}")
        print("-" * 60)
        
        results = engine.evolve(
            initial_pattern="001999555",
            generations=8,
            population_size=12,
            mutation_rate=0.75,
            elite_size=2,
            fitness_fn=fitness_fn
        )
        
        print(f"Initial: {results['initial_pattern']}")
        print(f"Best:    {results['best_pattern']['sequence']}")
        print(f"Fitness: {results['best_pattern']['fitness_score']:.4f}")
        print(f"Cultural Score: {results['best_pattern']['cultural_score']:.4f}")
        print(f"Generation: {results['best_pattern']['generation']}")
        print()
        
        print("Top 3 Variations:")
        for i, pattern in enumerate(results['top_5_patterns'][:3], 1):
            print(f"  {i}. {pattern['sequence']} "
                  f"(fitness: {pattern['fitness_score']:.4f}, "
                  f"cultural: {pattern['cultural_score']:.4f})")
        print()
        
        print(f"📊 Evolution Stats:")
        print(f"  Patterns Evaluated: {results['evolution_stats']['patterns_evaluated']}")
        print(f"  Fitness Improvement: {results['evolution_stats']['fitness_improvement']:.4f}")
        print(f"  Avg Cultural Score: {results['evolution_stats']['cultural_score_avg']:.4f}")
        print()
        
        print(f"🔐 DLP Metadata:")
        print(f"  T1 State: {results['metadata']['t1_anchor']['state']}")
        print(f"  SRB Resolution: {results['metadata']['srb_anchor']['resolution']}")
        print(f"  DLP Hash: {results['metadata']['dlp_hash']}")
        print()
        print("=" * 60)
        print()
    
    # Export lineage for best pattern
    print("📜 Lineage Trace for Best Pattern:")
    print("-" * 60)
    best_hash = results['best_pattern']['pattern_hash']
    lineage = engine.export_lineage(best_hash)
    
    for entry in lineage:
        print(f"Gen {entry['generation']}: {entry['sequence']} "
              f"(fitness: {entry['fitness_score']:.4f})")
    print()


if __name__ == "__main__":
    demo_pattern_mutation()
