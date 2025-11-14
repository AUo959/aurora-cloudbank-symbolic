#!/usr/bin/env python3
"""
Aurora CloudBank - Automated Branch Cleanup System
Intelligently identifies and manages stale branches based on configurable rules.
"""

import logging

logger = logging.getLogger(__name__)

import argparse
import datetime
import re
import subprocess
from pathlib import Path
from typing import Dict
from typing import List



class BranchCleanupManager:

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.config = {
            "stale_days": 30,
            "force_delete_patterns": [
                r"^origin/alert-autofix-\d+$",  # Old security fixes
                r"^origin/.*-backup-.*$",  # Backup branches
            ],
            "review_patterns": [
                r"^origin/dependabot/.*$",  # Dependency updates
                r"^origin/codex/.*$",  # Feature branches
            ],
            "protected_branches": [
                "origin/main",
                "origin/master",
                "origin/develop",
                "origin/HEAD",
            ],
            "dry_run": True,
        }

    def get_branch_info(self) -> List[Dict]:
        """Get detailed information about all remote branches."""
        try:
            # Get branch info with dates
            cmd = [
                "git",
                "for-each-re",
                "--format=%(refname:short)|%(committerdate:iso8601)|%(authorname)|%(subject)",
                "refs/remotes/origin/",
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            branches = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|", 3)
                if len(parts) >= 3:
                    branch_name = parts[0]
                    commit_date = parts[1]
                    author = parts[2] if len(parts) > 2 else "Unknown"
                    subject = parts[3] if len(parts) > 3 else "No subject"

                    # Calculate days since last commit
                    try:
                        commit_datetime = datetime.datetime.fromisoformat(
                            commit_date.replace("Z", "+00:00")
                        )
                        days_old = (
                            datetime.datetime.now(datetime.timezone.utc)
                            - commit_datetime
                        ).days
                    except BaseException:
                        days_old = 0

                    branches.append(
                        {
                            "name": branch_name,
                            "commit_date": commit_date,
                            "author": author,
                            "subject": subject,
                            "days_old": days_old,
                            "is_merged": self.is_branch_merged(branch_name),
                        }
                    )

            return branches
        except (OSError, ValueError, RuntimeError) as e:
            print("Error getting branch info: {e}")
            return []

    def is_branch_merged(self, branch_name: str) -> bool:
        """Check if a branch has been merged into main."""
        try:
            # Remove 'origin/' prefix for merge check
            branch_short = branch_name.replace("origin/", "")
            cmd = [
                "git",
                "merge-base",
                "--is-ancestor",
                "origin/{branch_short}",
                "origin/main",
            ]
            result = subprocess.run(
                cmd, capture_output=True, cwd=self.repo_path, shell=False, check=False
            )
            return result.returncode == 0
        except BaseException:
            return False

    def categorize_branches(self, branches: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize branches based on cleanup rules."""
        categories = {
            "protected": [],
            "force_delete": [],
            "review_needed": [],
            "stale_merged": [],
            "recent_active": [],
        }

        for branch in branches:
            name = branch["name"]

            # Protected branches
            if name in self.config["protected_branches"]:
                categories["protected"].append(branch)
                continue

            # Force delete patterns
            if any(
                re.match(pattern, name)
                for pattern in self.config["force_delete_patterns"]
            ):
                categories["force_delete"].append(branch)
                continue

            # Review patterns
            if any(
                re.match(pattern, name) for pattern in self.config["review_patterns"]
            ):
                categories["review_needed"].append(branch)
                continue

            # Stale and merged branches
            if branch["days_old"] > self.config["stale_days"] and branch["is_merged"]:
                categories["stale_merged"].append(branch)
                continue

            # Recent active branches
            categories["recent_active"].append(branch)

        return categories

    def generate_cleanup_report(self, categories: Dict[str, List[Dict]]) -> str:
        """Generate a detailed cleanup report."""
        report = []
        report.append("# Aurora CloudBank - Branch Cleanup Report")
        report.append("**Generated:** {datetime.datetime.now().isoformat()}")
        report.append("")

        total_branches = sum(len(branches) for branches in categories.values())
        report.append("**Total Branches Analyzed:** {total_branches}")
        report.append("")

        for category, branches in categories.items():
            if not branches:
                continue

            report.append(
                "## {category.replace('_', ' ').title()} ({len(branches)} branches)"
            )
            report.append("")

            for branch in branches:
                report.append("- **{branch['name']}**")
                report.append("  - Last commit: {branch['days_old']} days ago")
                report.append("  - Author: {branch['author']}")
                report.append("  - Subject: {branch['subject'][:80]}...")
                report.append("  - Merged: {'Yes' if branch['is_merged'] else 'No'}")
                report.append("")

        return "\n".join(report)

    def execute_cleanup(
        self, categories: Dict[str, List[Dict]], force: bool = False
    ) -> Dict[str, int]:
        """Execute the branch cleanup based on categories."""
        results = {"deleted": 0, "errors": 0, "skipped": 0}

        if self.config["dry_run"] and not force:
            print("🔍 DRY RUN MODE - No branches will be deleted")
            print("Use --execute to perform actual cleanup")
            return results

        # Delete force_delete branches
        for branch in categories["force_delete"]:
            if self.delete_branch(branch["name"]):
                results["deleted"] += 1
                logger.info("Deleted: {branch["name']}")
            else:
                results["errors"] += 1
                logger.error("Failed to delete: {branch["name']}")

        # Delete stale merged branches
        for branch in categories["stale_merged"]:
            if self.delete_branch(branch["name"]):
                results["deleted"] += 1
                logger.info("Deleted stale merged: {branch["name']}")
            else:
                results["errors"] += 1
                logger.error("Failed to delete: {branch["name']}")

        return results

    def delete_branch(self, branch_name: str) -> bool:
        """Delete a remote branch."""
        try:
            # Remove 'origin/' prefix for deletion
            branch_short = branch_name.replace("origin/", "")
            cmd = ["git", "push", "origin", "--delete", branch_short]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            return result.returncode == 0
        except (OSError, ValueError, RuntimeError) as e:
            print("Error deleting branch {branch_name}: {e}")
            return False

    def run_analysis(self, save_report: bool = True) -> Dict:
        """Run complete branch analysis and generate reports."""
        print("🔍 Analyzing repository branches...")

        branches = self.get_branch_info()
        if not branches:
            logger.error("No branches found or error occurred")
            return {}

        categories = self.categorize_branches(branches)

        # Generate report
        report = self.generate_cleanup_report(categories)

        if save_report:
            report_path = self.repo_path / "BRANCH_CLEANUP_REPORT.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print("📄 Report saved to: {report_path}")

        # Print summary
        print("\n📊 Branch Analysis Summary:")
        for category, branches in categories.items():
            print("  {category.replace('_', ' ').title()}: {len(branches)} branches")

        return {"branches": branches, "categories": categories, "report": report}


def main():
    parser = argparse.ArgumentParser(
        description="Aurora CloudBank Branch Cleanup Automation"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute cleanup (default: dry run)"
    )
    parser.add_argument(
        "--stale-days", type=int, default=30, help="Days to consider branch stale"
    )
    parser.add_argument(
        "--no-report", action="store_true", help="Skip saving report file"
    )

    args = parser.parse_args()

    manager = BranchCleanupManager()
    manager.config["dry_run"] = not args.execute
    manager.config["stale_days"] = args.stale_days

    # Run analysis
    results = manager.run_analysis(save_report=not args.no_report)

    if results:
        # Execute cleanup if requested
        if args.execute:
            cleanup_results = manager.execute_cleanup(results["categories"], force=True)
            print("\n🎯 Cleanup Results:")
            print("  Deleted: {cleanup_results['deleted']} branches")
            print("  Errors: {cleanup_results['errors']} branches")
            print("  Skipped: {cleanup_results['skipped']} branches")


if __name__ == "__main__":
    main()
