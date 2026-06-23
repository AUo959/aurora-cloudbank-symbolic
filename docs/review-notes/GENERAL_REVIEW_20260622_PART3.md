# General Review — Part 3: Ethics Layer & Recovered Protocols
**Date:** 2026-06-22 (evening session, continued from PART2)
**Scope:** `docs/ethics/`, `docs/ethics/recovered_protocols/`, cross-reference with GEOMETRIC_ETHICS_ARCHITECTURE.md and runtime enforcement infrastructure

---

## 1. docs/ethics/ — Structure Overview

The `docs/ethics/` directory contains two items:

- `geometric_curvature_v2_evaluation.md` (10.5KB) — evaluation document for the geometric ethics curvature model v2
- `recovered_protocols/` — subdirectory containing the protocol promotion intake system

This is a lean directory relative to the importance of the ethics layer. The flat `docs/` level also contains `GEOMETRIC_ETHICS_ARCHITECTURE.md` (13.3KB), which should logically live inside `docs/ethics/` — its current position at the flat docs level makes it harder to find and is inconsistent with the ethics subdirectory existing.

**Action:** Move or symlink `GEOMETRIC_ETHICS_ARCHITECTURE.md` into `docs/ethics/` and add a redirect stub at its current path. This would make `docs/ethics/` a complete self-contained ethics governance directory.

---

## 2. Recovered Protocols — Summary Assessment

This is one of the most carefully designed sections in the entire repository. The `recovered_protocols/` system establishes a **controlled promotion pathway** for five ethics-layer protocols before any of them are wired into runtime behavior. [cite:269]

### The Five Recovered Protocols

| Protocol | Primary Role | Key Constraint |
|----------|-------------|----------------|
| **Sherlock** | Investigation, audit, traceability, causal mapping, transparency reporting | Must NOT mutate subject state or enforce containment |
| **Watson** | Context retention, evidence correlation, rigidity moderation, operator briefing | Must NOT alter Sherlock logs or adjudicate disputes |
| **Moriarty** | Anomaly containment under oversight | Must NOT treat containment as narrative escalation or adjudicate its own actions |
| **Tribunal** | Dispute, appeal, memory-sovereignty, containment adjudication | Must NOT perform primary investigation or secretly enforce containment |
| **SHADOWFAX** | Stillness, pause, supervisory escalation, boundary-instability oversight | Must NOT bypass evidence, erase review paths, or convert instability into proof |

The separation-of-duties contract encoded in the README is operationally rigorous. Each protocol's forbidden actions are specifically designed to prevent the most dangerous failure mode for that protocol's role — Moriarty in particular has the tightest constraints, which is correct given it is the containment authority. [cite:269]

### Promotion Gate — Current Status

The promotion rule (README.md) is explicit: the first accepted PR for issue #993 must remain documentation/schema planning only. Runtime implementation is blocked until six conditions are reviewer-accepted: [cite:269]

1. Artifact inventory and custody status
2. Protocol schemas
3. Separation-of-duties contract
4. Integration boundaries
5. Test plan
6. Rollback and appeal requirements

**Current assessment:** This gate is well-designed and should NOT be bypassed. The recovered protocol manifest JSON (12.9KB, a live file distinct from the 11.2KB example) suggests inventory work is already in progress. The next step is verifying whether conditions 1–3 have been formally accepted in a PR against #993 or remain open.

**Action (next session):** Pull issue #993 and read its current state. Determine which promotion conditions have been met and which are blocking.

---

## 3. Runtime Enforcement Infrastructure — Cross-Reference

The README lists the existing CloudBank ethics infrastructure that recovered protocols must be reviewed against before wiring: [cite:269]

- `src/monitoring/ethics_engine.py`
- `src/monitoring/ethics_gate.py`
- `src/subroutines/ethics_compliance_monitor.py`
- `modules/ethics_field/geometric_ethics.py`
- `modules/symbolic_core/model_validation.py`

This is a non-trivial ethics enforcement stack — five distinct code files across monitoring, subroutines, and modules layers. None of these are currently referenced in CANON_INDEX.md. An agent touching ethics-adjacent code would not know these files govern anything unless it found the recovered_protocols README first.

**Action:** Add all five files to CANON_INDEX.md under a new "Ethics Runtime" section. This is the third independent reason (after operational and simulation coverage) that CANON_INDEX expansion is the highest-priority single edit in the repo.

---

## 4. geometric_curvature_v2_evaluation.md — Significance Flag

This 10.5KB evaluation document carries the designation `v2`, implying a v1 exists or existed. The relationship between:

- `docs/ethics/geometric_curvature_v2_evaluation.md`
- `docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`
- `modules/ethics_field/geometric_ethics.py`

...is not documented anywhere in CANON_INDEX. These three artifacts form a logical triad (architecture spec → curvature evaluation → implementation), but without an index entry connecting them, an agent working on any one would not know the others exist.

