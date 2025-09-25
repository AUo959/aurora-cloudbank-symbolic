#!/usr/bin/env python3
"""
SSMT v3.0 Enhanced Live Automation (v2)
Aurora CloudBank Symbolic - Improved automation with freshness and pre-merge validation

Based on live automation learnings: branch freshness, pre-merge simulation, 
defensive cleanup, and enhanced safety checks.
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSMTv3EnhancedAutomation:
    def __init__(self, repo_path: str = "."):
        """Initialize SSMT v3.0 Enhanced Automation with improved safety"""
        self.repo_path = Path(repo_path).resolve()
        self.backup_dir = self.repo_path / ".ssmt_backups"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Enhanced configuration
        self.max_branch_age_days = 30
        self.min_safety_score = 90
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info("🚀 SSMT v3.0 Enhanced Automation initialized (Session: %s)", str(self.session_id)[:100])

    def check_branch_freshness(self, branch_name: str) -> Dict[str, Any]:
        """Check if branch is fresh enough for safe automation"""
        logger.info("📅 Checking branch freshness: %s", str(branch_name)[:100])
        
        try:
            # Get branch last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct", f"origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            branch_timestamp = int(result.stdout.strip())
            branch_date = datetime.fromtimestamp(branch_timestamp)
            
            # Get main branch last commit date
            main_result = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "origin/main"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            main_timestamp = int(main_result.stdout.strip())
            main_date = datetime.fromtimestamp(main_timestamp)
            
            # Calculate freshness
            age_days = (main_date - branch_date).days
            is_fresh = age_days <= self.max_branch_age_days
            
            freshness_info = {
                "branch": branch_name,
                "branch_date": branch_date.isoformat(),
                "main_date": main_date.isoformat(),
                "age_days": age_days,
                "is_fresh": is_fresh,
                "max_age_allowed": self.max_branch_age_days,
                "freshness_score": max(0, 100 - (age_days * 2))  # Decrease 2 points per day
            }
            
            if is_fresh:
                logger.info("✅ Branch is fresh: %s days old", str(age_days)[:100])
            else:
                logger.warning("⚠️ Branch is stale: %s days old (max: %s)", str(age_days)[:100], str(self.max_branch_age_days)[:100])
            
            return freshness_info
            
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.error("❌ Failed to check branch freshness: %s", str(e)[:100])
            return {
                "branch": branch_name,
                "error": str(e),
                "is_fresh": False,
                "freshness_score": 0
            }

    def simulate_merge(self, branch_name: str) -> Dict[str, Any]:
        """Simulate merge in temporary branch to detect conflicts"""
        logger.info("🧪 Simulating merge for: %s", str(branch_name)[:100])
        
        temp_branch = f"ssmt_test_{self.session_id}_{branch_name.replace('/', '_')}"
        
        try:
            # Create temporary branch from main
            subprocess.run(
                ["git", "checkout", "-b", temp_branch, "origin/main"],
                cwd=self.repo_path, capture_output=True, check=True
            )
            
            # Attempt merge (no commit)
            merge_result = subprocess.run(
                ["git", "merge", "--no-commit", "--no-ff", f"origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            simulation_result = {
                "branch": branch_name,
                "temp_branch": temp_branch,
                "merge_success": merge_result.returncode == 0,
                "conflicts_detected": merge_result.returncode != 0,
                "merge_output": merge_result.stdout,
                "merge_errors": merge_result.stderr
            }
            
            if merge_result.returncode == 0:
                # Check what would be merged
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.repo_path, capture_output=True, text=True, check=True
                )
                
                simulation_result["staged_changes"] = len([
                    line for line in status_result.stdout.split('\n') 
                    if line.strip()
                ])
                
                logger.info("✅ Merge simulation successful: %s changes", str(simulation_result['staged_changes'])[:100])
            else:
                logger.warning("⚠️ Merge simulation detected conflicts")
            
            # Reset merge (abort without committing)
            subprocess.run(
                ["git", "merge", "--abort"],
                cwd=self.repo_path, capture_output=True
            )
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Merge simulation failed: %s", str(e)[:100])
            simulation_result = {
                "branch": branch_name,
                "temp_branch": temp_branch,
                "merge_success": False,
                "error": str(e)
            }
        
        finally:
            # Clean up temporary branch
            try:
                subprocess.run(
                    ["git", "checkout", "main"],
                    cwd=self.repo_path, capture_output=True
                )
                subprocess.run(
                    ["git", "branch", "-D", temp_branch],
                    cwd=self.repo_path, capture_output=True
                )
            except subprocess.CalledProcessError:
                pass  # Cleanup failed, but not critical
        
        return simulation_result

    def enhanced_branch_validation(self, branch_name: str) -> Dict[str, Any]:
        """Enhanced branch validation with freshness and merge simulation"""
        logger.info("🔍 Enhanced validation for: %s", str(branch_name)[:100])
        
        # Basic safety validation
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
            
            # Check freshness
            freshness_info = self.check_branch_freshness(branch_name)
            
            # Simulate merge
            merge_simulation = self.simulate_merge(branch_name)
            
            # Enhanced safety scoring
            base_safety = 30
            
            # File-based scoring
            if len(changed_files) <= 2:
                base_safety += 20
            if all(f.endswith(('.json', '.lock', '.txt', '.md')) for f in changed_files):
                base_safety += 20
            if not any('src/' in f or 'modules/' in f for f in changed_files):
                base_safety += 15
            if 'dependabot' in branch_name:
                base_safety += 10
            
            # Freshness scoring
            base_safety += min(20, freshness_info.get('freshness_score', 0) // 5)
            
            # Merge simulation scoring
            if merge_simulation.get('merge_success', False):
                base_safety += 15
            
            # Final validation
            is_safe = (
                base_safety >= self.min_safety_score and
                freshness_info.get('is_fresh', False) and
                merge_simulation.get('merge_success', False) and
                len(changed_files) <= 3
            )
            
            validation = {
                "branch": branch_name,
                "changed_files": changed_files,
                "file_count": len(changed_files),
                "freshness_info": freshness_info,
                "merge_simulation": merge_simulation,
                "safety_score": base_safety,
                "is_safe": is_safe,
                "validation_passed": is_safe,
                "timestamp": datetime.now().isoformat(),
                "validation_criteria": {
                    "min_safety_score": self.min_safety_score,
                    "max_branch_age_days": self.max_branch_age_days,
                    "merge_simulation_required": True
                }
            }
            
            if is_safe:
                logger.info("✅ Enhanced validation passed: %s (score: %s)", str(branch_name)[:100], str(base_safety)[:100])
            else:
                logger.warning("⚠️ Enhanced validation failed: %s (score: %s)", str(branch_name)[:100], str(base_safety)[:100])
                
            return validation
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Enhanced validation failed: %s", str(e)[:100])
            return {
                "branch": branch_name,
                "validation_passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def defensive_branch_cleanup(self, branch_name: str) -> Dict[str, Any]:
        """Defensive branch cleanup with existence checking"""
        logger.info("🗑️ Defensive cleanup for: %s", str(branch_name)[:100])
        
        try:
            # Check if branch exists on remote
            check_result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", branch_name],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            if check_result.stdout.strip():
                # Branch exists, proceed with deletion
                subprocess.run(
                    ["git", "push", "origin", "--delete", branch_name],
                    cwd=self.repo_path, check=True
                )
                
                return {
                    "branch": branch_name,
                    "cleanup_performed": True,
                    "method": "remote_deletion",
                    "success": True
                }
            else:
                # Branch doesn't exist, no cleanup needed
                logger.info("ℹ️ Branch %s already removed, skipping cleanup", str(branch_name)[:100])
                return {
                    "branch": branch_name,
                    "cleanup_performed": False,
                    "method": "already_deleted",
                    "success": True
                }
                
        except subprocess.CalledProcessError as e:
            logger.warning("⚠️ Branch cleanup failed (non-critical): %s", str(e)[:100])
            return {
                "branch": branch_name,
                "cleanup_performed": False,
                "error": str(e),
                "success": False
            }

    def find_fresh_easy_wins(self, max_results: int = 10) -> List[str]:
        """Find fresh dependabot branches for automation"""
        logger.info("🔎 Finding fresh easy wins (max: %s)", str(max_results)[:100])
        
        try:
            # Get all dependabot branches
            result = subprocess.run(
                ["git", "branch", "-r", "--no-merged", "main"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            dependabot_branches = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if 'dependabot' in line and 'origin/' in line:
                    branch = line.replace('origin/', '').strip()
                    dependabot_branches.append(branch)
            
            # Filter by freshness and validate
            fresh_branches = []
            for branch in dependabot_branches:
                freshness = self.check_branch_freshness(branch)
                if freshness.get('is_fresh', False):
                    fresh_branches.append((branch, freshness['age_days']))
            
            # Sort by freshness (newest first)
            fresh_branches.sort(key=lambda x: x[1])
            
            # Return just branch names, limited by max_results
            result_branches = [branch for branch, _ in fresh_branches[:max_results]]
            
            logger.info("📋 Found %s fresh easy win candidates", str(len(result_branches))[:100])
            return result_branches
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Failed to find fresh easy wins: %s", str(e)[:100])
            return []

def main():
    """Main entry point for enhanced live automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSMT v3.0 Enhanced Live Automation")
    parser.add_argument("command", choices=["find-fresh", "validate", "execute"], 
                       help="Command to execute")
    parser.add_argument("--branches", nargs="+", help="Branch names to process")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum results to return")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    automator = SSMTv3EnhancedAutomation(args.repo_path)
    
    if args.command == "find-fresh":
        fresh_branches = automator.find_fresh_easy_wins(args.max_results)
        result = {
            "session_id": automator.session_id,
            "fresh_branches_found": len(fresh_branches),
            "branches": fresh_branches,
            "criteria": {
                "max_age_days": automator.max_branch_age_days,
                "max_results": args.max_results
            }
        }
        print(json.dumps(result, indent=2))
        
    elif args.command == "validate":
        branches = args.branches or []
        if not branches:
            print("❌ No branches specified for validation")
            sys.exit(1)
        
        for branch in branches:
            validation = automator.enhanced_branch_validation(branch)
            print(json.dumps(validation, indent=2))
            print("---")

if __name__ == "__main__":
    main()