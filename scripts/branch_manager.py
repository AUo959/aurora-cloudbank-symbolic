#!/usr/bin/env python3
"""
Aurora CloudBank Branch Management System
Automated cleanup and monitoring for repository branches
"""

import argparse
import datetime
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BranchInfo:
    """Information about a git branch"""

    name: str
    last_commit_date: str
    last_commit_hash: str
    author: str
    is_merged: bool
    days_old: int
    category: str


class BranchManager:
    """Automated branch management and cleanup system"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.dry_run = True
        self.categories = {
            "codex/": "feature",
            "dependabot/": "dependency",
            "alert-autofix": "security",
            "backup": "backup",
            "feature/": "feature",
            "hotfix/": "hotfix",
        }

    def get_branch_info(self) -> List[BranchInfo]:
        """Get detailed information about all remote branches"""
        cmd = [
            "git",
            "for-each-re",
            "--format=%(refname:short)|%(committerdate:iso)|%(objectname:short)|%(authorname)",
            "refs/remotes/origin",
        ]

        _ = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            shell=False,
            check=False,
        )
        branches = []

        for line in result.stdout.strip().split("\n"):
            if not line or "origin/HEAD" in line:
                continue

            parts = line.split("|")
            if len(parts) != 4:
                continue

            branch_name = parts[0].replace("origin/", "")
            commit_date = parts[1]
            commit_hash = parts[2]
            author = parts[3]

            # Calculate days old
            try:
                commit_datetime = datetime.datetime.fromisoformat(
                    commit_date.replace(" ", "T").replace("+00:00", "")
                )
                days_old = (datetime.datetime.now() - commit_datetime).days
            except ValueError:
                # Fallback for problematic date formats
                days_old = 0

            # Check if merged
            is_merged = self._is_branch_merged(branch_name)

            # Categorize branch
            category = self._categorize_branch(branch_name)

            branch_info = BranchInfo(
                name=branch_name,
                last_commit_date=commit_date,
                last_commit_hash=commit_hash,
                author=author,
                is_merged=is_merged,
                days_old=days_old,
                category=category,
            )
            branches.append(branch_info)

        return branches

    def _is_branch_merged(self, branch_name: str) -> bool:
        """Check if a branch has been merged into main"""
        cmd = [
            "git",
            "merge-base",
            "--is-ancestor",
            f"origin/{branch_name}",
            "origin/main",
        ]
        _ = subprocess.run(
            cmd, capture_output=True, cwd=self.repo_path, shell=False, check=False
        )
        return result.returncode == 0

    def _categorize_branch(self, branch_name: str) -> str:
        """Categorize branch based on naming patterns"""
        for prefix, category in self.categories.items():
            if branch_name.startswith(prefix):
                return category
        return "other"

    def analyze_branches(self) -> Dict:
        """Analyze all branches and generate cleanup recommendations"""
        branches = self.get_branch_info()

        analysis = {
            "total_branches": len(branches),
            "categories": {},
            "cleanup_candidates": {
                "stale_merged": [],
                "old_unmerged": [],
                "dependabot_merged": [],
                "backup_old": [],
            },
            "recommendations": [],
        }

        # Categorize branches
        for branch in branches:
            if branch.category not in analysis["categories"]:
                analysis["categories"][branch.category] = []
            analysis["categories"][branch.category].append(branch.name)

            # Identify cleanup candidates
            if branch.is_merged and branch.days_old > 30:
                analysis["cleanup_candidates"]["stale_merged"].append(branch.name)
            elif not branch.is_merged and branch.days_old > 90:
                analysis["cleanup_candidates"]["old_unmerged"].append(branch.name)
            elif branch.category == "dependency" and branch.is_merged:
                analysis["cleanup_candidates"]["dependabot_merged"].append(branch.name)
            elif branch.category == "backup" and branch.days_old > 60:
                analysis["cleanup_candidates"]["backup_old"].append(branch.name)

        # Generate recommendations
        total_cleanup = sum(
            len(candidates) for candidates in analysis["cleanup_candidates"].values()
        )
        if total_cleanup > 0:
            analysis["recommendations"].append(
                f"Can safely delete {total_cleanup} stale branches"
            )

        if len(analysis["categories"].get("dependency", [])) > 5:
            analysis["recommendations"].append(
                "Consider bulk-processing dependabot PRs"
            )

        if analysis["total_branches"] > 30:
            analysis["recommendations"].append(
                "Repository has excessive branch count - cleanup recommended"
            )

        return analysis

    def cleanup_stale_branches(
        self, max_age_days: int = 90, categories: Optional[List[str]] = None
    ) -> Dict:
        """Clean up stale branches based on criteria"""
        if categories is None:
            categories = ["feature", "dependency", "security"]

        branches = self.get_branch_info()
        cleanup_results = {"deleted": [], "skipped": [], "errors": []}

        for branch in branches:
            should_delete = (
                branch.category in categories
                and branch.is_merged
                and branch.days_old > max_age_days
                and branch.name not in ["main", "develop", "master"]
            )

            if should_delete:
                if self.dry_run:
                    cleanup_results["deleted"].append(
                        f"[DRY RUN] Would delete: {branch.name}"
                    )
                else:
                    try:
                        cmd = ["git", "push", "origin", "--delete", branch.name]
                        subprocess.run(cmd, check=True, cwd=self.repo_path)
                        cleanup_results["deleted"].append(branch.name)
                    except subprocess.CalledProcessError as e:
                        cleanup_results["errors"].append(
                            f"Failed to delete {branch.name}: {e}"
                        )
            else:
                cleanup_results["skipped"].append(branch.name)

        return cleanup_results

    def generate_report(self) -> str:
        """Generate a comprehensive branch management report"""
        analysis = self.analyze_branches()

        report = """
