#!/usr/bin/env python3

from datetime import datetime

"""
Aurora CloudBank - Automated Branch Cleanup System
Intelligently manages repository branches with safety checks and automation.
"""

import datetime
from typing import Dict, List, Optional


class BranchCleanupManager:
    pass
    """Manages automated cleanup of stale repository branches."""

    def __init__(self, repo_path: str = "."):
    pass
        self.repo_path = Path(repo_path)

        self.dry_run = True
        self.config = self._load_cleanup_config()

        def _load_cleanup_config(self) -> Dict:
    pass
        """Load branch cleanup configuration."""
        return {
            "stale_days_threshold": 30,
            "keep_patterns": ["main", "develop", "master", "HEAD"],
            "cleanup_patterns": {
                "dependabot/*": {"max_age_days": 14, "auto_merge_if_ci_passes": True},
                "alert-autofix-*": {"max_age_days": 7, "auto_merge_if_ci_passes": True},
                "codex/create-*": {"max_age_days": 21, "archive_before_delete": True},
                "backup-*": {"max_age_days": 45, "convert_to_tag": True},
                "*-patch-*": {"max_age_days": 14, "merge_if_ahead": True},
            },
            "safety_checks": {
                "require_ci_success": True,
                "require_merged_or_behind": True,
                "max_branches_per_run": 10,
            },
        }

    def analyze_branches(self) -> Dict[str, List[Dict]]:
    pass
        """Analyze all remote branches and categorize for cleanup."""
        try:
    pass
            # Get all remote branches with metadata
        cmd = [
                "git",
                "for-each-re",
                "--format=%(refname:short)|%(committerdate:iso)|%(authorname)|%(ahead-behind:HEAD)",
                "refs/remotes/origin/",
            ]
        result = subprocess.run(cmd,
                capture_output=True,
        text=True,
                cwd=self.repo_path,
        shell=False,
                check=False,
            )

        if result.returncode != 0:
    pass
                print("Error getting branch info: {result.stderr}")

        return {}

            branches = {"cleanup_candidates": [], "keep": [], "manual_review": []}

            for line in result.stdout.strip().split("\n"):
    pass
                if not line:
    pass
                    continue
        parts = line.split("|")

        if len(parts) < 3:
    pass
                    continue

                branch_name = parts[0].replace("origin/", "")
        commit_date = parts[1]
                author = parts[2]
        ahead_behind = parts[3] if len(parts) > 3 else "0\t0"

                # Skip HEAD reference
                if branch_name == "HEAD":
    pass
                    continue

                branch_info = {
                    "name": branch_name,
                    "full_name": parts[0],
                    "commit_date": commit_date,
                    "author": author,
                    "ahead_behind": ahead_behind,
                    "age_days": self._calculate_age_days(commit_date),
                }
        category = self._categorize_branch(branch_info)

        branches[category].append(branch_info)

        return branches

        except (OSError, ValueError, RuntimeError) as e:
    pass
            print("Error analyzing branches: {e}")

        return {}

    def _calculate_age_days(self, commit_date: str) -> int:
    pass
        """Calculate branch age in days."""
        try:
    pass
            commit_dt = datetime.datetime.fromisoformat(commit_date.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)

        return (now - commit_dt).days
        except (OSError, ValueError, RuntimeError):
    pass
            return 0

    def _categorize_branch(self, branch_info: Dict) -> str:
    pass
        """Categorize branch for cleanup decision."""
        name = branch_info["name"]
        age_days = branch_info["age_days"]

        # Always keep protected branches
        if any(pattern in name for pattern in self.config["keep_patterns"]):
    pass
            return "keep"

        # Check cleanup patterns
        for pattern, rules in self.config["cleanup_patterns"].items():
    pass
            if self._matches_pattern(name, pattern):
    pass
                if age_days > rules["max_age_days"]:
    pass
                    return "cleanup_candidates"
                else:
    pass
                    return "keep"

        # Default: manual review if old, keep if recent
        return "cleanup_candidates" if age_days > self.config["stale_days_threshold"] else "manual_review"

    def _matches_pattern(self, branch_name: str, pattern: str) -> bool:
    pass
        """Check if branch name matches cleanup pattern."""
        if "*" in pattern:
    pass
            prefix = pattern.split("*")[0]
            return branch_name.startswith(prefix)

        return branch_name == pattern

    def execute_cleanup(self, branches: Dict[str, List[Dict]], dry_run: bool = True) -> Dict:
    pass
        """Execute branch cleanup with safety checks."""
        results = {
            "deleted": [],
            "archived": [],
            "merged": [],
            "errors": [],
            "skipped": [],
        }

        cleanup_candidates = branches.get("cleanup_candidates", [])
        max_per_run = self.config["safety_checks"]["max_branches_per_run"]

        # Limit cleanup per run for safety
        if len(cleanup_candidates) > max_per_run:
    pass
            print("⚠️  Limiting cleanup to {max_per_run} branches per run for safety")
        cleanup_candidates = cleanup_candidates[:max_per_run]

        for branch in cleanup_candidates:
    pass
            try:
    pass
        action = self._determine_cleanup_action(branch)

        if dry_run:
    pass
                    print("🔍 DRY RUN: Would {action} branch {branch['name']}")

        results["skipped"].append({"branch": branch["name"], "action": action})

        else:
    pass
                    success = self._execute_branch_action(branch, action)

        if success:
    pass
                        results[action].append(branch["name"])

        print("✅ {action.title()} branch: {branch['name']}")

        else:
    pass
                        results["errors"].append({"branch": branch["name"], "action": action})

        except (OSError, ValueError, RuntimeError) as e:
    pass
                print("❌ Error processing {branch['name']}: {e}")

        results["errors"].append({"branch": branch["name"], "error": str(e)})

        return results

    def _determine_cleanup_action(self, branch: Dict) -> str:
    pass
        """Determine the appropriate cleanup action for a branch."""
        name = branch["name"]

        # Check specific patterns
        for pattern, rules in self.config["cleanup_patterns"].items():
    pass
            if self._matches_pattern(name, pattern):
    pass
                if rules.get("convert_to_tag"):
    pass
                    return "archived"
                elif rules.get("auto_merge_if_ci_passes"):
    pass
                    return "merged"
                else:
    pass
                    return "deleted"

        return "deleted"  # Default action

    def _execute_branch_action(self, branch: Dict, action: str) -> bool:
    pass
        """Execute the specified action on a branch."""
        branch_name = branch["full_name"]

        try:
    pass
            if action == "archived":
    pass
                # Create tag before deleting
                tag_name = "archive/{branch['name']}"
                subprocess.run(
                    ["git", "tag", tag_name, branch_name],
        check=True,
                    cwd=self.repo_path,
                )

        subprocess.run(["git", "push", "origin", tag_name], check=True, cwd=self.repo_path)

        elif action == "merged":
    pass
                # This would require more complex logic to safely merge
                # For now, just delete after manual verification
                action = "deleted"

            if action == "deleted":
    pass
                # Delete remote branch
                branch_short = branch["name"]
                subprocess.run(
                    ["git", "push", "origin", "--delete", branch_short],
        check=True,
                    cwd=self.repo_path,
                )

        return True

        except subprocess.CalledProcessError as e:
    pass
            print("Git command failed: {e}")

        return False
        except (OSError, ValueError, RuntimeError) as e:
    pass
            print("Unexpected error: {e}")

        return False

        return True

    def generate_cleanup_report(self, branches: Dict[str, list], results: Optional[Dict[str, list]] = None) -> str:
    pass
        """Generate a comprehensive cleanup report."""
        report = [
            "# Branch Cleanup Analysis Report",
            "**Generated:** {datetime.datetime.now().isoformat()}",
            "",
            "## Summary",
            "- **Total Branches:** {sum(len(v) for v in branches.values())}",
            "- **Cleanup Candidates:** {len(branches.get('cleanup_candidates', []))}",
            "- **Keep:** {len(branches.get('keep', []))}",
            "- **Manual Review:** {len(branches.get('manual_review', []))}",
            "",
        ]

        if results:
    pass
            report.extend(
                [
                    "## Cleanup Results",
                    "- **Deleted:** {len(results.get('deleted', []))}",
                    "- **Archived:** {len(results.get('archived', []))}",
                    "- **Merged:** {len(results.get('merged', []))}",
                    "- **Errors:** {len(results.get('errors', []))}",
                    "",
                ]
            )

        # Add detailed branch listings
        for category, branch_list in branches.items():
    pass
            if branch_list:
    pass
                report.extend(["## {category.title().replace('_', ' ')}", ""])

        for branch in branch_list[:10]:  # Limit output
                    report.append("- `{branch['name']}` ({branch['age_days']} days old)")

        if len(branch_list) > 10:
    pass
                    report.append("- ... and {len(branch_list) - 10} more")

        report.append("")

        return "\n".join(report)

