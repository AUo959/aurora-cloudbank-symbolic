#!/usr/bin/env python3
"""
SSMT v3.0 Repository Pruning Mission - Phase 2 Direct Execution
Safe deletion of verified stale branches (automated execution)
"""

import subprocess
import json
from datetime import datetime, timedelta

def execute_branch_deletions():
    """Execute deletion of the 8 verified safe branches"""
    
    # The 8 branches verified as safe for deletion
    safe_branches = [
        "AUo959-patch-2",
        "AUo959-patch-3", 
        "alert-autofix-34",
        "copilot/fix-304c3a01-1eab-427a-8ff6-102ec9cf8114",
        "copilot/fix-51",
        "dependabot/npm_and_yarn/dotenv-17.1.0",
        "dependabot/npm_and_yarn/eslint-9.30.1",
        "dependabot/pip/pandas-2.3.1"
    ]
    
    print("🌳 SSMT v3.0 Repository Pruning Mission - Phase 2 EXECUTION")
    print("🎯 Mission: Delete 8 verified safe stale branches")
    print("🧹 Goal: Repository health improvement (60 → 52 branches)")
    print()
    
    print(f"🗑️ Executing deletion of {len(safe_branches)} verified safe branches:")
    for i, branch in enumerate(safe_branches, 1):
        print(f"   {i}. {branch}")
    print()
    
    # Create backup record before deletion
    backup_record = {
        "mission": "SSMT_v3_0_Phase_2_Deletion",
        "timestamp": datetime.now().isoformat(),
        "branches_deleted": [],
        "deletion_results": [],
        "safety_verified": True,
        "auto_executed": True
    }
    
    deletion_results = []
    successful_deletions = 0
    
    print("🛡️ Safety Check: Verifying branches exist before deletion...")
    
    for branch in safe_branches:
        print(f"\n🗑️ Deleting branch: {branch}")
        
        try:
            # First verify the branch exists
            check_result = subprocess.run(
                ["git", "show-ref", "--verify", f"refs/remotes/origin/{branch}"],
                capture_output=True,
                text=True,
                cwd="/workspaces/aurora-cloudbank-symbolic"
            )
            
            if check_result.returncode != 0:
                print(f"   ⚠️ Branch {branch} not found - may already be deleted")
                deletion_results.append({
                    "branch": branch,
                    "status": "not_found",
                    "message": "Branch not found - may already be deleted"
                })
                continue
            
            # Delete the remote branch
            delete_result = subprocess.run(
                ["git", "push", "origin", "--delete", branch],
                capture_output=True,
                text=True,
                cwd="/workspaces/aurora-cloudbank-symbolic"
            )
            
            if delete_result.returncode == 0:
                print(f"   ✅ Successfully deleted: {branch}")
                successful_deletions += 1
                deletion_results.append({
                    "branch": branch,
                    "status": "deleted",
                    "message": "Successfully deleted"
                })
                backup_record["branches_deleted"].append(branch)
            else:
                error_msg = delete_result.stderr.strip()
                print(f"   ❌ Failed to delete {branch}: {error_msg}")
                deletion_results.append({
                    "branch": branch,
                    "status": "failed",
                    "message": error_msg
                })
                
        except Exception as e:
            print(f"   💥 Exception deleting {branch}: {str(e)}")
            deletion_results.append({
                "branch": branch,
                "status": "exception", 
                "message": str(e)
            })
    
    # Update backup record
    backup_record["deletion_results"] = deletion_results
    backup_record["successful_deletions"] = successful_deletions
    backup_record["total_attempted"] = len(safe_branches)
    
    # Save backup record
    with open("phase_2_deletion_backup.json", "w") as f:
        json.dump(backup_record, f, indent=2)
    
    print(f"\n📊 Phase 2 Deletion Summary:")
    print(f"   ✅ Successfully deleted: {successful_deletions}/{len(safe_branches)} branches")
    print(f"   📁 Backup record saved: phase_2_deletion_backup.json")
    
    if successful_deletions > 0:
        print(f"\n🎯 Repository Health Improvement:")
        print(f"   📉 Branch count reduced by: {successful_deletions}")
        print(f"   🌳 Repository maintenance burden: REDUCED")
        print(f"   ✅ Mission status: {'COMPLETE' if successful_deletions == len(safe_branches) else 'PARTIAL SUCCESS'}")
    
    # Check final branch count
    try:
        branch_count_result = subprocess.run(
            ["git", "branch", "-r", "--format=%(refname:short)"],
            capture_output=True,
            text=True,
            cwd="/workspaces/aurora-cloudbank-symbolic"
        )
        
        if branch_count_result.returncode == 0:
            remaining_branches = len([b for b in branch_count_result.stdout.strip().split('\n') if b and not b.startswith('origin/HEAD')])
            print(f"   📊 Current remote branch count: {remaining_branches}")
    except:
        print("   📊 Could not determine final branch count")
    
    print(f"\n🏆 SSMT v3.0 Phase 2 Repository Pruning: {'SUCCESS!' if successful_deletions > 0 else 'NEEDS REVIEW'}")
    
    return {
        "successful_deletions": successful_deletions,
        "total_attempted": len(safe_branches),
        "deletion_results": deletion_results,
        "backup_file": "phase_2_deletion_backup.json"
    }

if __name__ == "__main__":
    result = execute_branch_deletions()
    exit(0 if result["successful_deletions"] > 0 else 1)