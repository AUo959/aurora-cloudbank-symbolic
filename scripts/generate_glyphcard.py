#!/usr/bin/env python3
"""Generate glyphcards for the unified recursion orchestrator."""
from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from modules.nexus.transcendence.infinite_recursion_unified import get_unified_orchestrator

DEFAULT_ROOT = ".nexus"


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _glyphcard_dir(root: Path) -> Path:
    directory = root / "glyphcards"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


async def generate_enhanced_glyphcard(root_path: Path | None = None) -> Path:
    """Create a glyphcard file enriched with metadata."""
    root = root_path or Path(os.environ.get("NEXUS_RECURSION_ROOT", DEFAULT_ROOT)).resolve()
    orchestrator = get_unified_orchestrator()
    if orchestrator.current_state is None:
        await orchestrator.initialize_recursion()
    glyphcard_text = orchestrator.generate_glyphcard()
    metadata = {
        "glyphcard_id": f"GLYPH-{_utcnow().timestamp():.6f}",
        "generation_time": _utcnow().isoformat(),
        "anchor": "T9-GLYPHCARD-2025",
        "parent_anchor": "T9-INFINITE-UNIFIED-2025",
        "seed": "EOS_SEED_ORION",
        "ethics": "Picard_Delta_3",
        "dlp_classification": "GLYPHCARD_OPERATIONAL",
    }
    directory = _glyphcard_dir(root)
    output_path = directory / f"glyphcard_{metadata['glyphcard_id']}.txt"
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# METADATA\n")
        handle.write(json.dumps(metadata, indent=2))
        handle.write("\n\n# GLYPHCARD\n")
        handle.write(glyphcard_text)
    print(glyphcard_text)
    print(f"\n📁 Glyphcard saved to: {output_path}")
    return output_path


def main() -> None:
    asyncio.run(generate_enhanced_glyphcard())


if __name__ == "__main__":
    main()