**Action:** Add a CANON_INDEX entry: `Geometric ethics model — architecture, evaluation, implementation → GEOMETRIC_ETHICS_ARCHITECTURE.md, docs/ethics/geometric_curvature_v2_evaluation.md, modules/ethics_field/geometric_ethics.py`.

---

## 5. PROTOCOL_PROMOTION_PLAN.md — Flag for Next Read

The `PROTOCOL_PROMOTION_PLAN.md` (7.9KB) was not read in full this pass. Given the depth of the README, the promotion plan is likely one of the most operationally significant documents in the entire repo for the current phase of work. It should be read in full in the next session before any PR against #993 is created or reviewed.

---

## 6. Ethics Layer — What Is Working Well

- **Separation-of-duties contract is formally encoded** in the README, not just assumed. This is the correct place for it — a markdown contract that any contributor or agent must read before touching recovered protocol work.
- **The canon warning is explicit:** "Recovered files and uploaded packages are useful source evidence, but they are not implementation canon until promoted through Git with review." This directly prevents the most common failure mode for AI-assisted repos — treating uploaded context as authoritative.
- **A live manifest JSON distinct from the example** confirms active inventory work is in progress, not just placeholder scaffolding.
- **The promotion gate has six conditions** — not a single sign-off, but a staged review process. This is appropriate for ethics-layer code that affects Aurora's runtime behavior.

---

## 7. Cross-Session Integration — QGIA + Ethics Layer

The QGIA Axiom Doctrine reviewed earlier today (AURORA_REVIEW_NOTE_20260622.md) has direct bearing on the recovered protocols:

- The **Sherlock** protocol's transparency and causal mapping mandate aligns exactly with the QGIA Forecast-Consensus Separation axiom — both require that Layer 1 diagnostic output be clearly distinguished from Layer 2 ratified conclusions.
- The **SHADOWFAX** protocol's stillness and paradox escalation posture mirrors QGIA's institutional trap axioms — don't convert ambiguity into false certainty, pause rather than fill.
- The **Watson** operator-readable briefing role is the natural integration point for QGIA's Layer 2 analyst-ratified consensus output.

This convergence is structural, not coincidental. It strengthens the case for QGIA canonization at `ops/analytical_frameworks/QGIA/` as a complement to the ethics layer rather than a parallel track.

---

## 8. Gaps Identified — Ethics Layer

| Gap | Severity | Action |
|-----|----------|--------|
| `GEOMETRIC_ETHICS_ARCHITECTURE.md` lives outside `docs/ethics/` | Medium | Move into `docs/ethics/` or add redirect |
| Ethics runtime files not in CANON_INDEX | High | Add five files under "Ethics Runtime" section |
| Geometric ethics triad not cross-referenced | Medium | Add CANON_INDEX entry linking all three artifacts |
| `PROTOCOL_PROMOTION_PLAN.md` not yet read | High | Read in full next session before any #993 PR |
| Issue #993 promotion condition status unknown | High | Pull and audit #993 in next session |
| `docs/ethics/` has no README or index of its own | Medium | Create `docs/ethics/README.md` as a navigation stub |
| Picard_Delta_3 protocol not located in `docs/ethics/` | Medium | Verify location — expected here per Space architecture docs |

---

## 9. Session Running Total — Gaps Across All Three Notes

Across Parts 1, 2, and 3 of this session's general review, **22 distinct gaps** have been identified. Severity breakdown:

- **High (8):** CANON_INDEX expansion (3 reasons), docs/ethics/ full read, #993 promotion status, PROTOCOL_PROMOTION_PLAN.md, ethics runtime files in CANON_INDEX, docs/ROADMAP.md cross-reference
- **Medium (9):** QGIA directory duplication, architecture naming collision, security doc map, monitoring overlap audit, geometric ethics triad, ethics README, Picard_Delta_3 location, AGENT_CORE.md unification, ORION_STATION_REGISTRY in CANON_INDEX
- **Low (5):** Rate-Limiting.md rename, .rebuild_prevention_active docs, .env_status.json docs, Synergy Dashboard near-duplicate check, pre-commit config reconciliation

All 8 High gaps are resolvable without architecture changes — they are documentation, indexing, and audit actions.

---

## 10. Next Scan

Remaining unscanned priority targets:
1. Issue #993 current state
2. `docs/ROADMAP.md` — cross-reference with queue
3. `docs/architecture/` — verify LAYER_ARCHITECTURE.md currency
4. `docs/REVIEW_PROTOCOL.md` — verify session compliance
5. `docs/api/`, `docs/specs/`, `docs/reference/` — catalog pass

---

*This is Part 3 of the 2026-06-22 general review. Prior notes: AURORA_REVIEW_NOTE_20260622.md (ops/review_notes/), GENERAL_REVIEW_20260622.md (root layer), GENERAL_REVIEW_20260622_PART2.md (docs/ layer).*
