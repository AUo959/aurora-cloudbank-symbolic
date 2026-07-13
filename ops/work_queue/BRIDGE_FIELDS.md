# Aurora Queue Bridge Fields

**Status:** Active compatibility reference
**Tracked in:** #1161  
**Purpose:** Define non-breaking metadata that lets queue items coordinate with the ORIONCORE control-plane layer.

---

## Why this exists

The current queue data model can prioritize work, but future automation needs enough metadata to route an item through:

1. live GitHub refresh,
2. duplicate PR/branch checks,
3. platform routing,
4. session-claim or issue-broker preflight,
5. durable handoff when paused,
6. peer-review classification when the work is floor-touching.

Bridge fields should be additive. Existing renderers may ignore them until they are explicitly upgraded.

---

## Recommended bridge fields

| Field | Type | Required now? | Meaning |
|---|---:|---:|---|
| `github_issue` | integer or null | No | Numeric GitHub issue backing the queue item |
| `linked_prs` | array of integers | No | Known PRs implementing or reviewing the queue item |
| `preferred_platform` | string | No | `codex`, `claude-code`, `perplexity`, `human`, or `either` |
| `claim_required` | boolean | No | Whether mutation must run through claim/broker preflight |
| `claim_paths` | array of strings | No | Intended mutation paths for overlap checks |
| `session_state_ref` | string or null | No | Control-plane handoff id if active/suspended |
| `review_class` | string | No | Peer-review / risk class |
| `handoff_surface` | string | No | Durable handoff target, usually `catalog/session_state.json` |
| `coordination_notes` | string | No | Human-readable safety/routing note |
| `metrics_tags` | array of strings | No | Tags for metrics grouping |

---

## Example: docs-only queue item

```json
{
  "id": "#1139",
  "github_issue": 1139,
  "preferred_platform": "either",
  "claim_required": true,
  "claim_paths": ["docs/ethics/README.md"],
  "session_state_ref": null,
  "review_class": "documentation-significant",
  "handoff_surface": "catalog/session_state.json",
  "coordination_notes": "Refresh issue and check for existing ethics README PR before creating a branch.",
  "metrics_tags": ["docs", "ethics", "navigation"]
}
```

---

## Example: coordination-layer item

```json
{
  "id": "#1161",
  "github_issue": 1161,
  "linked_prs": [1166],
  "preferred_platform": "either",
  "claim_required": true,
  "claim_paths": [
    "ops/work_queue/CROSS_PLATFORM_COORDINATION.md",
    "ops/work_queue/QUEUE_GUIDE.md",
    "ops/work_queue/COORDINATION_METRICS.md"
  ],
  "session_state_ref": null,
  "review_class": "coordination-layer",
  "handoff_surface": "catalog/session_state.json",
  "coordination_notes": "Treat changes to queue/control-plane authority, claims, or review gates as coordination-layer floor work unless proven mechanical.",
  "metrics_tags": ["ops", "coordination", "queue"]
}
```

---

## Compatibility rule

Bridge fields must not change queue ordering, blocker semantics, or generated views until the renderer and schema explicitly support them.

A safe migration order is:

1. Document fields.
2. Add fields to representative queue entries.
3. Update schema to allow optional bridge fields.
4. Update renderer to display a compact bridge section only when useful.
5. Add read-only metrics collection.
6. Add CI enforcement only after generated output is deterministic.

Steps 1–3 and 5 are implemented. The legacy renderer intentionally ignores bridge fields, while the deterministic metrics report counts their adoption. Broader rendering or CI enforcement remains a separate compatibility decision.

---

## Safety rule

Bridge fields are evidence-routing metadata. They do not authorize mutation.

Before mutation, agents still need:

- live GitHub refresh,
- issue/PR overlap check,
- branch/worktree check,
- claim or broker preflight when paths are mutable,
- review classification for floor-touching changes,
- explicit merge authority before merging.