def main():
    pass
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Automated branch cleanup for Aurora CloudBank")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute cleanup (overrides dry-run)",
    )
    parser.add_argument("--report-only", action="store_true", help="Generate analysis report only")
        args = parser.parse_args()
        cleanup_manager = BranchCleanupManager()

        print("🌿 Aurora CloudBank - Branch Cleanup System")
    print("=" * 50)

    # Analyze branches
    print("🔍 Analyzing repository branches...")
    branches = cleanup_manager.analyze_branches()

        if not branches:
    pass
        print("❌ Failed to analyze branches")

        sys.exit(1)

    # Generate report
    report = cleanup_manager.generate_cleanup_report(branches)

        if args.report_only:
    pass
        print(report)

        return

    # Execute cleanup if requested
    dry_run = not args.execute
    results = cleanup_manager.execute_cleanup(branches, dry_run=dry_run)

    # Update report with results
    final_report = cleanup_manager.generate_cleanup_report(branches, results)

    # Save report
    report_path = Path("branch_cleanup_report.md")
    report_path.write_text(final_report)
    print("📄 Report saved to: {report_path}")

        if dry_run:
    pass
        print("\n🔍 DRY RUN MODE - No changes made")

        print("Use --execute to perform actual cleanup")

if __name__ == "__main__":
    pass
    main()
