#!/usr/bin/env python3
"""
Orion Station Multi-Agent Simulation (L1 Canon) — Phase 1 Execution
-------------------------------------------------------------------
- Environment: Ant-farm universe sandbox, emergent behaviors encouraged
- Coordination: Aurora orchestrator
- Staff assignments: Alex Thorn (Coordinator)
- Pilot (Earth): External participant providing insight pulses

This simulation maps Phase 1 (Critical Security Fixes) from
`.github/IMPLEMENTATION_ROADMAP.md` into autonomous agent execution.

Phase 1 Tasks (from roadmap):
1. CORS Fix (2h)
2. CSRF Validation (4h) — depends on CORS
3. WebSocket Auth (4h) — depends on CSRF
4. Replace eval() with AST (3h) — independent, parallel

Agents (roles and strengths):
- Alex Thorn (Coordinator): boosts assignment efficiency and removes blockers
- Security Engineer: excels at appsec (CSRF, Auth, eval)
- Backend Engineer: strong API work (CORS, endpoints)
- DevOps Engineer: environment, rate limiting infra (future phases)
- Documentation Specialist: wraps changes with docs and tests scaffolds
- Pilot (Earth): injects insight pulses that can unlock accelerations

Emergent behaviors modeled:
- Swarm Sync: spontaneous pair-programming mid-tick (+15% productivity)
- Insight Pulse: Pilot sends context insight (+10% productivity team-wide)
- Cross-Pollination: knowledge transfer unlocks dependency sooner

Success criteria:
- All Phase 1 tasks completed within ~13 ticks (hours)
- Minimal idle time; dependencies respected; emergent boosts logged

Note: Keep stdlib only for portability.
"""
from __future__ import annotations

import argparse
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ----------------------
# Core Data Structures
# ----------------------


@dataclass
class Task:
    id: str
    name: str
    est_hours: float
    remaining: float
    depends_on: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    completed: bool = False

    def can_start(self, completed_ids: set[str]) -> bool:
        return all(d in completed_ids for d in self.depends_on)

    def work(self, effort_hours: float) -> None:
        if self.completed:
            return
        self.remaining = max(0.0, self.remaining - effort_hours)
        if self.remaining <= 0.0:
            self.completed = True


@dataclass
class Agent:
    name: str
    role: str
    base_speed: float
    focus: Optional[str] = None  # e.g., "security", "api"
    fatigue: float = 0.0         # grows slightly, reduces output
    assigned_task: Optional[str] = None

    def effective_speed(self) -> float:
        # Simple fatigue model: -0.5% per tick up to -10%
        fatigue_penalty = min(0.10, self.fatigue * 0.005)
        return self.base_speed * (1.0 - fatigue_penalty)

    def tick_recovery(self) -> None:
        # Tiny recovery when idle
        if not self.assigned_task:
            self.fatigue = max(0.0, self.fatigue - 0.5)
        else:
            self.fatigue = min(100.0, self.fatigue + 0.8)


@dataclass
class Event:
    tick: int
    kind: str
    description: str
    multiplier: float


# ----------------------
# Aurora Orchestrator
# ----------------------


class Aurora:
    def __init__(self, rng: random.Random, enable_emergent: bool = True):
        self.rng = rng
        self.global_multiplier = 1.0
        self.events: List[Event] = []
        self.enable_emergent = enable_emergent

    def maybe_emit_events(self, tick: int) -> List[Event]:
        emitted: List[Event] = []
        if not self.enable_emergent:
            return emitted
        # Swarm Sync: 20% chance per tick, +15% productivity for assignees
        if self.rng.random() < 0.20:
            e = Event(tick, "swarm_sync", "Spontaneous pair-programming", 1.15)
            emitted.append(e)
        # Insight Pulse (Pilot/Earth): 15% chance per tick, +10% team-wide
        if self.rng.random() < 0.15:
            e = Event(tick, "insight_pulse", "Pilot shares critical context", 1.10)
            emitted.append(e)
        # Cross-Pollination: 10% chance, reduces dependency friction
        if self.rng.random() < 0.10:
            e = Event(tick, "cross_pollination", "Knowledge transfer accelerates unblock", 1.05)
            emitted.append(e)
        self.events.extend(emitted)
        return emitted

    def aggregate_multiplier(self, events: List[Event]) -> float:
        m = 1.0
        for e in events:
            m *= e.multiplier
        return m


# ----------------------
# Assignment (Alex Thorn)
# ----------------------


