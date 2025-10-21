#!/usr/bin/env python3
from datetime import datetime
import argparse
import subprocess
import sys
"""
Aurora CloudBank - Automated Branch Management System
====================================================

This script provides intelligent branch cleanup automation with safety checks.
It analyzes branch patterns, merge status, and age to recommend cleanup actions.
"""

import argparse
import datetime
import re
import subprocess
import sys
from typing import Dict, List


class BranchManager:
    """Automated branch management and cleanup system."""

    def __init__(self, repo_path: str = "."):
        """Initialize branch manager.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path
        self.dry_run = True
        self.stale_days = 30
        self.patterns = {
            "stale": [
                r"^origin/codex/.*",
                r"^origin/dependabot/.*",
                r"^origin/alert-autofix-.*",
                r"^origin/.*-backup.*",
                r"^origin/backup-.*",
            ],
            "keep": [
                r"^origin/main$",
                r"^origin/HEAD$",
                r"^origin/master$",
                r"^origin/develop$",
                r"^origin/staging$",
                r"^origin/production$",
            ],
        }

    def get_branch_info(self) -> List[Dict]:
        """Get detailed branch information including dates and merge status.

        Returns:
            List of branch info dictionaries
        """
        try:
            # Get all remote branches with dates
        cmd = [
                "git",
                "for-each-re",
                "--format=%(refname:short)|%(committerdate:iso8601)|%(authorname)|%(subject)",
                "refs/remotes/origin/",
            ]
        result = subprocess.run(                cmd,
                capture_output=True,
        text=True,
                cwd=self.repo_path,
        shell=False,
                check=False,
            )


        if result.returncode != 0:
                print("Error getting branch info: %s", result.stderr)

        return []

            branches = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
        parts = line.split("|", 3)

        if len(parts) >= 4:
                    branch_name, date_str, author, subject = parts

                    # Parse date
                    try:
                        pass
        commit_date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        days_old = (datetime.datetime.now(datetime.timezone.utc) - commit_date).days
                    except ValueError:
                        pass
        days_old = 0

                    # Check if merged
                    is_merged = self.is_branch_merged(branch_name)


        branches.append(
                        {
                            "name": branch_name,
                            "date": date_str,
                            "days_old": days_old,
                            "author": author,
                            "subject": (subject[:50] + "..." if len(subject) > 50 else subject),
                            "is_merged": is_merged,
                            "category": self.categorize_branch(branch_name),
                            "action": self.recommend_action(branch_name, days_old, is_merged),
                        }
                    )


        return sorted(branches, key=lambda x: x["days_old"], reverse=True)


        except (OSError, ValueError, RuntimeError) as e:
            print("Error analyzing branches: %s", e)

        return []

    def is_branch_merged(self, branch_name: str) -> bool:
        """Check if a branch has been merged into main.

        Args:
            branch_name: Name of the branch to check

        Returns:
            True if branch is merged
        """
        try:
            # Check if branch is merged into main
        cmd = ["git", "merge-base", "--is-ancestor", branch_name, "origin/main"]
            result = subprocess.run(cmd, capture_output=True, cwd=self.repo_path, shell=False, check=False)

        return result.returncode == 0
        except (OSError, ValueError, RuntimeError):
            return False

    def categorize_branch(self, branch_name: str) -> str:
        """Categorize branch based on naming patterns.

        Args:
            branch_name: Name of the branch

        Returns:
            Category string
        """
        # Check keep patterns first
        for pattern in self.patterns["keep"]:
            if re.match(pattern, branch_name):
                return "protected"

        # Check stale patterns
        for pattern in self.patterns["stale"]:
            if re.match(pattern, branch_name):
                if "codex" in pattern:
                    return "codex-feature"
                elif "dependabot" in pattern:
                    return "dependency-update"
                elif "alert-autofix" in pattern:
                    return "security-fix"
                elif "backup" in pattern:
                    return "backup"

        return "other"

    def recommend_action(self, branch_name: str, days_old: int, is_merged: bool) -> str:
        """Recommend action for a branch.

        Args:
            branch_name: Name of the branch
            days_old: Age of branch in days
            is_merged: Whether branch is merged

        Returns:
            Recommended action
        """
        category = self.categorize_branch(branch_name)


        if category == "protected":
            return "keep"

    if is_merged and days_old > 7:
            return "delete"

    if category in ["codex-feature", "security-fix"] and days_old > 30:
            return "archive"

    if category == "dependency-update" and days_old > 14:
            return "review"

    if category == "backup" and days_old > 60:
            return "archive"

        if days_old > 90:
            return "review"

        return "keep"

    def execute_cleanup(self, branches: List[Dict], confirm: bool = False) -> Dict:
        """Execute branch cleanup actions.

        Args:
            branches: List of branch info dictionaries
            confirm: Whether to actually execute deletions

        Returns:
            Summary of actions taken
        """
        summary = {"deleted": [], "archived": [], "kept": [], "errors": []}

        for branch in branches:
            action = branch["action"]
        branch_name = branch["name"]

            if action == "delete" and branch["is_merged"]:
                if confirm and not self.dry_run:
                    try:
                        # Delete remote branch
                        cmd = [
                            "git",
                            "push",
                            "origin",
                            "--delete",
                            branch_name.replace("origin/", ""),
                        ]
        result = subprocess.run(
                            cmd,                        result = subprocess.run(
        text=True,
                            cwd=self.repo_path,
        shell=False,
                            check=False,
                        )


        if result.returncode == 0:
                            summary["deleted"].append(branch_name)

        else:
                            summary["errors"].append(f"Failed to delete {branch_name}: {result.stderr}")

        except (OSError, ValueError, RuntimeError) as e:
                        summary["errors"].append(f"Error deleting {branch_name}: {e}")

        else:
                    summary["deleted"].append(f"[DRY-RUN] {branch_name}")


        elif action == "archive":
                # Create tag for archive
                tag_name = f"archive/{branch_name.replace('origin/', '').replace('/', '-')}"
                if confirm and not self.dry_run:
                    try:
                        pass
        cmd = ["git", "tag", tag_name, branch_name]
                        subprocess.run(
                            cmd,
                            capture_output=True,
        cwd=self.repo_path,
                            shell=False,
        check=False,
                        )

        summary["archived"].append(f"{branch_name} -> {tag_name}")

        except (OSError, ValueError, RuntimeError) as e:
                        summary["errors"].append(f"Error archiving {branch_name}: {e}")

        else:
                    summary["archived"].append(f"[DRY-RUN] {branch_name} -> {tag_name}")


        else:
                summary["kept"].append(branch_name)


        return summary

    def generate_report(self, branches: List[Dict]) -> str:
        """Generate branch cleanup report.

        Args:
            branches: List of branch info dictionaries

        Returns:
            Formatted report string
        """
        report = []
        report.append("# Aurora CloudBank - Branch Management Report")

        report.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        report.append("")

        # Summary
        total = len(branches)
        by_action = {}
        by_category = {}

        for branch in branches:
            action = branch["action"]
        category = branch["category"]
            by_action[action] = by_action.get(action, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1

        report.append("## Summary")

        report.append("")

        report.append(f"**Total Branches:** {total}")

        report.append("")

        report.append("### By Action:")

        for action, count in sorted(by_action.items()):
            report.append(f"- **{action.title()}**: {count} branches")


        report.append("")

        report.append("### By Category:")

        for category, count in sorted(by_category.items()):
            report.append(f"- **{category.replace('-', ' ').title()}**: {count} branches")


        report.append("")

        report.append("## Branch Details")

        report.append("")

        # Group by action
        for action in ["delete", "archive", "review", "keep"]:
            action_branches = [b for b in branches if b["action"] == action]
            if not action_branches:
                continue

            report.append(f"### {action.title()} ({len(action_branches)} branches)")

        report.append("")


        for branch in action_branches:
                merged_status = "✅ Merged" if branch["is_merged"] else "❌ Not merged"
                report.append(f"- **{branch['name']}**")

        report.append(f"  - Age: {branch['days_old']} days")

        report.append(f"  - Status: {merged_status}")

        report.append(f"  - Category: {branch['category']}")

        report.append(f"  - Last commit: {branch['subject']}")

        report.append("")


        return "\n".join(report)


def main():
    """Main function for branch management CLI."""
    parser = argparse.ArgumentParser(description="Aurora CloudBank Branch Management")
    parser.add_argument("--analyze", action="store_true", help="Analyze branches and generate report")
    parser.add_argument("--cleanup", action="store_true", help="Execute cleanup actions")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually execute deletions (not dry-run)",
    )
    parser.add_argument("--stale-days", type=int, default=30, help="Days to consider branch stale")
    parser.add_argument("--output", help="Output file for report")
        args = parser.parse_args()
        manager = BranchManager()
    manager.stale_days = args.stale_days
    manager.dry_run = not args.confirm

    if args.analyze or args.cleanup:
        print("🔍 Analyzing branches...")
        branches = manager.get_branch_info()


        if not branches:
            print("❌ No branches found or error occurred")

        return 1

        # Generate report
        report = manager.generate_report(branches)


        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)

        print("📄 Report saved to %s", args.output)

        else:
            print(report)


        if args.cleanup:
            print("\n🧹 Executing cleanup...")
        summary = manager.execute_cleanup(branches, args.confirm)


        print("\n✅ Cleanup Summary:")

        print("  - Deleted: %s branches", len(summary['deleted']))

        print("  - Archived: %s branches", len(summary['archived']))

        print("  - Kept: %s branches", len(summary['kept']))

        print("  - Errors: %s issues", len(summary['errors']))


        if summary["errors"]:
                print("\n❌ Errors:")

        for error in summary["errors"]:
                    print("  - %s", error)


        else:
        parser.print_help()

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
