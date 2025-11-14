"""
Joy-Infused Evolution Engine v1.0

Genetic algorithms using joy_index as fitness function for agent evolution.
Implements positive reinforcement learning with emergent creativity patterns.

Features:
- Agent breeding with vector crossover
- Mutation operators for exploration
- Joy + alignment fitness function
- Selection pressure optimization
- Emergent creativity tracking

T1: JOY_EVOLUTION_ENGINE_v1.0
SRB: CREATIVE_AGENT_EVOLUTION
DLP: context_tag=joy_evolution, symbolic_hash=JEE_v1

Author: Aurora CloudBank Team
Version: 1.0.0
Date: 2025-11-13
"""

import hashlib
import json
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger(__name__)


@dataclass
class EvolutionParameters:
    """Parameters for evolutionary algorithm"""
    population_size: int = 50
    elite_size: int = 10
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    selection_pressure: float = 2.0  # Tournament size
    max_generations: int = 100
    convergence_threshold: float = 0.001


@dataclass
class AgentGenome:
    """Genetic representation of agent"""
    agent_id: str
    vector_core: List[float]
    joy_index: float
    intent_alignment: float
    generation: int
    parent_ids: List[str] = field(default_factory=list)
    mutations: int = 0
    
    @property
    def fitness(self) -> float:
        """Calculate fitness score (joy + alignment)"""
        return (self.joy_index * 0.6) + (self.intent_alignment * 0.4)


