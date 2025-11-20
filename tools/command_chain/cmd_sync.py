#!/usr/bin/env python3
"""
#SYNC//. - Sync to Remote Only

Sync local commits to remote repository.
Phase 4 from #321//. - sync to main.
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


def execute_sync(config_path: Optional[str] = None, workspace_path: Optional[str] = None):
    """
    Execute sync to remote (Phase 4 only).

    Args:
        config_path: Path to configuration file (optional)
        workspace_path: Path to workspace directory (optional)

    Returns:
        Phase 4 result
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

    print("\n🔄 #SYNC//. - Sync to Remote\n")
    print("=" * 60)

    # Execute Phase 4 only
    print("Syncing local commits to remote...")
    phase4_result = sync._phase4_sync_to_main()

    if not phase4_result.success:
        print(f"\n❌ {phase4_result.message}")

        # Check for specific error conditions
        if "conflict" in phase4_result.message.lower():
            print("\n⚠️  Conflict Resolution Steps:")
            print("  1. Run: git status")
            print("  2. Resolve conflicts manually")
            print("  3. Run: git add <resolved-files>")
            print("  4. Run: git rebase --continue")
            print("  5. Run: #SYNC//. again")

        print("=" * 60)
        return phase4_result

    print(f"\n✅ {phase4_result.message}")

    # Show sync details
    if phase4_result.details:
        if phase4_result.details.get('pulled'):
            print("  📥 Pulled changes from remote")
        if phase4_result.details.get('pushed'):
            print("  📤 Pushed local commits to remote")

    print("\n" + "=" * 60)
    print(f"⏱️  Sync completed in {phase4_result.duration_seconds:.2f}s")
    print("=" * 60)

    return phase4_result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sync to remote repository - Phase 4 of #321//.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Sync with default config
  %(prog)s --config custom.json  # Use custom configuration
  %(prog)s --workspace /path/to/repo  # Sync specific repository

This command syncs local commits to remote without staging or committing.
Assumes you have already committed changes (e.g., via #COMMIT//.).
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
        result = execute_sync(
            config_path=args.config,
            workspace_path=args.workspace
        )

        sys.exit(0 if result.success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Sync interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
