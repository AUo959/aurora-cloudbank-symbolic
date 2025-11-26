#!/usr/bin/env python3
"""
SSMT v3.0 Live Automation Executor
Aurora CloudBank Symbolic - Production Automation with Safety

This script executes live automation on verified easy wins with comprehensive
safety checks, backup creation, and rollback capabilities.
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSMTv3LiveAutomation:
    def __init__(self, repo_path: str = "."):
        """Initialize SSMT v3.0 Live Automation with safety protocols"""
        self.repo_path = Path(repo_path).resolve()
        self.backup_dir = self.repo_path / ".ssmt_backups"
        self.audit_log = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info("🚀 SSMT v3.0 Live Automation initialized (Session: %s)", str(self.session_id)[:100])

    def create_safety_backup(self) -> Dict[str, Any]:
        """Create comprehensive safety backup before automation"""
        logger.info("🛡️ Creating safety backup...")
        
        try:
            # Get current branch and commit
            current_branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            ).stdout.strip()
            
            current_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            ).stdout.strip()
            
            # Create backup info
            backup_info = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "current_branch": current_branch,
                "current_commit": current_commit,
                "backup_created": True,
                "rollback_command": f"git reset --hard {current_commit}"
            }
            
            # Save backup info
            backup_file = self.backup_dir / f"backup_{self.session_id}.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info("✅ Safety backup created: %s", str(backup_file)[:100])
            return backup_info
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Failed to create safety backup: %s", str(e)[:100])
            raise

    def validate_branch_safety(self, branch_name: str) -> Dict[str, Any]:
        """Validate branch safety before automation"""
        logger.info("🔍 Validating branch safety: %s", str(branch_name)[:100])
        
        try:
            # Check if branch exists
            subprocess.run(
                ["git", "show-ref", "--verify", f"refs/remotes/origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, check=True
            )
            
            # Get changed files
            changed_files_result = subprocess.run(
                ["git", "diff", "--name-only", f"main...origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            changed_files = [f.strip() for f in changed_files_result.stdout.split('\n') if f.strip()]
            
            # Safety validation rules
            is_safe = (
                len(changed_files) <= 3 and  # Limited file changes
                all(f.endswith(('.json', '.lock', '.txt', '.md')) for f in changed_files) and  # Safe file types
                not any('src/' in f or 'modules/' in f for f in changed_files) and  # No source code
                'dependabot' in branch_name  # Dependabot branch
            )
            
            validation = {
                "branch": branch_name,
                "changed_files": changed_files,
                "file_count": len(changed_files),
                "is_safe": is_safe,
                "safety_score": 95 if is_safe else 30,
                "validation_passed": is_safe,
                "timestamp": datetime.now().isoformat()
            }
            
            if is_safe:
                logger.info("✅ Branch validation passed: %s", str(branch_name)[:100])
            else:
                logger.warning("⚠️ Branch validation failed: %s", str(branch_name)[:100])
                
            return validation
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Branch validation failed: %s", str(e)[:100])
            return {
                "branch": branch_name,
                "validation_passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def execute_safe_merge(self, branch_name: str, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute safe merge with comprehensive error handling"""
        logger.info("🔧 Executing safe merge: %s", str(branch_name)[:100])
        
        merge_result = {
            "branch": branch_name,
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "success": False,
            "steps_completed": [],
            "rollback_performed": False
        }
        
        try:
            # Step 1: Fetch latest changes
            logger.info("📥 Fetching latest changes...")
            subprocess.run(["git", "fetch", "origin"], cwd=self.repo_path, check=True)
            merge_result["steps_completed"].append("fetch_completed")
            
            # Step 2: Ensure we're on main
            logger.info("🔄 Switching to main branch...")
            subprocess.run(["git", "checkout", "main"], cwd=self.repo_path, check=True)
            merge_result["steps_completed"].append("checkout_main")
            
            # Step 3: Pull latest main
            logger.info("⬇️ Pulling latest main...")
            subprocess.run(["git", "pull", "origin", "main"], cwd=self.repo_path, check=True)
            merge_result["steps_completed"].append("pull_main")
            
            # Step 4: Execute merge
            logger.info("🔗 Merging %s...", str(branch_name)[:100])
            merge_cmd = subprocess.run(
                ["git", "merge", "--no-ff", f"origin/{branch_name}", "-m", f"🤖 SSMT v3.0 Auto-merge: {branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            if merge_cmd.returncode == 0:
                merge_result["steps_completed"].append("merge_completed")
                logger.info("✅ Merge completed successfully")
                
                # Step 5: Push to origin
                logger.info("⬆️ Pushing to origin...")
                subprocess.run(["git", "push", "origin", "main"], cwd=self.repo_path, check=True)
                merge_result["steps_completed"].append("push_completed")
                
                # Step 6: Delete merged branch
                logger.info("🗑️ Cleaning up merged branch...")
                subprocess.run(["git", "push", "origin", "--delete", branch_name], cwd=self.repo_path, check=True)
                merge_result["steps_completed"].append("branch_cleanup")
                
                merge_result["success"] = True
                merge_result["completed_at"] = datetime.now().isoformat()
                logger.info("🎉 Successfully automated merge of %s", str(branch_name)[:100])
                
            else:
                # Merge failed - execute rollback
                logger.error("❌ Merge failed: %s", str(merge_cmd.stderr)[:100])
                merge_result["error"] = merge_cmd.stderr
                merge_result["rollback_performed"] = self.execute_emergency_rollback(backup_info)
                
        except subprocess.CalledProcessError as e:
            logger.error("❌ Merge execution failed: %s", str(e)[:100])
            merge_result["error"] = str(e)
            merge_result["rollback_performed"] = self.execute_emergency_rollback(backup_info)
            
        return merge_result

    def execute_emergency_rollback(self, backup_info: Dict[str, Any]) -> bool:
        """Execute emergency rollback to safe state"""
        logger.warning("🚨 Executing emergency rollback...")
        
        try:
            # Reset to backup commit
            subprocess.run(
                ["git", "reset", "--hard", backup_info["current_commit"]],
                cwd=self.repo_path, check=True
            )
            
            # Force push if needed (only in emergency)
            subprocess.run(
                ["git", "push", "origin", "main", "--force-with-lease"],
                cwd=self.repo_path, check=True
            )
            
            logger.info("✅ Emergency rollback completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Emergency rollback failed: %s", str(e)[:100])
            return False

    def execute_automation_batch(self, branches: List[str]) -> Dict[str, Any]:
        """Execute automation on a batch of verified easy win branches"""
        logger.info("🚀 Starting automation batch: %s branches", str(len(branches))[:100])
        
        # Create safety backup
        backup_info = self.create_safety_backup()
        
        batch_results = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "backup_info": backup_info,
            "total_branches": len(branches),
            "results": [],
            "summary": {
                "successful": 0,
                "failed": 0,
                "rollbacks": 0
            }
        }
        
        for branch in branches:
            logger.info("\n🔄 Processing branch %s/%s: %s", str(batch_results['summary']['successful'] + batch_results['summary']['failed'] + 1)[:100], str(len(branches))[:100], str(branch)[:100])
            
            # Validate branch safety
            validation = self.validate_branch_safety(branch)
            
            if validation.get("validation_passed", False):
                # Execute safe merge
                merge_result = self.execute_safe_merge(branch, backup_info)
                batch_results["results"].append(merge_result)
                
                if merge_result["success"]:
                    batch_results["summary"]["successful"] += 1
                else:
                    batch_results["summary"]["failed"] += 1
                    if merge_result.get("rollback_performed", False):
                        batch_results["summary"]["rollbacks"] += 1
            else:
                # Skip unsafe branch
                skip_result = {
                    "branch": branch,
                    "skipped": True,
                    "reason": "Failed safety validation",
                    "validation": validation
                }
                batch_results["results"].append(skip_result)
                batch_results["summary"]["failed"] += 1
        
        batch_results["completed_at"] = datetime.now().isoformat()
        
        # Save batch results
        results_file = self.backup_dir / f"automation_results_{self.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump(batch_results, f, indent=2)
        
        logger.info("📊 Batch automation completed: %s", str(batch_results['summary'])[:100])
        return batch_results

def main():
    """Main entry point for live automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSMT v3.0 Live Automation Executor")
    parser.add_argument("command", choices=["execute", "validate", "rollback"], 
                       help="Command to execute")
    parser.add_argument("--branches", nargs="+", help="Branch names to process")
    parser.add_argument("--easy-wins", action="store_true", 
                       help="Use predefined easy win branches")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    # Predefined easy win branches (from our analysis)
    EASY_WIN_BRANCHES = [
        "dependabot/npm_and_yarn/babel/core-7.28.4",
        "dependabot/npm_and_yarn/concurrently-9.2.1", 
        "dependabot/npm_and_yarn/dotenv-17.1.0",
        "dependabot/npm_and_yarn/eslint-9.30.1",
        "dependabot/npm_and_yarn/eslint-9.36.0"
    ]
    
    automator = SSMTv3LiveAutomation(args.repo_path)
    
    if args.command == "execute":
        branches = EASY_WIN_BRANCHES if args.easy_wins else (args.branches or [])
        
        if not branches:
            logger.error("No branches specified. Use --easy-wins or --branches")
            sys.exit(1)
        
        print(f"🚀 Executing live automation on {len(branches)} branches...")
        logger.warning("This will make real changes to the repository!")
        
        confirmation = input("Type 'EXECUTE' to proceed: ")
        if confirmation != "EXECUTE":
            print("🚫 Automation cancelled")
            sys.exit(0)
        
        results = automator.execute_automation_batch(branches)
        print(json.dumps(results, indent=2))
        
    elif args.command == "validate":
        branches = EASY_WIN_BRANCHES if args.easy_wins else (args.branches or [])
        
        if not branches:
            logger.error("No branches specified")
            sys.exit(1)
        
        for branch in branches:
            validation = automator.validate_branch_safety(branch)
            print(json.dumps(validation, indent=2))

if __name__ == "__main__":
    main()