# ops/work_queue

Aurora work-queue layer for `aurora-cloudbank-symbolic`.

Tracked in: [#1147](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147)

---

## Files

| File | Role | Edit? |
|---|---|---|
| `queue.json` | **Canonical source of truth** — machine-readable task list | ✅ Yes (via `aurora(queue):` commit) |
| `queue_schema.json` | JSON schema for `queue.json` | ✅ Yes (schema owner only) |
| `triage_rules.json` | Scoring weights and escalation triggers | ✅ Yes (Aurora / queue steward) |
| `gate_registry.json` | Named gate definitions | ✅ Yes (Aurora / queue steward) |
| `QUEUE_GUIDE.md` | Onboarding — how Aurora, agents, and humans use the queue | ✅ Yes |
| `CROSS_PLATFORM_COORDINATION.md` | Queue → broker/claim → GitHub → handoff contract | ✅ Yes |
| `BRIDGE_FIELDS.md` | Optional queue-to-control-plane metadata reference | ✅ Yes |
| `session_open_ritual.md` | Session-start checklist | ✅ Yes |
| `sync_queue.py` | Renderer / CI drift-checker | ✅ Yes (ops contributor) |
| `collect_coordination_metrics.py` | Read-only metrics collector / report checker | ✅ Yes (ops contributor) |
| `COORDINATION_METRICS.md` | 🚫 **GENERATED — DO NOT EDIT** | ❌ No |
| `QUEUE.md` | 🚫 **GENERATED — DO NOT EDIT** | ❌ No |
| `NEXT_UP.md` | 🚫 **GENERATED — DO NOT EDIT** | ❌ No |
| `OPEN_GATES.md` | 🚫 **GENERATED — DO NOT EDIT** | ❌ No |

---

## 🚫 Generated Files — Do Not Edit

`QUEUE.md`, `NEXT_UP.md`, `OPEN_GATES.md`, and `COORDINATION_METRICS.md` are **rendered projections** of `queue.json`.
They are generated automatically and must not be edited by hand.

**If you edit them directly:**
- Your changes will be silently overwritten the next time `sync_queue.py` runs.
- CI will flag the PR as failing the queue drift check.
- The queue loses its single-source-of-truth guarantee.

**To change what appears in these files, edit `queue.json` instead, then run:**

```bash
python ops/work_queue/sync_queue.py
git add ops/work_queue/QUEUE.md ops/work_queue/NEXT_UP.md ops/work_queue/OPEN_GATES.md
git commit -m "aurora(queue): regenerate views"
```

Regenerate or verify the deterministic metrics report with:

```bash
python ops/work_queue/collect_coordination_metrics.py --markdown > ops/work_queue/COORDINATION_METRICS.md
python ops/work_queue/collect_coordination_metrics.py --check
```

---

## Queue Authority Model

- **Canonical state:** `queue.json` — the only file agents and scripts read for task truth.
- **Computed views:** `QUEUE.md`, `NEXT_UP.md`, `OPEN_GATES.md` — rendered by `sync_queue.py`, verified by CI.
- **Aurora authority:** Items with `aurora_authority: true` may only have `rank` or `aurora_note` changed via a commit prefixed `aurora(queue):`.
- **Agent rules:** Agents may claim items with `status: open` and `depends_on: []`. Agents may not re-rank items, close gates, or edit generated views.
- **Human gates:** Items with `status: needs-decision` require a named human or governance decision before any work begins.

---

## CI Enforcement

[`.github/workflows/queue-validation.yml`](../../.github/workflows/queue-validation.yml) runs on every PR touching `ops/work_queue/**`.

It will **block merge** if:
- `queue.json` is not valid JSON.
- Any generated view (`QUEUE.md`, `NEXT_UP.md`, `OPEN_GATES.md`) is out of sync with `queue.json`.

To fix a failing check:
```bash
python ops/work_queue/sync_queue.py
git add ops/work_queue/QUEUE.md ops/work_queue/NEXT_UP.md ops/work_queue/OPEN_GATES.md
git commit -m "aurora(queue): regenerate views"
git push
```

---

## Commit Convention

Queue authority events must use the `aurora(queue):` prefix:

```
aurora(queue): re-rank #1140 above #1141 — topology contradiction is active blocker for QGIA
aurora(queue): add Q-new-item — docs/archive audit gap identified
aurora(queue): close #1148 — custody inventory complete, SHA verified
aurora(queue): regenerate views
```

This prefix makes queue deltas machine-readable for changelog generation and CI summaries, and is the traceable event surface for Aurora’s contextual authority.

---

_Authority: Aurora — `aurora_authority: true`_
