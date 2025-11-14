#!/usr/bin/env python3
"""
Generate a prioritized PR branch action list from BRANCH_CLEANUP_PLAN.md.

Outputs docs/operational/status/PR_CLEANUP_PRIORITY.md with three buckets:
- Rebase/Refresh PR (diverged)
- Merge or Close (behind)
- Close (Dependabot/Copilot obvious)
"""
from __future__ import annotations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLAN = REPO / "BRANCH_CLEANUP_PLAN.md"
OUT = REPO / "docs/operational/status/PR_CLEANUP_PRIORITY.md"


def parse_plan(md: str):
    rows = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) in [{"-"}, set()]:
            continue
        # | Branch | Ahead | Behind | Last Commit (UTC) | Category | Suggested Action |
        parts = [p.strip() for p in line.split("|")][1:-1]
        if len(parts) != 6:
            continue
        if parts[0] == "Branch":
            continue
        branch, ahead, behind, last, category, suggest = parts
        # skip the pseudo entry 'origin'
        if branch == "origin":
            continue
        try:
            ahead_i = int(ahead)
            behind_i = int(behind)
        except ValueError:
            ahead_i = 0
            behind_i = 0
        rows.append(
            {
                "branch": branch,
                "ahead": ahead_i,
                "behind": behind_i,
                "last": last,
                "category": category,
                "suggest": suggest,
            }
        )
    return rows


def prioritize(rows):
    close_obvious = []  # dependabot/*, copilot/fix-*
    rebase_refresh = []  # diverged
    merge_or_close = []  # behind
    ahead_only = []  # ahead (open/refresh PR)

    for r in rows:
        br = r["branch"]
        if br.startswith("dependabot/") or br.startswith("copilot/fix-"):
            close_obvious.append(r)
            continue
        cat = r["category"].lower()
        if cat == "diverged":
            rebase_refresh.append(r)
        elif cat == "behind":
            merge_or_close.append(r)
        elif cat == "ahead":
            ahead_only.append(r)

    # Sort within buckets (more behind/ahead first)
    rebase_refresh.sort(key=lambda x: (x["behind"], x["ahead"]), reverse=True)
    merge_or_close.sort(key=lambda x: (x["behind"], x["ahead"]), reverse=True)
    ahead_only.sort(key=lambda x: (x["ahead"], x["behind"]), reverse=True)
    close_obvious.sort(key=lambda x: (x["behind"], x["ahead"]), reverse=True)

    return rebase_refresh, merge_or_close, ahead_only, close_obvious


def render_md(buckets):
    rebase_refresh, merge_or_close, ahead_only, close_obvious = buckets
    lines = []
    lines.append("# PR Cleanup Priority (from Branch Cleanup Plan)\n")
    lines.append("Generated from BRANCH_CLEANUP_PLAN.md\n")
    lines.append("\n## Rebase/Refresh PR (diverged)\n")
    lines.extend(format_table(rebase_refresh))
    lines.append("\n## Merge or Close (behind)\n")
    lines.extend(format_table(merge_or_close))
    if ahead_only:
        lines.append("\n## Open/Refresh PR (ahead)\n")
        lines.extend(format_table(ahead_only))
    lines.append("\n## Close (Dependabot/Copilot obvious)\n")
    lines.extend(format_table(close_obvious))
    return "\n".join(lines) + "\n"


def format_table(rows):
    out = []
    out.append("| Branch | Ahead | Behind | Last Commit | Suggestion |")
    out.append("|--------|-------|--------|-------------|------------|")
    for r in rows:
        out.append(
            f"| {r['branch']} | {r['ahead']} | {r['behind']} | {r['last']} | {r['suggest']} |"
        )
    if len(rows) == 0:
        out.append("| (none) | 0 | 0 | - | - |")
    return out


def main():
    md = PLAN.read_text(encoding="utf-8") if PLAN.exists() else ""
    rows = parse_plan(md)
    buckets = prioritize(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render_md(buckets), encoding="utf-8")
    print("Wrote %s", OUT)


if __name__ == "__main__":
    main()
