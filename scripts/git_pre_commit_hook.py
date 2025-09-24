#!/usr/bin/env python3
"""

            from aurora_validation_manager import ValidationManager

Aurora CloudBank - Git Pre-commit Hook
Automatically validates changes against canonical specifications
Prevents commits that violate critical canonical requirements

This hook runs before each commit and:
1. Validates changed files against ORION CORE canonical spec
2. Auto-fixes minor issues
3. Blocks commits with critical violations
4. Provides clear feedback and remediation guidance
"""
from pathlib import Path
import subprocess
import os
import sys



# Add the scripts directory to Python path
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))

try:
    from canonical_validator import CanonicalValidator
except ImportError:
    print("❌ Error: Could not import canonical_validator")
    print("   Ensure scripts/canonical_validator.py exists")
    sys.exit(1)


def get_staged_files():
    """Get list of staged files for commit"""
    try:
        result = subprocess.run(
            ["git", "di", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []


def has_critical_violations(results):
    """Check if validation results contain critical violations"""
    critical_escalations = [
        r for r in results
        if r.status == "ESCALATE" and r.severity == "CRITICAL"
    ]
    return len(critical_escalations) > 0


def print_validation_summary(results):
    """Print formatted validation summary"""
    auto_fixes = [r for r in results if r.status == "AUTO_FIXED"]
    escalations = [r for r in results if r.status == "ESCALATE"]
    critical = [r for r in escalations if r.severity == "CRITICAL"]
    high = [r for r in escalations if r.severity == "HIGH"]

    print("\n🛰️ Aurora CloudBank Canonical Validation")
    print("=" * 50)

    if auto_fixes:
        print("🔧 Auto-fixes applied: {len(auto_fixes)}")
        for fix in auto_fixes[:3]:  # Show first 3
            print("  ✅ {fix.message}")
        if len(auto_fixes) > 3:
            print("  ... and {len(auto_fixes) - 3} more")

    if critical:
        print("\n🚨 CRITICAL VIOLATIONS ({len(critical)}):")
        for violation in critical:
            print("  ❗ {violation.message}")
            print("     Fix: {violation.suggested_fix}")

    if high:
        print("\n🔴 HIGH PRIORITY ISSUES ({len(high)}):")
        for issue in high[:2]:  # Show first 2
            print("  🔴 {issue.message}")
            print("     Fix: {issue.suggested_fix}")
        if len(high) > 2:
            print("  ... and {len(high) - 2} more (see full report)")


def main():
    """Main pre-commit hook execution"""
    print("🔍 Running Aurora CloudBank canonical validation...")

    # Get staged files
    staged_files = get_staged_files()

    if not staged_files:
        print("✅ No files to validate")
        return 0

    # Filter for files we can validate
    validatable_extensions = {'.md', '.txt', '.js', '.ts', '.py', '.json', '.yaml', '.yml'}
    files_to_validate = [
        f for f in staged_files
        if Path(f).exists() and Path(f).suffix in validatable_extensions
    ]

    if not files_to_validate:
        print("✅ No validatable files in commit")
        return 0

    print("📁 Validating {len(files_to_validate)} files...")

    # Initialize validator
    validator = CanonicalValidator()
    all_results = []

    # Validate each staged file
    for file_path in files_to_validate:
        try:
            results = validator.validate_file(file_path)
            all_results.extend(results)
        except Exception as e:
            print("❌ Error validating {file_path}: {e}")
            return 1

    # Print validation summary
    print_validation_summary(all_results)

    # Check for critical violations
    if has_critical_violations(all_results):
        print("\n🚫 COMMIT BLOCKED - Critical canonical violations detected!")
        print("   Fix critical issues before committing")
        print("   Run: python scripts/canonical_validator.py for full report")
        return 1

    # Check for high-priority violations (configurable)
    high_priority = [r for r in all_results if r.status == "ESCALATE" and r.severity == "HIGH"]
    if high_priority:
        print("\n⚠️ Warning: {len(high_priority)} high-priority issues detected")
        print("   Consider fixing before commit")

        # Optionally block on high-priority (can be configured)
        block_on_high = os.environ.get("AURORA_BLOCK_ON_HIGH", "false").lower() == "true"
        if block_on_high:
            print("🚫 COMMIT BLOCKED - High-priority violations (AURORA_BLOCK_ON_HIGH=true)")
            return 1

    # Generate quick report for escalations using validation manager
    escalations = [r for r in all_results if r.status == "ESCALATE"]
    if escalations:
        # Import validation manager to handle file paths intelligently
        try:
            sys.path.append(str(Path(__file__).parent))

            manager = ValidationManager()
            report_path = manager.get_validation_file_path("PRE_COMMIT_VALIDATION_ISSUES.md")

            # Only write if not in memory-only mode
            if manager.config["strategy"] != "memory_only":
                # Ensure directory exists
                report_path.parent.mkdir(parents=True, exist_ok=True)

                with open(report_path, 'w', encoding="utf-8") as f:
                    f.write("# Pre-Commit Validation Issues\n\n")
                    f.write("Generated: {Path(__file__).name} at {Path().cwd()}\n")
                    f.write("Strategy: {manager.config['strategy']}\n\n")
                    for issue in escalations:
                        f.write("## {issue.check_name} ({issue.severity})\n")
                        f.write("**Issue**: {issue.message}\n\n")
                        f.write("**Suggested Fix**: {issue.suggested_fix}\n\n")

                print("📊 Detailed issues saved to: {report_path}")

                # If using smart exclusion, don't stage the validation file
                if manager.config["strategy"] == "smart_exclusion":
                    print("🔒 Validation file excluded from commit (smart exclusion active)")
            else:
                print("📊 Validation complete (memory-only mode - no files written)")

        except ImportError:
            # Fallback to original behavior if manager not available
            report_path = "PRE_COMMIT_VALIDATION_ISSUES.md"
            with open(report_path, 'w', encoding="utf-8") as f:
                f.write("# Pre-Commit Validation Issues\n\n")
                for issue in escalations:
                    f.write("## {issue.check_name} ({issue.severity})\n")
                    f.write("**Issue**: {issue.message}\n\n")
                    f.write("**Suggested Fix**: {issue.suggested_fix}\n\n")
            print("📊 Detailed issues saved to: {report_path}")

    auto_fixes = [r for r in all_results if r.status == "AUTO_FIXED"]
    if auto_fixes:
        print("\n✅ Commit proceeding with {len(auto_fixes)} auto-fixes applied")

        # Re-stage auto-fixed files
        for file_path in files_to_validate:
            try:
                subprocess.run(["git", "add", file_path], check=True)
            except subprocess.CalledProcessError:
                pass  # File might not need re-staging
    else:
        print("\n✅ All canonical validations passed - commit proceeding")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
