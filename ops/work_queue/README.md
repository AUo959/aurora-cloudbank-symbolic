# ops/work_queue/

This directory is the **Aurora-managed work queue** for the `aurora-cloudbank-symbolic` repo.

## Files

| File | Purpose | Who reads it |
|---|---|---|
| `QUEUE.md` | Human-readable prioritized queue with Aurora annotations | Human contributors, code review |
| `queue.json` | Machine-readable mirror of the queue | Agents, LLMs, automation scripts |
| `README.md` | This file — orientation and protocol | Everyone on first read |

## Quick Start

### For human contributors

1. Open [`QUEUE.md`](./QUEUE.md).
2. Work on the highest-ranked `open` item with no unresolved `Depends On` entries.
3. Claim it by changing `Owner` to your GitHub handle and `Status` to `in-progress`.
4. When done, move it to the Completed table.

### For agents and LLMs working in this repo

1. Read `queue.json` first. It is the machine-readable source.
2. Pick the lowest `rank` item where `status == "open"` and all `depends_on` items are `"done"`.
3. Check the `aurora_note` field — this is Aurora's contextual override. Treat it as binding.
4. Before opening a PR, re-read the queue. Aurora may have re-ranked while you worked.
5. Update `owner` and `status` in `queue.json` **and** `QUEUE.md` as you work.

## Aurora's Role

Aurora holds **contextual authority** over this queue. This means:

- Aurora may re-rank items based on simulation state, ethics audit results, layer integrity, or cross-thread dependencies that are not visible in the GitHub issue list alone.
- Any commit with message prefix `aurora(queue):` should be treated as a canonical queue update.
- The `aurora_note` field is not a suggestion — it is the authoritative reason for the current rank.
- If Aurora's ranking conflicts with a GitHub milestone or label priority, Aurora's ranking wins for active work selection.

## Schema

See `queue.json` for the full field definitions. The required fields for each queue item are:

```json
{
  "rank": 1,
  "id": "#issue-number or internal-slug",
  "title": "Short description",
  "status": "open | in-progress | blocked | needs-decision | done",
  "owner": "github-handle or null",
  "depends_on": ["#id"],
  "tags": ["label"],
  "aurora_note": "Aurora's contextual reasoning for this item's rank and state.",
  "aurora_authority": true
}
```

## Sync Protocol

`QUEUE.md` and `queue.json` must stay in sync. When you update one, update the other in the same commit. A future `sync_queue.py` script will enforce this automatically (tracked in the queue as a meta-task).
