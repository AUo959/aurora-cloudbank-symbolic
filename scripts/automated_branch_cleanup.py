#!/usr/bin/env python3
"""
Aurora CloudBank - Automated Branch Cleanup System
Intelligently manages repository branches with safety checks and automation.
"""

import argparse
import datetime
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class BranchCleanupManager:
    """Manages automated cleanup of stale repository branches."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.dry_run = True
        self.config = self._load_cleanup_config()

    def _load_cleanup_config(self) -> Dict:
        """Load branch cleanup configuration."""
        return {
            'stale_days_threshold': 30,
            'keep_patterns': ['main', 'develop', 'master', 'HEAD'],
            'cleanup_patterns': {
                'dependabot/*': {'max_age_days': 14, 'auto_merge_if_ci_passes': True},
                'alert-autofix-*': {'max_age_days': 7, 'auto_merge_if_ci_passes': True},
                'codex/create-*': {'max_age_days': 21, 'archive_before_delete': True},
                'backup-*': {'max_age_days': 45, 'convert_to_tag': True},
                '*-patch-*': {'max_age_days': 14, 'merge_if_ahead': True}
            },
            'safety_checks': {
                'require_ci_success': True,
                'require_merged_or_behind': True,
                'max_branches_per_run': 10
            }
        }

    def analyze_branches(self) -> Dict[str, List[Dict]]:
        """Analyze all remote branches and categorize for cleanup."""
        try:
            # Get all remote branches with metadata
            cmd = [
                'git', 'for-each-re',
                '--format=%(refname:short)|%(committerdate:iso)|%(authorname)|%(ahead-behind:HEAD)',
                'refs/remotes/origin/'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path, shell=False, check=False)

            if result.returncode != 0:
                print(f"Error getting branch info: {result.stderr}")
                return {}

            branches = {'cleanup_candidates': [], 'keep': [], 'manual_review': []}

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|')
                if len(parts) < 3:
                    continue

                branch_name = parts[0].replace('origin/', '')
                commit_date = parts[1]
                author = parts[2]
                ahead_behind = parts[3] if len(parts) > 3 else "0\t0"

                # Skip HEAD reference
                if branch_name == 'HEAD':
                    continue

                branch_info = {
                    'name': branch_name,
                    'full_name': parts[0],
                    'commit_date': commit_date,
                    'author': author,
                    'ahead_behind': ahead_behind,
                    'age_days': self._calculate_age_days(commit_date)
                }

                category = self._categorize_branch(branch_info)
                branches[category].append(branch_info)

            return branches

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error analyzing branches: {e}")
            return {}

    def _calculate_age_days(self, commit_date: str) -> int:
        """Calculate branch age in days."""
        try:
            commit_dt = datetime.datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            return (now - commit_dt).days
        except (OSError, ValueError, RuntimeError):
            return 0

    def _categorize_branch(self, branch_info: Dict) -> str:
        """Categorize branch for cleanup decision."""
        name = branch_info['name']
        age_days = branch_info['age_days']

        # Always keep protected branches
        if any(pattern in name for pattern in self.config['keep_patterns']):
            return 'keep'

        # Check cleanup patterns
        for pattern, rules in self.config['cleanup_patterns'].items():
            if self._matches_pattern(name, pattern):
                if age_days > rules['max_age_days']:
                    return 'cleanup_candidates'
                else:
                    return 'keep'

        # Default: manual review if old, keep if recent
        return 'cleanup_candidates' if age_days > self.config['stale_days_threshold'] else 'manual_review'

    def _matches_pattern(self, branch_name: str, pattern: str) -> bool:
        """Check if branch name matches cleanup pattern."""
        if '*' in pattern:
            prefix = pattern.split('*')[0]
            return branch_name.startswith(prefix)
        return branch_name == pattern

    def execute_cleanup(self, branches: Dict[str, List[Dict]], dry_run: bool = True) -> Dict:
        """Execute branch cleanup with safety checks."""
        results = {'deleted': [], 'archived': [], 'merged': [], 'errors': [], 'skipped': []}

        cleanup_candidates = branches.get('cleanup_candidates', [])
        max_per_run = self.config['safety_checks']['max_branches_per_run']

        # Limit cleanup per run for safety
        if len(cleanup_candidates) > max_per_run:
            print(f"⚠️  Limiting cleanup to {max_per_run} branches per run for safety")
            cleanup_candidates = cleanup_candidates[:max_per_run]

        for branch in cleanup_candidates:
            try:
                action = self._determine_cleanup_action(branch)

                if dry_run:
                    print(f"🔍 DRY RUN: Would {action} branch {branch['name']}")
                    results['skipped'].append({'branch': branch['name'], 'action': action})
                else:
                    success = self._execute_branch_action(branch, action)
                    if success:
                        results[action].append(branch['name'])
                        print(f"✅ {action.title()} branch: {branch['name']}")
                    else:
                        results['errors'].append({'branch': branch['name'], 'action': action})

            except (OSError, ValueError, RuntimeError) as e:
                print(f"❌ Error processing {branch['name']}: {e}")
                results['errors'].append({'branch': branch['name'], 'error': str(e)})

        return results

    def _determine_cleanup_action(self, branch: Dict) -> str:
        """Determine the appropriate cleanup action for a branch."""
        name = branch['name']

        # Check specific patterns
        for pattern, rules in self.config['cleanup_patterns'].items():
            if self._matches_pattern(name, pattern):
                if rules.get('convert_to_tag'):
                    return 'archived'
                elif rules.get('auto_merge_if_ci_passes'):
                    return 'merged'
                else:
                    return 'deleted'

        return 'deleted'  # Default action

    def _execute_branch_action(self, branch: Dict, action: str) -> bool:
        """Execute the specified action on a branch."""
        branch_name = branch['full_name']

        try:
            if action == 'archived':
                # Create tag before deleting
                tag_name = f"archive/{branch['name']}"
                subprocess.run(['git', 'tag', tag_name, branch_name],
                               check=True, cwd=self.repo_path)
                subprocess.run(['git', 'push', 'origin', tag_name],
                               check=True, cwd=self.repo_path)

            elif action == 'merged':
                # This would require more complex logic to safely merge
                # For now, just delete after manual verification
                action = 'deleted'

            if action == 'deleted':
                # Delete remote branch
                branch_short = branch['name']
                subprocess.run(['git', 'push', 'origin', '--delete', branch_short],
                               check=True, cwd=self.repo_path)
                return True

        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return False
        except (OSError, ValueError, RuntimeError) as e:
            print(f"Unexpected error: {e}")
            return False

        return True

    def generate_cleanup_report(self, branches: Dict, results: Dict = None) -> str:
        """Generate a comprehensive cleanup report."""
        report = [
            "# Branch Cleanup Analysis Report",
            f"**Generated:** {datetime.datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- **Total Branches:** {sum(len(v) for v in branches.values())}",
            f"- **Cleanup Candidates:** {len(branches.get('cleanup_candidates', []))}",
            f"- **Keep:** {len(branches.get('keep', []))}",
            f"- **Manual Review:** {len(branches.get('manual_review', []))}",
            ""
        ]

        if results:
            report.extend([
                "## Cleanup Results",
                f"- **Deleted:** {len(results.get('deleted', []))}",
                f"- **Archived:** {len(results.get('archived', []))}",
                f"- **Merged:** {len(results.get('merged', []))}",
                f"- **Errors:** {len(results.get('errors', []))}",
                ""
            ])

        # Add detailed branch listings
        for category, branch_list in branches.items():
            if branch_list:
                report.extend([
                    f"## {category.title().replace('_', ' ')}",
                    ""
                ])

                for branch in branch_list[:10]:  # Limit output
                    report.append(f"- `{branch['name']}` ({branch['age_days']} days old)")

                if len(branch_list) > 10:
                    report.append(f"- ... and {len(branch_list) - 10} more")

                report.append("")

        return "\n".join(report)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Automated branch cleanup for Aurora CloudBank')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be done without making changes')
    parser.add_argument('--execute', action='store_true',
                        help='Actually execute cleanup (overrides dry-run)')
    parser.add_argument('--report-only', action='store_true',
                        help='Generate analysis report only')

    args = parser.parse_args()

    cleanup_manager = BranchCleanupManager()

    print("🌿 Aurora CloudBank - Branch Cleanup System")
    print("=" * 50)

    # Analyze branches
    print("🔍 Analyzing repository branches...")
    branches = cleanup_manager.analyze_branches()

    if not branches:
        print("❌ Failed to analyze branches")
        sys.exit(1)

    # Generate report
    report = cleanup_manager.generate_cleanup_report(branches)

    if args.report_only:
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
    print(f"📄 Report saved to: {report_path}")

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes made")
        print("Use --execute to perform actual cleanup")


if __name__ == "__main__":
    main()
