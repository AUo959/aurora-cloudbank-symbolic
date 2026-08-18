#!/usr/bin/env python3
"""Public CLI and schema boundary for deterministic Phase-1 corpus archaeology.

The public entry point owns structural input validation and filesystem output policy.
Pure semantic analysis lives in ``corpus_archaeology_core`` so custody, authority,
and reporting responsibilities remain independently reviewable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import jsonschema

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tools.salvage.corpus_archaeology_core import (  # noqa: E402
    RANKING_WEIGHTS,
    SCHEMA_VERSION,
    CorpusArchaeologyError,
    analyze_validated_corpus,
    render_markdown,
)

INPUT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "salvage"
    / "corpus_archaeology_input.schema.json"
)

__all__ = [
    "CorpusArchaeologyError",
    "INPUT_SCHEMA_PATH",
    "RANKING_WEIGHTS",
    "SCHEMA_VERSION",
    "analyze_corpus",
    "main",
    "render_markdown",
]


def _load_input_validator() -> jsonschema.Draft202012Validator:
    try:
        schema = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise CorpusArchaeologyError(
            "committed prepared-corpus input schema is unavailable or invalid"
        ) from exc
    return jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def _first_schema_error(
    validator: jsonschema.Draft202012Validator,
    corpus: dict[str, Any],
) -> jsonschema.ValidationError | None:
    errors = sorted(
        validator.iter_errors(corpus),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    return errors[0] if errors else None


def _schema_error_message(error: jsonschema.ValidationError) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    detail = (
        error.message
        if error.validator in {"required", "additionalProperties"}
        else f"violates {error.validator}"
    )
    return f"input schema validation failed at {path}: {detail}"


def _validate_input_contract(corpus: dict[str, Any]) -> None:
    error = _first_schema_error(_load_input_validator(), corpus)
    if error is not None:
        raise CorpusArchaeologyError(_schema_error_message(error))


def analyze_corpus(
    corpus: dict[str, Any], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Validate and analyze a prepared corpus without mutating external state."""
    if not isinstance(corpus, dict):
        raise CorpusArchaeologyError("corpus input must be an object")
    _validate_input_contract(corpus)
    return analyze_validated_corpus(corpus, generated_at=generated_at)


def _write_new(path: Path, payload: str) -> None:
    path = path.resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise CorpusArchaeologyError(
            f"output already exists and will not be replaced: {path}"
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a custody-cleared prepared corpus without mutation"
    )
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--generated-at")
    return parser


def _write_optional_output(
    output: Path | None,
    source: Path,
    payload: str,
    label: str,
) -> None:
    if output is None:
        return
    if output.resolve(strict=False) == source.resolve():
        raise CorpusArchaeologyError(f"{label} path must not replace the source corpus")
    _write_new(output, payload)


def _emit_outputs(args: argparse.Namespace, report: dict[str, Any]) -> None:
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is None:
        print(payload, end="")
    _write_optional_output(args.output, args.corpus, payload, "output")
    _write_optional_output(
        args.markdown_output,
        args.corpus,
        render_markdown(report),
        "markdown output",
    )


def _execute(args: argparse.Namespace) -> None:
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    report = analyze_corpus(corpus, generated_at=args.generated_at)
    _emit_outputs(args, report)


def main() -> int:
    args = _build_parser().parse_args()
    try:
        _execute(args)
    except (OSError, json.JSONDecodeError, CorpusArchaeologyError) as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
