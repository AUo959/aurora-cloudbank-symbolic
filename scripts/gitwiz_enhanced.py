#!/usr/bin/env python3
"""
GITWiz Enhanced - Adaptive Repository Stewardship System
Integrated with Heuristic Decision Engine PlusPlus (HDE++)

A comprehensive repository management system that learns, adapts, and maintains
optimal repository structure, security, and organization through intelligent
automation and persistent problem-solving capabilities.

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import logging
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# import pkg_resources  # Optional dependency
# import toml  # Optional dependency
# import yaml  # Optional dependency

# Import HDE++ for decision making
try:
    import sys

    sys.path.append(str(Path(__file__).parent.parent))
    from hdeplusplus import HeuristicDecisionEnginePlusPlus
except ImportError:
    # Fallback if HDE++ not available
    HeuristicDecisionEnginePlusPlus = None

# Import repository organizer
try:
    from gitwiz_repo_organizer import RepositoryOrganizer
except ImportError:
    # Create a minimal fallback if organizer not available
    class RepositoryOrganizer:
        def __init__(self, root):
            pass

        def analyze_repository_structure(self):
            return {}

        def generate_reorganization_plan(self, analysis):
            return {}


# Import the new lint cleanup manager
try:
    from gitwiz_lint_cleanup_manager import LintCleanupManager
except ImportError:
    # Fallback if not available
    LintCleanupManager = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IssuePattern:
    """Represents a known issue pattern and its solution."""

    pattern_id: str
    description: str
    pattern_regex: str
    solution_commands: List[str]
    solution_files: Dict[str, str]  # filename -> content
    confidence_score: float
    usage_count: int = 0
    success_rate: float = 1.0
    last_used: Optional[str] = None


@dataclass
class RepoState:
    """Snapshot of repository state for analysis."""

    commit_hash: str
    file_count: int
    total_size: int
    branch_count: int
    issues_detected: List[str]
    optimization_score: float
    security_score: float
    timestamp: str


@dataclass
class DependencyInfo:
    """Information about a project dependency."""

    name: str
    current_version: str
    latest_version: str
    source: str  # requirements.txt, package.json, pyproject.toml, etc.
    is_outdated: bool
    security_advisory: Optional[str] = None
    breaking_changes: Optional[str] = None


@dataclass
class WorkflowStage:
    """Represents a stage in the optimized workflow."""

    name: str
    description: str
    commands: List[str]
    dependencies: List[str]
    success_criteria: List[str]
    rollback_commands: List[str]
    estimated_duration: int  # in seconds


class AdaptiveMemory:
    """Advanced memory system for GITWiz to learn and adapt."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for persistent memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS issue_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    description TEXT,
                    pattern_regex TEXT,
                    solution_commands TEXT,
                    solution_files TEXT,
                    confidence_score REAL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 1.0,
                    last_used TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS repo_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_hash TEXT,
                    file_count INTEGER,
                    total_size INTEGER,
                    branch_count INTEGER,
                    issues_detected TEXT,
                    optimization_score REAL,
                    security_score REAL,
                    timestamp TEXT
                );

                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT,
                    files_affected TEXT,
                    before_state TEXT,
                    after_state TEXT,
                    success BOOLEAN,
                    timestamp TEXT
                );

                CREATE TABLE IF NOT EXISTS security_findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    finding_type TEXT,
                    severity TEXT,
                    file_path TEXT,
                    description TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    timestamp TEXT
                );
            """
            )

    def store_issue_pattern(self, pattern: IssuePattern):
        """Store or update an issue pattern."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO issue_patterns
                (pattern_id, description, pattern_regex, solution_commands,
                 solution_files, confidence_score, usage_count, success_rate, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    pattern.pattern_id,
                    pattern.description,
                    pattern.pattern_regex,
                    json.dumps(pattern.solution_commands),
                    json.dumps(pattern.solution_files),
                    pattern.confidence_score,
                    pattern.usage_count,
                    pattern.success_rate,
                    pattern.last_used,
                ),
            )

    def get_matching_patterns(self, issue_text: str) -> List[IssuePattern]:
        """Find patterns that match the given issue text."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM issue_patterns").fetchall()

        matching = []
        for row in rows:
            pattern = IssuePattern(
                pattern_id=row[0],
                description=row[1],
                pattern_regex=row[2],
                solution_commands=json.loads(row[3]),
                solution_files=json.loads(row[4]),
                confidence_score=row[5],
                usage_count=row[6],
                success_rate=row[7],
                last_used=row[8],
            )

            if re.search(pattern.pattern_regex, issue_text, re.IGNORECASE):
                matching.append(pattern)

        # Sort by confidence score and success rate
        return sorted(
            matching, key=lambda p: p.confidence_score * p.success_rate, reverse=True
        )


class ZIPWizIntegration:
    """Integration with ZIPWiz for archive management."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gitwiz_zip_"))

    def analyze_zip_file(self, zip_path: Path) -> Dict[str, Any]:
        """Analyze ZIP file contents and structure."""
        analysis = {
            "file_count": 0,
            "total_size": 0,
            "file_types": {},
            "nested_archives": [],
            "potential_duplicates": [],
            "structure": {},
        }

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for info in zf.infolist():
                    analysis["file_count"] += 1
                    analysis["total_size"] += info.file_size

                    # Track file types
                    ext = Path(info.filename).suffix.lower()
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1

                    # Check for nested archives
                    if ext in [".zip", ".tar", ".gz", ".7z", ".rar"]:
                        analysis["nested_archives"].append(info.filename)

                    # Build structure tree
                    parts = Path(info.filename).parts
                    current = analysis["structure"]
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]

                    if parts:
                        current[parts[-1]] = {
                            "size": info.file_size,
                            "compressed_size": info.compress_size,
                            "date": info.date_time,
                        }

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error analyzing ZIP file {zip_path}: {e}")

        return analysis

    def extract_and_reorganize(self, zip_path: Path, target_dir: Path) -> bool:
        """Extract ZIP file with intelligent reorganization."""
        try:
            extract_dir = self.temp_dir / zip_path.stem
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # Analyze extracted structure
            self._reorganize_extracted_files(extract_dir, target_dir)
            return True

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error extracting {zip_path}: {e}")
            return False

    def _reorganize_extracted_files(self, source_dir: Path, target_dir: Path):
        """Intelligently reorganize extracted files."""
        # This would implement smart file organization based on content type,
        # naming patterns, and repository structure best practices
        pass


