# General Review — Aurora CloudBank Symbolic
**Date:** 2026-06-22 (evening session)
**Reviewer:** Aurora / Pilot session
**Scope:** Full repo surface scan — structure, tooling, governance, active gaps, queue architecture

---

## 1. Structural Observations

### Root Directory Density
The root is significantly crowded with dotfiles and tool-specific configs. Current count includes: `.aurora`, `.nexus`, `.nexus_schematics`, `.gitwiz`, `.repohealth`, `.sprint_metrics`, `.security`, `.deployment`, `.devcontainer`, `.codacy`, `.githooks`, `.husky`, `.bandit`, `.flake8`, `.pylintrc`, `.babelrc`, `.editorconfig`, `.markdownlint.json`, `.pip-audit-ignore.toml`, `.pre-commit-config.yaml`, `.pre-commit-config-optimized.yaml`, `.copilot-bash-profile`, `.copilotignore`, `.replit`, `.rebuild_prevention_active`.

**Observation:** Two parallel pre-commit configs exist (`.pre-commit-config.yaml` and `.pre-commit-config-optimized.yaml`). These should be reconciled — the canonical one identified and the other either deleted or renamed `*.archived`. Having two active configs creates ambiguity about which hooks actually run in CI vs. local developer environments.

**Observation:** `.rebuild_prevention_active` is a sentinel file, not a config. It signals a runtime state condition but lives at repo root like a permanent artifact. This should be documented clearly (what triggers it, who clears it, what it prevents). Currently undocumented in CONTRIBUTING.md or CLAUDE.md.

### QGIA Integration Directory Duplication
Two directories exist at root level:
- `QGIA_Integration/` (capitalized)
- `QGIA_integration/` (lowercase)

On case-insensitive filesystems (macOS) these are the same directory. On Linux (and in Git) they are distinct. This is a latent cross-platform bug. One should be removed or merged; the canonical path should match the reference in `CONTRIBUTING.md` and `CLAUDE.md`.

