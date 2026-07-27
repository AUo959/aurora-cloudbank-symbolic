"""Command-line trigger for the Narrative River workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml
from pydantic import ValidationError

from .storage import NarrativeRiverStore, load_delta_file, load_frame_file
from .workflow import NarrativeRiverWorkflow


def _read_mapping(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    payload = json.loads(text) if source.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{source} must contain a mapping at the document root")
    return payload


def _read_optional_text(path: str | None) -> str:
    return "" if path is None else Path(path).read_text(encoding="utf-8")


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _add_workspace(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workspace",
        default="narrative/river",
        help="Durable artifact root. Defaults to narrative/river.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="narrative-river",
        description="Explicit Narrative River scene-state workflow.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-frame", help="Build and persist a Narrative River Frame.")
    _add_workspace(build)
    build.add_argument("--scene-request", required=True)
    build.add_argument("--canon-snapshot", required=True)
    build.add_argument("--prior-delta")
    build.add_argument("--no-auto-prior", action="store_true")

    prompt = subparsers.add_parser("render-prompt", help="Render and persist a prose prompt packet.")
    _add_workspace(prompt)
    prompt.add_argument("--frame", required=True)
    prompt.add_argument("--axioms")

    validate = subparsers.add_parser("validate-draft", help="Validate a draft and persist an advisory report.")
    _add_workspace(validate)
    validate.add_argument("--frame", required=True)
    validate.add_argument("--draft", required=True)
    validate.add_argument("--fail-on-error", action="store_true")

    close = subparsers.add_parser("close-scene", help="Validate and persist the approved post-scene delta.")
    _add_workspace(close)
    close.add_argument("--frame", required=True)
    close.add_argument("--delta", required=True)

    run = subparsers.add_parser("run-scene", help="Run frame -> prompt -> validation -> delta in one command.")
    _add_workspace(run)
    run.add_argument("--scene-request", required=True)
    run.add_argument("--canon-snapshot", required=True)
    run.add_argument("--draft", required=True)
    run.add_argument("--delta", required=True)
    run.add_argument("--prior-delta")
    run.add_argument("--axioms")
    run.add_argument("--no-auto-prior", action="store_true")
    run.add_argument("--fail-on-error", action="store_true")

    status = subparsers.add_parser("status", help="Show the current durable scene-chain manifest.")
    _add_workspace(status)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = NarrativeRiverStore(args.workspace)
    workflow = NarrativeRiverWorkflow(store)

    try:
        if args.command == "build-frame":
            prior = load_delta_file(args.prior_delta) if args.prior_delta else None
            frame, path = workflow.build_and_store_frame(
                scene_request=_read_mapping(args.scene_request),
                canon_snapshot=_read_mapping(args.canon_snapshot),
                prior_delta=prior,
                auto_prior=not args.no_auto_prior,
            )
            _emit({"frame_id": frame.frame_id, "scene_id": frame.scene_id, "frame_path": str(path)})
            return 0

        if args.command == "render-prompt":
            frame = load_frame_file(args.frame)
            _prompt, path = workflow.render_and_store_prompt(frame, axioms_text=_read_optional_text(args.axioms))
            _emit({"frame_id": frame.frame_id, "scene_id": frame.scene_id, "prompt_path": str(path)})
            return 0

        if args.command == "validate-draft":
            frame = load_frame_file(args.frame)
            report, path = workflow.validate_and_store_draft(
                frame,
                Path(args.draft).read_text(encoding="utf-8"),
            )
            _emit(
                {
                    "frame_id": frame.frame_id,
                    "scene_id": frame.scene_id,
                    "validation_report_path": str(path),
                    "findings": len(report.findings),
                    "has_errors": report.has_errors,
                }
            )
            return 3 if args.fail_on_error and report.has_errors else 0

        if args.command == "close-scene":
            frame = load_frame_file(args.frame)
            delta, path = workflow.close_scene(frame=frame, delta_payload=_read_mapping(args.delta))
            _emit({"scene_id": delta.scene_id, "delta_path": str(path)})
            return 0

        if args.command == "run-scene":
            prior = load_delta_file(args.prior_delta) if args.prior_delta else None
            result = workflow.run_scene(
                scene_request=_read_mapping(args.scene_request),
                canon_snapshot=_read_mapping(args.canon_snapshot),
                draft_text=Path(args.draft).read_text(encoding="utf-8"),
                delta_payload=_read_mapping(args.delta),
                axioms_text=_read_optional_text(args.axioms),
                prior_delta=prior,
                auto_prior=not args.no_auto_prior,
                fail_on_error=args.fail_on_error,
            )
            _emit(result)
            return 3 if args.fail_on_error and result["validation_has_errors"] else 0

        if args.command == "status":
            _emit(store.load_manifest())
            return 0

        raise ValueError(f"unknown command: {args.command}")
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError, ValidationError) as exc:
        print(f"narrative-river: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
