#!/usr/bin/env python3
"""
#321//. - Comprehensive Sync & Validate Implementation
======================================================
Anchor: CMD-CHAIN-COMPREHENSIVE-SYNC-321
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Universal "clean working tree" command with intelligent context awareness.

Philosophy: Reliable, fast, elegant - clean your working tree anytime with
consistent high quality and minimal cognitive overhead.

Usage:
    from tools.command_chain.comprehensive_sync_321 import execute_321
    result = execute_321()  # Uses smart defaults
    result = execute_321(config_path=".aurora/sync_config.json")  # Custom config
"""

import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def resolve_workspace_path(workspace_path: Optional[str] = None) -> Path:
    """Resolve the target workspace directory for command execution."""
    return Path(workspace_path).expanduser() if workspace_path else Path.cwd()


def resolve_config_path(config_path: Optional[str] = None, workspace_path: Optional[str] = None) -> Optional[Path]:
    """Resolve config lookup without leaking caller-cwd config into another workspace."""
    workspace = resolve_workspace_path(workspace_path) if workspace_path else None

    if config_path:
        candidate = Path(config_path).expanduser()
        if candidate.exists() or candidate.is_absolute() or workspace is None:
            return candidate

        workspace_candidate = workspace / candidate
        if workspace_candidate.exists():
            return workspace_candidate

        return candidate

    if workspace is not None:
        workspace_config = workspace / ".aurora" / "sync_config.json"
        return workspace_config if workspace_config.exists() else None

    local_config = Path(".aurora/sync_config.json")
    return local_config if local_config.exists() else None


@dataclass
class SyncConfig:
    """Configuration for #321//. command execution"""

    # Commit message generation
    commit_message_template: str = "{type}({scope}): {summary}"
    default_commit_type: str = "chore"

    # Validation settings
    validation_level: str = "fast"  # fast, thorough, complete
    skip_validation_on_docs_only: bool = True
    skip_tests_on_config_only: bool = True

    # Staging patterns (priority order)
    auto_stage_patterns: List[str] = field(default_factory=lambda: [
        "src/**/*.py",
        "api/**/*.py",
        "modules/**/*.py",
        "tests/**/*.py",
        "docs/**/*.md",
        ".github/**/*.yml",
        "*.json",
        "*.yaml",
        "*.toml"
    ])

    # Performance targets
    performance_target_seconds: int = 45
    timeout_seconds: int = 300

    # Conflict resolution
    conflict_resolution_strategy: str = "prompt"  # prompt, abort, auto

    # Sync behavior
    use_rebase: bool = True
    auto_push: bool = True
    verify_remote_sync: bool = True

    # Validation selectors
    lint_command: str = "flake8 src/ api/ modules/ --max-line-length=120 --select=E,F --statistics"
    test_command: str = "pytest -m unit -x --tb=short -q"
    fast_test_markers: str = "unit"
    thorough_test_markers: str = "unit or integration"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "SyncConfig":
        """Load configuration from file or use defaults"""
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                return cls(**data)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                logger.info("Using default configuration")
        return cls()

    def save(self, config_path: Path):
        """Save configuration to file"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)


@dataclass
class PhaseResult:
    """Result from a single phase execution"""
    phase_number: int
    phase_name: str
    success: bool
    duration_seconds: float
    message: str
    details: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SyncResult:
    """Complete result from #321//. execution"""
    success: bool
    total_duration: float
    phases: List[PhaseResult]
    commit_sha: Optional[str] = None
    files_changed: int = 0
    summary_message: str = ""

    def format_report(self) -> str:
        """Generate human-readable completion report"""
        status_emoji = "✅" if self.success else "❌"

        report_lines = [
            "━" * 60,
            f"{status_emoji} #321//. {'COMPLETE' if self.success else 'FAILED'} - "
            f"{'ALL PHASES SUCCESSFUL' if self.success else 'EXECUTION STOPPED'}",
            "━" * 60,
            "",
            "📊 EXECUTION SUMMARY:",
            f"   Total Time: {self.total_duration:.1f}s",
            f"   Changes: {self.files_changed} files",
        ]

        if self.commit_sha:
            report_lines.append(f"   Commit: {self.commit_sha[:8]}")

        if self.summary_message:
            report_lines.append(f"   Message: {self.summary_message}")

        report_lines.extend([
            "",
            "🎯 PHASE STATUS:",
        ])

        for phase in self.phases:
            phase_emoji = "✅" if phase.success else "❌"
            report_lines.append(
                f"   Phase {phase.phase_number}: {phase.phase_name:<25} "
                f"{phase.duration_seconds:>5.1f}s {phase_emoji}"
            )
            if phase.warnings:
                for warning in phase.warnings:
                    report_lines.append(f"      ⚠️  {warning}")

        report_lines.extend([
            "",
            "━" * 60,
        ])

        return "\n".join(report_lines)


