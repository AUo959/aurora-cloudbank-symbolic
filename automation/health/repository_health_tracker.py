#!/usr/bin/env python3
"""
Repository Health Impact Tracker
Measures and tracks the impact of issue closures on overall repository health
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

class RepositoryHealthTracker:
    def __init__(self):
        self.repo_path = "/workspaces/aurora-cloudbank-symbolic"
        self.health_metrics = {}
        self.baseline_date = datetime.now() - timedelta(days=30)  # 30 days ago baseline
        
    def analyze_code_quality_metrics(self):
        """Analyze current code quality metrics"""
        print("🔍 Analyzing Code Quality Metrics...")
        
        metrics = {
            "python_files": 0,
            "python_syntax_errors": 0,
            "python_files_compiling": 0,
            "security_validation_score": 0,
            "repository_size_mb": 0,
            "large_files_count": 0
        }
        
        # Count Python files and check compilation
        python_files = list(Path(self.repo_path).rglob("*.py"))
        metrics["python_files"] = len(python_files)
        
        compiling_files = 0
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                # Test compilation
                result = subprocess.run([
                    "python3", "-m", "py_compile", str(py_file)
                ], capture_output=True, text=True, cwd=self.repo_path)
                
                if result.returncode == 0:
                    compiling_files += 1
                else:
                    syntax_errors += 1
                    
            except Exception:
                syntax_errors += 1
        
        metrics["python_files_compiling"] = compiling_files
        metrics["python_syntax_errors"] = syntax_errors
        
        # Check security validation score (if security_verification.py exists)
        security_file = Path(self.repo_path) / "security_verification.py"
        if security_file.exists():
            try:
                result = subprocess.run([
                    "python3", str(security_file)
                ], capture_output=True, text=True, cwd=self.repo_path)
                
                # Parse security score from output
                if "Security Score:" in result.stdout:
                    score_line = [line for line in result.stdout.split('\n') if "Security Score:" in line]
                    if score_line:
                        score_part = score_line[0].split("Security Score:")[1].strip()
                        if "/" in score_part:
                            score = score_part.split("/")[0].strip()
                            metrics["security_validation_score"] = int(score)
                        
            except Exception as e:
                print(f"   ⚠️  Could not run security validation: {e}")
        
        # Calculate repository size
        try:
            result = subprocess.run([
                "du", "-sm", "."
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                size_mb = int(result.stdout.strip().split()[0])
                metrics["repository_size_mb"] = size_mb
                
        except Exception:
            pass
        
        # Count large files (>1MB)
        large_files = 0
        try:
            result = subprocess.run([
                "find", ".", "-type", "f", "-size", "+1M"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                large_files = len([f for f in result.stdout.strip().split('\n') if f.strip()])
                metrics["large_files_count"] = large_files
                
        except Exception:
            pass
        
        return metrics
    
    def analyze_git_health_metrics(self):
        """Analyze git-related health metrics"""
        print("📊 Analyzing Git Health Metrics...")
        
        metrics = {
            "commit_count_last_30_days": 0,
            "active_branches": 0,
            "clean_working_directory": False,
            "latest_commit_date": None
        }
        
        try:
            # Count recent commits
            result = subprocess.run([
                "git", "log", "--since=30 days ago", "--oneline"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                commit_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]
                metrics["commit_count_last_30_days"] = len(commit_lines)
            
            # Count active branches
            result = subprocess.run([
                "git", "branch", "-a"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                branches = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                metrics["active_branches"] = len(branches)
            
            # Check working directory status
            result = subprocess.run([
                "git", "status", "--porcelain"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            metrics["clean_working_directory"] = (result.returncode == 0 and not result.stdout.strip())
            
            # Get latest commit date
            result = subprocess.run([
                "git", "log", "-1", "--format=%ci"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                metrics["latest_commit_date"] = result.stdout.strip()
                
        except Exception as e:
            print(f"   ⚠️  Git analysis error: {e}")
        
        return metrics
    
    def calculate_health_score(self, code_metrics, git_metrics):
        """Calculate overall repository health score (0-100)"""
        score = 0
        max_score = 100
        
        # Code Quality (40 points)
        if code_metrics["python_files"] > 0:
            compilation_rate = code_metrics["python_files_compiling"] / code_metrics["python_files"]
            score += compilation_rate * 20  # 20 points for compilation
            
            syntax_error_penalty = min(code_metrics["python_syntax_errors"] * 2, 10)
            score -= syntax_error_penalty  # Up to -10 points for syntax errors
        else:
            score += 20  # No Python files = no syntax issues
        
        # Security (20 points)
        if code_metrics["security_validation_score"] >= 6:
            score += 20  # Perfect security score
        elif code_metrics["security_validation_score"] >= 4:
            score += 15  # Good security score
        elif code_metrics["security_validation_score"] >= 2:
            score += 10  # Acceptable security score
        else:
            score += 5   # Basic security measures
        
        # Repository Optimization (20 points)
        if code_metrics["repository_size_mb"] < 50:
            score += 10  # Optimal size
        elif code_metrics["repository_size_mb"] < 100:
            score += 7   # Good size
        elif code_metrics["repository_size_mb"] < 200:
            score += 5   # Acceptable size
        else:
            score += 2   # Large repository
        
        if code_metrics["large_files_count"] == 0:
            score += 10  # No large files
        elif code_metrics["large_files_count"] <= 2:
            score += 7   # Few large files
        elif code_metrics["large_files_count"] <= 5:
            score += 5   # Some large files
        else:
            score += 2   # Many large files
        
        # Git Health (20 points)
        if git_metrics["clean_working_directory"]:
            score += 5   # Clean working directory
        
        if git_metrics["commit_count_last_30_days"] >= 10:
            score += 10  # Active development
        elif git_metrics["commit_count_last_30_days"] >= 5:
            score += 7   # Moderate activity
        elif git_metrics["commit_count_last_30_days"] >= 1:
            score += 5   # Some activity
        else:
            score += 2   # Low activity
        
        if git_metrics["active_branches"] <= 5:
            score += 5   # Well-managed branches
        elif git_metrics["active_branches"] <= 10:
            score += 3   # Moderate branch count
        else:
            score += 1   # Many branches
        
        return min(max(score, 0), max_score)
    
    def load_issue_closure_data(self):
        """Load issue closure summary data"""
        summary_file = Path(self.repo_path) / "issue_closure_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                return json.load(f)
        return None
    
    def generate_health_report(self):
        """Generate comprehensive repository health report"""
        print("🏥 Aurora CloudBank - Repository Health Assessment")
        print("=" * 55)
        print(f"📅 Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Repository: {self.repo_path}")
        print()
        
        # Analyze current metrics
        code_metrics = self.analyze_code_quality_metrics()
        git_metrics = self.analyze_git_health_metrics()
        
        # Load issue closure data
        issue_data = self.load_issue_closure_data()
        
        # Calculate health score
        health_score = self.calculate_health_score(code_metrics, git_metrics)
        
        # Display results
        print("📊 CODE QUALITY METRICS:")
        print("-" * 30)
        print(f"   Python Files: {code_metrics['python_files']}")
        print(f"   Files Compiling: {code_metrics['python_files_compiling']}/{code_metrics['python_files']}")
        print(f"   Syntax Errors: {code_metrics['python_syntax_errors']}")
        print(f"   Security Score: {code_metrics['security_validation_score']}/6")
        print()
        
        print("📈 REPOSITORY METRICS:")
        print("-" * 30)
        print(f"   Repository Size: {code_metrics['repository_size_mb']} MB")  
        print(f"   Large Files: {code_metrics['large_files_count']}")
        print()
        
        print("🔄 GIT HEALTH METRICS:")
        print("-" * 30)
        print(f"   Recent Commits (30d): {git_metrics['commit_count_last_30_days']}")
        print(f"   Active Branches: {git_metrics['active_branches']}")
        print(f"   Working Directory: {'Clean' if git_metrics['clean_working_directory'] else 'Modified'}")
        print(f"   Latest Commit: {git_metrics['latest_commit_date'] or 'Unknown'}")
        print()
        
        if issue_data:
            print("🎯 ISSUE CLOSURE IMPACT:")
            print("-" * 30)
            print(f"   Issues Closed: {issue_data['total_closed']}")
            print(f"   Closure Date: {issue_data['timestamp'][:10]}")
            print(f"   Categories Addressed:")
            for pattern, count in issue_data['issues_by_pattern'].items():
                pattern_name = pattern.replace("_", " ").title()
                print(f"     • {pattern_name}: {count} issues")
            print()
        
        # Health score and grade
        print("🏆 OVERALL HEALTH ASSESSMENT:")
        print("-" * 30)
        print(f"   Health Score: {health_score:.1f}/100")
        
        if health_score >= 90:
            grade = "A+ (Excellent)"
            status = "🟢 Production Ready"
        elif health_score >= 80:
            grade = "A (Very Good)"
            status = "🟢 Production Ready"
        elif health_score >= 70:
            grade = "B (Good)"
            status = "🟡 Minor Issues"
        elif health_score >= 60:
            grade = "C (Fair)"
            status = "🟡 Needs Attention"
        elif health_score >= 50:
            grade = "D (Poor)"
            status = "🔴 Major Issues"
        else:
            grade = "F (Failing)"
            status = "🔴 Critical Issues"
        
        print(f"   Grade: {grade}")
        print(f"   Status: {status}")
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 30)
        
        recommendations = []
        
        if code_metrics["python_syntax_errors"] > 0:
            recommendations.append(f"Fix {code_metrics['python_syntax_errors']} remaining syntax errors")
        
        if code_metrics["security_validation_score"] < 6:
            recommendations.append(f"Improve security score (currently {code_metrics['security_validation_score']}/6)")
        
        if code_metrics["repository_size_mb"] > 100:
            recommendations.append("Consider repository size optimization")
        
        if code_metrics["large_files_count"] > 0:
            recommendations.append(f"Remove or optimize {code_metrics['large_files_count']} large files")
        
        if not git_metrics["clean_working_directory"]:
            recommendations.append("Commit or stash working directory changes")
        
        if git_metrics["commit_count_last_30_days"] < 5:
            recommendations.append("Consider more frequent commits for better tracking")
        
        if not recommendations:
            recommendations.append("Repository is in excellent health! 🎉")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Save report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "grade": grade,
            "status": status,
            "code_metrics": code_metrics,
            "git_metrics": git_metrics,
            "issue_closure_data": issue_data,
            "recommendations": recommendations
        }
        
        report_file = "repository_health_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📁 Full report saved to: {report_file}")
        print("🎊 Health assessment completed successfully!")
        
        return health_score

def main():
    tracker = RepositoryHealthTracker()
    health_score = tracker.generate_health_report()
    
    # Return health score for scripting
    exit(0 if health_score >= 80 else 1)

if __name__ == "__main__":
    main()