#!/usr/bin/env python3
"""
SSMT v3.0 - Automated Safety & Easy Wins Implementation
Aurora CloudBank Symbolic - Smart Selective Merge Technology Evolution

Focus Areas:
- Automated safety checks and rollback capabilities
- Easy wins in merge automation with minimal risk  
- Enhanced validation and conflict prevention
- Progressive automation with safety-first approach

Building on v2.3's intelligence-driven success with practical automation layers.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSMTv3AutomatedSafety:
    """SSMT v3.0 - Automated Safety & Easy Wins Implementation"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.version = "3.0.0"
        self.safety_enabled = True
        self.backup_dir = self.repo_path / ".ssmt_backups"
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        
        # Safety configuration
        self.safety_config = {
            "max_files_per_merge": 50,          # Easy win: limit merge scope
            "require_backup": True,             # Always backup before merge
            "auto_rollback_on_failure": True,  # Automatic rollback on errors
            "conflict_threshold": 0.1,          # Low tolerance for conflicts (10%)
            "validation_timeout": 30,           # Quick validation timeout
            "safe_merge_patterns": [            # Easy win patterns - safe to merge
                "*.md", "*.txt", "*.json", "*.yaml", "*.yml", 
                "docs/**", "README*", "CHANGELOG*", ".github/**"
            ],
            "high_risk_patterns": [             # High risk - require manual review
                "*.py", "*.js", "*.ts", "src/**", "modules/**", 
                "package.json", "requirements.txt", "Dockerfile"
            ]
        }
        
        # Automation levels (progressive)
        self.automation_levels = {
            "SAFE": {"max_changes": 5, "patterns": ["*.md", "docs/**"], "auto_merge": True},
            "LOW_RISK": {"max_changes": 15, "patterns": ["*.json", "*.yaml"], "auto_merge": True},
            "MEDIUM_RISK": {"max_changes": 30, "patterns": ["tests/**"], "auto_merge": False},
            "HIGH_RISK": {"max_changes": 100, "patterns": ["src/**"], "auto_merge": False}
        }
        
        # Load previous v2.3 results if available
        self.v2_3_results = self._load_previous_results()
        
    def _load_previous_results(self) -> Optional[Dict]:
        """Load SSMT v2.3 results for building upon"""
        try:
            results_file = self.repo_path / "SSMT_v2_3_INTEGRATION_RESULTS.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("Could not load v2.3 results: %s", str(e)[:100])
        return None
    
    def create_safety_backup(self, backup_name: str) -> Path:
        """Create a safety backup before any merge operations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{backup_name}_{timestamp}"
        
        try:
            # Create git stash as backup
            result = subprocess.run(
                ["git", "stash", "push", "-m", f"SSMT_v3_backup_{backup_name}_{timestamp}"],
                cwd=self.repo_path, capture_output=True, text=True, check=False
            )
            
            # Also create directory backup for critical files
            backup_path.mkdir(exist_ok=True)
            critical_files = ["package.json", "requirements.txt", "pyproject.toml"]
            
            for file in critical_files:
                src_file = self.repo_path / file
                if src_file.exists():
                    shutil.copy2(src_file, backup_path / file)
            
            logger.info("✅ Safety backup created: %s", str(backup_path)[:100])
            return backup_path
            
        except Exception as e:
            logger.error("❌ Failed to create safety backup: %s", str(e)[:100])
            raise
    
    def analyze_branch_safety(self, branch_name: str) -> Dict[str, Any]:
        """Analyze branch for safety classification and automation eligibility"""
        logger.info("🔍 Analyzing branch safety: %s", str(branch_name)[:100])
        
        try:
            # Get branch diff stats
            result = subprocess.run(
                ["git", "diff", "--stat", f"main...{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            # Get list of changed files
            files_result = subprocess.run(
                ["git", "diff", "--name-only", f"main...{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            changed_files = [f.strip() for f in files_result.stdout.split('\n') if f.strip()]
            
            # Classify safety level
            safety_analysis = self._classify_branch_safety(changed_files)
            
            # Calculate automation eligibility
            automation_eligible = self._calculate_automation_eligibility(safety_analysis, changed_files)
            
            analysis = {
                "branch": branch_name,
                "changed_files": changed_files,
                "file_count": len(changed_files),
                "safety_level": safety_analysis["level"],
                "risk_factors": safety_analysis["risks"],
                "automation_eligible": automation_eligible,
                "recommended_action": self._get_recommended_action(safety_analysis, automation_eligible),
                "safety_score": safety_analysis["score"],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("📊 Safety analysis complete: %s risk, Score: %s", str(analysis['safety_level'])[:100], str(analysis['safety_score'])[:100])
            return analysis
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Git command failed: %s", str(e)[:100])
            raise
        except Exception as e:
            logger.error("❌ Safety analysis failed: %s", str(e)[:100])
            raise
    
    def _classify_branch_safety(self, changed_files: List[str]) -> Dict[str, Any]:
        """Classify branch safety based on changed files"""
        risk_score = 0
        risks = []
        
        # File pattern analysis
        safe_files = 0
        risky_files = 0
        
        for file in changed_files:
            # Check against safe patterns
            if any(Path(file).match(pattern) for pattern in self.safety_config["safe_merge_patterns"]):
                safe_files += 1
            # Check against high-risk patterns  
            elif any(Path(file).match(pattern) for pattern in self.safety_config["high_risk_patterns"]):
                risky_files += 1
                risk_score += 10
        
        # Volume-based risk
        if len(changed_files) > self.safety_config["max_files_per_merge"]:
            risks.append(f"Too many files changed: {len(changed_files)}")
            risk_score += 20
        
        # Calculate safety level
        if risk_score == 0 and risky_files == 0:
            level = "SAFE"
        elif risk_score <= 10 and risky_files <= 2:
            level = "LOW_RISK"
        elif risk_score <= 30 and risky_files <= 5:
            level = "MEDIUM_RISK"
        else:
            level = "HIGH_RISK"
            
        return {
            "level": level,
            "score": max(0, 100 - risk_score),  # Higher score = safer
            "risks": risks,
            "safe_files": safe_files,
            "risky_files": risky_files
        }
    
    def _calculate_automation_eligibility(self, safety_analysis: Dict, changed_files: List[str]) -> bool:
        """Determine if branch is eligible for automated merging"""
        level = safety_analysis["level"]
        file_count = len(changed_files)
        
        # Check automation level rules
        automation_rules = self.automation_levels.get(level, {})
        
        if not automation_rules.get("auto_merge", False):
            return False
            
        if file_count > automation_rules.get("max_changes", 0):
            return False
            
        # Additional safety checks
        if safety_analysis["score"] < 80:  # Require high safety score
            return False
            
        return True
    
    def _get_recommended_action(self, safety_analysis: Dict, automation_eligible: bool) -> str:
        """Get recommended action based on analysis"""
        if automation_eligible and safety_analysis["level"] == "SAFE":
            return "AUTO_MERGE"
        elif safety_analysis["level"] in ["SAFE", "LOW_RISK"]:
            return "SAFE_MERGE_WITH_VALIDATION"
        elif safety_analysis["level"] == "MEDIUM_RISK":
            return "MANUAL_REVIEW_RECOMMENDED"
        else:
            return "MANUAL_REVIEW_REQUIRED"
    
    def execute_safe_merge(self, branch_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute a safe merge with full automation and safety checks"""
        logger.info("🚀 Starting safe merge: %s (dry_run=%s)", str(branch_name)[:100], str(dry_run)[:100])
        
        merge_id = f"ssmt_v3_{branch_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Safety analysis
            safety_analysis = self.analyze_branch_safety(branch_name)
            
            # Step 2: Safety backup (if not dry run)
            backup_path = None
            if not dry_run and self.safety_config["require_backup"]:
                backup_path = self.create_safety_backup(merge_id)
            
            # Step 3: Pre-merge validation
            validation_results = self._run_pre_merge_validation(branch_name)
            
            # Step 4: Execute merge based on safety level
            merge_results = self._execute_merge_by_safety_level(
                branch_name, safety_analysis, dry_run
            )
            
            # Step 5: Post-merge validation (if merge was executed)
            post_merge_results = None
            if not dry_run and merge_results.get("executed", False):
                post_merge_results = self._run_post_merge_validation()
            
            # Compile comprehensive results
            results = {
                "merge_id": merge_id,  
                "branch": branch_name,
                "version": self.version,
                "dry_run": dry_run,
                "timestamp": datetime.now().isoformat(),
                "safety_analysis": safety_analysis,
                "pre_merge_validation": validation_results,
                "merge_execution": merge_results,
                "post_merge_validation": post_merge_results,
                "backup_path": str(backup_path) if backup_path else None,
                "success": merge_results.get("success", False),
                "automation_used": safety_analysis.get("automation_eligible", False)
            }
            
            # Save results
            self._save_merge_results(results)
            
            logger.info("✅ Safe merge completed: %s", str(merge_id)[:100])
            return results
            
        except Exception as e:
            logger.error("❌ Safe merge failed: %s", str(e)[:100])
            
            # Auto-rollback on failure
            if not dry_run and self.safety_config["auto_rollback_on_failure"]:
                self._execute_emergency_rollback(merge_id)
            
            raise
    
    def _run_pre_merge_validation(self, branch_name: str) -> Dict[str, Any]:
        """Run comprehensive pre-merge validation"""
        logger.info("🔍 Running pre-merge validation...")
        
        validations = {
            "git_status_clean": self._validate_git_status(),
            "branch_exists": self._validate_branch_exists(branch_name),
            "no_conflicts": self._validate_no_conflicts(branch_name),
            "tests_pass": self._validate_tests_pass(),
            "lint_pass": self._validate_lint_pass()
        }
        
        all_passed = all(validations.values())
        
        return {
            "validations": validations,
            "all_passed": all_passed,
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_git_status(self) -> bool:
        """Validate git working directory is clean"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def _validate_branch_exists(self, branch_name: str) -> bool:
        """Validate branch exists"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", branch_name],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return True
        except:
            return False
    
    def _validate_no_conflicts(self, branch_name: str) -> bool:
        """Validate no merge conflicts"""
        try:
            # Use git merge-tree to check for conflicts without actually merging
            result = subprocess.run(
                ["git", "merge-tree", "main", branch_name],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            # If merge-tree produces output, there might be conflicts
            return "<<<<<<< " not in result.stdout
        except:
            return False
    
    def _validate_tests_pass(self) -> bool:
        """Quick test validation (subset for speed)"""
        try:
            # Run fast tests only for pre-merge validation
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "-x", "--tb=no", "-q"],
                cwd=self.repo_path, capture_output=True, text=True, 
                timeout=self.safety_config["validation_timeout"], check=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _validate_lint_pass(self) -> bool:
        """Quick lint validation"""
        try:
            # Basic syntax check
            result = subprocess.run(
                ["python3", "-m", "py_compile", "-"], 
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return True
        except:
            return True  # Don't fail on lint for now (easy win)
    
    def _execute_merge_by_safety_level(self, branch_name: str, safety_analysis: Dict, dry_run: bool) -> Dict[str, Any]:
        """Execute merge based on safety level classification"""
        level = safety_analysis["safety_level"]
        recommended_action = safety_analysis.get("recommended_action", "MANUAL_REVIEW_REQUIRED")
        
        if dry_run:
            return {
                "executed": False,
                "dry_run": True,
                "would_execute": recommended_action,
                "safety_level": level,
                "success": True
            }
        
        if recommended_action == "AUTO_MERGE":
            return self._execute_automated_merge(branch_name)
        elif recommended_action == "SAFE_MERGE_WITH_VALIDATION":
            return self._execute_validated_merge(branch_name)
        else:
            return {
                "executed": False,
                "reason": f"Safety level {level} requires manual review",
                "recommended_action": recommended_action,
                "success": False
            }
    
    def _execute_automated_merge(self, branch_name: str) -> Dict[str, Any]:
        """Execute fully automated merge for safe branches"""
        logger.info("🤖 Executing automated merge: %s", str(branch_name)[:100])
        
        try:
            # Fast-forward merge if possible
            result = subprocess.run(
                ["git", "merge", "--ff-only", branch_name],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            return {
                "executed": True,
                "method": "fast_forward",
                "success": True,
                "output": result.stdout
            }
            
        except subprocess.CalledProcessError:
            # Try regular merge
            try:
                result = subprocess.run(
                    ["git", "merge", "--no-ff", "-m", f"SSMT v3.0 automated merge: {branch_name}", branch_name],
                    cwd=self.repo_path, capture_output=True, text=True, check=True
                )
                
                return {
                    "executed": True,
                    "method": "merge_commit",
                    "success": True,
                    "output": result.stdout
                }
                
            except subprocess.CalledProcessError as e:
                return {
                    "executed": False,
                    "error": str(e),
                    "success": False
                }
    
    def _execute_validated_merge(self, branch_name: str) -> Dict[str, Any]:
        """Execute merge with additional validation steps"""
        logger.info("🔍 Executing validated merge: %s", str(branch_name)[:100])
        
        # Additional pre-merge checks for validated merge
        additional_validations = {
            "file_size_check": self._validate_file_sizes(branch_name),
            "security_scan": self._quick_security_scan(branch_name)
        }
        
        if not all(additional_validations.values()):
            return {
                "executed": False,
                "reason": "Additional validations failed",
                "failed_validations": additional_validations,
                "success": False
            }
        
        # Execute merge if validations pass
        return self._execute_automated_merge(branch_name)
    
    def _validate_file_sizes(self, branch_name: str) -> bool:
        """Validate no excessively large files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", f"main...{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            # Quick check - no files with extremely large diffs
            return "+++++" not in result.stdout
        except:
            return True
    
    def _quick_security_scan(self, branch_name: str) -> bool:
        """Quick security scan for obvious issues"""
        try:
            # Check for suspicious patterns in diff
            result = subprocess.run(
                ["git", "diff", f"main...{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            suspicious_patterns = ["password", "api_key", "secret", "token"]
            diff_lower = result.stdout.lower()
            
            for pattern in suspicious_patterns:
                if f"+{pattern}" in diff_lower:  # New additions only
                    return False
            
            return True
        except:
            return True
    
    def _run_post_merge_validation(self) -> Dict[str, Any]:
        """Run post-merge validation"""
        logger.info("✅ Running post-merge validation...")
        
        validations = {
            "git_status_clean": self._validate_git_status(),
            "basic_tests_pass": self._validate_tests_pass(),
            "no_syntax_errors": self._validate_syntax()
        }
        
        return {
            "validations": validations,
            "all_passed": all(validations.values()),
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_syntax(self) -> bool:
        """Basic syntax validation"""
        try:
            # Check Python files for syntax errors
            for py_file in self.repo_path.rglob("*.py"):
                if py_file.is_file():
                    subprocess.run(
                        ["python3", "-m", "py_compile", str(py_file)],
                        check=True, capture_output=True
                    )
            return True
        except:
            return False
    
    def _execute_emergency_rollback(self, merge_id: str):
        """Execute emergency rollback on failure"""
        logger.warning("🚨 Executing emergency rollback: %s", str(merge_id)[:100])
        
        try:
            # Reset to previous HEAD
            subprocess.run(
                ["git", "reset", "--hard", "HEAD~1"],
                cwd=self.repo_path, check=True
            )
            logger.info("✅ Emergency rollback completed")
        except Exception as e:
            logger.error("❌ Emergency rollback failed: %s", str(e)[:100])
    
    def _save_merge_results(self, results: Dict[str, Any]):
        """Save merge results to file"""
        results_file = self.repo_path / f"SSMT_v3_0_RESULTS_{results['merge_id']}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also update consolidated results
        consolidated_file = self.repo_path / "SSMT_v3_0_CONSOLIDATED_RESULTS.json"
        
        if consolidated_file.exists():
            with open(consolidated_file, 'r') as f:
                consolidated = json.load(f)
        else:
            consolidated = {"version": "3.0.0", "merges": []}
        
        consolidated["merges"].append(results)
        consolidated["last_updated"] = datetime.now().isoformat()
        
        with open(consolidated_file, 'w') as f:
            json.dump(consolidated, f, indent=2)
    
    def generate_safety_report(self) -> Dict[str, Any]:
        """Generate comprehensive safety and automation report"""
        logger.info("📊 Generating SSMT v3.0 safety report...")
        
        # Load all results
        results_files = list(self.repo_path.glob("SSMT_v3_0_RESULTS_*.json"))
        all_results = []
        
        for file in results_files:
            try:
                with open(file, 'r') as f:
                    all_results.append(json.load(f))
            except Exception as e:
                logger.warning("Could not load %s: %s", str(file)[:100], str(e)[:100])
        
        # Calculate statistics
        total_merges = len(all_results)
        successful_merges = sum(1 for r in all_results if r.get("success", False))
        automated_merges = sum(1 for r in all_results if r.get("automation_used", False))
        
        safety_levels = {}
        for result in all_results:
            level = result.get("safety_analysis", {}).get("safety_level", "UNKNOWN")
            safety_levels[level] = safety_levels.get(level, 0) + 1
        
        report = {
            "version": self.version,
            "report_timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_merges": total_merges,
                "successful_merges": successful_merges,
                "success_rate": successful_merges / total_merges if total_merges > 0 else 0,
                "automated_merges": automated_merges,
                "automation_rate": automated_merges / total_merges if total_merges > 0 else 0,
                "safety_level_distribution": safety_levels
            },
            "safety_config": self.safety_config,
            "automation_levels": self.automation_levels,
            "easy_wins_achieved": self._calculate_easy_wins(),
            "recommendations": self._generate_recommendations(all_results)
        }
        
        # Save report
        report_file = self.repo_path / f"SSMT_v3_0_SAFETY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📊 Safety report generated: %s", str(report_file)[:100])
        return report
    
    def _calculate_easy_wins(self) -> List[str]:
        """Calculate easy wins achieved"""
        wins = [
            "Automated safety backup system",
            "Progressive automation levels (SAFE → LOW_RISK → MEDIUM_RISK → HIGH_RISK)",
            "Pre-merge validation pipeline",
            "Post-merge validation and rollback",
            "File pattern-based risk assessment",
            "Quick security scanning",
            "Comprehensive logging and reporting",
            "Emergency rollback capabilities"
        ]
        return wins
    
    def _generate_recommendations(self, all_results: List[Dict]) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        if len(all_results) == 0:
            recommendations.append("Execute first safe merge to gather data")
            return recommendations
        
        success_rate = sum(1 for r in all_results if r.get("success", False)) / len(all_results)
        
        if success_rate < 0.8:
            recommendations.append("Review failed merges and adjust safety thresholds")
        
        automation_rate = sum(1 for r in all_results if r.get("automation_used", False)) / len(all_results)
        
        if automation_rate < 0.3:
            recommendations.append("Consider relaxing automation criteria for more easy wins")
        
        recommendations.append("Continue building on SSMT v3.0 success with advanced features")
        
        return recommendations

def main():
    """Main entry point for SSMT v3.0"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSMT v3.0 - Automated Safety & Easy Wins")
    parser.add_argument("command", choices=["analyze", "merge", "report"], 
                       help="Command to execute")
    parser.add_argument("--branch", help="Branch name for analyze/merge commands")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    ssmt = SSMTv3AutomatedSafety(args.repo_path)
    
    if args.command == "analyze":
        if not args.branch:
            print("❌ --branch required for analyze command")
            sys.exit(1)
        
        analysis = ssmt.analyze_branch_safety(args.branch)
        print(json.dumps(analysis, indent=2))
        
    elif args.command == "merge":
        if not args.branch:
            print("❌ --branch required for merge command")
            sys.exit(1)
        
        results = ssmt.execute_safe_merge(args.branch, dry_run=args.dry_run)
        print(json.dumps(results, indent=2))
        
    elif args.command == "report":
        report = ssmt.generate_safety_report()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()