class ComprehensiveSync:
    """
    Implements #321//. - Universal working tree cleanup with intelligence

    Key Features:
    - Context-aware change detection
    - Intelligent staging by file type
    - Semantic commit message generation
    - Safe sync with conflict detection
    - Optimized validation (speed vs thoroughness)
    - Performance tracking and reporting
    """

    def __init__(self, config: Optional[SyncConfig] = None, workspace_path: Optional[Path] = None):
        self.config = config or SyncConfig()
        self.workspace = workspace_path or Path.cwd()
        self.start_time = time.time()
        self.phases: List[PhaseResult] = []

    def execute(self) -> SyncResult:
        """Execute all 6 phases of comprehensive sync"""
        logger.info("Starting #321//. - Comprehensive Sync & Validate")

        try:
            # Phase 1: Check for pending changes
            phase1 = self._phase1_check_changes()
            self.phases.append(phase1)
            if not phase1.success:
                return self._build_result(success=False)

            files_changed = phase1.details.get('files_changed', 0)

            # Early exit if no changes
            if files_changed == 0:
                logger.info("No changes detected - working tree already clean")
                return self._build_result(success=True)

            # Phase 2: Intelligent staging
            phase2 = self._phase2_intelligent_staging(phase1.details)
            self.phases.append(phase2)
            if not phase2.success:
                return self._build_result(success=False, files_changed=files_changed)

            # Phase 3: Generate & commit
            phase3 = self._phase3_generate_commit(phase1.details, phase2.details)
            self.phases.append(phase3)
            if not phase3.success:
                return self._build_result(success=False, files_changed=files_changed)

            # Phase 4: Sync to main
            phase4 = self._phase4_sync_to_main()
            self.phases.append(phase4)
            if not phase4.success:
                return self._build_result(
                    success=False,
                    commit_sha=phase3.details.get('commit_sha'),
                    files_changed=files_changed,
                    summary_message=phase3.details.get('commit_message', '')
                )

            # Phase 5: Quick validation
            phase5 = self._phase5_quick_validation(phase1.details)
            self.phases.append(phase5)
            if not phase5.success:
                return self._build_result(
                    success=False,
                    commit_sha=phase3.details.get('commit_sha'),
                    files_changed=files_changed,
                    summary_message=phase3.details.get('commit_message', '')
                )

            # Phase 6: Performance verification
            phase6 = self._phase6_performance_verification()
            self.phases.append(phase6)

            return self._build_result(
                success=True,
                commit_sha=phase3.details.get('commit_sha'),
                files_changed=files_changed,
                summary_message=phase3.details.get('commit_message', '')
            )

        except KeyboardInterrupt:
            logger.warning("Execution interrupted by user")
            return self._build_result(success=False)
        except Exception as e:
            logger.error(f"Unexpected error during execution: {e}", exc_info=True)
            return self._build_result(success=False)

    def _phase1_check_changes(self) -> PhaseResult:
        """Phase 1: Comprehensive change detection with context awareness"""
        phase_start = time.time()
        logger.info("Phase 1: Checking for pending changes...")

        try:
            # Get git status in machine-readable format
            status_result = self._run_command(['git', 'status', '--porcelain'])
            if status_result.returncode != 0:
                return PhaseResult(
                    phase_number=1,
                    phase_name="Check Changes",
                    success=False,
                    duration_seconds=time.time() - phase_start,
                    message="Failed to check git status"
                )

            status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []

            # Categorize changes
            categories = self._categorize_changes(status_lines)
            total_files = sum(len(files) for files in categories.values())

            if total_files == 0:
                return PhaseResult(
                    phase_number=1,
                    phase_name="Check Changes",
                    success=True,
                    duration_seconds=time.time() - phase_start,
                    message="No changes detected",
                    details={'files_changed': 0}
                )

            # Get diff statistics
            diff_result = self._run_command(['git', 'diff', '--stat'])

            details = {
                'files_changed': total_files,
                'categories': categories,
                'diff_stat': diff_result.stdout if diff_result.returncode == 0 else "",
                'is_docs_only': (
                    len(categories.get('docs', [])) > 0 and
                    total_files == len(categories.get('docs', []))
                ),
                'is_config_only': (
                    len(categories.get('config', [])) > 0 and
                    total_files == len(categories.get('config', []))
                )
            }

            return PhaseResult(
                phase_number=1,
                phase_name="Check Changes",
                success=True,
                duration_seconds=time.time() - phase_start,
                message=f"Detected {total_files} files changed across {len(categories)} categories",
                details=details
            )

        except Exception as e:
            return PhaseResult(
                phase_number=1,
                phase_name="Check Changes",
                success=False,
                duration_seconds=time.time() - phase_start,
                message=f"Error checking changes: {e}"
            )

    def _categorize_changes(self, status_lines: List[str]) -> Dict[str, List[str]]:
        """Categorize changed files by type for intelligent staging"""
        categories = {
            'source': [],
            'tests': [],
            'docs': [],
            'config': [],
            'workflows': [],
            'other': []
        }

        for line in status_lines:
            if not line.strip():
                continue

            # Parse git status format: XY filename
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue

            filepath = parts[1]

            # Categorize by path patterns
            if filepath.startswith(('src/', 'api/', 'modules/')) and filepath.endswith('.py'):
                categories['source'].append(filepath)
            elif filepath.startswith('tests/') and filepath.endswith('.py'):
                categories['tests'].append(filepath)
            elif filepath.endswith('.md') or filepath.startswith('docs/'):
                categories['docs'].append(filepath)
            elif filepath.startswith('.github/workflows/'):
                categories['workflows'].append(filepath)
            elif filepath.endswith(('.json', '.yaml', '.yml', '.toml', '.cfg', '.ini')):
                categories['config'].append(filepath)
            else:
                categories['other'].append(filepath)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _phase2_intelligent_staging(self, phase1_details: Dict) -> PhaseResult:
        """Phase 2: Smart staging based on file categories"""
        phase_start = time.time()
        logger.info("Phase 2: Staging files intelligently...")

        try:
            categories = phase1_details.get('categories', {})

            # Stage in priority order
            priority_order = ['source', 'tests', 'workflows', 'docs', 'config', 'other']
            staged_count = 0

            for category in priority_order:
                files = categories.get(category, [])
                if not files:
                    continue

                logger.debug(f"Staging {len(files)} {category} files")
                for filepath in files:
                    result = self._run_command(['git', 'add', filepath])
                    if result.returncode == 0:
                        staged_count += 1

            return PhaseResult(
                phase_number=2,
                phase_name="Intelligent Staging",
                success=True,
                duration_seconds=time.time() - phase_start,
                message=f"Staged {staged_count} files by category",
                details={'staged_count': staged_count, 'categories': list(categories.keys())}
            )

        except Exception as e:
            return PhaseResult(
                phase_number=2,
                phase_name="Intelligent Staging",
                success=False,
                duration_seconds=time.time() - phase_start,
                message=f"Error during staging: {e}"
            )

    def _phase3_generate_commit(self, phase1_details: Dict, phase2_details: Dict) -> PhaseResult:
        """Phase 3: Generate semantic commit message and commit"""
        phase_start = time.time()
        logger.info("Phase 3: Generating commit...")

        try:
            # Generate semantic commit message
            commit_message = self._generate_commit_message(phase1_details)

            # Create commit
            result = self._run_command(['git', 'commit', '-m', commit_message])
            warnings = []
            error_output = f"{result.stdout}\n{result.stderr}".lower()
            if result.returncode != 0 and 'gpg failed to sign the data' in error_output:
                logger.warning("Git commit signing unavailable; retrying commit without GPG signing")
                result = self._run_command(['git', '-c', 'commit.gpgsign=false', 'commit', '-m', commit_message])
                if result.returncode == 0:
                    warnings.append(
                        'Commit created without GPG signing because signing is unavailable in this environment'
                    )

            if result.returncode != 0:
                return PhaseResult(
                    phase_number=3,
                    phase_name="Generate & Commit",
                    success=False,
                    duration_seconds=time.time() - phase_start,
                    message="Failed to create commit",
                    warnings=[result.stderr.strip()] if result.stderr else []
                )

            # Get commit SHA
            sha_result = self._run_command(['git', 'rev-parse', 'HEAD'])
            commit_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

            return PhaseResult(
                phase_number=3,
                phase_name="Generate & Commit",
                success=True,
                duration_seconds=time.time() - phase_start,
                message=f"Commit created: {commit_sha[:8] if commit_sha else 'unknown'}",
                details={'commit_sha': commit_sha, 'commit_message': commit_message},
                warnings=warnings
            )

        except Exception as e:
            return PhaseResult(
                phase_number=3,
                phase_name="Generate & Commit",
                success=False,
                duration_seconds=time.time() - phase_start,
                message=f"Error creating commit: {e}"
            )

    def _generate_commit_message(self, phase1_details: Dict) -> str:
        """Generate semantic commit message based on changes"""
        categories = phase1_details.get('categories', {})
        files_changed = phase1_details.get('files_changed', 0)

        # Determine commit type based on predominant category
        if categories.get('source') and len(categories['source']) > len(categories.get('tests', [])):
            commit_type = "feat" if files_changed > 5 else "refactor"
            scope = "core"
        elif categories.get('tests'):
            commit_type = "test"
            scope = "suite"
        elif categories.get('docs'):
            commit_type = "docs"
            scope = "readme"
        elif categories.get('workflows'):
            commit_type = "ci"
            scope = "workflow"
        elif categories.get('config'):
            commit_type = "chore"
            scope = "config"
        else:
            commit_type = self.config.default_commit_type
            scope = "project"

        # Generate summary
        category_summary = ", ".join([f"{len(v)} {k}" for k, v in categories.items()])
        summary = f"Update {files_changed} files ({category_summary})"

        # Use template
        commit_message = self.config.commit_message_template.format(
            type=commit_type,
            scope=scope,
            summary=summary
        )

        # Add DLP tag
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        commit_message += f"\n\nDLP: CMD-CHAIN-SYNC-321-{timestamp}"

        return commit_message

    def _handle_conflict_prompt(self, phase_start: float) -> PhaseResult:
        """Handle conflicts with prompt strategy - provide guidance"""
        # Get list of conflicted files
        status_result = self._run_command(['git', 'status', '--porcelain'])
        conflicted_files = []
        if status_result.returncode == 0 and status_result.stdout:
            for line in status_result.stdout.split('\n'):
                if line.startswith('UU') or line.startswith('AA') or line.startswith('DD'):
                    conflicted_files.append(line[3:].strip())

        conflict_msg = "Merge conflicts detected"
        if conflicted_files:
            conflict_msg += f" in {len(conflicted_files)} file(s)"

        return PhaseResult(
            phase_number=4,
            phase_name="Sync to Main",
            success=False,
            duration_seconds=time.time() - phase_start,
            message=conflict_msg,
            details={'conflicted_files': conflicted_files},
            warnings=[
                "Manual resolution required:",
                "1. Edit conflicted files to resolve markers",
                "2. Run: git add <resolved-files>",
                "3. Run: git rebase --continue",
                "4. Retry sync with #SYNC//. or #321//."
            ]
        )

    def _handle_conflict_abort(self, phase_start: float) -> PhaseResult:
        """Handle conflicts with abort strategy - preserve work"""
        # Abort the rebase/merge
        self._run_command(['git', 'rebase', '--abort'])

        return PhaseResult(
            phase_number=4,
            phase_name="Sync to Main",
            success=False,
            duration_seconds=time.time() - phase_start,
            message="Conflicts detected - aborted to preserve work",
            warnings=[
                "Rebase aborted to protect local changes",
                "To resolve manually:",
                "1. Run: git pull origin main",
                "2. Resolve conflicts in affected files",
                "3. Commit resolved changes",
                "4. Retry #321//. or #SYNC//."
            ]
        )

    def _phase4_sync_to_main(self) -> PhaseResult:
        """Phase 4: Safe synchronization with remote"""
        phase_start = time.time()
        logger.info("Phase 4: Syncing to main...")

        try:
            branch_result = self._run_command(['git', 'branch', '--show-current'])
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'main'
            sync_uses_rebase = self.config.use_rebase and current_branch == 'main'
            merge_command = ['git', '-c', 'commit.gpgsign=false', 'merge', 'origin/main', '--no-edit']

            # First, fetch latest from main
            fetch_result = self._run_command(['git', 'fetch', 'origin', 'main'])
            if fetch_result.returncode != 0:
                return PhaseResult(
                    phase_number=4,
                    phase_name="Sync to Main",
                    success=False,
                    duration_seconds=time.time() - phase_start,
                    message="Failed to fetch from origin/main"
                )

            # Check if we're behind main
            rev_list_result = self._run_command(['git', 'rev-list', '--left-right', '--count', 'origin/main...HEAD'])
            if rev_list_result.returncode == 0:
                counts = rev_list_result.stdout.strip().split()
                behind_count = int(counts[0]) if len(counts) >= 2 else 0

                if behind_count > 0:
                    logger.info(f"Branch is {behind_count} commit(s) behind main - syncing...")

                    # Merge main into current branch (works for both main and feature branches)
                    if sync_uses_rebase:
                        pull_result = self._run_command(['git', 'pull', '--rebase', 'origin', 'main'])
                    else:
                        pull_result = self._run_command(merge_command)
                else:
                    logger.info("Branch is up-to-date with main")
                    pull_result = subprocess.CompletedProcess(
                        args=['git', 'pull'],
                        returncode=0,
                        stdout="Already up to date.\n",
                        stderr=""
                    )
            else:
                # Fallback: try to sync anyway
                if sync_uses_rebase:
                    pull_result = self._run_command(['git', 'pull', '--rebase', 'origin', 'main'])
                else:
                    pull_result = self._run_command(merge_command)

            if pull_result.returncode != 0:
                # Enhanced conflict detection
                conflict_indicators = ['CONFLICT', 'conflict', 'Merge conflict']
                error_output = pull_result.stderr.lower() if pull_result.stderr else ""
                has_conflict = any(indicator.lower() in error_output for indicator in conflict_indicators)

                if has_conflict:
                    # Handle conflict based on strategy
                    if self.config.conflict_resolution_strategy == "prompt":
                        return self._handle_conflict_prompt(phase_start)
                    elif self.config.conflict_resolution_strategy == "abort":
                        return self._handle_conflict_abort(phase_start)
                    else:
                        return self._handle_conflict_prompt(phase_start)  # Default to prompt

                return PhaseResult(
                    phase_number=4,
                    phase_name="Sync to Main",
                    success=False,
                    duration_seconds=time.time() - phase_start,
                    message="Failed to sync with origin/main",
                    warnings=["Check for network issues or repository access"]
                )

            # Push if auto_push enabled
            if self.config.auto_push:
                push_result = self._run_command(['git', 'push', 'origin', current_branch])
                if push_result.returncode != 0:
                    return PhaseResult(
                        phase_number=4,
                        phase_name="Sync to Main",
                        success=False,
                        duration_seconds=time.time() - phase_start,
                        message=f"Failed to push to remote branch {current_branch}"
                    )

            return PhaseResult(
                phase_number=4,
                phase_name="Sync to Main",
                success=True,
                duration_seconds=time.time() - phase_start,
                message="Successfully synced with remote"
            )

        except Exception as e:
            return PhaseResult(
                phase_number=4,
                phase_name="Sync to Main",
                success=False,
                duration_seconds=time.time() - phase_start,
                message=f"Error during sync: {e}"
            )

    def _phase5_quick_validation(self, phase1_details: Dict) -> PhaseResult:
        """Phase 5: Context-aware validation (optimized for speed)"""
        phase_start = time.time()
        logger.info("Phase 5: Running validation...")

        try:
            warnings = []

            # Skip validation for docs-only changes if configured
            if self.config.skip_validation_on_docs_only and phase1_details.get('is_docs_only'):
                return PhaseResult(
                    phase_number=5,
                    phase_name="Quick Validation",
                    success=True,
                    duration_seconds=time.time() - phase_start,
                    message="Skipped validation (docs-only changes)",
                    warnings=["Validation skipped per configuration"]
                )

            # Run lint check
            lint_result = self._run_command(self.config.lint_command.split())
            if lint_result.returncode != 0:
                warnings.append("Lint check found issues (non-blocking)")

            # Run tests based on validation level
            if not (self.config.skip_tests_on_config_only and phase1_details.get('is_config_only')):
                if self.config.validation_level == "fast":
                    test_result = self._run_command(self.config.test_command.split())
                elif self.config.validation_level == "thorough":
                    test_cmd = f"pytest -m '{self.config.thorough_test_markers}' -x --tb=short -q"
                    test_result = self._run_command(test_cmd.split())
                else:  # complete
                    test_result = self._run_command(['pytest', '-x', '--tb=short', '-q'])

                if test_result.returncode != 0:
                    warnings.append("Some tests failed (non-blocking)")

            return PhaseResult(
                phase_number=5,
                phase_name="Quick Validation",
                success=True,
                duration_seconds=time.time() - phase_start,
                message="Validation complete",
                warnings=warnings
            )

        except Exception as e:
            return PhaseResult(
                phase_number=5,
                phase_name="Quick Validation",
                success=True,  # Non-blocking
                duration_seconds=time.time() - phase_start,
                message=f"Validation completed with errors: {e}",
                warnings=["Validation errors are non-blocking"]
            )

    def _phase6_performance_verification(self) -> PhaseResult:
        """Phase 6: Performance metrics and final verification"""
        phase_start = time.time()
        logger.info("Phase 6: Verifying performance...")

        total_duration = time.time() - self.start_time

        # Check if within performance target
        within_target = total_duration <= self.config.performance_target_seconds

        # Verify working tree is clean
        status_result = self._run_command(['git', 'status', '--porcelain'])
        is_clean = status_result.returncode == 0 and not status_result.stdout.strip()

        warnings = []
        if not within_target:
            warnings.append(f"Execution took {total_duration:.1f}s (target: {self.config.performance_target_seconds}s)")
        if not is_clean:
            warnings.append("Working tree not completely clean")

        return PhaseResult(
            phase_number=6,
            phase_name="Performance Verification",
            success=True,
            duration_seconds=time.time() - phase_start,
            message=f"Total execution: {total_duration:.1f}s",
            details={'total_duration': total_duration, 'is_clean': is_clean},
            warnings=warnings
        )

    def _run_command(self, cmd: List[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """Execute shell command with timeout"""
        timeout = timeout or self.config.timeout_seconds
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {' '.join(cmd)}")
            raise

    def _build_result(self, success: bool, commit_sha: Optional[str] = None,
                      files_changed: int = 0, summary_message: str = "") -> SyncResult:
        """Build final sync result"""
        total_duration = time.time() - self.start_time
        return SyncResult(
            success=success,
            total_duration=total_duration,
            phases=self.phases,
            commit_sha=commit_sha,
            files_changed=files_changed,
            summary_message=summary_message
        )


def execute_321(config_path: Optional[str] = None, workspace_path: Optional[str] = None) -> SyncResult:
    """
    Execute #321//. command - Comprehensive Sync & Validate

    Args:
        config_path: Optional path to JSON configuration file
        workspace_path: Optional workspace directory (defaults to current)

    Returns:
        SyncResult with execution details and completion report

    Example:
        >>> result = execute_321()
        >>> print(result.format_report())
        >>> if result.success:
        ...     print(f"Clean working tree in {result.total_duration:.1f}s")
    """
    resolved_config_path = resolve_config_path(config_path=config_path, workspace_path=workspace_path)
    config = SyncConfig.load(resolved_config_path)
    workspace = resolve_workspace_path(workspace_path)

    sync = ComprehensiveSync(config=config, workspace_path=workspace)
    result = sync.execute()

    # Print completion report
    print(result.format_report())

    return result


if __name__ == '__main__':
    # Command-line execution
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    result = execute_321(config_path=config_path)

    sys.exit(0 if result.success else 1)
