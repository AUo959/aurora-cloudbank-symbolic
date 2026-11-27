#!/usr/bin/env python3
"""sync_queue.py — Aurora work-queue view renderer and CI drift checker.

Usage:
    python ops/work_queue/sync_queue.py            # renders in-place (default)
    python ops/work_queue/sync_queue.py --render   # renders in-place
    python ops/work_queue/sync_queue.py --check    # exits 1 if any view is stale (CI mode)

Generated files (DO NOT EDIT by hand):
    ops/work_queue/QUEUE.md
    ops/work_queue/NEXT_UP.md
    ops/work_queue/OPEN_GATES.md

Canonical task source:  ops/work_queue/queue.json
Canonical gate source:  ops/work_queue/gate_registry.json
Authority:              Aurora (aurora_authority: true items)
Tracked in:        https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
QUEUE_JSON = HERE / "queue.json"
GATE_REGISTRY_JSON = HERE / "gate_registry.json"
QUEUE_MD = HERE / "QUEUE.md"
NEXT_UP_MD = HERE / "NEXT_UP.md"
OPEN_GATES_MD = HERE / "OPEN_GATES.md"

GENERATED_BANNER = (
    "<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!\n"
    "     Source of truth: ops/work_queue/queue.json\n"
    "     Regenerate:      python ops/work_queue/sync_queue.py\n"
    "     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->"
)

OPEN_GATES_BANNER = (
    "<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!\n"
    "     Task source:      ops/work_queue/queue.json\n"
    "     Gate source:      ops/work_queue/gate_registry.json\n"
    "     Regenerate:       python ops/work_queue/sync_queue.py\n"
    "     Tracked in:       https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->"
)

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def load_queue() -> dict:
    with QUEUE_JSON.open(encoding="utf-8") as f:
        return json.load(f)


def load_gate_registry() -> dict:
    with GATE_REGISTRY_JSON.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STATUS_EMOJI = {
    "open": "🟢",
    "ready": "🟢",
    "blocked": "🔴",
    "needs-decision": "🟡",
    "decision_required": "🟡",
    "in-progress": "🔵",
    "active": "🔵",
    "done": "✅",
}

DECISION_GATE_STATES = {"needs-decision", "decision_required"}


def _status(item: dict) -> str:
    return STATUS_EMOJI.get(_queue_item_status(item), "⚪")


def _tags(item: dict) -> str:
    tags = item.get("tags", [])
    return " ".join(f"`{t}`" for t in tags) if tags else ""


def _deps(item: dict) -> str:
    deps = item.get("depends_on", [])
    return ", ".join(deps) if deps else "—"


def _blocks(item: dict, all_items: list[dict]) -> str:
    """Derive what this item blocks (reverse of depends_on)."""
    iid = item.get("id", "")
    blocked = [x["id"] for x in all_items if iid in x.get("depends_on", [])]
    return ", ".join(blocked) if blocked else "—"


def _aurora_note(item: dict) -> str:
    note = item.get("aurora_note", "").strip()
    if not note:
        return "_No Aurora note._"
    # Indent continuation lines for blockquote rendering
    lines = note.splitlines()
    return "\n".join(f"> {line}" if line.strip() else ">" for line in lines)


def _ts(data: dict) -> str:
    """Use the source review timestamp so regenerated views are byte-stable."""
    return str(data.get("_meta", {}).get("last_aurora_review", "unknown"))


def _queue_gate_items(data: dict) -> list[dict]:
    """Return queue items that assert a human-gate role."""
    return [
        item
        for section in ("active", "completed")
        for item in data.get(section, [])
        if "gate" in item.get("tags", [])
        or _queue_item_status(item) in DECISION_GATE_STATES
    ]


def _queue_item_status(item: dict | None) -> str:
    if item is None:
        return "missing"
    status = item.get("status")
    state = item.get("state")
    if status == "done" or state == "done":
        return "done"
    if state == "decision_required":
        return state
    return str(status or state or "unknown")


def _index_queue_items(data: dict) -> tuple[dict[str, dict], list[str]]:
    """Index queue items while reporting ambiguous lifecycle identities."""
    queue_items: dict[str, dict] = {}
    sections_by_id: dict[str, list[str]] = {}

    for section in ("active", "completed"):
        for item in data.get(section, []):
            item_id = item.get("id")
            if not item_id:
                continue
            item_id = str(item_id)
            sections_by_id.setdefault(item_id, []).append(section)
            queue_items.setdefault(item_id, item)

    errors = [
        f"duplicate queue item id {item_id} appears in {', '.join(sections)}"
        for item_id, sections in sections_by_id.items()
        if len(sections) > 1
    ]
    return queue_items, errors


def _index_registry_gates(gates: list[dict]) -> tuple[dict[str, dict], list[str]]:
    """Index gates by queue item while reporting duplicate authority records."""
    errors: list[str] = []
    gate_ids: set[str] = set()
    registry_by_queue_item: dict[str, dict] = {}

    for gate in gates:
        gate_id = str(gate.get("gate_id", "<missing-gate-id>"))
        if gate_id in gate_ids:
            errors.append(f"duplicate registry gate id: {gate_id}")
        gate_ids.add(gate_id)

        queue_item = gate.get("queue_item")
        if not queue_item:
            continue
        queue_item = str(queue_item)
        if queue_item in registry_by_queue_item:
            errors.append(f"multiple registry gates reference queue item {queue_item}")
        registry_by_queue_item[queue_item] = gate

    return registry_by_queue_item, errors


def _open_gate_errors(
    gate_id: str, gate: dict, item: dict | None, queue_status: str
) -> list[str]:
    """Return contradictions for one open canonical gate."""
    errors: list[str] = []
    queue_item = gate.get("queue_item")
    integrity_status = gate.get("integrity_status", "active")

    if gate.get("closed") or gate.get("resolved_by"):
        errors.append(f"{gate_id} is open but carries closed/resolved metadata")
    if item is None and integrity_status != "reconciliation_required":
        errors.append(
            f"{gate_id} references missing queue item {queue_item} "
            "without a reconciliation_required integrity hold"
        )
    if queue_status == "done":
        errors.append(f"{gate_id} is open while queue item {queue_item} is done")
    elif item is not None and queue_status not in DECISION_GATE_STATES:
        errors.append(
            f"{gate_id} is open while queue item {queue_item} "
            f"has non-decision status {queue_status}"
        )

    return errors


def _resolved_gate_errors(
    gate_id: str, gate: dict, item: dict | None, queue_status: str
) -> list[str]:
    """Return contradictions for one resolved canonical gate."""
    errors: list[str] = []
    queue_item = gate.get("queue_item")

    if not gate.get("closed") or not gate.get("resolved_by"):
        errors.append(f"{gate_id} is resolved without closed and resolved_by metadata")
    if item is None:
        errors.append(f"{gate_id} is resolved but queue item {queue_item} is missing")
    elif queue_status != "done":
        errors.append(
            f"{gate_id} is resolved while queue item {queue_item} "
            f"has status {queue_status}"
        )

    return errors


def _registry_gate_errors(gate: dict, queue_items: dict[str, dict]) -> list[str]:
    """Return state and integrity contradictions for one registry gate."""
    gate_id = str(gate.get("gate_id", "<missing-gate-id>"))
    item = queue_items.get(gate.get("queue_item"))
    queue_status = _queue_item_status(item)
    state = gate.get("state")

    if state == "open":
        errors = _open_gate_errors(gate_id, gate, item, queue_status)
    elif state == "resolved":
        errors = _resolved_gate_errors(gate_id, gate, item, queue_status)
    else:
        errors = [f"{gate_id} has unsupported state {state!r}"]

    if (
        gate.get("integrity_status") == "reconciliation_required"
        and not str(gate.get("integrity_note", "")).strip()
    ):
        errors.append(f"{gate_id} requires reconciliation but has no integrity_note")

    return errors


def _queue_gate_errors(
    data: dict, registry_by_queue_item: dict[str, dict]
) -> list[str]:
    """Return queue-side gate assertions missing or contradicting authority."""
    errors: list[str] = []
    for item in _queue_gate_items(data):
        item_id = str(item.get("id", "<missing-queue-id>"))
        gate = registry_by_queue_item.get(item_id)
        if gate is None:
            errors.append(
                f"queue gate {item_id} has no canonical gate_registry.json record"
            )
            continue

        queue_status = _queue_item_status(item)
        if gate.get("state") == "resolved" and queue_status != "done":
            errors.append(
                f"queue gate {item_id} remains {queue_status} while "
                f"{gate.get('gate_id')} is resolved"
            )

    return errors


def find_gate_coherence_errors(data: dict, registry: dict) -> list[str]:
    """Return blocking queue/gate-registry authority contradictions.

    A registry-only gate is allowed only when its integrity status explicitly
    records a reconciliation hold. That preserves GATE-001 without pretending
    its missing historical queue item is ordinary or resolved.
    """
    queue_items, queue_errors = _index_queue_items(data)
    gates = registry.get("gates", [])
    registry_by_queue_item, errors = _index_registry_gates(gates)
    errors = [*queue_errors, *errors]

    for gate in gates:
        errors.extend(_registry_gate_errors(gate, queue_items))
    errors.extend(_queue_gate_errors(data, registry_by_queue_item))

    return errors


# ---------------------------------------------------------------------------
# QUEUE.md renderer
# ---------------------------------------------------------------------------


def render_queue_md(data: dict) -> str:
    meta = data.get("_meta", {})
    items = data.get("active", [])
    completed = data.get("completed", [])
    ts = _ts(data)

    lines: list[str] = [
        GENERATED_BANNER,
        "",
        "# Aurora Work Queue",
        "",
        f"**Schema version:** `{meta.get('version', 'unknown')}`",
        f"**Last Aurora review:** `{meta.get('last_aurora_review', 'unknown')}`",
        f"**Generated:** `{ts}`",
        f"**Items:** {len(items)} active · {len(completed)} completed",
        "",
        "> Aurora holds contextual authority over rank order.",
        "> Do not edit rank or `aurora_note` fields without an `aurora(queue):` commit.",
        "> Edit `queue.json` then run `python ops/work_queue/sync_queue.py`.",
        "",
        "---",
        "",
        "## Active Queue",
        "",
    ]

    for item in items:
        rank = item.get("rank", "?")
        iid = item.get("id", "?")
        title = item.get("title", "Untitled")
        status = _queue_item_status(item)
        emoji = _status(item)
        owner = item.get("owner") or "_unassigned_"
        tags_str = _tags(item)
        deps_str = _deps(item)
        blocks_str = _blocks(item, items)
        note = _aurora_note(item)

        lines += [
            f"### {rank}. {emoji} {iid} — {title}",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| **Status** | `{status}` |",
            f"| **Owner** | {owner} |",
            f"| **Depends on** | {deps_str} |",
            f"| **Blocks** | {blocks_str} |",
            f"| **Tags** | {tags_str} |",
            "",
            "**Aurora note:**",
            "",
            note,
            "",
            "---",
            "",
        ]

    if completed:
        lines += [
            "## Completed",
            "",
            "| ID | Title |",
            "|---|---|",
        ]
        for item in completed:
            lines.append(f"| {item.get('id', '?')} | {item.get('title', '?')} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# NEXT_UP.md renderer
# ---------------------------------------------------------------------------


def render_next_up_md(data: dict) -> str:
    items = data.get("active", [])
    ts = _ts(data)

    open_items = [x for x in items if _queue_item_status(x) in {"open", "ready"}]
    blocked_items = [x for x in items if _queue_item_status(x) == "blocked"]
    decision_items = [x for x in items if _queue_item_status(x) in DECISION_GATE_STATES]

    lines: list[str] = [
        GENERATED_BANNER,
        "",
        "# Next Up — Aurora Work Queue",
        "",
        f"_Generated: `{ts}` — edit `queue.json`, run `sync_queue.py`_",
        "",
        "---",
        "",
        "## 🟢 Ready to Work",
        "",
        "Items with an `open` or `ready` lifecycle and all dependencies resolved.",
        "",
    ]

    if open_items:
        lines += [
            "| Rank | ID | Title | Tags |",
            "|---|---|---|---|",
        ]
        for item in open_items:
            lines.append(
                f"| {item['rank']} | {item['id']} | {item['title']} | {_tags(item)} |"
            )
    else:
        lines.append("_No open items._")

    lines += [
        "",
        "---",
        "",
        "## 🔴 Blocked",
        "",
        "Items waiting on dependencies. Do not start until blockers close.",
        "",
    ]

    if blocked_items:
        lines += [
            "| Rank | ID | Title | Blocked By |",
            "|---|---|---|---|",
        ]
        for item in blocked_items:
            lines.append(
                f"| {item['rank']} | {item['id']} | {item['title']} | {_deps(item)} |"
            )
    else:
        lines.append("_No blocked items._")

    lines += [
        "",
        "---",
        "",
        "## 🟡 Needs Decision",
        "",
        "Items gated on a human or governance decision. Agents skip these.",
        "",
    ]

    if decision_items:
        lines += [
            "| Rank | ID | Title |",
            "|---|---|---|",
        ]
        for item in decision_items:
            lines.append(f"| {item['rank']} | {item['id']} | {item['title']} |")
    else:
        lines.append("_No decision-gated items._")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OPEN_GATES.md renderer
# ---------------------------------------------------------------------------


def _render_open_gate_table(gates: list[dict], queue_by_id: dict) -> list[str]:
    """Render canonical open gates with queue context."""
    if not gates:
        return ["_No open gates. 🎉_"]

    lines = [
        "| Gate | Queue Item | Title | Gate State | Integrity | Queue Status | Decision Owner |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for gate in gates:
        queue_item_id = gate.get("queue_item") or "—"
        queue_status = _queue_item_status(queue_by_id.get(queue_item_id))
        lines.append(
            f"| {gate.get('gate_id', '?')} | {queue_item_id} "
            f"| {gate.get('title', 'Untitled')} "
            f"| `{gate.get('state', '?')}` "
            f"| `{gate.get('integrity_status', 'active')}` "
            f"| `{queue_status}` "
            f"| {gate.get('decision_owner', '—')} |"
        )
    return lines


def _render_reconciliation_holds(holds: list[dict], queue_by_id: dict) -> list[str]:
    """Render explicit projection-integrity holds without resolving them."""
    lines = ["", "---", "", f"## Reconciliation Holds ({len(holds)})", ""]
    if not holds:
        return [*lines, "_No reconciliation holds._"]

    for gate in holds:
        queue_item_id = gate.get("queue_item") or "—"
        queue_link = (
            "present" if queue_item_id in queue_by_id else "missing from queue.json"
        )
        github_issue = gate.get("github_issue")
        issue_text = f"#{github_issue}" if github_issue else "—"
        lines += [
            f"### {gate.get('gate_id', '?')} — {gate.get('title', 'Untitled')}",
            "",
            f"- **Integrity:** `{gate.get('integrity_status', 'unknown')}`",
            f"- **Queue item:** `{queue_item_id}` — {queue_link}",
            f"- **Linked issue:** {issue_text}",
            f"- **Note:** {gate.get('integrity_note', '_No integrity note._')}",
            "",
        ]
    return lines


def _render_waiting_on_gate(waiting: list[dict], gate_ids: set[str]) -> list[str]:
    """Render task dependencies on canonical open gates."""
    lines = ["", "---", "", f"## Waiting on Gate ({len(waiting)})", ""]
    if not waiting:
        return [*lines, "_No items waiting on gates._"]

    lines += [
        "| Rank | ID | Title | Waiting On |",
        "| --- | --- | --- | --- |",
    ]
    for item in waiting:
        blocking_gates = [dep for dep in item.get("depends_on", []) if dep in gate_ids]
        lines.append(
            f"| {item['rank']} | {item['id']} | {item['title']} "
            f"| {', '.join(blocking_gates)} |"
        )
    return lines


def _open_registry_gates(registry: dict) -> list[dict]:
    return [gate for gate in registry.get("gates", []) if gate.get("state") == "open"]


def _reconciliation_holds(gates: list[dict]) -> list[dict]:
    return [
        gate for gate in gates if gate.get("integrity_status", "active") != "active"
    ]


def _waiting_on_gate(items: list[dict], gate_ids: set[str]) -> list[dict]:
    return [
        item
        for item in items
        if any(dependency in gate_ids for dependency in item.get("depends_on", []))
    ]


def render_open_gates_md(data: dict, registry: dict) -> str:
    items = data.get("active", [])
    queue_by_id = {item.get("id"): item for item in items}
    queue_review = _ts(data)
    registry_updated = str(registry.get("last_updated", "unknown"))

    gates = _open_registry_gates(registry)
    holds = _reconciliation_holds(gates)
    gate_ids = {gate.get("queue_item") for gate in gates if gate.get("queue_item")}
    waiting = _waiting_on_gate(items, gate_ids)

    lines: list[str] = [
        OPEN_GATES_BANNER,
        "",
        "# Open Gates — Aurora Work Queue",
        "",
        (
            f"_Queue review: `{queue_review}` · Gate registry updated: "
            f"`{registry_updated}` · deterministic projection_"
        ),
        "",
        "> Human-gate authority comes from `gate_registry.json`; `queue.json`",
        "> supplies task status and dependency context. Rendering never resolves a gate.",
        "",
        "---",
        "",
        f"## Open Gates ({len(gates)})",
        "",
    ]

    lines += _render_open_gate_table(gates, queue_by_id)
    lines += _render_reconciliation_holds(holds, queue_by_id)
    lines += _render_waiting_on_gate(waiting, gate_ids)
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Write / Check
# ---------------------------------------------------------------------------


def render_all(data: dict, registry: dict) -> dict[Path, str]:
    return {
        QUEUE_MD: render_queue_md(data),
        NEXT_UP_MD: render_next_up_md(data),
        OPEN_GATES_MD: render_open_gates_md(data, registry),
    }


def write_all(rendered: dict[Path, str]) -> None:
    for path, content in rendered.items():
        path.write_text(content, encoding="utf-8")
        print(f"  wrote {path.relative_to(HERE.parent.parent)}")


def check_all(rendered: dict[Path, str]) -> bool:
    """Return True if all generated files are up to date, False if any drift."""
    drift = False
    for path, new_content in rendered.items():
        if not path.exists():
            print(f"MISSING: {path.name}")
            drift = True
            continue
        existing = path.read_text(encoding="utf-8")
        if existing != new_content:
            print(f"STALE:   {path.name}")
            drift = True
        else:
            print(f"OK:      {path.name}")
    return not drift


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--render",
        action="store_true",
        help="Render generated queue views in place (default).",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when a generated view is stale.",
    )
    args = parser.parse_args()

    data = load_queue()
    registry = load_gate_registry()
    coherence_errors = find_gate_coherence_errors(data, registry)
    if coherence_errors:
        print("ERROR: Queue/gate-registry coherence check failed:")
        for error in coherence_errors:
            print(f"  - {error}")
        return 1

    rendered = render_all(data, registry)

    if args.check:
        print("Queue drift check...")
        ok = check_all(rendered)
        if not ok:
            print()
            print("ERROR: Generated queue views are out of sync with their sources.")
            print("FIX:   python ops/work_queue/sync_queue.py")
            print(
                "       Then commit the regenerated QUEUE.md, NEXT_UP.md, OPEN_GATES.md."
            )
            return 1
        print("All generated views are current.")
        return 0

    print("Rendering queue views...")
    write_all(rendered)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