class AssignmentCoordinator:
    def __init__(self, rng: random.Random):
        self.rng = rng

    def assign(self, agents: Dict[str, Agent], tasks: Dict[str, Task], completed: set[str]) -> None:
        # Simple heuristic assignment: respect dependencies, match focus
        available_tasks = self._available_sorted(tasks, completed)
        self._assign_idle(agents, available_tasks)
        self._maybe_shuffle(agents, available_tasks)

    def _available_sorted(self, tasks: Dict[str, Task], completed: set[str]) -> List[Task]:
        available = [t for t in tasks.values() if (not t.completed) and t.can_start(completed)]
        available.sort(key=lambda t: (-t.remaining, t.id))
        return available

    def _assign_idle(self, agents: Dict[str, Agent], available_tasks: List[Task]) -> None:
        idle_agents = [a for a in agents.values() if a.assigned_task is None]
        for agent in idle_agents:
            focused = [t for t in available_tasks if (agent.focus and agent.focus in t.name.lower())]
            candidate_pool = focused or available_tasks
            if candidate_pool:
                pick = candidate_pool[0]
                agent.assigned_task = pick.id
                if agent.name not in pick.assignees:
                    pick.assignees.append(agent.name)

    def _maybe_shuffle(self, agents: Dict[str, Agent], available_tasks: List[Task]) -> None:
        if self.rng.random() >= 0.10:
            return
        busy_agents = [a for a in agents.values() if a.assigned_task is not None]
        if not busy_agents:
            return
        agent = self.rng.choice(busy_agents)
        for t in available_tasks:
            if agent.focus and agent.focus in t.name.lower() and t.id != agent.assigned_task:
                agent.assigned_task = t.id
                break


# ----------------------
# Simulation Engine
# ----------------------


class OrionSimulation:
    def __init__(self, seed: int = 42, enable_emergent: bool = True, logger: Optional[logging.Logger] = None):
        self.rng = random.Random(seed)
        self.aurora = Aurora(self.rng, enable_emergent=enable_emergent)
        self.coordinator = AssignmentCoordinator(self.rng)
        self.ticks: int = 0
        self.max_ticks: int = 30  # ~hours
        self.log: List[str] = []
        # Chat transcript per tick (crew dialogue)
        self.transcript: List[str] = []
        self.logger = logger or logging.getLogger(__name__)

        # Define Phase 1 tasks
        self.tasks: Dict[str, Task] = {
            "T1": Task("T1", "CORS Fix", est_hours=2.0, remaining=2.0, depends_on=[]),
            "T2": Task("T2", "CSRF Validation", est_hours=4.0, remaining=4.0, depends_on=["T1"]),
            "T3": Task("T3", "WebSocket Auth", est_hours=4.0, remaining=4.0, depends_on=["T2"]),
            "T4": Task("T4", "Replace eval() with AST", est_hours=3.0, remaining=3.0, depends_on=[]),
        }

        # Define agents
        self.agents: Dict[str, Agent] = {
            # Crew constants
            "Alex Thorn": Agent("Alex Thorn", role="Coordinator", base_speed=0.2, focus="coord"),
            "SecEng": Agent("SecEng", role="Security Engineer", base_speed=1.25, focus="validation auth eval"),
            "Backend": Agent("Backend", role="Backend Engineer", base_speed=1.10, focus="api cors"),
            "DevOps": Agent("DevOps", role="DevOps Engineer", base_speed=0.90, focus="infra"),
            "DocSpec": Agent("DocSpec", role="Documentation", base_speed=0.60, focus="doc"),
            "Pilot": Agent("Pilot", role="Pilot (Earth)", base_speed=0.10, focus="insight"),
        }

        self.completed: set[str] = set()

    def tick(self) -> None:
        tick = self.ticks
        events, multiplier = self._emit_and_multiply(tick)
        self._coordinate_assignments()
        progress = self._apply_work(multiplier)
        self._log_and_transcript(tick, events, progress)
        self.ticks += 1

    def _emit_and_multiply(self, tick: int) -> Tuple[List[Event], float]:
        events = self.aurora.maybe_emit_events(tick)
        # Stochastic obstruction: 10% chance to add friction (0.85x)
        obstruction_multiplier = 0.85 if self.rng.random() < 0.10 else 1.0
        multiplier = self.aurora.aggregate_multiplier(events) * obstruction_multiplier
        return events, multiplier

    def _coordinate_assignments(self) -> None:
        self.coordinator.assign(self.agents, self.tasks, self.completed)

    def _apply_work(self, multiplier: float) -> List[Tuple[str, str, float]]:
        progress: List[Tuple[str, str, float]] = []
        for agent in self.agents.values():
            if agent.role == "Coordinator":
                agent.tick_recovery()
                continue
            if agent.assigned_task is None:
                agent.tick_recovery()
                continue
            task = self.tasks.get(agent.assigned_task)
            if not task or task.completed:
                agent.assigned_task = None
                agent.tick_recovery()
                continue

            # Base effort with stochasticity (partial progress realism)
            focus_bonus = 1.10 if (agent.focus and any(f in task.name.lower() for f in agent.focus.split())) else 1.0
            noise = self.rng.uniform(0.85, 1.15)
            effort = agent.effective_speed() * focus_bonus * multiplier * noise
            effort = min(2.0, max(0.1, effort))  # ensure some minimal forward motion

            task.work(effort)
            progress.append((agent.name, task.name, effort))
            agent.tick_recovery()

            if task.completed:
                self.completed.add(task.id)
                for a in self.agents.values():
                    if a.assigned_task == task.id:
                        a.assigned_task = None
        return progress

    def _log_and_transcript(self, tick: int, events: List[Event], progress: List[Tuple[str, str, float]]) -> None:
        ev_desc = "; ".join(f"{e.kind}+{int((e.multiplier-1)*100)}%" for e in events) or "none"
        prog_desc = ", ".join(f"{a}->{t} (+{effort:.2f}h)" for a, t, effort in progress) or "idle"
        remaining_desc = ", ".join(
            f"{t.id}:{t.remaining:.2f}h{'*' if t.completed else ''}"
            for t in self.tasks.values()
        )
        line = f"Tick {tick:02d} | events: {ev_desc} | work: {prog_desc} | remaining: {remaining_desc}"
        self.log.append(line)
        self._append_chat_messages(tick, events, progress)

    def _append_chat_messages(self, tick: int, events: List[Event], progress: List[Tuple[str, str, float]]) -> None:
        # Crew chat vibe: short, role-tagged messages
        def say(agent: str, msg: str) -> None:
            self.transcript.append(f"[{tick:02d}] {agent}: {msg}")

        if tick == 0:
            say("Alex Thorn", "Aurora synced. Kicking off Phase 1. Assignments in flight.")
        for e in events:
            if e.kind == "swarm_sync":
                say("Aurora", "Swarm sync detected — pairing up for throughput boost.")
            if e.kind == "insight_pulse":
                say("Pilot", "Pushing context: prioritize CSRF rigor; bind tokens to session.")
            if e.kind == "cross_pollination":
                say("DocSpec", "Capturing learnings for protocol appendix.")
        for a, t, effort in progress:
            if a == "SecEng":
                say(a, f"Advancing {t} (+{effort:.2f}h).")
            elif a == "Backend":
                say(a, f"API path steady on {t} (+{effort:.2f}h).")
            elif a == "DevOps":
                say(a, f"Infra assist on {t} (+{effort:.2f}h).")
            elif a == "DocSpec":
                say(a, f"Documenting changes for {t} (+{effort:.2f}h).")
            elif a == "Pilot":
                say(a, f"Observing; echoing best practices for {t} (+{effort:.2f}h).")
        if all(t.completed for t in self.tasks.values()):
            say("Aurora", "Phase 1 criticals complete. Proceeding to validation gate.")

    def run(self, max_ticks: Optional[int] = None) -> Dict[str, Any]:
        limit = max_ticks if max_ticks is not None else self.max_ticks
        for _ in range(limit):
            # Early exit if all done
            if all(t.completed for t in self.tasks.values()):
                break
            self.tick()

        # Final summary
        total_est = sum(t.est_hours for t in self.tasks.values())
        total_spent = sum(t.est_hours - t.remaining for t in self.tasks.values())
        completed_all = all(t.completed for t in self.tasks.values())
        return {
            "ticks": self.ticks,
            "completed": completed_all,
            "total_est": total_est,
            "total_spent": round(total_spent, 2),
            "completed_ids": sorted(self.completed),
            "log_tail": self.log[-8:],
            "transcript": self.transcript,
        }



