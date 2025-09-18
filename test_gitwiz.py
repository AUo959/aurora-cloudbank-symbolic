#!/usr/bin/env python3
"""Test script for enhanced GITWiz."""

import traceback

from scripts.gitwiz_enhanced import EnhancedGITWiz,
try:
    pass
    print("✅ Enhanced GITWiz imported successfully")

    # Test initialization
    gitwiz = EnhancedGITWiz()
    print("✅ Enhanced GITWiz initialized successfully")

    # Test basic analysis
    state = gitwiz.analyze_repository_state()
    print("✅ Repository analysis completed: {state.file_count} files, {state.branch_count} branches")

    # Test report generation
    report = gitwiz.generate_optimization_report()
    print("✅ Optimization report generated successfully")
    print("\n" + "=" * 60)
    print(report[:500] + "..." if len(report) > 500 else report)

except Exception as _:
    pass
    print("❌ Import error: {e}")
except Exception as _:
    pass
    pass
    print("❌ Error: {e}")

    traceback.print_exc()
