"""Path-contained durable storage for Narrative River workflow artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from .models import NarrativeRiverFrame, SceneRiverDelta, ValidationReport
from .serialization import dumps_json, dumps_yaml, loads_json, loads_yaml

_MANIFEST_SCHEMA_VERSION = "0.1.0"
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


class NarrativeRiverStore:
    """Store frames and deltas durably without touching simulation or canon repositories."""

    def __init__(self, root: str | Path = "narrative/river") -> None:
        self.root = Path(root).expanduser().resolve()
        self.frames_dir = self.root / "frames"
        self.deltas_dir = self.root / "deltas"
        self.prompts_dir = self.root / "prompt_packets"
        self.reports_dir = self.root / "validation_reports"
        self.manifest_path = self.root / "manifest.json"

    @staticmethod
    def safe_scene_name(scene_id: str) -> str:
        """Convert a scene ID into a stable filename without accepting path syntax."""

        raw = scene_id.strip()
        normalized = _SAFE_NAME.sub("_", raw).strip("._-")
        if not normalized:
            raise ValueError("scene_id does not contain a usable filename component")
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
        return f"{normalized[:160]}--{digest}"

    def _contained(self, path: Path) -> Path:
        resolved = path.resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise ValueError("artifact path escapes the Narrative River workspace")
        return resolved

    def _artifact_path(self, directory: Path, scene_id: str, suffix: str) -> Path:
        return self._contained(directory / f"{self.safe_scene_name(scene_id)}{suffix}")

    def frame_path(self, scene_id: str) -> Path:
        return self._artifact_path(self.frames_dir, scene_id, ".frame.yaml")

    def delta_path(self, scene_id: str) -> Path:
        return self._artifact_path(self.deltas_dir, scene_id, ".delta.yaml")

    def prompt_path(self, scene_id: str) -> Path:
        return self._artifact_path(self.prompts_dir, scene_id, ".prompt.txt")

    def report_path(self, scene_id: str) -> Path:
        return self._artifact_path(self.reports_dir, scene_id, ".validation.json")

    def frame_receipt(self, scene_id: str) -> str:
        return self.frame_path(scene_id).as_uri()

    def delta_receipt(self, scene_id: str) -> str:
        return self.delta_path(scene_id).as_uri()

    def report_receipt(self, scene_id: str) -> str:
        return self.report_path(scene_id).as_uri()

    @staticmethod
    def _digest(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _atomic_write(self, path: Path, text: str) -> None:
        path = self._contained(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        )
        temp_path = Path(handle.name)
        try:
            with handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _empty_manifest(self) -> dict[str, Any]:
        return {
            "schema_version": _MANIFEST_SCHEMA_VERSION,
            "latest_closed_scene_id": None,
            "scenes": {},
        }

    def load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return self._empty_manifest()
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != _MANIFEST_SCHEMA_VERSION:
            raise ValueError("unsupported or malformed Narrative River manifest")
        if not isinstance(payload.get("scenes"), dict):
            raise ValueError("Narrative River manifest scenes must be a mapping")
        return payload

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        self._atomic_write(self.manifest_path, text)

    def _record(self, manifest: dict[str, Any], scene_id: str, key: str, path: Path, text: str) -> None:
        relative_path = path.relative_to(self.root).as_posix()
        scene = manifest.setdefault("scenes", {}).setdefault(scene_id, {})
        scene[key] = {"path": relative_path, "sha256": self._digest(text)}

    def save_frame(self, frame: NarrativeRiverFrame) -> Path:
        path = self.frame_path(frame.scene_id)
        expected_receipt = path.as_uri()
        if frame.narrative_status.storage_receipt != expected_receipt:
            raise ValueError("frame storage_receipt does not match its durable path")
        text = dumps_yaml(frame)
        self._atomic_write(path, text)
        manifest = self.load_manifest()
        self._record(manifest, frame.scene_id, "frame", path, text)
        manifest["scenes"][frame.scene_id]["frame_id"] = frame.frame_id
        self._write_manifest(manifest)
        return path

    def save_delta(self, delta: SceneRiverDelta) -> Path:
        path = self.delta_path(delta.scene_id)
        if delta.storage_receipt != path.as_uri():
            raise ValueError("delta storage_receipt does not match its durable path")
        text = dumps_yaml(delta)
        self._atomic_write(path, text)
        manifest = self.load_manifest()
        self._record(manifest, delta.scene_id, "delta", path, text)
        manifest["latest_closed_scene_id"] = delta.scene_id
        self._write_manifest(manifest)
        return path

    def save_prompt(self, frame: NarrativeRiverFrame, prompt_text: str) -> Path:
        path = self.prompt_path(frame.scene_id)
        self._atomic_write(path, prompt_text)
        manifest = self.load_manifest()
        self._record(manifest, frame.scene_id, "prompt", path, prompt_text)
        self._write_manifest(manifest)
        return path

    def save_report(self, frame: NarrativeRiverFrame, report: ValidationReport) -> Path:
        path = self.report_path(frame.scene_id)
        expected_receipt = path.as_uri()
        if report.storage_receipt != expected_receipt:
            raise ValueError("validation report storage_receipt does not match its durable path")
        text = dumps_json(report) + "\n"
        self._atomic_write(path, text)
        manifest = self.load_manifest()
        self._record(manifest, frame.scene_id, "validation_report", path, text)
        self._write_manifest(manifest)
        return path

    def _load_record_text(self, scene_id: str, key: str) -> str:
        manifest = self.load_manifest()
        try:
            record = manifest["scenes"][scene_id][key]
            relative = record["path"]
            expected_digest = record["sha256"]
        except (KeyError, TypeError) as exc:
            raise FileNotFoundError(f"no {key} recorded for scene {scene_id}") from exc
        path = self._contained(self.root / relative)
        text = path.read_text(encoding="utf-8")
        if self._digest(text) != expected_digest:
            raise ValueError(f"stored {key} for scene {scene_id} failed integrity verification")
        return text

    def load_frame_for_scene(self, scene_id: str) -> NarrativeRiverFrame:
        return loads_yaml(NarrativeRiverFrame, self._load_record_text(scene_id, "frame"))

    def load_delta_for_scene(self, scene_id: str) -> SceneRiverDelta:
        return loads_yaml(SceneRiverDelta, self._load_record_text(scene_id, "delta"))

    def load_latest_delta(self) -> SceneRiverDelta | None:
        latest = self.load_manifest().get("latest_closed_scene_id")
        return None if not latest else self.load_delta_for_scene(str(latest))


def load_frame_file(path: str | Path) -> NarrativeRiverFrame:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    return loads_json(NarrativeRiverFrame, text) if source.suffix.lower() == ".json" else loads_yaml(NarrativeRiverFrame, text)


def load_delta_file(path: str | Path) -> SceneRiverDelta:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    return loads_json(SceneRiverDelta, text) if source.suffix.lower() == ".json" else loads_yaml(SceneRiverDelta, text)
