#!/usr/bin/env python3
"""
Aurora CloudBank - Safe Branch Cleanup Script

Analyzes all remote branches, cross-references with GitHub PR status,
categorizes them by safety level, and supports dry-run + execute modes.

Usage:
    python scripts/safe_branch_cleanup.py                    # Dry-run analysis
    python scripts/safe_branch_cleanup.py --execute          # Delete safe-to-remove branches
    python scripts/safe_branch_cleanup.py --report-only      # Generate report without prompts
    python scripts/safe_branch_cleanup.py --stale-days 60    # Custom staleness threshold

Requires:
    - git CLI with access to the repository
    - GITHUB_TOKEN env var for GitHub API (optional, enables PR cross-referencing)
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger("safe_branch_cleanup")

PROTECTED_BRANCHES = {"main", "master", "develop", "HEAD"}

# Branches matching these prefixes with closed/unmerged PRs are safe to delete
STALE_PREFIXES = [
    "alert-autofix-",
    "dependabot/",
    "imgbot",
    "codex/",
]

# Branches from AI assistants that are typically ephemeral
EPHEMERAL_PREFIXES = [
    "copilot/sub-pr-",
    "copilot/fix-",
    "copilot/start-work-on-pr-",
    "copilot/finish-todos-on-pr-",
    "claude/",
]


def run_git(args: List[str], cwd: str = ".") -> str:
    """Run a git command and return stdout."""
    cmd = ["git", "--no-pager"] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd, check=False
    )
    if result.returncode != 0 and "not a git repository" in result.stderr:
        logger.error("Not a git repository: %s", cwd)
        sys.exit(1)
    return result.stdout.strip()


def fetch_and_prune(cwd: str = ".") -> None:
    """Fetch latest remote state and prune deleted branches."""
    logger.info("Fetching latest remote state...")
    subprocess.run(
        ["git", "fetch", "origin", "--prune"],
        capture_output=True, text=True, cwd=cwd, check=False,
    )


def get_remote_branches(cwd: str = ".") -> List[str]:
    """Get all remote branch names (without origin/ prefix)."""
    output = run_git(
        ["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/"],
        cwd=cwd,
    )
    branches = []
    for line in output.splitlines():
        name = line.strip()
        if not name:
            continue
        # Strip origin/ prefix
        if name.startswith("origin/"):
            name = name[len("origin/"):]
        if name == "HEAD" or not name or name == "origin":
            continue
        branches.append(name)
    return branches


def get_branch_details(branch: str, cwd: str = ".") -> Dict[str, Any]:
    """Get detailed info about a branch relative to main."""
    ref = f"origin/{branch}"

    # Last commit date and author
    log_output = run_git(
        ["log", "-1", "--format=%cI|%an|%s", ref], cwd=cwd
    )
    parts = log_output.split("|", 2)
    commit_date_str = parts[0] if parts else ""
    author = parts[1] if len(parts) > 1 else "Unknown"
    subject = parts[2] if len(parts) > 2 else ""

    # Parse commit date
    days_old = 0
    commit_date = None
    if commit_date_str:
        try:
            commit_date = datetime.fromisoformat(commit_date_str.strip())
            if commit_date.tzinfo is None:
                commit_date = commit_date.replace(tzinfo=timezone.utc)
            days_old = (datetime.now(timezone.utc) - commit_date).days
        except (ValueError, TypeError):
            pass

    # Ahead/behind relative to main
    ahead_behind = run_git(
        ["rev-list", "--left-right", "--count", f"origin/main...{ref}"],
        cwd=cwd,
    )
    behind, ahead = 0, 0
    ab_parts = ahead_behind.split()
    if len(ab_parts) == 2:
        try:
            behind = int(ab_parts[0])
            ahead = int(ab_parts[1])
        except ValueError:
            pass

    # Check if fully merged into main
    merged_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ref, "origin/main"],
        capture_output=True, cwd=cwd, check=False,
    )
    is_merged = merged_check.returncode == 0

    return {
        "name": branch,
        "commit_date": commit_date_str.strip() if commit_date_str else "Unknown",
        "author": author,
        "subject": subject[:80],
        "days_old": days_old,
        "ahead": ahead,
        "behind": behind,
        "is_merged": is_merged,
    }


def fetch_github_prs(
    owner: str, repo: str, token: Optional[str] = None
) -> Dict[str, List[Dict]]:
    """Fetch PR info from GitHub API, keyed by head branch name."""
    branch_prs: Dict[str, List[Dict]] = {}
    page = 1
    per_page = 100

    while True:
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/pulls"
            f"?state=all&per_page={per_page}&page={page}"
        )
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as resp:
                prs = json.loads(resp.read().decode())
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            logger.warning("GitHub API request failed (page %d): %s", page, exc)
            break

        if not prs:
            break

        for pr in prs:
            head_ref = pr.get("head", {}).get("ref", "")
            if not head_ref:
                continue
            entry = {
                "number": pr["number"],
                "state": pr["state"],
                "merged": bool(pr.get("merged_at")),
                "title": pr.get("title", "")[:80],
            }
            branch_prs.setdefault(head_ref, []).append(entry)

        page += 1
        if len(prs) < per_page:
            break

    return branch_prs


def categorize_branches(
    branches: List[Dict[str, Any]],
    branch_prs: Dict[str, List[Dict]],
    stale_days: int = 30,
) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize branches into cleanup groups."""
    categories: Dict[str, List[Dict[str, Any]]] = {
        "protected": [],
        "active_prs": [],
        "merged_safe_delete": [],
        "closed_pr_safe_delete": [],
        "stale_no_pr": [],
        "review_needed": [],
    }

    for branch in branches:
        name = branch["name"]

        # Protected branches
        if name in PROTECTED_BRANCHES:
            categories["protected"].append(branch)
            continue

        prs = branch_prs.get(name, [])
        has_open_pr = any(p["state"] == "open" for p in prs)
        has_merged_pr = any(p["merged"] for p in prs)
        has_closed_unmerged_pr = any(
            p["state"] == "closed" and not p["merged"] for p in prs
        )

        # Annotate branch with PR info
        branch["prs"] = prs

        # 1. Active open PRs – keep
        if has_open_pr:
            categories["active_prs"].append(branch)
            continue

        # 2. Fully merged into main (git ancestor check)
        if branch["is_merged"]:
            categories["merged_safe_delete"].append(branch)
            continue

        # 3. PR was merged (squash-merge won't show as ancestor)
        if has_merged_pr:
            categories["merged_safe_delete"].append(branch)
            continue

        # 4. PR was closed without merge – safe to delete
        if has_closed_unmerged_pr and not has_open_pr:
            categories["closed_pr_safe_delete"].append(branch)
            continue

        # 5. No PR at all and stale
        if not prs and branch["days_old"] > stale_days:
            # Check if it's an ephemeral prefix branch
            is_ephemeral = any(
                name.startswith(p) for p in STALE_PREFIXES + EPHEMERAL_PREFIXES
            )
            if is_ephemeral:
                categories["stale_no_pr"].append(branch)
            else:
                categories["review_needed"].append(branch)
            continue

        # 6. Everything else needs review
        categories["review_needed"].append(branch)

    return categories


