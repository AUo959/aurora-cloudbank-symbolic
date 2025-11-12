#!/usr/bin/env python3
"""
Command Chain CLI
=================
Anchor: CMD-CHAIN-CLI-001
Team: AUo959-team
Ethics: Picard_Delta_3

Command-line interface for parsing and executing command chains.
"""

import logging

logger = logging.getLogger(__name__)

import argparse
import sys
from pathlib import Path

from tools.command_chain.parser import CommandChainParser

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def cmd_parse(args):
    """Parse command chain and show results"""
    parser = CommandChainParser()
    result = parser.parse(args.input)
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Command Chain Parse Results                             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Input: {result.raw_input}")
    print()
    
    if result.commands:
        logger.info("Valid Commands: {len(result.commands)}")
        for cmd in result.commands:
            status = "✓" if cmd.is_valid else "✗"
            print(f"   {status} {cmd.raw} → {cmd.name}")
            if cmd.error_message:
                print(f"      Error: {cmd.error_message}")
        print()
    
    if result.naked_commands:
        logger.warning("Naked Commands Detected: {len(result.naked_commands)}")
        print()
        for cmd in result.naked_commands:
            print(cmd.error_message)
            print()
    
    if not result.commands and not result.naked_commands:
        print("ℹ️  No commands detected in input")
    
    # Generate command chain hash for DLP tracking
    if result.commands:
        valid_cmds = [c.name for c in result.commands if c.is_valid]
        if valid_cmds:
            cmd_hash = parser.generate_command_hash(valid_cmds)
            print(f"📊 Command Chain Hash (DLP): {cmd_hash[:16]}...")
            print(f"   Full Hash: {cmd_hash}")
    
    # Exit with error code if there are issues
    return 1 if result.has_errors else 0


def cmd_validate(args):
    """Validate command chain syntax"""
    parser = CommandChainParser()
    is_valid, errors = parser.validate_command_chain(args.input)
    
    if is_valid:
        logger.info("Command chain is valid!")
        valid_cmds = parser.extract_valid_commands(args.input)
        if valid_cmds:
            print(f"   Commands: {', '.join(valid_cmds)}")
        return 0
    else:
        logger.error("Command chain has errors:")
        for error in errors:
            print(error)
        return 1


def cmd_list(args):
    """List supported commands"""
    parser = CommandChainParser()
    commands = parser.get_supported_commands()
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Supported Commands                                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Total: {len(commands)} commands")
    print()
    
    for cmd in commands:
        print(f"  • #{cmd}//.")
    
    print()
    print("💡 Usage: #{command}//.")
    logger.warning("Commands without //. terminator will NOT execute")
    
    return 0


def cmd_format(args):
    """Format command list as proper chain"""
    parser = CommandChainParser()
    commands = args.commands
    
    # Validate commands
    invalid = [c for c in commands if c not in parser.SUPPORTED_COMMANDS]
    if invalid:
        logger.error("Unknown commands: {", '.join(invalid)}")
        print()
        print("Supported commands:")
        for cmd in sorted(parser.SUPPORTED_COMMANDS):
            print(f"  • {cmd}")
        return 1
    
    # Format as command chain
    chain = parser.format_command_chain(commands)
    cmd_hash = parser.generate_command_hash(commands)
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Formatted Command Chain                                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Chain: {chain}")
    print()
    print(f"Hash: {cmd_hash[:16]}...")
    print(f"Full: {cmd_hash}")
    
    return 0


def cmd_demo(args):
    """Run demonstration"""
    from tools.command_chain.parser import demo
    demo()
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Command Chain Parser - Safe command execution with //. terminator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse command chain
  %(prog)s parse "Please #seal//. and #verify//."
  
  # Detect naked commands
  %(prog)s parse "Run #deploy without terminator"
  
  # Validate syntax
  %(prog)s validate "#seal//. #verify//. #deploy//."
  
  # List supported commands
  %(prog)s list
  
  # Format command chain
  %(prog)s format seal verify deploy
  
  # Run demonstration
  %(prog)s demo

Command Syntax:
  ✅ Valid:   #command//.
  ❌ Invalid: #command (missing terminator)
  
Safety:
  Commands without //. terminator are NEVER executed.
  System provides helpful guidance for malformed commands.
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse command chain')
    parse_parser.add_argument('input', help='Input text containing commands')
    parse_parser.set_defaults(func=cmd_parse)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate command syntax')
    validate_parser.add_argument('input', help='Command chain to validate')
    validate_parser.set_defaults(func=cmd_validate)
    
    # List commands
    list_parser = subparsers.add_parser('list', help='List supported commands')
    list_parser.set_defaults(func=cmd_list)
    
    # Format command chain
    format_parser = subparsers.add_parser('format', help='Format command chain')
    format_parser.add_argument('commands', nargs='+', help='Command names to format')
    format_parser.set_defaults(func=cmd_format)
    
    # Demo
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.set_defaults(func=cmd_demo)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
