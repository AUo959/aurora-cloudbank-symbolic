# Quantum Forge v3.0 - Phases 6 & 7 Quick Reference

## Phase 6: Constellation Topology Mapping

**Purpose:** Optimize Aurora's physical architecture for quantum operations.

### Core Classes

#### ConstellationTopologyMapper
Maps physical module architecture to quantum-optimal topology.

```python
from modules.quantum_forge import (
    ConstellationTopologyMapper,
    get_topology_mapper,
    TopologyMetric,
    ModuleType
)

# Get mapper (auto-registers 8 core modules)
mapper = get_topology_mapper(
    optimization_metric=TopologyMetric.ENTANGLEMENT_FIDELITY
)

# Calculate optimal topology
mapping = mapper.calculate_optimal_topology()
print(f"Average fidelity: {mapping.average_fidelity:.4f}")
print(f"Total links: {len(mapping.links)}")

# Optimize placement
new_positions = mapper.optimize_module_placement(
    module_ids=["quantum_forge", "aumemmanager"],
    target_fidelity=0.95
)

# Find coherence-preserving route
route = mapper.find_coherence_preserving_route(
    source_id="quantum_forge",
    target_id="aumemmanager"
)
print(f"Route: {' → '.join(route)}")

# Export for visualization
viz_data = mapper.export_topology_visualization()
```

### Key Features

**Optimization Metrics:**
- `ENTANGLEMENT_FIDELITY` - Maximize quantum fidelity between modules
- `DECOHERENCE_TIME` - Minimize decoherence rates
- `PATH_LENGTH` - Minimize physical distances
- `COMMUNICATION_COST` - Minimize communication overhead

**Auto-Registered Modules (8 core):**
1. `aumemmanager` - Memory (coherence 0.95)
2. `quantum_simulator` - Quantum ops (coherence 0.98)
3. `data_guardian` - Data protection (coherence 0.85)
4. `insight_ledger` - Insights (coherence 0.80)
5. `gumas_ethics` - Ethics (coherence 0.90)
6. `monitoring_dashboard` - Monitoring (coherence 0.75)
7. `r2_telemetry` - Telemetry (coherence 0.70)
8. `quantum_forge` - Agent generation (coherence 0.95)

### Common Operations

**Register Custom Module:**
```python
from modules.quantum_forge import ModuleNode, ModuleType

custom_module = ModuleNode(
    module_id="my_module",
    module_type=ModuleType.AGENT,
    position=(2.0, 1.5, 0.5),
    coherence_requirement=0.88,
    communication_frequency=150.0
)
mapper.register_module(custom_module)
```

**Optimize for Target Fidelity:**
```python
# Move high-coherence modules close together
new_positions = mapper.optimize_module_placement(
    module_ids=["quantum_forge", "aumemmanager", "quantum_simulator"],
    target_fidelity=0.98
)

# Apply new positions
for module_id, position in new_positions.items():
    mapper.modules[module_id].position = position
    
# Recalculate topology with new positions
optimized_mapping = mapper.calculate_optimal_topology()
```

**Export Manifest:**
```python
manifest = mapper.export_topology_manifest()
print(f"Modules: {manifest['modules']}")
print(f"Links: {manifest['active_links']}")
print(f"Hash: {manifest['integrity_hash']}")
```

---

## Phase 7: Joy-Infused Evolution Engine

**Purpose:** Evolve agent populations toward higher joy and creativity using genetic algorithms.

### Core Classes

#### JoyEvolutionEngine
Genetic algorithm engine with joy_index as primary fitness.

```python
from modules.quantum_forge import (
    QuantumForge,
    EthicsLevel,
    JoyEvolutionEngine,
    EvolutionParameters,
    get_joy_evolution_engine
)

# Initialize forge
forge = QuantumForge(default_ethics_level=EthicsLevel.BALANCED)

# Create evolution engine
params = EvolutionParameters(
    population_size=50,
    elite_size=10,
    mutation_rate=0.1,
    crossover_rate=0.7,
    max_generations=100
)
engine = JoyEvolutionEngine(forge, params)

# Initialize population
engine.initialize_population(
    base_intent="Creative exploration and joyful optimization",
    constellation_targets=["ORION"]
)

# Evolve
final_stats = engine.evolve(generations=50)
print(f"Final avg fitness: {final_stats.avg_fitness:.4f}")
print(f"Final avg joy: {final_stats.avg_joy:.4f}")

# Get best agents
best = engine.get_best_agent()
most_joyful = engine.get_most_joyful_agent()

print(f"Best agent: {best.agent_id}")
print(f"  Fitness: {best.fitness:.4f}")
print(f"  Joy: {best.joy_index:.4f}")
print(f"  Alignment: {best.intent_alignment:.4f}")
```

### Key Features

**Fitness Function:**
```python
fitness = (joy_index * 0.6) + (intent_alignment * 0.4)
```

**Genetic Operators:**

