#!/usr/bin/env python3
"""
Lint Tracking Manager
Tracks and manages staged lint cleanup across the Aurora CloudBank repository
"""

import subprocess
import json
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class AreaStatus:
    """Status tracking for a code area."""
    name: str
    total_files: int
    stage1_issues: int  # W293, E303, E302
    stage2_issues: int  # F401, F811  
    stage3_issues: int  # F821, E999
    stage4_issues: int  # E501
    stage1_complete: bool = False
    stage2_complete: bool = False
    stage3_complete: bool = False
    stage4_complete: bool = False
    last_updated: str = ""


class LintTracker:
    """Main tracking class for lint cleanup progress."""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.tracking_file = self.repo_root / ".lint_tracking.json"
        self.target_areas = [
            "modules/opal2",
            "modules/cask", 
            "src/core",
            "src/bridges",
            "src/servers"
        ]
        
    def count_issues_by_type(self, area: str, error_codes: List[str]) -> int:
        """Count specific types of lint issues in an area."""
        try:
            cmd = [
                "flake8", area, 
                "--max-line-length=120", 
                "--extend-ignore=E203,W503",
                f"--select={','.join(error_codes)}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except Exception:
            return -1  # Error state
            
    def count_python_files(self, area: str) -> int:
        """Count Python files in an area."""
        area_path = self.repo_root / area
        return len(list(area_path.rglob("*.py"))) if area_path.exists() else 0
        
    def scan_area(self, area: str) -> AreaStatus:
        """Scan a single area and return its status."""
        return AreaStatus(
            name=area,
            total_files=self.count_python_files(area),
            stage1_issues=self.count_issues_by_type(area, ["W293", "E303", "E302"]),
            stage2_issues=self.count_issues_by_type(area, ["F401", "F811"]),
            stage3_issues=self.count_issues_by_type(area, ["F821", "E999"]),
            stage4_issues=self.count_issues_by_type(area, ["E501"]),
            last_updated=datetime.datetime.now().isoformat()
        )
        
    def scan_all_areas(self) -> Dict[str, AreaStatus]:
        """Scan all target areas."""
        print("🔍 Scanning all areas for lint issues...")
        results = {}
        
        for area in self.target_areas:
            print(f"   Scanning {area}...")
            status = self.scan_area(area)
            
            # Determine completion status
            status.stage1_complete = status.stage1_issues == 0
            status.stage2_complete = status.stage2_issues == 0  
            status.stage3_complete = status.stage3_issues == 0
            status.stage4_complete = status.stage4_issues == 0
            
            results[area] = status
            
        return results
        
    def save_tracking_data(self, data: Dict[str, AreaStatus]) -> None:
        """Save tracking data to file."""
        serializable_data = {
            "scan_timestamp": datetime.datetime.now().isoformat(),
            "areas": {name: asdict(status) for name, status in data.items()}
        }
        
        with open(self.tracking_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
            
        print(f"📊 Tracking data saved to {self.tracking_file}")
        
    def load_tracking_data(self) -> Dict[str, AreaStatus]:
        """Load tracking data from file."""
        if not self.tracking_file.exists():
            return {}
            
        with open(self.tracking_file, 'r') as f:
            data = json.load(f)
            
        return {
            name: AreaStatus(**area_data) 
            for name, area_data in data.get("areas", {}).items()
        }
        
    def generate_report(self, data: Dict[str, AreaStatus]) -> str:
        """Generate a status report."""
        report = []
        report.append("# 🧹 Lint Refactor Tracking Report")
        report.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_files = sum(status.total_files for status in data.values())
        total_stage1 = sum(status.stage1_issues for status in data.values())
        total_stage2 = sum(status.stage2_issues for status in data.values())
        total_stage3 = sum(status.stage3_issues for status in data.values())
        total_stage4 = sum(status.stage4_issues for status in data.values())
        
        areas_stage1_complete = sum(1 for status in data.values() if status.stage1_complete)
        areas_stage2_complete = sum(1 for status in data.values() if status.stage2_complete)
        areas_stage3_complete = sum(1 for status in data.values() if status.stage3_complete)
        areas_stage4_complete = sum(1 for status in data.values() if status.stage4_complete)
        
        report.append("## 📊 Overall Progress")
        report.append(f"- **Total Python files:** {total_files}")
        report.append(f"- **Stage 1 (Whitespace):** {total_stage1} issues, {areas_stage1_complete}/{len(data)} areas complete")
        report.append(f"- **Stage 2 (Imports):** {total_stage2} issues, {areas_stage2_complete}/{len(data)} areas complete")
        report.append(f"- **Stage 3 (Logic/Names):** {total_stage3} issues, {areas_stage3_complete}/{len(data)} areas complete")
        report.append(f"- **Stage 4 (Line Length):** {total_stage4} issues, {areas_stage4_complete}/{len(data)} areas complete")
        report.append("")
        
        # Per-area details
        report.append("## 🎯 Area Details")
        report.append("")
        
        for area, status in data.items():
            report.append(f"### {area}")
            report.append(f"- **Files:** {status.total_files}")
            report.append(f"- **Stage 1:** {'✅' if status.stage1_complete else '❌'} ({status.stage1_issues} issues)")
            report.append(f"- **Stage 2:** {'✅' if status.stage2_complete else '❌'} ({status.stage2_issues} issues)")
            report.append(f"- **Stage 3:** {'✅' if status.stage3_complete else '❌'} ({status.stage3_issues} issues)")
            report.append(f"- **Stage 4:** {'✅' if status.stage4_complete else '❌'} ({status.stage4_issues} issues)")
            report.append(f"- **Last Updated:** {status.last_updated}")
            report.append("")
            
        return "\n".join(report)
        
    def update_makefile(self) -> None:
        """Update Makefile with staged lint targets."""
        makefile_path = self.repo_root / "Makefile"
        
        if not makefile_path.exists():
            print("⚠️  Makefile not found")
            return
            
        # Add staged lint targets
        new_targets = """
# Staged lint targets for tracking
.PHONY: lint-stage1
lint-stage1:
\t# Stage 1: Whitespace and formatting issues
\tflake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=W293,E303,E302

.PHONY: lint-stage2  
lint-stage2:
\t# Stage 2: Import issues
\tflake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=F401,F811

.PHONY: lint-stage3
lint-stage3:
\t# Stage 3: Undefined names and logic errors
\tflake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=F821,E999

.PHONY: lint-stage4
lint-stage4:
\t# Stage 4: Line length issues
\tflake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=E501

.PHONY: lint-tracking
lint-tracking:
\t# Generate lint tracking report
\tpython scripts/lint_tracking_manager.py --report
"""
        
        with open(makefile_path, 'a') as f:
            f.write(new_targets)
            
        print("✅ Updated Makefile with staged lint targets")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Lint tracking manager")
    parser.add_argument("--scan", action="store_true", help="Scan all areas")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--update-makefile", action="store_true", help="Update Makefile")
    
    args = parser.parse_args()
    
    tracker = LintTracker()
    
    if args.scan or not args.report:
        data = tracker.scan_all_areas()
        tracker.save_tracking_data(data)
        
    if args.report:
        data = tracker.load_tracking_data()
        if not data:
            print("No tracking data found. Run with --scan first.")
            return
            
        report = tracker.generate_report(data)
        print(report)
        
        # Save report to file
        report_file = tracker.repo_root / "LINT_TRACKING_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to {report_file}")
        
    if args.update_makefile:
        tracker.update_makefile()


if __name__ == "__main__":
    main()