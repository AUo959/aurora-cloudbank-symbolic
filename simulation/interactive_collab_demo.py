#!/usr/bin/env python3
"""
Interactive Collaborative Simulation Demo
Real-time visualization of Orion Station crew dynamics
"""
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation.orion_station_simulation import OrionSimulation


def print_header():
    print("\n" + "="*70)
    print("🌌 ORION STATION - INTERACTIVE COLLABORATION SIMULATION")
    print("="*70)
    print("Simulating professional development environment with emergent dynamics")
    print()


def print_crew_status(agents):
    print("\n👥 CREW STATUS:")
    for name, agent in agents.items():
        status = "🔴 BUSY" if agent.assigned_task else "🟢 IDLE"
        task = agent.assigned_task or "Awaiting assignment"
        fatigue_bar = "█" * int(agent.fatigue / 10) + "░" * (10 - int(agent.fatigue / 10))
        print(f"   {name:15} {status} | Task: {task:25} | Energy: [{fatigue_bar}]")


def print_tick_header(tick, events):
    print(f"\n{'━'*70}")
    print(f"⏱️  CYCLE {tick:02d}")
    if events:
        for event in events:
            icon = {"swarm_sync": "🤝", "insight_pulse": "💡", "cross_pollination": "🔄"}.get(event.kind, "✨")
            print(f"   {icon} {event.description} (+{int((event.multiplier-1)*100)}%)")
    print(f"{'━'*70}")


def interactive_simulation(seed=42, ticks=10, delay=1.5):
    """Run simulation with real-time visual updates"""
    print_header()
    
    sim = OrionSimulation(seed=seed, enable_emergent=True)
    
    print("\n📋 PHASE 1 CRITICAL TASKS:")
    for task_id, task in sim.tasks.items():
        deps = f" (depends: {', '.join(task.depends_on)})" if task.depends_on else ""
        print(f"   {task_id}: {task.name} ({task.est_hours}h){deps}")
    
    print_crew_status(sim.agents)
    input("\n▶️  Press ENTER to begin simulation...")
    
    for _ in range(ticks):
        if all(t.completed for t in sim.tasks.values()):
            break
        
        # Capture tick state
        tick = sim.ticks
        events, multiplier = sim._emit_and_multiply(tick)
        
        # Display tick header
        print_tick_header(tick, events)
        
        # Show assignments
        sim._coordinate_assignments()
        
        print("\n📊 WORK ASSIGNMENTS:")
        active_agents = [a for a in sim.agents.values() if a.assigned_task]
        for agent in active_agents:
            task = sim.tasks.get(agent.assigned_task)
            if task:
                focus_icon = "⚡" if agent.focus and any(f in task.name.lower() for f in agent.focus.split()) else "  "
                print(f"   {focus_icon} {agent.name} → {task.name} ({task.remaining:.1f}h remaining)")
        
        time.sleep(delay)
        
        # Apply work
        progress = sim._apply_work(multiplier)
        
        print("\n💼 PROGRESS THIS CYCLE:")
        for agent_name, task_name, effort in progress:
            print(f"   ✓ {agent_name}: +{effort:.2f}h on {task_name}")
        
        # Log and transcript
        sim._log_and_transcript(tick, events, progress)
        sim.ticks += 1
        
        # Show task status
        print("\n📈 TASK STATUS:")
        for task in sim.tasks.values():
            status = "✅ COMPLETE" if task.completed else f"🔄 {task.remaining:.1f}h left"
            bar_filled = int((1 - task.remaining/task.est_hours) * 20) if task.est_hours > 0 else 20
            bar = "█" * bar_filled + "░" * (20 - bar_filled)
            print(f"   {task.id}: [{bar}] {status}")
        
        time.sleep(delay)
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 SIMULATION COMPLETE")
    print("="*70)
    
    result = sim.run(max_ticks=0)  # Just get the current state
    result["ticks"] = sim.ticks
    result["completed"] = all(t.completed for t in sim.tasks.values())
    result["completed_ids"] = sorted(sim.completed)
    
    print(f"\n📊 FINAL METRICS:")
    print(f"   ⏱️  Cycles Elapsed: {result['ticks']}")
    print(f"   ✅ Tasks Completed: {len(result['completed_ids'])}/{len(sim.tasks)}")
    print(f"   🎯 Completion Rate: {len(result['completed_ids'])/len(sim.tasks)*100:.0f}%")
    print(f"   ⚡ Efficiency: {(sum(t.est_hours for t in sim.tasks.values())/result['ticks'])*100:.1f}% parallelization")
    
    print("\n👥 FINAL CREW STATUS:")
    print_crew_status(sim.agents)
    
    print("\n💬 CREW CHAT HIGHLIGHTS:")
    for msg in sim.transcript[-8:]:
        print(f"   {msg}")
    
    print("\n" + "="*70)
    print("✨ Ready for next phase deployment")
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive Orion Station Simulation")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--ticks", type=int, default=10, help="Max cycles")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between cycles (seconds)")
    parser.add_argument("--fast", action="store_true", help="Run without delays")
    
    args = parser.parse_args()
    delay = 0.1 if args.fast else args.delay
    
    try:
        interactive_simulation(seed=args.seed, ticks=args.ticks, delay=delay)
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
        sys.exit(0)
