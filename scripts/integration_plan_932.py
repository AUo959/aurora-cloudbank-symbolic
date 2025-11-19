#!/usr/bin/env python3
"""Integration Plan Generator v2 (#932//.) - Phased Execution Strategy

Generates concrete, actionable integration plans with specific commands
and checkpoint gates based on current repository state.

Enhanced from v1 to provide:
- Specific execution strategies per PR (not generic tasks)
- Phased integration sequence with checkpoints
- Context-aware resolution commands
- Risk-based ordering within phases

Usage:
    python scripts/integration_plan_932_v2.py              # Full plan
    python scripts/integration_plan_932_v2.py --phases     # Phases only
    python scripts/integration_plan_932_v2.py --execute    # Interactive execution

DLP: context_tag=integration_plan_932_v2
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

# === Configuration ===
REPO_ENV_VAR = "INTEGRATION_PLAN_REPO"
PR_REF_PATTERN = re.compile(r"#(\d+)")
RISK_HIGH_FILES = 30
RISK_HIGH_CHURN = 500
RISK_MEDIUM_FILES = 15
RISK_MEDIUM_CHURN = 200


# === GitHub CLI Wrapper ===
def run_gh(args: List[str]) -> Tuple[int, str, str]:
    """Run gh command and return (rc, stdout, stderr)."""
    try:
        completed = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False
        )
        return completed.returncode, completed.stdout, completed.stderr
    except FileNotFoundError:
        return 127, "", "GitHub CLI (gh) not found"


def gh_json(args: List[str]) -> Any:
    rc, out, err = run_gh(args)
    if rc != 0:
        raise RuntimeError(f"gh failed (rc={rc}): {err.strip()}")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse JSON from gh output")


def fetch_issues() -> List[Dict[str, Any]]:
    """Fetch all open issues with labels and priorities."""
    args = ["issue", "list", "--state", "open", "--json",
            "number,title,labels,milestone,assignees,createdAt,updatedAt,url"]
    return gh_json(args)


def fetch_pull_requests() -> List[Dict[str, Any]]:
    args = ["pr", "list", "--state", "open", "--json",
            "number,title,state,isDraft,mergeable,mergeStateStatus,url"]
    return gh_json(args)


def enrich_pr(pr_number: int) -> Dict[str, Any]:
    args = [
        "pr", "view", str(pr_number), "--json",
        "closingIssuesReferences,reviewDecision,reviews,mergeStateStatus,"
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


def assess_pr_quality(detail: Dict[str, Any]) -> Dict[str, Any]:
    """Assess if PR improves codebase or risks regression."""
    files = detail.get("files", [])
    additions = sum(f.get("additions", 0) for f in files)
    deletions = sum(f.get("deletions", 0) for f in files)
    
    # Quality indicators
    quality = {
        "score": 0,
        "indicators": [],
        "warnings": [],
        "recommendation": "merge"
    }
    
    # Positive indicators
    if deletions > additions * 0.5:  # Net code reduction
        quality["score"] += 2
        quality["indicators"].append("Code reduction (simplification)")
    
    test_files = [f for f in files if "test" in f.get("filename", "").lower()]
    if test_files:
        quality["score"] += 1
        quality["indicators"].append(f"Test coverage: {len(test_files)} test file(s)")
    
    doc_files = [f for f in files if any(ext in f.get("filename", "") for ext in [".md", "README", "CHANGELOG"])]
    if doc_files:
        quality["score"] += 1
        quality["indicators"].append("Documentation updated")
    
    # Warning indicators
    if additions > 1000 and not test_files:
        quality["score"] -= 2
        quality["warnings"].append("Large change without test additions")
    
    large_single_file = [f for f in files if f.get("additions", 0) > 500]
    if large_single_file:
        quality["score"] -= 1
        quality["warnings"].append(f"Large single-file change: {large_single_file[0].get('filename')}")
    
    # Generate recommendation
    if quality["score"] < -2:
        quality["recommendation"] = "review_carefully"
    elif quality["score"] < 0:
        quality["recommendation"] = "verify_tests"
    
    return quality


def categorize_issue_priority(issue: Dict[str, Any]) -> str:
    """Categorize issue priority based on labels and age."""
    labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
    
    # Priority labels
    if any(label in labels for label in ["critical", "p0", "blocking"]):
        return "critical"
    if any(label in labels for label in ["high", "p1", "bug"]):
        return "high"
    if any(label in labels for label in ["enhancement", "feature", "p2"]):
        return "medium"
    
    # Age-based priority (older = higher priority)
    created = issue.get("createdAt", "")
    if created:
        try:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - created_dt).days
            if age_days > 90:
                return "high"
            elif age_days > 30:
                return "medium"
        except (ValueError, AttributeError):
            pass
    
    return "low"


# === Strategy Generation ===
def generate_pr_strategy(pr_data: Dict[str, Any], detail: Dict[str, Any],
                         issues: List[Dict[str, Any]] = None) -> Dict[str, Any]:  # noqa: B006
    """Generate specific execution strategy for a PR based on its current state.
    
    Args:
        pr_data: Basic PR metadata
        detail: Detailed PR info from enrich_pr
        issues: All open issues for context mapping
    """
    pr_num = pr_data["number"]
    issues = issues or []
    
    # Analyze current state
    is_draft = pr_data.get("isDraft", False)
    merge_state = pr_data.get("mergeStateStatus", "")
    has_conflicts = merge_state == "UNSTABLE"
    
    status_checks = detail.get("statusCheckRollup", [])
    failing_checks = [c for c in status_checks if c.get("conclusion") == "FAILURE"]
    pending_checks = [c for c in status_checks if c.get("conclusion") in ["PENDING", "IN_PROGRESS", None]]
    
    review_decision = detail.get("reviewDecision", "")
    
    # Calculate risk
    files_changed = len(detail.get("files", []))
    additions = sum(f.get("additions", 0) for f in detail.get("files", []))
    deletions = sum(f.get("deletions", 0) for f in detail.get("files", []))
    churn = additions + deletions
    
    # Extract dependencies
    pr_refs = [int(m) for m in re.findall(r'#(\d{3,})', detail.get("body", "")) if int(m) != pr_num]
    
    # Link to issues
    linked_issues = [ref.get("number") for ref in detail.get("closingIssuesReferences", [])]
    body_issue_refs = extract_issue_refs_from_body(detail.get("body", ""))
    all_issue_refs = sorted(set(linked_issues + body_issue_refs))
    
    # Map issue priorities
    issue_map = {issue["number"]: issue for issue in issues}
    linked_issue_priorities = []
    for issue_num in all_issue_refs:
        if issue_num in issue_map:
            priority = categorize_issue_priority(issue_map[issue_num])
            linked_issue_priorities.append((issue_num, priority, issue_map[issue_num].get("title", "")))
    
    # Assess quality
    quality = assess_pr_quality(detail)
    
    strategy = {
        "pr": pr_num,
        "title": pr_data.get("title", ""),
        "phase": "",
        "steps": [],
        "commands": [],
        "checkpoint_required": False,
        "estimated_time": "5-15min",
        "dependencies": pr_refs,
        "linked_issues": linked_issue_priorities,
        "quality_assessment": quality,
        "risk_factors": [],
        "files_changed": files_changed,
        "churn": churn,
        "mission_score": 0
    }
    
    # Risk assessment
    if files_changed >= RISK_HIGH_FILES or churn >= RISK_HIGH_CHURN:
        strategy["risk_factors"].append(f"High complexity: {files_changed} files, {churn} lines")
    
    # Add quality warnings
    if quality["warnings"]:
        strategy["risk_factors"].extend(quality["warnings"])
    
    # Mission alignment scoring
    mission_score = 0
    if any(priority == "critical" for _, priority, _ in linked_issue_priorities):
        mission_score += 3
        strategy["risk_factors"].insert(0, "⭐ Addresses CRITICAL issue")
    elif any(priority == "high" for _, priority, _ in linked_issue_priorities):
        mission_score += 2
        strategy["risk_factors"].insert(0, "🎯 Addresses HIGH priority issue")
    
    if quality["score"] > 0:
        mission_score += quality["score"]
    elif quality["recommendation"] == "review_carefully":
        strategy["risk_factors"].insert(0, "⚠️  Quality concerns - review carefully")
    
    strategy["mission_score"] = mission_score
    
    # === DECISION TREE ===
    
    # Case 1: READY TO MERGE
    if not is_draft and not has_conflicts and not failing_checks and not pending_checks:
        strategy["phase"] = "immediate"
        strategy["steps"] = ["✅ PR is ready - all checks passed, no blockers"]
        strategy["commands"] = [
            f"gh pr view {pr_num}  # Final review",
            f"gh pr merge {pr_num} --squash --auto  # Auto-merge when CI completes"
        ]
        strategy["estimated_time"] = "2-5min"
    
    # Case 2: DRAFT BUT CLEAN
    elif is_draft and not has_conflicts and not failing_checks:
        strategy["phase"] = "quick_win"
        strategy["steps"] = [
            "1. Review PR changes (code appears ready)",
            "2. Mark as ready for review",
            "3. Wait for CI confirmation (~2min)",
            "4. Merge via auto-merge"
        ]
        strategy["commands"] = [
            f"gh pr ready {pr_num}  # Mark ready",
            "# Wait ~2min for CI re-run",
            f"gh pr merge {pr_num} --squash --auto"
        ]
        strategy["estimated_time"] = "5-10min"
    
    # Case 3: HAS CONFLICTS
    elif has_conflicts:
        strategy["phase"] = "rebase_required"
        strategy["checkpoint_required"] = True
        strategy["steps"] = [
            "1. Checkout PR branch locally",
            "2. Rebase on latest main",
            "3. Resolve merge conflicts",
            "4. Force push rebased branch",
            "5. Wait for CI re-run",
            "6. Verify tests still pass"
        ]
        strategy["commands"] = [
            f"gh pr checkout {pr_num}",
            "git fetch origin main",
            "git rebase origin/main",
            "# Resolve conflicts in editor, then:",
            "git add .",
            "git rebase --continue",
            "git push --force-with-lease"
        ]
        strategy["estimated_time"] = "15-30min"
        strategy["risk_factors"].append("Merge conflicts require manual resolution")
    
    # Case 4: FAILING CI
    elif failing_checks:
        strategy["phase"] = "fix_required"
        strategy["checkpoint_required"] = True
        failing_names = [c["name"] for c in failing_checks[:3]]
        strategy["steps"] = [
            f"1. Investigate failing checks: {', '.join(failing_names)}",
            "2. Fix code/tests locally",
            "3. Push fixes",
            "4. Wait for CI re-run",
            "5. Proceed to merge after green"
        ]
        strategy["commands"] = [
            f"gh pr checks {pr_num}  # View full failure details",
            f"gh pr checkout {pr_num}",
            "# Fix issues locally, then:",
            "git commit -am 'fix: Address CI failures'",
            "git push"
        ]
        strategy["estimated_time"] = "30-60min"
        strategy["risk_factors"].append(f"Failing: {', '.join(failing_names)}")
    
    # Case 5: PENDING CHECKS
    elif pending_checks:
        strategy["phase"] = "wait"
        strategy["steps"] = [
            "⏳ CI checks still running - wait for completion",
            f"Pending: {len(pending_checks)} check(s)"
        ]
        strategy["commands"] = [
            f"gh pr checks {pr_num} --watch  # Monitor progress",
            "# Re-run plan after checks complete"
        ]
        strategy["estimated_time"] = "5-15min (wait time)"
    
    # Case 6: COMPLEX / NEEDS REVIEW
    else:
        strategy["phase"] = "complex"
        strategy["checkpoint_required"] = True
        strategy["steps"] = ["⚠️  Complex PR requiring manual triage"]
        
        if is_draft:
            strategy["steps"].append("• Currently in draft - needs author action")
        if review_decision == "CHANGES_REQUESTED":
            strategy["steps"].append("• Changes requested - address review feedback")
        if not pr_refs and not detail.get("closingIssuesReferences"):
            strategy["steps"].append("• No linked issues - add context")
        
        strategy["commands"] = [
            f"gh pr view {pr_num}  # Full inspection",
            f"gh pr diff {pr_num}  # Review changes",
            "# Coordinate with PR author"
        ]
        strategy["estimated_time"] = "60-120min"
    
    return strategy


# === Integration Sequence Builder ===
def build_integration_sequence(strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build phased integration sequence with checkpoints.
    
    Orders PRs within phases by:
    1. Mission score (higher = more critical)
    2. Quality score (higher = safer to merge)
    3. PR number (lower = older, higher priority)
    """
    sequence = []
    seq_num = 1
    
    # Mission-focused sorting function
    def mission_sort_key(s: Dict[str, Any]) -> Tuple:
        return (
            -s.get("mission_score", 0),  # Higher mission score first
            -s.get("quality_assessment", {}).get("score", 0),  # Higher quality first
            s["pr"]  # Lower PR number (older) first
        )
    
    # Phase 1: Immediate merges (mission-sorted)
    immediate = sorted(
        [s for s in strategies if s["phase"] == "immediate"],
        key=mission_sort_key
    )
    if immediate:
        sequence.append({
            "sequence": seq_num,
            "name": "🚀 Immediate Merge Batch",
            "description": "PRs ready to merge with zero blockers",
            "prs": [s["pr"] for s in immediate],
            "count": len(immediate),
            "strategy": "parallel_merge",
            "estimated_time": f"{len(immediate) * 3}min",
            "checkpoint": "✅ Verify all merged successfully before proceeding",
            "commands": [cmd for s in immediate for cmd in s["commands"]]
        })
        seq_num += 1
    
    # Phase 2: Quick wins (clean drafts, mission-sorted)
    quick_wins = sorted(
        [s for s in strategies if s["phase"] == "quick_win"],
        key=mission_sort_key
    )
    if quick_wins:
        sequence.append({
            "sequence": seq_num,
            "name": "⚡ Quick Win Activation",
            "description": "Mark ready and merge clean draft PRs",
            "prs": [s["pr"] for s in quick_wins],
            "count": len(quick_wins),
            "strategy": "sequential_activate",
            "estimated_time": f"{len(quick_wins) * 8}min",
            "checkpoint": "📋 Review each before marking ready",
            "commands": (
                [f"# PR #{s['pr']}: {s['title']}" for s in quick_wins] +
                [cmd for s in quick_wins[:1] for cmd in s["commands"]] +
                [f"# Repeat for remaining {len(quick_wins)-1} PRs"]
            )
        })
        seq_num += 1
    
    # Phase 3: Rebase operations (mission-sorted)
    rebase_prs = sorted(
        [s for s in strategies if s["phase"] == "rebase_required"],
        key=mission_sort_key
    )
    if rebase_prs:
        sequence.append({
            "sequence": seq_num,
            "name": "🔄 Batch Rebase & Conflict Resolution",
            "description": "Rebase conflicting PRs on updated main",
            "prs": [s["pr"] for s in rebase_prs],
            "count": len(rebase_prs),
            "strategy": "one_by_one_rebase",
            "estimated_time": f"{len(rebase_prs) * 20}min",
            "checkpoint": "⚠️  Test each rebased PR locally before pushing",
            "commands": (
                [f"# PR #{s['pr']}: {s['title']}" for s in rebase_prs] +
                [cmd for s in rebase_prs[:1] for cmd in s["commands"]] +
                [f"# Repeat rebase for remaining {len(rebase_prs)-1} PRs"]
            )
        })
        seq_num += 1
    
    # Phase 4: Fix failing checks (mission-sorted)
    fix_prs = sorted(
        [s for s in strategies if s["phase"] == "fix_required"],
        key=mission_sort_key
    )
    if fix_prs:
        sequence.append({
            "sequence": seq_num,
            "name": "🔧 CI Failure Remediation",
            "description": "Fix failing checks and push updates",
            "prs": [s["pr"] for s in fix_prs],
            "count": len(fix_prs),
            "strategy": "parallel_fix",
            "estimated_time": f"{len(fix_prs) * 40}min",
            "checkpoint": "✅ Verify all checks green before next phase",
            "commands": (
                [f"# PR #{s['pr']}: {'; '.join(s['risk_factors'])}" for s in fix_prs] +
                ["# Coordinate with PR authors to fix issues"]
            )
        })
        seq_num += 1
    
    # Phase 5: Waiting on CI (mission-sorted)
    wait_prs = sorted(
        [s for s in strategies if s["phase"] == "wait"],
        key=mission_sort_key
    )
    if wait_prs:
        sequence.append({
            "sequence": seq_num,
            "name": "⏳ Pending CI Checks",
            "description": "Wait for CI completion before proceeding",
            "prs": [s["pr"] for s in wait_prs],
            "count": len(wait_prs),
            "strategy": "monitor",
            "estimated_time": f"{len(wait_prs) * 10}min",
            "checkpoint": "🔄 Re-run plan after checks complete",
            "commands": [f"gh pr checks {s['pr']} --watch" for s in wait_prs]
        })
        seq_num += 1
    
    # Phase 6: Complex cases (mission-sorted)
    complex_prs = sorted(
        [s for s in strategies if s["phase"] == "complex"],
        key=mission_sort_key
    )
    if complex_prs:
        sequence.append({
            "sequence": seq_num,
            "name": "🎯 Complex Case Triage",
            "description": "Manual coordination required",
            "prs": [s["pr"] for s in complex_prs],
            "count": len(complex_prs),
            "strategy": "manual_review",
            "estimated_time": f"{len(complex_prs) * 90}min",
            "checkpoint": "📝 Assign owners and schedule 1-on-1 reviews",
            "commands": [f"gh pr view {s['pr']}  # Manual triage" for s in complex_prs]
        })
    
    return sequence


