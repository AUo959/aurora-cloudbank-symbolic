#!/usr/bin/env python3
"""
SSMT v3.0 Pruning Mission - Phase 2 Executor
Mission: Safe deletion of stale branches (60+ days old)
Focus: Repository health improvement through targeted branch cleanup
"""

import logging

logger = logging.getLogger(__name__)

import subprocess
import sys
import json
from datetime import datetime

# Phase 2: Safe deletion candidates (60+ days old, verified stale)
STALE_BRANCHES_FOR_DELETION = [
    "AUo959-patch-1",
    "AUo959-patch-2", 
    "AUo959-patch-3",
    "alert-autofix-34",
    "codex/implement-opal2-core-and-regex-generation-engine",
    "copilot/fix-2957056e-ce6b-4b83-b42b-c14308484edd",
    "copilot/fix-304c3a01-1eab-427a-8ff6-102ec9cf8114",
    "copilot/fix-51",
    "dependabot/npm_and_yarn/dotenv-17.1.0",
    "dependabot/npm_and_yarn/eslint-9.30.1",
    "dependabot/pip/pandas-2.3.1"
]

def analyze_stale_branch_impact(branch_name: str) -> dict:
    """Analyze the potential impact of deleting a stale branch"""
    try:
        # Get branch age
        branch_date_result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", f"origin/{branch_name}"],
            cwd=".", capture_output=True, text=True, check=True
        )
        
        branch_timestamp = int(branch_date_result.stdout.strip())
        branch_date = datetime.fromtimestamp(branch_timestamp)
        age_days = (datetime.now() - branch_date).days
        
        # Get commit count
        commit_count_result = subprocess.run(
            ["git", "rev-list", "--count", f"main..origin/{branch_name}"],
            cwd=".", capture_output=True, text=True, check=True
        )
        
        commit_count = int(commit_count_result.stdout.strip())
        
        # Get changed files count
        changed_files_result = subprocess.run(
            ["git", "diff", "--name-only", f"main...origin/{branch_name}"],
            cwd=".", capture_output=True, text=True, check=True
        )
        
        changed_files = [f.strip() for f in changed_files_result.stdout.split('\n') if f.strip()]
        
        # Risk assessment
        risk_level = "LOW"
        if commit_count > 10 or len(changed_files) > 20:
            risk_level = "MEDIUM"
        if any("src/" in f or "modules/" in f for f in changed_files):
            if commit_count > 5:
                risk_level = "MEDIUM"
        
        return {
            "branch": branch_name,
            "age_days": age_days,
            "commit_count": commit_count,
            "changed_files_count": len(changed_files),
            "risk_level": risk_level,
            "deletion_recommended": age_days > 60 and risk_level == "LOW",
            "reason": f"Stale branch ({age_days} days old, {commit_count} commits)"
        }
        
    except (subprocess.CalledProcessError, ValueError) as e:
        return {
            "branch": branch_name,
            "error": str(e),
            "deletion_recommended": False,
            "risk_level": "UNKNOWN"
        }

def execute_safe_branch_deletion(branches: list, dry_run: bool = True) -> dict:
    """Execute safe deletion of verified stale branches"""
    print(f"🗑️ SSMT v3.0 Safe Branch Deletion (dry_run={dry_run})")
    print(f"📋 Analyzing {len(branches)} stale branches for deletion...")
    
    deletion_analysis = []
    safe_deletions = []
    requires_review = []
    
    # Analyze each branch
    for branch in branches:
        analysis = analyze_stale_branch_impact(branch)
        deletion_analysis.append(analysis)
        
        if analysis.get("deletion_recommended", False):
            safe_deletions.append(branch)
        else:
            requires_review.append(branch)
    
    print(f"\n📊 Deletion Analysis Results:")
    print(f"  ✅ Safe for deletion: {len(safe_deletions)} branches")
    print(f"  ⚠️ Requires review: {len(requires_review)} branches")
    
    if safe_deletions:
        print(f"\n🗑️ Safe Deletion Candidates:")
        for i, branch in enumerate(safe_deletions, 1):
            analysis = next(a for a in deletion_analysis if a["branch"] == branch)
            print(f"  {i}. {branch} ({analysis.get('age_days', 'unknown')} days old)")
    
    if requires_review:
        print(f"\n⚠️ Manual Review Required:")
        for branch in requires_review:
            analysis = next(a for a in deletion_analysis if a["branch"] == branch)
            print(f"  • {branch} - {analysis.get('reason', 'Complex changes')}")
    
    result = {
        "phase": "phase_2_safe_deletion",
        "analyzed": len(branches),
        "safe_deletions": safe_deletions,
        "requires_review": requires_review,
        "deletion_analysis": deletion_analysis,
        "dry_run": dry_run
    }
    
    if dry_run:
        print("")
