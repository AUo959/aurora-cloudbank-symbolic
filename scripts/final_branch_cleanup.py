#!/usr/bin/env python3
"""
Aurora CloudBank - Final Branch Cleanup Script
Completes ZERO PR strategy by cleaning remaining branches
"""

import logging

logger = logging.getLogger(__name__)

import subprocess
import sys
import json
from datetime import datetime

class FinalBranchCleanup:
    def __init__(self):
        self.deleted_branches = []
        self.failed_branches = []
        
        # PHASE 3 - Final cleanup of all remaining branches
        self.branches_to_delete = [
            "origin/codex/deprecate-crypto.js-and-update-imports",
            "origin/codex/design-pqn-modular-architecture-with-orion-integration", 
            "origin/codex/refactor-diagnostics-for-async-file-handling",
            "origin/codex/refactor-numeric-checks-in-aurora_api.py",
            "origin/codex/remove-large-binary-files-from-version-control",
            "origin/codex/replace-crypto.js-with-environment-keys",
            "origin/codex/validate-command-input-in-ethics_layer",
            "origin/feat/harvest-modules-cask-glyph-2025-09-18",
            "origin/feature/digital-ghost-dlp-sonar"
        ]
        
    def delete_remote_branch(self, branch_name):
        """Delete a remote branch with error handling"""
        try:
            # Extract branch name without origin/ prefix
            clean_branch = branch_name.replace("origin/", "")
            
            print(f"🗑️  Deleting branch: {clean_branch}")
            result = subprocess.run(
                ["git", "push", "origin", "--delete", clean_branch],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.deleted_branches.append(clean_branch)
            logger.info("Successfully deleted: %s", clean_branch)
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            logger.error("Failed to delete {clean_branch}: %s", error_msg)
            self.failed_branches.append({
                "branch": clean_branch,
                "error": error_msg
            })
            return False
    
    def run_cleanup(self):
        """Execute the final branch cleanup"""
        print("🚀 Starting final branch cleanup - %s branches", len(self.branches_to_delete))
        print("=" * 60)
        
        for branch in self.branches_to_delete:
            self.delete_remote_branch(branch)
            print()
        
        # Generate completion report
        self.generate_completion_report()
        
        return len(self.deleted_branches), len(self.failed_branches)
    
    def generate_completion_report(self):
        """Generate zero PR completion report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "phase": "ZERO_PR_COMPLETION",
            "deleted_branches": self.deleted_branches,
            "failed_branches": self.failed_branches,
            "total_deleted": len(self.deleted_branches),
            "total_failed": len(self.failed_branches),
            "status": "ZERO_PRS_ACHIEVED" if len(self.failed_branches) == 0 else "PARTIAL_CLEANUP"
        }
        
        with open("ZERO_PR_COMPLETION_REPORT.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "=" * 60)
        print("🎯 ZERO PR STRATEGY - COMPLETION REPORT")
        print("=" * 60)
        logger.info("Successfully deleted: %s branches", len(self.deleted_branches))
        logger.error("Failed deletions: %s branches", len(self.failed_branches))
        
        if self.deleted_branches:
            print(f"\n🗑️  Deleted branches:")
            for branch in self.deleted_branches:
                print(f"   - {branch}")
        
        if self.failed_branches:
            print(f"\n⚠️  Failed branches:")
            for failure in self.failed_branches:
                print(f"   - {failure['branch']}: {failure['error']}")
        
        print(f"\n📊 Report saved: ZERO_PR_COMPLETION_REPORT.json")
        
        if len(self.failed_branches) == 0:
            print("\n🎉 SUCCESS: ZERO OPEN PRS ACHIEVED!")
        else:
            print("")
# ⚠️  %s branches require manual review", len(self.failed_branches))

if __name__ == "__main__":
    cleanup = FinalBranchCleanup()
    deleted, failed = cleanup.run_cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)