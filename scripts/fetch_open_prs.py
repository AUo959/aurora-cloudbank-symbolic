#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
from typing import Any, Dict, List


def get_repo_slug() -> str:
    try:
        url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode().strip()
        )
    except Exception:
        return ""
    if url.startswith("git@github.com:"):
        return url[len("git@github.com:") :].removesuffix(".git")
    if url.startswith("https://github.com/"):
        return url[len("https://github.com/") :].removesuffix(".git")
    if url.startswith("http://github.com/"):
        return url[len("http://github.com/") :].removesuffix(".git")
    return ""


def gh_api(path: str) -> Any:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read().decode()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"HTTP error {e.code} for {path}: {e.reason}\n")
    except Exception as e:
        sys.stderr.write(f"Error fetching {path}: {e}\n")
    return None


def fetch_open_prs(slug: str) -> List[Dict[str, Any]]:
    prs = gh_api(f"/repos/{slug}/pulls?state=open&per_page=100")
    return prs or []


def fetch_pr_details(slug: str, number: int) -> Dict[str, Any]:
    pr = gh_api(f"/repos/{slug}/pulls/{number}")
    return pr or {}


def write_markdown(slug: str, prs: List[Dict[str, Any]], out_path: str) -> None:
    lines: List[str] = []
    lines.append(f"# Open PRs Summary for {slug}")
    lines.append("")
    if not prs:
        lines.append("No open pull requests found.")
    else:
        lines.append("| # | Title | Head | Draft | Updated | Labels | Link |")
        lines.append("|---:|-------|------|-------|---------|--------|------|")
        for pr in prs:
            number = pr.get("number")
            title = (pr.get("title") or "").replace("|", "/")
            head_ref = pr.get("head", {}).get("label") or pr.get("head", {}).get("ref")
            draft = "yes" if pr.get("draft") else "no"
            updated = pr.get("updated_at") or pr.get("created_at") or ""
            labels = ",".join([lbl.get("name") for lbl in pr.get("labels", []) if lbl.get("name")])
            html_url = pr.get("html_url") or f"https://github.com/{slug}/pull/{number}"
            lines.append(f"| {number} | {title} | `{head_ref}` | {draft} | {updated} | {labels} | [open]({html_url}) |")

        # Optional deeper details: mergeable_state
        lines.append("")
        lines.append("## Details")
        for pr in prs:
            number = pr.get("number")
            detail = fetch_pr_details(slug, number)
            mergeable_state = detail.get("mergeable_state")
            base_ref = detail.get("base", {}).get("ref")
            head_sha = detail.get("head", {}).get("sha")
            lines.append(f"- PR #{number}: mergeable_state={mergeable_state}, base={base_ref}, head_sha={head_sha}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    slug = get_repo_slug()
    if not slug:
        sys.stderr.write("Could not determine repo slug from git remote.\n")
        return 2
    prs = fetch_open_prs(slug)
    out_path = os.path.join(os.getcwd(), "OPEN_PRS_SUMMARY.md")
    write_markdown(slug, prs, out_path)
    print(f"Wrote {out_path} with {len(prs)} open PR(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
