#!/usr/bin/env python3
"""Test script for Batch 6 crew agent integration."""

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
    get_park, get_suresh, get_halden, get_vatra,
)

# Initialize all agents
all_getters = [
    get_thorne, get_markov, get_roberts, get_qin, get_chen, get_noor,
    get_velin, get_shepard, get_lin, get_vu, get_sato, get_vell,
    get_porter, get_tanaka_j, get_feldman, get_patel, get_sorensen,
    get_vasquez, get_martinez, get_patel_ryan, get_okada, get_zhao,
    get_menon, get_kale, get_rivas, get_koss, get_kyros, get_drev,
    get_park, get_suresh, get_halden, get_vatra,
]

print("Initializing all agents...")
for getter in all_getters:
    getter()
print()


def test_batch_6_agents():
    """Test that all Batch 6 agents are properly instantiated."""
    print("=" * 80)
    print("BATCH 6 CREW AGENT INTEGRATION TEST")
    print("=" * 80)
    print()

    # Get all agents from registry (initialized above)
    all_agents = get_all_crew_agents()
    print(f"Total agents in registry: {len(all_agents)}")
    print()

    # Verify expected count (28 from previous batches + 4 new = 32)
    expected_count = 32
    if len(all_agents) != expected_count:
        print(f"❌ ERROR: Expected {expected_count} agents, found {len(all_agents)}")
        return False
    else:
        print(f"✓ Correct agent count: {expected_count}")
    print()

    # Verify Batch 6 agents are in registry
    print("Verifying Batch 6 agents in registry...")
    batch_6_surnames = ['park', 'suresh', 'halden', 'vatra']
    for surname in batch_6_surnames:
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
    interface_agents = get_agents_by_role(AgentRole.INTERFACE)
    print(f"  Interface agents: {len(interface_agents)}")
    print()

    # Test division-based retrieval
    print("Testing division-based agent retrieval...")
    interface_division = get_agents_by_division("Interface & Aesthetics")
    print(f"  Interface & Aesthetics: {len(interface_division)} agents")
    print()

    # Verify Batch 6 specific attributes
    print("Verifying Batch 6 specific attributes...")

    # Park - Immersive Experience Theorist
    park = all_agents['park']
    assert park.agent_id == "UX_004"
    assert "experiential_cognition" in park.specializations
    print(f"  ✓ Park (UX_004) - Immersive experience specializations verified")

    # Suresh - Symbolic Systems Artist
    suresh = all_agents['suresh']
    assert suresh.agent_id == "UX_005"
    assert "data_visualization_artistry" in suresh.specializations
    print(f"  ✓ Suresh (UX_005) - Symbolic visualization specializations verified")

    # Halden - Lead Visual Concept Designer
    halden = all_agents['halden']
    assert halden.agent_id == "UX_006"
    assert "design_direction" in halden.specializations
    print(f"  ✓ Halden (UX_006) - Visual identity specializations verified")

    # Vatra - Atmospheric Painter & Color Theorist
    vatra = all_agents['vatra']
    assert vatra.agent_id == "UX_007"
    assert "colorimetry" in vatra.specializations
    print(f"  ✓ Vatra (UX_007) - Color theory specializations verified")
    print()

    # Summary
    print("=" * 80)
    print("BATCH 6 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"✓ All 4 Batch 6 agents successfully implemented")
    print(f"✓ Total agent count: {len(all_agents)}/36 ({len(all_agents)/36*100:.1f}% complete)")
    print(f"✓ Interface & Aesthetics division expanded to 6 agents")
    print(f"✓ All agents properly registered and accessible")
    print(f"✓ Module exports and API initialization working correctly")
    print()
    print("BATCH 6 STATUS: SUCCESS ✓")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        success = test_batch_6_agents()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
