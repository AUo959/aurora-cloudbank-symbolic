#!/usr/bin/env python3
"""
Orion Station Simulation v2.0 - L1 Canon Character Integration
--------------------------------------------------------------
Enhanced simulation using canonical character loader for authentic crew modeling.

Key Improvements from v1.0:
- Loads characters from L1_CANON_CHARACTER_ROSTER.md (no hardcoded profiles)
- Supports full 40+ character roster expansion
- Accurate simulation stats from canonical data
- Dynamic focus matching based on character specializations
- Collaboration bonuses for canonical partnerships
- Phase 1 role integration

Symbolic Tag: s.tag::sim.orion.v2
"""

from __future__ import annotations

import argparse
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import character loader
from character_loader import CharacterLoader

# ----------------------
# Core Data Structures
# ----------------------


@dataclass
class Task:
    """Simulation task with dependencies and progress tracking"""
    id: str
    name: str
    est_hours: float
    remaining: float
    depends_on: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    completed: bool = False
    # New: semantic tags for better character matching
    semantic_tags: Set[str] = field(default_factory=set)

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
    """Enhanced agent with canonical character integration"""
    name: str
    role: str
    character_id: str
    base_speed: float
    specialization_multiplier: float = 1.0
    collaboration_bonus: float = 0.0
    focus_keywords: Set[str] = field(default_factory=set)
    collaborators: Set[str] = field(default_factory=set)
    fatigue: float = 0.0
    assigned_task: Optional[str] = None

    def effective_speed(self, is_collaborative_context: bool = False) -> float:
        """Calculate effective work speed with all modifiers"""
        # Fatigue penalty (up to -10%)
        fatigue_penalty = min(0.10, self.fatigue * 0.005)
        base = self.base_speed * (1.0 - fatigue_penalty)
        
        # Collaboration bonus
        if is_collaborative_context:
            base *= (1.0 + self.collaboration_bonus)
        
        return base

    def get_specialization_match(self, task_tags: Set[str]) -> float:
        """Calculate specialization match bonus for task"""
        if not task_tags or not self.focus_keywords:
            return 1.0
        
        # Check overlap between task tags and character focus
        overlap = len(task_tags & self.focus_keywords)
        if overlap > 0:
            return self.specialization_multiplier
        return 1.0

    def tick_recovery(self) -> None:
        """Tiny recovery when idle, fatigue accumulation when working"""
        if not self.assigned_task:
            self.fatigue = max(0.0, self.fatigue - 0.5)
        else:
            self.fatigue = min(100.0, self.fatigue + 0.8)


@dataclass
class Event:
    """Simulation event (emergent behaviors, milestones, etc.)"""
    tick: int
    kind: str
    description: str
    multiplier: float
    affected_agents: List[str] = field(default_factory=list)


# ----------------------
# Aurora Orchestrator v2
# ----------------------