def generate_report(
    categories: Dict[str, List[Dict[str, Any]]]
) -> str:
    """Generate a markdown cleanup report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = sum(len(v) for v in categories.values())

    safe_count = (
        len(categories["merged_safe_delete"])
        + len(categories["closed_pr_safe_delete"])
        + len(categories["stale_no_pr"])
    )

    lines = [
        "# 🧹 Branch Cleanup Analysis",
        f"**Generated:** {now}",
        f"**Total Remote Branches Analyzed:** {total}",
        f"**Safe to Delete:** {safe_count}",
        f"**Active (keep):** {len(categories['protected']) + len(categories['active_prs'])}",
        f"**Needs Review:** {len(categories['review_needed'])}",
        "",
        "---",
        "",
    ]

    def _branch_table(branch_list: List[Dict[str, Any]]) -> List[str]:
        if not branch_list:
            return ["_None_", ""]
        rows = [
            "| Branch | Age (days) | Ahead | Behind | PR Info |",
            "|--------|-----------|-------|--------|---------|",
        ]
        for b in sorted(branch_list, key=lambda x: x["days_old"], reverse=True):
            pr_info = ""
            for p in b.get("prs", []):
                status = (
                    "merged" if p["merged"]
                    else ("open" if p["state"] == "open" else "closed")
                )
                pr_info += f"#{p['number']} ({status}) "
            if not pr_info:
                pr_info = "—"
            rows.append(
                f"| `{b['name']}` | {b['days_old']} | {b['ahead']} | {b['behind']} | {pr_info.strip()} |"
            )
        rows.append("")
        return rows

    # Protected
    lines.append("## 🔒 Protected (keep)")
    lines.extend(_branch_table(categories["protected"]))

    # Active PRs
    lines.append("## 🟢 Active Open PRs (keep)")
    lines.extend(_branch_table(categories["active_prs"]))

    # Merged – safe to delete
    lines.append("## ✅ Merged / Squash-Merged (safe to delete)")
    lines.extend(_branch_table(categories["merged_safe_delete"]))

    # Closed unmerged PRs – safe to delete
    lines.append("## 🟡 Closed PRs (never merged — safe to delete)")
    lines.extend(_branch_table(categories["closed_pr_safe_delete"]))

    # Stale with no PR
    lines.append("## 🔴 Stale with No PR (safe to delete)")
    lines.extend(_branch_table(categories["stale_no_pr"]))

    # Review needed
    lines.append("## ⚠️ Needs Manual Review")
    lines.extend(_branch_table(categories["review_needed"]))

    # Cleanup commands
    safe_branches = (
        categories["merged_safe_delete"]
        + categories["closed_pr_safe_delete"]
        + categories["stale_no_pr"]
    )
    if safe_branches:
        lines.append("---")
        lines.append("")
        lines.append("## 🚀 Cleanup Commands")
        lines.append("")
        lines.append("```bash")
        lines.append("# Delete all safe-to-remove branches")
        for b in sorted(safe_branches, key=lambda x: x["name"]):
            lines.append(f"git push origin --delete {b['name']}")
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def delete_branches(
    branches: List[Dict[str, Any]], cwd: str = "."
) -> Dict[str, List[str]]:
    """Delete remote branches. Returns dict of deleted and failed branch names."""
    results: Dict[str, List[str]] = {"deleted": [], "failed": []}
    for branch in branches:
        name = branch["name"]
        logger.info("Deleting origin/%s ...", name)
        result = subprocess.run(
            ["git", "push", "origin", "--delete", name],
            capture_output=True, text=True, cwd=cwd, check=False,
        )
        if result.returncode == 0:
            results["deleted"].append(name)
            print(f"  ✅ Deleted: {name}")
        else:
            results["failed"].append(name)
            err = result.stderr.strip()[:120] if result.stderr else "unknown error"
            print(f"  ❌ Failed: {name} — {err}")
    return results


def detect_repo_slug(cwd: str = ".") -> Optional[str]:
    """Try to detect owner/repo from git remote URL."""
    import re as _re

    url = run_git(["remote", "get-url", "origin"], cwd=cwd)
    if not url:
        return None

    # Match SSH format: git@github.com:owner/repo.git
    ssh_match = _re.match(r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$", url)
    if ssh_match:
        return ssh_match.group(1)

    # Match HTTPS format: https://github.com/owner/repo.git
    https_match = _re.match(
        r"^https?://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$", url
    )
    if https_match:
        return https_match.group(1)

    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aurora CloudBank — Safe Branch Cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="Actually delete safe-to-remove branches (default: dry run)",
    )
    parser.add_argument(
        "--report-only", action="store_true",
        help="Generate report and exit without interactive prompts",
    )
    parser.add_argument(
        "--stale-days", type=int, default=30,
        help="Days of inactivity before a branch is considered stale (default: 30)",
    )
    parser.add_argument(
        "--save-report", type=str, default=None,
        help="Path to save the markdown report (default: stdout)",
    )
    parser.add_argument(
        "--repo", type=str, default=None,
        help="GitHub owner/repo slug (auto-detected from git remote if omitted)",
    )
    parser.add_argument(
        "--skip-github", action="store_true",
        help="Skip GitHub API calls (offline mode, no PR cross-referencing)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    cwd = "."

    # Fetch and prune
    fetch_and_prune(cwd)

    # Detect repo slug
    slug = args.repo or detect_repo_slug(cwd)
    owner, repo = (slug.split("/", 1) if slug and "/" in slug else (None, None))

    # Get all remote branches
    branch_names = get_remote_branches(cwd)
    logger.info("Found %d remote branches", len(branch_names))

    # Get details for each branch
    branches = []
    for name in branch_names:
        # Skip the current cleanup branch itself
        if name == "copilot/consolidate-and-cleanup-branches":
            continue
        try:
            details = get_branch_details(name, cwd)
            branches.append(details)
        except Exception as exc:
            logger.warning("Skipping branch %s: %s", name, exc)

    # Fetch GitHub PR data
    branch_prs: Dict[str, List[Dict]] = {}
    if not args.skip_github and owner and repo:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        logger.info("Fetching PR data from GitHub API for %s/%s ...", owner, repo)
        branch_prs = fetch_github_prs(owner, repo, token)
        logger.info("Found PR data for %d branches", len(branch_prs))
    elif not args.skip_github:
        logger.warning(
            "Could not detect GitHub repo slug from git remotes. "
            "Use --repo owner/repo to specify it explicitly. "
            "Skipping PR cross-referencing."
        )

    # Categorize branches
    categories = categorize_branches(branches, branch_prs, args.stale_days)

    # Generate report
    report = generate_report(categories)

    if args.save_report:
        with open(args.save_report, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📄 Report saved to: {args.save_report}")
    else:
        print(report)

    # Summary
    safe_count = (
        len(categories["merged_safe_delete"])
        + len(categories["closed_pr_safe_delete"])
        + len(categories["stale_no_pr"])
    )
    print("\n📊 Summary:")
    print(f"  Protected:             {len(categories['protected'])}")
    print(f"  Active PRs (keep):     {len(categories['active_prs'])}")
    print(f"  Safe to delete:        {safe_count}")
    print(f"    - Merged:            {len(categories['merged_safe_delete'])}")
    print(f"    - Closed PRs:        {len(categories['closed_pr_safe_delete'])}")
    print(f"    - Stale (no PR):     {len(categories['stale_no_pr'])}")
    print(f"  Needs review:          {len(categories['review_needed'])}")

    if args.report_only:
        return

    # Execute cleanup
    safe_branches = (
        categories["merged_safe_delete"]
        + categories["closed_pr_safe_delete"]
        + categories["stale_no_pr"]
    )

    if not safe_branches:
        print("\n✅ No branches to clean up.")
        return

    if not args.execute:
        print(
            f"\n💡 {safe_count} branches can be safely deleted. "
            f"Re-run with --execute to delete them."
        )
        return

    print(f"\n🚀 Deleting {len(safe_branches)} safe-to-remove branches...")
    results = delete_branches(safe_branches, cwd)
    print(
        f"\n🎯 Cleanup complete: "
        f"{len(results['deleted'])} deleted, "
        f"{len(results['failed'])} failed"
    )

    if results["failed"]:
        print("⚠️  Failed branches may require admin permissions or manual cleanup.")


if __name__ == "__main__":
    main()
