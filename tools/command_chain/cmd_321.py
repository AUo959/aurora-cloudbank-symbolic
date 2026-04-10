#!/usr/bin/env python3
"""
#321//. Command Line Interface
==============================
Anchor: CMD-CHAIN-CLI-321
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

CLI wrapper for executing #321//. - Comprehensive Sync & Validate

Usage:
    ./cmd_321.py                          # Use default config
    ./cmd_321.py --config custom.json     # Use custom config
    ./cmd_321.py --init-config            # Create config file
    ./cmd_321.py --dry-run                # Show what would happen
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.command_chain.comprehensive_sync_321 import (  # noqa: E402
    SyncConfig,
    execute_321,
    resolve_config_path,
)


def init_config(config_path: Path):
    """Initialize a new configuration file"""
    config = SyncConfig()
    config.save(config_path)
    print(f"✅ Created configuration file: {config_path}")
    print(f"\nEdit {config_path} to customize behavior:")
    print("  • commit_message_template - Customize commit format")
    print("  • validation_level - Choose: fast, thorough, complete")
    print("  • skip_validation_on_docs_only - Skip tests for doc changes")
    print("  • performance_target_seconds - Set speed goals")
    print("  • And more...")
    return 0


def dry_run(config_path: Optional[Path] = None):
    """Show what #321//. would do without executing"""
    config = SyncConfig.load(config_path)

    print("━" * 60)
    print("🔍 DRY RUN - #321//. Execution Plan")
    print("━" * 60)
    print()

    print("📋 Configuration:")
    print(f"  Validation Level: {config.validation_level}")
    print(f"  Commit Template: {config.commit_message_template}")
    print(f"  Use Rebase: {config.use_rebase}")
    print(f"  Auto Push: {config.auto_push}")
    print(f"  Performance Target: {config.performance_target_seconds}s")
    print(f"  Skip Docs-Only Validation: {config.skip_validation_on_docs_only}")
    print()

    print("🎯 Execution Plan:")
    print("  Phase 1: Check for pending changes")
    print("  Phase 2: Stage files intelligently by category")
    print("  Phase 3: Generate semantic commit message")
    print("  Phase 4: Sync to main (pull + push)")
    print("  Phase 5: Run quick validation checks")
    print("  Phase 6: Verify performance metrics")
    print()

    print("📝 Staging Priority:")
    for i, pattern in enumerate(config.auto_stage_patterns, 1):
        print(f"  {i}. {pattern}")
    print()

    print("✅ Validation Commands:")
    print(f"  Lint: {config.lint_command}")
    print(f"  Test: {config.test_command}")
    print()

    print("━" * 60)
    print("Run without --dry-run to execute")
    print("━" * 60)

    return 0


def show_config(config_path: Optional[Path] = None):
    """Display current configuration"""
    config = SyncConfig.load(config_path)

    print("━" * 60)
    print("⚙️  Current #321//. Configuration")
    print("━" * 60)
    print()

    print(json.dumps(config.__dict__, indent=2))
    print()

    if config_path:
        print(f"📄 Loaded from: {config_path}")
    else:
        print("📄 Using default configuration")
    print()

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="#321//. - Comprehensive Sync & Validate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Execute with defaults
  %(prog)s --config .aurora/sync_config.json  # Use custom config
  %(prog)s --init-config ~/.aurora/sync.json  # Create config file
  %(prog)s --dry-run                          # Preview execution
  %(prog)s --show-config                      # Display current config

Configuration File:
  Create ~/.aurora/sync_config.json or .aurora/sync_config.json
  to customize behavior. Use --init-config to generate template.

Philosophy:
  Reliable, fast, elegant - clean your working tree anytime with
  consistent high quality and minimal cognitive overhead.
        """
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to JSON configuration file'
    )

    parser.add_argument(
        '--init-config',
        type=str,
        metavar='PATH',
        help='Create a new configuration file with defaults'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show execution plan without running'
    )

    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Display current configuration'
    )

    parser.add_argument(
        '--workspace', '-w',
        type=str,
        help='Workspace directory (default: current directory)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    # Handle init-config
    if args.init_config:
        config_path = Path(args.init_config)
        return init_config(config_path)

    # Determine config path
    config_path = resolve_config_path(args.config, args.workspace)
    if args.config:
        if not config_path.exists():
            print(f"❌ Config file not found: {config_path}")
            return 1
    elif config_path:
        print(f"📄 Using config: {config_path}")

    # Handle show-config
    if args.show_config:
        return show_config(config_path)

    # Handle dry-run
    if args.dry_run:
        return dry_run(config_path)

    # Execute #321//.
    print("🚀 Executing #321//. - Comprehensive Sync & Validate")
    print()

    try:
        result = execute_321(
            config_path=str(config_path) if config_path else None,
            workspace_path=args.workspace
        )
        return 0 if result.success else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        return 130

    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
