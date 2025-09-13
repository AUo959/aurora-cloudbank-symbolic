#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import argparse
import json
import os
import subprocess
import zipfile
"""
GITWiz Simple - Basic Repository Management
A simplified version without external dependencies for testing
"""

import argparse
import json
import logging
import os
import sqlite3
import subprocess
import zipfile
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GITWiz")


@dataclass
class RepositoryIssue:
    """Represents a repository issue that GITWiz can track and fix."""

    issue_type: str
    file_path: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    fix_applied: bool = False
    first_seen: str = None
    last_seen: str = None
    fix_count: int = 0


class GITWizSimple:
    """Simplified GITWiz for basic repository management."""

    self.repo_path = Path(repo_path or os.getcwd())
    self.db_path = self.repo_path / ".gitwiz" / "memory.db"
    self.init_memory()

    def init_memory(self):
        """Initialize the SQLite memory database."""
        os.makedirs(self.db_path.parent, exist_ok=True)

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Issues table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    description TEXT,
                    severity TEXT DEFAULT 'medium',
                    fix_applied BOOLEAN DEFAULT 0,
                    first_seen TEXT,
                    last_seen TEXT,
                    fix_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Solutions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_type TEXT NOT NULL,
                    solution_pattern TEXT,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def record_issue(self, issue: RepositoryIssue):
        """Record an issue in memory."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Check if issue already exists
            cursor.execute(
                """
                SELECT id, fix_count FROM issues
                WHERE issue_type = ? AND file_path = ? AND description = ?
            """,
                (issue.issue_type, issue.file_path, issue.description),
            )

            existing = cursor.fetchone()

            if existing:
                # Update existing issue
                cursor.execute(
                    """
                    UPDATE issues
                    SET last_seen = ?, fix_count = ?
                    WHERE id = ?
                """,
                    (
                        datetime.now().isoformat(),
                        existing[1] + (1 if issue.fix_applied else 0),
                        existing[0],
                    ),
                )
            else:
                # Insert new issue
                cursor.execute(
                    """
                    INSERT INTO issues (issue_type, file_path, description, severity,
                                      fix_applied, first_seen, last_seen, fix_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        issue.issue_type,
                        issue.file_path,
                        issue.description,
                        issue.severity,
                        issue.fix_applied,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        1 if issue.fix_applied else 0,
                    ),
                )

            conn.commit()

    def get_repo_status(self) -> Dict[str, Any]:
        """Get comprehensive repository status."""
        status = {
            "repo_path": str(self.repo_path),
            "timestamp": datetime.now().isoformat(),
            "git_status": self._get_git_status(),
            "file_stats": self._get_file_stats(),
            "issues": self._get_stored_issues(),
            "recommendations": [],
        }

        return status

    def _get_git_status(self) -> Dict[str, Any]:
        """Get git repository status."""
        try:
            # Check if it's a git repo            result = subprocess.run(                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode != 0:
                return {"is_git_repo": False}

            # Get git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],            result = subprocess.run(                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            files = result.stdout.strip().split("\n") if result.stdout.strip() else []

            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            current_branch = branch_result.stdout.strip()

            return {
                "is_git_repo": True,
                "current_branch": current_branch,
                "modified_files": [f[3:] for f in files if f.startswith(" M")],
                "new_files": [f[3:] for f in files if f.startswith("??")],
                "staged_files": [f[3:] for f in files if f.startswith("A ")],
                "total_changes": len(files),
            }

        except (OSError, ValueError, RuntimeError) as e:
            return {"is_git_repo": False, "error": str(e)}

    def _get_file_stats(self) -> Dict[str, Any]:
        """Get file statistics for the repository."""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_extension": defaultdict(int),
            "large_files": [],
            "zip_files": [],
        }

        try:
            for root, dirs, files in os.walk(self.repo_path):
                # Skip .git and other hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue

                    file_path = Path(root) / file
                    try:
                        file_size = file_path.stat().st_size
                        stats["total_files"] += 1
                        stats["total_size"] += file_size

                        # Track by extension
                        ext = file_path.suffix.lower()
                        stats["by_extension"][ext] += 1

                        # Track large files (>10MB)
                        if file_size > 10 * 1024 * 1024:
                            stats["large_files"].append(
                                {
                                    "path": str(file_path.relative_to(self.repo_path)),
                                    "size": file_size,
                                }
                            )

                        # Track ZIP files
                        if ext in [".zip", ".tar", ".gz", ".bz2"]:
                            stats["zip_files"].append(str(file_path.relative_to(self.repo_path)))

                    except (OSError, PermissionError):
                        continue

        except (OSError, ValueError, RuntimeError) as e:
            logger.warning(f"Error getting file stats: {e}")

        return stats

    def _get_stored_issues(self) -> List[Dict[str, Any]]:
        """Get issues from memory database."""
        issues = []

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT issue_type, file_path, description, severity,
                           fix_applied, first_seen, last_seen, fix_count
                    FROM issues
                    ORDER BY last_seen DESC
                    LIMIT 20
                """
                )

                for row in cursor.fetchall():
                    issues.append(
                        {
                            "issue_type": row[0],
                            "file_path": row[1],
                            "description": row[2],
                            "severity": row[3],
                            "fix_applied": bool(row[4]),
                            "first_seen": row[5],
                            "last_seen": row[6],
                            "fix_count": row[7],
                        }
                    )

        except (OSError, ValueError, RuntimeError) as e:
            logger.warning(f"Error getting stored issues: {e}")

        return issues

    def analyze_repository(self) -> Dict[str, Any]:
        """Analyze the repository for issues and optimization opportunities."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(self.repo_path),
            "issues_found": [],
            "optimizations": [],
            "archive_analysis": [],
        }

        # Analyze markdown files for common issues
        self._analyze_markdown_files(analysis)

        # Analyze ZIP files
        self._analyze_zip_files(analysis)

        # Check for common repo issues
        self._check_common_repo_issues(analysis)

        return analysis

    def _analyze_markdown_files(self, analysis: Dict[str, Any]):
        """Analyze markdown files for common issues."""
        md_files = list(self.repo_path.glob("**/*.md"))

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")

                # Check for MD022 (Headers should be surrounded by blank lines)
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().startswith("#"):
                        # Check if header has blank line before it (except first line)
                        if i > 0 and lines[i - 1].strip() != "":
                            issue = RepositoryIssue(
                                issue_type="MD022",
                                file_path=str(md_file.relative_to(self.repo_path)),
                                description=f"Header at line {i + 1} should have blank line before it",
                                severity="low",
                            )
                            self.record_issue(issue)
                            analysis["issues_found"].append(asdict(issue))

                        # Check if header has blank line after it
                        if i < len(lines) - 1 and lines[i + 1].strip() != "":
                            issue = RepositoryIssue(
                                issue_type="MD022",
                                file_path=str(md_file.relative_to(self.repo_path)),
                                description=f"Header at line {i + 1} should have blank line after it",
                                severity="low",
                            )
                            self.record_issue(issue)
                            analysis["issues_found"].append(asdict(issue))

            except (OSError, ValueError, RuntimeError) as e:
                logger.warning(f"Error analyzing {md_file}: {e}")

    def _analyze_zip_files(self, analysis: Dict[str, Any]):
        """Analyze ZIP files in the repository."""
        zip_files = list(self.repo_path.glob("**/*.zip"))

        for zip_file in zip_files:
            try:
                with zipfile.ZipFile(zip_file, "r") as zf:
                    file_list = zf.namelist()
                    total_size = sum(zf.getinfo(name).file_size for name in file_list)

                    zip_analysis = {
                        "path": str(zip_file.relative_to(self.repo_path)),
                        "file_count": len(file_list),
                        "total_uncompressed_size": total_size,
                        "compressed_size": zip_file.stat().st_size,
                        "compression_ratio": (
                            (1 - zip_file.stat().st_size / total_size) * 100 if total_size > 0 else 0
                        ),
                        "contains_nested_archives": any(name.endswith((".zip", ".tar", ".gz")) for name in file_list),
                    }

                    analysis["archive_analysis"].append(zip_analysis)

                    # Flag large archives as potential optimization targets
                    if zip_file.stat().st_size > 50 * 1024 * 1024:  # >50MB
                        analysis["optimizations"].append(
                            f"Large archive: {zip_file.name} ({zip_file.stat().st_size / (1024 * 1024):.1f}MB)"
                        )

            except (OSError, ValueError, RuntimeError) as e:
                logger.warning(f"Error analyzing ZIP file {zip_file}: {e}")

    def _check_common_repo_issues(self, analysis: Dict[str, Any]):
        """Check for common repository structure issues."""

        # Check for README
        if not any((self.repo_path / name).exists() for name in ["README.md", "README.txt", "README"]):
            analysis["issues_found"].append(
                {
                    "issue_type": "missing_readme",
                    "file_path": ".",
                    "description": "Repository is missing a README file",
                    "severity": "medium",
                }
            )

        # Check for .gitignore
        if not (self.repo_path / ".gitignore").exists():
            analysis["issues_found"].append(
                {
                    "issue_type": "missing_gitignore",
                    "file_path": ".",
                    "description": "Repository is missing a .gitignore file",
                    "severity": "low",
                }
            )

        # Check for very large files that might need LFS
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                file_path = Path(root) / file
                try:
                    if file_path.stat().st_size > 100 * 1024 * 1024:  # >100MB
                        analysis["optimizations"].append(
                            f"Consider Git LFS for: {file_path.relative_to(self.repo_path)}"
                        )
                except (OSError, PermissionError):
                    continue


