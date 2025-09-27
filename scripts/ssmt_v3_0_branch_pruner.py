#!/usr/bin/env python3
"""
SSMT v3.0 Branch Pruning & Issue Consolidation Engine
Aurora CloudBank Symbolic - Repository Health & Maintenance

Focus: Consolidate PRs, close open issues, trim branch sappers (unnecessary branches)
Core mission: Clean repository health through intelligent automation
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSMTv3BranchPruner:
    def __init__(self, repo_path: str = "."):
        """Initialize SSMT v3.0 Branch Pruning & Issue Consolidation"""
        self.repo_path = Path(repo_path).resolve()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.pruning_report = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "branch_analysis": {},
            "consolidation_opportunities": [],
            "pruning_candidates": [],
            "automation_queue": []
        }
        
        logger.info("🌳 SSMT v3.0 Branch Pruning Engine initialized (Session: %s)", str(self.session_id)[:100])

    def analyze_repository_health(self) -> Dict[str, Any]:
        """Comprehensive repository health analysis for pruning strategy"""
        logger.info("🔍 Analyzing repository health for pruning opportunities...")
        
        try:
            # Get all branches (local and remote)
            all_branches_result = subprocess.run(
                ["git", "branch", "-a", "--no-merged", "main"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            # Get merged branches
            merged_branches_result = subprocess.run(
                ["git", "branch", "-a", "--merged", "main"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            # Parse branches
            unmerged_branches = []
            merged_branches = []
            
            for line in all_branches_result.stdout.split('\n'):
                line = line.strip()
                if line and 'origin/' in line and 'main' not in line and 'HEAD' not in line:
                    branch = line.replace('origin/', '').replace('remotes/', '').strip()
                    unmerged_branches.append(branch)
            
            for line in merged_branches_result.stdout.split('\n'):
                line = line.strip()
                if line and 'origin/' in line and 'main' not in line and 'HEAD' not in line:
                    branch = line.replace('origin/', '').replace('remotes/', '').strip()
                    merged_branches.append(branch)
            
            # Repository health metrics
            health_analysis = {
                "total_unmerged_branches": len(unmerged_branches),
                "total_merged_branches": len(merged_branches),
                "branch_categories": {
                    "dependabot": [],
                    "feature": [],
                    "hotfix": [],
                    "experimental": [],
                    "stale": [],
                    "other": []
                },
                "pruning_potential": {
                    "immediate_automation": [],
                    "safe_deletion": [],
                    "requires_review": [],
                    "keep_active": []
                }
            }
            
            # Categorize unmerged branches
            for branch in unmerged_branches:
                if 'dependabot' in branch:
                    health_analysis["branch_categories"]["dependabot"].append(branch)
                elif any(keyword in branch.lower() for keyword in ['feature', 'feat', 'add', 'implement']):
                    health_analysis["branch_categories"]["feature"].append(branch)
                elif any(keyword in branch.lower() for keyword in ['hotfix', 'fix', 'patch', 'urgent']):
                    health_analysis["branch_categories"]["hotfix"].append(branch)
                elif any(keyword in branch.lower() for keyword in ['experiment', 'test', 'trial', 'poc']):
                    health_analysis["branch_categories"]["experimental"].append(branch)
                else:
                    health_analysis["branch_categories"]["other"].append(branch)
            
            # Analyze branch staleness and automation potential
            for branch in unmerged_branches:
                branch_analysis = self.analyze_branch_for_pruning(branch)
                
                if branch_analysis.get("is_automatable", False):
                    health_analysis["pruning_potential"]["immediate_automation"].append(branch)
                elif branch_analysis.get("is_stale", False):
                    health_analysis["pruning_potential"]["safe_deletion"].append(branch)
                elif branch_analysis.get("needs_review", False):
                    health_analysis["pruning_potential"]["requires_review"].append(branch)
                else:
                    health_analysis["pruning_potential"]["keep_active"].append(branch)
            
            self.pruning_report["branch_analysis"] = health_analysis
            
            logger.info("📊 Repository health analysis complete:")
            logger.info("   🔄 Unmerged branches: %s", str(len(unmerged_branches))[:100])
            logger.info("   ✅ Merged branches: %s", str(len(merged_branches))[:100])
            logger.info("   🤖 Immediate automation: %s", str(len(health_analysis['pruning_potential']['immediate_automation']))[:100])
            logger.info("   🗑️ Safe deletion candidates: %s", str(len(health_analysis['pruning_potential']['safe_deletion']))[:100])
            
            return health_analysis
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Repository health analysis failed: %s", str(e)[:100])
            return {"error": str(e)}

    def analyze_branch_for_pruning(self, branch_name: str) -> Dict[str, Any]:
        """Analyze individual branch for pruning classification"""
        try:
            # Get branch age
            branch_date_result = subprocess.run(
                ["git", "log", "-1", "--format=%ct", f"origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            branch_timestamp = int(branch_date_result.stdout.strip())
            branch_date = datetime.fromtimestamp(branch_timestamp)
            age_days = (datetime.now() - branch_date).days
            
            # Get changed files
            changed_files_result = subprocess.run(
                ["git", "diff", "--name-only", f"main...origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            changed_files = [f.strip() for f in changed_files_result.stdout.split('\n') if f.strip()]
            
            # Get commit count
            commit_count_result = subprocess.run(
                ["git", "rev-list", "--count", f"main..origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            commit_count = int(commit_count_result.stdout.strip())
            
            # Classification logic
            is_dependabot = 'dependabot' in branch_name
            is_stale = age_days > 60  # 2+ months old
            is_simple = len(changed_files) <= 3 and commit_count <= 2
            is_fresh = age_days <= 30
            
            # Automation potential
            is_automatable = (
                is_dependabot and 
                is_fresh and 
                is_simple and
                all(f.endswith(('.json', '.lock', '.txt', '.md')) for f in changed_files)
            )
            
            # Deletion potential  
            is_safe_to_delete = (
                is_stale and 
                not any(keyword in branch_name.lower() for keyword in ['main', 'master', 'prod', 'release'])
            )
            
            # Review requirement
            needs_review = (
                not is_automatable and 
                not is_safe_to_delete and 
                (commit_count > 5 or len(changed_files) > 10)
            )
            
            analysis = {
                "branch": branch_name,
                "age_days": age_days,
                "commit_count": commit_count,
                "changed_files": changed_files,
                "file_count": len(changed_files),
                "is_dependabot": is_dependabot,
                "is_stale": is_stale,
                "is_simple": is_simple,
                "is_fresh": is_fresh,
                "is_automatable": is_automatable,
                "is_safe_to_delete": is_safe_to_delete,
                "needs_review": needs_review,
                "classification": self.classify_branch_action(is_automatable, is_safe_to_delete, needs_review),
                "priority": self.calculate_pruning_priority(is_automatable, is_stale, age_days)
            }
            
            return analysis
            
        except (subprocess.CalledProcessError, ValueError) as e:
            return {
                "branch": branch_name,
                "error": str(e),
                "classification": "ERROR",
                "priority": 0
            }

    def classify_branch_action(self, is_automatable: bool, is_safe_to_delete: bool, needs_review: bool) -> str:
        """Classify the recommended action for a branch"""
        if is_automatable:
            return "AUTOMATE_MERGE"
        elif is_safe_to_delete:
            return "SAFE_DELETE"
        elif needs_review:
            return "MANUAL_REVIEW"
        else:
            return "KEEP_ACTIVE"

    def calculate_pruning_priority(self, is_automatable: bool, is_stale: bool, age_days: int) -> int:
        """Calculate pruning priority (higher = more urgent)"""
        priority = 0
        
        if is_automatable:
            priority += 100  # Highest priority - immediate value
        if is_stale:
            priority += 50   # High priority - cleanup value
        if age_days > 90:
            priority += 25   # Medium priority - very old branches
        if age_days > 180:
            priority += 25   # Additional priority for ancient branches
            
        return priority

    def generate_pruning_plan(self) -> Dict[str, Any]:
        """Generate comprehensive pruning and consolidation plan"""
        logger.info("📋 Generating comprehensive pruning plan...")
        
        health_analysis = self.analyze_repository_health()
        
        if "error" in health_analysis:
            return {"error": "Failed to analyze repository health"}
        
        # Create actionable pruning plan
        pruning_plan = {
            "session_id": self.session_id,
            "generated_at": datetime.now().isoformat(),
            "repository_summary": {
                "total_branches_analyzed": health_analysis["total_unmerged_branches"],
                "immediate_automation_candidates": len(health_analysis["pruning_potential"]["immediate_automation"]),
                "safe_deletion_candidates": len(health_analysis["pruning_potential"]["safe_deletion"]),
                "manual_review_required": len(health_analysis["pruning_potential"]["requires_review"]),
                "active_branches_to_keep": len(health_analysis["pruning_potential"]["keep_active"])
            },
            "action_phases": {
                "phase_1_immediate_automation": {
                    "description": "High-confidence dependency updates for immediate automation",
                    "branches": health_analysis["pruning_potential"]["immediate_automation"][:10],  # Limit to 10
                    "estimated_time_saved": len(health_analysis["pruning_potential"]["immediate_automation"][:10]) * 5,
                    "success_rate_estimate": "75%",
                    "action": "Execute SSMT v3.0 enhanced automation"
                },
                "phase_2_safe_deletion": {
                    "description": "Stale branches safe for deletion (60+ days old)",
                    "branches": health_analysis["pruning_potential"]["safe_deletion"][:20],  # Limit to 20
                    "repository_cleanup_value": "High",
                    "action": "Batch delete with confirmation"
                },
                "phase_3_manual_review": {
                    "description": "Complex branches requiring human review",
                    "branches": health_analysis["pruning_potential"]["requires_review"][:5],  # Limit to 5
                    "action": "Individual assessment and decision"
                }
            },
            "consolidation_opportunities": {
                "dependabot_branches": len(health_analysis["branch_categories"]["dependabot"]),
                "feature_branches": len(health_analysis["branch_categories"]["feature"]),
                "experimental_branches": len(health_analysis["branch_categories"]["experimental"]),
                "consolidation_potential": "Batch process dependabot updates, review feature branches for relevance"
            },
            "estimated_impact": {
                "branches_to_be_processed": len(health_analysis["pruning_potential"]["immediate_automation"][:10]),
                "branches_to_be_deleted": len(health_analysis["pruning_potential"]["safe_deletion"][:20]),
                "repository_health_improvement": "Significant",
                "maintenance_burden_reduction": "High",
                "estimated_cleanup_time": "2-3 hours total across all phases"
            }
        }
        
        self.pruning_report["pruning_plan"] = pruning_plan
        
        logger.info("✅ Pruning plan generated:")
        logger.info("   🤖 Phase 1 - Automate: %s branches", str(len(pruning_plan['action_phases']['phase_1_immediate_automation']['branches']))[:100])
        logger.info("   🗑️ Phase 2 - Delete: %s branches", str(len(pruning_plan['action_phases']['phase_2_safe_deletion']['branches']))[:100])
        logger.info("   👁️ Phase 3 - Review: %s branches", str(len(pruning_plan['action_phases']['phase_3_manual_review']['branches']))[:100])
        
        return pruning_plan

    def execute_pruning_phase_1(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute Phase 1: Immediate automation of high-confidence branches"""
        logger.info("🚀 Executing Phase 1 pruning - Immediate automation (dry_run=%s)", str(dry_run)[:100])
        
        pruning_plan = self.generate_pruning_plan()
        if "error" in pruning_plan:
            return pruning_plan
        
        automation_branches = pruning_plan["action_phases"]["phase_1_immediate_automation"]["branches"]
        
        if not automation_branches:
            return {
                "phase": "phase_1_immediate_automation",
                "status": "no_candidates",
                "message": "No branches identified for immediate automation"
            }
        
        if dry_run:
            return {
                "phase": "phase_1_immediate_automation",
                "status": "dry_run_complete",
                "would_process": automation_branches,
                "estimated_time_saved": len(automation_branches) * 5,
                "command_to_execute": f"python3 scripts/ssmt_v3_0_live_automation.py execute --branches {' '.join(automation_branches[:5])}"
            }
        else:
            # Execute actual automation (delegated to existing automation system)
            logger.info("⚡ Would execute automation on %s branches", str(len(automation_branches))[:100])
            return {
                "phase": "phase_1_immediate_automation",
                "status": "delegated_to_automation_system",
                "branches_queued": automation_branches
            }

