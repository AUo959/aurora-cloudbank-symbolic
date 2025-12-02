import { PlaygroundExample } from '@/types/playground';

export const playgroundExamples: PlaygroundExample[] = [
  {
    id: 'quantum/supply_chain',
    title: 'Quantum Supply Chain (T1)',
    description: 'Optimize resilient supply chains with Aurora quantum solvers.',
    language: 'python',
    tags: ['quantum', 'optimization', 'resilience'],
    code: `from aurora_sdk import AuroraClient  # T1:quantum-supply-anchor

client = AuroraClient()

# T1:scenario-seed supply_chain_optimization
result = await client.quantum.run_scenario(
    scenario="supply_chain_optimization",
    num_suppliers=5,
    demand_variance=0.2,
    cost_weights=[0.3, 0.4, 0.2, 0.5, 0.3]
)

print(f"Optimal configuration: {result.optimal_state}")
print(f"Cost reduction: {result.metrics['cost_reduction']:.1f}%")
print(f"Reliability score: {result.metrics['reliability']:.2f}")`,
  },
  {
    id: 'decision/oracle',
    title: 'Decision Oracle Ranking',
    description: 'Multi-criteria decision analysis with Monte Carlo sampling.',
    language: 'python',
    tags: ['decision', 'monte-carlo', 'analysis'],
    code: `from aurora_sdk import AuroraClient  # T1:decision-anchor

client = AuroraClient()

# T1:oracle Monte Carlo decision weights
result = await client.decision.oracle(
    options=[
        "Deploy to Cloud Provider A",
        "Deploy to Cloud Provider B",
        "Deploy to On-Premise"
    ],
    criteria={
        "cost": 0.4,
        "performance": 0.3,
        "security": 0.2,
        "reliability": 0.1
    },
    monte_carlo_samples=10000
)

for idx, option in enumerate(result.ranked_options, 1):
    print(f"{idx}. {option['name']}")
    print(f"   Confidence: {option['confidence']:.1%}")`,
  },
  {
    id: 'memory/search',
    title: 'Semantic Memory Search',
    description: 'Search Aurora memories with semantic understanding.',
    language: 'python',
    tags: ['memory', 'semantic', 'retrieval'],
    code: `from aurora_sdk import AuroraClient  # T1:memory-anchor

client = AuroraClient()

# T1:memory-ingest anchor for semantic search
await client.memory.create(
    "Quantum algorithms for optimization",
    tier="active",
    tags=["quantum", "algorithms"]
)

await client.memory.create(
    "Supply chain best practices",
    tier="active",
    tags=["supply-chain", "business"]
)

results = await client.memory.search(
    query="optimization techniques",
    top_k=5
)

for memory in results:
    print(f"• {memory.content}")
    print(f"  Score: {memory.attention_score:.2f}")
    print(f"  Tags: {', '.join(memory.tags)}")`,
  },
];

export const defaultPlaygroundCode = playgroundExamples[0]?.code ?? '# Aurora playground ready';