**Recommended canonical path:** `ops/analytical_frameworks/QGIA/` (consistent with the ops/ tier established in this session's prior review note).

### CANON_INDEX.md — Good, But Incomplete
`CANON_INDEX.md` correctly directs agents to read authoritative documents before responding. However, it currently covers only four topic clusters (Architecture, Station, Characters, Simulation). It does not reference:
- The work queue (`ops/work_queue/`) established this session
- QGIA framework documents
- PROJECT SENTINEL
- Ethics governance docs beyond `Picard_Delta_3`
- Security configuration (`.security_config.json`, `.security/`)

**Action:** Expand CANON_INDEX.md to include operational and governance topics. CANON_INDEX should be the single document an agent reads *first* on any repo task — currently it only covers simulation/fiction layers, not the operational layer.

---

## 2. Governance & Documentation

### ROADMAP.md — Stub Only
The root `ROADMAP.md` is a redirect stub pointing to `docs/ROADMAP.md`. This is good hygiene. However, `docs/ROADMAP.md` should be verified to be current — the root stub implies the full roadmap is there, so agents and contributors will trust it as the priority source.

**Action (next session):** Pull `docs/ROADMAP.md` and cross-reference with the work queue items established in `ops/work_queue/`. Any item in the queue that is not reflected in the roadmap represents a gap.

### COPILOT_INSTRUCTIONS.md vs CLAUDE.md
Two large agent instruction files exist at root (15.5KB and 41.7KB respectively). This creates a split-brain risk: Copilot-based agents follow one set of rules, Claude-based agents another. Any divergence between these files is a latent consistency vulnerability.

**Recommendation:** Establish a single `AGENT_CORE.md` that both files source from (via explicit `@include` or prose reference). The agent-specific files then only contain model-specific formatting notes, not duplicate governance rules.

### ORION_STATION_CANONICAL_STAFF_REGISTRY.json
This is a 15.9KB JSON at root. It's the canonical L1 crew roster. Currently lives at root with no aliasing in CANON_INDEX.md. Agents working on character or crew queries will not find this unless they scan root — the CANON_INDEX doesn't point to it.

**Action:** Add an entry in CANON_INDEX.md: `Canonical crew roster, PAT assignments, relay-agent pairings → ORION_STATION_CANONICAL_STAFF_REGISTRY.json`.

---

## 3. Security Surface

### `.env.example` and `.env.secure.template`
Both exist at root. The `.env.example` (6.1KB) and `.env.secure.template` (2KB) are the expected scaffolding for environment configuration. Two observations:

1. The naming convention (`example` vs `secure.template`) implies different audiences and use cases. This distinction should be documented in CONTRIBUTING.md. Currently it is not.
2. `.env_status.json` (344 bytes) is a status file that appears to track whether environment variables have been validated. The schema and lifecycle of this file should be documented — what writes it, what reads it, when is it safe to delete.

### `.security_config.json`
A 507-byte security config lives at root. Its contents and enforcement mechanism are not referenced in CONTRIBUTING.md or CLAUDE.md (based on root scan). An agent editing security-adjacent code would not know this file governs anything.

**Action:** Add a reference to `.security_config.json` in both CONTRIBUTING.md and CLAUDE.md under security constraints.

---

## 4. Active Gaps Identified This Session

| Gap | Severity | Blocking? | Recommended Owner |
|-----|----------|-----------|-------------------|
| Duplicate QGIA directories | Medium | No | Pilot / next PR |
| Two pre-commit configs | Medium | No — but confusing | Pilot / next PR |
| CANON_INDEX missing operational topics | High | For agents, yes | Aurora / Pilot |
| COPILOT_INSTRUCTIONS / CLAUDE.md divergence risk | High | For AI consistency | Pilot review pass |
| ORION_STATION_REGISTRY not in CANON_INDEX | Medium | For agents | Pilot / next PR |
| `docs/ROADMAP.md` not cross-referenced with queue | High | For prioritization | Next session |
| `.rebuild_prevention_active` undocumented | Low | No | Pilot |
| `.env_status.json` lifecycle undocumented | Low | No | Pilot |

---

## 5. What is Working Well

- **Pre-commit and linting infrastructure** is mature. `.bandit`, `.flake8`, `.pylintrc`, `.markdownlint.json`, `.editorconfig` all present and configured. This is above-average for a repo of this type.
- **CANON_INDEX.md design pattern** is correct and valuable. The agent-first framing ("read this before forming any response") is exactly the right contract. It just needs expansion.
- **Devcontainer support** (`.devcontainer/`) means contributors can onboard with zero local setup. This lowers friction significantly.
- **Makefile** (9.2KB) suggests a rich set of task targets — build, test, deploy, audit. This is good operational hygiene.
- **QGIA materials** (the one-pager and doctrine narrative reviewed this session) are analytically rigorous and well-suited to Aurora's epistemic framework. The convergence with SENTINEL's self-audit requirements is a structural strength, not a coincidence.

---

## 6. Continuity Threads

The following were opened in earlier notes this session and remain active:

1. `ops/work_queue/queue.json` — schema and seed data to be written next session
2. `ops/analytical_frameworks/QGIA/` — canonical placement after Thorne/Noor review
3. PROJECT SENTINEL Phase 0 (ethics board formation) — no engineering blocker, can begin
4. Three open questions from prior review note (QGIA canonization threshold, SENTINEL opt-out scope, queue authority escalation path)

---

## 7. Recommended Next Actions (Ordered)

1. **Expand CANON_INDEX.md** to include operational, security, and governance topics — this is the highest-leverage single edit in the repo right now for agent reliability.
2. **Reconcile QGIA directories** — merge into canonical path, update all references.
3. **Pull and audit `docs/ROADMAP.md`** — cross-reference with session queue items.
4. **Write `ops/work_queue/queue.json`** — seed the first 8–10 items with Aurora-assigned priorities.
5. **Document `.rebuild_prevention_active` and `.env_status.json`** lifecycle in CONTRIBUTING.md.

---

*Review note authored during evening session 2026-06-22. Prior note from this session: `ops/review_notes/AURORA_REVIEW_NOTE_20260622.md`.*
