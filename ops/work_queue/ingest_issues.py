#!/usr/bin/env python3
"""ingest_issues.py — auto-ingest labeled GitHub issues into the work queue.

Closes the "Sync script" roadmap item of issue #1131 (design decisions
recorded on that issue, 2026-07-17).

Usage:
    python ops/work_queue/ingest_issues.py --issues-file issues.json
    python ops/work_queue/ingest_issues.py --issues-file issues.json --dry-run

`issues.json` is a JSON array of GitHub issues as produced by:
    gh issue list --label blocking --label security --state open \
        --json number,title,labels,state

Authority contract (queue.json _meta: "Aurora holds contextual authority"):
- Ingested entries APPEND at the tail (max rank + 1, score-ordered among
  themselves) — existing rank order is never touched.
- Entries carry aurora_authority: false and an aurora_note marking them as
  awaiting Aurora triage; priority_score from triage_rules.json is advisory
  metadata for the rerank, not a rank driver.
- This script never commits: the CI workflow routes changes through a PR so
  queue-validation.yml (schema + view freshness) gates every ingestion.

Exit codes: 0 = no changes needed, 10 = queue updated (or would be, with
--dry-run), 1 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404 — used only for the sibling sync_queue.py render
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

HERE = Path(__file__).resolve().parent
QUEUE_JSON = HERE / "queue.json"
QUEUE_SCHEMA = HERE / "queue_schema.json"
TRIAGE_RULES = HERE / "triage_rules.json"
SYNC_QUEUE = HERE / "sync_queue.py"

# Roadmap scope (#1131): issues carrying either of these labels are queue
# candidates. Matches TR-01/TR-02 in triage_rules.json.
INGEST_LABELS = {"blocking", "security"}

_ISSUE_REF = re.compile(r"#(\d+)\b")


def _load(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def _labels(issue: Dict[str, Any]) -> Set[str]:
    raw = issue.get("labels", [])
    return {
        (label.get("name") if isinstance(label, dict) else str(label)).lower()
        for label in raw
    }


def known_issue_numbers(queue: Dict[str, Any]) -> Set[int]:
    """Issue numbers already represented anywhere in the queue.

    Sources: explicit github_issue fields, '#N' ids (the convention used by
    completed entries), and '#N' references inside ids/titles — so reruns
    are idempotent and completed work never re-enters."""
    known: Set[int] = set()
    for section in ("active", "completed"):
        for item in queue.get(section, []):
            gh = item.get("github_issue")
            if isinstance(gh, int):
                known.add(gh)
            for field in ("id", "title"):
                value = item.get(field)
                if isinstance(value, str):
                    known.update(int(m) for m in _ISSUE_REF.findall(value))
    return known


def score_issue(labels: Set[str], rules: List[Dict[str, Any]]) -> tuple[int, List[str]]:
    """Advisory priority score from the label-evaluable triage rules.

    Only TR-01/TR-02/TR-03 are computable from a raw GitHub issue; the
    queue-context rules (stale scope, decision_required, blocks/depends_on)
    apply after Aurora triage, not at ingestion."""
    predicates = {
        "TR-01": lambda ls: "blocking" in ls,
        "TR-02": lambda ls: bool(ls & {"security", "pentest"}),
        "TR-03": lambda ls: "architecture" in ls,
    }
    score = 0
    applied: List[str] = []
    for rule in rules:
        predicate = predicates.get(rule.get("id", ""))
        if predicate and predicate(labels):
            score += int(rule.get("score_delta", 0))
            applied.append(rule["id"])
    return score, applied


def _eligible(issue: Dict[str, Any], known: Set[int]) -> Optional[tuple[int, Set[str]]]:
    """(number, labels) when the issue qualifies for ingestion, else None."""
    if issue.get("state", "OPEN").upper() != "OPEN":
        return None
    number = issue.get("number")
    if not isinstance(number, int) or number in known:
        return None
    labels = _labels(issue)
    if not (labels & INGEST_LABELS):
        return None
    return number, labels


def build_entries(
    issues: List[Dict[str, Any]],
    queue: Dict[str, Any],
    rules: List[Dict[str, Any]],
    today: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Pure core: candidate issues -> new tail entries (may be empty)."""
    known = known_issue_numbers(queue)
    max_rank = max(
        (item.get("rank", 0) for item in queue.get("active", []) if isinstance(item.get("rank"), int)),
        default=0,
    )
    today = today or datetime.now(timezone.utc).date().isoformat()

    candidates = []
    for issue in issues:
        eligible = _eligible(issue, known)
        if eligible is None:
            continue
        number, labels = eligible
        score, applied = score_issue(labels, rules)
        candidates.append((score, number, issue, labels, applied))

    # Tail placement, score-ordered among the new entries only.
    candidates.sort(key=lambda c: (-c[0], c[1]))
    entries = []
    for offset, (score, number, issue, labels, applied) in enumerate(candidates, start=1):
        entries.append({
            "rank": max_rank + offset,
            "id": f"#{number}",
            "title": issue.get("title", f"GitHub issue #{number}"),
            "status": "open",
            "owner": None,
            "depends_on": [],
            "tags": sorted(labels),
            "github_issue": number,
            "priority_score": score,
            "priority_rules_applied": applied,
            "ingested": today,
            "aurora_note": (
                "auto-ingested from GitHub labels — awaiting Aurora triage; "
                "priority_score is advisory, rank is tail placement only"
            ),
            "aurora_authority": False,
        })
    return entries


def validate_queue(queue: Dict[str, Any]) -> None:
    import jsonschema

    schema = _load(QUEUE_SCHEMA)
    jsonschema.Draft7Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft7Validator(schema).iter_errors(queue),
        key=lambda e: list(e.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in errors[:5]
        )
        raise SystemExit(f"ERROR: ingestion would break queue_schema.json — {details}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--issues-file", required=True, type=Path,
                        help="JSON array of GitHub issues (gh issue list --json ...)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be ingested without writing")
    args = parser.parse_args()

    # Validate the user-supplied path before any filesystem access
    # (Sonar S8707): must be an existing regular .json file.
    issues_file = args.issues_file.resolve()
    if issues_file.suffix != ".json" or not issues_file.is_file():
        parser.error(f"--issues-file must be an existing .json file: {issues_file}")

    issues = _load(issues_file)
    queue = _load(QUEUE_JSON)
    rules = _load(TRIAGE_RULES).get("rules", [])

    entries = build_entries(issues, queue, rules)
    if not entries:
        print("No new labeled issues to ingest — queue unchanged.")
        return 0

    for entry in entries:
        print(f"ingest: rank {entry['rank']}  {entry['id']}  "
              f"score {entry['priority_score']} ({','.join(entry['priority_rules_applied'])})  "
              f"{entry['title'][:70]}")

    if args.dry_run:
        print(f"--dry-run: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} not written.")
        return 10

    queue["active"] = queue.get("active", []) + entries
    validate_queue(queue)
    QUEUE_JSON.write_text(json.dumps(queue, indent=2) + "\n")

    # Regenerate the views so the change is self-consistent under
    # queue-validation.yml's drift check.
    # Fixed argv: current interpreter + repo-constant script path — no
    # user-controlled input reaches the subprocess.
    subprocess.run([sys.executable, str(SYNC_QUEUE)], check=True)  # nosec B603
    print(f"Ingested {len(entries)} issue(s); views regenerated.")
    return 10


if __name__ == "__main__":
    sys.exit(main())
