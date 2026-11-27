#!/usr/bin/env python3
"""Public schema/API boundary for deterministic Phase-1 corpus archaeology.

Structural input validation remains here because callers import ``analyze_corpus``
from this module. Filesystem/CLI output policy lives in ``corpus_archaeology_cli``;
semantic analysis lives in ``corpus_archaeology_core``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tools.salvage.corpus_archaeology_cli import run_cli  # noqa: E402
from tools.salvage.corpus_archaeology_core import (  # noqa: E402
    RANKING_WEIGHTS,
    SCHEMA_VERSION,
    analyze_validated_corpus,
    render_markdown,
)
from tools.salvage.corpus_archaeology_shared import (  # noqa: E402
    CorpusArchaeologyError,
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


def main() -> int:
    return run_cli(analyze_corpus, render_markdown)


if __name__ == "__main__":
    raise SystemExit(main())
