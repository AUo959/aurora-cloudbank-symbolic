# Aurora CloudBank Development Roadmap

**Status:** Active control-plane document  
**Last updated:** 2026-05-28  
**Owner surface:** repository maintainers, Codex agents, Aurora review sessions  
**Related intake queue:** [`docs/review-notes/`](review-notes/)  
**Execution queue:** [GitHub Issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)

This is the central, discoverable roadmap for current and upcoming Aurora CloudBank feature work. It is intentionally short enough to stay readable and explicit enough to steer agents, contributors, and outside reviews toward the same priorities.

Older roadmap and status documents remain useful as historical references, but this file is the current coordination surface.

---

## 1. Purpose

Aurora CloudBank is building toward a governed AI control plane: a modular runtime where memory, simulation, ethics, drift monitoring, audit logs, mesh communication, and developer tools can operate through clear API surfaces with traceable authority boundaries.

Roadmap work should therefore prioritize:

1. **Trustworthy operation** — tests, startup paths, secrets, and docs must fail closed or state uncertainty clearly.
2. **Usable vertical workflows** — existing modules should compose into coherent operator journeys.
3. **Governed extensibility** — new features must enter through documented intake, issue, and PR paths.

---

## 2. Canonical planning surfaces

| Surface | Path | Purpose | Update rule |
|---|---|---|---|
| Current roadmap | `docs/ROADMAP.md` | Central priority and sequencing document | Update when priorities, lanes, or issue status materially change |
| Review-note intake | `docs/review-notes/` | Persistent queue for outside reviews, session observations, architectural tensions, and risks | Add an entry before work becomes actionable, then triage to issue or direct fix |
| GitHub Issues | Repository issues | Execution queue for actionable work | Open only evidence-backed tasks with acceptance criteria |
| Runtime governance | `docs/api/API_CATALOG_GOVERNANCE.md`, `docs/api/api_surface_inventory.json`, `docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md` | API/runtime authority map | Update with API or service-surface changes |
| Path-drift ledger | `docs/architecture/RUNTIME_PATH_DRIFT_LEDGER.md` | Known stale/conflicting runtime claims | Update when a stale path is fixed, retired, or newly discovered |

---

## 3. Intake-to-roadmap workflow

Use this path for outside reviews, AI audits, architecture reviews, and session discoveries:

```text
outside/session review
  → docs/review-notes/entries/YYYYMMDD-short-slug.md
  → triage status: open | picked_up | issued | resolved | wont_fix
  → GitHub issue when actionable
  → roadmap lane when priority affects sequencing
  → implementation PR
  → update issue + review note + roadmap
```

Rules:

- Do not delete review notes. They are permanent audit records.
- Do not convert every observation directly into an issue. Preserve uncertain observations as review notes first.
- Open GitHub issues only when the evidence, risk, and acceptance criteria are clear.
- When a review note becomes an issue, update its frontmatter to `status: issued` and add `issue_url`.
- When a PR closes or materially changes a roadmap item, update this file in the same PR or a follow-up docs PR.

---

## 4. Current active lanes

### Lane A — Verification and trust hardening

**Goal:** make the repository's stated health match enforced checks.

