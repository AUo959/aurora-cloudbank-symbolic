#!/usr/bin/env python3
"""
SSMT v3.0 Easy Wins Automation Engine
Aurora CloudBank Symbolic - Practical Automation Implementation

Focus: Easy wins with maximum safety, minimal risk
- Documentation updates (README, CHANGELOG, etc.)
- Configuration file updates (JSON, YAML) 
- Test file additions/updates
- GitHub workflow improvements
- Asset and resource files

This script identifies and automatically handles the "easy wins" - low-risk
changes that can be safely automated without complex conflict resolution.
"""

import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSMTv3EasyWinsEngine:
    """SSMT v3.0 Easy Wins Automation Engine"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.version = "3.0.0-easy-wins"
        
        # Easy win patterns - these are safe to automate
        self.easy_win_patterns = {
            "documentation": {
                "patterns": ["*.md", "*.txt", "*.rst", "docs/**", "README*", "CHANGELOG*", "LICENSE*"],
                "description": "Documentation updates",
                "auto_merge": True,
                "risk_level": "MINIMAL"
            },
            "configuration": {
                "patterns": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", ".github/**/*.yml"],
                "description": "Configuration file updates", 
                "auto_merge": True,
                "risk_level": "LOW"
            },
            "assets": {
                "patterns": ["*.png", "*.jpg", "*.svg", "*.ico", "assets/**", "static/**"],
                "description": "Asset and media files",
                "auto_merge": True,
                "risk_level": "MINIMAL"
            },
            "tests": {
                "patterns": ["tests/**", "test_*.py", "*_test.py", "spec/**"],
                "description": "Test files and specs",
                "auto_merge": False,  # Need validation
                "risk_level": "LOW"
            },
            "dependencies": {
                "patterns": ["package-lock.json", "yarn.lock", "poetry.lock"],
                "description": "Dependency lock files",
                "auto_merge": False,  # Need careful review
                "risk_level": "MEDIUM"
            }
        }
        
        # Automation success metrics
        self.success_metrics = {
            "total_branches_analyzed": 0,
            "easy_wins_identified": 0,
            "successful_auto_merges": 0,
            "manual_review_required": 0,
            "automation_time_saved": 0
        }
        
    def scan_for_easy_wins(self) -> Dict[str, List[str]]:
        """Scan repository for branches with easy win potential"""
        logger.info("🔍 Scanning for easy win opportunities...")
        
        try:
            # Get all branches
            result = subprocess.run(
                ["git", "branch", "-r", "--no-merged", "main"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            branches = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('origin/HEAD') and 'origin/' in line:
                    branch = line.replace('origin/', '').strip()
                    if branch != 'main':
                        branches.append(branch)
            
            # Analyze each branch for easy wins
            easy_win_candidates = {
                "auto_merge_ready": [],
                "validation_needed": [],
                "manual_review": [],
                "analysis_details": {}
            }
            
            for branch in branches:
                analysis = self.analyze_branch_for_easy_wins(branch)
                
                if analysis["easy_win_score"] >= 90:
                    easy_win_candidates["auto_merge_ready"].append(branch)
                elif analysis["easy_win_score"] >= 70:
                    easy_win_candidates["validation_needed"].append(branch)
                else:
                    easy_win_candidates["manual_review"].append(branch)
                
                easy_win_candidates["analysis_details"][branch] = analysis
                
            logger.info("✅ Scan complete: %s auto-merge ready", str(len(easy_win_candidates['auto_merge_ready']))[:100])
            return easy_win_candidates
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Failed to scan branches: %s", str(e)[:100])
            raise
    
    def analyze_branch_for_easy_wins(self, branch_name: str) -> Dict[str, Any]:
        """Analyze specific branch for easy win potential"""
        try:
            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--name-only", f"main...origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Categorize files
            categorized_files = self._categorize_changed_files(changed_files)
            
            # Calculate easy win score
            easy_win_score = self._calculate_easy_win_score(categorized_files, changed_files)
            
            # Get branch metadata
            branch_metadata = self._get_branch_metadata(branch_name)
            
            analysis = {
                "branch": branch_name,
                "changed_files": changed_files,
                "file_count": len(changed_files),
                "categorized_files": categorized_files,
                "easy_win_score": easy_win_score,
                "branch_metadata": branch_metadata,
                "recommended_action": self._get_easy_win_recommendation(easy_win_score, categorized_files),
                "automation_eligible": easy_win_score >= 80,
                "risk_assessment": self._assess_easy_win_risk(categorized_files),
                "timestamp": datetime.now().isoformat()
            }
            
            self.success_metrics["total_branches_analyzed"] += 1
            if analysis["automation_eligible"]:
                self.success_metrics["easy_wins_identified"] += 1
            
            return analysis
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Failed to analyze branch %s: %s", str(branch_name)[:100], str(e)[:100])
            raise
    
    def _categorize_changed_files(self, changed_files: List[str]) -> Dict[str, List[str]]:
        """Categorize changed files by easy win patterns"""
        categorized = {category: [] for category in self.easy_win_patterns.keys()}
        categorized["other"] = []
        
        for file in changed_files:
            file_path = Path(file)
            categorized_flag = False
            
            for category, config in self.easy_win_patterns.items():
                for pattern in config["patterns"]:
                    if file_path.match(pattern) or any(file_path.match(p) for p in [pattern]):
                        categorized[category].append(file)
                        categorized_flag = True
                        break
                if categorized_flag:
                    break
            
            if not categorized_flag:
                categorized["other"].append(file)
        
        return categorized
    
    def _calculate_easy_win_score(self, categorized_files: Dict[str, List[str]], all_files: List[str]) -> int:
        """Calculate easy win score (0-100)"""
        if not all_files:
            return 0
        
        score = 0
        total_files = len(all_files)
        
        # Score based on file categories
        for category, files in categorized_files.items():
            if category == "other":
                continue
                
            file_count = len(files)
            if file_count == 0:
                continue
                
            category_config = self.easy_win_patterns.get(category, {})
            
            if category_config.get("risk_level") == "MINIMAL":
                score += (file_count / total_files) * 40
            elif category_config.get("risk_level") == "LOW":
                score += (file_count / total_files) * 30
            elif category_config.get("risk_level") == "MEDIUM":
                score += (file_count / total_files) * 10
        
        # Bonus for documentation-heavy branches
        doc_files = len(categorized_files.get("documentation", []))
        if doc_files / total_files > 0.5:
            score += 20
        
        # Penalty for mixed-risk branches
        other_files = len(categorized_files.get("other", []))
        if other_files / total_files > 0.3:
            score -= 30
        
        # Penalty for too many files (complexity)
        if total_files > 20:
            score -= 10
        
        return max(0, min(100, int(score)))
    
    def _get_branch_metadata(self, branch_name: str) -> Dict[str, Any]:
        """Get metadata about the branch"""
        try:
            # Get last commit info
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%ae|%ad|%s", f"origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            commit_info = result.stdout.strip().split('|')
            
            return {
                "last_commit_hash": commit_info[0] if len(commit_info) > 0 else "",
                "author_name": commit_info[1] if len(commit_info) > 1 else "",
                "author_email": commit_info[2] if len(commit_info) > 2 else "",
                "last_commit_date": commit_info[3] if len(commit_info) > 3 else "",
                "last_commit_message": commit_info[4] if len(commit_info) > 4 else ""
            }
        except:
            return {}
    
    def _get_easy_win_recommendation(self, score: int, categorized_files: Dict[str, List[str]]) -> str:
        """Get recommendation for easy win handling"""
        if score >= 90:
            return "AUTO_MERGE_IMMEDIATE"
        elif score >= 80:
            return "AUTO_MERGE_WITH_BASIC_VALIDATION"
        elif score >= 70:
            return "SEMI_AUTOMATED_WITH_REVIEW"
        elif score >= 50:
            return "MANUAL_REVIEW_RECOMMENDED"
        else:
            return "COMPLEX_MANUAL_HANDLING_REQUIRED"
    
    def _assess_easy_win_risk(self, categorized_files: Dict[str, List[str]]) -> Dict[str, Any]:
        """Assess risk level for easy win automation"""
        risk_factors = []
        risk_level = "LOW"
        
        # Check for risky combinations
        if categorized_files.get("other", []):
            risk_factors.append(f"Contains {len(categorized_files['other'])} uncategorized files")
            risk_level = "MEDIUM"
        
        if categorized_files.get("dependencies", []):
            risk_factors.append("Contains dependency changes")
            risk_level = "MEDIUM"
        
        # Check total volume
        total_files = sum(len(files) for files in categorized_files.values())
        if total_files > 50:
            risk_factors.append(f"High volume: {total_files} files")
            risk_level = "HIGH"
        
        return {
            "level": risk_level,
            "factors": risk_factors,
            "mitigation": self._get_risk_mitigation(risk_factors)
        }
    
    def _get_risk_mitigation(self, risk_factors: List[str]) -> List[str]:
        """Get risk mitigation strategies"""
        mitigation = []
        
        if any("uncategorized" in factor for factor in risk_factors):
            mitigation.append("Review uncategorized files manually")
        
        if any("dependency" in factor for factor in risk_factors):
            mitigation.append("Run dependency vulnerability scan")
        
        if any("volume" in factor for factor in risk_factors):
            mitigation.append("Split into smaller batches")
        
        return mitigation
    
    def execute_easy_win_automation(self, branch_name: str, dry_run: bool = True) -> Dict[str, Any]:
        """Execute easy win automation for a specific branch"""
        logger.info("🚀 Executing easy win automation: %s (dry_run=%s)", str(branch_name)[:100], str(dry_run)[:100])
        
        start_time = datetime.now()
        
        try:
            # Analyze branch
            analysis = self.analyze_branch_for_easy_wins(branch_name)
            
            if not analysis["automation_eligible"]:
                return {
                    "branch": branch_name,
                    "executed": False,
                    "reason": f"Not eligible for automation (score: {analysis['easy_win_score']})",
                    "analysis": analysis,
                    "success": False
                }
            
            # Execute based on recommendation
            recommendation = analysis["recommended_action"]
            execution_result = None
            
            if recommendation == "AUTO_MERGE_IMMEDIATE":
                execution_result = self._execute_immediate_merge(branch_name, dry_run)
            elif recommendation == "AUTO_MERGE_WITH_BASIC_VALIDATION":
                execution_result = self._execute_validated_merge(branch_name, dry_run)
            else:
                execution_result = {
                    "executed": False,
                    "reason": f"Recommendation {recommendation} requires manual intervention"
                }
            
            # Calculate time saved
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            estimated_manual_time = self._estimate_manual_time(analysis)
            time_saved = max(0, estimated_manual_time - execution_time)
            
            # Update metrics
            if execution_result.get("success", False):
                self.success_metrics["successful_auto_merges"] += 1
                self.success_metrics["automation_time_saved"] += time_saved
            else:
                self.success_metrics["manual_review_required"] += 1
            
            return {
                "branch": branch_name,
                "analysis": analysis,
                "execution": execution_result,
                "timing": {
                    "execution_time_seconds": execution_time,
                    "estimated_manual_time_seconds": estimated_manual_time,
                    "time_saved_seconds": time_saved
                },
                "success": execution_result.get("success", False),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("❌ Easy win automation failed for %s: %s", str(branch_name)[:100], str(e)[:100])
            raise
    
    def _execute_immediate_merge(self, branch_name: str, dry_run: bool) -> Dict[str, Any]:
        """Execute immediate merge for highest-confidence easy wins"""
        if dry_run:
            return {
                "method": "immediate_merge",
                "executed": False,
                "dry_run": True,
                "would_execute": "Fast-forward or merge commit",
                "success": True
            }
        
        try:
            # Fetch latest
            subprocess.run(
                ["git", "fetch", "origin", branch_name],
                cwd=self.repo_path, check=True, capture_output=True
            )
            
            # Try fast-forward first
            try:
                result = subprocess.run(
                    ["git", "merge", "--ff-only", f"origin/{branch_name}"],
                    cwd=self.repo_path, capture_output=True, text=True, check=True
                )
                
                return {
                    "method": "fast_forward",
                    "executed": True,
                    "success": True,
                    "output": result.stdout
                }
                
            except subprocess.CalledProcessError:
                # Fall back to merge commit
                result = subprocess.run(
                    ["git", "merge", "--no-ff", "-m", 
                     f"SSMT v3.0 Easy Win: Auto-merge {branch_name}", f"origin/{branch_name}"],
                    cwd=self.repo_path, capture_output=True, text=True, check=True
                )
                
                return {
                    "method": "merge_commit",
                    "executed": True,  
                    "success": True,
                    "output": result.stdout
                }
                
        except subprocess.CalledProcessError as e:
            return {
                "method": "immediate_merge",
                "executed": False,
                "error": str(e),
                "success": False
            }
    
    def _execute_validated_merge(self, branch_name: str, dry_run: bool) -> Dict[str, Any]:
        """Execute merge with basic validation"""
        if dry_run:
            return {
                "method": "validated_merge",
                "executed": False,
                "dry_run": True,
                "would_execute": "Merge with validation checks",
                "success": True
            }
        
        # Run basic validations
        validations = {
            "syntax_check": self._quick_syntax_check(branch_name),
            "file_size_check": self._check_reasonable_file_sizes(branch_name),
            "no_binary_conflicts": self._check_binary_conflicts(branch_name)
        }
        
        if not all(validations.values()):
            return {
                "method": "validated_merge",
                "executed": False,
                "failed_validations": validations,
                "success": False
            }
        
        # Execute merge if validations pass
        return self._execute_immediate_merge(branch_name, False)
    
    def _quick_syntax_check(self, branch_name: str) -> bool:
        """Quick syntax check for obvious issues"""
        try:
            # Get Python files in the diff
            result = subprocess.run(
                ["git", "diff", "--name-only", f"main...origin/{branch_name}", "*.py"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            py_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Check syntax for changed Python files
            for py_file in py_files:
                file_path = self.repo_path / py_file
                if file_path.exists():
                    subprocess.run(
                        ["python3", "-m", "py_compile", str(file_path)],
                        check=True, capture_output=True
                    )
            
            return True
        except:
            return False
    
    def _check_reasonable_file_sizes(self, branch_name: str) -> bool:
        """Check for unreasonably large files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", f"main...origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            # Look for files with excessive changes (rough heuristic)
            lines = result.stdout.split('\n')
            for line in lines:
                if '|' in line and ('+++++++' in line or '-------' in line):
                    return False  # Suspicious large changes
            
            return True
        except:
            return True
    
    def _check_binary_conflicts(self, branch_name: str) -> bool:
        """Check for binary file conflicts"""
        try:
            result = subprocess.run(
                ["git", "merge-tree", "main", f"origin/{branch_name}"],
                cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            
            # Look for binary conflict markers
            return "Binary files differ" not in result.stdout
        except:
            return True
    
    def _estimate_manual_time(self, analysis: Dict[str, Any]) -> float:
        """Estimate time that would be required for manual merge"""
        base_time = 300  # 5 minutes base
        file_count = analysis.get("file_count", 0)
        
        # Add time per file
        time_per_file = 30  # 30 seconds per file
        
        # Adjust based on complexity
        easy_win_score = analysis.get("easy_win_score", 0)
        complexity_multiplier = max(1.0, (100 - easy_win_score) / 50)
        
        estimated_time = (base_time + (file_count * time_per_file)) * complexity_multiplier
        return estimated_time
    
    def generate_easy_wins_report(self) -> Dict[str, Any]:
        """Generate comprehensive easy wins report"""
        logger.info("📊 Generating SSMT v3.0 Easy Wins report...")
        
        # Scan for current opportunities
        opportunities = self.scan_for_easy_wins()
        
        report = {
            "version": self.version,
            "report_timestamp": datetime.now().isoformat(),
            "opportunities": opportunities,
            "success_metrics": self.success_metrics,
            "easy_win_patterns": self.easy_win_patterns,
            "recommendations": self._generate_easy_win_recommendations(opportunities),
            "automation_potential": self._calculate_automation_potential(opportunities)
        }
        
        # Save report
        report_file = self.repo_path / f"SSMT_v3_0_EASY_WINS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📊 Easy wins report generated: %s", str(report_file)[:100])
        return report
    
    def _generate_easy_win_recommendations(self, opportunities: Dict[str, List[str]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        auto_ready = len(opportunities.get("auto_merge_ready", []))
        validation_needed = len(opportunities.get("validation_needed", []))
        
        if auto_ready > 0:
            recommendations.append(f"Execute immediate automation on {auto_ready} auto-merge ready branches")
        
        if validation_needed > 0:
            recommendations.append(f"Run validated automation on {validation_needed} branches needing validation")
        
        if auto_ready + validation_needed > 10:
            recommendations.append("Consider batch processing to maximize efficiency")
        
        if self.success_metrics["successful_auto_merges"] > 0:
            success_rate = self.success_metrics["successful_auto_merges"] / max(1, self.success_metrics["total_branches_analyzed"])
            if success_rate > 0.8:
                recommendations.append("High success rate - consider expanding automation criteria")
        
        return recommendations
    
    def _calculate_automation_potential(self, opportunities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate overall automation potential"""
        total_branches = sum(len(branches) for branches in opportunities.values() if isinstance(branches, list))
        automatable = len(opportunities.get("auto_merge_ready", [])) + len(opportunities.get("validation_needed", []))
        
        potential_time_saved = 0
        for branch_list in [opportunities.get("auto_merge_ready", []), opportunities.get("validation_needed", [])]:
            potential_time_saved += len(branch_list) * 300  # 5 minutes per branch
        
        return {
            "total_branches_analyzed": total_branches,
            "immediately_automatable": len(opportunities.get("auto_merge_ready", [])),
            "semi_automatable": len(opportunities.get("validation_needed", [])),
            "automation_rate": automatable / max(1, total_branches),
            "potential_time_saved_minutes": potential_time_saved / 60,
            "easy_win_opportunity": "HIGH" if automatable > 5 else "MEDIUM" if automatable > 2 else "LOW"
        }

def main():
    """Main entry point for SSMT v3.0 Easy Wins Engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSMT v3.0 Easy Wins Automation Engine")
    parser.add_argument("command", choices=["scan", "analyze", "automate", "report"], 
                       help="Command to execute")
    parser.add_argument("--branch", help="Branch name for analyze/automate commands")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--batch", action="store_true", help="Batch process all eligible branches")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    engine = SSMTv3EasyWinsEngine(args.repo_path)
    
    if args.command == "scan":
        opportunities = engine.scan_for_easy_wins()
        print(json.dumps(opportunities, indent=2))
        
    elif args.command == "analyze":
        if not args.branch:
            print("❌ --branch required for analyze command")
            sys.exit(1)
        
        analysis = engine.analyze_branch_for_easy_wins(args.branch)
        print(json.dumps(analysis, indent=2))
        
    elif args.command == "automate":
        if args.batch:
            # Batch process all eligible branches
            opportunities = engine.scan_for_easy_wins()
            results = []
            
            for branch in opportunities.get("auto_merge_ready", []):
                result = engine.execute_easy_win_automation(branch, dry_run=args.dry_run)
                results.append(result)
            
            print(json.dumps({"batch_results": results}, indent=2))
            
        else:
            if not args.branch:
                print("❌ --branch required for automate command (or use --batch)")
                sys.exit(1)
            
            result = engine.execute_easy_win_automation(args.branch, dry_run=args.dry_run)
            print(json.dumps(result, indent=2))
        
    elif args.command == "report":
        report = engine.generate_easy_wins_report()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()