class AuroraOrchestrator:
    """Enhanced orchestrator with character-aware event generation"""
    
    def __init__(self, rng: random.Random, enable_emergent: bool = True):
        self.rng = rng
        self.global_multiplier = 1.0
        self.events: List[Event] = []
        self.enable_emergent = enable_emergent

    def maybe_emit_events(
        self,
        tick: int,
        agents: Dict[str, Agent],
        tasks: Dict[str, Task]
    ) -> List[Event]:
        """Generate emergent events based on current simulation state"""
        emitted: List[Event] = []
        if not self.enable_emergent:
            return emitted
        
        # Swarm Sync: Check for collaborative pairs
        working_agents = [a for a in agents.values() if a.assigned_task]
        if len(working_agents) >= 2 and self.rng.random() < 0.20:
            pair = self.rng.sample(working_agents, 2)
            e = Event(
                tick, "swarm_sync",
                f"{pair[0].name} & {pair[1].name} spontaneous pair-programming",
                1.15,
                [a.name for a in pair]
            )
            emitted.append(e)
        
        # Collaborative Boost: Characters working with canonical collaborators
        for agent in working_agents:
            task = tasks.get(agent.assigned_task)
            if task and self.rng.random() < 0.15:
                # Check if any collaborators are on same task
                collab_present = any(
                    c in task.assignees for c in agent.collaborators
                )
                if collab_present:
                    e = Event(
                        tick, "collaboration_boost",
                        f"{agent.name} synergy with key collaborator",
                        1.0 + agent.collaboration_bonus,
                        [agent.name]
                    )
                    emitted.append(e)
        
        # Insight Pulse (meta-knowledge injection)
        if self.rng.random() < 0.15:
            e = Event(
                tick, "insight_pulse",
                "Aurora provides strategic context",
                1.10,
                []
            )
            emitted.append(e)
        
        # Cross-Pollination (knowledge transfer)
        if len(working_agents) >= 3 and self.rng.random() < 0.10:
            e = Event(
                tick, "cross_pollination",
                "Knowledge transfer across specializations",
                1.05,
                []
            )
            emitted.append(e)
        
        self.events.extend(emitted)
        return emitted

    def aggregate_multiplier(self, events: List[Event], agent_name: Optional[str] = None) -> float:
        """Calculate aggregate multiplier for specific agent or global"""
        m = 1.0
        for e in events:
            # Apply event if global or agent-specific
            if not e.affected_agents or (agent_name and agent_name in e.affected_agents):
                m *= e.multiplier
        return m


# ----------------------
# Assignment Coordinator v2
# ----------------------


class AssignmentCoordinator:
    """Enhanced coordinator using canonical character data for assignment"""
    
    def __init__(self, rng: random.Random):
        self.rng = rng

    def assign(
        self,
        agents: Dict[str, Agent],
        tasks: Dict[str, Task],
        completed: set[str]
    ) -> None:
        """Assign tasks to agents based on specializations and availability"""
        available_tasks = self._available_sorted(tasks, completed)
        self._assign_idle(agents, available_tasks)
        self._maybe_reassign(agents, available_tasks)

    def _available_sorted(self, tasks: Dict[str, Task], completed: set[str]) -> List[Task]:
        """Get available tasks sorted by priority"""
        available = [
            t for t in tasks.values()
            if (not t.completed) and t.can_start(completed)
        ]
        # Sort by remaining hours (longest first) then by ID
        available.sort(key=lambda t: (-t.remaining, t.id))
        return available

    def _assign_idle(self, agents: Dict[str, Agent], available_tasks: List[Task]) -> None:
        """Assign idle agents to best-fit tasks"""
        idle_agents = [a for a in agents.values() if a.assigned_task is None]
        
        for agent in idle_agents:
            if not available_tasks:
                break
            
            # Find best task match based on focus keywords
            best_task = None
            best_score = 0.0
            
            for task in available_tasks:
                if agent.name in task.assignees:
                    continue  # Skip if already assigned to this task
                
                # Calculate match score
                keyword_overlap = len(agent.focus_keywords & task.semantic_tags)
                score = keyword_overlap + self.rng.random() * 0.1  # Small random tie-breaker
                
                if score > best_score:
                    best_score = score
                    best_task = task
            
            # Assign to best match (or first available if no good match)
            target_task = best_task or available_tasks[0]
            agent.assigned_task = target_task.id
            if agent.name not in target_task.assignees:
                target_task.assignees.append(agent.name)

    def _maybe_reassign(self, agents: Dict[str, Agent], available_tasks: List[Task]) -> None:
        """Occasionally reassign agents to better-fit tasks"""
        if self.rng.random() >= 0.10:
            return
        
        busy_agents = [a for a in agents.values() if a.assigned_task is not None]
        if not busy_agents or not available_tasks:
            return
        
        agent = self.rng.choice(busy_agents)
        current_task = next((t for t in available_tasks if t.id == agent.assigned_task), None)
        
        # Look for better match
        for task in available_tasks:
            if task.id == agent.assigned_task:
                continue
            
            current_score = len(agent.focus_keywords & (current_task.semantic_tags if current_task else set()))
            new_score = len(agent.focus_keywords & task.semantic_tags)
            
            if new_score > current_score:
                agent.assigned_task = task.id
                if agent.name not in task.assignees:
                    task.assignees.append(agent.name)
                break


