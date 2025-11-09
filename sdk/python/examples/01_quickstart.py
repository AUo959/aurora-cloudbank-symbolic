"""Quickstart example for Aurora SDK.

This example demonstrates the basics of using the Aurora SDK:
1. Initialize the client
2. Run a quantum scenario
3. Work with memories
"""

import asyncio
import os

from aurora_sdk import AuroraClient


async def main():
    """Run quickstart example."""
    # Set API key (get yours at https://dashboard.aurora.dev)
    os.environ["AURORA_API_KEY"] = "sk_test_..."  # Replace with your actual key

    # Initialize client
    async with AuroraClient() as client:
        print("🚀 Aurora SDK Quickstart\n")

        # 1. Run quantum supply chain optimization
        print("1. Running quantum supply chain optimization...")
        result = await client.quantum.run_scenario(
            "supply_chain_optimization",
            num_suppliers=5,
            demand_variance=0.2,
            cost_weights=[0.3, 0.4, 0.2, 0.5, 0.3]
        )

        print(f"   ✓ Scenario ID: {result.scenario_id}")
        print(f"   ✓ Optimal configuration: {result.optimal_state}")
        print(f"   ✓ Cost reduction: {result.metrics.get('cost_reduction', 0):.1f}%")
        print(f"   ✓ Execution time: {result.execution_time:.2f}s\n")

        # 2. Create a memory
        print("2. Creating memory...")
        memory = await client.memory.create(
            content="Quantum supply chain results from quickstart",
            tier="active",
            tags=["quickstart", "supply-chain", "results"]
        )

        print(f"   ✓ Memory ID: {memory.memory_id}")
        print(f"   ✓ Tier: {memory.tier}")
        print(f"   ✓ Tags: {', '.join(memory.tags)}\n")

        # 3. Search memories
        print("3. Searching memories...")
        results = await client.memory.search(
            query="supply chain",
            top_k=5
        )

        print(f"   ✓ Found {len(results)} memories:")
        for mem in results[:3]:
            print(f"     • {mem.content[:50]}... (score: {mem.attention_score:.2f})")

        # 4. Get memory statistics
        print("\n4. Memory statistics...")
        stats = await client.memory.get_stats()
        print(f"   ✓ Total memories: {stats.total_memories}")
        print(f"   ✓ Active: {stats.active_count}")
        print(f"   ✓ Compressed: {stats.compressed_count}")
        print(f"   ✓ Archived: {stats.archived_count}")

    print("\n✅ Quickstart complete!")


if __name__ == "__main__":
    asyncio.run(main())
