#!/usr/bin/env python3
"""
#STATUS//. - Quick Status Check

Quick overview of working tree status without any modifications.
Phase 1 only from #321//. - check for pending changes.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.command_chain.comprehensive_sync_321 import (  # noqa: E402
    ComprehensiveSync,
    SyncConfig
)


def execute_status(config_path: Optional[str] = None, workspace_path: Optional[str] = None):
    """
    Execute quick status check (Phase 1 only).

    Args:
        config_path: Path to configuration file (optional)
        workspace_path: Path to workspace directory (optional)

    Returns:
        Phase 1 result with file categorization
    """
    # Load configuration
    if config_path and Path(config_path).exists():
        config = SyncConfig.load(Path(config_path))
    elif Path(".aurora/sync_config.json").exists():
        config = SyncConfig.load(Path(".aurora/sync_config.json"))
    else:
        config = SyncConfig()

    # Set workspace
    if workspace_path:
        workspace = Path(workspace_path)
    else:
        workspace = Path.cwd()

    # Create sync instance
    sync = ComprehensiveSync(config, workspace)

    # Execute Phase 1 only
    print("\n🔍 #STATUS//. - Quick Status Check\n")
    print("=" * 60)

    phase1_result = sync._phase1_check_changes()

    if not phase1_result.success:
        print(f"\n❌ {phase1_result.message}")
        return phase1_result

    # Display results
    details = phase1_result.details

    if details.get('files_changed', 0) == 0:
        print("\n✅ Working tree is clean - no changes detected")
        print("=" * 60)
        return phase1_result

    print(f"\n📊 Changes detected: {details['files_changed']} files\n")

    # Show categorized changes
    categories = details.get('categories', {})
    for category, files in categories.items():
        if files:
            print(f"  {category.upper()}: {len(files)} files")
            for file in files[:5]:  # Show first 5 files per category
                print(f"    - {file}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
            print()

    # Show special flags
    if details.get('is_docs_only'):
        print("  ℹ️  Changes are documentation-only")
    if details.get('is_config_only'):
        print("  ℹ️  Changes are configuration-only")

    print("=" * 60)
    print(f"\n⏱️  Status check completed in {phase1_result.duration_seconds:.2f}s")

    return phase1_result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Quick status check - Phase 1 of #321//.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Check status with default config
  %(prog)s --config custom.json  # Use custom configuration
  %(prog)s --workspace /path/to/repo  # Check specific repository

This command provides a quick overview of pending changes without
staging, committing, or syncing anything.
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (default: .aurora/sync_config.json)'
    )

    parser.add_argument(
        '--workspace',
        type=str,
        help='Path to workspace directory (default: current directory)'
    )

    args = parser.parse_args()

    try:
        result = execute_status(
            config_path=args.config,
            workspace_path=args.workspace
        )

        sys.exit(0 if result.success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Status check interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
