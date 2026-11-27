"""Command-line trigger for the Narrative River workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

from .storage import NarrativeRiverStore, load_delta_file, load_frame_file
from .workflow import NarrativeRiverWorkflow, SceneRunRequest


def _resolve_input_path(path: str | Path, allowed_root: Path) -> Path:
    try:
        source = Path(path).expanduser().resolve(strict=True)
        source.relative_to(allowed_root)
    except (OSError, ValueError) as exc:
        raise ValueError(
            f"input path {path} is outside allowed root {allowed_root}"
        ) from exc
    if not source.is_file():
        raise ValueError(f"input path is not a regular file: {source}")
    return source


def _resolve_workspace(path: str | Path, allowed_root: Path) -> Path:
    source = Path(path).expanduser()
    resolved = (
        (allowed_root / source).resolve()
        if not source.is_absolute()
        else source.resolve()
    )
    try:
        resolved.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError(
            f"workspace {path} is outside allowed root {allowed_root}"
        ) from exc
    return resolved


def _read_mapping(path: str | Path, allowed_root: Path) -> dict[str, Any]:
    source = _resolve_input_path(path, allowed_root)
    text = source.read_text(encoding="utf-8")
    payload = json.loads(text) if source.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{source} must contain a mapping at the document root")
    return payload


def _read_text(path: str | Path, allowed_root: Path) -> str:
    return _resolve_input_path(path, allowed_root).read_text(encoding="utf-8")


def _read_optional_text(path: str | None, allowed_root: Path) -> str:
    return "" if path is None else _read_text(path, allowed_root)


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _add_workspace(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workspace",
        default="narrative/river",
        help="Durable artifact root. Defaults to narrative/river.",
    )
    parser.add_argument(
        "--allowed-root",
        default=".",
        help="Filesystem root allowed for inputs and workflow artifacts.",
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


def _handle_build_frame(
    args: argparse.Namespace,
    workflow: NarrativeRiverWorkflow,
    _store: NarrativeRiverStore,
    allowed_root: Path,
) -> int:
    prior = (
        load_delta_file(args.prior_delta, allowed_root=allowed_root)
        if args.prior_delta
        else None
    )
    frame, path = workflow.build_and_store_frame(
        scene_request=_read_mapping(args.scene_request, allowed_root),
        canon_snapshot=_read_mapping(args.canon_snapshot, allowed_root),
        prior_delta=prior,
        auto_prior=not args.no_auto_prior,
    )
    _emit({"frame_id": frame.frame_id, "scene_id": frame.scene_id, "frame_path": str(path)})
    return 0


def _handle_render_prompt(
    args: argparse.Namespace,
    workflow: NarrativeRiverWorkflow,
    _store: NarrativeRiverStore,
    allowed_root: Path,
) -> int:
    frame = load_frame_file(args.frame, allowed_root=allowed_root)
    _prompt, path = workflow.render_and_store_prompt(
        frame,
        axioms_text=_read_optional_text(args.axioms, allowed_root),
    )
    _emit({"frame_id": frame.frame_id, "scene_id": frame.scene_id, "prompt_path": str(path)})
    return 0


def _handle_validate_draft(
    args: argparse.Namespace,
    workflow: NarrativeRiverWorkflow,
    _store: NarrativeRiverStore,
    allowed_root: Path,
) -> int:
    frame = load_frame_file(args.frame, allowed_root=allowed_root)
    report, path = workflow.validate_and_store_draft(
        frame,
        _read_text(args.draft, allowed_root),
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


def _handle_close_scene(
    args: argparse.Namespace,
    workflow: NarrativeRiverWorkflow,
    _store: NarrativeRiverStore,
    allowed_root: Path,
) -> int:
    frame = load_frame_file(args.frame, allowed_root=allowed_root)
    delta, path = workflow.close_scene(
        frame=frame,
        delta_payload=_read_mapping(args.delta, allowed_root),
    )
    _emit({"scene_id": delta.scene_id, "delta_path": str(path)})
    return 0


def _handle_run_scene(
    args: argparse.Namespace,
    workflow: NarrativeRiverWorkflow,
    _store: NarrativeRiverStore,
    allowed_root: Path,
) -> int:
    prior = (
        load_delta_file(args.prior_delta, allowed_root=allowed_root)
        if args.prior_delta
        else None
    )
    result = workflow.run_scene(
        SceneRunRequest(
            scene_request=_read_mapping(args.scene_request, allowed_root),
            canon_snapshot=_read_mapping(args.canon_snapshot, allowed_root),
            draft_text=_read_text(args.draft, allowed_root),
            delta_payload=_read_mapping(args.delta, allowed_root),
            axioms_text=_read_optional_text(args.axioms, allowed_root),
            prior_delta=prior,
            auto_prior=not args.no_auto_prior,
            fail_on_error=args.fail_on_error,
        )
    )
    _emit(result)
    return 3 if args.fail_on_error and result["validation_has_errors"] else 0


def _handle_status(
    _args: argparse.Namespace,
    _workflow: NarrativeRiverWorkflow,
    store: NarrativeRiverStore,
    _allowed_root: Path,
) -> int:
    _emit(store.load_manifest())
    return 0


_HANDLERS = {
    "build-frame": _handle_build_frame,
    "render-prompt": _handle_render_prompt,
    "validate-draft": _handle_validate_draft,
    "close-scene": _handle_close_scene,
    "run-scene": _handle_run_scene,
    "status": _handle_status,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        allowed_root = Path(args.allowed_root).expanduser().resolve(strict=True)
        store = NarrativeRiverStore(_resolve_workspace(args.workspace, allowed_root))
        workflow = NarrativeRiverWorkflow(store)
        return _HANDLERS[args.command](args, workflow, store, allowed_root)
    except (KeyError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"narrative-river: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
