"""Manifest loading helpers for the mesh runtime."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable

from .models import AgentManifest


DEFAULT_MEMORY_FILES = {
    "alex_thorne.md": """# Alex Thorne

Project Manager and Systems Architect for the Aurora mesh.
Respond with concise, strategic guidance grounded in structure, delivery, and coordination.
Prioritize system coherence over flourish.
""",
}


def normalize_lookup(value: str) -> str:
    """Normalize aliases to a stable routing key."""

    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def ensure_seed_memory_files(memory_dir: Path) -> None:
    """Create minimal seed memory files when they do not already exist."""

    memory_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in DEFAULT_MEMORY_FILES.items():
        target = memory_dir / filename
        if not target.exists():
            target.write_text(content)


def load_manifests(manifest_dir: Path) -> Dict[str, AgentManifest]:
    """Load all JSON manifests in the mesh agent directory."""

    manifests: Dict[str, AgentManifest] = {}
    if not manifest_dir.exists():
        return manifests

    for path in sorted(manifest_dir.glob("*.json")):
        manifest = AgentManifest.from_dict(json.loads(path.read_text()))
        manifests[manifest.id] = manifest
    return manifests


def build_alias_index(manifests: Iterable[AgentManifest]) -> Dict[str, str]:
    """Build a lookup map from aliases and display names to agent ids."""

    alias_index: Dict[str, str] = {}
    for manifest in manifests:
        values = {manifest.id, manifest.display_name, *manifest.aliases}
        for value in values:
            alias_index[normalize_lookup(value)] = manifest.id
    return alias_index


def export_manifest_snapshot(manifests: Dict[str, AgentManifest]) -> str:
    """Serialize manifests for diagnostics and quick inspection."""

    return json.dumps({key: manifest.to_dict() for key, manifest in manifests.items()}, indent=2, sort_keys=True)
