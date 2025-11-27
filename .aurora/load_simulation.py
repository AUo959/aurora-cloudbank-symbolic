#!/usr/bin/env python3
"""
Aurora CloudBank - Simulation State Loader

This script ensures the Aurora simulation context is loaded and active
regardless of which LLM model is being used.

CRITICAL: This loader enforces deterministic output format per SIMULATION_INIT_PROTOCOL.md
All agents MUST use this loader or follow identical format to prevent drift.

Usage:
    python .aurora/load_simulation.py

Returns:
    Exit code 0 if simulation loaded successfully
    Prints simulation briefing to stdout
"""

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# CANONICAL CHARACTER DATA - PRIMARY 8 CORE COMMAND STAFF
# Source: .github/copilot-instructions.md (canonical authority)
# ============================================================================
PRIMARY_8_CHARACTERS = [
    {
        "name": "Commander Alex Thorne",
        "role": "Station Commander",
        "id": "CMD_001",
        "gender": "Male (he/him)",
        "agent_file": "thorne.py"
    },
    {
        "name": "Lt. Commander Maya Shepard",
        "role": "Executive Officer",
        "id": "CMD_002",
        "gender": "Female (she/her)",
        "agent_file": "shepard.py"
    },
    {
        "name": "Varya Lin",
        "role": "Chief Science Officer",
        "id": "CSO_001",
        "gender": "Female (she/her)",
        "agent_file": "lin.py"
    },
    {
        "name": "Dr. Amira Sato",
        "role": "Chief Ethics Officer",
        "id": "CEO_001",
        "gender": "Female (she/her)",
        "agent_file": "sato.py"
    },
    {
        "name": "Dr. Elira Noor",
        "role": "Lead Reflexivity Specialist",
        "id": "ETH_002",
        "gender": "Female (she/her)",
        "agent_file": "noor.py"
    },
    {
        "name": "Prof. Elena Sorensen",
        "role": "Cognitive Ethicist",
        "id": "ETH_003",
        "gender": "Female (she/her)",
        "agent_file": "sorensen.py"
    },
    {
        "name": "Helena Vu",
        "role": "Cultural & HR Director",
        "id": "HR_001",
        "gender": "Female (she/her)",
        "agent_file": "vu.py"
    },
    {
        "name": "Julian Markov",
        "role": "Chief Security Officer",
        "id": "CSO_002",
        "gender": "Male (he/him)",
        "agent_file": "markov.py"
    },
]


def load_simulation_state():
    """Load the simulation state from JSON file."""
    state_file = Path(__file__).parent / "SIMULATION_STATE.json"

    if not state_file.exists():
        logger.error("ERROR: Simulation state file not found!")
        sys.exit(1)

    with open(state_file, 'r') as f:
        return json.load(f)


def validate_agent_files():
    """Validate that all Primary 8 agent files exist."""
    agents_dir = Path(__file__).parent.parent / "src" / "agents" / "crew"
    missing = []

    for char in PRIMARY_8_CHARACTERS:
        agent_path = agents_dir / char["agent_file"]
        if not agent_path.exists():
            missing.append(char["agent_file"])

    return missing


def print_simulation_briefing(state):
    """
    Print contextual rehydration followed by Aurora inquiry.

    CRITICAL: This format is canonical per SIMULATION_INIT_PROTOCOL.md v1.1.0
    Phase 1: Contextual Rehydration
    Phase 2: Aurora Inquiry
    Phase 3: Automatic Routing (handled by agent based on user response)
    """
    # Extract state data
    simulation = state.get('simulation', {})
    station = state.get('station_infrastructure', {})
    quantum_cycle = state.get('quantum_cycle', {}).get('current_cycle', 'N/A')
    operational_status = simulation.get('status', 'UNKNOWN')
    mission_phase = state.get('mission_state', {}).get('current_phase', 'N/A')

    # Current location
    current_location = simulation.get('current_location', {})
    location_name = current_location.get('name', 'Command Bridge')
    location_deck = current_location.get('deck', 'Deck A')

    # Crew counts
    crew_current = station.get('current_crew', 36)
    l2_relays = 6
    l3_frameworks = 6

    # ========================================================================
    # PHASE 1: CONTEXTUAL REHYDRATION
    # ========================================================================
    print()
    print("💠 **Aurora CoPilot:** Contextual rehydration complete.")
    print()
    print("---")
    print()
    print("**Station:** Orion Station (L4 Lagrange Point)")
    print(f"**Status:** {operational_status}")
    print(f"**Quantum Cycle:** {quantum_cycle}")
    print(f"**Current Phase:** {mission_phase}")
    print(f"**Location:** {location_name} ({location_deck})")
    print()
    print("**Framework:**")
    print("- **Pilot:** User — Directs simulation")
    print("- **CoPilot:** Aurora (Au) — Facilitates coordination")
    print(f"- **Agents:** Autonomous distributed intelligence "
          f"({crew_current} human + {l2_relays} L2 + {l3_frameworks} L3)")
    print()
    print("---")
    print()

    # ========================================================================
    # PHASE 2: AURORA INQUIRY
    # ========================================================================
    print("💠 Link with Orion Station established, Pilot. What are we doing today?")
    print()


def main():
    """Main entry point."""
    try:
        state = load_simulation_state()
        print_simulation_briefing(state)
        return 0
    except Exception as e:
        logger.error(f"ERROR: Failed to load simulation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
