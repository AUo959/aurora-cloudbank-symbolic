#!/usr/bin/env python3
"""Read-only Aurora work-queue coordination metrics collector.

This script reads local queue files and emits a small metrics packet or Markdown
report. It does not mutate queue state, create claims, call GitHub, edit
control-plane files, or touch runtime code.

Usage:
    python ops/work_queue/collect_coordination_metrics.py --json
    python ops/work_queue/collect_coordination_metrics.py --markdown
    python ops/work_queue/collect_coordination_metrics.py --github-state path/to/state.json --json

Optional GitHub state format:
{
  "issues": {
    "1161": {"state": "open"},
    "1147": {"state": "closed"}
  },
  "pulls": {
    "1162": {"state": "open", "merged": false}
  }
}
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
QUEUE_JSON = HERE / "queue.json"
SYNC_QUEUE = HERE / "sync_queue.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object at {path}")
    return payload


def queue_items(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    active = data.get("active", [])
    completed = data.get("completed", [])
    if not isinstance(active, list):
        raise ValueError("queue.json active must be a list")
    if not isinstance(completed, list):
        raise ValueError("queue.json completed must be a list")
    return active, completed


def item_status(item: dict[str, Any]) -> str:
    return str(item.get("status") or item.get("state") or "unknown")


def item_issue_number(item: dict[str, Any]) -> int | None:
    github_issue = item.get("github_issue")
    if isinstance(github_issue, int):
        return github_issue
    raw_id = str(item.get("id", ""))
    if raw_id.startswith("#") and raw_id[1:].isdigit():
        return int(raw_id[1:])
    return None


def generated_view_drift() -> dict[str, Any]:
    """Run sync_queue.py --check as a read-only generated-view drift probe."""
    if not SYNC_QUEUE.exists():
        return {"status": "blocked", "drift_count": None, "error": "sync_queue.py missing"}

    result = subprocess.run(
        [sys.executable, str(SYNC_QUEUE), "--check"],
        cwd=HERE.parent.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    stale = [line for line in result.stdout.splitlines() if line.startswith("STALE:")]
    missing = [line for line in result.stdout.splitlines() if line.startswith("MISSING:")]
    return {
        "status": "ok" if result.returncode == 0 else "drift",
        "returncode": result.returncode,
        "drift_count": len(stale) + len(missing),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def queue_drift(active: list[dict[str, Any]], completed: list[dict[str, Any]], github_state: dict[str, Any] | None) -> dict[str, Any]:
    if github_state is None:
        return {
            "status": "not_measured",
            "drift_count": None,
            "items": [],
            "note": "Provide --github-state to compare queue entries with issue/PR state.",
        }

    issues = github_state.get("issues", {}) if isinstance(github_state.get("issues", {}), dict) else {}
    drift_items: list[dict[str, Any]] = []

    for section_name, items in (("active", active), ("completed", completed)):
        for item in items:
            issue = item_issue_number(item)
            if issue is None:
                continue
            record = issues.get(str(issue)) or issues.get(issue)
            if not isinstance(record, dict):
                continue
            gh_state = str(record.get("state") or "unknown")
            q_status = item_status(item)
            if section_name == "active" and gh_state == "closed":
                drift_items.append(
                    {
                        "id": item.get("id"),
                        "section": section_name,
                        "queue_status": q_status,
                        "github_state": gh_state,
                        "finding": "closed_issue_still_active",
                    }
                )
            if section_name == "completed" and gh_state != "closed":
                drift_items.append(
                    {
                        "id": item.get("id"),
                        "section": section_name,
                        "queue_status": q_status,
                        "github_state": gh_state,
                        "finding": "completed_issue_not_closed",
                    }
                )

    return {"status": "measured", "drift_count": len(drift_items), "items": drift_items}


def collect(github_state_path: Path | None = None) -> dict[str, Any]:
    data = load_json(QUEUE_JSON)
    active, completed = queue_items(data)
    status_counts = Counter(item_status(item) for item in active)
    bridge_counts = Counter()

    for item in active:
        if "github_issue" in item or str(item.get("id", "")).startswith("#"):
            bridge_counts["github_linkable"] += 1
        if item.get("claim_required") is True:
            bridge_counts["claim_required"] += 1
        if item.get("preferred_platform"):
            bridge_counts["preferred_platform_set"] += 1
        if item.get("review_class"):
            bridge_counts["review_class_set"] += 1
        if item.get("claim_paths"):
            bridge_counts["claim_paths_set"] += 1

    github_state = load_json(github_state_path) if github_state_path else None
    view_probe = generated_view_drift()
    drift_probe = queue_drift(active, completed, github_state)

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "repo": "AUo959/aurora-cloudbank-symbolic",
        "queue_ref": "ops/work_queue/queue.json",
        "control_plane_ref": "AUo959/Aurora_ORIONCORE_Directory_Main/catalog/session_state.json",
        "metrics": {
            "active_count": len(active),
            "completed_count": len(completed),
            "status_counts": dict(sorted(status_counts.items())),
            "bridge_field_counts": dict(sorted(bridge_counts.items())),
            "queue_drift_count": drift_probe.get("drift_count"),
            "generated_view_drift_count": view_probe.get("drift_count"),
            "claim_conflict_count": None,
            "duplicate_pr_avoidance_count": None,
            "blocked_item_aging_count": None,
            "review_debt_age_days_max": None,
            "pr_cycle_time_days_median": None,
            "handoff_success_count": None,
            "ci_validation_success_rate": None,
        },
        "probes": {
            "queue_drift": drift_probe,
            "generated_view_drift": view_probe,
        },
        "observations": [
            "Collector is read-only and local-file based.",
            "GitHub issue/PR comparison requires an explicit --github-state export.",
            "Control-plane session-state and claim metrics are placeholders until cross-repo input is explicitly provided.",
        ],
        "blocked": [
            "No direct GitHub API calls are made by this script.",
            "No control-plane file is read unless future options explicitly pass a path.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# Aurora Dev Coordination Metrics Report",
        "",
        f"**Generated:** `{payload['generated_at']}`  ",
        f"**Repo:** `{payload['repo']}`  ",
        f"**Queue:** `{payload['queue_ref']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in metrics.items():
        if isinstance(value, dict):
            rendered = "`" + json.dumps(value, sort_keys=True) + "`"
        elif value is None:
            rendered = "_not measured_"
        else:
            rendered = f"`{value}`"
        lines.append(f"| {key} | {rendered} |")

    lines += ["", "## Observations", ""]
    for item in payload.get("observations", []):
        lines.append(f"- {item}")

    lines += ["", "## Blocked / not measured", ""]
    for item in payload.get("blocked", []):
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-state", type=Path, help="Optional JSON export of issue/PR state for drift comparison.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--json", action="store_true", help="Emit JSON metrics packet.")
    group.add_argument("--markdown", action="store_true", help="Emit Markdown report.")
    args = parser.parse_args()

    payload = collect(args.github_state)
    if args.markdown:
        print(render_markdown(payload), end="")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
