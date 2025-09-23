# Aurora CLI – Anchor Tracking & Manifests

This guide explains how to use the Aurora Developer CLI for anchor tracking, lineage, drift checks, and manifest export.

## Quick reference

- Filter by file extension(s): repeat `--ext .py --ext .md`
- Filter by substring in anchor ID or context: `--pattern INFRA`
- Scan only files modified since a date/time: `--since 2025-09-01` or `--since 2025-09-01T00:00:00`
- Machine-readable output: `--json`

## Examples

- Track anchors with filters and JSON output:
  - `python tools/cli/aurora_dev_cli.py anchor track --ext .md --pattern INFRA --since 2025-09-01 --json`

- Resolve a specific anchor (after scanning with since cutoff):
  - `python tools/cli/aurora_dev_cli.py anchor resolve T70_DOC_REORG --since 2025-09-01`

- Generate a manifest (repository-wide) with since filter:
  - `python tools/cli/aurora_dev_cli.py manifest --json --since 2025-09-01T00:00:00`

- Generate a DLP manifest alongside the main manifest (when available):
  - `python tools/cli/aurora_dev_cli.py manifest --json --output out.json --dlp-manifest-out dlp.json`

- Status with JSON for CI pipelines:
  - `python tools/cli/aurora_dev_cli.py status --json --since 2025-09-15`

## Notes

- `--since` uses file modification time (mtime). If reading a file's metadata fails, it is skipped (scan continues).
- `--pattern` is a case-insensitive substring match across both anchor ID and the line context.
- In `--json` mode, the CLI prints only JSON to stdout to keep it parseable.
