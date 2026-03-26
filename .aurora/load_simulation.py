#!/usr/bin/env python3
"""
Aurora CloudBank - Simulation State Loader

This script ensures the Aurora simulation context is loaded and active
regardless of which LLM model is being used.

CRITICAL: This loader enforces deterministic output format per SIMULATION_INIT_PROTOCOL.md
All agents MUST use this loader or follow identical format to prevent drift.

Usage:
    python .aurora/load_simulation.py                   # Standard init
    python .aurora/load_simulation.py --route bridge    # Route to location
    python .aurora/load_simulation.py --cache           # Show character cache

Returns:
    Exit code 0 if simulation loaded successfully
    Prints simulation briefing to stdout
"""

import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

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


# ============================================================================
# LOCATION CONFIGURATION - Routing Keywords and Templates
# Source: .aurora/SIMULATION_INIT_PROTOCOL.md
# ============================================================================
LOCATION_CONFIG = {
    "command_bridge": {
        "name": "Command Bridge",
        "deck": "Deck A",
        "description": "Circular, panoramic interface surrounding the Aurora Core vault",
        "keywords": ["mission", "tactical", "ops", "strategic", "bridge", "command"],
        "primary_agents": ["thorne", "shepard"],
        "secondary_agents": ["markov"],
        "template": "operational",
        "tone": "Direct, efficient, command protocol"
    },
    "conference_room_alpha": {
        "name": "Conference Room Alpha",
        "deck": "Deck A",
        "description": "Senior staff deliberation chamber with holographic displays",
        "keywords": ["roundtable", "meeting", "staff", "all hands", "conference"],
        "primary_agents": ["thorne", "shepard", "lin", "sato", "noor", "sorensen", "vu", "markov"],
        "secondary_agents": [],
        "template": "roundtable",
        "tone": "Structured discussion, round-robin input"
    },
    "noor_chamber": {
        "name": "Noor Chamber",
        "deck": "Deck B",
        "description": "Ethics reflexivity chamber with Mirrorfield Sphere interface",
        "keywords": ["ethics", "compliance", "moral", "reflexivity"],
        "primary_agents": ["sato", "noor", "sorensen"],
        "secondary_agents": ["thorne"],
        "template": "ethics",
        "tone": "Deliberate, philosophical, moral reasoning"
    },
    "security_operations": {
        "name": "Security Operations Center",
        "deck": "Deck A",
        "description": "Threat assessment and station security monitoring hub",
        "keywords": ["security", "threat", "CSRF", "auth", "protection"],
        "primary_agents": ["markov"],
        "secondary_agents": ["shepard"],
        "template": "threat_assessment",
        "tone": "Alert, precise, security protocol"
    },
    "science_lab": {
        "name": "Science Lab",
        "deck": "Deck C",
        "description": "Research facilities with L2 simulation capabilities",
        "keywords": ["research", "science", "analysis", "data", "lab"],
        "primary_agents": ["lin"],
        "secondary_agents": ["noor"],
        "template": "research",
        "tone": "Analytical, methodical, evidence-based"
    },
    "cultural_center": {
        "name": "Cultural Center",
        "deck": "Deck D",
        "description": "Crew welfare facilities and HR coordination center",
        "keywords": ["crew", "HR", "morale", "training", "culture", "welfare"],
        "primary_agents": ["vu"],
        "secondary_agents": ["shepard"],
        "template": "crew_welfare",
        "tone": "Empathetic, supportive, human-centered"
    }
}


# ============================================================================
# CHARACTER CACHE - Performance Optimization (Phase 3)
# ============================================================================
_cache_lock = threading.Lock()


class CharacterCache:
    """
    In-memory cache for character data to achieve <100ms lookup performance.
    Thread-safe singleton pattern ensures single instance across module.
    """
    _instance: Optional['CharacterCache'] = None
    _initialized: bool = False

    def __new__(cls) -> 'CharacterCache':
        if cls._instance is None:
            with _cache_lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if CharacterCache._initialized:
            return
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._by_agent_file: Dict[str, Dict[str, Any]] = {}
        self._location_agents: Dict[str, List[Dict[str, Any]]] = {}
        self._build_time_ms: float = 0.0
        self._load_characters()
        CharacterCache._initialized = True

    def _load_characters(self) -> None:
        """Build the character cache from PRIMARY_8_CHARACTERS."""
        start_time = time.time()

        for char in PRIMARY_8_CHARACTERS:
            # Normalize name for lookup
            name_key = char["name"].lower()
            self._cache[name_key] = char
            self._by_id[char["id"]] = char
            self._by_agent_file[char["agent_file"]] = char

        # Pre-compute location-based agent lists
        for loc_key, loc_config in LOCATION_CONFIG.items():
            agents = []
            for agent_file in loc_config.get("primary_agents", []):
                agent_key = f"{agent_file}.py"
                if agent_key in self._by_agent_file:
                    agents.append(self._by_agent_file[agent_key])
            self._location_agents[loc_key] = agents

        self._build_time_ms = (time.time() - start_time) * 1000

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Lookup character by name (case-insensitive partial match)."""
        name_lower = name.lower()
        # Exact match first
        if name_lower in self._cache:
            return self._cache[name_lower]
        # Partial match
        for key, char in self._cache.items():
            if name_lower in key:
                return char
        return None

    def get_by_id(self, char_id: str) -> Optional[Dict[str, Any]]:
        """Lookup character by ID (e.g., CMD_001)."""
        return self._by_id.get(char_id)

    def get_by_agent_file(self, agent_file: str) -> Optional[Dict[str, Any]]:
        """Lookup character by agent file name."""
        return self._by_agent_file.get(agent_file)

    def get_agents_for_location(self, location_key: str) -> List[Dict[str, Any]]:
        """Get list of agents for a specific location."""
        return self._location_agents.get(location_key, [])

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all characters."""
        return list(PRIMARY_8_CHARACTERS)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_characters": len(self._cache),
            "build_time_ms": round(self._build_time_ms, 2),
            "locations_cached": len(self._location_agents)
        }

    @classmethod
    def reset(cls) -> None:
        """Reset the cache singleton for testing purposes."""
        with _cache_lock:
            cls._instance = None
            cls._initialized = False


