"""
Insight Ledger CLI Commands

Command-line interface for managing the Insight Ledger.

Anchor: T1-TIL-004
"""

import json
import sys
from typing import Optional

from modules.insight_ledger.ledger_core import InsightLedger
from modules.insight_ledger.schemas import AuditQuery, InsightRecord, InsightType


def record_insight_cli(
    storage_path: str,
    insight_type: str,
    content: str,
    source: str,
    tags: Optional[str] = None,
    severity: str = "info",
    context: Optional[str] = None,
) -> None:
    """
    Record a new insight via CLI.

    Args:
        storage_path: Ledger storage directory
        insight_type: Type of insight (decision, analysis, alert, etc.)
        content: Insight content
        source: Source system
        tags: Comma-separated tags
        severity: Severity level (info, warning, error, critical)
        context: JSON string with context metadata
    """
    try:
        # Validate insight type
        try:
            itype = InsightType(insight_type)
        except ValueError:
            print(f"❌ Invalid insight type: {insight_type}")
            print(f"Valid types: {', '.join([t.value for t in InsightType])}")
            sys.exit(1)

        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        # Parse context
        context_dict = None
        if context:
            try:
                context_dict = json.loads(context)
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON context: {context}")
                sys.exit(1)

        # Create ledger and record
        ledger = InsightLedger(storage_path=storage_path)

        insight = InsightRecord(
            insight_type=itype,
            content=content,
            source=source,
            tags=tag_list,
            severity=severity,
            context=context_dict,
        )

        entry = ledger.record_insight(insight)

        print("✅ Insight recorded successfully")
        print(f"   Entry ID: {entry.entry_id}")
        print(f"   Hash: {entry.entry_hash[:16]}...")
        print(f"   Signature: {entry.signature[:16]}...")

    except Exception as e:
        print(f"❌ Failed to record insight: {e}")
        sys.exit(1)


def verify_integrity_cli(storage_path: str, limit: Optional[int] = None) -> None:
    """
    Verify ledger integrity via CLI.

    Args:
        storage_path: Ledger storage directory
        limit: Maximum entries to verify (None = all)
    """
    try:
        ledger = InsightLedger(storage_path=storage_path)

        print(f"🔍 Verifying ledger integrity...")
        if limit:
            print(f"   Checking last {limit} entries")

        report = ledger.verify_integrity(limit=limit)

        if report["chain_intact"]:
            print(f"✅ Ledger integrity verified")
            print(f"   Entries verified: {report['verified_entries']}/{report['total_entries']}")
            print(f"   Verification time: {report['verification_time_ms']:.1f}ms")
        else:
            print(f"❌ Integrity compromised!")
            print(f"   Verified: {report['verified_entries']}/{report['total_entries']}")
            print(f"   Failed entries: {len(report['failed_entries'])}")
            if report["errors"]:
                print("\n🔍 Errors:")
                for error in report["errors"][:10]:  # Show first 10 errors
                    print(f"   - {error}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        sys.exit(1)


def query_history_cli(
    storage_path: str,
    insight_type: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    format: str = "table",
) -> None:
    """
    Query ledger history via CLI.

    Args:
        storage_path: Ledger storage directory
        insight_type: Filter by insight type
        source: Filter by source
        tags: Filter by tags (comma-separated)
        search: Full-text search
        limit: Maximum results
        format: Output format (table, json, csv)
    """
    try:
        ledger = InsightLedger(storage_path=storage_path)

        # Build query
        query = AuditQuery(limit=limit)

        if insight_type:
            try:
                query.insight_types = [InsightType(insight_type)]
            except ValueError:
                print(f"❌ Invalid insight type: {insight_type}")
                sys.exit(1)

        if source:
            query.sources = [source]

        if tags:
            query.tags = [t.strip() for t in tags.split(",")]

        if search:
            query.search_text = search

        # Execute query
        entries = ledger.query_history(query)

        if format == "json":
            # JSON output
            output = [entry.model_dump() for entry in entries]
            print(json.dumps(output, indent=2, default=str))

        elif format == "csv":
            # CSV output
            print("entry_id,timestamp,type,source,content,severity")
            for entry in entries:
                content_escaped = entry.content.replace('"', '""')[:50]  # Truncate
                print(
                    f'"{entry.entry_id}","{entry.timestamp.isoformat()}",'
                    f'"{entry.insight_type}","{entry.source}",'
                    f'"{content_escaped}","{entry.severity}"'
                )

        else:
            # Table output (default)
            if not entries:
                print("No matching entries found.")
                return

            print(f"\n📊 Found {len(entries)} entries:\n")
            print(
                f"{'Entry ID':<30} {'Timestamp':<20} {'Type':<12} {'Source':<20} {'Content':<40}"
            )
            print("-" * 122)

            for entry in entries:
                content_short = (
                    entry.content[:37] + "..." if len(entry.content) > 40 else entry.content
                )
                timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"{entry.entry_id:<30} {timestamp_str:<20} "
                    f"{entry.insight_type.value:<12} {entry.source:<20} {content_short:<40}"
                )

    except Exception as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)


