#!/usr/bin/env python3
"""
Demo: Aurora Code Quality Analyzer
Shows how to use the code quality analysis system locally.
Part of Issue #258 implementation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.code_quality_analyzer import CodeQualityAnalyzer


def main():
    """Run a demo code quality analysis."""
    print("=" * 70)
    print("Aurora Code Quality Analyzer - Demo")
    print("=" * 70)
    print()
    
    # Initialize analyzer
    print("📊 Initializing analyzer...")
    analyzer = CodeQualityAnalyzer()
    print(f"   Repository: {analyzer.repo_path}")
    print(f"   Config file: {analyzer.config_file}")
    print()
    
    # Run analysis on src directory
    print("🔍 Running analysis on src/ directory...")
    print("   (This may take a moment...)")
    print()
    
    report = analyzer.run_flake8_analysis(['src'])
    
    # Display results
    print("=" * 70)
    print("Analysis Results")
    print("=" * 70)
    print()
    print(f"Status: {'✅ PASSED' if report.passed else '❌ FAILED'}")
    print(f"Timestamp: {report.timestamp}")
    print()
    print("Violation Breakdown:")
    print(f"  🔴 Critical: {report.critical_count}")
    print(f"  🟠 High:     {report.high_count}")
    print(f"  🟡 Medium:   {report.medium_count}")
    print(f"  🟢 Low:      {report.low_count}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━")
    print(f"  📊 Total:    {report.total_violations}")
    print()
    
    # Show critical violations if any
    if report.critical_count > 0:
        print("⚠️  Critical Violations (require immediate attention):")
        print()
        critical = analyzer.get_critical_violations(report)
        for i, violation in enumerate(critical[:5], 1):  # Show first 5
            print(f"{i}. {violation.file_path}:{violation.line_number}")
            print(f"   Code: {violation.code}")
            print(f"   Message: {violation.message}")
            print()
        
        if len(critical) > 5:
            print(f"   ... and {len(critical) - 5} more critical violations")
            print()
    
    # Generate Aurora reflection
    print("🌌 Generating Aurora reflection format...")
    reflection = analyzer.generate_reflection_report(report)
    print(f"   Context tag: {reflection['context_tag']}")
    print(f"   Symbolic hash: {reflection['symbolic_hash_validation']}")
    print(f"   Chain notation: {reflection['dlp_trail']['chain_notation']}")
    print()
    
    # Save report
    output_path = Path('reports') / 'demo_quality_report.json'
    analyzer.save_report(report, output_path)
    print(f"💾 Report saved to: {output_path}")
    print()
    
    # Summary
    print("=" * 70)
    if report.passed:
        print("✅ Analysis completed successfully!")
        print("   No critical violations found.")
    else:
        print("❌ Analysis found critical violations!")
        print("   Please review and fix before committing.")
    print("=" * 70)
    
    return 0 if report.passed else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
