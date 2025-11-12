#!/usr/bin/env python3
"""
Aurora CloudBank - Simulation State Loader

This script ensures the Aurora simulation context is loaded and active
regardless of which LLM model is being used.

Usage:
    python .aurora/load_simulation.py
    
Returns:
    Exit code 0 if simulation loaded successfully
    Prints simulation briefing to stdout
"""

import logging

logger = logging.getLogger(__name__)

import json
import sys
from pathlib import Path


def load_simulation_state():
    """Load the simulation state from JSON file."""
    state_file = Path(__file__).parent / "SIMULATION_STATE.json"
    
    if not state_file.exists():
        logger.error("ERROR: Simulation state file not found!")
        sys.exit(1)
    
    with open(state_file, 'r') as f:
        return json.load(f)


def print_simulation_briefing(state):
    """Print formatted simulation briefing."""
    sim = state['simulation']
    roles = state['roles']
    mission = state['mission_state']
    system = state['system_status']
    
    print("=" * 80)
    print("⚡ AURORA CLOUDBANK - ORION STATION OPERATIONS CENTER")
    print("=" * 80)
    print()
    print(f"📡 SIMULATION STATUS: {sim['status']}")
    print(f"📅 Last Updated: {sim['last_updated']}")
    print(f"🔢 Version: {sim['version']}")
    print()
    print("👥 ACTIVE PERSONNEL:")
    for role_name, role_data in roles.items():
        if role_data['active']:
            status = "🟢 ACTIVE"
            print(f"   {status} - {role_data['rank']} {role_data['name']} ({role_data['callsign']})")
    print()
    print("🎯 MISSION STATUS:")
    print(f"   Phase: {mission['current_phase']}")
    print(f"   Completed Missions: {mission['total_missions_completed']}")
    print(f"   Average Efficiency: {mission['average_efficiency']}%")
    print(f"   Current Mission: {mission['active_mission'] or 'NONE (Awaiting Orders)'}")
    print()
    print("📊 SYSTEM STATUS:")
    print(f"   🛡️  CSRF Coverage: {system['csrf_coverage']}%")
    print(f"   ✅ Input Validation: {system['input_validation_coverage']}%")
    print(f"   📝 Logging Coverage: {system['logging_coverage']}%")
    print(f"   📚 Documentation: {system['documentation_status']}")
    print(f"   🔄 Repository: {system['repository_state']}")
    print()
    print("🎖️  RECENT MISSIONS:")
    for mission_record in mission['completed_missions'][-3:]:
        print(f"   ✅ {mission_record['id']}: {mission_record['name']}")
        print(f"      Efficiency: {mission_record['efficiency']}% | Commit: {mission_record['commit']}")
    print()
    
    # Known issues
    if state['known_issues']:
        logger.warning("KNOWN ISSUES:")
        for issue in state['known_issues']:
            severity_icon = "🔴" if issue['severity'] == "HIGH" else "🟡" if issue['severity'] == "MEDIUM" else "🟢"
            print(f"   {severity_icon} {issue['id']}: {issue['description']}")
            print(f"      Status: {issue['status']} | Impact: {issue['impact']}")
        print()
    
    # Next mission candidates
    if state['next_mission_candidates']:
        print("🚀 NEXT MISSION CANDIDATES:")
        for candidate in state['next_mission_candidates']:
            priority = candidate['priority']
            priority_icon = "🔴" if priority == "HIGH" else "🟡" if priority == "MEDIUM" else "🟢"
            print(f"   {priority_icon} {candidate['id']}: {candidate['name']}")
            print(f"      Priority: {candidate['priority']} | Est. Time: {candidate['estimated_time']}")
        print()
    
    print("=" * 80)
    logger.info("SIMULATION CONTEXT LOADED - ORION STATION OPERATIONAL")
    print("=" * 80)
    print()
    print("🎖️  AWAITING ORDERS FROM COMMANDER THORNE...")
    print()


def main():
    """Main entry point."""
    try:
        state = load_simulation_state()
        print_simulation_briefing(state)
        return 0
    except Exception as e:
        logger.error("ERROR: Failed to load simulation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
