#!/usr/bin/env python3
"""
Real Command Implementations
============================
Anchor: CMD-CHAIN-REAL-IMPL-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Real subprocess-based implementations for command handlers.
Replaces mock implementations with actual git, pytest, lint operations.

Pattern:
  Mock → Real → Subprocess → Parse → Return
"""

import subprocess
import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class RealCommandImplementations:
    """Real implementations for command chain operations"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize with workspace root.
        
        Args:
            workspace_root: Path to workspace root (default: current directory)
        """
        self.workspace_root = workspace_root or os.getcwd()
    
    # ==================== GIT OPERATIONS ====================
    
    def git_status(self) -> Dict[str, Any]:
        """
        Get comprehensive git status.
        
        Returns dict with:
        - branch: current branch name
        - clean: whether working tree is clean
        - modified_files: list of modified files
        - untracked_files: list of untracked files
        - staged_files: list of staged files
        - ahead: commits ahead of remote
        - behind: commits behind remote
        - total_changes: total number of changes
        """
        try:
            result = {
                'branch': self._git_current_branch(),
                'clean': False,
                'modified_files': [],
                'untracked_files': [],
                'staged_files': [],
                'ahead': 0,
                'behind': 0,
                'total_changes': 0
            }
            
            # Get porcelain status
            status_output = self._run_command(['git', 'status', '--porcelain'])
            
            if not status_output.strip():
                result['clean'] = True
                return result
            
            # Parse porcelain output
            for line in status_output.strip().split('\n'):
                if not line:
                    continue
                
                status_code = line[:2]
                filepath = line[3:].strip()
                
                # Staged changes
                if status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                    result['staged_files'].append(filepath)
                
                # Modified/untracked
                if status_code[1] == 'M':
                    result['modified_files'].append(filepath)
                elif status_code == '??':
                    result['untracked_files'].append(filepath)
            
            # Get ahead/behind info
            try:
                ahead_behind = self._run_command([
                    'git', 'rev-list', '--left-right', '--count',
                    'HEAD...@{upstream}'
                ])
                parts = ahead_behind.strip().split()
                if len(parts) == 2:
                    result['ahead'] = int(parts[0])
                    result['behind'] = int(parts[1])
            except Exception:
                # No upstream or other error
                pass
            
            result['total_changes'] = (
                len(result['staged_files']) +
                len(result['modified_files']) +
                len(result['untracked_files'])
            )
            result['clean'] = result['total_changes'] == 0
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'clean': False,
                'branch': 'unknown',
                'total_changes': 0
            }
    
    def git_add_intelligent(self, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Intelligently stage files by category.
        
        Args:
            files: Specific files to stage, or None for smart staging
            
        Returns dict with:
        - staged_count: number of files staged
        - categories: dict of files by category
        - success: whether staging succeeded
        """
        try:
            if files:
                # Stage specific files
                self._run_command(['git', 'add'] + files)
                return {
                    'success': True,
                    'staged_count': len(files),
                    'categories': {'specified': files}
                }
            
            # Smart staging by category
            status = self.git_status()
            categories = {
                'source': [],
                'tests': [],
                'docs': [],
                'config': [],
                'other': []
            }
            
            all_files = (
                status['modified_files'] +
                status['untracked_files']
            )
            
            # Categorize files
            for filepath in all_files:
                if filepath.startswith('src/') or filepath.endswith('.py'):
                    if 'test' in filepath.lower():
                        categories['tests'].append(filepath)
                    else:
                        categories['source'].append(filepath)
                elif filepath.endswith('.md') or filepath.startswith('docs/'):
                    categories['docs'].append(filepath)
                elif filepath.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
                    categories['config'].append(filepath)
                else:
                    categories['other'].append(filepath)
            
            # Stage by priority: source, tests, docs, config, other
            staged_files = []
            for category in ['source', 'tests', 'docs', 'config', 'other']:
                if categories[category]:
                    self._run_command(['git', 'add'] + categories[category])
                    staged_files.extend(categories[category])
            
            return {
                'success': True,
                'staged_count': len(staged_files),
                'categories': {k: v for k, v in categories.items() if v}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'staged_count': 0
            }
    
    def git_commit(self, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Create git commit with message.
        
        Args:
            message: Commit message, or None for auto-generated
            
        Returns dict with:
        - success: whether commit succeeded
        - commit_hash: hash of created commit
        - message: commit message used
        """
        try:
            if not message:
                # Auto-generate commit message
                message = self._generate_commit_message()
            
            # Create commit
            output = self._run_command(['git', 'commit', '-m', message])
            
            # Get commit hash
            commit_hash = self._run_command(['git', 'rev-parse', 'HEAD']).strip()
            
            return {
                'success': True,
                'commit_hash': commit_hash[:8],
                'message': message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': message or 'auto-generated'
            }
    
    def git_pull_push(self) -> Dict[str, Any]:
        """
        Pull with rebase and push to remote.
        
        Returns dict with:
        - pull_success: whether pull succeeded
        - push_success: whether push succeeded
        - conflicts: list of conflicting files if any
        - pushed_commits: number of commits pushed
        """
        try:
            result = {
                'pull_success': False,
                'push_success': False,
                'conflicts': [],
                'pushed_commits': 0
            }
            
            # Get current branch
            branch = self._git_current_branch()
            
            # Pull with rebase
            try:
                self._run_command(['git', 'pull', '--rebase', 'origin', branch])
                result['pull_success'] = True
            except subprocess.CalledProcessError as e:
                # Check for conflicts
                status = self.git_status()
                # In real rebase conflicts, files would have conflict markers
                if 'REBASE' in e.output or 'conflict' in e.output.lower():
                    result['conflicts'] = status.get('modified_files', [])
                    return result
                raise
            
            # Count commits to push
            try:
                ahead_count = self._run_command([
                    'git', 'rev-list', '--count', f'origin/{branch}..HEAD'
                ])
                result['pushed_commits'] = int(ahead_count.strip())
            except Exception:
                result['pushed_commits'] = 0
            
            # Push to remote
            self._run_command(['git', 'push', 'origin', branch])
            result['push_success'] = True
            
            return result
            
        except Exception as e:
            return {
                'pull_success': False,
                'push_success': False,
                'error': str(e),
                'conflicts': []
            }
    
    # ==================== TEST OPERATIONS ====================
    
    def run_tests_fast(self) -> Dict[str, Any]:
        """
        Run fast unit tests with pytest.
        
        Returns dict with:
        - success: whether tests passed
        - passed: number of tests passed
        - failed: number of tests failed
        - duration: test duration in seconds
        - failures: list of failed test names
        """
        try:
            start_time = datetime.now()
            
            # Run pytest with unit marker, fast fail
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '-m', 'unit', '-x', '--tb=short', '-q'],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse pytest output
            output = result.stdout + result.stderr
            passed = failed = 0
            failures = []
            
            # Look for summary line like "5 passed in 2.3s"
            for line in output.split('\n'):
                if 'passed' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed' and i > 0:
                            try:
                                passed = int(parts[i-1])
                            except ValueError:
                                pass
                if 'failed' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'failed' and i > 0:
                            try:
                                failed = int(parts[i-1])
                            except ValueError:
                                pass
                if line.startswith('FAILED'):
                    failures.append(line.split()[1] if len(line.split()) > 1 else line)
            
            return {
                'success': result.returncode == 0,
                'passed': passed,
                'failed': failed,
                'duration': duration,
                'failures': failures,
                'output': output[-500:] if len(output) > 500 else output  # Last 500 chars
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Tests timed out after 60 seconds',
                'passed': 0,
                'failed': 0,
                'duration': 60.0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'passed': 0,
                'failed': 0,
                'duration': 0
            }
    
    # ==================== LINT/FORMAT OPERATIONS ====================
    
    def format_code(self) -> Dict[str, Any]:
        """
        Format code with black and isort.
        
        Returns dict with:
        - success: whether formatting succeeded
        - black_changed: number of files changed by black
        - isort_changed: number of files changed by isort
        - errors: list of errors if any
        """
        try:
            result = {
                'success': True,
                'black_changed': 0,
                'isort_changed': 0,
                'errors': []
            }
            
            # Run black
            try:
                black_output = self._run_command(['python', '-m', 'black', '.', '--quiet'])
                # Black's quiet mode doesn't print counts, so we'd need to check git diff
                result['black_changed'] = 0  # Would need to check git diff
            except subprocess.CalledProcessError as e:
                result['errors'].append(f"Black error: {e.stderr}")
                result['success'] = False
            
            # Run isort
            try:
                isort_output = self._run_command(['python', '-m', 'isort', '.', '--quiet'])
                result['isort_changed'] = 0  # Would need to check git diff
            except subprocess.CalledProcessError as e:
                result['errors'].append(f"isort error: {e.stderr}")
                result['success'] = False
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'black_changed': 0,
                'isort_changed': 0
            }
    
    def lint_code(self) -> Dict[str, Any]:
        """
        Run flake8 linting.
        
        Returns dict with:
        - success: whether linting passed (no errors)
        - errors: number of errors
        - warnings: number of warnings
        - files_checked: number of files checked
        - details: list of error details
        """
        try:
            # Run flake8 with config
            result = subprocess.run(
                ['python', '-m', 'flake8', 'src/', 'tools/', 'tests/', '--count', '--statistics'],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            lines = output.split('\n')
            
            errors = 0
            warnings = 0
            details = []
            
            # Parse flake8 output
            for line in lines:
                if ':' in line and any(code in line for code in ['E', 'W', 'F']):
                    details.append(line.strip())
                    if 'E' in line or 'F' in line:
                        errors += 1
                    elif 'W' in line:
                        warnings += 1
            
            return {
                'success': result.returncode == 0,
                'errors': errors,
                'warnings': warnings,
                'files_checked': len(details),
                'details': details[:20]  # First 20 issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'errors': 0,
                'warnings': 0
            }
    
    # ==================== HELPER METHODS ====================
    
    def _run_command(self, cmd: List[str], **kwargs) -> str:
        """
        Run shell command and return output.
        
        Args:
            cmd: Command and arguments as list
            **kwargs: Additional subprocess.run arguments
            
        Returns:
            Command output as string
            
        Raises:
            subprocess.CalledProcessError: If command fails
        """
        result = subprocess.run(
            cmd,
            cwd=self.workspace_root,
            capture_output=True,
            text=True,
            check=True,
            **kwargs
        )
        return result.stdout
    
    def _git_current_branch(self) -> str:
        """Get current git branch name"""
        try:
            return self._run_command(['git', 'branch', '--show-current']).strip()
        except Exception:
            return 'unknown'
    
    def _generate_commit_message(self) -> str:
        """Generate semantic commit message from staged changes"""
        try:
            # Get diff stat
            diff_output = self._run_command(['git', 'diff', '--cached', '--stat'])
            
            # Simple heuristic for commit type
            if 'test' in diff_output.lower():
                prefix = 'test'
            elif 'doc' in diff_output.lower() or '.md' in diff_output:
                prefix = 'docs'
            elif 'fix' in diff_output.lower() or 'bug' in diff_output.lower():
                prefix = 'fix'
            else:
                prefix = 'feat'
            
            # Count files
            files_changed = diff_output.count('|')
            
            return f"{prefix}: Update {files_changed} file{'s' if files_changed != 1 else ''}"
            
        except Exception:
            return "chore: Update project files"
