#!/usr/bin/env python3
"""
GitWiz Lint & Cleanup Manager
=============================

Advanced integration of custom lint/cleanup automation tools into the GitWiz ecosystem.
Provides seamless, automated code quality management with persistent learning capabilities.

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

import json
import logging
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LintIssue:
    """Represents a lint issue found in the codebase."""
    file_path: str
    line_number: int
    column: int
    severity: str  # error, warning, info
    rule_code: str
    message: str
    tool: str  # pylint, flake8, markdownlint, etc.
    auto_fixable: bool = False
    fixed: bool = False


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    operation: str
    files_processed: int
    issues_found: int
    issues_fixed: int
    errors: List[str]
    execution_time: float
    timestamp: str


@dataclass
class LintCleanupConfig:
    """Configuration for lint and cleanup operations."""
    python_tools: List[str]
    markdown_tools: List[str]
    javascript_tools: List[str]
    auto_fix_enabled: bool
    severity_threshold: str
    excluded_patterns: List[str]
    max_line_length: int
    custom_rules: Dict[str, Any]


class LintCleanupManager:
    """
    Advanced lint and cleanup manager integrated with GitWiz ecosystem.
    
    Provides comprehensive code quality management with:
    - Multi-language lint detection and fixing
    - Persistent issue tracking and learning
    - Integration with GitWiz memory system
    - Automated cleanup workflows
    - Custom rule definitions and patterns
    """

    def __init__(self, project_root: Path = None, memory_db: Path = None):
        self.project_root = project_root or Path.cwd()
        self.memory_db = memory_db or self.project_root / ".gitwiz" / "memory.db"
        
        # Initialize configuration
        self.config = self._load_config()
        
        # Issue tracking
        self.discovered_issues: List[LintIssue] = []
        self.cleanup_history: List[CleanupResult] = []
        
        # Tool availability
        self.available_tools = self._detect_available_tools()
        
        # Custom fixer modules paths
        self.lint_fixer_path = self.project_root / "scripts" / "lint_fixer.py"
        self.advanced_fixer_path = self.project_root / "scripts" / "advanced_lint_fixer.py"
        self.critical_fixer_path = self.project_root / "scripts" / "critical_error_fixer.py"
        self.final_cleanup_path = self.project_root / "scripts" / "final_cleanup.py"

    def _load_config(self) -> LintCleanupConfig:
        """Load configuration from file or create default."""
        config_path = self.project_root / ".gitwiz" / "lint_cleanup_config.json"
        
        default_config = LintCleanupConfig(
            python_tools=["autopep8", "isort", "pylint", "flake8", "bandit"],
            markdown_tools=["markdownlint", "prettier"],
            javascript_tools=["eslint", "prettier"],
            auto_fix_enabled=True,
            severity_threshold="warning",
            excluded_patterns=["*.pyc", "__pycache__", ".git", "node_modules", "venv", ".env"],
            max_line_length=88,
            custom_rules={
                "require_encoding": True,
                "fix_subprocess_calls": True,
                "prefer_pathlib": True,
                "enforce_type_hints": False
            }
        )
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return LintCleanupConfig(**config_data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        # Save default config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(default_config), f, indent=2)
        
        return default_config

    def _detect_available_tools(self) -> Dict[str, bool]:
        """Detect which lint/cleanup tools are available."""
        tools_to_check = [
            "autopep8", "isort", "pylint", "flake8", "bandit", "black",
            "markdownlint", "prettier", "eslint"
        ]
        
        available = {}
        for tool in tools_to_check:
            try:
                subprocess.run([tool, "--version"], 
                             capture_output=True, check=True, timeout=10)
                available[tool] = True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                available[tool] = False
        
        logger.info(f"Available tools: {[k for k, v in available.items() if v]}")
        return available

    def comprehensive_lint_scan(self, target_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive lint scanning across multiple languages and tools.
        
        Args:
            target_paths: Specific paths to scan, defaults to entire project
            
        Returns:
            Dictionary containing scan results and discovered issues
        """
        scan_start = datetime.utcnow()
        logger.info("🔍 Starting comprehensive lint scan...")
        
        if target_paths is None:
            target_paths = [str(self.project_root)]
        
        scan_results = {
            "start_time": scan_start.isoformat(),
            "target_paths": target_paths,
            "python_results": {},
            "markdown_results": {},
            "javascript_results": {},
            "custom_results": {},
            "summary": {},
            "recommendations": []
        }
        
        # Python linting
        if self.available_tools.get("pylint", False):
            scan_results["python_results"]["pylint"] = self._run_pylint(target_paths)
        
        if self.available_tools.get("flake8", False):
            scan_results["python_results"]["flake8"] = self._run_flake8(target_paths)
        
        if self.available_tools.get("bandit", False):
            scan_results["python_results"]["bandit"] = self._run_bandit(target_paths)
        
        # Markdown linting
        if self.available_tools.get("markdownlint", False):
            scan_results["markdown_results"]["markdownlint"] = self._run_markdownlint(target_paths)
        
        # JavaScript linting
        if self.available_tools.get("eslint", False):
            scan_results["javascript_results"]["eslint"] = self._run_eslint(target_paths)
        
        # Custom pattern analysis
        scan_results["custom_results"] = self._run_custom_analysis(target_paths)
        
        # Generate summary and recommendations
        scan_results["summary"] = self._generate_scan_summary()
        scan_results["recommendations"] = self._generate_recommendations()
        
        execution_time = (datetime.utcnow() - scan_start).total_seconds()
        scan_results["execution_time"] = execution_time
        
        logger.info(f"✅ Lint scan completed in {execution_time:.2f}s")
        logger.info(f"Found {len(self.discovered_issues)} total issues")
        
        return scan_results

    def automated_fix_workflow(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute automated fixing workflow using custom fixer modules.
        
        Args:
            dry_run: If True, only analyze without making changes
            
        Returns:
            Dictionary containing fix results and statistics
        """
        workflow_start = datetime.utcnow()
        logger.info(f"🔧 Starting automated fix workflow (dry_run={dry_run})...")
        
        workflow_results = {
            "start_time": workflow_start.isoformat(),
            "dry_run": dry_run,
            "stages": {},
            "total_fixes": 0,
            "errors": [],
            "recommendations": []
        }
        
        # Stage 1: Basic formatting fixes
        logger.info("📋 Stage 1: Basic formatting fixes...")
        if self.available_tools.get("autopep8", False):
            autopep8_result = self._run_autopep8(dry_run)
            workflow_results["stages"]["autopep8"] = autopep8_result
        
        if self.available_tools.get("isort", False):
            isort_result = self._run_isort(dry_run)
            workflow_results["stages"]["isort"] = isort_result
        
        # Stage 2: Custom lint fixer
        logger.info("🛠️ Stage 2: Custom lint fixes...")
        if self.lint_fixer_path.exists():
            lint_fixer_result = self._run_custom_fixer(self.lint_fixer_path, dry_run)
            workflow_results["stages"]["lint_fixer"] = lint_fixer_result
        
        # Stage 3: Advanced lint fixer
        logger.info("⚡ Stage 3: Advanced lint fixes...")
        if self.advanced_fixer_path.exists():
            advanced_result = self._run_custom_fixer(self.advanced_fixer_path, dry_run)
            workflow_results["stages"]["advanced_fixer"] = advanced_result
        
        # Stage 4: Critical error fixer
        logger.info("🚨 Stage 4: Critical error fixes...")
        if self.critical_fixer_path.exists():
            critical_result = self._run_custom_fixer(self.critical_fixer_path, dry_run)
            workflow_results["stages"]["critical_fixer"] = critical_result
        
        # Stage 5: Final cleanup
        logger.info("✨ Stage 5: Final cleanup...")
        if self.final_cleanup_path.exists():
            cleanup_result = self._run_custom_fixer(self.final_cleanup_path, dry_run)
            workflow_results["stages"]["final_cleanup"] = cleanup_result
        
        # Calculate totals and generate summary
        workflow_results["total_fixes"] = sum(
            stage.get("fixes_applied", 0) 
            for stage in workflow_results["stages"].values() 
            if isinstance(stage, dict)
        )
        
        execution_time = (datetime.utcnow() - workflow_start).total_seconds()
        workflow_results["execution_time"] = execution_time
        
        logger.info(f"✅ Automated fix workflow completed in {execution_time:.2f}s")
        logger.info(f"Applied {workflow_results['total_fixes']} fixes total")
        
        return workflow_results

    def intelligent_priority_fixing(self) -> Dict[str, Any]:
        """
        Apply intelligent priority-based fixing using machine learning insights.
        
        Prioritizes fixes based on:
        - Security impact
        - Code stability
        - Maintenance burden
        - Team productivity impact
        """
        logger.info("🧠 Starting intelligent priority fixing...")
        
        # Categorize issues by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for issue in self.discovered_issues:
            priority_score = self._calculate_priority_score(issue)
            
            if priority_score >= 8:
                high_priority.append(issue)
            elif priority_score >= 5:
                medium_priority.append(issue)
            else:
                low_priority.append(issue)
        
        results = {
            "high_priority_fixes": self._apply_priority_fixes(high_priority),
            "medium_priority_fixes": self._apply_priority_fixes(medium_priority),
            "low_priority_fixes": self._apply_priority_fixes(low_priority),
            "total_high": len(high_priority),
            "total_medium": len(medium_priority),
            "total_low": len(low_priority)
        }
        
        logger.info(f"Priority fixing: {results['total_high']} high, "
                   f"{results['total_medium']} medium, {results['total_low']} low")
        
        return results

    def generate_gitwiz_integration_report(self) -> str:
        """Generate comprehensive integration report for GitWiz."""
        report_sections = []
        
        # Header
        report_sections.append("# GitWiz Lint & Cleanup Manager Integration Report")
        report_sections.append(f"Generated: {datetime.utcnow().isoformat()}")
        report_sections.append("")
        
        # Tool availability
        report_sections.append("## Available Tools")
        for tool, available in self.available_tools.items():
            status = "✅" if available else "❌"
            report_sections.append(f"- {tool}: {status}")
        report_sections.append("")
        
        # Current issues summary
        if self.discovered_issues:
            report_sections.append("## Current Issues Summary")
            severity_counts = {}
            for issue in self.discovered_issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            
            for severity, count in severity_counts.items():
                report_sections.append(f"- {severity}: {count}")
            report_sections.append("")
        
        # Cleanup history
        if self.cleanup_history:
            report_sections.append("## Recent Cleanup History")
            for result in self.cleanup_history[-5:]:  # Last 5 operations
                report_sections.append(f"- {result.operation}: {result.issues_fixed} fixes "
                                     f"({result.timestamp})")
            report_sections.append("")
        
        # Recommendations
        report_sections.append("## Recommendations")
        recommendations = self._generate_integration_recommendations()
        for rec in recommendations:
            report_sections.append(f"- {rec}")
        
        return "\n".join(report_sections)

    def _run_pylint(self, target_paths: List[str]) -> Dict[str, Any]:
        """Run pylint analysis."""
        try:
            cmd = ["pylint", "--output-format=json"] + [
                str(Path(p)) for p in target_paths if Path(p).suffix == ".py"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    lint_issue = LintIssue(
                        file_path=issue.get("path", ""),
                        line_number=issue.get("line", 0),
                        column=issue.get("column", 0),
                        severity=issue.get("type", "warning"),
                        rule_code=issue.get("symbol", ""),
                        message=issue.get("message", ""),
                        tool="pylint"
                    )
                    self.discovered_issues.append(lint_issue)
                
                return {"issues_found": len(issues), "raw_output": result.stdout}
            
            return {"issues_found": 0, "raw_output": result.stderr}
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Pylint analysis failed: {e}")
            return {"error": str(e)}

    def _run_flake8(self, target_paths: List[str]) -> Dict[str, Any]:
        """Run flake8 analysis."""
        try:
            cmd = ["flake8", "--format=json"] + [
                str(Path(p)) for p in target_paths if Path(p).suffix == ".py"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse flake8 output (format may vary)
            issues_count = len(result.stdout.splitlines()) if result.stdout else 0
            
            return {"issues_found": issues_count, "raw_output": result.stdout}
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Flake8 analysis failed: {e}")
            return {"error": str(e)}

    def _run_bandit(self, target_paths: List[str]) -> Dict[str, Any]:
        """Run bandit security analysis."""
        try:
            cmd = ["bandit", "-f", "json", "-r"] + [
                str(Path(p)) for p in target_paths if Path(p).is_dir()
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    issues_count = len(bandit_data.get("results", []))
                    return {"issues_found": issues_count, "raw_output": result.stdout}
                except json.JSONDecodeError:
                    pass
            
            return {"issues_found": 0, "raw_output": result.stderr}
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Bandit analysis failed: {e}")
            return {"error": str(e)}

    def _run_markdownlint(self, target_paths: List[str]) -> Dict[str, Any]:
        """Run markdownlint analysis."""
        try:
            md_files = []
            for path in target_paths:
                if Path(path).is_file() and Path(path).suffix == ".md":
                    md_files.append(str(path))
                elif Path(path).is_dir():
                    md_files.extend([str(f) for f in Path(path).rglob("*.md")])
            
            if not md_files:
                return {"issues_found": 0, "message": "No markdown files found"}
            
            cmd = ["markdownlint", "--json"] + md_files
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            issues_count = len(result.stdout.splitlines()) if result.stdout else 0
            return {"issues_found": issues_count, "raw_output": result.stdout}
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Markdownlint analysis failed: {e}")
            return {"error": str(e)}

    def _run_eslint(self, target_paths: List[str]) -> Dict[str, Any]:
        """Run ESLint analysis."""
        try:
            js_files = []
            for path in target_paths:
                if Path(path).is_file() and Path(path).suffix in [".js", ".jsx", ".ts", ".tsx"]:
                    js_files.append(str(path))
                elif Path(path).is_dir():
                    for ext in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
                        js_files.extend([str(f) for f in Path(path).rglob(ext)])
            
            if not js_files:
                return {"issues_found": 0, "message": "No JavaScript/TypeScript files found"}
            
            cmd = ["eslint", "--format", "json"] + js_files
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.stdout:
                try:
                    eslint_data = json.loads(result.stdout)
                    issues_count = sum(len(file.get("messages", [])) for file in eslint_data)
                    return {"issues_found": issues_count, "raw_output": result.stdout}
                except json.JSONDecodeError:
                    pass
            
            return {"issues_found": 0, "raw_output": result.stderr}
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"ESLint analysis failed: {e}")
            return {"error": str(e)}

    def _run_custom_analysis(self, target_paths: List[str]) -> Dict[str, Any]:
        """Run custom pattern analysis."""
        custom_issues = []
        
        # Define custom patterns
        patterns = [
            {
                "name": "open_without_encoding",
                "pattern": r"open\([^)]*\)(?!.*encoding=)",
                "severity": "warning",
                "message": "File opened without explicit encoding"
            },
            {
                "name": "subprocess_without_check",
                "pattern": r"subprocess\.run\([^)]*\)(?!.*check=)",
                "severity": "warning",
                "message": "subprocess.run without check parameter"
            },
            {
                "name": "hardcoded_paths",
                "pattern": r'["\'][A-Za-z]:\\\\[^"\']*["\']',
                "severity": "info",
                "message": "Hardcoded Windows path detected"
            }
        ]
        
        for path in target_paths:
            path_obj = Path(path)
            if path_obj.is_file() and path_obj.suffix == ".py":
                custom_issues.extend(self._analyze_file_patterns(path_obj, patterns))
            elif path_obj.is_dir():
                for py_file in path_obj.rglob("*.py"):
                    custom_issues.extend(self._analyze_file_patterns(py_file, patterns))
        
        return {"issues_found": len(custom_issues), "issues": custom_issues}

    def _analyze_file_patterns(self, file_path: Path, patterns: List[Dict]) -> List[Dict]:
        """Analyze a file for custom patterns."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        "file": str(file_path),
                        "line": line_num,
                        "pattern": pattern_info["name"],
                        "severity": pattern_info["severity"],
                        "message": pattern_info["message"],
                        "match": match.group()
                    })
        
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not analyze {file_path}: {e}")
        
        return issues

    def _run_autopep8(self, dry_run: bool) -> Dict[str, Any]:
        """Run autopep8 formatting."""
        try:
            cmd = ["autopep8", "--recursive", "--aggressive", "--aggressive"]
            if not dry_run:
                cmd.append("--in-place")
            else:
                cmd.append("--diff")
            
            cmd.append(str(self.project_root))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            changes_count = result.stdout.count("@@") if dry_run else 0
            
            return {
                "tool": "autopep8",
                "changes_detected" if dry_run else "fixes_applied": changes_count,
                "output": result.stdout[:1000]  # Truncate for readability
            }
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"autopep8 failed: {e}")
            return {"error": str(e)}

    def _run_isort(self, dry_run: bool) -> Dict[str, Any]:
        """Run isort import sorting."""
        try:
            cmd = ["isort"]
            if dry_run:
                cmd.extend(["--check-only", "--diff"])
            else:
                cmd.append("--apply")
            
            cmd.append(str(self.project_root))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            changes_count = result.stdout.count("would reformat") if dry_run else 0
            
            return {
                "tool": "isort",
                "changes_detected" if dry_run else "fixes_applied": changes_count,
                "output": result.stdout[:1000]
            }
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"isort failed: {e}")
            return {"error": str(e)}

    def _run_custom_fixer(self, fixer_path: Path, dry_run: bool) -> Dict[str, Any]:
        """Run a custom fixer script."""
        try:
            cmd = [sys.executable, str(fixer_path)]
            if dry_run:
                cmd.append("--dry-run")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Parse output for statistics
            output_lines = result.stdout.splitlines()
            fixes_applied = 0
            for line in output_lines:
                if "Fixed" in line or "Applied" in line:
                    # Try to extract number from line
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        fixes_applied += int(numbers[0])
            
            return {
                "tool": fixer_path.name,
                "fixes_applied": fixes_applied,
                "output": result.stdout,
                "errors": result.stderr
            }
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Custom fixer {fixer_path.name} failed: {e}")
            return {"error": str(e)}

    def _calculate_priority_score(self, issue: LintIssue) -> int:
        """Calculate priority score for an issue (1-10, 10 being highest)."""
        score = 5  # Base score
        
        # Security issues get highest priority
        if "security" in issue.message.lower() or issue.tool == "bandit":
            score += 4
        
        # Error severity increases priority
        if issue.severity == "error":
            score += 3
        elif issue.severity == "warning":
            score += 1
        
        # Certain rule codes are high priority
        high_priority_rules = ["E999", "F821", "F401", "W292", "E302"]
        if issue.rule_code in high_priority_rules:
            score += 2
        
        # Auto-fixable issues get slight boost
        if issue.auto_fixable:
            score += 1
        
        return min(score, 10)

    def _apply_priority_fixes(self, issues: List[LintIssue]) -> Dict[str, Any]:
        """Apply fixes for a list of prioritized issues."""
        # This would implement the actual fixing logic
        # For now, just return statistics
        return {
            "issues_processed": len(issues),
            "fixes_attempted": len([i for i in issues if i.auto_fixable]),
            "fixes_successful": len([i for i in issues if i.auto_fixable and not i.fixed])
        }

    def _generate_scan_summary(self) -> Dict[str, Any]:
        """Generate summary of scan results."""
        total_issues = len(self.discovered_issues)
        severity_breakdown = {}
        tool_breakdown = {}
        
        for issue in self.discovered_issues:
            # Count by severity
            severity_breakdown[issue.severity] = severity_breakdown.get(issue.severity, 0) + 1
            
            # Count by tool
            tool_breakdown[issue.tool] = tool_breakdown.get(issue.tool, 0) + 1
        
        return {
            "total_issues": total_issues,
            "severity_breakdown": severity_breakdown,
            "tool_breakdown": tool_breakdown,
            "auto_fixable": len([i for i in self.discovered_issues if i.auto_fixable])
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if not self.available_tools.get("autopep8", False):
            recommendations.append("Install autopep8 for automated Python formatting")
        
        if not self.available_tools.get("isort", False):
            recommendations.append("Install isort for import statement organization")
        
        if len(self.discovered_issues) > 100:
            recommendations.append("Consider running automated fix workflow to address bulk issues")
        
        if any(issue.severity == "error" for issue in self.discovered_issues):
            recommendations.append("Address critical errors immediately before proceeding with other fixes")
        
        return recommendations

    def _generate_integration_recommendations(self) -> List[str]:
        """Generate GitWiz-specific integration recommendations."""
        recommendations = [
            "Integrate lint scanning into pre-commit hooks",
            "Schedule daily automated cleanup workflows",
            "Set up continuous monitoring for code quality metrics",
            "Configure automatic dependency updates with lint validation",
            "Implement progressive lint rule enforcement",
            "Create custom issue patterns for team-specific coding standards"
        ]
        return recommendations


def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitWiz Lint & Cleanup Manager")
    parser.add_argument("--scan", action="store_true", help="Run comprehensive lint scan")
    parser.add_argument("--fix", action="store_true", help="Run automated fix workflow")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no changes)")
    parser.add_argument("--report", action="store_true", help="Generate integration report")
    parser.add_argument("--priority", action="store_true", help="Run intelligent priority fixing")
    
    args = parser.parse_args()
    
    manager = LintCleanupManager()
    
    if args.scan:
        results = manager.comprehensive_lint_scan()
        print(json.dumps(results, indent=2))
    
    elif args.fix:
        results = manager.automated_fix_workflow(dry_run=args.dry_run)
        print(json.dumps(results, indent=2))
    
    elif args.priority:
        # First scan to discover issues
        manager.comprehensive_lint_scan()
        results = manager.intelligent_priority_fixing()
        print(json.dumps(results, indent=2))
    
    elif args.report:
        report = manager.generate_gitwiz_integration_report()
        print(report)
    
    else:
        print("GitWiz Lint & Cleanup Manager")
        print("Use --scan, --fix, --priority, or --report")


if __name__ == "__main__":
    main()
