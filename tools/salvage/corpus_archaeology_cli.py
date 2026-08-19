"""CLI and exclusive output policy for Phase-1 corpus archaeology."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tools.salvage.corpus_archaeology_shared import CorpusArchaeologyError

Analyzer = Callable[..., dict[str, Any]]
Renderer = Callable[[dict[str, Any]], str]


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


def _emit_outputs(
    args: argparse.Namespace,
    report: dict[str, Any],
    render_markdown: Renderer,
) -> None:
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


def _execute(
    args: argparse.Namespace,
    analyze_corpus: Analyzer,
    render_markdown: Renderer,
) -> None:
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    report = analyze_corpus(corpus, generated_at=args.generated_at)
    _emit_outputs(args, report, render_markdown)


def run_cli(analyze_corpus: Analyzer, render_markdown: Renderer) -> int:
    """Run the public CLI while keeping analysis and rendering dependency-injected."""
    args = _build_parser().parse_args()
    try:
        _execute(args, analyze_corpus, render_markdown)
    except (OSError, json.JSONDecodeError, CorpusArchaeologyError) as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0
