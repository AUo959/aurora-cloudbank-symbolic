<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!
     Source of truth: ops/work_queue/queue.json
     Regenerate:      python ops/work_queue/sync_queue.py
     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->

# Open Gates — Aurora Work Queue

_Generated: `2026-06-23T22:43:00Z` — edit `queue.json`, run `sync_queue.py`_

> Gates are items tagged `gate` or carrying `status: needs-decision`.
> Nothing downstream can advance until the gate closes.

---

## Open Gates (3)

| Rank | ID | Title | Status |
|---|---|---|---|
| 7 | #1148 | Protocol custody inventory — machine-readable manifest of recovered package/file hashes and blockers | `open` |
| 24 | sim/SENTINEL-phase0 | PROJECT SENTINEL — Phase 0: Ethics review board constitution | `needs-decision` |
| 27 | feat/QGIA | QGIA integration hooks | `needs-decision` |

---

## Waiting on Gate (5)

| Rank | ID | Title | Waiting On |
|---|---|---|---|
| 8 | #1149 | Protocol JSON schemas — add schema files and validation tests for all five protocols | #1148 |
| 9 | #1150 | Protocol fixture intake — sanitized canonical examples for all five protocols | #1148 |
| 10 | #1151 | Runtime mapping design — map protocol decisions to EthicsEngine, ethics_gate, compliance monitor, geometric ethics | #1148 |
| 11 | #1152 | Moriarty containment tests — anomaly quarantine/review-only/rollback without L2-to-L1 bleed | #1148 |
| 12 | #1153 | Tribunal appeal tests — dispute/appeal record requirements without runtime enforcement | #1148 |
