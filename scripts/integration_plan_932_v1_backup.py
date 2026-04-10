#!/usr/bin/env python3
"""Integration Plan Generator (#932//.)

Scans issues and pull requests using GitHub CLI and synthesizes
an optimal phased merge plan.

Phases:
  Phase 1: Ready (no blocking tasks)
  Phase 2: Near-Ready (<=2 minor tasks)
  Phase 3: Complex (>2 tasks or structural blockers)

Outputs both Markdown and JSON structures to stdout.

Prerequisites:
  - GitHub CLI installed (`gh`)
  - Authenticated (`gh auth status`)

Graceful Degradation:
  If GitHub CLI or auth is missing, emits structured error JSON.

Sequence Integration:
  --next-commands: Emit executable commands for next phase
  --execute: Auto-run Phase 1 merges (with confirmation)

DLP:
  context_tag: integration_plan_932

"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

REPO_ENV_VAR = "INTEGRATION_PLAN_REPO"  # optionally override repo ("owner/repo")
PR_REF_PATTERN = re.compile(r"#(\d+)")

# Risk thresholds
RISK_HIGH_FILES = 30
RISK_HIGH_CHURN = 500
RISK_MEDIUM_FILES = 15
RISK_MEDIUM_CHURN = 200


def run_gh(args: List[str]) -> Tuple[int, str, str]:
    """Run gh command and return (rc, stdout, stderr)."""
    try:
        completed = subprocess.run([
            "gh", *args
        ], capture_output=True, text=True, check=False)
        return completed.returncode, completed.stdout, completed.stderr
    except FileNotFoundError:
        return 127, "", "GitHub CLI (gh) not found"


def gh_json(args: List[str]) -> Any:
    rc, out, err = run_gh(args)
    if rc != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed (rc={rc}): {err.strip()}")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from gh output for args: {args}")


def fetch_issues() -> List[Dict[str, Any]]:
    args = ["issue", "list", "--state", "open", "--json", "number,title,labels,assignees,url"]
    return gh_json(args)


def fetch_pull_requests() -> List[Dict[str, Any]]:
    args = ["pr", "list", "--state", "open", "--json",
            "number,title,state,isDraft,mergeable,mergeStateStatus,headRefName,baseRefName,url"]
    return gh_json(args)


def enrich_pr(pr_number: int) -> Dict[str, Any]:
    args = [
        "pr", "view", str(pr_number), "--json",
        "closingIssuesReferences,reviewDecision,reviews,mergeStateStatus,commits,"
        "statusCheckRollup,body,files,additions,deletions"
    ]
    return gh_json(args)


def extract_issue_refs_from_body(body: str) -> List[int]:
    refs = set()
    for match in PR_REF_PATTERN.finditer(body or ""):
        try:
            refs.add(int(match.group(1)))
        except ValueError:
            continue
    return sorted(refs)


def calculate_risk_score(detail: Dict[str, Any]) -> Tuple[str, int]:
    """Calculate risk score based on file changes and complexity."""
    files_changed = len(detail.get("files", []))
    additions = sum(f.get("additions", 0) for f in detail.get("files", []))
    deletions = sum(f.get("deletions", 0) for f in detail.get("files", []))
    churn = additions + deletions
    
    if files_changed >= RISK_HIGH_FILES or churn >= RISK_HIGH_CHURN:
        return "high", files_changed
    elif files_changed >= RISK_MEDIUM_FILES or churn >= RISK_MEDIUM_CHURN:
        return "medium", files_changed
    return "low", files_changed


def estimate_merge_time(risk_level: str, files_changed: int) -> str:
    """Estimate time to merge based on risk and size."""
    if risk_level == "high":
        return "60-120min"
    elif risk_level == "medium":
        return "30-60min"
    elif files_changed > 5:
        return "15-30min"
    return "5-15min"


def build_dependency_graph(enriched: List[Dict[str, Any]]) -> Dict[int, List[int]]:
    """Build directed graph of PR dependencies (pr -> [blocking_prs])."""
    graph: Dict[int, List[int]] = {}
    pr_numbers = {pr["number"] for pr in enriched}
    
    for pr in enriched:
        pr_num = pr["number"]
        graph[pr_num] = []
        
        # Check body for PR references
        body_refs = extract_issue_refs_from_body(pr.get("raw_body", ""))
        for ref in body_refs:
            if ref in pr_numbers and ref != pr_num:
                graph[pr_num].append(ref)
    
    return graph


def find_critical_path(graph: Dict[int, List[int]], enriched: List[Dict[str, Any]]) -> List[int]:
    """Find longest dependency chain (critical path)."""
    def dfs_depth(node: int, visited: set) -> int:
        if node in visited:
            return 0
        visited.add(node)
        if not graph.get(node):
            return 1
        return 1 + max((dfs_depth(dep, visited.copy()) for dep in graph[node]), default=0)
    
    depths = {pr["number"]: dfs_depth(pr["number"], set()) for pr in enriched}
    if not depths:
        return []
    
    max_depth_pr = max(depths.items(), key=lambda x: x[1])[0]
    
    # Trace back the path
    path = [max_depth_pr]
    current = max_depth_pr
    while graph.get(current):
        deps = graph[current]
        if deps:
            current = deps[0]  # Take first dependency
            path.append(current)
        else:
            break
    
    return list(reversed(path))


def identify_bottlenecks(graph: Dict[int, List[int]]) -> List[Tuple[int, int]]:
    """Find PRs that block multiple others."""
    blocked_count: Dict[int, int] = {}
    
    for pr_num, deps in graph.items():
        for dep in deps:
            blocked_count[dep] = blocked_count.get(dep, 0) + 1
    
    bottlenecks = [(pr, count) for pr, count in blocked_count.items() if count > 1]
    return sorted(bottlenecks, key=lambda x: x[1], reverse=True)


def derive_tasks(base_pr: Dict[str, Any], detail: Dict[str, Any]) -> List[str]:
    tasks: List[str] = []
    # Draft status
    if base_pr.get("isDraft"):
        tasks.append("Mark ready for review")
    # Merge status
    if detail.get("mergeStateStatus") and detail.get("mergeStateStatus") != "CLEAN":
        tasks.append("Resolve merge conflicts or merge blockers")
    # Status checks
    rollup = detail.get("statusCheckRollup") or []
    failing = [c for c in rollup if c.get("conclusion") == "FAILURE"]
    pending = [c for c in rollup if c.get("conclusion") in (None, "PENDING")]
    if failing:
        tasks.append("Fix failing status checks")
    if pending and not failing:
        tasks.append("Await or re-run pending checks")
    # Review decision
    decision = detail.get("reviewDecision")
    if decision in ("REVIEW_REQUIRED", "CHANGES_REQUESTED"):
        tasks.append("Obtain required approvals / address review feedback")
    # Issue linkage
    closing_refs = detail.get("closingIssuesReferences") or []
    if not closing_refs:
        tasks.append("Link or create issue reference")
    # Dependency hints (other PR refs mentioned in body)
    body = detail.get("body") or ""
    other_pr_refs = [ref for ref in extract_issue_refs_from_body(body) if ref != base_pr.get("number")]
    if other_pr_refs:
        tasks.append("Verify dependency PR sequencing")
    # Heuristic: Encourage tests if commits > threshold & no test mention
    commits = detail.get("commits") or []
    if len(commits) > 3 and "test" not in body.lower():
        tasks.append("Add or confirm test coverage")
    return tasks


def phase_for_tasks(tasks: List[str]) -> str:
    if not tasks:
        return "phase_1"
    if len(tasks) <= 2:
        return "phase_2"
    return "phase_3"


def build_plan() -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # Basic environment checks
    rc_auth, out_auth, _ = run_gh(["auth", "status"])
    if rc_auth != 0:
        return {
            "error": "GitHub CLI not authenticated or unavailable",
            "generated_at": now,
            "context_tag": "integration_plan_932"
        }

    try:
        issues = fetch_issues()  # noqa: F841 - Reserved for future issue linkage
        prs = fetch_pull_requests()
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "generated_at": now, "context_tag": "integration_plan_932"}

    enriched = []
    for pr in prs:
        try:
            detail = enrich_pr(pr["number"])  # noqa: S113
        except Exception as e:  # noqa: BLE001
            detail = {"error": str(e)}
        tasks = derive_tasks(pr, detail)
        closing_issue_numbers = [i.get("number") for i in (detail.get("closingIssuesReferences") or [])]
        body_refs = extract_issue_refs_from_body(detail.get("body") or "")
        phase = phase_for_tasks(tasks)
        risk_level, files_changed = calculate_risk_score(detail)
        time_estimate = estimate_merge_time(risk_level, files_changed)
        
        enriched.append({
            "number": pr.get("number"),
            "title": pr.get("title"),
            "url": pr.get("url"),
            "state": pr.get("state"),
            "is_draft": pr.get("isDraft"),
            "merge_state": detail.get("mergeStateStatus"),
            "review_decision": detail.get("reviewDecision"),
            "tasks": tasks,
            "issues": sorted(set(closing_issue_numbers + body_refs)),
            "phase": phase,
            "risk": risk_level,
            "files_changed": files_changed,
            "time_estimate": time_estimate,
            "raw_body": detail.get("body", ""),
        })

    phases: Dict[str, List[Dict[str, Any]]] = {"phase_1": [], "phase_2": [], "phase_3": []}
    for item in enriched:
        phases[item["phase"]].append(item)

    # Build dependency graph and identify bottlenecks
    dep_graph = build_dependency_graph(enriched)
    bottlenecks = identify_bottlenecks(dep_graph)
    critical_path = find_critical_path(dep_graph, enriched)
    
    # Ordering: Phase 1 first, then Phase 2, then Phase 3
    # Within phase: prioritize by dependencies (bottlenecks first), then risk (low first), then tasks
    def sort_key(p: Dict[str, Any]) -> Tuple:
        is_bottleneck = any(p["number"] == bn[0] for bn in bottlenecks)
        risk_score = {"low": 0, "medium": 1, "high": 2}.get(p.get("risk", "low"), 0)
        return (not is_bottleneck, risk_score, len(p["tasks"]), p["number"])
    
    ordering = [
        *[p["number"] for p in sorted(phases["phase_1"], key=sort_key)],
        *[p["number"] for p in sorted(phases["phase_2"], key=sort_key)],
        *[p["number"] for p in sorted(phases["phase_3"], key=sort_key)],
    ]

    # Checkpoints heuristics
    checkpoints = []
    if phases["phase_1"]:
        checkpoints.append({
            "name": "Batch Merge – Ready Set",
            "prs": [p["number"] for p in phases["phase_1"]]
        })
    if phases["phase_2"]:
        checkpoints.append({
            "name": "Rebase Near-Ready After Phase 1",
            "prs": [p["number"] for p in phases["phase_2"]]
        })
    if phases["phase_3"]:
        checkpoints.append({
            "name": "Sequential Complex Integration",
            "prs": [p["number"] for p in phases["phase_3"]]
        })

    # Generate recommendations
    recommendations = []
    draft_count = sum(1 for p in enriched if p.get("is_draft"))
    if draft_count > 0:
        recommendations.append(f"{draft_count} PRs in draft - marking ready could accelerate Phase 2")
    
    if bottlenecks:
        for pr_num, blocked_count in bottlenecks[:3]:
            recommendations.append(f"PR #{pr_num} blocks {blocked_count} others - prioritize merge")
    
    high_risk = [p for p in enriched if p.get("risk") == "high"]
    if high_risk:
        recommendations.append(f"{len(high_risk)} high-risk PRs - schedule dedicated review/testing")
    
    conflict_count = sum(1 for p in enriched if p.get("merge_state") == "UNSTABLE")
    if conflict_count > 5:
        recommendations.append(f"{conflict_count} PRs have conflicts - consider batch rebase")
    
    # Estimate total time
    phase_1_time = sum(
        int(p.get("time_estimate", "15min").split("-")[0])
        for p in phases["phase_1"]
    ) if phases["phase_1"] else 0
    
    # Generate phased integration sequence
    integration_sequence = []
    
    # Phase 1: Immediate merges
    immediate_prs = [s for s in strategies if s["phase"] == "immediate"]
    if immediate_prs:
        integration_sequence.append({
            "sequence": 1,
            "name": "Immediate Merge Batch",
            "description": "PRs ready to merge with zero blockers",
            "prs": [s["pr"] for s in immediate_prs],
            "strategy": "parallel_merge",
            "estimated_time": f"{len(immediate_prs) * 3}min",
            "checkpoint": "Verify all merged successfully before proceeding",
            "commands": [cmd for s in immediate_prs for cmd in s["commands"]]
        })
    
    # Phase 2: Quick wins (drafts that are clean)
    quick_wins = [s for s in strategies if s["phase"] == "quick_win"]
    if quick_wins:
        integration_sequence.append({
            "sequence": 2,
            "name": "Quick Win Activation",
            "description": "Mark ready and merge clean draft PRs",
            "prs": [s["pr"] for s in quick_wins],
            "strategy": "sequential_activate",
            "estimated_time": f"{len(quick_wins) * 8}min",
            "checkpoint": "Review each before marking ready",
            "commands": [cmd for s in quick_wins for cmd in s["commands"]]
        })
    
    # Phase 3: Rebase operations (conflicts)
    rebase_prs = [s for s in strategies if s["phase"] == "rebase_required"]
    if rebase_prs:
        integration_sequence.append({
            "sequence": 3,
            "name": "Batch Rebase & Conflict Resolution",
            "description": "Rebase all conflicting PRs on updated main",
            "prs": [s["pr"] for s in rebase_prs],
            "strategy": "one_by_one_rebase",
            "estimated_time": f"{len(rebase_prs) * 20}min",
            "checkpoint": "Test each rebased PR locally before pushing",
            "commands": [f"# PR #{s['pr']}: {s['title']}" for s in rebase_prs] + 
                       [cmd for s in rebase_prs[:1] for cmd in s["commands"]] +
                       [f"# Repeat for remaining {len(rebase_prs)-1} PRs"]
        })
    
    # Phase 4: Fix failing checks
    fix_prs = [s for s in strategies if s["phase"] == "fix_required"]
    if fix_prs:
        integration_sequence.append({
            "sequence": 4,
            "name": "CI Failure Remediation",
            "description": "Fix failing checks and push updates",
            "prs": [s["pr"] for s in fix_prs],
            "strategy": "parallel_fix",
            "estimated_time": f"{len(fix_prs) * 40}min",
            "checkpoint": "Verify all checks green before next phase",
            "commands": [f"# PR #{s['pr']}: {'; '.join(s['risk_factors'])}" for s in fix_prs]
        })
    
    # Phase 5: Complex cases
    complex_prs = [s for s in strategies if s["phase"] == "complex"]
    if complex_prs:
        integration_sequence.append({
            "sequence": 5,
            "name": "Complex Case Triage",
            "description": "Manual coordination required",
            "prs": [s["pr"] for s in complex_prs],
            "strategy": "manual_review",
            "estimated_time": f"{len(complex_prs) * 90}min",
            "checkpoint": "Assign owners and schedule 1-on-1 reviews",
            "commands": [f"gh pr view {s['pr']}  # Manual triage" for s in complex_prs]
        })
    
    repo = os.getenv(REPO_ENV_VAR, "")
    plan = {
        "generated_at": now,
        "context_tag": "integration_plan_932",
        "repository": repo or "(auto-detected via gh context)",
        "summary": {
            "total_open_prs": len(enriched),
            "phase_counts": {
                "phase_1": len(phases["phase_1"]),
                "phase_2": len(phases["phase_2"]),
                "phase_3": len(phases["phase_3"]),
            },
            "estimated_phase_1_time": f"{phase_1_time}min" if phase_1_time else "0min",
            "high_risk_count": len(high_risk),
            "draft_count": draft_count,
        },
        "integration_sequence": integration_sequence,
        "strategies": strategies,
        "phases": phases,
        "checkpoints": checkpoints,
        "ordering": ordering,
        "recommendations": recommendations,
        "bottlenecks": [{"pr": pr, "blocks": count} for pr, count in bottlenecks[:5]],
        "critical_path": critical_path,
        "hash": hash(tuple(ordering)),  # Simple lineage hash (non-cryptographic)
    }
    return plan


def generate_next_commands(plan: Dict[str, Any]) -> List[str]:
    """Generate executable commands for next sequence step."""
    commands = []
    phase_1 = plan.get("phases", {}).get("phase_1", [])
    
    if phase_1:
        commands.append("# Phase 1: Ready to merge")
        for pr in phase_1[:3]:  # First 3 as safe batch
            commands.append(f"gh pr merge {pr['number']} --auto --squash")
        if len(phase_1) > 3:
            commands.append(f"# ... {len(phase_1) - 3} more Phase 1 PRs")
    
    phase_2 = plan.get("phases", {}).get("phase_2", [])
    if phase_2:
        commands.append("\n# Phase 2: Near-ready (after Phase 1)")
        for pr in phase_2[:2]:
            tasks = pr.get("tasks", [])
            commands.append(f"# PR #{pr['number']}: {', '.join(tasks)}")
            commands.append(f"gh pr view {pr['number']}")
    
    return commands


def render_markdown(plan: Dict[str, Any], include_commands: bool = False) -> str:
    if "error" in plan:
        return f"# Integration Plan Error\n\n{plan['error']}\n"
    lines: List[str] = []
    lines.append(f"# Intelligent Integration Plan (Generated {plan['generated_at']})")
    summary = plan.get("summary", {})
    phase_counts = summary.get("phase_counts", {})
    lines.append("")
    lines.append("## Summary")
    lines.append(f"Open PRs: {summary.get('total_open_prs', 0)}")
    p1, p2, p3 = phase_counts.get('phase_1', 0), phase_counts.get('phase_2', 0), phase_counts.get('phase_3', 0)
    lines.append(f"Phase 1 Ready: {p1} | Phase 2 Near-Ready: {p2} | Phase 3 Complex: {p3}")
    
    if summary.get("estimated_phase_1_time"):
        lines.append(f"Estimated Phase 1 Time: {summary['estimated_phase_1_time']}")
    if summary.get("high_risk_count", 0) > 0:
        lines.append(f"⚠️  High Risk PRs: {summary['high_risk_count']}")
    lines.append("")
    
    # Recommendations
    recommendations = plan.get("recommendations", [])
    if recommendations:
        lines.append("## 🎯 Recommendations")
        for rec in recommendations:
            lines.append(f"- {rec}")
        lines.append("")
    
    # Bottlenecks
    bottlenecks = plan.get("bottlenecks", [])
    if bottlenecks:
        lines.append("## 🚨 Bottlenecks")
        for bn in bottlenecks:
            pr_info = next((p for p in plan.get("phases", {}).get("phase_3", []) + 
                           plan.get("phases", {}).get("phase_2", []) + 
                           plan.get("phases", {}).get("phase_1", []) 
                           if p["number"] == bn["pr"]), None)
            if pr_info:
                lines.append(f"- PR #{bn['pr']}: {pr_info['title']} (blocks {bn['blocks']} PRs)")
        lines.append("")
    
    # Critical path
    critical_path = plan.get("critical_path", [])
    if critical_path and len(critical_path) > 1:
        lines.append("## 🔗 Critical Path")
        lines.append(" → ".join(f"#{pr}" for pr in critical_path))
        lines.append("")
    for phase_key, phase_title in [
        ("phase_1", "Phase 1 – Ready"),
        ("phase_2", "Phase 2 – Near-Ready"),
        ("phase_3", "Phase 3 – Complex"),
    ]:
        pr_items = plan["phases"].get(phase_key, [])
        lines.append(f"## {phase_title} ({len(pr_items)})")
        if not pr_items:
            lines.append("(none)")
        else:
            for pr in pr_items:
                risk_icon = "" if pr.get("risk") == "low" else ("⚠️ " if pr.get("risk") == "medium" else "🔴 ")
                time_est = pr.get("time_estimate", "")
                tasks_display = " ✅" if not pr["tasks"] else " – " + "; ".join(pr["tasks"])
                lines.append(f"- {risk_icon}PR #{pr['number']}: {pr['title']} ({time_est}){tasks_display}")
        lines.append("")
    lines.append("## Checkpoints")
    if plan.get("checkpoints"):
        for cp in plan["checkpoints"]:
            lines.append(f"1. {cp['name']}: {', '.join('#'+str(n) for n in cp['prs'])}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## Suggested Merge Ordering")
    ordering = plan.get("ordering", [])
    if ordering:
        lines.append(" → ".join(f"#{n}" for n in ordering))
    else:
        lines.append("(none)")
    lines.append("")
    
    if include_commands:
        lines.append("## Next Commands")
        next_cmds = generate_next_commands(plan)
        if next_cmds:
            lines.append("```bash")
            lines.extend(next_cmds)
            lines.append("```")
        lines.append("")
    
    lines.append(f"Context Tag: {plan.get('context_tag')}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Integration Plan Generator (#932//.)")
    parser.add_argument(
        "--next-commands", action="store_true",
        help="Include executable commands for next phase")
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only (no markdown)")
    parser.add_argument(
        "--execute", action="store_true",
        help="Auto-execute Phase 1 merges (with confirmation)")
    args = parser.parse_args()
    
    plan = build_plan()
    
    if args.execute and "error" not in plan:
        phase_1 = plan.get("phases", {}).get("phase_1", [])
        if phase_1:
            print(f"Found {len(phase_1)} ready PRs. Merge now? [y/N]: ", end="")
            confirm = input().strip().lower()
            if confirm == "y":
                for pr in phase_1:
                    print(f"Merging PR #{pr['number']}...")
                    subprocess.run(["gh", "pr", "merge", str(pr["number"]), "--auto", "--squash"])
                return 0
            print("Execution cancelled.")
    
    if not args.json_only:
        markdown = render_markdown(plan, include_commands=args.next_commands)
        print(markdown)
        print("\n---\n")
    
    print(json.dumps(plan, indent=2))
    return 0 if "error" not in plan else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
