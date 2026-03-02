#!/usr/bin/env python3
"""Compatibility adapter around branch_manager.py for branch cleanup automation."""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path
from typing import Dict, List

from branch_manager import BranchManager


class BranchCleanupManager:
    """Backwards-compatible adapter used by maintenance scripts."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self._manager = BranchManager(str(self.repo_path))

    def analyze_branches(self) -> Dict[str, List[Dict]]:
        analysis = self._manager.analyze_branches()
        cleanup_names = []
        for names in analysis.get("cleanup_candidates", {}).values():
            cleanup_names.extend(names)

        cleanup_set = set(cleanup_names)
        all_names = []
        for names in analysis.get("categories", {}).values():
            all_names.extend(names)

        return {
            "cleanup_candidates": [{"name": name} for name in sorted(cleanup_set)],
            "keep": [{"name": name} for name in sorted(set(all_names) - cleanup_set)],
            "manual_review": [
                {"name": name} for name in analysis.get("cleanup_candidates", {}).get("old_unmerged", [])
            ],
        }

    def execute_cleanup(self, branches: Dict[str, List[Dict]], dry_run: bool = True) -> Dict:
        self._manager.dry_run = dry_run
        raw = self._manager.cleanup_stale_branches(
            max_age_days=30,
            categories=["feature", "dependency", "security", "backup", "hotfix", "other"],
        )
        return {
            "deleted": raw.get("deleted", []),
            "archived": [],
            "merged": [],
            "errors": raw.get("errors", []),
            "skipped": raw.get("skipped", []),
        }

    def generate_cleanup_report(self, branches: Dict[str, List[Dict]], results: Dict | None = None) -> str:
        lines = [
            "# Branch Cleanup Analysis Report",
            f"**Generated:** {datetime.datetime.now().isoformat()}",
            "",
            f"- Cleanup candidates: {len(branches.get('cleanup_candidates', []))}",
            f"- Keep: {len(branches.get('keep', []))}",
            f"- Manual review: {len(branches.get('manual_review', []))}",
        ]
        if results is not None:
            lines.extend(
                [
                    "",
                    f"- Deleted: {len(results.get('deleted', []))}",
                    f"- Errors: {len(results.get('errors', []))}",
                ]
            )
        return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated branch cleanup adapter")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry-run)")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    args = parser.parse_args()

    manager = BranchCleanupManager()
    branches = manager.analyze_branches()

    report = manager.generate_cleanup_report(branches)
    report_path = Path("branch_cleanup_report.md")
    report_path.write_text(report, encoding="utf-8")
    print(f"Report saved to: {report_path}")

    if args.report_only:
        return 0

    results = manager.execute_cleanup(branches, dry_run=not args.execute)
    print(f"Deleted: {len(results['deleted'])}, Errors: {len(results['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