# Branch Management Report
Generated: {datetime.datetime.now().isoformat()}

## Summary
- **Total Branches**: {analysis['total_branches']}
- **Cleanup Candidates**: {sum(len(candidates) for candidates in analysis['cleanup_candidates'].values())}

## Branch Categories
"""

        for category, branches in analysis["categories"].items():
            report += f"- **{category}**: {len(branches)} branches\n"

        report += """
## Cleanup Recommendations
"""
        for rec in analysis["recommendations"]:
            report += f"- {rec}\n"

        report += """
## Detailed Cleanup Candidates

### Stale Merged Branches ({len(analysis['cleanup_candidates']['stale_merged'])})
"""
        for branch in analysis["cleanup_candidates"]["stale_merged"]:
            report += f"- `{branch}`\n"

        report += """
### Old Unmerged Branches ({len(analysis['cleanup_candidates']['old_unmerged'])})
"""
        for branch in analysis["cleanup_candidates"]["old_unmerged"]:
            report += f"- `{branch}` (Review before deletion)\n"

        return report


def main():
    parser = argparse.ArgumentParser(description="Aurora CloudBank Branch Manager")
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze branches and generate report"
    )
    parser.add_argument("--cleanup", action="store_true", help="Perform branch cleanup")
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run mode (default)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute actual cleanup (overrides dry-run)",
    )
    parser.add_argument(
        "--max-age", type=int, default=90, help="Maximum age in days for cleanup"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["feature", "dependency", "security"],
        help="Branch categories to clean up",
    )

    args = parser.parse_args()

    manager = BranchManager()
    manager.dry_run = not args.execute

    if args.analyze:
        report = manager.generate_report()
        print(report)

        # Save report to file
        with open("branch_management_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n📄 Report saved to branch_management_report.md")

    if args.cleanup:
        print(
            f"🧹 Starting branch cleanup {'(DRY RUN)' if manager.dry_run else '(EXECUTING)'}"
        )
        results = manager.cleanup_stale_branches(args.max_age, args.categories)

        print(f"\n✅ Deleted: {len(results['deleted'])}")
        for branch in results["deleted"][:5]:  # Show first 5
            print(f"  - {branch}")
        if len(results["deleted"]) > 5:
            print(f"  ... and {len(results['deleted']) - 5} more")

        if results["errors"]:
            print(f"\n❌ Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")


if __name__ == "__main__":
    main()
