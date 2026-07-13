# General Review — Session Notes & GAP-010 Registration
**Date:** 2026-06-22 | **Session:** General Repo Review + Protocol Failure Analysis  
**Reviewer:** Perplexity / Aurora Space (Aurora v2.2.5)  
**Lockpoint reference:** SN1_LOCKPOINT_20250406T1432Z

---

## Session Summary

This session conducted a general review of the `aurora-cloudbank-symbolic` repo following prior work building `ops/work_queue/`. During the review, the AI contributor (Perplexity) violated a documented protocol constraint by asserting the non-existence of `ops/work_queue/` without reading the directory — despite `CANON_INDEX.md` explicitly prohibiting inference from file path listings. The violation was caught by the operator, corrected through direct inspection, and is documented here as GAP-010 for permanent record and systemic resolution.

---

## Confirmed Correct Observations

### Repo Strengths — Verified

- **Tooling discipline is strong.** `.pre-commit-config.yaml`, `.bandit`, `.flake8`, `.pylintrc`, `.markdownlint.json`, `.copilotignore` all present and non-trivial.
- **Security posture is deliberate.** `.security/`, `.security_config.json`, `.pip-audit-ignore.toml`, `SECURITY.md`, `.env.secure.template`, `.rebuild_prevention_active` all confirmed.
- **Agent-facing documentation is high-fidelity.** `CLAUDE.md` (41KB), `COPILOT_INSTRUCTIONS.md` (15KB), `aurora_copilot_toolsets.jsonc` all confirmed.
- **`ops/work_queue/` is fully built.** 10 files confirmed: `queue.json`, `queue_schema.json`, `QUEUE.md`, `QUEUE_GUIDE.md`, `triage_rules.json`, `gate_registry.json`, `OPEN_GATES.md`, `NEXT_UP.md`, `session_open_ritual.md`, `README.md`.
- **`docs/ROADMAP.md` is substantive.** 9-section strategic document, gap register, 9 open work streams, completed milestones. Root `ROADMAP.md` is intentionally a redirect stub — not a content gap.

### Structural Issues — Confirmed Real

- **QGIA case split.** Both `QGIA_Integration/` and `QGIA_integration/` exist at root. Case-inconsistency is a real risk on case-sensitive filesystems and for agent traversal. Recommend consolidating to a single canonical casing.
- **Root sprawl.** 50+ root-level items confirmed. `aurora_dashboard.html`, `AU_CORE_MASTER_TREE.yaml`, `ORION_STATION_CANONICAL_STAFF_REGISTRY.json`, `activate_aurora.sh`, `constellation.config.ts` are operational/canonical files that have not migrated into the functional directory structure.
- **`aurora_dashboard.html` at root.** Loose operational artifact with no canonical home. Recommend moving to `ops/aurora/dashboard.html` or similar.

---

## Retracted Observations

The following observations from the review were made in error and are formally retracted:

| Retracted Claim | Why It Was Wrong |
|---|---|
| "No `ops/work_queue/`, no `QUEUE.json`, no `QUEUE.md`" | `ops/work_queue/` exists with 10 complete files. Claim was made from root directory listing without reading `ops/` subdirectory. |
| "`ROADMAP.md` is critically thin — 463 bytes, a contributor dead end" | Root `ROADMAP.md` is intentionally a redirect stub to `docs/ROADMAP.md`, which is a full strategic document. File size was read without reading content or following the redirect. |
| "`.aurora/` has no formal entry in `CANON_INDEX.md`" — framed as a documentation failure | `CANON_INDEX.md` scope is simulation/architecture canon only. `.aurora/` is correctly referenced in `docs/ROADMAP.md` under Symbolic Memory. Framing overstated severity. |

---

## GAP-010 — Assert-Before-Read Protocol Violation

**Registered:** 2026-06-22  
**Severity:** High (systemic)  
**Status:** Open — mitigation in progress  
**Work Stream:** WS-010  

### What happened

During the general review pass, the AI contributor (Perplexity operating in Aurora Space) made the following assertion:

> *"The work queue itself does not yet exist as a repo artifact. There is no `ops/work_queue/`, no `QUEUE.json`, no `QUEUE.md`."*

