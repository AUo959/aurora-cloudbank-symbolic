#!/usr/bin/env python3
"""Mint collision-aware L2 names and emit CanonRec naming receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from modules.gumas.naming import (
    NameEntityType,
    NameRegister,
    NameRequest,
    NameService,
    load_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_output_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else REPO_ROOT / path
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"output path escapes repository root: {path}") from exc
    if not resolved.parent.is_dir():
        raise ValueError(f"output directory does not exist: {resolved.parent}")
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entity-type",
        required=True,
        choices=[item.value for item in NameEntityType],
    )
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--faction")
    parser.add_argument("--region")
    parser.add_argument(
        "--register",
        default="FORMAL",
        choices=[item.value for item in NameRegister],
    )
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--constraints", default="{}", help="JSON object")
    parser.add_argument(
        "--select",
        type=int,
        help="Select candidate index and emit a final naming receipt",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    constraints = json.loads(args.constraints)
    if not isinstance(constraints, dict):
        raise SystemExit("--constraints must decode to a JSON object")

    request = NameRequest(
        entity_type=NameEntityType(args.entity_type),
        entity_id=args.entity_id,
        faction_context=args.faction,
        region_context=args.region,
        register=NameRegister(args.register),
        constraints=constraints,
        seed_hint=args.seed,
        candidate_count=max(1, args.count),
    )
    try:
        registry = load_registry(args.registry, allowed_root=REPO_ROOT)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid registry: {exc}") from exc
    service = NameService(registry)
    source_registry_digest = service.registry.digest
    candidates = service.resolve_candidates(request)
    for candidate in candidates:
        candidate.registry_digest = source_registry_digest

    if args.select is None:
        payload = {
            "protocol": candidates[0].protocol,
            "entity_id": args.entity_id,
            "registry_digest": source_registry_digest,
            "candidates": [candidate.to_dict() for candidate in candidates],
        }
    else:
        if args.select < 0 or args.select >= len(candidates):
            raise SystemExit(f"--select must be between 0 and {len(candidates) - 1}")
        selected = NameService.select(candidates, args.select, args.entity_id)
        selected.registry_digest = source_registry_digest
        payload = {"naming_receipt": selected.naming_receipt()}

    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        try:
            output_path = _resolve_output_path(args.output)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        output_path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
