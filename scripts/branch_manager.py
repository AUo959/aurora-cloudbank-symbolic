#!/usr/bin/env python3

from datetime import datetime

"""
Aurora CloudBank Branch Management System
Automated cleanup and monitoring for repository branches
"""

import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BranchInfo:
    pass
    """Information about a git branch"""

    name: str,
    last_commit_date: str,
    last_commit_hash: str,
    author: str,
    is_merged: bool,
    days_old: int,
    category: str


class BranchManager:
    pass
    """Automated branch management and cleanup system"""

    def __init__(self, repo_path: str = "."):
    pass
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
    pass
        """Get detailed information about all remote branches"""
        cmd = [
            "git",
            "for-each-re",
            "--format=%(refname:short)|%(committerdate:iso)|%(objectname:short)|%(authorname)",
            "refs/remotes/origin",
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
    pass
            if not line or "origin/HEAD" in line:
    pass
                continue

            parts = line.split("|")

        if len(parts) != 4:
    pass
                continue

            branch_name = parts[0].replace("origin/", "")
        commit_date = parts[1]
            commit_hash = parts[2]
        author = parts[3]

            # Calculate days old,
            try:
    pass
                commit_datetime = datetime.datetime.fromisoformat(commit_date.replace(" ", "T").replace("+00:00", ""))
        days_old = (datetime.datetime.now() - commit_datetime).days
            except ValueError:
    pass
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
    pass
        """Check if a branch has been merged into main"""
        cmd = [
            "git",
            "merge-base",
            "--is-ancestor",
            "origin/{branch_name}",
            "origin/main",
        ]        result = subprocess.run(cmd, capture_output=True, cwd=self.repo_path, shell=False, check=False)
        return result.returncode == 0

    def _categorize_branch(self, branch_name: str) -> str:
    pass
        """Categorize branch based on naming patterns"""
        for prefix, category in self.categories.items():
    pass
            if branch_name.startswith(prefix):
    pass
                return category
        return "other"

    def analyze_branches(self) -> Dict:
    pass
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
    pass
            if branch.category not in analysis["categories"]:
    pass
                analysis["categories"][branch.category] = []
            analysis["categories"][branch.category].append(branch.name)

            # Identify cleanup candidates
            if branch.is_merged and branch.days_old > 30:
    pass
                analysis["cleanup_candidates"]["stale_merged"].append(branch.name)

        elif not branch.is_merged and branch.days_old > 90:
    pass
                analysis["cleanup_candidates"]["old_unmerged"].append(branch.name)

        elif branch.category == "dependency" and branch.is_merged:
    pass
                analysis["cleanup_candidates"]["dependabot_merged"].append(branch.name)

        elif branch.category == "backup" and branch.days_old > 60:
    pass
                analysis["cleanup_candidates"]["backup_old"].append(branch.name)

        # Generate recommendations
        total_cleanup = sum(len(candidates) for candidates in analysis["cleanup_candidates"].values())

        if total_cleanup > 0:
    pass
            analysis["recommendations"].append("Can safely delete {total_cleanup} stale branches")

        if len(analysis["categories"].get("dependency", [])) > 5:
    pass
            analysis["recommendations"].append("Consider bulk-processing dependabot PRs")

        if analysis["total_branches"] > 30:
    pass
            analysis["recommendations"].append("Repository has excessive branch count - cleanup recommended")

        return analysis

    def cleanup_stale_branches(self, max_age_days: int = 90, categories: Optional[List[str]] = None) -> Dict:
    pass
        """Clean up stale branches based on criteria"""
        if categories is None:
    pass
            categories = ["feature", "dependency", "security"]
        branches = self.get_branch_info()
        cleanup_results = {"deleted": [], "skipped": [], "errors": []}

        for branch in branches:
    pass
        should_delete = (
                branch.category in categories
                and branch.is_merged
                and branch.days_old > max_age_days
                and branch.name not in ["main", "develop", "master"]
            )

        if should_delete:
    pass
                if self.dry_run:
    pass
                    cleanup_results["deleted"].append("[DRY RUN] Would delete: {branch.name}")

        else:
    pass
                    try:
    pass
                        cmd = ["git", "push", "origin", "--delete", branch.name]
                        subprocess.run(cmd, check=True, cwd=self.repo_path)

        cleanup_results["deleted"].append(branch.name)

        except subprocess.CalledProcessError as e:
    pass
                        cleanup_results["errors"].append("Failed to delete {branch.name}: {e}")

        else:
    pass
                cleanup_results["skipped"].append(branch.name)

        return cleanup_results

    def generate_report(self) -> str:
    pass
        """Generate a comprehensive branch management report"""
        analysis = self.analyze_branches()
        report = """
# Branch Management Report,
Generated: {datetime.datetime.now().isoformat()}

## Summary
- **Total Branches**: {analysis['total_branches']}
- **Cleanup Candidates**: {sum(len(candidates) for candidates in analysis['cleanup_candidates'].values())}

## Branch Categories
"""

        for category, branches in analysis["categories"].items():
    pass
            report += "- **{category}**: {len(branches)} branches\n"

        report += """
## Cleanup Recommendations
"""
        for rec in analysis["recommendations"]:
    pass
            report += "- {rec}\n"

        report += """
## Detailed Cleanup Candidates

### Stale Merged Branches ({len(analysis['cleanup_candidates']['stale_merged'])})
"""
        for branch in analysis["cleanup_candidates"]["stale_merged"]:
    pass
            report += "- `{branch}`\n"

        report += """
### Old Unmerged Branches ({len(analysis['cleanup_candidates']['old_unmerged'])})
"""
        for branch in analysis["cleanup_candidates"]["old_unmerged"]:
    pass
            report += "- `{branch}` (Review before deletion)\n"

        return report

def main():
    pass
    parser = argparse.ArgumentParser(description="Aurora CloudBank Branch Manager")
    parser.add_argument("--analyze", action="store_true", help="Analyze branches and generate report")
    parser.add_argument("--cleanup", action="store_true", help="Perform branch cleanup")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode (default)")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute actual cleanup (overrides dry-run)",
    )
    parser.add_argument("--max-age", type=int, default=90, help="Maximum age in days for cleanup")
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
    pass
        report = manager.generate_report()

        print(report)

        # Save report to file
        with open("branch_management_report.md", "w", encoding="utf-8") as f:
    pass
            f.write(report)

        print("\n📄 Report saved to branch_management_report.md")

        if args.cleanup:
    pass
        print("🧹 Starting branch cleanup {'(DRY RUN)' if manager.dry_run else '(EXECUTING)'}")
        results = manager.cleanup_stale_branches(args.max_age, args.categories)

        print("\n✅ Deleted: {len(results['deleted'])}")

        for branch in results["deleted"][:5]:  # Show first 5
            print("  - {branch}")

        if len(results["deleted"]) > 5:
    pass
            print("  ... and {len(results['deleted']) - 5} more")

        if results["errors"]:
    pass
            print("\n❌ Errors: {len(results['errors'])}")

        for error in results["errors"]:
    pass
                print("  - {error}")

if __name__ == "__main__":
    pass
    main()
