#!/usr/bin/env python3
"""Reuse pending bot queue proposals and explicitly dispatch their validation.

GITHUB_TOKEN-created PR events require approval. workflow_dispatch can start
the existing CI jobs directly, without merging or weakening branch protection.
Only same-repository bot PRs with the expected generated-file scope qualify.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
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


def select_pending(prs: list[dict], kind: str, repo: str) -> dict | None:
    pattern, _ = POLICIES[kind]
    matching = [p for p in prs if re.fullmatch(pattern, p["head"]["ref"])]
    for pr in matching:
        if (
            pr["state"] != "open"
            or pr["base"]["ref"] != "main"
            or pr["user"]["login"] != "github-actions[bot]"
            or (pr["head"].get("repo") or {}).get("full_name") != repo
            or not re.fullmatch(r"[0-9a-f]{40}", pr["head"]["sha"])
        ):
            raise ValueError(f"Untrusted queue proposal #{pr['number']}; operator review required")
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=POLICIES, required=True)
    args = parser.parse_args()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("GITHUB_REPOSITORY must identify the workflow repository")
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
