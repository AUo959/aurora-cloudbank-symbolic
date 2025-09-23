#!/usr/bin/env python3
import json
import os
import urllib.request

REPO = "AUo959/aurora-cloudbank-symbolic"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
}

PRS = [146, 147, 149, 148, 152, 151]


def gh(path: str):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main():
    rows = []
    for pr in PRS:
        prj = gh(f"/pulls/{pr}")
        mergeable = prj.get("mergeable_state")
        draft = prj.get("draft")
        head_sha = prj.get("head", {}).get("sha")
        labels_issue = gh(f"/issues/{pr}")
        labels = [lbl.get("name") for lbl in labels_issue.get("labels", [])]
        ci_state = None
        checks_summary = {}
        if head_sha:
            st = gh(f"/commits/{head_sha}/status")
            ci_state = st.get("state")
            checks = gh(f"/commits/{head_sha}/check-runs")
            total = checks.get("total_count", 0) or 0
            inprog = [c for c in checks.get("check_runs", []) if c.get("status") in ("in_progress", "queued")]
            failed = [c for c in checks.get("check_runs", []) if c.get("status") == "completed" and c.get("conclusion") in ("failure", "cancelled", "timed_out", "action_required")]
            completed = [c for c in checks.get("check_runs", []) if c.get("status") == "completed"]
            # consider success if all completed and no failed (success/neutral/skipped allowed)
            all_completed_success = (len(completed) == total) and (len(failed) == 0) if total else False
            checks_summary = {
                "total": total,
                "in_progress": len(inprog),
                "failed": len(failed),
                "all_completed_success": all_completed_success,
            }
        rows.append({
            "pr": pr,
            "mergeable": mergeable,
            "draft": bool(draft),
            "ci": ci_state,
            "head_sha": head_sha,
            "labels": labels,
            "checks": checks_summary,
        })
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