def demo_run(seed: int, ticks: int, enable_emergent: bool, log_level: str, transcript_out: Optional[str]) -> None:
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO), format="%(levelname)s %(message)s")
    sim = OrionSimulation(seed=seed, enable_emergent=enable_emergent)
    result = sim.run(max_ticks=ticks)

    print("=== Orion Station: Phase 1 Simulation Summary ===")
    print(f"Ticks elapsed: {result['ticks']}")
    print(f"Completed all: {result['completed']}")
    print(f"Tasks completed: {', '.join(result['completed_ids'])}")
    print(f"Total estimated hours: {result['total_est']}")
    print(f"Total simulated effort: {result['total_spent']}h")
    print("\n--- Recent Activity (last ticks) ---")
    for line in result["log_tail"]:
        print(line)

    if transcript_out:
        with open(transcript_out, "w", encoding="utf-8") as f:
            f.write("\n".join(result["transcript"]))
        print(f"\nTranscript written to: {transcript_out}")

    if not result["completed"]:
        print("\nNOTE: Not all tasks finished within the time window — consider increasing ticks or adding agents.")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Orion Station Multi-Agent Simulation (Phase 1)")
    p.add_argument("--seed", type=int, default=1337, help="Random seed")
    p.add_argument("--ticks", type=int, default=30, help="Max ticks (hours)")
    p.add_argument("--no-emergent", action="store_true", help="Disable emergent behavior events")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")
    p.add_argument("--transcript-out", default=None, help="Write chat transcript to file path")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    demo_run(
        seed=args.seed,
        ticks=args.ticks,
        enable_emergent=not args.no_emergent,
        log_level=args.log_level,
        transcript_out=args.transcript_out,
    )
