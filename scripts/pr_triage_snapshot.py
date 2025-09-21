#!/usr/bin/env python3
"""
Quick PR triage snapshot for the current repo.

Usage:
  GITHUB_TOKEN=<token> python3 scripts/pr_triage_snapshot.py

Notes:
  - Token is optional for public repos, but recommended to avoid rate limits.
  - Set GITHUB_REPO explicitly (e.g., "AUo959/aurora-cloudbank-symbolic") if auto-detection fails.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from typing import Any, Dict, List


API = "https://api.github.com"


def http_get(url: str, token: str | None) -> Dict[str, Any]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "aurora-cloudbank-pr-triage/1.0")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except Exception as e:
        print(f"ERROR: GET {url} failed: {e}", file=sys.stderr)
        return {}


def get_repo() -> str:
    repo = os.environ.get("GITHUB_REPO")
    if repo:
        return repo
    # Attempt to detect from git config
    try:
        import subprocess

        url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True)
            .strip()
            .rstrip(".git")
        )
        # Expect https://github.com/owner/repo
        if url.startswith("https://github.com/"):
            return url.split("https://github.com/")[-1]
    except Exception:
        pass
    # Fallback to repo in question
    return "AUo959/aurora-cloudbank-symbolic"


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = get_repo()
    prs_url = f"{API}/repos/{repo}/pulls?state=open&per_page=100"
    data = http_get(prs_url, token)
    if not isinstance(data, list):
        print("No PR data returned. Provide GITHUB_TOKEN and ensure network access.")
        return 1

    # Summaries
    ready: List[Dict[str, Any]] = []
    drafts: List[Dict[str, Any]] = []
    others: List[Dict[str, Any]] = []

    for pr in sorted(data, key=lambda x: x.get("updated_at", ""), reverse=True):
        entry = {
            "number": pr["number"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "labels": [lbl["name"] for lbl in pr.get("labels", [])],
            "draft": pr.get("draft", False),
            "branch": f"{pr['head']['ref']} -> {pr['base']['ref']}",
            "updated": pr.get("updated_at"),
            "url": pr.get("html_url"),
        }
        if entry["draft"]:
            drafts.append(entry)
        elif "blocked" in entry["labels"]:
            others.append(entry)
        else:
            ready.append(entry)

    def fmt(items: List[Dict[str, Any]]) -> str:
        lines = []
        for e in items:
            labels = ",".join(e["labels"]) or "-"
            lines.append(
                f"#{e['number']} | {e['title']} | {e['author']} | {e['branch']} | labels: [{labels}] | {e['url']}"
            )
        return "\n".join(lines) or "(none)"

    print("Open PRs triage summary:\n")
    print("Ready for review/merge:")
    print(fmt(ready))
    print("\nDrafts:")
    print(fmt(drafts))
    print("\nBlocked/Other:")
    print(fmt(others))
    print("\nHint: export GITHUB_TOKEN for richer data and higher rate limits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