# ----------------------
# Enhanced Simulation Engine
# ----------------------


class OrionSimulationV2:
    """Orion Station simulation with L1 Canon character integration"""
    
    def __init__(
        self,
        seed: int = 42,
        enable_emergent: bool = True,
        roster_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.rng = random.Random(seed)
        self.aurora = AuroraOrchestrator(self.rng, enable_emergent=enable_emergent)
        self.coordinator = AssignmentCoordinator(self.rng)
        self.ticks: int = 0
        self.max_ticks: int = 30
        self.log: List[str] = []
        self.transcript: List[str] = []
        self.logger = logger or logging.getLogger(__name__)
        
        # Load canonical characters
        self.char_loader = CharacterLoader(roster_path=roster_path, logger=self.logger)
        self.logger.info(f"Loaded {len(self.char_loader.characters)} canonical characters")
        
        # Initialize tasks
        self.tasks = self._init_phase1_tasks()
        
        # Initialize agents from canonical roster
        self.agents = self._init_agents_from_roster()
        
        self.completed: set[str] = set()

    def _init_phase1_tasks(self) -> Dict[str, Task]:
        """Initialize Phase 1 security tasks with semantic tags"""
        return {
            "T1": Task(
                "T1", "CORS Fix", est_hours=2.0, remaining=2.0, depends_on=[],
                semantic_tags={"security", "api", "cors", "backend"}
            ),
            "T2": Task(
                "T2", "CSRF Validation", est_hours=4.0, remaining=4.0, depends_on=["T1"],
                semantic_tags={"security", "validation", "csrf", "auth"}
            ),
            "T3": Task(
                "T3", "WebSocket Auth", est_hours=4.0, remaining=4.0, depends_on=["T2"],
                semantic_tags={"security", "auth", "websocket", "backend"}
            ),
            "T4": Task(
                "T4", "Replace eval() with AST", est_hours=3.0, remaining=3.0, depends_on=[],
                semantic_tags={"security", "compiler", "ast", "validation", "code"}
            ),
        }

    def _init_agents_from_roster(self) -> Dict[str, Agent]:
        """Create Agent instances from canonical character data"""
        agents = {}
        
        # Get Phase 1 characters
        phase1_chars = self.char_loader.get_characters_for_phase1()
        self.logger.info(f"Found {len(phase1_chars)} characters with Phase 1 roles")
        
        for char in phase1_chars:
            focus_keywords = self.char_loader.get_focus_keywords(char)
            collaborator_names = {c.split('(')[0].strip() for c in char.key_collaborators}
            
            agent = Agent(
                name=char.name,
                role=char.role,
                character_id=char.character_id,
                base_speed=char.base_speed,
                specialization_multiplier=char.specialization_multiplier,
                collaboration_bonus=char.collaboration_bonus,
                focus_keywords=focus_keywords,
                collaborators=collaborator_names
            )
            agents[char.name] = agent
            self.logger.debug(f"Created agent: {char.name} (focus: {len(focus_keywords)} keywords)")
        
        return agents

    def tick(self) -> None:
        """Execute one simulation tick"""
        tick = self.ticks
        events = self.aurora.maybe_emit_events(tick, self.agents, self.tasks)
        self._coordinate_assignments()
        progress = self._apply_work(events)
        self._log_and_transcript(tick, events, progress)
        self.ticks += 1

    def _coordinate_assignments(self) -> None:
        """Coordinate task assignments across agents"""
        self.coordinator.assign(self.agents, self.tasks, self.completed)

    def _apply_work(self, events: List[Event]) -> List[Tuple[str, str, float, str]]:
        """Apply work from all agents for current tick"""
        progress: List[Tuple[str, str, float, str]] = []
        
        for agent in self.agents.values():
            work_result = self._process_agent_work(agent, events)
            if work_result:
                progress.append(work_result)
        
        return progress

    def _process_agent_work(
        self,
        agent: Agent,
        events: List[Event]
    ) -> Optional[Tuple[str, str, float, str]]:
        """Process single agent's work for current tick"""
        if agent.assigned_task is None:
            agent.tick_recovery()
            return None
        
        task = self.tasks.get(agent.assigned_task)
        if not task or task.completed:
            agent.assigned_task = None
            agent.tick_recovery()
            return None
        
        # Calculate work with all bonuses
        effort = self._calculate_effort(agent, task, events)
        task.work(effort)
        agent.tick_recovery()
        
        if task.completed:
            self._mark_task_complete(task.id)
            result_marker = "✓ COMPLETE"
        else:
            result_marker = f"{task.remaining:.2f}h left"
        
        return (agent.name, task.name, effort, result_marker)

    def _calculate_effort(
        self,
        agent: Agent,
        task: Task,
        events: List[Event]
    ) -> float:
        """Calculate effort with all modifiers"""
        # Check if agent has key collaborators on this task
        is_collaborative = any(
            collab in task.assignees for collab in agent.collaborators
        )
        
        # Base speed with collaboration context
        base = agent.effective_speed(is_collaborative_context=is_collaborative)
        
        # Specialization match
        spec_bonus = agent.get_specialization_match(task.semantic_tags)
        
        # Event multipliers
        event_mult = self.aurora.aggregate_multiplier(events, agent.name)
        
        # Noise
        noise = self.rng.uniform(0.85, 1.15)
        
        effort = base * spec_bonus * event_mult * noise
        return min(2.0, max(0.1, effort))

    def _mark_task_complete(self, task_id: str) -> None:
        """Mark task complete and unassign all agents"""
        self.completed.add(task_id)
        for agent in self.agents.values():
            if agent.assigned_task == task_id:
                agent.assigned_task = None

    def _log_and_transcript(
        self,
        tick: int,
        events: List[Event],
        progress: List[Tuple[str, str, float, str]]
    ) -> None:
        """Log tick summary and generate transcript"""
        ev_desc = "; ".join(
            f"{e.kind}+{int((e.multiplier-1)*100)}%{f' [{e.affected_agents[0]}]' if e.affected_agents else ''}"
            for e in events
        ) or "none"
        
        prog_desc = ", ".join(
            f"{a}->{t} (+{eff:.2f}h){' ' + mark if '✓' in mark else ''}"
            for a, t, eff, mark in progress
        ) or "idle"
        
        remaining_desc = ", ".join(
            f"{t.id}:{t.remaining:.2f}h{'✓' if t.completed else ''}"
            for t in self.tasks.values()
        )
        
        line = f"Tick {tick:02d} | events: {ev_desc} | work: {prog_desc} | remaining: {remaining_desc}"
        self.log.append(line)
        self._append_chat_messages(tick, events, progress)

    def _append_chat_messages(
        self,
        tick: int,
        events: List[Event],
        progress: List[Tuple[str, str, float, str]]
    ) -> None:
        """Generate authentic crew dialogue using canonical character data"""
        def say(agent: str, msg: str) -> None:
            self.transcript.append(f"[{tick:02d}] {agent}: {msg}")
        
        # Opening message
        if tick == 0:
            say("Alex Thorne", "All hands, Phase 1 security implementation beginning. Aurora, coordinate assignments.")
            say("Aurora", "Phase 1 task distribution initiated. Assignments optimized for canonical specializations.")
        
        # Event messages
        for e in events:
            if e.kind == "swarm_sync" and e.affected_agents:
                say(e.affected_agents[0], f"Syncing with {e.affected_agents[1]} for collaborative sprint.")
            elif e.kind == "collaboration_boost" and e.affected_agents:
                say("Aurora", f"Collaboration synergy detected: {e.affected_agents[0]} performance enhanced.")
            elif e.kind == "insight_pulse":
                say("Aurora", "Strategic insight: prioritize authentication rigor and session binding.")
            elif e.kind == "cross_pollination":
                say("Varya Lin", "Documenting cross-functional learnings for protocol appendix.")
        
        # Progress messages (use actual character names and roles)
        for agent_name, task_name, effort, marker in progress:
            char = self.char_loader.get_character(agent_name)
            if char and "✓" in marker:
                say(agent_name, f"{task_name} complete. {char.role} validation passed.")
            elif tick % 3 == 0:  # Occasional progress updates
                if char:
                    say(agent_name, f"Progress on {task_name}: +{effort:.2f}h [{char.title}]")
        
        # Completion message
        if all(t.completed for t in self.tasks.values()):
            say("Alex Thorne", "Phase 1 security criticals complete. Excellent work, crew.")
            say("Aurora", "All Phase 1 tasks validated. Proceeding to security audit gate.")

    def run(self, max_ticks: Optional[int] = None) -> Dict[str, Any]:
        """Run simulation to completion or max ticks"""
        limit = max_ticks if max_ticks is not None else self.max_ticks
        
        for _ in range(limit):
            if all(t.completed for t in self.tasks.values()):
                break
            self.tick()
        
        # Final summary
        total_est = sum(t.est_hours for t in self.tasks.values())
        total_spent = sum(t.est_hours - t.remaining for t in self.tasks.values())
        completed_all = all(t.completed for t in self.tasks.values())
        
        return {
            "version": "2.0_l1_canon",
            "roster_version": self.char_loader.version,
            "characters_used": len(self.agents),
            "ticks": self.ticks,
            "completed": completed_all,
            "total_est": total_est,
            "total_spent": round(total_spent, 2),
            "completed_ids": sorted(self.completed),
            "log_tail": self.log[-8:],
            "transcript": self.transcript,
            "emergent_events": len(self.aurora.events)
        }


def demo_run(
    seed: int,
    ticks: int,
    enable_emergent: bool,
    log_level: str,
    transcript_out: Optional[str],
    json_out: Optional[str]
) -> None:
    """Run enhanced simulation with canonical characters"""
    import json
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(levelname)s: %(message)s"
    )
    
    sim = OrionSimulationV2(seed=seed, enable_emergent=enable_emergent)
    result = sim.run(max_ticks=ticks)
    
    print("=== Orion Station v2.0: L1 Canon Character Simulation ===")
    print(f"Roster Version: {result['roster_version']}")
    print(f"Characters: {result['characters_used']}")
    print(f"Ticks elapsed: {result['ticks']}")
    print(f"Completed all: {result['completed']}")
    print(f"Tasks completed: {', '.join(result['completed_ids'])}")
    print(f"Total estimated: {result['total_est']}h")
    print(f"Total simulated: {result['total_spent']}h")
    print(f"Emergent events: {result['emergent_events']}")
    
    print("\n--- Recent Activity (last ticks) ---")
    for line in result["log_tail"]:
        print(line)
    
    if transcript_out:
        with open(transcript_out, "w", encoding="utf-8") as f:
            f.write("\n".join(result["transcript"]))
        print(f"\n📝 Transcript: {transcript_out}")
    
    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"📊 JSON summary: {json_out}")
    
    if not result["completed"]:
        print("\n⚠️  Not all tasks finished — consider increasing ticks")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Orion Station v2.0 Multi-Agent Simulation with L1 Canon Characters"
    )
    p.add_argument("--seed", type=int, default=1337, help="Random seed")
    p.add_argument("--ticks", type=int, default=30, help="Max simulation ticks (hours)")
    p.add_argument("--no-emergent", action="store_true", help="Disable emergent behaviors")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    p.add_argument("--transcript-out", default=None, help="Write transcript to file")
    p.add_argument("--json-out", default=None, help="Write JSON summary to file")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    demo_run(
        seed=args.seed,
        ticks=args.ticks,
        enable_emergent=not args.no_emergent,
        log_level=args.log_level,
        transcript_out=args.transcript_out,
        json_out=args.json_out,
    )