def get_stats_cli(storage_path: str) -> None:
    """
    Get ledger statistics via CLI.

    Args:
        storage_path: Ledger storage directory
    """
    try:
        ledger = InsightLedger(storage_path=storage_path)
        stats = ledger.get_stats()

        print(f"\n📊 Ledger Statistics\n")
        print(f"Total Entries:      {stats.total_entries}")
        print(f"First Entry:        {stats.first_entry_time.strftime('%Y-%m-%d %H:%M:%S') if stats.first_entry_time else 'N/A'}")
        print(f"Last Entry:         {stats.last_entry_time.strftime('%Y-%m-%d %H:%M:%S') if stats.last_entry_time else 'N/A'}")
        print(f"Integrity Verified: {'✅ Yes' if stats.integrity_verified else '❌ No'}")
        print(f"Storage Size:       {stats.ledger_size_bytes:,} bytes")

        if stats.entries_by_type:
            print(f"\n📈 Entries by Type:")
            for itype, count in sorted(stats.entries_by_type.items(), key=lambda x: -x[1]):
                print(f"   {itype:<15} {count:>6}")

        if stats.entries_by_source:
            print(f"\n🔍 Entries by Source:")
            for source, count in sorted(stats.entries_by_source.items(), key=lambda x: -x[1])[:10]:
                print(f"   {source:<30} {count:>6}")

    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
        sys.exit(1)


def export_ledger_cli(
    storage_path: str, output_path: str, include_genesis: bool = True
) -> None:
    """
    Export ledger to JSON file via CLI.

    Args:
        storage_path: Ledger storage directory
        output_path: Output file path
        include_genesis: Include genesis entry
    """
    try:
        ledger = InsightLedger(storage_path=storage_path)

        print(f"📤 Exporting ledger to {output_path}...")

        count = ledger.export_ledger(output_path, include_genesis=include_genesis)

        print(f"✅ Export completed successfully")
        print(f"   Entries exported: {count}")
        print(f"   Output file: {output_path}")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Insight Ledger CLI - Manage Aurora's cryptographic audit trail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record a decision
  %(prog)s record --type decision --content "Approved user request" --source auth-service

  # Verify integrity
  %(prog)s verify --storage ./data/insight_ledger

  # Query history
  %(prog)s query --type alert --source monitor-service --limit 50

  # Get statistics
  %(prog)s stats --storage ./data/insight_ledger

  # Export ledger
  %(prog)s export --output ./exports/ledger_backup.json
        """,
    )

    parser.add_argument(
        "--storage",
        default="./data/insight_ledger",
        help="Ledger storage directory (default: ./data/insight_ledger)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Record command
    record_parser = subparsers.add_parser("record", help="Record a new insight")
    record_parser.add_argument("--type", required=True, help="Insight type")
    record_parser.add_argument("--content", required=True, help="Insight content")
    record_parser.add_argument("--source", required=True, help="Source system")
    record_parser.add_argument("--tags", help="Comma-separated tags")
    record_parser.add_argument(
        "--severity", default="info", choices=["info", "warning", "error", "critical"]
    )
    record_parser.add_argument("--context", help="JSON context metadata")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify ledger integrity")
    verify_parser.add_argument("--limit", type=int, help="Max entries to verify")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query ledger history")
    query_parser.add_argument("--type", help="Filter by insight type")
    query_parser.add_argument("--source", help="Filter by source")
    query_parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    query_parser.add_argument("--search", help="Full-text search")
    query_parser.add_argument("--limit", type=int, default=100, help="Max results (default: 100)")
    query_parser.add_argument(
        "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )

    # Stats command
    subparsers.add_parser("stats", help="Get ledger statistics")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export ledger to JSON")
    export_parser.add_argument("--output", required=True, help="Output file path")
    export_parser.add_argument(
        "--no-genesis", action="store_true", help="Exclude genesis entry"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "record":
        record_insight_cli(
            args.storage,
            args.type,
            args.content,
            args.source,
            args.tags,
            args.severity,
            args.context,
        )
    elif args.command == "verify":
        verify_integrity_cli(args.storage, args.limit)
    elif args.command == "query":
        query_history_cli(
            args.storage, args.type, args.source, args.tags, args.search, args.limit, args.format
        )
    elif args.command == "stats":
        get_stats_cli(args.storage)
    elif args.command == "export":
        export_ledger_cli(args.storage, args.output, not args.no_genesis)


if __name__ == "__main__":
    main()
