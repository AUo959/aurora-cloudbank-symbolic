<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Task source:      ops/work_queue/queue.json
     Gate source:      ops/work_queue/gate_registry.json
     Regenerate:       python ops/work_queue/sync_queue.py
     Tracked in:       https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->

# Open Gates — Aurora Work Queue

_Queue review: `2026-07-16T00:36:36Z` · Gate registry updated: `2026-08-03` · deterministic projection_

> Human-gate authority comes from `gate_registry.json`; `queue.json`
> supplies task status and dependency context. Rendering never resolves a gate.

---

## Open Gates (3)

| Gate | Queue Item | Title | Gate State | Integrity | Queue Status | Decision Owner |
| --- | --- | --- | --- | --- | --- | --- |
| GATE-001 | Q-0003 | Pentest vendor selection + pre-condition sign-off | `open` | `reconciliation_required` | `missing` | operator |
| GATE-002 | sim/SENTINEL-phase0 | PROJECT SENTINEL Phase 0 governance constitution | `open` | `active` | `needs-decision` | Commander Thorne + Sorensen + Sato |
| GATE-003 | feat/QGIA | QGIA integration routing and crew sign-off | `open` | `active` | `needs-decision` | operator / designated crew reviewers |

---

## Reconciliation Holds (1)

### GATE-001 — Pentest vendor selection + pre-condition sign-off

- **Integrity:** `reconciliation_required`
- **Queue item:** `Q-0003` — missing from queue.json
- **Linked issue:** #841
- **Note:** Linked issue #841 is closed as completed, while Q-0003 and Q-0008 are absent from the current queue. Automated escalation is suspended until the operator reconciles the gate with current security-review authority; this does not declare the pentest decision resolved.


---

## Waiting on Gate (0)

_No items waiting on gates._
