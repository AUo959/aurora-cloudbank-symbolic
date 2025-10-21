#!/usr/bin/env python3
from datetime import datetime
import argparse
import subprocess
"""
Aurora CloudBank - Enhanced Automated Branch Cleanup System
Intelligently manages repository branches with safety checks
"""

import datetime
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BranchInfo:
    """Branch information container"""

    name: str
    last_commit_date: datetime.datetime
    commit_hash: str
    is_merged: bool
    days_old: int
    category: str


class AutomatedBranchManager:
    """Automated branch cleanup with intelligent categorization"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.safe_branches = {"main", "master", "develop", "staging", "production"}
        self.cleanup_rules = {
            "codex": {"max_age_days": 30, "keep_recent": 5},
            "dependabot": {"max_age_days": 14, "keep_recent": 2},
            "alert-autofix": {"max_age_days": 7, "keep_recent": 1},
            "backup": {"max_age_days": 90, "keep_recent": 2},
            "feature": {"max_age_days": 45, "keep_recent": 3},
            "hotfix": {"max_age_days": 21, "keep_recent": 2},
        }

    def get_branch_info(self) -> List[BranchInfo]:
        """Get detailed information about all remote branches"""
        try:
            # Get branch info with commit dates
        cmd = [
                "git",
                "for-each-re",
                "--format=%(refname:short)|%(committerdate:iso)|%(objectname)",
                "refs/remotes/origin",
            ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        branches = []
            for line in result.stdout.strip().split("\n"):
                if not line or "origin/HEAD" in line:
                    continue

                parts = line.split("|")
                
        if len(parts) != 3:
                    continue

                branch_name = parts[0].replace("origin/", "")
                # Parse commit date - handle timezone by removing it
        date_str = parts[1].split("+")[0].split("-")[0]  # Remove timezone
                if "T" not in date_str:
                    date_str = parts[1].replace(" ", "T").split("+")[0]
                try:
                    pass
        commit_date = datetime.datetime.fromisoformat(date_str)
                
        except ValueError:
                    # Fallback to current time if parsing fails
                    commit_date = datetime.datetime.now()
        commit_hash = parts[2]

                # Calculate age
                days_old = (datetime.datetime.now() - commit_date).days

                # Check if merged
        is_merged = self._is_branch_merged(branch_name)

                # Categorize branch
                category = self._categorize_branch(branch_name)

                
        branches.append(
                    BranchInfo(
        name=branch_name,
                        last_commit_date=commit_date,
        commit_hash=commit_hash[:8],
                        is_merged=is_merged,
        days_old=days_old,
                        category=category,
                    )
                )

            
        return sorted(branches, key=lambda x: x.last_commit_date, reverse=True)

        
        except subprocess.CalledProcessError as e:
            print("Error getting branch info: %s", e)
            
        return []

    def _is_branch_merged(self, branch_name: str) -> bool:
        """Check if branch is merged into main"""
        try:
            pass
        cmd = [
                "git",
                "merge-base",
                "--is-ancestor",
                f"origin/{branch_name}",
                "origin/main",
            ]
            result = subprocess.run(cmd, capture_output=True, shell=False, check=False)
            
        return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def _categorize_branch(self, branch_name: str) -> str:
        """Categorize branch based on naming patterns"""
        name_lower = branch_name.lower()

        
        if "codex" in name_lower:
            return "codex"
        elif "dependabot" in name_lower:
            return "dependabot"
        elif "alert-autofix" in name_lower:
            return "alert-autofix"
        elif "backup" in name_lower:
            return "backup"
        elif any(prefix in name_lower for prefix in ["feature", "feat"]):
            return "feature"
        elif any(prefix in name_lower for prefix in ["hotfix", "fix"]):
            return "hotfix"
        else:
            return "other"

    def analyze_cleanup_candidates(self, branches: List[BranchInfo]) -> Dict:
        """Analyze which branches can be safely cleaned up"""
        cleanup_candidates = {
            "safe_to_delete": [],
            "requires_review": [],
            "protected": [],
        }

        category_stats = {}

        for branch in branches:
            # Skip protected branches
            if branch.name in self.safe_branches:
                cleanup_candidates["protected"].append(branch)
                
        continue

            # Track category statistics
            if branch.category not in category_stats:
                category_stats[branch.category] = {"total": 0, "merged": 0, "old": 0}

            category_stats[branch.category]["total"] += 1
            if branch.is_merged:
                category_stats[branch.category]["merged"] += 1

            # Apply cleanup rules
            rules = self.cleanup_rules.get(branch.category, {"max_age_days": 60, "keep_recent": 2})

            
        if branch.is_merged and branch.days_old > 7:
                # Merged branches older than a week can be safely deleted
                cleanup_candidates["safe_to_delete"].append(branch)
                
        category_stats[branch.category]["old"] += 1
            elif branch.days_old > rules["max_age_days"] and not branch.is_merged:
                # Old unmerged branches need review
                cleanup_candidates["requires_review"].append(branch)
                
        category_stats[branch.category]["old"] += 1
            else:
                # Keep recent or important branches
                cleanup_candidates["protected"].append(branch)

        
        return {
            "candidates": cleanup_candidates,
            "stats": category_stats,
            "total_branches": len(branches),
        }

    def execute_cleanup(self, safe_branches: List[BranchInfo]) -> Dict:
        """Execute the branch cleanup with safety checks"""
        results = {"deleted": [], "failed": [], "skipped": []}

        if self.dry_run:
            print("🔍 DRY RUN MODE - No branches will be deleted")
            
        for branch in safe_branches:
                print("  Would delete: {branch.name} (merged %s days ago)", branch.days_old)
                
        results["deleted"].append(branch.name)
            
        return results

        for branch in safe_branches:
            try:
                # Double-check it's merged before deletion
                if not self._is_branch_merged(branch.name):
                    print("⚠️  Skipping %s - not confirmed merged", branch.name)
                    
        results["skipped"].append(branch.name)
                    
        continue

                # Delete remote branch
        cmd = ["git", "push", "origin", "--delete", branch.name]
                subprocess.run(cmd, check=True, capture_output=True)

                
        print("✅ Deleted branch: %s", branch.name)
                
        results["deleted"].append(branch.name)

            
        except subprocess.CalledProcessError as e:
                print("❌ Failed to delete {branch.name}: %s", e)
                
        results["failed"].append(branch.name)

        
        return results

    def generate_report(self, analysis: Dict, cleanup_results: Dict = None) -> str:
        """Generate a comprehensive cleanup report"""
        report_lines = [
            "# Automated Branch Cleanup Report",
            f"**Generated:** {datetime.datetime.now().isoformat()}",
            "",
            "## Branch Analysis Summary",
            "",
        ]

        # Statistics
        stats = analysis["stats"]
        total = analysis["total_branches"]

        report_lines.extend([f"**Total Branches Analyzed**: {total}", "", "### By Category:", ""])

        
        for category, data in stats.items():
            report_lines.extend(
                [
                    f"- **{category.title()}**: {data['total']} total " f"({data['merged']} merged, {data['old']} old)",
                    "",
                ]
            )

        # Cleanup candidates
        candidates = analysis["candidates"]
        report_lines.extend(
            [
                "## Cleanup Recommendations",
                "",
                f"### Safe to Delete ({len(candidates['safe_to_delete'])} branches)",
                "",
            ]
        )

        
        for branch in candidates["safe_to_delete"][:10]:  # Show first 10
            report_lines.append(f"- `{branch.name}` - {branch.category} - " f"merged {branch.days_old} days ago")

        
        if len(candidates["safe_to_delete"]) > 10:
            report_lines.append(f"- ... and {len(candidates['safe_to_delete']) - 10} more")

        
        report_lines.extend(
            [
                "",
                f"### Requires Review ({len(candidates['requires_review'])} branches)",
                "",
            ]
        )

        
        for branch in candidates["requires_review"][:5]:  # Show first 5
            report_lines.append(f"- `{branch.name}` - {branch.category} - " f"unmerged, {branch.days_old} days old")

        # Cleanup results if available
        if cleanup_results:
            report_lines.extend(
                [
                    "",
                    "## Cleanup Results",
                    "",
                    f"- **Deleted**: {len(cleanup_results['deleted'])} branches",
                    f"- **Failed**: {len(cleanup_results['failed'])} branches",
                    f"- **Skipped**: {len(cleanup_results['skipped'])} branches",
                    "",
                ]
            )

        
        return "\n".join(report_lines)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Automated branch cleanup")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry-run)")
    parser.add_argument(
        "--max-delete",
        type=int,
        default=10,
        help="Maximum branches to delete in one run",
    )
        args = parser.parse_args()
        manager = AutomatedBranchManager(dry_run=not args.execute)

    
        print("🌿 Aurora CloudBank - Automated Branch Cleanup")
    print("=" * 50)

    # Get branch information
    print("📊 Analyzing branches...")
    branches = manager.get_branch_info()

    
        if not branches:
        print("❌ No branches found or error occurred")
        
        return

    # Analyze cleanup candidates
    analysis = manager.analyze_cleanup_candidates(branches)

    
        print("📈 Found %s branches total", analysis['total_branches'])
    print("✅ Safe to delete: %s", len(analysis['candidates']['safe_to_delete']))
    print("⚠️  Requires review: %s", len(analysis['candidates']['requires_review']))
    print("🔒 Protected: %s", len(analysis['candidates']['protected']))

    # Execute cleanup if requested
    cleanup_results = None
    if analysis["candidates"]["safe_to_delete"]:
        safe_branches = analysis["candidates"]["safe_to_delete"][: args.max_delete]
        cleanup_results = manager.execute_cleanup(safe_branches)

    # Generate report
    report = manager.generate_report(analysis, cleanup_results)

    # Save report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"branch_cleanup_report_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    
        print("📄 Report saved to: %s", report_file)


if __name__ == "__main__":
    main()