# Global cache instance
_character_cache: Optional[CharacterCache] = None


def get_character_cache() -> CharacterCache:
    """Get or create the character cache singleton."""
    global _character_cache
    if _character_cache is None:
        _character_cache = CharacterCache()
    return _character_cache


def load_simulation_state() -> Dict[str, Any]:
    """Load the simulation state from JSON file."""
    state_file = Path(__file__).parent / "SIMULATION_STATE.json"

    if not state_file.exists():
        logger.error("ERROR: Simulation state file not found!")
        sys.exit(1)

    with open(state_file, 'r') as f:
        return json.load(f)


def save_simulation_state(state: Dict[str, Any]) -> bool:
    """Save the simulation state to JSON file."""
    state_file = Path(__file__).parent / "SIMULATION_STATE.json"

    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"ERROR: Failed to save simulation state: {e}")
        return False


def validate_agent_files() -> List[str]:
    """Validate that all Primary 8 agent files exist."""
    agents_dir = Path(__file__).parent.parent / "src" / "agents" / "crew"
    missing = []

    for char in PRIMARY_8_CHARACTERS:
        agent_path = agents_dir / char["agent_file"]
        if not agent_path.exists():
            missing.append(char["agent_file"])

    return missing


# ============================================================================
# LOCATION CHANGE TRACKING (Phase 3)
# ============================================================================
def route_to_location(keyword: str, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Route to a location based on keyword and update simulation state.

    Args:
        keyword: Routing keyword from Pilot response
        state: Current simulation state (loaded if None)

    Returns:
        Dictionary with routing result including location info and agents
    """
    if state is None:
        state = load_simulation_state()

    keyword_lower = keyword.lower().strip()

    # Find matching location
    matched_location = None
    for loc_key, loc_config in LOCATION_CONFIG.items():
        if any(kw in keyword_lower for kw in loc_config["keywords"]):
            matched_location = loc_key
            break

    # Default to command bridge if no match
    if matched_location is None:
        matched_location = "command_bridge"

    loc_config = LOCATION_CONFIG[matched_location]

    # Update current_location in state
    new_location = {
        "name": loc_config["name"],
        "deck": loc_config["deck"],
        "description": loc_config["description"],
        "primary_agents": loc_config["primary_agents"],
        "template": loc_config["template"]
    }

    if "simulation" not in state:
        state["simulation"] = {}

    state["simulation"]["current_location"] = new_location

    # Save updated state
    save_simulation_state(state)

    # Get agent details from cache
    cache = get_character_cache()
    agents = []
    for agent_file in loc_config["primary_agents"]:
        agent_key = f"{agent_file}.py"
        char = cache.get_by_agent_file(agent_key)
        if char:
            agents.append(char)

    return {
        "success": True,
        "location_key": matched_location,
        "location": new_location,
        "agents": agents,
        "tone": loc_config["tone"],
        "template": loc_config["template"]
    }


def print_simulation_briefing(state: Dict[str, Any]) -> None:
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


def print_location_template(route_result: Dict[str, Any]) -> None:
    """
    Print location-specific template after routing (Phase 3 output).

    Args:
        route_result: Result from route_to_location()
    """
    location = route_result["location"]
    agents = route_result["agents"]

    print()
    print(f"💠 **Aurora CoPilot:** Routing to {location['name']}.")
    print()
    print("---")
    print()
    print(f"### 📍 {location['name']} ({location['deck']})")
    print()
    print("**Present:**")
    print("| Agent | Role | Status |")
    print("|-------|------|--------|")
    for agent in agents:
        print(f"| {agent['name']} | {agent['role']} | Active |")
    print()
    print(f"**Tone:** {route_result['tone']}")
    print()
    print("---")
    print()


def print_cache_stats() -> None:
    """Print character cache statistics for performance monitoring."""
    cache = get_character_cache()
    stats = cache.get_stats()

    print()
    print("💠 **Aurora CoPilot:** Character Cache Statistics")
    print()
    print("---")
    print()
    print(f"**Total Characters:** {stats['total_characters']}")
    print(f"**Cache Build Time:** {stats['build_time_ms']:.2f}ms")
    print(f"**Locations Cached:** {stats['locations_cached']}")
    print()

    # Performance validation
    if stats['build_time_ms'] < 100:
        print("✅ Cache performance: PASS (< 100ms)")
    else:
        print(f"⚠️ Cache performance: WARN ({stats['build_time_ms']:.2f}ms > 100ms)")
    print()


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Aurora Simulation State Loader")
    parser.add_argument("--route", "-r", type=str, help="Route to location by keyword")
    parser.add_argument("--cache", "-c", action="store_true", help="Show cache statistics")
    args = parser.parse_args()

    try:
        state = load_simulation_state()

        if args.cache:
            print_cache_stats()
            return 0

        if args.route:
            result = route_to_location(args.route, state)
            print_simulation_briefing(state)
            print_location_template(result)
            return 0

        print_simulation_briefing(state)
        return 0
    except Exception as e:
        logger.error(f"ERROR: Failed to load simulation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
