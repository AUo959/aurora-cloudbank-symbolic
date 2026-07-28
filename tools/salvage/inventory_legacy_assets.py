#!/usr/bin/env python3
"""Read-only inventory for legacy Aurora/GUMAS artifacts.

The inventory never executes or extracts archive content. ZIP entries are read
only when their metadata satisfies configured size and compression limits.
Suspicious entries remain blocked and are represented without content values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

DEFAULT_MAX_FILE_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_MEMBER_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 100.0
TEXT_SCAN_BYTES = 64 * 1024

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz", ".7z"}
CODE_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".sh",
    ".ps1",
}
DATA_SUFFIXES = {".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml", ".xml", ".simstate"}
DOC_SUFFIXES = {".md", ".txt", ".rst", ".pdf", ".doc", ".docx"}
CONFIG_NAMES = {
    "dockerfile",
    "makefile",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "requirements.txt",
    "requirements-test.txt",
}
CONFIG_SUFFIXES = {".ini", ".cfg", ".conf", ".toml", ".env"}
MEDIA_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp3", ".wav", ".mp4", ".mov"}
EXECUTABLE_SUFFIXES = {".exe", ".dll", ".so", ".dylib", ".bin", ".app", ".com", ".msi"}

SECRET_FILENAME_RE = re.compile(
    (
        r"(^|[._-])(secret|secrets|credential|credentials|private[_-]?key|token|tokens|password|passwd|"
        r"api[_-]?key)([._-]|$)"
    ),
    re.IGNORECASE,
)
SECRET_CONTENT_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{12,}"),
)


class InventoryError(ValueError):
    """Raised when inventory cannot be completed safely."""


def _sha256_stream(stream: BinaryIO, limit: int | None = None) -> str:
    digest = hashlib.sha256()
    consumed = 0
    while True:
        chunk_size = 1024 * 1024
        if limit is not None:
            remaining = limit - consumed
            if remaining <= 0:
                break
            chunk_size = min(chunk_size, remaining)
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)
        consumed += len(chunk)
    return digest.hexdigest()


def sha256_file(path: Path, max_bytes: int = DEFAULT_MAX_FILE_BYTES) -> str:
    size = path.stat().st_size
    if size > max_bytes:
        raise InventoryError(f"File exceeds configured hash limit: {path}")
    with path.open("rb") as stream:
        return _sha256_stream(stream)


def validate_output_path(root: Path, output: Path) -> Path:
    """Require generated reports to live outside the inventoried source tree."""
    root_resolved = root.resolve()
    output_resolved = output.resolve(strict=False)
    if output_resolved == root_resolved or output_resolved.is_relative_to(root_resolved):
        raise InventoryError("Output path must be outside the inventory source tree")
    return output_resolved


def _is_safe_archive_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
        return False
    path = PurePosixPath(normalized)
    return all(part not in {"", ".", ".."} for part in path.parts)


def _zip_entry_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0o170000
    return mode == stat.S_IFLNK


def _potential_secret(path_name: str, sample: bytes) -> bool:
    if SECRET_FILENAME_RE.search(Path(path_name).name):
        return True
    return any(pattern.search(sample) for pattern in SECRET_CONTENT_PATTERNS)


def classify_path(path_name: str, executable: bool = False, archive: bool = False) -> str:
    name = Path(path_name).name.lower()
    suffix = Path(path_name).suffix.lower()
    if archive or suffix in ARCHIVE_SUFFIXES:
        return "archive"
    if executable or suffix in EXECUTABLE_SUFFIXES:
        return "executable"
    if name in CONFIG_NAMES or suffix in CONFIG_SUFFIXES:
        return "configuration"
    if suffix in CODE_SUFFIXES:
        return "code"
    if suffix in DATA_SUFFIXES:
        return "data"
    if suffix in DOC_SUFFIXES:
        return "documentation"
    if suffix in MEDIA_SUFFIXES:
        return "generated_media"
    return "unknown"


def proposed_disposition(category: str, security_flags: list[str]) -> str:
    blocking = {
        "archive_path_traversal",
        "archive_absolute_path",
        "archive_symlink",
        "archive_member_too_large",
        "archive_total_too_large",
        "archive_compression_ratio",
        "archive_size_mismatch",
        "archive_read_error",
        "unsupported_archive",
        "filesystem_symlink",
        "hash_limit_exceeded",
        "hash_error",
        "stat_error",
        "nested_archive",
    }
    if blocking.intersection(security_flags):
        return "blocked"
    if "potential_secret" in security_flags or category == "executable":
        return "quarantine"
    if category in {"documentation", "generated_media"}:
        return "archive"
    if category == "unknown":
        return "review"
    return "retain_review"


def _artifact_id(source_kind: str, relative_path: str, sha256: str | None, size_bytes: int | None) -> str:
    material = f"{source_kind}\0{relative_path}\0{sha256 or ''}\0{size_bytes if size_bytes is not None else ''}"
    return f"artifact:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:24]}"


def _read_sample(path: Path, max_bytes: int = TEXT_SCAN_BYTES) -> bytes:
    try:
        with path.open("rb") as stream:
            return stream.read(max_bytes)
    except OSError:
        return b""


def _base_artifact(
    *,
    source_kind: str,
    relative_path: str,
    size_bytes: int | None,
    sha256: str | None,
    category: str,
    security_flags: list[str],
    archive_parent: str | None = None,
    media_type: str | None = None,
) -> dict[str, Any]:
    flags = sorted(set(security_flags))
    return {
        "artifact_id": _artifact_id(source_kind, relative_path, sha256, size_bytes),
        "source_kind": source_kind,
        "relative_path": relative_path,
        "archive_parent": archive_parent,
        "size_bytes": size_bytes,
        "sha256": sha256,
        "media_type": media_type or mimetypes.guess_type(relative_path)[0],
        "category": category,
        "security_flags": flags,
        "proposed_disposition": proposed_disposition(category, flags),
    }


def inspect_zip(
    archive_path: Path,
    relative_archive_path: str,
    *,
    max_member_bytes: int = DEFAULT_MAX_MEMBER_BYTES,
    max_archive_bytes: int = DEFAULT_MAX_ARCHIVE_BYTES,
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO,
) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    try:
        archive = zipfile.ZipFile(archive_path)
    except (OSError, zipfile.BadZipFile):
        return [
            _base_artifact(
                source_kind="archive_error",
                relative_path=relative_archive_path,
                archive_parent=None,
                size_bytes=archive_path.stat().st_size if archive_path.exists() else None,
                sha256=None,
                category="archive",
                security_flags=["unsupported_archive"],
                media_type="application/zip",
            )
        ]

    total_uncompressed = sum(info.file_size for info in archive.infolist())
    archive_total_exceeded = total_uncompressed > max_archive_bytes

    with archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue

            flags: list[str] = []
            normalized = info.filename.replace("\\", "/")
            if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
                flags.append("archive_absolute_path")
            elif not _is_safe_archive_name(normalized):
                flags.append("archive_path_traversal")

            if _zip_entry_is_symlink(info):
                flags.append("archive_symlink")
            if info.file_size > max_member_bytes:
                flags.append("archive_member_too_large")
            if archive_total_exceeded:
                flags.append("archive_total_too_large")

            ratio = (
                float("inf")
                if info.compress_size == 0 and info.file_size
                else info.file_size / max(info.compress_size, 1)
            )
            if ratio > max_compression_ratio:
                flags.append("archive_compression_ratio")

            suffix = Path(normalized).suffix.lower()
            if suffix in ARCHIVE_SUFFIXES:
                flags.append("nested_archive")

            digest: str | None = None
            sample = b""
            read_blocked = any(
                flag
                in {
                    "archive_absolute_path",
                    "archive_path_traversal",
                    "archive_symlink",
                    "archive_member_too_large",
                    "archive_total_too_large",
                    "archive_compression_ratio",
                    "nested_archive",
                }
                for flag in flags
            )
            if not read_blocked:
                try:
                    with archive.open(info, "r") as stream:
                        data = stream.read(info.file_size + 1)
                    if len(data) != info.file_size:
                        flags.append("archive_size_mismatch")
                    else:
                        digest = hashlib.sha256(data).hexdigest()
                        sample = data[:TEXT_SCAN_BYTES]
                except (OSError, RuntimeError, zipfile.BadZipFile):
                    flags.append("archive_read_error")

            if _potential_secret(normalized, sample):
                flags.append("potential_secret")

            category = classify_path(normalized, archive=suffix in ARCHIVE_SUFFIXES)
            artifacts.append(
                _base_artifact(
                    source_kind="archive_member",
                    relative_path=normalized,
                    archive_parent=relative_archive_path,
                    size_bytes=info.file_size,
                    sha256=digest,
                    category=category,
                    security_flags=flags,
                    media_type=mimetypes.guess_type(normalized)[0],
                )
            )
    return artifacts


def inventory_tree(
    root: Path,
    *,
    generated_at: str | None = None,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_member_bytes: int = DEFAULT_MAX_MEMBER_BYTES,
    max_archive_bytes: int = DEFAULT_MAX_ARCHIVE_BYTES,
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise InventoryError(f"Inventory root is not a directory: {root}")

    artifacts: list[dict[str, Any]] = []
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        retained_dirs: list[str] = []
        for dirname in sorted(dirnames):
            candidate = current_path / dirname
            if candidate.is_symlink():
                artifacts.append(
                    _base_artifact(
                        source_kind="filesystem",
                        relative_path=candidate.relative_to(root).as_posix(),
                        archive_parent=None,
                        size_bytes=None,
                        sha256=None,
                        category="unknown",
                        security_flags=["filesystem_symlink"],
                    )
                )
            else:
                retained_dirs.append(dirname)
        dirnames[:] = retained_dirs

        for filename in sorted(filenames):
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            flags: list[str] = []

            if path.is_symlink():
                flags.append("filesystem_symlink")
                artifacts.append(
                    _base_artifact(
                        source_kind="filesystem",
                        relative_path=relative,
                        archive_parent=None,
                        size_bytes=None,
                        sha256=None,
                        category="unknown",
                        security_flags=flags,
                    )
                )
                continue

            try:
                path_stat = path.stat()
                mode = path_stat.st_mode
                size = path_stat.st_size
            except OSError:
                artifacts.append(
                    _base_artifact(
                        source_kind="filesystem",
                        relative_path=relative,
                        archive_parent=None,
                        size_bytes=None,
                        sha256=None,
                        category="unknown",
                        security_flags=["stat_error"],
                    )
                )
                continue

            executable = bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            suffix = path.suffix.lower()
            archive = suffix in ARCHIVE_SUFFIXES

            digest: str | None = None
            if size > max_file_bytes:
                flags.append("hash_limit_exceeded")
            else:
                try:
                    digest = sha256_file(path, max_bytes=max_file_bytes)
                except (OSError, InventoryError):
                    flags.append("hash_error")

            sample = _read_sample(path, TEXT_SCAN_BYTES)
            if _potential_secret(relative, sample):
                flags.append("potential_secret")
            if executable:
                flags.append("filesystem_executable")

            category = classify_path(relative, executable=executable, archive=archive)
            artifacts.append(
                _base_artifact(
                    source_kind="filesystem",
                    relative_path=relative,
                    archive_parent=None,
                    size_bytes=size,
                    sha256=digest,
                    category=category,
                    security_flags=flags,
                )
            )

            if suffix == ".zip":
                artifacts.extend(
                    inspect_zip(
                        path,
                        relative,
                        max_member_bytes=max_member_bytes,
                        max_archive_bytes=max_archive_bytes,
                        max_compression_ratio=max_compression_ratio,
                    )
                )
            elif archive:
                artifacts.append(
                    _base_artifact(
                        source_kind="archive_notice",
                        relative_path=relative,
                        archive_parent=None,
                        size_bytes=size,
                        sha256=digest,
                        category="archive",
                        security_flags=["unsupported_archive"],
                    )
                )

    artifacts = sorted(
        artifacts,
        key=lambda item: (
            item["archive_parent"] or "",
            item["relative_path"],
            item["source_kind"],
            item["artifact_id"],
        ),
    )

    duplicate_map: dict[str, list[str]] = {}
    for artifact in artifacts:
        digest = artifact.get("sha256")
        if digest:
            duplicate_map.setdefault(digest, []).append(artifact["artifact_id"])
    duplicate_groups = [
        {"sha256": digest, "artifact_ids": sorted(ids)}
        for digest, ids in sorted(duplicate_map.items())
        if len(ids) > 1
    ]

    stable_material = {
        "root_name": root.name,
        "artifacts": artifacts,
        "duplicate_groups": duplicate_groups,
    }
    report_id = hashlib.sha256(
        json.dumps(stable_material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()

    return {
        "schema_version": "1.0.0",
        "report_id": f"inventory:{report_id}",
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source_root_name": root.name,
        "read_only": True,
        "artifacts": artifacts,
        "duplicate_groups": duplicate_groups,
        "migration_applied": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inventory legacy Aurora/GUMAS artifacts without mutation")
    parser.add_argument("root", type=Path, help="Directory to inventory")
    parser.add_argument("--output", type=Path, help="Optional report path outside the source tree")
    parser.add_argument("--generated-at", help="Optional ISO-8601 timestamp for deterministic fixtures")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--max-member-bytes", type=int, default=DEFAULT_MAX_MEMBER_BYTES)
    parser.add_argument("--max-archive-bytes", type=int, default=DEFAULT_MAX_ARCHIVE_BYTES)
    parser.add_argument("--max-compression-ratio", type=float, default=DEFAULT_MAX_COMPRESSION_RATIO)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        output_path = validate_output_path(args.root, args.output) if args.output else None
        report = inventory_tree(
            args.root,
            generated_at=args.generated_at,
            max_file_bytes=args.max_file_bytes,
            max_member_bytes=args.max_member_bytes,
            max_archive_bytes=args.max_archive_bytes,
            max_compression_ratio=args.max_compression_ratio,
        )
    except InventoryError as exc:
        print(f"INVALID: {exc}")
        return 1

    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