# 📋 DRY RUN - Would delete %s branches", len(safe_deletions))
        return result
    
    # Execute actual deletions
    if safe_deletions:
        print("")
# ⚠️ This will permanently delete %s branches!", len(safe_deletions))
        confirmation = input("Type 'DELETE-STALE-BRANCHES' to confirm: ")
        
        if confirmation != "DELETE-STALE-BRANCHES":
            print("🚫 Branch deletion cancelled")
            result["executed"] = False
            return result
        
        deleted_branches = []
        failed_deletions = []
        
        for branch in safe_deletions:
            try:
                print(f"🗑️ Deleting {branch}...")
                subprocess.run(
                    ["git", "push", "origin", "--delete", branch],
                    cwd=".", check=True
                )
                deleted_branches.append(branch)
                logger.info("Deleted: %s", branch)
                
            except subprocess.CalledProcessError as e:
                failed_deletions.append({"branch": branch, "error": str(e)})
                logger.error("Failed to delete {branch}: %s", e)
        
        result.update({
            "executed": True,
            "deleted_branches": deleted_branches,
            "failed_deletions": failed_deletions,
            "success_count": len(deleted_branches),
            "failure_count": len(failed_deletions)
        })
        
        print(f"\n🎯 Phase 2 Deletion Complete:")
        print(f"  ✅ Successfully deleted: {len(deleted_branches)} branches")
        print(f"  ❌ Failed deletions: {len(failed_deletions)} branches")
    
    return result

def execute_pruning_mission_phase_2():
    """Execute Phase 2 of repository pruning mission"""
    print("🌳 SSMT v3.0 Repository Pruning Mission - Phase 2")
    print("🎯 Mission: Safe deletion of stale branches (60+ days old)")
    print("🧹 Goal: Repository health improvement through targeted cleanup")
    
    print("")
# 📋 Stale Branch Deletion Candidates (%s total):", len(STALE_BRANCHES_FOR_DELETION))
    for i, branch in enumerate(STALE_BRANCHES_FOR_DELETION, 1):
        print(f"  {i:2d}. {branch}")
    
    print(f"\n🛡️ Safety Measures:")
    print(f"  ✅ Only branches 60+ days old")
    print(f"  ✅ Risk analysis for each branch")
    print(f"  ✅ Manual confirmation required")
    print(f"  ✅ Individual deletion tracking")
    
    # Execute dry run first
    print(f"\n🔍 Performing safety analysis...")
    dry_run_result = execute_safe_branch_deletion(STALE_BRANCHES_FOR_DELETION, dry_run=True)
    
    print(f"\n📊 Phase 2 Analysis Complete:")
    print(json.dumps(dry_run_result, indent=2))
    
    if dry_run_result["safe_deletions"]:
        print("")
# 🚀 Ready to execute deletion of %s safe branches", len(dry_run_result['safe_deletions']))
        proceed = input("Execute actual deletion? (y/N): ")
        
        if proceed.lower() == 'y':
            final_result = execute_safe_branch_deletion(dry_run_result["safe_deletions"], dry_run=False)
            print(f"\n🎯 Phase 2 Pruning Mission Complete!")
            return final_result
    
    print(f"\n✅ Phase 2 analysis complete - ready for manual review of remaining branches")
    return dry_run_result

if __name__ == "__main__":
    execute_pruning_mission_phase_2()