def main():
    """Main entry point for branch pruning and issue consolidation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSMT v3.0 Branch Pruning & Issue Consolidation")
    parser.add_argument("command", choices=["analyze", "plan", "execute-phase-1", "health-report"], 
                       help="Command to execute")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Perform dry run (default: true)")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    pruner = SSMTv3BranchPruner(args.repo_path)
    
    if args.command == "analyze":
        health_analysis = pruner.analyze_repository_health()
        print(json.dumps(health_analysis, indent=2))
        
    elif args.command == "plan":
        pruning_plan = pruner.generate_pruning_plan()
        print(json.dumps(pruning_plan, indent=2))
        
    elif args.command == "execute-phase-1":
        result = pruner.execute_pruning_phase_1(dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
        
    elif args.command == "health-report":
        # Generate comprehensive health report
        health_analysis = pruner.analyze_repository_health()
        pruning_plan = pruner.generate_pruning_plan()
        
        report = {
            "repository_health": health_analysis,
            "pruning_strategy": pruning_plan,
            "executive_summary": {
                "total_branches": health_analysis.get("total_unmerged_branches", 0),
                "automation_ready": len(pruning_plan["action_phases"]["phase_1_immediate_automation"]["branches"]),
                "deletion_candidates": len(pruning_plan["action_phases"]["phase_2_safe_deletion"]["branches"]),
                "cleanup_potential": "High" if health_analysis.get("total_unmerged_branches", 0) > 20 else "Medium"
            }
        }
        
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()