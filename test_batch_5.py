#!/usr/bin/env python3
"""Test script for Batch 5 crew agent integration."""

import sys
from collections import Counter

# Import all crew agent getter functions to initialize them
from src.agents.crew import (
    get_all_crew_agents,
    get_agents_by_role,
    get_agents_by_division,
    AgentRole,
    # All agent getters
    get_thorne, get_markov, get_roberts, get_qin, get_chen, get_noor,
    get_velin, get_shepard, get_lin, get_vu, get_sato, get_vell,
    get_porter, get_tanaka_j, get_feldman, get_patel, get_sorensen,
    get_vasquez, get_martinez, get_patel_ryan, get_okada, get_zhao,
    get_menon, get_kale, get_rivas, get_koss, get_kyros, get_drev,
)

# Initialize all agents
all_getters = [
    get_thorne, get_markov, get_roberts, get_qin, get_chen, get_noor,
    get_velin, get_shepard, get_lin, get_vu, get_sato, get_vell,
    get_porter, get_tanaka_j, get_feldman, get_patel, get_sorensen,
    get_vasquez, get_martinez, get_patel_ryan, get_okada, get_zhao,
    get_menon, get_kale, get_rivas, get_koss, get_kyros, get_drev,
]

print("Initializing all agents...")
for getter in all_getters:
    getter()
print()


def test_batch_5_agents():
    """Test that all Batch 5 agents are properly instantiated."""
    print("=" * 80)
    print("BATCH 5 CREW AGENT INTEGRATION TEST")
    print("=" * 80)
    print()

    # Get all agents from registry (initialized by API import)
    all_agents = get_all_crew_agents()
    print(f"Total agents in registry: {len(all_agents)}")
    print()

    # Verify expected count (23 from previous batches + 5 new = 28)
    expected_count = 28
    if len(all_agents) != expected_count:
        print(f"❌ ERROR: Expected {expected_count} agents, found {len(all_agents)}")
        return False
    else:
        print(f"✓ Correct agent count: {expected_count}")
    print()

    # Verify Batch 5 agents are in registry
    print("Verifying Batch 5 agents in registry...")
    batch_5_surnames = ['kale', 'rivas', 'koss', 'kyros', 'drev']
    for surname in batch_5_surnames:
        if surname in all_agents:
            agent = all_agents[surname]
            print(f"  ✓ {surname}: {agent.full_name} ({agent.agent_id})")
            print(f"    Role: {agent.role.value}, Division: {agent.division}")
            print(f"    Location: {agent.location}")
        else:
            print(f"  ❌ {surname}: NOT FOUND")
            return False
    print()

    # Analyze role distribution
    print("Role distribution:")
    role_counts = Counter()
    for agent in all_agents.values():
        role_counts[agent.role.value] += 1

    for role, count in sorted(role_counts.items()):
        percentage = (count / len(all_agents)) * 100
        print(f"  {role}: {count} agents ({percentage:.1f}%)")
    print()

    # Analyze division distribution
    print("Division distribution:")
    division_counts = Counter()
    for agent in all_agents.values():
        division_counts[agent.division] += 1

    for division, count in sorted(division_counts.items()):
        percentage = (count / len(all_agents)) * 100
        print(f"  {division}: {count} agents ({percentage:.1f}%)")
    print()

    # Analyze clearance distribution
    print("Clearance distribution:")
    clearance_counts = Counter()
    for agent in all_agents.values():
        clearance_counts[agent.clearance.value] += 1

    for clearance, count in sorted(clearance_counts.items()):
        percentage = (count / len(all_agents)) * 100
        print(f"  {clearance}: {count} agents ({percentage:.1f}%)")
    print()

    # Test role-based retrieval
    print("Testing role-based agent retrieval...")
    systems_agents = get_agents_by_role(AgentRole.SYSTEMS)
    simulation_agents = get_agents_by_role(AgentRole.SIMULATION)
    interface_agents = get_agents_by_role(AgentRole.INTERFACE)

    print(f"  Systems agents: {len(systems_agents)}")
    print(f"  Simulation agents: {len(simulation_agents)}")
    print(f"  Interface agents: {len(interface_agents)}")
    print()

    # Test division-based retrieval
    print("Testing division-based agent retrieval...")
    systems_division = get_agents_by_division("Systems & Infrastructure")
    simulation_division = get_agents_by_division("Simulation & Cognitive Systems")
    interface_division = get_agents_by_division("Interface & Aesthetics")

    print(f"  Systems & Infrastructure: {len(systems_division)} agents")
    print(f"  Simulation & Cognitive Systems: {len(simulation_division)} agents")
    print(f"  Interface & Aesthetics: {len(interface_division)} agents")
    print()

    # Verify Batch 5 specific attributes
    print("Verifying Batch 5 specific attributes...")

    # Kale - Layer Isolation Theorist
    kale = all_agents['kale']
    assert kale.agent_id == "SYS_007"
    assert "layer_segmentation" in kale.specializations
    print(f"  ✓ Kale (SYS_007) - Layer Isolation specializations verified")

    # Rivas - Simulation Binding Specialist
    rivas = all_agents['rivas']
    assert rivas.agent_id == "SIM_004"
    assert "temporal_coupling" in rivas.specializations
    print(f"  ✓ Rivas (SIM_004) - Temporal coupling specializations verified")

    # Koss - Cognitive Drift Mapper
    koss = all_agents['koss']
    assert koss.agent_id == "SIM_005"
    assert "drift_nullification" in koss.specializations
    print(f"  ✓ Koss (SIM_005) - Drift detection specializations verified")

    # Kyros - UX Architect
    kyros = all_agents['kyros']
    assert kyros.agent_id == "UX_001"
    assert "cognitive_ergonomics" in kyros.specializations
    print(f"  ✓ Kyros (UX_001) - UX specializations verified")

    # Drev - Interface Ecologist
    drev = all_agents['drev']
    assert drev.agent_id == "UX_003"
    assert "bio_adaptive_design" in drev.specializations
    print(f"  ✓ Drev (UX_003) - Bio-adaptive specializations verified")
    print()

    # Summary
    print("=" * 80)
    print("BATCH 5 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"✓ All 5 Batch 5 agents successfully implemented")
    print(f"✓ Total agent count: {len(all_agents)}/36 ({len(all_agents)/36*100:.1f}% complete)")
    print(f"✓ New divisions added: Interface & Aesthetics")
    print(f"✓ All agents properly registered and accessible")
    print(f"✓ Module exports and API initialization working correctly")
    print()
    print("BATCH 5 STATUS: SUCCESS ✓")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        success = test_batch_5_agents()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
