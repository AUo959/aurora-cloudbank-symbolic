#!/usr/bin/env python3
"""
ORACULITH Forecast CLI

Command-line interface for generating symbolic forecasts from CONSTELLINK meshes.

Usage:
    python -m cli.oraculith_forecast < context.json
    python -m cli.oraculith_forecast --input context.json --output forecast.json
    python -m cli.oraculith_forecast --mesh mesh.json --output forecast.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add symbolic to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from symbolic.oraculith import (  # noqa: E402
    OraculithEngine,
    forecast_context_from_dict,
    DEFAULT_ANCHOR_SEED,
    DEFAULT_ETHICS_PROTOCOL
)


CLI_VERSION = "1.0.0"


def load_json_input(input_path: Optional[str] = None) -> dict:
    """
    Load JSON input from file or stdin.

    Args:
        input_path: Path to input file, or None for stdin

    Returns:
        Parsed JSON dictionary
    """
    if input_path:
        with open(input_path, 'r') as f:
            return json.load(f)
    else:
        # Read from stdin
        return json.load(sys.stdin)


def write_json_output(data: dict, output_path: Optional[str] = None, pretty: bool = False):
    """
    Write JSON output to file or stdout.

    Args:
        data: Dictionary to write
        output_path: Path to output file, or None for stdout
        pretty: Whether to pretty-print JSON
    """
    if pretty:
        json_str = json.dumps(data, indent=2, sort_keys=False)
    else:
        json_str = json.dumps(data, separators=(',', ':'))

    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_str)
            f.write('\n')
    else:
        print(json_str)


def create_minimal_context_from_mesh(
    mesh_data: dict,
    request_id: Optional[str] = None
) -> dict:
    """
    Create a minimal OraculithForecastContext from a mesh.

    Args:
        mesh_data: Dictionary representation of ConstellinkMesh
        request_id: Optional request identifier

    Returns:
        Dictionary representing OraculithForecastContext
    """
    import uuid

    if request_id is None:
        request_id = f"cli_request_{uuid.uuid4().hex[:12]}"

    return {
        "request_id": request_id,
        "mesh": mesh_data
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ORACULITH Symbolic Forecast Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate forecast from full context JSON via stdin
  python -m cli.oraculith_forecast < context.json

  # Generate forecast from context file
  python -m cli.oraculith_forecast --input context.json --output forecast.json

  # Generate forecast from mesh-only JSON (auto-wraps in minimal context)
  python -m cli.oraculith_forecast --mesh mesh.json --output forecast.json --pretty

  # Display glyphcard to stderr
  python -m cli.oraculith_forecast --mesh mesh.json --glyphcard > forecast.json

  # Override anchor seed and ethics protocol
  python -m cli.oraculith_forecast --mesh mesh.json --anchor-seed CUSTOM_SEED --ethics-protocol Protocol_Alpha
        """
    )

    parser.add_argument(
        '--input',
        '-i',
        help='Input file with OraculithForecastContext JSON (default: stdin)'
    )
    parser.add_argument(
        '--mesh',
        '-m',
        help='Input file with ConstellinkMesh JSON (creates minimal context)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file for SymbolicForecast JSON (default: stdout)'
    )
    parser.add_argument(
        '--pretty',
        '-p',
        action='store_true',
        help='Pretty-print JSON output'
    )
    parser.add_argument(
        '--glyphcard',
        '-g',
        action='store_true',
        help='Print human-readable glyphcard to stderr'
    )
    parser.add_argument(
        '--anchor-seed',
        default=DEFAULT_ANCHOR_SEED,
        help=f'Override anchor seed (default: {DEFAULT_ANCHOR_SEED})'
    )
    parser.add_argument(
        '--ethics-protocol',
        default=DEFAULT_ETHICS_PROTOCOL,
        help=f'Override ethics protocol (default: {DEFAULT_ETHICS_PROTOCOL})'
    )
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f'ORACULITH CLI v{CLI_VERSION}'
    )

    args = parser.parse_args()

    # Validate input options
    if args.input and args.mesh:
        parser.error("Cannot specify both --input and --mesh")

    try:
        # Load input
        if args.mesh:
            # Load mesh and wrap in minimal context
            mesh_data = load_json_input(args.mesh)
            context_data = create_minimal_context_from_mesh(mesh_data)
        elif args.input:
            # Load full context from file
            context_data = load_json_input(args.input)
        else:
            # Load from stdin (could be context or mesh)
            input_data = load_json_input()

            # Auto-detect: if it has 'request_id' and 'mesh', it's a context
            if 'request_id' in input_data and 'mesh' in input_data:
                context_data = input_data
            elif 'mesh_id' in input_data:
                # Looks like a mesh, wrap it
                context_data = create_minimal_context_from_mesh(input_data)
            else:
                # Assume it's a full context
                context_data = input_data

        # Build context
        context = forecast_context_from_dict(context_data, validate_mesh=True)

        # Create engine with custom anchors
        engine = OraculithEngine(
            anchor_seed=args.anchor_seed,
            ethics_protocol=args.ethics_protocol
        )

        # Generate forecast
        forecast = engine.forecast(context)

        # Write output
        write_json_output(forecast.to_dict(), args.output, args.pretty)

        # Print glyphcard if requested
        if args.glyphcard:
            print(forecast.glyphcard(), file=sys.stderr)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
