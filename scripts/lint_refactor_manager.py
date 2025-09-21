#!/usr/bin/env python3
"""
Lint Refactor Integration Manager

Unified interface for managing the staged lint refactor process.
Integrates tracking, fixing, and reporting capabilities.

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class LintRefactorManager:
    """Unified manager for lint refactor operations."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.tracker_script = self.project_root / "scripts" / "lint_refactor_tracker.py"
        self.stage1_fixer = self.project_root / "scripts" / "stage1_lint_fixer.py"
    
    def run_command(self, cmd: List[str], capture_output: bool = False) -> Optional[str]:
        """Run a command and return output if requested."""
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                return result.stdout if result.returncode == 0 else None
            else:
                subprocess.run(cmd, cwd=self.project_root, check=True)
                return None
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {e}")
            return None
    
    def initialize_tracking(self):
        """Initialize the tracking system with baseline analysis."""
        print("🚀 Initializing lint refactor tracking system...")
        
        # Run initial analysis
        self.run_command(["python3", str(self.tracker_script), "analyze"])
        
        # Generate initial report
        print("\n📊 Initial status:")
        self.run_command(["python3", str(self.tracker_script), "report"])
        
        print("\n✅ Tracking system initialized!")
        print("Use 'status' command to check progress anytime.")
    
    def status(self):
        """Show current status."""
        print("📊 Current Lint Refactor Status")
        print("=" * 50)
        self.run_command(["python3", str(self.tracker_script), "report"])
    
    def quick_status(self):
        """Show brief status summary."""
        print("📋 Quick Status Summary")
        print("=" * 30)
        self.run_command(["python3", str(self.tracker_script), "checklist"])
    
    def fix_stage1(self, area: str, dry_run: bool = False):
        """Apply Stage 1 fixes to an area."""
        area_path = self.project_root / area
        
        if not area_path.exists():
            print(f"❌ Area not found: {area}")
            return False
        
        print(f"🔧 Applying Stage 1 fixes to {area}")
        
        # Build command
        cmd = ["python3", str(self.stage1_fixer)]
        if dry_run:
            cmd.append("--dry-run")
        cmd.append(area)
        
        # Run fixer
        if self.run_command(cmd) is not None or not dry_run:
            if not dry_run:
                # Re-analyze the area
                print(f"\n🔍 Re-analyzing {area}...")
                self.run_command(["python3", str(self.tracker_script), "analyze", "--area", area])
                
                # Check if Stage 1 can be marked complete
                print(f"\n✅ Stage 1 fixes applied to {area}")
                print("Run 'complete-stage' to mark Stage 1 complete if all issues are resolved.")
            
            return True
        
        return False
    
    def complete_stage(self, area: str, stage: int):
        """Mark a stage as complete for an area."""
        print(f"✅ Marking Stage {stage} complete for {area}")
        
        if self.run_command(["python3", str(self.tracker_script), "complete", "--area", area, "--stage", str(stage)]):
            print("\n📋 Updated checklist:")
            self.run_command(["python3", str(self.tracker_script), "checklist"])
            return True
        
        return False
    
    def analyze_area(self, area: str):
        """Analyze lint issues in a specific area."""
        print(f"🔍 Analyzing {area}...")
        self.run_command(["python3", str(self.tracker_script), "analyze", "--area", area])
    
    def analyze_all(self):
        """Analyze all areas."""
        print("🔍 Analyzing all areas...")
        self.run_command(["python3", str(self.tracker_script), "analyze"])
    
    def workflow_guide(self, area: str):
        """Show workflow guide for a specific area."""
        print(f"📚 Workflow Guide for {area}")
        print("=" * 50)
        
        workflow_steps = [
            f"1. Analyze current state:",
            f"   python3 scripts/lint_refactor_manager.py analyze {area}",
            "",
            f"2. Apply Stage 1 fixes (preview first):",
            f"   python3 scripts/lint_refactor_manager.py fix-stage1 {area} --dry-run",
            f"   python3 scripts/lint_refactor_manager.py fix-stage1 {area}",
            "",
            f"3. Mark Stage 1 complete:",
            f"   python3 scripts/lint_refactor_manager.py complete-stage {area} 1",
            "",
            f"4. Continue with manual fixes for stages 2-4",
            "",
            f"5. Update tracking after each stage completion"
        ]
        
        for step in workflow_steps:
            print(step)
    
    def validate_lint(self, area: str):
        """Validate lint status for an area."""
        area_path = self.project_root / area
        
        if not area_path.exists():
            print(f"❌ Area not found: {area}")
            return False
        
        print(f"🔍 Validating lint status for {area}...")
        
        # Run flake8 with tracking error codes
        error_codes = ["W293", "E303", "E302", "F401", "F811", "F821", "E999", "E501"]
        cmd = ["flake8", f"--select={','.join(error_codes)}", area]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print(f"✅ No tracked lint issues found in {area}")
                return True
            else:
                print(f"⚠️  Found lint issues in {area}:")
                print(result.stdout)
                return False
                
        except subprocess.CalledProcessError:
            print(f"❌ Error running flake8 on {area}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Lint Refactor Integration Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Initialize command
    subparsers.add_parser("init", help="Initialize tracking system")
    
    # Status commands
    subparsers.add_parser("status", help="Show detailed status")
    subparsers.add_parser("quick-status", help="Show brief status summary")
    
    # Analysis commands
    analyze_parser = subparsers.add_parser("analyze", help="Analyze lint issues")
    analyze_parser.add_argument("area", nargs="?", help="Specific area to analyze (optional)")
    
    # Fix commands
    fix_parser = subparsers.add_parser("fix-stage1", help="Apply Stage 1 fixes")
    fix_parser.add_argument("area", help="Area to fix")
    fix_parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    
    # Complete commands
    complete_parser = subparsers.add_parser("complete-stage", help="Mark stage complete")
    complete_parser.add_argument("area", help="Area name")
    complete_parser.add_argument("stage", type=int, help="Stage number")
    
    # Utility commands
    guide_parser = subparsers.add_parser("workflow", help="Show workflow guide")
    guide_parser.add_argument("area", help="Area name")
    
    validate_parser = subparsers.add_parser("validate", help="Validate lint status")
    validate_parser.add_argument("area", help="Area to validate")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = LintRefactorManager()
    
    # Command dispatch
    if args.command == "init":
        manager.initialize_tracking()
    
    elif args.command == "status":
        manager.status()
    
    elif args.command == "quick-status":
        manager.quick_status()
    
    elif args.command == "analyze":
        if args.area:
            manager.analyze_area(args.area)
        else:
            manager.analyze_all()
    
    elif args.command == "fix-stage1":
        manager.fix_stage1(args.area, args.dry_run)
    
    elif args.command == "complete-stage":
        manager.complete_stage(args.area, args.stage)
    
    elif args.command == "workflow":
        manager.workflow_guide(args.area)
    
    elif args.command == "validate":
        manager.validate_lint(args.area)
    
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()