"""
T1-EDG-CLI - Data Guardian CLI Commands
Ethical Data Guardian command-line interface for PII scanning and redaction.

Chain: #005//002/EDG
Anchor: T1-EDG-CLI-001
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from .detection_rules import PIIDetector
    from .redaction import RedactionEngine, RedactionStrategy
except ImportError:
    from detection_rules import PIIDetector
    from redaction import RedactionEngine, RedactionStrategy


class DataGuardianCLI:
    """Command-line interface for Data Guardian operations."""

    def __init__(self, region: str = "US"):
        """Initialize CLI with detector and redactor."""
        self.region = region
        self.detector = PIIDetector(region=region)
        self.redactor = RedactionEngine()

    def scan_file(
        self,
        file_path: str,
        confidence_threshold: float = 0.7,
        region: str = "US",
        output_format: str = "text",
    ) -> Dict[str, Any]:
        """
        Scan a file for PII.

        Args:
            file_path: Path to file to scan
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            region: Region for detection rules (US, EU, UK, CA, AU)
            output_format: Output format (text, json)

        Returns:
            Dict with scan results
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"error": f"File is not valid UTF-8: {file_path}"}

        # Detect PII
        detections = self.detector.detect(content, confidence_threshold)

        # Format output
        if output_format == "json":
            return {
                "file": str(path),
                "total_detections": len(detections),
                "detections": [
                    {
                        "type": d['type'],
                        "value": d['match'],
                        "confidence": d['confidence'],
                        "region": d.get('region'),
                        "location": {"start": d['start'], "end": d['end']} if d.get('start') is not None else None,
                    }
                    for d in detections
                ],
            }
        else:
            # Text output
            result = {
                "file": str(path),
                "total_detections": len(detections),
                "summary": self._format_text_summary(detections),
            }
            return result

    def redact_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        strategy: str = "mask",
        confidence_threshold: float = 0.7,
        region: str = "US",
        in_place: bool = False,
    ) -> Dict[str, Any]:
        """
        Redact PII from a file.

        Args:
            file_path: Path to file to redact
            output_path: Path to write redacted file (optional)
            strategy: Redaction strategy (mask, hash, remove, partial, token, synthetic)
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            region: Region for detection rules
            in_place: Modify file in place (overwrite original)

        Returns:
            Dict with redaction results
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"error": f"File is not valid UTF-8: {file_path}"}

        # Parse strategy
        try:
            redaction_strategy = RedactionStrategy[strategy.upper()]
        except KeyError:
            return {"error": f"Invalid strategy: {strategy}. Valid: mask, hash, remove, partial, token, synthetic"}

        # Detect PII
        detections = self.detector.detect(content, confidence_threshold)

        if not detections:
            return {
                "file": str(path),
                "total_redactions": 0,
                "message": "No PII detected",
            }

        # Redact content
        redacted_content = self.redactor.redact_text(content, detections, redaction_strategy)

        # Determine output path
        if in_place:
            out_path = path
        elif output_path:
            out_path = Path(output_path)
        else:
            # Default: add .redacted suffix
            out_path = path.with_suffix(f".redacted{path.suffix}")

        # Write redacted content
        out_path.write_text(redacted_content, encoding="utf-8")

        # Get audit trail
        audit = self.redactor.get_audit_trail()

        return {
            "file": str(path),
            "output_file": str(out_path),
            "total_redactions": len(detections),
            "strategy": strategy,
            "audit_entries": len(audit),
        }

    def scan_stdin(
        self,
        confidence_threshold: float = 0.7,
        region: str = "US",
        output_format: str = "text",
    ) -> Dict[str, Any]:
        """
        Scan stdin for PII.

        Args:
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            region: Region for detection rules
            output_format: Output format (text, json)

        Returns:
            Dict with scan results
        """
        content = sys.stdin.read()

        # Detect PII
        detections = self.detector.detect(content, confidence_threshold)

        # Format output
        if output_format == "json":
            return {
                "source": "stdin",
                "total_detections": len(detections),
                "detections": [
                    {
                        "type": d['type'],
                        "value": d['match'],
                        "confidence": d['confidence'],
                        "region": d.get('region'),
                        "location": {"start": d['start'], "end": d['end']} if d.get('start') is not None else None,
                    }
                    for d in detections
                ],
            }
        else:
            return {
                "source": "stdin",
                "total_detections": len(detections),
                "summary": self._format_text_summary(detections),
            }

    def redact_stdin(
        self,
        strategy: str = "mask",
        confidence_threshold: float = 0.7,
        region: str = "US",
    ) -> Dict[str, Any]:
        """
        Redact PII from stdin and output to stdout.

        Args:
            strategy: Redaction strategy (mask, hash, remove, partial, token, synthetic)
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            region: Region for detection rules

        Returns:
            Dict with redaction results (metadata written to stderr, redacted content to stdout)
        """
        content = sys.stdin.read()

        # Parse strategy
        try:
            redaction_strategy = RedactionStrategy[strategy.upper()]
        except KeyError:
            return {"error": f"Invalid strategy: {strategy}. Valid: mask, hash, remove, partial, token, synthetic"}

        # Detect PII
        detections = self.detector.detect(content, confidence_threshold)

        if not detections:
            # No PII, output original
            print(content, file=sys.stdout, end="")
            return {
                "source": "stdin",
                "total_redactions": 0,
                "message": "No PII detected",
            }

        # Redact content
        redacted_content = self.redactor.redact_text(content, detections, redaction_strategy)

        # Output redacted content to stdout
        print(redacted_content, file=sys.stdout, end="")

        # Return metadata (will be written to stderr by caller)
        audit = self.redactor.get_audit_trail()
        return {
            "source": "stdin",
            "total_redactions": len(detections),
            "strategy": strategy,
            "audit_entries": len(audit),
        }

    def list_strategies(self) -> Dict[str, Any]:
        """
        List available redaction strategies.

        Returns:
            Dict with strategy information
        """
        strategies = {
            "MASK": "Replace with asterisks (structure-preserving)",
            "HASH": "Replace with SHA256 hash (deterministic)",
            "REMOVE": "Remove completely",
            "PARTIAL": "Show first and last characters only",
            "TOKEN": "Replace with numbered token placeholders",
            "SYNTHETIC": "Replace with fake but realistic data",
        }

        return {
            "strategies": [{"name": name, "description": desc} for name, desc in strategies.items()],
            "default": "MASK",
        }

    def list_pii_types(self) -> Dict[str, Any]:
        """
        List detectable PII types.

        Returns:
            Dict with PII type information
        """
        types = {
            "EMAIL": "Email addresses (RFC 5322)",
            "PHONE": "Phone numbers (multiple formats)",
            "SSN": "US Social Security Numbers (XXX-XX-XXXX)",
            "CREDIT_CARD": "Credit card numbers (16-digit)",
            "IP_ADDRESS": "IPv4 addresses",
            "DATE_OF_BIRTH": "Dates of birth (multiple formats)",
            "PASSPORT": "Passport numbers",
            "DRIVER_LICENSE": "Driver's license numbers",
            "ADDRESS": "Physical addresses",
            "NAME": "Person names",
            "ACCOUNT_NUMBER": "Bank account numbers",
            "OTHER": "Other sensitive data",
        }

        return {
            "pii_types": [{"type": name, "description": desc} for name, desc in types.items()],
            "total": len(types),
        }

    def _format_text_summary(self, detections) -> str:
        """Format detections as human-readable text summary."""
        if not detections:
            return "No PII detected"

        # Group by type
        by_type = {}
        for d in detections:
            type_name = d['type']
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(d)

        lines = []
        for pii_type, items in sorted(by_type.items()):
            lines.append(f"  {pii_type}: {len(items)} detection(s)")
            for item in items[:3]:  # Show first 3
                lines.append(f"    - {item['match'][:50]}... (confidence: {item['confidence']:.2f})")
            if len(items) > 3:
                lines.append(f"    ... and {len(items) - 3} more")

        return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="aurora-data",
        description="Aurora Data Guardian - PII detection and redaction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for PII")
    scan_parser.add_argument("file", nargs="?", help="File to scan (omit for stdin)")
    scan_parser.add_argument("--confidence", type=float, default=0.7, help="Confidence threshold (0.0-1.0)")
    scan_parser.add_argument("--region", default="US", help="Region (US, EU, UK, CA, AU)")
    scan_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    # Redact command
    redact_parser = subparsers.add_parser("redact", help="Redact PII")
    redact_parser.add_argument("file", nargs="?", help="File to redact (omit for stdin)")
    redact_parser.add_argument("--output", "-o", help="Output file (default: <file>.redacted<ext>)")
    redact_parser.add_argument(
        "--strategy",
        "-s",
        default="mask",
        choices=["mask", "hash", "remove", "partial", "token", "synthetic"],
        help="Redaction strategy",
    )
    redact_parser.add_argument("--confidence", type=float, default=0.7, help="Confidence threshold (0.0-1.0)")
    redact_parser.add_argument("--region", default="US", help="Region (US, EU, UK, CA, AU)")
    redact_parser.add_argument("--in-place", action="store_true", help="Modify file in place")

    # List strategies
    subparsers.add_parser("strategies", help="List redaction strategies")

    # List PII types
    subparsers.add_parser("pii-types", help="List detectable PII types")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = DataGuardianCLI()

    try:
        if args.command == "scan":
            if args.file:
                result = cli.scan_file(args.file, args.confidence, args.region, args.format)
            else:
                result = cli.scan_stdin(args.confidence, args.region, args.format)

            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1

            if args.format == "json":
                print(json.dumps(result, indent=2))
            else:
                print(f"File: {result.get('file', result.get('source'))}")
                print(f"Total detections: {result['total_detections']}")
                if result['total_detections'] > 0:
                    print("\nDetections by type:")
                    print(result['summary'])

        elif args.command == "redact":
            if args.file:
                result = cli.redact_file(
                    args.file,
                    args.output,
                    args.strategy,
                    args.confidence,
                    args.region,
                    args.in_place,
                )
            else:
                result = cli.redact_stdin(args.strategy, args.confidence, args.region)

            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1

            # For stdin, metadata goes to stderr
            if not args.file:
                print(
                    f"[Data Guardian: {result['total_redactions']} redaction(s) applied]",
                    file=sys.stderr,
                )
            else:
                print(f"File: {result['file']}")
                print(f"Output: {result['output_file']}")
                print(f"Total redactions: {result['total_redactions']}")
                print(f"Strategy: {result['strategy']}")
                print(f"Audit entries: {result['audit_entries']}")

        elif args.command == "strategies":
            result = cli.list_strategies()
            print("Available Redaction Strategies:")
            print("=" * 60)
            for strategy in result["strategies"]:
                print(f"  {strategy['name']:12} - {strategy['description']}")
            print(f"\nDefault: {result['default']}")

        elif args.command == "pii-types":
            result = cli.list_pii_types()
            print("Detectable PII Types:")
            print("=" * 60)
            for pii_type in result["pii_types"]:
                print(f"  {pii_type['type']:18} - {pii_type['description']}")
            print(f"\nTotal: {result['total']} types")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
