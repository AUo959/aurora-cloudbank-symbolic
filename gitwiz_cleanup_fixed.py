#!/usr/bin/env python3
"""
GITWiz Repository Cleanup & Health Maintenance
Aurora CloudBank Symbolic Repository

This script performs comprehensive repository cleanup and health maintenance
using GITWiz intelligence and automation.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import shutil


class GITWizCleanup:
    """Repository cleanup and health maintenance tool."""

    def __init__(self, repo_path="/workspaces/aurora-cloudbank-symbolic"):
        """Initialize the cleanup tool."""
        self.repo_path = Path(repo_path)
        self.stats = {
            "files_removed": 0,
            "space_freed": 0,
            "branches_cleaned": 0,
            "actions_taken": []
        }

    def log_action(self, action, details=""):
        """Log cleanup actions for reporting."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_log = f"[{timestamp}] {action}"
        if details:
            action_log += f": {details}"
        self.stats["actions_taken"].append(action_log)
        print(f"🔧 {action_log}")

    def get_repo_size(self):
        """Get repository size in bytes."""
        try:
            result = subprocess.run(
                ["du", "-sb", str(self.repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.split()[0])
        except (subprocess.CalledProcessError, ValueError, IndexError):
            return 0

    def clean_python_cache(self):
        """Remove Python cache files and directories."""
        print("🧹 Cleaning Python cache files...")
        cache_files_removed = 0
        cache_dirs_removed = 0

        # Remove .pyc files
        for pyc_file in self.repo_path.rglob("*.pyc"):
            try:
                pyc_file.unlink()
                cache_files_removed += 1
            except (OSError, PermissionError):
                pass

        # Remove __pycache__ directories
        for cache_dir in self.repo_path.rglob("__pycache__"):
            if cache_dir.is_dir():
                try:
                    shutil.rmtree(cache_dir)
                    cache_dirs_removed += 1
                except (OSError, PermissionError):
                    pass

        self.stats["files_removed"] += cache_files_removed
        self.log_action(
            "Python Cache Cleanup",
            f"Removed {cache_files_removed} .pyc files and "
            f"{cache_dirs_removed} __pycache__ dirs"
        )

    def analyze_zip_files(self):
        """Analyze ZIP files in the repository."""
        print("📦 Analyzing ZIP files...")
        zip_files = list(self.repo_path.glob("*.zip"))
        total_size = 0
        zip_analysis = []

        for zip_file in zip_files:
            size = zip_file.stat().st_size
            total_size += size
            zip_analysis.append({
                "name": zip_file.name,
                "size": size,
                "size_mb": round(size / (1024 * 1024), 1)
            })

        # Sort by size descending
        zip_analysis.sort(key=lambda x: x["size"], reverse=True)

        self.log_action(
            "ZIP File Analysis",
            f"Found {len(zip_files)} ZIP files totaling "
            f"{round(total_size / (1024 * 1024), 1)}MB"
        )

        print("📊 Largest ZIP files:")
        for zip_info in zip_analysis[:5]:
            print(f"   {zip_info['size_mb']}MB - {zip_info['name']}")

        return zip_analysis

    def analyze_branches(self):
        """Analyze git branches."""
        print("🌿 Analyzing git branches...")
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                check=True
            )
            branches = result.stdout.strip().split('\n')
            branch_counts = {
                "codex": 0,
                "dependabot": 0,
                "alert-autofix": 0,
                "backup": 0,
                "other": 0
            }

            for branch in branches:
                branch = branch.strip()
                if 'codex' in branch:
                    branch_counts["codex"] += 1
                elif 'dependabot' in branch:
                    branch_counts["dependabot"] += 1
                elif 'alert-autofix' in branch:
                    branch_counts["alert-autofix"] += 1
                elif 'backup' in branch:
                    branch_counts["backup"] += 1
                else:
                    branch_counts["other"] += 1

            total_branches = len(branches)
            self.log_action(
                "Branch Analysis",
                f"Found {total_branches} total branches"
            )

            for branch_type, count in branch_counts.items():
                if count > 0:
                    print(f"   📋 {branch_type}: {count} branches")

            return branch_counts

        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_action("Branch Analysis", "Failed to analyze branches")
            return {}

    def update_gitignore(self):
        """Update .gitignore with common bloat patterns."""
        print("📝 Updating .gitignore...")
        gitignore_path = self.repo_path / ".gitignore"

        new_patterns = [
            "# Python cache and build artifacts",
            "*.pyc",
            "__pycache__/",
            "*.so",
            "*.dylib",
            "*.dll",
            "*.egg-info/",
            "build/",
            "dist/",
            "",
            "# IDE and editor files",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            "",
            "# OS generated files",
            ".DS_Store",
            ".DS_Store?",
            "._*",
            ".Spotlight-V100",
            ".Trashes",
            "ehthumbs.db",
            "Thumbs.db",
            "",
            "# Temporary files",
            "*.tmp",
            "*.temp",
            "*.log",
            "tmp/",
            "temp/",
            "",
            "# Large archives (with exceptions for deployment)",
            "*.zip",
            "!deploy*.zip",
            "!*_deploy*.zip",
            "!essential_*.zip",
        ]

        try:
            existing_content = ""
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

            patterns_to_add = []
            for pattern in new_patterns:
                if pattern and pattern not in existing_content:
                    patterns_to_add.append(pattern)

            if patterns_to_add:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write("\n# GITWiz Auto-generated patterns\n")
                    for pattern in patterns_to_add:
                        f.write(f"{pattern}\n")

                self.log_action(
                    "GitIgnore Update",
                    f"Added {len([p for p in patterns_to_add if p and not p.startswith('#')])} new ignore patterns"
                )
            else:
                self.log_action(
                    "GitIgnore Update",
                    "No new patterns needed"
                )

        except (OSError, PermissionError) as e:
            self.log_action("GitIgnore Update", f"Failed: {e}")

    def run_analysis_only(self):
        """Run analysis without making changes."""
        print("🔍 GITWiz Repository Analysis Mode")
        print("=" * 50)

        initial_size = self.get_repo_size()
        if initial_size > 0:
            print(f"📏 Repository size: {round(initial_size / (1024*1024), 1)}MB")

        self.analyze_zip_files()
        self.analyze_branches()

        print("\n✅ Analysis complete - no changes made")
        return self.stats

    def run_cleanup(self, include_gitignore=True):
        """Run full cleanup process."""
        print("🚀 GITWiz Repository Cleanup Starting")
        print("=" * 50)

        initial_size = self.get_repo_size()
        if initial_size > 0:
            print(f"📏 Initial repository size: {round(initial_size / (1024*1024), 1)}MB")

        # Perform cleanup operations
        self.clean_python_cache()
        self.analyze_zip_files()
        self.analyze_branches()

        if include_gitignore:
            self.update_gitignore()

        # Calculate space savings
        final_size = self.get_repo_size()
        if initial_size > 0 and final_size > 0:
            space_saved = initial_size - final_size
            self.stats["space_freed"] = space_saved
            print(f"\n💾 Space saved: {round(space_saved / (1024*1024), 1)}MB")
            print(f"📏 Final repository size: {round(final_size / (1024*1024), 1)}MB")

        print("\n✅ Cleanup complete!")
        return self.stats

    def generate_report(self):
        """Generate cleanup report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "repository": str(self.repo_path),
            "statistics": self.stats,
            "recommendations": [
                "Consider removing duplicate ZIP files",
                "Review and merge/close stale branches",
                "Set up automated cleanup workflows",
                "Monitor repository size regularly"
            ]
        }

        report_file = self.repo_path / "gitwiz_cleanup_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {report_file}")
        except (OSError, PermissionError):
            print("⚠️ Could not save report file")

        return report


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GITWiz Repository Cleanup Tool"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Run analysis only, don't make changes"
    )
    parser.add_argument(
        "--update-gitignore",
        action="store_true",
        help="Update .gitignore with cleanup patterns"
    )
    parser.add_argument(
        "--repo-path",
        default="/workspaces/aurora-cloudbank-symbolic",
        help="Path to repository"
    )

    args = parser.parse_args()

    cleanup_tool = GITWizCleanup(args.repo_path)

    try:
        if args.analyze_only:
            cleanup_tool.run_analysis_only()
        elif args.update_gitignore:
            cleanup_tool.update_gitignore()
        else:
            cleanup_tool.run_cleanup()

        cleanup_tool.generate_report()

    except KeyboardInterrupt:
        print("\n⚠️ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
