#!/usr/bin/env python3
"""Reuse pending bot queue proposals and explicitly dispatch their validation.

GITHUB_TOKEN-created PR events require approval. workflow_dispatch can start
the existing CI jobs directly, without merging or weakening branch protection.
Only same-repository bot PRs with the expected generated-file scope qualify.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess  # nosec B404 — fixed gh argv; no shell or eval.
from pathlib import Path


POLICIES = {
    "ingestion": (
        r"queue/auto-ingest-\d{8}-\d{4}",
        {
            "ops/work_queue/queue.json",
            "ops/work_queue/QUEUE.md",
            "ops/work_queue/NEXT_UP.md",
            "ops/work_queue/OPEN_GATES.md",
        },
    ),
    "escalation": (
        r"queue/escalation-surfaced-\d{8}-\d{4}",
        {"ops/work_queue/gate_registry.json", "ops/work_queue/OPEN_GATES.md"},
    ),
}
WORKFLOWS = ("aurora-ci-minimal.yml", "queue-validation.yml")


def gh(*args: str) -> str:
    # Fixed CLI executable, argv only; credentials remain in gh's environment.
    return subprocess.run(  # nosec B603 B607
        ["gh", *args], check=True, capture_output=True, text=True
    ).stdout


def pages(endpoint: str) -> list[dict]:
    result = json.loads(gh("api", endpoint, "--paginate", "--slurp"))
    return [item for page in result for item in page]


def validate_proposal(pr: dict, repo: str) -> None:
    if (
        pr["state"] != "open"
        or pr["base"]["ref"] != "main"
        or pr["user"]["login"] != "github-actions[bot]"
        or (pr["head"].get("repo") or {}).get("full_name") != repo
        or not re.fullmatch(r"[0-9a-f]{40}", pr["head"]["sha"])
    ):
        raise ValueError(f"Untrusted queue proposal #{pr['number']}; operator review required")


def select_pending(prs: list[dict], kind: str, repo: str) -> dict | None:
    pattern, _ = POLICIES[kind]
    matching = [p for p in prs if re.fullmatch(pattern, p["head"]["ref"])]
    for pr in matching:
        validate_proposal(pr, repo)
    return max(matching, key=lambda p: p["number"], default=None)


def validate_files(files: list[dict], kind: str) -> None:
    _, allowed = POLICIES[kind]
    if not files or any(
        f["filename"] not in allowed or f["status"] not in {"modified", "added"}
        for f in files
    ):
        raise ValueError("Queue proposal changes files outside its generated-data scope")


def dispatch_checks(repo: str, pr: dict) -> None:
    sha, branch = pr["head"]["sha"], pr["head"]["ref"]
    for workflow in WORKFLOWS:
        result = json.loads(gh(
            "api", f"repos/{repo}/actions/workflows/{workflow}/runs"
            f"?head_sha={sha}&event=workflow_dispatch&per_page=100",
            "--paginate", "--slurp",
        ))
        runs = [
            run for page in result for run in page["workflow_runs"]
            if run["head_sha"] == sha and run["event"] == "workflow_dispatch"
        ]
        if runs:
            latest = max(runs, key=lambda r: r["id"])
            print(f"#{pr['number']} {workflow}: existing dispatch "
                  f"{latest['id']} ({latest.get('conclusion') or latest['status']}); "
                  "no automatic rerun")
            continue
        gh("workflow", "run", workflow, "--repo", repo, "--ref", branch)
        print(f"#{pr['number']} dispatched {workflow} on {sha}")


def escalation_marker(gate: dict) -> str:
    # Use the pre-apply registry baseline, which survives failed PR publication.
    cycle = [gate["gate_id"], gate.get("opened"), gate.get("last_surfaced")]
    digest = hashlib.sha256(json.dumps(cycle).encode()).hexdigest()
    return f"<!-- queue-escalation:{digest} -->"


def notify_gate(repo: str, gate: dict, threshold: int) -> None:
    issue = gate["github_issue"]
    if not isinstance(issue, int) or isinstance(issue, bool) or issue <= 0:
        raise ValueError("Escalation requires a positive GitHub issue number")
    endpoint = f"repos/{repo}/issues/{issue}"
    state = json.loads(gh("api", endpoint))["state"]
    if state != "open":
        print(f"Skipping {gate['gate_id']}: issue #{issue} is {state}")
        return
    marker = escalation_marker(gate)
    comments = pages(f"{endpoint}/comments?per_page=100")
    if any(c["user"]["login"] == "github-actions[bot]"
           and marker in (c.get("body") or "") for c in comments):
        print(f"Issue #{issue} already notified for {gate['gate_id']} at this baseline")
        return
    age = gate.get("days_since_surfaced")
    body = (
        f"⏰ **Decision-gate escalation** ({gate['gate_id']}, tier {gate['escalation_tier']}): "
        f"this gate has awaited an operator decision for "
        f"{age if age is not None else 'an unknown number of'} days "
        f"(threshold {threshold}).\n\n"
        f"Blocks: {', '.join(gate.get('blocks_queue_items') or []) or 'none recorded'}. "
        f"Owner: {gate.get('decision_owner') or 'operator'}.\n\n"
        "_Automated weekly escalation per #1131; the surfacing update is proposed "
        "through review. This marker prevents retry duplicates until the registry "
        f"baseline changes._\n\n{marker}"
    )
    gh("issue", "comment", str(issue), "--repo", repo, "--body", body)


def notify_escalations(repo: str, report: dict) -> None:
    for gate in report["escalations"]:
        if gate.get("github_issue") is not None:
            notify_gate(repo, gate, report["threshold_days"])
    for item in report["ungated_decisions"]:
        print(f"registry drift (reported in PR body): {item['id']} — {item['title']}")
    for gate in report.get("integrity_holds", []):
        print(f"integrity hold (reported in PR body): {gate['gate_id']} — "
              f"{gate.get('integrity_note') or gate['title']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=POLICIES, required=True)
    parser.add_argument("--notify-escalations", type=Path)
    args = parser.parse_args()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("GITHUB_REPOSITORY must identify the workflow repository")
    if args.notify_escalations:
        if args.kind != "escalation":
            raise ValueError("Issue notifications are only supported for escalation")
        notify_escalations(repo, json.loads(args.notify_escalations.read_text()))
        return 0
    prs = pages(f"repos/{repo}/pulls?state=open&base=main&per_page=100")
    pr = select_pending(prs, args.kind, repo)
    if pr:
        files = pages(f"repos/{repo}/pulls/{pr['number']}/files?per_page=100")
        validate_files(files, args.kind)
        dispatch_checks(repo, pr)
        print(f"Reuse pending proposal #{pr['number']}; defer new generation and issue pings.")
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a") as handle:
            handle.write(f"pending={'true' if pr else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
