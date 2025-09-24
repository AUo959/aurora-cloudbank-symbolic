#!/usr/bin/env python3
"""Test script for enhanced GITWiz."""

from scripts.gitwiz_enhanced import EnhancedGITWiz
import traceback


try:

    print("✅ Enhanced GITWiz imported successfully")

    # Test initialization
    gitwiz = EnhancedGITWiz()
    print("✅ Enhanced GITWiz initialized successfully")

    # Test basic analysis
    state = gitwiz.analyze_repository_state()
    print("✅ Repository analysis completed: {state.file_count} files, %s branches", state.branch_count)

    # Test report generation
    report = gitwiz.generate_optimization_report()
    print("✅ Optimization report generated successfully")
    print("\n" + "=" * 60)
    print(report[:500] + "..." if len(report) > 500 else report)

except ImportError as e:
    print("❌ Import error: %s", e)
except Exception as e:
    print("❌ Error: %s", e)

    traceback.print_exc()