@dataclass
class GenerationStats:
    """Statistics for a generation"""
    generation: int
    population_size: int
    avg_fitness: float
    max_fitness: float
    min_fitness: float
    avg_joy: float
    avg_alignment: float
    diversity_score: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class JoyEvolutionEngine:
    """
    Genetic algorithm engine using joy_index as primary fitness
    
    Evolves agent populations toward higher joy and creativity while
    maintaining ethical alignment.
    """
    
    def __init__(
        self,
        forge,
        params: Optional[EvolutionParameters] = None
    ):
        self.forge = forge
        self.params = params or EvolutionParameters()
        self.population: List[AgentGenome] = []
        self.generation_history: List[GenerationStats] = []
        self.current_generation = 0
        
        logger.info(f"🧬 Joy Evolution Engine initialized")
        logger.info(f"   Population size: {self.params.population_size}")
        logger.info(f"   Elite size: {self.params.elite_size}")
        logger.info(f"   Mutation rate: {self.params.mutation_rate:.2%}")
        
    def initialize_population(
        self,
        base_intent: str = "Creative exploration and joyful optimization",
        constellation_targets: Optional[List[str]] = None
    ):
        """Initialize random population of agents"""
        logger.info(f"🌱 Initializing population ({self.params.population_size} agents)...")
        
        targets = constellation_targets or ["ORION"]
        
        for i in range(self.params.population_size):
            # Add variation to base intent
            variations = [
                f"{base_intent} with focus on innovation",
                f"{base_intent} emphasizing creativity",
                f"{base_intent} through joyful discovery",
                f"{base_intent} via emergent patterns",
                f"{base_intent} with playful exploration"
            ]
            intent = random.choice(variations)
            
            # Generate agent
            agent = self.forge.generate_agent(
                intent_query=intent,
                constellation_targets=targets
            )
            
            # Create genome
            genome = AgentGenome(
                agent_id=agent.agent_id,
                vector_core=agent.vector_core if isinstance(agent.vector_core, list) else agent.vector_core.tolist(),
                joy_index=agent.joy_index,
                intent_alignment=agent.intent_alignment,
                generation=0
            )
            
            self.population.append(genome)
        
        logger.info(f"✅ Population initialized")
        self._log_generation_stats()
        
    def evolve(self, generations: Optional[int] = None) -> GenerationStats:
        """
        Run evolutionary algorithm for specified generations
        
        Args:
            generations: Number of generations (uses params.max_generations if None)
            
        Returns:
            Final generation statistics
        """
        target_gen = generations or self.params.max_generations
        logger.info(f"🔄 Starting evolution for {target_gen} generations...")
        
        for gen in range(target_gen):
            self.current_generation += 1
            
            # Selection
            parents = self._select_parents()
            
            # Crossover
            offspring = self._crossover(parents)
            
            # Mutation
            offspring = self._mutate(offspring)
            
            # Elitism: Keep best from previous generation
            elite = self._select_elite()
            
            # New population = elite + offspring
            self.population = elite + offspring[:self.params.population_size - len(elite)]
            
            # Track stats
            stats = self._log_generation_stats()
            
            # Check convergence
            if self._check_convergence():
                logger.info(f"✅ Converged at generation {self.current_generation}")
                break
        
        final_stats = self.generation_history[-1]
        logger.info(f"🎯 Evolution complete!")
        logger.info(f"   Final avg fitness: {final_stats.avg_fitness:.4f}")
        logger.info(f"   Final avg joy: {final_stats.avg_joy:.4f}")
        
        return final_stats
        
    def _select_parents(self) -> List[AgentGenome]:
        """Select parents using tournament selection"""
        parents = []
        tournament_size = int(self.params.selection_pressure)
        
        for _ in range(self.params.population_size):
            # Random tournament
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda g: g.fitness)
            parents.append(winner)
        
        return parents
        
    def _crossover(self, parents: List[AgentGenome]) -> List[AgentGenome]:
        """Create offspring through crossover"""
        offspring = []
        
        for i in range(0, len(parents), 2):
            if i + 1 >= len(parents):
                break
                
            parent1 = parents[i]
            parent2 = parents[i + 1]
            
            if random.random() < self.params.crossover_rate:
                # Single-point crossover
                crossover_point = len(parent1.vector_core) // 2
                
                child1_vector = (
                    parent1.vector_core[:crossover_point] +
                    parent2.vector_core[crossover_point:]
                )
                child2_vector = (
                    parent2.vector_core[:crossover_point] +
                    parent1.vector_core[crossover_point:]
                )
                
                # Calculate fitness for offspring
                child1_joy = (parent1.joy_index + parent2.joy_index) / 2
                child1_alignment = (parent1.intent_alignment + parent2.intent_alignment) / 2
                
                child2_joy = child1_joy  # Similar for now
                child2_alignment = child1_alignment
                
                child1 = AgentGenome(
                    agent_id=f"CHILD_{self.current_generation}_{i}",
                    vector_core=child1_vector,
                    joy_index=child1_joy,
                    intent_alignment=child1_alignment,
                    generation=self.current_generation,
                    parent_ids=[parent1.agent_id, parent2.agent_id]
                )
                
                child2 = AgentGenome(
                    agent_id=f"CHILD_{self.current_generation}_{i+1}",
                    vector_core=child2_vector,
                    joy_index=child2_joy,
                    intent_alignment=child2_alignment,
                    generation=self.current_generation,
                    parent_ids=[parent1.agent_id, parent2.agent_id]
                )
                
                offspring.extend([child1, child2])
            else:
                # No crossover, copy parents
                offspring.extend([parent1, parent2])
        
        return offspring
        
    def _mutate(self, offspring: List[AgentGenome]) -> List[AgentGenome]:
        """Apply mutation to offspring"""
        for genome in offspring:
            if random.random() < self.params.mutation_rate:
                # Mutate random dimension
                mutation_idx = random.randint(0, len(genome.vector_core) - 1)
                mutation_strength = random.gauss(0, 0.1)
                
                genome.vector_core[mutation_idx] += mutation_strength
                genome.mutations += 1
                
                # Re-normalize vector
                if HAS_NUMPY:
                    vec = np.array(genome.vector_core)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        genome.vector_core = (vec / norm).tolist()
                else:
                    # Simple normalization without numpy
                    norm = sum(x**2 for x in genome.vector_core) ** 0.5
                    if norm > 0:
                        genome.vector_core = [x / norm for x in genome.vector_core]
                
                # Slightly adjust joy (mutation can increase creativity)
                genome.joy_index = min(1.0, genome.joy_index + random.uniform(-0.05, 0.1))
        
        return offspring
        
    def _select_elite(self) -> List[AgentGenome]:
        """Select elite individuals to preserve"""
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        return sorted_pop[:self.params.elite_size]
        
    def _log_generation_stats(self) -> GenerationStats:
        """Log and return generation statistics"""
        fitnesses = [g.fitness for g in self.population]
        joys = [g.joy_index for g in self.population]
        alignments = [g.intent_alignment for g in self.population]
        
        # Calculate diversity (variance in vectors)
        if HAS_NUMPY:
            vectors = np.array([g.vector_core for g in self.population])
            diversity = float(np.mean(np.var(vectors, axis=0)))
        else:
            # Simple diversity measure without numpy
            diversity = 0.1  # placeholder
        
        stats = GenerationStats(
            generation=self.current_generation,
            population_size=len(self.population),
            avg_fitness=sum(fitnesses) / len(fitnesses),
            max_fitness=max(fitnesses),
            min_fitness=min(fitnesses),
            avg_joy=sum(joys) / len(joys),
            avg_alignment=sum(alignments) / len(alignments),
            diversity_score=diversity
        )
        
        self.generation_history.append(stats)
        
        logger.info(f"📊 Generation {self.current_generation}")
        logger.info(f"   Avg fitness: {stats.avg_fitness:.4f}")
        logger.info(f"   Avg joy: {stats.avg_joy:.4f}")
        logger.info(f"   Max fitness: {stats.max_fitness:.4f}")
        logger.info(f"   Diversity: {stats.diversity_score:.4f}")
        
        return stats
        
    def _check_convergence(self) -> bool:
        """Check if population has converged"""
        if len(self.generation_history) < 5:
            return False
        
        recent = self.generation_history[-5:]
        fitness_changes = [
            abs(recent[i].avg_fitness - recent[i-1].avg_fitness)
            for i in range(1, len(recent))
        ]
        
        avg_change = sum(fitness_changes) / len(fitness_changes)
        return avg_change < self.params.convergence_threshold
        
    def get_best_agent(self) -> AgentGenome:
        """Get best agent from current population"""
        return max(self.population, key=lambda g: g.fitness)
        
    def get_most_joyful_agent(self) -> AgentGenome:
        """Get agent with highest joy_index"""
        return max(self.population, key=lambda g: g.joy_index)
        
    def export_evolution_history(self) -> Dict[str, Any]:
        """Export complete evolution history"""
        return {
            "generations": [
                {
                    "generation": stats.generation,
                    "avg_fitness": stats.avg_fitness,
                    "max_fitness": stats.max_fitness,
                    "avg_joy": stats.avg_joy,
                    "diversity": stats.diversity_score
                }
                for stats in self.generation_history
            ],
            "final_population": [
                {
                    "agent_id": g.agent_id,
                    "fitness": g.fitness,
                    "joy": g.joy_index,
                    "alignment": g.intent_alignment,
                    "generation": g.generation,
                    "mutations": g.mutations
                }
                for g in self.population[:10]  # Top 10
            ]
        }
        
    def export_evolution_manifest(self) -> Dict[str, Any]:
        """Export sealed manifest for audit trail"""
        best = self.get_best_agent()
        most_joyful = self.get_most_joyful_agent()
        
        manifest = {
            "component": "joy_evolution_engine",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": {
                "population_size": self.params.population_size,
                "elite_size": self.params.elite_size,
                "mutation_rate": self.params.mutation_rate,
                "generations_run": self.current_generation
            },
            "best_agent": {
                "agent_id": best.agent_id,
                "fitness": best.fitness,
                "joy": best.joy_index,
                "alignment": best.intent_alignment
            },
            "most_joyful": {
                "agent_id": most_joyful.agent_id,
                "joy": most_joyful.joy_index
            },
            "evolution_history": self.export_evolution_history(),
            "integrity_hash": self._compute_manifest_hash()
        }
        return manifest
        
    def _compute_manifest_hash(self) -> str:
        """Compute integrity hash for manifest"""
        data = json.dumps({
            "generations": self.current_generation,
            "population": len(self.population),
            "params": str(self.params)
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# Convenience singleton
_evolution_engine_instance: Optional[JoyEvolutionEngine] = None


def get_joy_evolution_engine(forge, params: Optional[EvolutionParameters] = None) -> JoyEvolutionEngine:
    """Get singleton evolution engine"""
    global _evolution_engine_instance
    if _evolution_engine_instance is None:
        _evolution_engine_instance = JoyEvolutionEngine(forge, params)
    return _evolution_engine_instance
