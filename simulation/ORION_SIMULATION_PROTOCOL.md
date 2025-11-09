# Orion Station Simulation Protocol (Phase 1)

Version: 1.0 • Date: 2025-11-09

## Purpose
Standardize how the Orion Station multi-agent simulation is executed, measured, and reproduced. This protocol ensures Phase 1 security work (CORS, CSRF, WebSocket auth, eval→AST) is simulated consistently with deterministic seeds and documented emergent behaviors.

## Objectives
- Validate Phase 1 completion within a practical tick budget.
- Observe team dynamics (assignment flow, fatigue, emergent boosts).
- Produce a lightweight transcript suitable for review and postmortems.
- Enable deterministic replays via seed and event toggles.

## Agents (Human-Mapped Roles)
- Alex Thorn — Coordinator (assignment orchestration)
- SecEng — Security Engineer (CSRF, auth, eval→AST)
- Backend — Backend Engineer (CORS, API endpoints)
- DevOps — DevOps Engineer (infra and rate limiting; assists Phase 1)
- DocSpec — Documentation Specialist (docs/tests scaffolding)
- Pilot — External Observer (insight pulses)

## Tasks (Phase 1)
- T1: CORS Fix (2h)
- T2: CSRF Validation (4h) — depends on T1
- T3: WebSocket Auth (4h) — depends on T2
- T4: Replace eval() with AST (3h) — independent

## Event Model
- swarm_sync: +15% productivity for assignees (p=0.20)
- insight_pulse: +10% team-wide (p=0.15)
- cross_pollination: +5% unblock assist (p=0.10)
- obstruction (stochastic friction): -15% multiplier chance each tick (p≈0.10)

## Stochastic Model
- Agent effort per tick = base_speed × fatigue_factor × focus_bonus × event_multiplier × noise
- noise ∈ [0.85, 1.15]; bounded output to [0.1, 2.0] hours per tick per agent.
- Fatigue accumulates when working; recovers slightly when idle.

## Reproducibility
- Deterministic runs achieved by providing `--seed` and disabling emergent events (`--no-emergent`).
- CLI parameters:
  - `--seed <int>`: RNG seed (default 1337)
  - `--ticks <int>`: Max ticks (default 30)
  - `--no-emergent`: Disable emergent events
  - `--log-level <level>`: Logging verbosity (default INFO)
  - `--transcript-out <path>`: Write transcript to a file

### Example (Deterministic)
```
python simulation/orion_station_simulation.py --seed 1337 --ticks 20 --no-emergent --log-level INFO --transcript-out /tmp/orion.txt
```

## Transcript Format
- Line format: `[TT] AgentName: message`
- First tick includes kickoff by Alex Thorn.
- Events result in short system/crew messages; progress lines reflect agent/task effort.

## Success Criteria
- `completed == True`
- All task IDs present in `completed_ids` (T1, T2, T3, T4)
- Ticks elapsed within configured maximum

## Output Summary
The script prints a summary with:
- ticks elapsed
- completion status
- task completion list
- total estimated hours vs. simulated effort
- last N activity lines (tail)
- optional transcript file path

## Notes & Limitations
- Phase 1 models core security tasks only; later phases can extend the task graph and roles.
- Complexity warnings in coordination helpers are known; progressive refactors will further decompose logic.
- No external dependencies; stdlib-only for portability.