def main():
    parser = argparse.ArgumentParser(description="GITWiz Simple - Basic Repository Management")
    parser.add_argument("command", choices=["status", "analyze", "memory"], help="Command to execute")
    parser.add_argument("--detailed", action="store_true", help="Show detailed output")
    parser.add_argument("--repo", default=None, help="Repository path (default: current directory)")

    args = parser.parse_args()

    gitwiz = GITWizSimple(args.repo)

    if args.command == "status":
        status = gitwiz.get_repo_status()
        if args.detailed:
            print(json.dumps(status, indent=2))
        else:
            print(f"Repository: {status['repo_path']}")
            print(f"Git repo: {status['git_status'].get('is_git_repo', False)}")
            if status["git_status"].get("is_git_repo"):
                print(f"Current branch: {status['git_status'].get('current_branch', 'unknown')}")
                print(f"Total changes: {status['git_status'].get('total_changes', 0)}")
            print(f"Total files: {status['file_stats']['total_files']}")
            print(f"Total size: {status['file_stats']['total_size'] / (1024 * 1024):.1f} MB")
            print(f"Stored issues: {len(status['issues'])}")

    elif args.command == "analyze":
        analysis = gitwiz.analyze_repository()
        if args.detailed:
            print(json.dumps(analysis, indent=2))
        else:
            print(f"Analysis completed at {analysis['timestamp']}")
            print(f"Issues found: {len(analysis['issues_found'])}")
            print(f"Optimizations suggested: {len(analysis['optimizations'])}")
            print(f"Archives analyzed: {len(analysis['archive_analysis'])}")

            if analysis["issues_found"]:
                print("\nTop Issues:")
                for issue in analysis["issues_found"][:5]:
                    print(f"  - {issue['issue_type']}: {issue['description']}")

            if analysis["optimizations"]:
                print("\nOptimizations:")
                for opt in analysis["optimizations"][:5]:
                    print(f"  - {opt}")

    elif args.command == "memory":
        # Show memory database stats
        issues = gitwiz._get_stored_issues()
        print(f"Stored issues: {len(issues)}")
        if issues:
            print("\nRecent issues:")
            for issue in issues[:10]:
                print(f"  - {issue['issue_type']}: {issue['file_path']} (fixes: {issue['fix_count']})")


if __name__ == "__main__":
    main()