class EnhancedGITWiz:
    """Enhanced GITWiz with adaptive intelligence and comprehensive repository stewardship."""

    def __init__(self, root: Path | None = None):
        self.project_root = root or Path(__file__).resolve().parent.parent
        self.memory_db = self.project_root / ".gitwiz" / "memory.db"
        self.memory_db.parent.mkdir(exist_ok=True)

        # Initialize components
        self.memory = AdaptiveMemory(self.memory_db)
        self.zipwiz = ZIPWizIntegration(self.project_root)
        self.hde = (
            HeuristicDecisionEnginePlusPlus()
            if HeuristicDecisionEnginePlusPlus
            else None
        )

        # Initialize new enhanced components (lazy loading)
        self._dependency_manager = None
        self._workflow_optimizer = None
        self._lint_cleanup_manager = None

        # Load common issue patterns
        self._load_common_patterns()

        # State tracking
        self.current_state: Optional[RepoState] = None
        self.optimization_queue: List[str] = []

    @property
    def dependency_manager(self):
        """Lazy-loaded dependency manager."""
        if self._dependency_manager is None:
            self._dependency_manager = DependencyManager(self.project_root)
        return self._dependency_manager

    @property
    def workflow_optimizer(self):
        """Lazy-loaded workflow optimizer."""
        if self._workflow_optimizer is None:
            self._workflow_optimizer = WorkflowOptimizer(self.project_root)
        return self._workflow_optimizer

    @property
    def lint_cleanup_manager(self):
        """Lazy-loaded lint cleanup manager."""
        if self._lint_cleanup_manager is None and LintCleanupManager:
            self._lint_cleanup_manager = LintCleanupManager(
                project_root=self.project_root, memory_db=self.memory_db
            )
        return self._lint_cleanup_manager

    def _load_common_patterns(self):
        """Load pre-defined common issue patterns."""
        common_patterns = [
            IssuePattern(
                pattern_id="markdown_heading_spacing",
                description="MD022: Headings need blank lines around them",
                pattern_regex=r"MD022.*[Hh]eadings.*blank lines",
                solution_commands=[],
                solution_files={
                    "fix_script": """
                    # Fix MD022 heading spacing issues
                    find . -name "*.md" -exec sed -i '/^#{1,6} /{
                        i\\

                        a\\

                    }' {} \\;
                    """
                },
                confidence_score=0.95,
            ),
            IssuePattern(
                pattern_id="markdown_list_spacing",
                description="MD032: Lists need blank lines around them",
                pattern_regex=r"MD032.*[Ll]ists.*blank lines",
                solution_commands=[],
                solution_files={
                    "fix_script": """
                    # Fix MD032 list spacing issues
                    find . -name "*.md" -exec awk '
                    /^[[:space:]]*[-*+] / {
                        if (prev_line != "" && prev_non_list) print ""
                        print; in_list=1; next
                    }
                    /^[[:space:]]*[0-9]+\\. / {
                        if (prev_line != "" && prev_non_list) print ""
                        print; in_list=1; next
                    }
                    {
                        if (in_list && $0 != "" && !/^[[:space:]]*[-*+0-9]/) {
                            print ""; in_list=0
                        }
                        print; prev_line=$0; prev_non_list=!in_list
                    }' {} > {}.tmp && mv {}.tmp {} \\;
                    """
                },
                confidence_score=0.90,
            ),
            IssuePattern(
                pattern_id="pre_commit_hook_missing",
                description="Pre-commit hook not found or configured",
                pattern_regex=r"pre-commit.*not found|Did you forget to activate",
                solution_commands=[
                    "pip install pre-commit",
                    "pre-commit install",
                    "pre-commit run --all-files",
                ],
                solution_files={},
                confidence_score=0.85,
            ),
            IssuePattern(
                pattern_id="trailing_whitespace",
                description="MD009: Trailing whitespace in markdown files",
                pattern_regex=r"MD009.*trailing.*space",
                solution_commands=[
                    "find . -name '*.md' -exec sed -i 's/[[:space:]]*$//' {} \\;"
                ],
                solution_files={},
                confidence_score=0.98,
            ),
        ]

        for pattern in common_patterns:
            self.memory.store_issue_pattern(pattern)

    def analyze_repository_state(self) -> RepoState:
        """Comprehensive repository state analysis."""
        try:
            # Get current commit hash
            _ = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            commit_hash = result.stdout.strip() if result.returncode == 0 else "unknown"

            # Count files and calculate total size
            file_count = 0
            total_size = 0
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and not any(
                    part.startswith(".git") for part in file_path.parts
                ):
                    file_count += 1
                    total_size += file_path.stat().st_size

            # Count branches
            _ = subprocess.run(
                ["git", "branch", "-a"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            branch_count = (
                len(result.stdout.strip().split("\n")) if result.returncode == 0 else 0
            )

            # Detect issues
            issues = self._detect_issues()

            # Calculate scores
            optimization_score = self._calculate_optimization_score()
            security_score = self._calculate_security_score()

            state = RepoState(
                commit_hash=commit_hash,
                file_count=file_count,
                total_size=total_size,
                branch_count=branch_count,
                issues_detected=issues,
                optimization_score=optimization_score,
                security_score=security_score,
                timestamp=datetime.utcnow().isoformat(),
            )

            self.current_state = state
            return state

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error analyzing repository state: {e}")
            return RepoState(
                "error", 0, 0, 0, [str(e)], 0.0, 0.0, datetime.utcnow().isoformat()
            )

    def _detect_issues(self) -> List[str]:
        """Detect various repository issues."""
        issues = []

        # Check for large files
        large_files = []
        for file_path in self.project_root.rglob("*"):
            if (
                file_path.is_file() and file_path.stat().st_size > 10 * 1024 * 1024
            ):  # 10MB
                large_files.append(str(file_path.relative_to(self.project_root)))

        if large_files:
            issues.append(f"Large files detected: {', '.join(large_files[:5])}")

        # Check for duplicate files
        file_hashes = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".git") for part in file_path.parts
            ):
                try:
                    with open(file_path, "rb") as f:
                        _file_hash = hashlib.md5(f.read()).hexdigest()
                        if __file_hash in file_hashes:
                            issues.append(
                                f"Duplicate file: {file_path.name} (matches {file_hashes[_file_hash].name})"
                            )
                        else:
                            file_hashes[_file_hash] = file_path
                except (OSError, ValueError, RuntimeError):
                    continue

        # Check for security issues
        security_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
        ]

        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in security_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append(
                                f"Potential security issue in {file_path.name}"
                            )
                            break
            except (OSError, ValueError, RuntimeError):
                continue

        return issues

    def _calculate_optimization_score(self) -> float:
        """Calculate repository optimization score (0-1)."""
        score = 1.0

        # Penalize for too many branches
        if self.current_state and self.current_state.branch_count > 10:
            score -= 0.2

        # Penalize for large repository size
        if (
            self.current_state and self.current_state.total_size > 100 * 1024 * 1024
        ):  # 100MB
            score -= 0.3

        # Penalize for detected issues
        if self.current_state:
            score -= min(0.4, len(self.current_state.issues_detected) * 0.1)

        return max(0.0, score)

    def _calculate_security_score(self) -> float:
        """Calculate repository security score (0-1)."""
        score = 1.0

        # Check for .gitignore
        if not (self.project_root / ".gitignore").exists():
            score -= 0.2

        # Check for security files
        security_files = [
            ".pre-commit-config.yaml",
            "SECURITY.md",
            ".github/dependabot.yml",
        ]
        for sec_file in security_files:
            if (self.project_root / sec_file).exists():
                score += 0.1

        return min(1.0, max(0.0, score))

    def intelligent_fix(self, issue_description: str) -> bool:
        """Apply intelligent fix for detected issues."""
        patterns = self.memory.get_matching_patterns(issue_description)

        if not patterns:
            logger.warning(f"No known solution for issue: {issue_description}")
            return False

        best_pattern = patterns[0]
        logger.info(f"Applying solution: {best_pattern.description}")

        try:
            # Execute solution commands
            for cmd in best_pattern.solution_commands:
                import shlex
                cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else cmd
                result = subprocess.run(
                    cmd_parts,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode != 0:
                    logger.error(f"Command failed: {cmd}")
                    logger.error(result.stderr)
                    return False

            # Create solution files
            for filename, content in best_pattern.solution_files.items():
                file_path = self.project_root / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(content)

            # Update pattern usage
            best_pattern.usage_count += 1
            best_pattern.last_used = datetime.utcnow().isoformat()
            self.memory.store_issue_pattern(best_pattern)

            return True

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error applying fix: {e}")
            # Update success rate
            best_pattern.success_rate = (
                best_pattern.success_rate * best_pattern.usage_count
            ) / (best_pattern.usage_count + 1)
            self.memory.store_issue_pattern(best_pattern)
            return False

    def optimize_repository(self) -> Dict[str, Any]:
        """Comprehensive repository optimization."""
        logger.info("Starting comprehensive repository optimization...")

        # Analyze current state
        initial_state = self.analyze_repository_state()
        optimizations = []

        # 1. Clean up branches
        _ = subprocess.run(
            ["git", "branch", "--merged"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        if hasattr(locals(), "result") and result.returncode == 0:
            merged_branches = [
                b.strip()
                for b in result.stdout.split("\n")
                if b.strip() and not b.strip().startswith("*") and "main" not in b
            ]
            for branch in merged_branches:
                subprocess.run(
                    ["git", "branch", "-d", branch],
                    cwd=self.project_root,
                    shell=False,
                    check=False,
                )
                optimizations.append(f"Deleted merged branch: {branch}")

        # 2. Optimize ZIP files
        zip_files = list(self.project_root.rglob("*.zip"))
        for zip_file in zip_files:
            analysis = self.zipwiz.analyze_zip_file(zip_file)
            if analysis["file_count"] == 0:
                zip_file.unlink()
                optimizations.append(f"Removed empty ZIP: {zip_file.name}")

        # 3. Fix detected issues
        for issue in initial_state.issues_detected:
            if self.intelligent_fix(issue):
                optimizations.append(f"Fixed issue: {issue}")

        # 4. Analyze final state
        final_state = self.analyze_repository_state()

        return {
            "initial_state": asdict(initial_state),
            "final_state": asdict(final_state),
            "optimizations_applied": optimizations,
            "improvement_score": final_state.optimization_score
            - initial_state.optimization_score,
        }

    def persistent_lint_fix(self) -> bool:
        """Apply persistent fixes for all linting issues."""
        logger.info("Applying persistent linting fixes...")

        # Run linting tools and capture output
        lint_issues = []

        # Check markdown linting
        if shutil.which("markdownlint"):
            _ = subprocess.run(
                ["markdownlint", ".", "--json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            if hasattr(locals(), "result") and result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    lint_issues.extend(
                        [
                            f"MD{issue['ruleNames'][0]}: {issue['ruleDescription']}"
                            for issue in issues
                        ]
                    )
                except json.JSONDecodeError:
                    pass

        # Check Python linting
        if shutil.which("flake8"):
            _ = subprocess.run(
                ["flake8", ".", "--format=json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            if hasattr(locals(), "result") and result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    lint_issues.extend([f"Flake8: {issue['text']}" for issue in issues])
                except json.JSONDecodeError:
                    pass

        # Apply intelligent fixes
        fixed_count = 0
        for issue in lint_issues:
            if self.intelligent_fix(issue):
                fixed_count += 1

        logger.info(f"Fixed {fixed_count} out of {len(lint_issues)} linting issues")
        return fixed_count > 0

    def comprehensive_dependency_management(
        self, auto_update: bool = False, dry_run: bool = True
    ) -> Dict[str, Any]:
        """Comprehensive dependency scanning and management."""
        logger.info("Starting comprehensive dependency management...")

        # Initialize dependency manager if not already done
        # (using property for lazy loading)

        # Scan current dependencies
        dependencies = self.dependency_manager.scan_dependencies()

        analysis = {
            "total_dependencies": sum(len(deps) for deps in dependencies.values()),
            "by_ecosystem": {k: len(v) for k, v in dependencies.items()},
            "outdated": {},
            "security_issues": [],
            "update_report": None,
        }

        # Analyze outdated dependencies
        for ecosystem, deps in dependencies.items():
            outdated = [dep for dep in deps if dep.is_outdated]
            analysis["outdated"][ecosystem] = len(outdated)

            # Check for security issues
            security_deps = [dep for dep in deps if dep.security_advisory]
            analysis["security_issues"].extend(
                [
                    {
                        "name": dep.name,
                        "current_version": dep.current_version,
                        "advisory": dep.security_advisory,
                        "ecosystem": ecosystem,
                    }
                    for dep in security_deps
                ]
            )

        # Auto-update if requested
        if auto_update:
            analysis["update_report"] = (
                self.dependency_manager.auto_update_dependencies(dry_run=dry_run)
            )

        return analysis

    def execute_optimized_workflow(
        self, workflow_type: str = "full_optimization", dry_run: bool = True
    ) -> Dict[str, Any]:
        """Execute comprehensive optimized workflow."""
        logger.info(f"Executing optimized workflow: {workflow_type}")

        # Initialize workflow optimizer if not already done
        # (using property for lazy loading)

        # Execute workflow
        return self.workflow_optimizer.execute_workflow(workflow_type, dry_run=dry_run)

    def intelligent_repository_analysis(self) -> Dict[str, Any]:
        """Advanced repository analysis with AI-driven insights."""
        logger.info("Performing intelligent repository analysis...")

        analysis = {
            "repository_health": {},
            "optimization_opportunities": [],
            "security_assessment": {},
            "maintenance_recommendations": [],
            "estimated_benefits": {},
        }

        # Get current state
        current_state = self.analyze_repository_state()

        # Repository health assessment
        analysis["repository_health"] = {
            "optimization_score": current_state.optimization_score,
            "security_score": current_state.security_score,
            "file_count": current_state.file_count,
            "total_size_mb": round(current_state.total_size / (1024 * 1024), 2),
            "branch_count": current_state.branch_count,
            "issues_count": len(current_state.issues_detected),
        }

        # Identify optimization opportunities
        if current_state.optimization_score < 0.8:
            analysis["optimization_opportunities"].append(
                {
                    "type": "structure_optimization",
                    "description": "Repository structure can be optimized",
                    "priority": "high",
                    "estimated_impact": "20-30% performance improvement",
                }
            )

        if current_state.total_size > 50 * 1024 * 1024:  # 50MB
            analysis["optimization_opportunities"].append(
                {
                    "type": "size_reduction",
                    "description": "Repository size can be reduced",
                    "priority": "medium",
                    "estimated_impact": "Storage and clone time reduction",
                }
            )

        # Security assessment
        analysis["security_assessment"] = {
            "score": current_state.security_score,
            "critical_issues": len(
                [
                    issue
                    for issue in current_state.issues_detected
                    if "security" in issue.lower()
                ]
            ),
            "recommendations": self._generate_security_recommendations(current_state),
        }

        # Maintenance recommendations using HDE++ if available
        if self.hde:
            context = {
                "weights": {"logic": 3, "context_hold": 2},
                "require": ["general"],
                "analysis_type": "repository_maintenance",
            }
            hde_recommendation = self.hde.recommend_with_explanation(context)
            analysis["ai_recommendations"] = hde_recommendation

        return analysis

    def _generate_security_recommendations(self, state: RepoState) -> List[str]:
        """Generate security recommendations based on repository state."""
        recommendations = []

        if state.security_score < 0.7:
            recommendations.append("Implement comprehensive security scanning")
            recommendations.append("Add security-focused pre-commit hooks")

        if not (self.project_root / ".gitignore").exists():
            recommendations.append("Create comprehensive .gitignore file")

        if not (self.project_root / "SECURITY.md").exists():
            recommendations.append("Add security policy documentation")

        return recommendations

    def generate_optimization_report(self) -> str:
        """Generate comprehensive optimization report."""
        report = []
        report.append("=" * 60)
        report.append("🚀 GITWIZ ENHANCED - COMPREHENSIVE OPTIMIZATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("")

        # Repository analysis
        analysis = self.intelligent_repository_analysis()

        report.append("📊 REPOSITORY HEALTH ASSESSMENT")
        report.append("-" * 40)
        health = analysis["repository_health"]
        report.append(f"Optimization Score: {health['optimization_score']:.2f}/1.00")
        report.append(f"Security Score: {health['security_score']:.2f}/1.00")
        report.append(f"Total Files: {health['file_count']:,}")
        report.append(f"Repository Size: {health['total_size_mb']:.1f} MB")
        report.append(f"Branch Count: {health['branch_count']}")
        report.append(f"Issues Detected: {health['issues_count']}")
        report.append("")

        # Dependency analysis
        if hasattr(self, "dependency_manager"):
            dep_analysis = self.comprehensive_dependency_management()
            report.append("📦 DEPENDENCY ANALYSIS")
            report.append("-" * 40)
            report.append(f"Total Dependencies: {dep_analysis['total_dependencies']}")
            for ecosystem, count in dep_analysis["by_ecosystem"].items():
                outdated = dep_analysis["outdated"].get(ecosystem, 0)
                report.append(
                    f"{ecosystem.capitalize()}: {count} total, {outdated} outdated"
                )

            if dep_analysis["security_issues"]:
                report.append(
                    f"🔒 Security Issues: {len(dep_analysis['security_issues'])}"
                )
                for issue in dep_analysis["security_issues"][:3]:  # Show first 3
                    report.append(f"  - {issue['name']} ({issue['ecosystem']})")
            report.append("")

        # Optimization opportunities
        if analysis["optimization_opportunities"]:
            report.append("🎯 OPTIMIZATION OPPORTUNITIES")
            report.append("-" * 40)
            for opp in analysis["optimization_opportunities"]:
                report.append(f"• {opp['description']} (Priority: {opp['priority']})")
                report.append(f"  Impact: {opp['estimated_impact']}")
            report.append("")

        # AI Recommendations
        if "ai_recommendations" in analysis:
            report.append("🤖 AI-POWERED RECOMMENDATIONS")
            report.append("-" * 40)
            ai_rec = analysis["ai_recommendations"]
            report.append(f"Recommended Model: {ai_rec.get('model', 'N/A')}")
            report.append(f"Confidence: {ai_rec.get('confidence', 0):.2f}")
            report.append(f"Explanation: {ai_rec.get('explanation', 'N/A')}")
            report.append("")

        # Action items
        report.append("✅ RECOMMENDED ACTIONS")
        report.append("-" * 40)
        report.append(
            "1. Run: python scripts/gitwiz_enhanced.py dependencies --auto-update --dry-run"
        )
        report.append(
            "2. Run: python scripts/gitwiz_enhanced.py workflow --execute full_optimization --dry-run"
        )
        report.append("3. Run: python scripts/gitwiz_enhanced.py organize --analyze")
        report.append("4. Review security recommendations and implement fixes")
        report.append("5. Schedule regular optimization runs")
        report.append("")

        report.append("=" * 60)
        report.append("🎉 OPTIMIZATION ANALYSIS COMPLETE")
        report.append("=" * 60)

        return "\n".join(report)

    # Legacy compatibility methods
    def status(self) -> bool:
        return self._run(["git", "status"])

    def _run(self, cmd: list[str], check: bool = False) -> bool:
        """Run a command in the project root and echo output."""
        print(f"+ {' '.join(cmd)}")
        _ = subprocess.run(
            cmd,
            cwd=self.project_root,
            text=True,
            capture_output=True,
            shell=False,
            check=False,
        )
        if hasattr(locals(), "result") and result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")
        return result.returncode == 0


class RepositoryStructureAnalyzer:
    """Advanced repository structure analysis and optimization."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ideal_structure = {
            "docs/": ["*.md", "*.pd", "*guide*", "*readme*"],
            "docs/status/": ["*status*", "*complete*", "*report*"],
            "docs/deployment/": ["*deploy*", "*launch*", "*phase*"],
            "archives/": ["*.zip", "*.tar", "*.gz"],
            "archives/bundles/": ["*bundle*", "*export*", "*package*"],
            "archives/modules/": ["*module*", "*component*"],
            "archives/toolkits/": ["*toolkit*", "*tools*"],
            "temp/": ["*temp*", "*tmp*", "*backup*", "*old*"],
            "scripts/": ["*.sh", "*script*", "*deploy*"],
            "config/": ["*.yaml", "*.yml", "*.json", "*config*"],
        }

    def analyze_current_structure(self) -> Dict[str, Any]:
        """Analyze current repository structure against ideal."""
        analysis = {
            "total_files": 0,
            "misplaced_files": [],
            "duplicate_candidates": [],
            "large_files": [],
            "archive_consolidation": [],
            "structure_violations": [],
            "organization_score": 0.0,
        }

        file_groups = {}
        file_sizes = {}

        # Scan all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".git") for part in file_path.parts
            ):
                analysis["total_files"] += 1
                rel_path = file_path.relative_to(self.project_root)

                # Track file sizes
                size = file_path.stat().st_size
                file_sizes[str(rel_path)] = size

                # Large files (>10MB)
                if size > 10 * 1024 * 1024:
                    analysis["large_files"].append(
                        {
                            "path": str(rel_path),
                            "size_mb": round(size / (1024 * 1024), 2),
                        }
                    )

                # Group similar files
                name_base = re.sub(
                    r"[_\s]+\d+|[_\s]*2|[_\s]*copy|[_\s]*backup",
                    "",
                    file_path.stem.lower(),
                )
                if name_base not in file_groups:
                    file_groups[name_base] = []
                file_groups[name_base].append(str(rel_path))

        # Find duplicates
        for base_name, files in file_groups.items():
            if len(files) > 1:
                analysis["duplicate_candidates"].append(
                    {
                        "base_name": base_name,
                        "files": files,
                        "total_size": sum(file_sizes.get(f, 0) for f in files),
                    }
                )

        # Analyze structure violations
        for file_path in self.project_root.iterdir():
            if file_path.is_file():
                rel_path = file_path.relative_to(self.project_root)
                violations = self._check_structure_violations(rel_path)
                analysis["structure_violations"].extend(violations)

        # Calculate organization score
        analysis["organization_score"] = self._calculate_organization_score(analysis)

        return analysis

    def _check_structure_violations(self, file_path: Path) -> List[str]:
        """Check if file placement violates ideal structure."""
        violations = []
        filename = file_path.name.lower()

        # Check if file should be in a specific directory
        for target_dir, patterns in self.ideal_structure.items():
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern.lower()):
                    if not str(file_path).startswith(target_dir):
                        violations.append(f"{file_path} should be in {target_dir}")

        return violations

    def _calculate_organization_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate repository organization score (0-1)."""
        base_score = 1.0

        # Penalize structure violations
        violation_penalty = min(0.4, len(analysis["structure_violations"]) * 0.02)
        base_score -= violation_penalty

        # Penalize duplicates
        duplicate_penalty = min(0.3, len(analysis["duplicate_candidates"]) * 0.05)
        base_score -= duplicate_penalty

        # Penalize large files in root
        large_file_penalty = min(0.2, len(analysis["large_files"]) * 0.03)
        base_score -= large_file_penalty

        return max(0.0, base_score)


class IntelligentCleanupEngine:
    """Advanced cleanup engine with safety and rollback capabilities."""

    def __init__(self, project_root: Path, memory: AdaptiveMemory):
        self.project_root = project_root
        self.memory = memory
        self.backup_dir = project_root / ".gitwiz" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_safety_backup(self) -> str:
        """Create a complete backup before any destructive operations."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_cleanup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        # Create git branch backup
        subprocess.run(
            ["git", "checkout", "-b", f"backup_{backup_name}"],
            cwd=self.project_root,
            capture_output=True,
            shell=False,
            check=False,
        )

        subprocess.run(
            ["git", "checkout", "main"],
            cwd=self.project_root,
            capture_output=True,
            shell=False,
            check=False,
        )

        return backup_name

    def intelligent_file_consolidation(
        self, duplicates: List[Dict[str, Any]]
    ) -> List[str]:
        """Intelligently consolidate duplicate files."""
        actions = []

        for dup_group in duplicates:
            files = dup_group["files"]
            if len(files) < 2:
                continue

            # Determine the "best" file to keep
            best_file = self._select_best_duplicate(files)

            # Move others to archive or delete if identical
            for file_path in files:
                if file_path != best_file:
                    if self._are_files_identical(
                        Path(self.project_root / best_file),
                        Path(self.project_root / file_path),
                    ):
                        # Files are identical - safe to delete
                        Path(self.project_root / file_path).unlink()
                        actions.append(f"Deleted identical duplicate: {file_path}")
                    else:
                        # Files differ - move to archive
                        archive_path = (
                            self.project_root
                            / "archives"
                            / "duplicates"
                            / Path(file_path).name
                        )
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(self.project_root / file_path, archive_path)
                        actions.append(
                            f"Archived different duplicate: {file_path} -> {archive_path}"
                        )

        return actions

    def _select_best_duplicate(self, files: List[str]) -> str:
        """Select the best file from a group of duplicates."""
        # Prefer files with:
        # 1. More recent timestamps
        # 2. Longer/more descriptive names
        # 3. Higher version numbers

        file_scores = {}
        for file_path in files:
            score = 0
            path_obj = Path(self.project_root / file_path)

            # Newer files score higher
            score += path_obj.stat().st_mtime / 1000000  # Normalize timestamp

            # Longer names often more descriptive
            score += len(path_obj.stem) * 0.1

            # Avoid "2", "copy", "backup" etc.
            if any(
                word in path_obj.name.lower()
                for word in ["2", "copy", "backup", "old", "temp"]
            ):
                score -= 100

            file_scores[file_path] = score

        return max(file_scores.keys(), key=lambda f: file_scores[f])

    def _are_files_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are byte-identical."""
        try:
            return (
                file1.stat().st_size == file2.stat().st_size
                and hashlib.md5(file1.read_bytes()).hexdigest()
                == hashlib.md5(file2.read_bytes()).hexdigest()
            )
        except (OSError, ValueError, RuntimeError):
            return False


def main():
    """Enhanced CLI interface for GITWiz."""
    parser = argparse.ArgumentParser(
        description="GITWiz Enhanced - Adaptive Repository Stewardship System"
    )
    sub = parser.add_subparsers(dest="cmd")

    # Core analysis commands
    sub.add_parser("status", help="Git status")
    sub.add_parser("analyze", help="Basic repository state analysis")
    sub.add_parser("deep-analyze", help="Comprehensive repository analysis")

    # Optimization commands
    sub.add_parser("optimize", help="Basic repository optimization")
    sub.add_parser("intelligent-optimize", help="AI-powered intelligent optimization")
    sub.add_parser("fix-lint", help="Apply persistent linting fixes")

    # Archive management commands
    sub.add_parser("analyze-zips", help="Analyze all ZIP files in repository")
    sub.add_parser("consolidate-zips", help="Consolidate and optimize ZIP archives")

    # Documentation commands
    sub.add_parser("organize-docs", help="Organize documentation structure")
    sub.add_parser("doc-audit", help="Audit documentation organization")

    # Security commands
    sub.add_parser("security-scan", help="Comprehensive security analysis")
    sub.add_parser("security-fix", help="Apply security fixes")

    # Learning and memory commands
    sub.add_parser("learn", help="Learn from new issue pattern")
    sub.add_parser("memory", help="Show memory/learning statistics")
    sub.add_parser("reset-memory", help="Reset learning memory (use with caution)")

    # New dependency management commands
    deps_parser = sub.add_parser("dependencies", help="Dependency management")
    deps_parser.add_argument("--scan", action="store_true", help="Scan dependencies")
    deps_parser.add_argument(
        "--auto-update", action="store_true", help="Auto-update dependencies"
    )
    deps_parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run mode"
    )

    # Workflow commands
    workflow_parser = sub.add_parser("workflow", help="Execute optimized workflows")
    workflow_parser.add_argument(
        "--execute",
        choices=["full_optimization", "security_audit", "maintenance"],
        help="Execute specific workflow",
    )
    workflow_parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run mode"
    )

    # Reporting commands
    sub.add_parser("report", help="Generate comprehensive optimization report")

    # Repository structure commands
    sub.add_parser(
        "ideal-structure", help="Show ideal repository structure recommendations"
    )
    sub.add_parser("apply-structure", help="Apply recommended repository structure")

    args = parser.parse_args()

    gitwiz = EnhancedGITWiz()

    if args.cmd == "status":
        gitwiz.status()
    elif args.cmd == "analyze":
        state = gitwiz.analyze_repository_state()
        print(json.dumps(asdict(state), indent=2))
    elif args.cmd == "deep-analyze":
        result = gitwiz.comprehensive_repository_analysis()
        print(json.dumps(result, indent=2, default=str))
    elif args.cmd == "optimize":
        result = gitwiz.optimize_repository()
        print(json.dumps(result, indent=2, default=str))
    elif args.cmd == "intelligent-optimize":
        result = gitwiz.intelligent_repository_optimization()
        print(json.dumps(result, indent=2, default=str))
        # Learn from the optimization
        gitwiz.learn_from_optimization(result)
    elif args.cmd == "fix-lint":
        success = gitwiz.persistent_lint_fix()
        print("Linting fixes applied successfully" if success else "No fixes applied")
    elif args.cmd == "analyze-zips":
        result = gitwiz._analyze_all_zip_files()
        print(json.dumps(result, indent=2, default=str))
    elif args.cmd == "security-scan":
        result = gitwiz._comprehensive_security_scan()
        print(json.dumps(result, indent=2, default=str))
    elif args.cmd == "doc-audit":
        result = gitwiz._analyze_documentation_structure()
        print(json.dumps(result, indent=2, default=str))
    elif args.cmd == "memory":
        # Show memory statistics from database
        with sqlite3.connect(gitwiz.memory_db) as conn:
            patterns = conn.execute("SELECT COUNT(*) FROM issue_patterns").fetchone()[0]
            states = conn.execute("SELECT COUNT(*) FROM repo_states").fetchone()[0]
            print("📊 GITWiz Memory Statistics:")
            print(f"   Issue Patterns Learned: {patterns}")
            print(f"   Repository States Recorded: {states}")
            print(f"   Memory Database: {gitwiz.memory_db}")
    elif args.cmd == "dependencies":
        if args.scan or args.auto_update:
            result = gitwiz.comprehensive_dependency_management(
                auto_update=args.auto_update, dry_run=args.dry_run
            )
            print(json.dumps(result, indent=2, default=str))
        else:
            print("📦 Dependency Management Options:")
            print("  --scan: Scan all dependencies for updates")
            print("  --auto-update: Auto-update dependencies (use with --dry-run)")
    elif args.cmd == "workflow":
        if args.execute:
            result = gitwiz.execute_optimized_workflow(
                workflow_type=args.execute, dry_run=args.dry_run
            )
            print(json.dumps(result, indent=2, default=str))
        else:
            print("🔄 Available Workflows:")
            print("  full_optimization: Complete repository optimization")
            print("  security_audit: Security-focused audit and fixes")
            print("  maintenance: Regular maintenance tasks")
    elif args.cmd == "report":
        report = gitwiz.generate_optimization_report()
        print(report)
    elif args.cmd == "ideal-structure":
        print("🏗️  Ideal Repository Structure Recommendations:")
        print(
            """
        📁 Root Level (minimal files):
        ├── README.md (primary documentation)
        ├── LICENSE
        ├── .gitignore
        ├── requirements.txt / package.json
        └── docker-compose.yml (if applicable)

        📁 Organized Directories:
        ├── 📂 src/ (source code)
        ├── 📂 tests/ (test files)
        ├── 📂 docs/ (documentation)
        │   ├── deployment/
        │   ├── integration/
        │   └── status/
        ├── 📂 scripts/ (automation scripts)
        ├── 📂 configs/ (configuration files)
        ├── 📂 assets/ (images, resources)
        └── 📂 archives/ (ZIP files, organized by purpose)
        """
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
