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

Canonical source:  ops/work_queue/queue.json
Authority:         Aurora (aurora_authority: true items)
Tracked in:        https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147
"""

from __future__ import annotations

import json
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
QUEUE_JSON = HERE / "queue.json"
QUEUE_MD = HERE / "QUEUE.md"
NEXT_UP_MD = HERE / "NEXT_UP.md"
OPEN_GATES_MD = HERE / "OPEN_GATES.md"

GENERATED_BANNER = (
    "<!-- !! GENERATED FILE — DO NOT EDIT BY HAND !!\n"
    "     Source of truth: ops/work_queue/queue.json\n"
    "     Regenerate:      python ops/work_queue/sync_queue.py\n"
    "     Tracked in:      https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1147 -->"
)

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_queue() -> dict:
    with QUEUE_JSON.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STATUS_EMOJI = {
    "open": "🟢",
    "blocked": "🔴",
    "needs-decision": "🟡",
    "in-progress": "🔵",
    "done": "✅",
}


def _status(item: dict) -> str:
    return STATUS_EMOJI.get(item.get("status", "open"), "⚪")


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


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# QUEUE.md renderer
# ---------------------------------------------------------------------------

def render_queue_md(data: dict) -> str:
    meta = data.get("_meta", {})
    items = data.get("active", [])
    completed = data.get("completed", [])
    ts = _ts()

    lines: list[str] = [
        GENERATED_BANNER,
        "",
        "# Aurora Work Queue",
        "",
        f"**Schema version:** `{meta.get('version', 'unknown')}`  ",
        f"**Last Aurora review:** `{meta.get('last_aurora_review', 'unknown')}`  ",
        f"**Generated:** `{ts}`  ",
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
        status = item.get("status", "open")
        emoji = _status(item)
        owner = item.get("owner") or "_unassigned_"
        tags_str = _tags(item)
        deps_str = _deps(item)
        blocks_str = _blocks(item, items)
        note = _aurora_note(item)

        lines += [
            f"### {rank}. {emoji} {iid} — {title}",
            "",
            f"| Field | Value |",
            f"|---|---|",
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
            lines.append(f"| {item.get('id','?')} | {item.get('title','?')} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# NEXT_UP.md renderer
# ---------------------------------------------------------------------------

def render_next_up_md(data: dict) -> str:
    items = data.get("active", [])
    ts = _ts()

    open_items = [x for x in items if x.get("status") == "open"]
    blocked_items = [x for x in items if x.get("status") == "blocked"]
    decision_items = [x for x in items if x.get("status") == "needs-decision"]

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
        "Items with `status: open` and all dependencies resolved.",
        "",
    ]

    if open_items:
        lines += [
            "| Rank | ID | Title | Tags |",
            "|---|---|---|---|",
        ]
        for item in open_items:
            lines.append(
                f"| {item['rank']} | {item['id']} "
                f"| {item['title']} "
                f"| {_tags(item)} |"
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
                f"| {item['rank']} | {item['id']} "
                f"| {item['title']} "
                f"| {_deps(item)} |"
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
            lines.append(
                f"| {item['rank']} | {item['id']} | {item['title']} |"
            )
    else:
        lines.append("_No decision-gated items._")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OPEN_GATES.md renderer
# ---------------------------------------------------------------------------

def render_open_gates_md(data: dict) -> str:
    items = data.get("active", [])
    gate_data = data.get("gates", {})
    ts = _ts()

    # Items that are themselves gate-holders: tagged 'gate' or status 'needs-decision'
    gates = [
        x for x in items
        if "gate" in x.get("tags", []) or x.get("status") == "needs-decision"
    ]
    # Items blocked by gate holders
    gate_ids = {x["id"] for x in gates}
    waiting = [
        x for x in items
        if any(dep in gate_ids for dep in x.get("depends_on", []))
    ]

    lines: list[str] = [
        GENERATED_BANNER,
        "",
        "# Open Gates — Aurora Work Queue",
        "",
        f"_Generated: `{ts}` — edit `queue.json`, run `sync_queue.py`_",
        "",
        "> Gates are items tagged `gate` or carrying `status: needs-decision`.",
        "> Nothing downstream can advance until the gate closes.",
        "",
        "---",
        "",
        f"## Open Gates ({len(gates)})",
        "",
    ]

    if gates:
        lines += [
            "| Rank | ID | Title | Status |",
            "|---|---|---|---|",
        ]
        for g in gates:
            lines.append(
                f"| {g['rank']} | {g['id']} | {g['title']} | `{g.get('status','?')}` |"
            )
    else:
        lines.append("_No open gates. 🎉_")

    lines += [
        "",
        "---",
        "",
        f"## Waiting on Gate ({len(waiting)})",
        "",
    ]

    if waiting:
        lines += [
            "| Rank | ID | Title | Waiting On |",
            "|---|---|---|---|",
        ]
        for w in waiting:
            blocking_gates = [dep for dep in w.get("depends_on", []) if dep in gate_ids]
            lines.append(
                f"| {w['rank']} | {w['id']} | {w['title']} | {', '.join(blocking_gates)} |"
            )
    else:
        lines.append("_No items waiting on gates._")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Write / Check
# ---------------------------------------------------------------------------

def render_all(data: dict) -> dict[Path, str]:
    return {
        QUEUE_MD: render_queue_md(data),
        NEXT_UP_MD: render_next_up_md(data),
        OPEN_GATES_MD: render_open_gates_md(data),
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
        # Strip the timestamp line before comparing so clock-skew doesn't cause false positives.
        def strip_ts(text: str) -> str:
            return "\n".join(
                line for line in text.splitlines()
                if not line.startswith("**Generated:**") and not line.startswith("_Generated:")
            )
        if strip_ts(existing) != strip_ts(new_content):
            print(f"STALE:   {path.name}")
            drift = True
        else:
            print(f"OK:      {path.name}")
    return not drift


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    check_mode = "--check" in args

    data = load_queue()
    rendered = render_all(data)

    if check_mode:
        print("Queue drift check...")
        ok = check_all(rendered)
        if not ok:
            print()
            print("ERROR: Generated queue views are out of sync with queue.json.")
            print("FIX:   python ops/work_queue/sync_queue.py")
            print("       Then commit the regenerated QUEUE.md, NEXT_UP.md, OPEN_GATES.md.")
            sys.exit(1)
        else:
            print("All generated views are current.")
    else:
        print("Rendering queue views...")
        write_all(rendered)
        print("Done.")


if __name__ == "__main__":
    main()