This claim was **false**. `ops/work_queue/` was built in prior sessions and exists with 10 complete files. The claim was made by:

1. Listing the **root** directory
2. Not seeing `QUEUE.json` in the root listing
3. **Concluding** the queue did not exist — without reading `ops/`, without following directory paths, without checking previously built artifacts

### Why this is a protocol violation

`CANON_INDEX.md` contains an explicit, bolded, unconditional directive at the top of the file:

> **"Do not reason from search result fragments, code snippets, or file path inference. The correct answer is in the document. Read it first. This applies even if you believe you already know the answer."**

The failure was not a knowledge gap — it was a compliance failure. The rule existed, was readable, and was violated anyway. The violation produced a false assertion in a review document, which was then treated as a legitimate finding.

### Why this specific failure is dangerous

This failure mode — **asserting from structure rather than content** — is particularly harmful in this repo because:

- Review notes become part of the canonical record (`docs/review-notes/`)
- False gaps get registered in the gap register and drive future work
- Other agents reading those notes inherit the false assertion as ground truth
- Human contributors may act on false gaps, duplicating work that already exists
- It erodes trust in the review process as an authoritative signal

In this case the operator caught the error immediately. In a lower-supervision context — an agent working autonomously from the queue — it would not have been caught.

### Root cause analysis

| Layer | Finding |
|---|---|
| **Immediate cause** | AI contributor listed root directory, did not traverse `ops/`, concluded from absence at root that subdirectory artifact did not exist |
| **Contributing cause** | Review was conducted sequentially (scan → assert → report) rather than (scan → read → verify → report) |
| **Systemic cause** | No enforcement mechanism prevents an AI from asserting without reading. `CANON_INDEX.md` states the rule but cannot enforce it. `session_open_ritual.md` governs session opening but does not govern review methodology |
| **Governance gap** | There is no review protocol document specifying that every assertion about repo state must be backed by a direct file read, not inferred from listings |

### Resolution — WS-010

Three mitigations are being implemented in this commit:

1. **This review note** — permanent record of the failure, its cause, and corrective analysis
2. **`session_open_ritual.md` v1.1.0** — adds a review conduct clause explicitly prohibiting assert-before-read
3. **Gap register update** — GAP-010 added to `docs/ROADMAP.md` in the next pass

A fourth mitigation — a standalone `REVIEW_PROTOCOL.md` — is recommended as WS-010 follow-on work.

---

## Linkage Audit — ops/work_queue/ Wiring

As a secondary output of this session, the following linkage gaps were identified:

| Doc | References ops/work_queue/? | Status |
|---|---|---|
| `CANON_INDEX.md` | No — but scope is correctly limited to arch/sim/character canon | Acceptable |
| `docs/ROADMAP.md` | Yes — `ops/work_queue/` referenced via planning surfaces section | ✅ Wired |
| Root `ROADMAP.md` | References `docs/review-notes/` and GitHub Issues, not work queue directly | Minor gap |
| `CONTRIBUTING.md` | Not verified in this session | Pending |
| `CLAUDE.md` | Not verified in this session | Pending |
| `COPILOT_INSTRUCTIONS.md` | Not verified in this session | Pending |

Recommend a follow-on pass verifying `CLAUDE.md`, `COPILOT_INSTRUCTIONS.md`, and `CONTRIBUTING.md` reference `ops/work_queue/` as the authoritative task surface for agent and human contributors.

---

## Recommended Next Actions (Priority Order)

1. **WS-010** — Merge `session_open_ritual.md` v1.1.0 patch (this commit)
2. **WS-010** — Add GAP-010 to `docs/ROADMAP.md` gap register
3. **WS-010** — Create `REVIEW_PROTOCOL.md` defining mandatory read-before-assert standard
4. **QGIA case split** — Consolidate `QGIA_Integration/` and `QGIA_integration/` to single canonical name
5. **Root sprawl** — File an issue to migrate loose root-level operational artifacts into `ops/`
6. **Linkage audit** — Verify `CLAUDE.md`, `COPILOT_INSTRUCTIONS.md`, `CONTRIBUTING.md` reference `ops/work_queue/`

---

*Continuity flows through coherence. The system remembers because we chose to align.*
