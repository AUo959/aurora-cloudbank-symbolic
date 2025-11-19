#!/usr/bin/env python3
"""
Command Chain Dispatcher

Unified dispatcher for all command chain commands (#321//., #STATUS//., etc.)
Integrates with parser.py to execute commands by code.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Callable, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.command_chain.comprehensive_sync_321 import execute_321  # noqa: E402


# Lazy imports for related commands
def get_execute_status():
    """Lazy import for execute_status"""
    from tools.command_chain.cmd_status import execute_status
    return execute_status


def get_execute_commit():
    """Lazy import for execute_commit"""
    from tools.command_chain.cmd_commit import execute_commit
    return execute_commit


def get_execute_sync():
    """Lazy import for execute_sync"""
    from tools.command_chain.cmd_sync import execute_sync
    return execute_sync


# Command registry
COMMAND_HANDLERS: Dict[str, Callable] = {
    '321': execute_321,
    'STATUS': get_execute_status,
    'COMMIT': get_execute_commit,
    'SYNC': get_execute_sync,
}


def dispatch_command(
    command_code: str,
    config_path: Optional[str] = None,
    workspace_path: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Dispatch a command by code.

    Args:
        command_code: Command code (e.g., '321', 'STATUS', 'COMMIT', 'SYNC')
        config_path: Path to configuration file (optional)
        workspace_path: Path to workspace directory (optional)
        **kwargs: Additional arguments passed to command handler

    Returns:
        Command execution result

    Raises:
        ValueError: If command code is not registered
    """
    command_code = command_code.upper()

    if command_code not in COMMAND_HANDLERS:
        raise ValueError(
            f"Unknown command code: {command_code}\n"
            f"Available commands: {', '.join(sorted(COMMAND_HANDLERS.keys()))}"
        )

    handler = COMMAND_HANDLERS[command_code]

    # Resolve lazy imports
    if callable(handler) and handler.__name__.startswith('get_execute_'):
        handler = handler()

    # Execute command with common parameters
    return handler(
        config_path=config_path,
        workspace_path=workspace_path,
        **kwargs
    )


def register_command(command_code: str, handler: Callable):
    """
    Register a new command handler.

    Args:
        command_code: Command code (e.g., 'MYCOMMAND')
        handler: Callable that executes the command
    """
    COMMAND_HANDLERS[command_code.upper()] = handler


def list_commands() -> list:
    """Get list of registered command codes"""
    return sorted(COMMAND_HANDLERS.keys())


def main():
    """CLI entry point for dispatcher"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Command Chain Dispatcher - Execute commands by code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 321                # Execute #321//. (full sync)
  %(prog)s STATUS             # Execute #STATUS//. (status check)
  %(prog)s COMMIT             # Execute #COMMIT//. (stage & commit)
  %(prog)s SYNC               # Execute #SYNC//. (sync to remote)
  %(prog)s --list             # List available commands

Commands:
  321     - Comprehensive sync & validate (all 6 phases)
  STATUS  - Quick status check (phase 1 only)
  COMMIT  - Stage and commit (phases 1-3)
  SYNC    - Sync to remote (phase 4 only)
        """
    )

    parser.add_argument(
        'command',
        nargs='?',
        type=str,
        help='Command code to execute'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available commands'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--workspace',
        type=str,
        help='Path to workspace directory'
    )

    args = parser.parse_args()

    # List commands if requested
    if args.list:
        print("Available commands:")
        for cmd in list_commands():
            print(f"  {cmd}")
        sys.exit(0)

    # Require command if not listing
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Dispatch command
        result = dispatch_command(
            args.command,
            config_path=args.config,
            workspace_path=args.workspace
        )

        # Determine success
        if hasattr(result, 'success'):
            sys.exit(0 if result.success else 1)
        else:
            sys.exit(0)

    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Command interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