1. **Selection:** Tournament selection with configurable pressure
2. **Crossover:** Single-point vector crossover
3. **Mutation:** Gaussian mutation with re-normalization
4. **Elitism:** Preserve top performers across generations

**Evolution Parameters:**
```python
EvolutionParameters(
    population_size=50,           # Number of agents
    elite_size=10,                # Top performers to preserve
    mutation_rate=0.1,            # 10% mutation probability
    crossover_rate=0.7,           # 70% crossover probability
    selection_pressure=2.0,       # Tournament size
    max_generations=100,          # Maximum generations
    convergence_threshold=0.001   # Fitness change threshold
)
```

### Common Operations

**Track Evolution History:**
```python
# Access generation statistics
for stats in engine.generation_history:
    print(f"Gen {stats.generation}: "
          f"fitness={stats.avg_fitness:.4f}, "
          f"joy={stats.avg_joy:.4f}")

# Export complete history
history = engine.export_evolution_history()
```

**Customize Base Intent:**
```python
# Initialize with specific creative focus
engine.initialize_population(
    base_intent="Innovative problem solving with playful exploration",
    constellation_targets=["ORION", "NEXUS"]
)
```

**Convergence Detection:**
```python
# Evolution automatically stops if population converges
# (fitness change < threshold for 5 consecutive generations)
final_stats = engine.evolve()  # May stop early

if engine.current_generation < engine.params.max_generations:
    print(f"Converged at generation {engine.current_generation}")
```

**Export Manifest:**
```python
manifest = engine.export_evolution_manifest()
print(f"Best agent: {manifest['best_agent']}")
print(f"Most joyful: {manifest['most_joyful']}")
print(f"Generations: {manifest['parameters']['generations_run']}")
```

---

## Integration Example: Topology + Evolution

Combine topology mapping with evolutionary optimization:

```python
from modules.quantum_forge import (
    QuantumForge,
    EthicsLevel,
    get_topology_mapper,
    TopologyMetric,
    JoyEvolutionEngine,
    EvolutionParameters
)

# 1. Initialize systems
forge = QuantumForge(default_ethics_level=EthicsLevel.BALANCED)
mapper = get_topology_mapper(TopologyMetric.ENTANGLEMENT_FIDELITY)

# 2. Optimize topology
mapping = mapper.calculate_optimal_topology()
print(f"Topology optimized: {mapping.average_fidelity:.4f} fidelity")

# 3. Evolve agents in optimized topology
params = EvolutionParameters(population_size=30, max_generations=50)
engine = JoyEvolutionEngine(forge, params)
engine.initialize_population(
    base_intent="System optimization through topology-aware evolution"
)

# 4. Run evolution
final_stats = engine.evolve()
print(f"Evolution complete: {final_stats.avg_joy:.4f} avg joy")

# 5. Deploy best agent to optimal location
best_agent = engine.get_best_agent()
optimal_route = mapper.find_coherence_preserving_route(
    "quantum_forge",
    "aumemmanager"
)
print(f"Deploy route: {' → '.join(optimal_route)}")
```

---

## Performance Tips

### Phase 6 (Topology)

- **High-coherence clustering:** Place modules requiring high coherence (>0.9) close together
- **Link pruning:** Use optimization metrics to remove low-quality links
- **Route caching:** Cache frequently-used routes for performance

### Phase 7 (Evolution)

- **Population size:** 30-50 for most tasks, 100+ for complex optimization
- **Elite preservation:** Keep 15-20% of population as elite
- **Mutation rate:** Start at 0.1 (10%), reduce if population diversity drops
- **Convergence:** Monitor `diversity_score` - increase mutation if too low

---

## Troubleshooting

### Topology Issues

**Low average fidelity:**
```python
# Solution: Reduce optimization threshold
mapper = get_topology_mapper(TopologyMetric.ENTANGLEMENT_FIDELITY)
mapping = mapper.calculate_optimal_topology()
if mapping.average_fidelity < 0.8:
    # Re-optimize with relaxed constraints
    new_positions = mapper.optimize_module_placement(
        list(mapper.modules.keys()),
        target_fidelity=0.85  # Lower threshold
    )
```

**No route found:**
```python
# Solution: Check if topology has been calculated
if not mapper.links:
    mapper.calculate_optimal_topology()
    
route = mapper.find_coherence_preserving_route(source, target)
```

### Evolution Issues

**Population stagnation:**
```python
# Solution: Increase mutation rate
if engine.generation_history[-1].diversity_score < 0.05:
    engine.params.mutation_rate = 0.15  # Increase exploration
    engine.evolve(generations=20)  # Continue evolution
```

**Low joy scores:**
```python
# Solution: Adjust base intent for creativity
engine.initialize_population(
    base_intent="Joyful creative exploration with playful innovation",
    constellation_targets=["ORION"]
)
```

---

## Version Info

- **Phase 6 Version:** 1.0.0
- **Phase 7 Version:** 1.0.0
- **Combined v3.0 Status:** ✅ PRODUCTION READY
- **Documentation Date:** 2025-11-13