| Issue | Title | Priority | Outcome sought |
|---|---|---:|---|
| [#758](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/758) | Harden CI gates so critical tests and quality checks fail closed | Critical | Mandatory tests fail workflows when critical runtime behavior regresses |
| [#760](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/760) | Reconcile README production and coverage claims with enforced verification | High | README assurance language matches real, reproducible verification |
| [#766](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/766) | Fail closed if Vercel build-phase placeholder secrets reach runtime | Critical | Placeholder secrets cannot silently reach runtime |

**Next feature impact:** no major expansion should rely on unverified production claims until this lane is complete or explicitly scoped.

---

### Lane B — Runtime entrypoint and API authority cleanup

**Goal:** make startup commands, API docs, and runtime authority consistent.

| Issue | Title | Priority | Outcome sought |
|---|---|---:|---|
| [#759](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/759) | Align startup and deployment commands with canonical FastAPI entrypoint | Critical | Operators launch the canonical runtime surface, not stale root scripts |
| [#763](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/763) | Regenerate or retire stale generated API catalog snapshots | High | Generated API docs are current or clearly historical |
| [#764](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/764) | Resolve Mesh Runtime V1 contract drift for `/api/mesh/agents` routes | High | Mesh contract is either implemented and tested or marked future/planned |

**Next feature impact:** new API surfaces should not be added until the inventory, generated docs, and drift ledger update process is followed.

---

### Lane C — Feature completion and capability honesty

**Goal:** convert partial or mock-backed surfaces into honest, testable capabilities.

| Issue | Title | Priority | Outcome sought |
|---|---|---:|---|
| [#761](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/761) | Replace or explicitly gate HR mock fallbacks and implement `OrganizationalIntelligence` | High | HR routes either use real implementations or return explicit degraded/mock status |
| [#762](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/762) | Implement or explicitly scope quantum simulator mixed-state operations | Medium | Mixed-state behavior is implemented or rejected through documented capability errors |
| [#765](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/765) | Fix Opal2 API decorators and add Opal2 syntax coverage | High | Opal2 route registration and syntax/import health are covered by tests |

**Next feature impact:** feature work should prefer finishing and testing these surfaces before starting large new modules.

---

### Lane D — Review-note intake and architecture references

**Goal:** keep outside/session review findings persistent, triageable, and discoverable.

| Review note | Status | Priority | Next step |
|---|---|---:|---|
| [`20260526-drift-threshold-stratification`](review-notes/entries/20260526-drift-threshold-stratification.md) | open | Medium | Promote stable drift-threshold reference and decide whether to open an issue |

**Next feature impact:** outside reviews should enter through `docs/review-notes/` before becoming issues unless the task is already fully actionable.

---

## 5. Feature-development direction

### Near-term product goal

Turn the existing module constellation into reliable operator workflows:

1. **Operator console / mission control** — health, drift, telemetry, audit, active agents, and warnings in one place.
2. **Simulation run lifecycle** — create scenario, run, stream progress, record result, audit ethics/drift, export receipt.
3. **Memory + ledger workflow** — store context, retrieve, inspect provenance, sign or record ledger entry.
4. **Mesh agent workflow** — inspect/register agents, send messages, view channel history, enforce L3 boundaries.
5. **Governance review workflow** — evaluate proposed action, allow/block/degrade, record rationale and lineage.

### Development posture

- Prefer vertical workflows over new isolated modules.
- Prefer explicit degraded states over mock success.
- Prefer small, issue-linked PRs over broad rewrites.
- Update roadmap, review-note status, and runtime governance docs as part of the change when affected.

---

## 6. Roadmap update triggers

Update this file when any of the following occurs:

- A new outside/session review identifies a gap that affects sequencing.
- A review note is promoted to a GitHub issue.
- A GitHub issue in an active lane is opened, closed, or materially re-scoped.
- A PR changes canonical startup paths, API surfaces, mesh contracts, security posture, or feature maturity.
- A new feature family is proposed.
- Historical roadmap claims are superseded by current repo evidence.

---

## 7. Historical roadmap references

These documents remain useful, but they are not the primary current coordination surface:

- [`docs/operational/reports/FEATURE_ROADMAP_STATUS.md`](operational/reports/FEATURE_ROADMAP_STATUS.md)
- [`docs/FEATURE_IMPLEMENTATION_ROADMAP_7PHASE.md`](FEATURE_IMPLEMENTATION_ROADMAP_7PHASE.md)
- [`docs/implementation/PHASED_IMPLEMENTATION_PLAN.md`](implementation/PHASED_IMPLEMENTATION_PLAN.md)
- [`docs/reports/STRATEGIC_ANALYSIS.md`](reports/STRATEGIC_ANALYSIS.md)
- [`docs/reports/STRATEGIC_VANTAGE_POINT.md`](reports/STRATEGIC_VANTAGE_POINT.md)

When these documents conflict with current runtime evidence or open issue status, prefer this roadmap plus the runtime governance docs.

---

*Built for consistency, clarity, and care.*
