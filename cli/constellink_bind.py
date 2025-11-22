"""CONSTELLINK CLI: constellink-bind

Command-line interface for binding threads into CONSTELLINK mesh artifacts.

Usage:
    python -m cli.constellink_bind [OPTIONS]

    Reads ConstellinkMeshRequest JSON from stdin or --input file,
    binds threads using ConstellinkRelay, and writes ConstellinkMesh
    JSON to stdout or --output file.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from symbolic.constellink import (
    ConstellinkRelay,
    mesh_request_from_dict,
    DEFAULT_ANCHOR_SEED,
    DEFAULT_ETHICS_PROTOCOL
)


CLI_VERSION = "1.0.0"


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entrypoint

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        prog="constellink-bind",
        description="Bind threads into a CONSTELLINK mesh artifact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From stdin to stdout
  cat request.json | python -m cli.constellink_bind

  # From file to file with pretty printing
  python -m cli.constellink_bind --input request.json --output mesh.json --pretty

  # With glyphcard summary to stderr
  python -m cli.constellink_bind --input request.json --glyphcard > mesh.json

  # Override anchor seed
  python -m cli.constellink_bind --anchor-seed CUSTOM_SEED < request.json
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        metavar='FILE',
        help='Input file with ConstellinkMeshRequest JSON (default: stdin)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        metavar='FILE',
        help='Output file for ConstellinkMesh JSON (default: stdout)'
    )

    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty-print JSON output with indentation'
    )

    parser.add_argument(
        '--glyphcard', '-g',
        action='store_true',
        help='Print human-readable glyphcard summary to stderr'
    )

    parser.add_argument(
        '--anchor-seed',
        type=str,
        metavar='SEED',
        help=f'Override default anchor seed (default: {DEFAULT_ANCHOR_SEED})'
    )

    parser.add_argument(
        '--ethics-protocol',
        type=str,
        metavar='PROTOCOL',
        help=f'Override default ethics protocol (default: {DEFAULT_ETHICS_PROTOCOL})'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'%(prog)s {CLI_VERSION}'
    )

    args = parser.parse_args(argv)

    try:
        # Read input
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        else:
            input_data = json.load(sys.stdin)

        # Parse request
        request = mesh_request_from_dict(input_data)

        # Apply CLI overrides to request if provided
        if args.anchor_seed:
            request.target_anchor_seed = args.anchor_seed

        # Create relay and bind
        relay = ConstellinkRelay()

        # Apply ethics protocol override if needed
        if args.ethics_protocol:
            relay.DEFAULT_ETHICS_PROTOCOL = args.ethics_protocol

        mesh = relay.bind(request)

        # Write output
        mesh_dict = mesh.to_dict()

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.pretty:
                    json.dump(mesh_dict, f, indent=2)
                else:
                    json.dump(mesh_dict, f)
        else:
            if args.pretty:
                json.dump(mesh_dict, sys.stdout, indent=2)
            else:
                json.dump(mesh_dict, sys.stdout)
            print()  # Add newline for terminal output

        # Print glyphcard if requested
        if args.glyphcard:
            print(mesh.glyphcard(), file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyError as e:
        print(f"Error: Missing required field in input: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
