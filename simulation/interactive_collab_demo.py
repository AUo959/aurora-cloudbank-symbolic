#!/usr/bin/env python3
"""Interactive visualization of the canonical Orion Phase-1 benchmark.

This demo exercises ``OrionSimulationV2``. It is a benchmark/demo surface, not
the live L1 INIT/runtime path.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

SIMULATION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SIMULATION_DIR))

from orion_station_simulation_v2 import OrionSimulationV2  # noqa: E402


def print_header() -> None:
    print("\n" + "=" * 70)
    print("🌌 ORION STATION — PHASE-1 COLLABORATION BENCHMARK v2")
    print("=" * 70)
    print("Deterministic institutional/task benchmark; not the live L1 world runtime")
    print()


def print_crew_status(agents) -> None:
    print("\n👥 CREW STATUS:")
    for name, agent in agents.items():
        status = "🔴 BUSY" if agent.assigned_task else "🟢 IDLE"
        task = agent.assigned_task or "Awaiting assignment"
        fatigue_bar = "█" * int(agent.fatigue / 10) + "░" * (10 - int(agent.fatigue / 10))
        print(f"   {name:24} {status} | Task: {task:10} | Energy: [{fatigue_bar}]")


def print_tick_header(tick, events) -> None:
    print(f"\n{'━' * 70}")
    print(f"⏱️  CYCLE {tick:02d}")
    if events:
        for event in events:
            icon = {
                "swarm_sync": "🤝",
                "collaboration_boost": "⚡",
                "insight_pulse": "💡",
                "cross_pollination": "🔄",
            }.get(event.kind, "✨")
            print(f"   {icon} {event.description} (+{int((event.multiplier - 1) * 100)}%)")
    else:
        print("   routine cycle — no emergent event")
    print("━" * 70)


def interactive_simulation(seed: int = 42, ticks: int = 10, delay: float = 1.5) -> None:
    print_header()
    sim = OrionSimulationV2(seed=seed, enable_emergent=True)

    print("\n📋 HISTORICAL PHASE-1 BENCHMARK TASKS:")
    for task_id, task in sim.tasks.items():
        deps = f" (depends: {', '.join(task.depends_on)})" if task.depends_on else ""
        print(f"   {task_id}: {task.name} ({task.est_hours}h){deps}")

    print_crew_status(sim.agents)
    input("\n▶️  Press ENTER to begin benchmark...")

    for _ in range(ticks):
        if all(task.completed for task in sim.tasks.values()):
            break

        tick = sim.ticks
        event_start = len(sim.aurora.events)
        sim.tick()
        events = sim.aurora.events[event_start:]

        print_tick_header(tick, events)
        print("\n📊 ACTIVE ASSIGNMENTS:")
        active_agents = [agent for agent in sim.agents.values() if agent.assigned_task]
        if not active_agents:
            print("   none")
        for agent in active_agents:
            task = sim.tasks.get(agent.assigned_task)
            if task:
                print(f"   {agent.name} → {task.name} ({task.remaining:.1f}h remaining)")

        print("\n📈 TASK STATUS:")
        for task in sim.tasks.values():
            status = "✅ COMPLETE" if task.completed else f"🔄 {task.remaining:.1f}h left"
            bar_filled = int((1 - task.remaining / task.est_hours) * 20) if task.est_hours > 0 else 20
            bar = "█" * bar_filled + "░" * (20 - bar_filled)
            print(f"   {task.id}: [{bar}] {status}")

        time.sleep(delay)

    result = sim.run(max_ticks=0)

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
    print(f"\n📊 Cycles elapsed: {result['ticks']}")
    print(f"✅ Tasks completed: {len(result['completed_ids'])}/{len(sim.tasks)}")
    print(f"✨ Emergent events: {result['emergent_events']}")

    print("\n👥 FINAL CREW STATUS:")
    print_crew_status(sim.agents)

    print("\n💬 TRANSCRIPT HIGHLIGHTS:")
    for message in sim.transcript[-8:]:
        print(f"   {message}")

    print("\nLive L1 INIT remains: python .aurora/init_l1.py preflight / init")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Orion Phase-1 benchmark v2")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--ticks", type=int, default=10, help="Max cycles")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between cycles (seconds)")
    parser.add_argument("--fast", action="store_true", help="Run without visible delays")
    args = parser.parse_args()

    delay = 0.1 if args.fast else args.delay
    try:
        interactive_simulation(seed=args.seed, ticks=args.ticks, delay=delay)
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        raise SystemExit(0)
