#!/usr/bin/env python3
"""Automatic selective-integration gate for ingest-style commits."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_builder() -> Path:
    return Path.home() / ".codex" / "skills" / "aurora-selective-integration" / "scripts" / "build_selective_integration_capsule.py"


def parse_args() -> argparse.Namespace:
    root = repo_root()
    parser = argparse.ArgumentParser(
        description="Run Aurora selective integration capsule generation when ingest manifests are staged."
    )
    parser.add_argument(
        "--builder",
        default=os.environ.get("AURORA_SI_BUILDER", str(default_builder())),
        help="Path to build_selective_integration_capsule.py",
    )
    parser.add_argument(
        "--protocol-json",
        default=str(root / "manifests" / "selective_integration" / "Aurora_SelectiveIntegrationProtocol_v2.5_VIEW.json"),
        help="Protocol JSON path",
    )
    parser.add_argument(
        "--modules-json",
        default=str(root / "manifests" / "selective_integration" / "modules_manifest.json"),
        help="Module manifest JSON path",
    )
    parser.add_argument(
        "--triage-json",
        default=str(root / "manifests" / "selective_integration" / "triage_overrides.json"),
        help="Optional triage override JSON path",
    )
    parser.add_argument(
        "--source-json",
        default=str(root / "manifests" / "selective_integration" / "source.json"),
        help="Optional source metadata JSON path",
    )
    parser.add_argument(
        "--out-dir",
        default=str(root / "workflow_output" / "selective_integration"),
        help="Output directory for generated capsule/report",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run gate even if no selective-integration files are staged",
    )
    parser.add_argument(
        "--no-fail-on-reject",
        action="store_true",
        help="Do not fail when generated capsule contains rejected modules",
    )
    return parser.parse_args()


def staged_files(root: Path) -> list[str]:
    cmd = ["git", "-C", str(root), "diff", "--cached", "--name-only"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def should_run(staged: list[str]) -> bool:
    if not staged:
        return False
    for path in staged:
        lower = path.lower()
        if "selective_integration" in lower and lower.endswith(".json"):
            return True
        if lower.endswith(".zip") and ("ingest" in lower or "integration" in lower):
            return True
    return False


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    args = parse_args()
    root = repo_root()
    staged = staged_files(root)
    run_gate = args.force or should_run(staged)

    if not run_gate:
        print("[selective-ingest-gate] Skip: no selective integration ingest files staged.")
        return 0

    builder = Path(args.builder).expanduser().resolve()
    protocol_json = Path(args.protocol_json).expanduser().resolve()
    modules_json = Path(args.modules_json).expanduser().resolve()
    triage_json = Path(args.triage_json).expanduser().resolve()
    source_json = Path(args.source_json).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not builder.exists():
        print(f"[selective-ingest-gate] ERROR: builder not found: {builder}", file=sys.stderr)
        print("[selective-ingest-gate] Install/verify ~/.codex/skills/aurora-selective-integration.", file=sys.stderr)
        return 1
    if not protocol_json.exists():
        print(f"[selective-ingest-gate] ERROR: protocol JSON not found: {protocol_json}", file=sys.stderr)
        return 1
    if not modules_json.exists():
        print(f"[selective-ingest-gate] ERROR: modules JSON not found: {modules_json}", file=sys.stderr)
        return 1

    stamp = utc_stamp()
    out_json = out_dir / f"capsule_{stamp}.json"
    out_md = out_dir / f"report_{stamp}.md"
    latest_json = out_dir / "latest_capsule.json"
    latest_md = out_dir / "latest_report.md"

    cmd = [
        sys.executable,
        str(builder),
        "--protocol-json",
        str(protocol_json),
        "--modules-json",
        str(modules_json),
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    if source_json.exists():
        cmd.extend(["--source-json", str(source_json)])
    else:
        source_name = modules_json.stem
        source_type = "manifest"
        source_uri = f"repo:{modules_json.relative_to(root)}"
        cmd.extend(
            [
                "--source-name",
                source_name,
                "--source-type",
                source_type,
                "--source-uri",
                source_uri,
            ]
        )
    if triage_json.exists():
        cmd.extend(["--triage-json", str(triage_json)])
    if not args.no_fail_on_reject:
        cmd.append("--fail-on-reject")

    print("[selective-ingest-gate] Running:", " ".join(cmd))
    run = subprocess.run(cmd, check=False)
    if run.returncode not in {0, 2}:
        print(f"[selective-ingest-gate] ERROR: capsule generation failed with exit {run.returncode}", file=sys.stderr)
        return run.returncode
    if run.returncode == 2 and not args.no_fail_on_reject:
        print("[selective-ingest-gate] ERROR: rejected modules detected (fail-on-reject active).", file=sys.stderr)
        return 2

    latest_json.write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
    latest_md.write_text(out_md.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[selective-ingest-gate] Capsule written: {out_json}")
    print(f"[selective-ingest-gate] Report written: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