# === Main Plan Builder ===
def build_plan() -> Dict[str, Any]:
    """Build comprehensive integration plan with execution strategies."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    
    # Check GitHub CLI authentication
    rc_auth, _, _ = run_gh(["auth", "status"])
    if rc_auth != 0:
        return {
            "error": "GitHub CLI not authenticated or unavailable",
            "generated_at": now,
            "context_tag": "integration_plan_932_v2"
        }
    
    try:
        issues = fetch_issues()
        prs = fetch_pull_requests()
    except Exception as e:
        return {
            "error": str(e),
            "generated_at": now,
            "context_tag": "integration_plan_932_v2"
        }
    
    # Generate strategies for each PR
    strategies = []
    for pr in prs:
        try:
            detail = enrich_pr(pr["number"])
            strategy = generate_pr_strategy(pr, detail, issues)
            strategies.append(strategy)
        except Exception as e:
            strategies.append({
                "pr": pr["number"],
                "title": pr.get("title", ""),
                "phase": "error",
                "error": str(e)
            })
    
    # Build integration sequence
    integration_sequence = build_integration_sequence(strategies)
    
    # Generate summary metrics
    phase_counts = {
        "immediate": len([s for s in strategies if s["phase"] == "immediate"]),
        "quick_win": len([s for s in strategies if s["phase"] == "quick_win"]),
        "rebase_required": len([s for s in strategies if s["phase"] == "rebase_required"]),
        "fix_required": len([s for s in strategies if s["phase"] == "fix_required"]),
        "wait": len([s for s in strategies if s["phase"] == "wait"]),
        "complex": len([s for s in strategies if s["phase"] == "complex"])
    }
    
    total_time = sum(
        int(phase["estimated_time"].split("min")[0])
        for phase in integration_sequence
    )
    
    high_risk_count = len([s for s in strategies if s.get("risk_factors")])
    
    repo = os.getenv(REPO_ENV_VAR, "") or "(auto-detected)"
    
    return {
        "generated_at": now,
        "context_tag": "integration_plan_932_v2",
        "repository": repo,
        "summary": {
            "total_prs": len(strategies),
            "phase_counts": phase_counts,
            "total_estimated_time": f"{total_time}min",
            "high_risk_count": high_risk_count,
            "phases_with_work": len(integration_sequence)
        },
        "integration_sequence": integration_sequence,
        "strategies": strategies,
        "issues": issues
    }


# === Renderers ===
def render_markdown(plan: Dict[str, Any]) -> str:
    """Render plan as human-readable Markdown."""
    if "error" in plan:
        return f"# ❌ Integration Plan Error\n\n{plan['error']}\n"
    
    lines = [
        f"# 🎯 Phased Integration Plan",
        f"Generated: {plan['generated_at']}",
        f"Repository: {plan['repository']}",
        "",
        "## 📊 Summary",
        f"- **Total PRs:** {plan['summary']['total_prs']}",
        f"- **Estimated Total Time:** {plan['summary']['total_estimated_time']}",
        f"- **High Risk PRs:** {plan['summary']['high_risk_count']}",
        f"- **Phases with Work:** {plan['summary']['phases_with_work']}",
        ""
    ]
    
    # Phase breakdown
    lines.append("### Phase Breakdown")
    for phase, count in plan['summary']['phase_counts'].items():
        if count > 0:
            lines.append(f"- **{phase}:** {count} PR(s)")
    lines.append("")
    
    # Open Issues Overview
    if plan.get('issues'):
        lines.append("## 🎯 Open Issues Overview")
        lines.append("")
        
        # Group issues by priority
        priority_groups = {"critical": [], "high": [], "medium": [], "low": []}
        issue_to_prs = {}  # Map issue number to PRs that address it
        
        # Build issue-to-PR mapping
        for strategy in plan['strategies']:
            if strategy.get('linked_issues'):
                for issue_num, priority, issue_title in strategy['linked_issues']:
                    if issue_num not in issue_to_prs:
                        issue_to_prs[issue_num] = []
                    issue_to_prs[issue_num].append(strategy['pr'])
        
        # Categorize all issues
        for issue in plan['issues']:
            priority = categorize_issue_priority(issue)
            priority_groups[priority].append(issue)
        
        # Render by priority
        for priority in ["critical", "high", "medium", "low"]:
            if priority_groups[priority]:
                priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📌", "low": "ℹ️"}[priority]
                lines.append(f"### {priority_emoji} {priority.upper()} Priority ({len(priority_groups[priority])} issues)")
                lines.append("")
                
                for issue in priority_groups[priority]:
                    issue_num = issue['number']
                    addressing_prs = issue_to_prs.get(issue_num, [])
                    pr_status = f" → Addressed by PR(s): {', '.join(f'#{pr}' for pr in addressing_prs)}" if addressing_prs else " ⚠️ No PRs addressing this issue"
                    
                    lines.append(f"- **Issue #{issue_num}:** {issue['title']}{pr_status}")
                lines.append("")
        
        # Show orphaned issues (no PRs addressing them)
        orphaned = [i for i in plan['issues'] if i['number'] not in issue_to_prs]
        if orphaned:
            lines.append("### ⚠️ Orphaned Issues (No PRs)")
            for issue in orphaned:
                priority = categorize_issue_priority(issue)
                priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📌", "low": "ℹ️"}[priority]
                lines.append(f"- {priority_emoji} Issue #{issue['number']}: {issue['title']} ({priority})")
            lines.append("")
    
    # Integration sequence
    lines.append("## 🚀 Integration Sequence")
    lines.append("")
    
    for phase in plan['integration_sequence']:
        lines.extend([
            f"### Phase {phase['sequence']}: {phase['name']}",
            f"**{phase['description']}**",
            "",
            f"- **PRs:** {', '.join(f'#{pr}' for pr in phase['prs'])}",
            f"- **Count:** {phase['count']}",
            f"- **Strategy:** {phase['strategy']}",
            f"- **Estimated Time:** {phase['estimated_time']}",
            f"- **Checkpoint:** {phase['checkpoint']}",
            "",
            "**Commands:**",
            "```bash"
        ])
        lines.extend(phase['commands'])
        lines.extend(["```", ""])
    
    # Detailed strategies
    lines.append("## 📋 Detailed PR Strategies")
    lines.append("")
    
    for strategy in plan['strategies']:
        if strategy.get('error'):
            lines.append(f"### PR #{strategy['pr']}: {strategy['title']}")
            lines.append(f"❌ Error: {strategy['error']}")
            lines.append("")
            continue
        
        risk_indicator = "🔴" if strategy.get('risk_factors') else "✅"
        
        # Build PR header with mission/quality indicators
        header_prefix = ""
        if strategy.get('mission_score', 0) >= 3:
            header_prefix = "⭐ "
        elif strategy.get('mission_score', 0) >= 2:
            header_prefix = "🎯 "
        
        lines.extend([
            f"### {risk_indicator} {header_prefix}PR #{strategy['pr']}: {strategy['title']}",
            f"**Phase:** {strategy['phase']} | **Mission Score:** {strategy.get('mission_score', 0)}",
            f"**Estimated Time:** {strategy['estimated_time']}",
            ""
        ])
        
        # Show linked issues and priorities
        if strategy.get('linked_issues'):
            lines.append("**Addresses Issues:**")
            for issue_num, priority, issue_title in strategy['linked_issues']:
                priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📌", "low": "ℹ️"}.get(priority, "")
                lines.append(f"- {priority_emoji} Issue #{issue_num}: {issue_title} ({priority} priority)")
            lines.append("")
        
        # Show quality assessment
        if strategy.get('quality_assessment'):
            qa = strategy['quality_assessment']
            quality_emoji = "✅" if qa['score'] >= 2 else "⚠️" if qa['score'] >= 0 else "🔴"
            lines.append(f"**Code Quality:** {quality_emoji} Score: {qa['score']} | Recommendation: {qa['recommendation']}")
            
            if qa['indicators']:
                lines.append(f"  - Positive: {', '.join(qa['indicators'])}")
            if qa['warnings']:
                lines.append(f"  - Warnings: {', '.join(qa['warnings'])}")
            lines.append("")
        
        if strategy.get('risk_factors'):
            lines.append("**Risk Factors:**")
            for risk in strategy['risk_factors']:
                lines.append(f"- {risk}")
            lines.append("")
        
        if strategy.get('dependencies'):
            lines.append(f"**Dependencies:** {', '.join(f'#{dep}' for dep in strategy['dependencies'])}")
            lines.append("")
        
        lines.append("**Steps:**")
        for step in strategy['steps']:
            lines.append(f"{step}")
        lines.append("")
        
        if strategy.get('commands'):
            lines.append("**Commands:**")
            lines.append("```bash")
            lines.extend(strategy['commands'])
            lines.append("```")
            lines.append("")
    
    lines.extend([
        "---",
        f"**Context Tag:** {plan['context_tag']}",
        f"**Thread:** T1→T8→T9→INFINITE"
    ])
    
    return "\n".join(lines)


# === CLI ===
def main():
    parser = argparse.ArgumentParser(description="Integration Plan Generator v2 (#932//.)")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only")
    parser.add_argument("--phases", action="store_true", help="Show only integration sequence")
    parser.add_argument("--execute", action="store_true", help="Interactive execution mode")
    args = parser.parse_args()
    
    plan = build_plan()
    
    if args.json_only:
        print(json.dumps(plan, indent=2))
    elif args.phases:
        print(f"# Integration Sequence ({plan['summary']['phases_with_work']} phases)")
        for phase in plan.get('integration_sequence', []):
            print(f"\nPhase {phase['sequence']}: {phase['name']}")
            print(f"  PRs: {', '.join(f'#{pr}' for pr in phase['prs'])}")
            print(f"  Time: {phase['estimated_time']}")
            print(f"  Checkpoint: {phase['checkpoint']}")
    else:
        print(render_markdown(plan))
        print("\n\n" + "="*80)
        print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
