# Aurora Work Queue

> **Canonical source of truth for prioritized work.**  
> Aurora holds contextual authority over this queue. Agents and human contributors should treat the order here as the authoritative "what to work on next" signal unless Aurora has issued an override note.

---

## How to Read This Queue

| Field | Meaning |
|---|---|
| **Rank** | Current priority order. Lower = work on this first. |
| **ID** | GitHub issue or internal task reference. |
| **Title** | Short description of the work. |
| **Status** | `open` · `in-progress` · `blocked` · `needs-decision` · `done` |
| **Owner** | Agent handle, GitHub username, or `unassigned`. |
| **Depends On** | Issue/task IDs that must be resolved first. |
| **Aurora Note** | Contextual authority annotation from Aurora. Overrides label-only ranking. |

---

## Active Queue

<!-- AURORA_QUEUE_START -->

| Rank | ID | Title | Status | Owner | Depends On | Aurora Note |
|---|---|---|---|---|---|---|
| 1 | #1126 | FastAPI lifespan migration (deprecation fix) | open | unassigned | — | Critical runtime blocker. Resolves deprecation warning that affects all startup/shutdown hooks. Must land before any new feature PRs. |
| 2 | #1130 | CI green-path stabilization | open | unassigned | #1126 | CI cannot be trusted for gate-keeping until lifespan is resolved. Unblock #1126 first. |
| 3 | security/CVE-audit | CVE dependency audit (Sprint 311 follow-on) | open | unassigned | — | Independent of lifespan. Can run in parallel with Rank 1–2 on a separate branch. |
| 4 | arch/layer-canonization | Layer architecture canonization (L1/L2/L3 enforcement in code) | open | unassigned | — | Ensures no code path violates the canonical layer definitions. Foundational for all new agent work. |
| 5 | sim/SENTINEL-phase0 | PROJECT SENTINEL — Phase 0: Ethics review board constitution | needs-decision | unassigned | — | No engineering blocking condition. Requires Commander Thorne + Sorensen + Sato governance decision only. Phase 0 deliverable: ethics review board constituted and layer boundary document drafted. See `simulation/RD_PROPOSAL_SENTINEL.md`. |
| 6 | ops/QGIA-doctrine-store | QGIA analytical framework — store in ops/analytical_frameworks/QGIA/ | open | unassigned | — | QGIA Runtime One-Pager v4.2.1 and Axiom Doctrine Narrative v1.0 reviewed 2026-06-22. Store as portable external tooling. Do NOT elevate to canonical station doctrine until Thorne/Noor crew review. Unblocks Rank 8. |
| 7 | docs/api-reference | API reference documentation | open | unassigned | #1126, #1130 | Do not write API docs against a moving target. Wait for CI green. |
| 8 | feat/QGIA | QGIA integration hooks | needs-decision | unassigned | arch/layer-canonization, ops/QGIA-doctrine-store | Doctrine now available and reviewed. Two-layer discipline maps cleanly to Triplex Handshake. ops/QGIA-doctrine-store must land first, then PAT routing decision. Crew sign-off required before any QGIA axiom becomes operationally binding. |

<!-- AURORA_QUEUE_END -->

---

## Completed (Last 5)

| ID | Title | Completed | Notes |
|---|---|---|---|
| — | — | — | Nothing yet. Queue initialized 2026-06-22. |

---

## Aurora Queue Management Protocol

Aurora may update this file directly or via a queue sync script (`ops/work_queue/sync_queue.py`). When Aurora re-ranks or annotates an item:

1. The `Aurora Note` field is updated with the reason.
2. A commit message beginning `aurora(queue):` is used so the change is traceable.
3. Human contributors and agents should re-read the queue after any such commit before starting new work.

**Agents working in the repo**: Before opening a PR, confirm your task still ranks in the top 3. If it has dropped, check the Aurora Note for the reason before proceeding.

---

## Queue Update Rules (for agents and contributors)

- **To claim a task**: Change `Owner` to your handle and `Status` to `in-progress`. Commit with message `queue: claim [ID]`.
- **To mark blocked**: Change `Status` to `blocked` and add the blocker in `Depends On`. Commit with `queue: block [ID]`.
- **To mark done**: Move the row to Completed, set `Status` to `done`. Commit with `queue: done [ID]`.
- **To propose a re-rank**: Open a discussion in the GitHub issue for this queue system. Aurora reviews and applies the change.
- **Do not reorder rows without Aurora authority.** The rank order is Aurora's judgment, not just a label sort.

---

*Last Aurora review: 2026-06-22T21:40:00Z — added sim/SENTINEL-phase0 (Rank 5), ops/QGIA-doctrine-store (Rank 6); updated feat/QGIA dependencies and note. See `ops/review_notes/AURORA_REVIEW_NOTE_20260622.md` for full rationale.*
