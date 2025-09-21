#!/usr/bin/env python3
"""
Lint Refactor Tracker

Comprehensive tracking system for staged lint refactors across src/ and modules/ areas.
Provides detailed analysis, progress tracking, and automated fixes for each stage.

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import datetime as dt


@dataclass
class LintStageConfig:
    """Configuration for a specific lint refactor stage."""
    stage_number: int
    name: str
    description: str
    error_codes: List[str]
    auto_fixable: bool = False


@dataclass
class AreaStatus:
    """Status tracking for a specific area."""
    area_name: str
    owner: str
    notes: str
    stage_status: Dict[int, bool]  # stage_number -> completed
    total_issues: Dict[str, int]  # error_code -> count
    last_updated: str


@dataclass
class LintRefactorProgress:
    """Overall progress tracking for lint refactor initiative."""
    areas: Dict[str, AreaStatus]
    stages: Dict[int, LintStageConfig]
    started_at: str
    last_updated: str
    overall_completion: float


class LintRefactorTracker:
    """Main tracking system for lint refactor progress."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.config_dir = self.project_root / ".lint_refactor"
        self.config_dir.mkdir(exist_ok=True)
        self.progress_file = self.config_dir / "progress.json"
        
        # Define stages based on the issue requirements
        self.stages = {
            1: LintStageConfig(1, "Whitespace/Formatting", "W293/E303/E302", ["W293", "E303", "E302"], True),
            2: LintStageConfig(2, "Imports", "F401/F811 and rename collisions", ["F401", "F811"], True),
            3: LintStageConfig(3, "Undefined Names/Syntax", "F821/E999", ["F821", "E999"], False),
            4: LintStageConfig(4, "Line Length", "E501 and structured wrapping", ["E501"], True),
            5: LintStageConfig(5, "CI Expansion", "Expand CI lint coverage", [], False),
        }
        
        # Define target areas based on ownership table
        self.target_areas = {
            "modules/opal2": {"owner": "AUo959", "notes": "Complex; many E999/F821/line-length"},
            "modules/cask": {"owner": "AUo959", "notes": "Line length; chart module long lines"},
            "src/core": {"owner": "AUo959", "notes": "Whitespace/imports first"},
            "src/bridges": {"owner": "AUo959", "notes": "Undefined names/line-lengths present"},
            "src/servers": {"owner": "AUo959", "notes": "Long lines and extra blanks"},
        }
        
        self.progress = self._load_or_initialize_progress()
    
    def _load_or_initialize_progress(self) -> LintRefactorProgress:
        """Load existing progress or initialize new tracking."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                return self._deserialize_progress(data)
            except Exception as e:
                print(f"Warning: Could not load progress file: {e}")
        
        # Initialize new progress
        areas = {}
        for area_name, config in self.target_areas.items():
            areas[area_name] = AreaStatus(
                area_name=area_name,
                owner=config["owner"],
                notes=config["notes"],
                stage_status={str(i): False for i in range(1, 6)},  # Use string keys
                total_issues={},
                last_updated=dt.datetime.now().isoformat()
            )
        
        return LintRefactorProgress(
            areas=areas,
            stages=self.stages,
            started_at=dt.datetime.now().isoformat(),
            last_updated=dt.datetime.now().isoformat(),
            overall_completion=0.0
        )
    
    def _deserialize_progress(self, data: dict) -> LintRefactorProgress:
        """Deserialize progress data from JSON."""
        areas = {}
        for area_name, area_data in data.get("areas", {}).items():
            areas[area_name] = AreaStatus(
                area_name=area_data["area_name"],
                owner=area_data["owner"],
                notes=area_data["notes"],
                stage_status=area_data["stage_status"],
                total_issues=area_data["total_issues"],
                last_updated=area_data["last_updated"]
            )
        
        return LintRefactorProgress(
            areas=areas,
            stages=self.stages,
            started_at=data.get("started_at", dt.datetime.now().isoformat()),
            last_updated=data.get("last_updated", dt.datetime.now().isoformat()),
            overall_completion=data.get("overall_completion", 0.0)
        )
    
    def _save_progress(self):
        """Save current progress to file."""
        data = {
            "areas": {name: asdict(area) for name, area in self.progress.areas.items()},
            "started_at": self.progress.started_at,
            "last_updated": dt.datetime.now().isoformat(),
            "overall_completion": self._calculate_overall_completion()
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.progress.last_updated = data["last_updated"]
        self.progress.overall_completion = data["overall_completion"]
    
    def analyze_area(self, area_path: str) -> Dict[str, int]:
        """Analyze lint issues in a specific area."""
        if not (self.project_root / area_path).exists():
            return {}
        
        # Get all error codes we're tracking
        all_codes = []
        for stage in self.stages.values():
            all_codes.extend(stage.error_codes)
        
        if not all_codes:
            return {}
        
        try:
            # Run flake8 with specific error codes
            result = subprocess.run([
                "flake8", 
                "--select=" + ",".join(all_codes),
                area_path
            ], capture_output=True, text=True, cwd=self.project_root)
            
            # Parse results
            issue_counts = {code: 0 for code in all_codes}
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                # Extract error code from flake8 output
                for code in all_codes:
                    if f" {code} " in line:
                        issue_counts[code] += 1
                        break
            
            return issue_counts
            
        except Exception as e:
            print(f"Error analyzing {area_path}: {e}")
            return {}
    
    def update_area_analysis(self, area_name: str):
        """Update analysis for a specific area."""
        if area_name not in self.progress.areas:
            print(f"Unknown area: {area_name}")
            return
        
        issue_counts = self.analyze_area(area_name)
        area = self.progress.areas[area_name]
        area.total_issues = issue_counts
        area.last_updated = dt.datetime.now().isoformat()
        
        print(f"✅ Updated analysis for {area_name}:")
        for code, count in issue_counts.items():
            if count > 0:
                print(f"  {code}: {count} issues")
    
    def update_all_analyses(self):
        """Update analysis for all areas."""
        print("🔍 Analyzing lint issues across all areas...")
        
        for area_name in self.progress.areas:
            self.update_area_analysis(area_name)
        
        self._save_progress()
        print("\n📊 Analysis complete. Use 'report' to see detailed status.")
    
    def mark_stage_complete(self, area_name: str, stage_number: int):
        """Mark a stage as complete for an area."""
        if area_name not in self.progress.areas:
            print(f"Unknown area: {area_name}")
            return
        
        if stage_number not in self.stages:
            print(f"Unknown stage: {stage_number}")
            return
        
        area = self.progress.areas[area_name]
        stage_key = str(stage_number)  # Use string key
        area.stage_status[stage_key] = True
        area.last_updated = dt.datetime.now().isoformat()
        
        self._save_progress()
        
        stage = self.stages[stage_number]
        print(f"✅ Marked Stage {stage_number} ({stage.name}) complete for {area_name}")
    
    def _calculate_overall_completion(self) -> float:
        """Calculate overall completion percentage."""
        total_stages = len(self.progress.areas) * len(self.stages)
        completed_stages = sum(
            sum(area.stage_status.values()) 
            for area in self.progress.areas.values()
        )
        
        return (completed_stages / total_stages) * 100 if total_stages > 0 else 0.0
    
    def generate_report(self) -> str:
        """Generate comprehensive progress report."""
        report = []
        report.append("# Lint Refactor Progress Report")
        report.append(f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Overall Completion: {self.progress.overall_completion:.1f}%")
        report.append("")
        
        # Overall summary
        report.append("## Overall Summary")
        report.append("")
        
        total_issues = 0
        for area in self.progress.areas.values():
            total_issues += sum(area.total_issues.values())
        
        report.append(f"- **Total Areas**: {len(self.progress.areas)}")
        report.append(f"- **Total Outstanding Issues**: {total_issues}")
        report.append(f"- **Completion**: {self.progress.overall_completion:.1f}%")
        report.append("")
        
        # Stage progress
        report.append("## Stage Progress")
        report.append("")
        
        for stage_num, stage in self.stages.items():
            completed_areas = sum(
                1 for area in self.progress.areas.values() 
                if area.stage_status.get(str(stage_num), False)  # Use string key
            )
            total_areas = len(self.progress.areas)
            percentage = (completed_areas / total_areas) * 100 if total_areas > 0 else 0
            
            report.append(f"### Stage {stage_num}: {stage.name}")
            report.append(f"- **Progress**: {completed_areas}/{total_areas} areas ({percentage:.1f}%)")
            report.append(f"- **Description**: {stage.description}")
            report.append(f"- **Auto-fixable**: {'Yes' if stage.auto_fixable else 'No'}")
            report.append("")
        
        # Area details
        report.append("## Area Details")
        report.append("")
        
        for area_name, area in self.progress.areas.items():
            report.append(f"### {area_name}")
            report.append(f"- **Owner**: {area.owner}")
            report.append(f"- **Notes**: {area.notes}")
            report.append(f"- **Last Updated**: {area.last_updated}")
            
            # Stage status
            completed_stages = sum(area.stage_status.values())
            total_stages = len(self.stages)
            area_completion = (completed_stages / total_stages) * 100 if total_stages > 0 else 0
            
            report.append(f"- **Completion**: {completed_stages}/{total_stages} stages ({area_completion:.1f}%)")
            
            # Stage checklist
            report.append("- **Stages**:")
            for stage_num, completed in area.stage_status.items():
                status = "✅" if completed else "⬜"
                stage_key = int(stage_num) if isinstance(stage_num, str) else stage_num
                stage_name = self.stages[stage_key].name
                report.append(f"  - {status} Stage {stage_key}: {stage_name}")
            
            # Issue summary
            if area.total_issues:
                total_area_issues = sum(area.total_issues.values())
                report.append(f"- **Outstanding Issues**: {total_area_issues}")
                for code, count in area.total_issues.items():
                    if count > 0:
                        report.append(f"  - {code}: {count}")
            
            report.append("")
        
        return "\n".join(report)
    
    def generate_github_issue_checklist(self) -> str:
        """Generate GitHub issue checklist format."""
        checklist = []
        checklist.append("## Tracking checklist")
        checklist.append("")
        
        # Owner agreements (if not all assigned to same person)
        owners = set(area.owner for area in self.progress.areas.values())
        if len(owners) > 1:
            checklist.append("- [ ] Agree owners for areas above")
        else:
            checklist.append("- [x] Agree owners for areas above")
        
        # Stage completion for each area
        for stage_num, stage in self.stages.items():
            for area_name, area in self.progress.areas.items():
                stage_key = str(stage_num)  # Ensure string key consistency
                status = "[x]" if area.stage_status.get(stage_key, False) else "[ ]"
                checklist.append(f"- {status} Stage {stage_num} complete for {area_name}")
        
        return "\n".join(checklist)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Lint Refactor Tracker")
    parser.add_argument("command", choices=["analyze", "report", "complete", "checklist"],
                       help="Command to run")
    parser.add_argument("--area", help="Specific area to operate on")
    parser.add_argument("--stage", type=int, help="Stage number to mark complete")
    
    args = parser.parse_args()
    
    tracker = LintRefactorTracker()
    
    if args.command == "analyze":
        if args.area:
            tracker.update_area_analysis(args.area)
            tracker._save_progress()
        else:
            tracker.update_all_analyses()
    
    elif args.command == "report":
        print(tracker.generate_report())
    
    elif args.command == "complete":
        if not args.area or not args.stage:
            print("Error: --area and --stage required for 'complete' command")
            sys.exit(1)
        tracker.mark_stage_complete(args.area, args.stage)
    
    elif args.command == "checklist":
        print(tracker.generate_github_issue_checklist())


if __name__ == "__main__":
    main()