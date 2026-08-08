#!/usr/bin/env python3
"""Read-only inventory for legacy Aurora/GUMAS artifacts.

The inventory never executes or extracts archive content. ZIP entries are read
only when their metadata satisfies configured size, count, and compression
limits. Suspicious entries remain blocked and are represented without content
values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import mimetypes
import os
import re
import stat
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

DEFAULT_MAX_FILE_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_MEMBER_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
DEFAULT_MAX_ARCHIVE_ENTRIES = 10_000
DEFAULT_MAX_CENTRAL_DIRECTORY_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 100.0
TEXT_SCAN_BYTES = 64 * 1024

ZIP_EOCD_SIGNATURE = b"PK\x05\x06"
ZIP_EOCD_STRUCT = struct.Struct("<4s4H2LH")
ZIP_MAX_COMMENT_BYTES = 65_535
ZIP64_SENTINEL_16 = 0xFFFF
ZIP64_SENTINEL_32 = 0xFFFFFFFF

# The ZIP64 end-of-central-directory locator sits immediately before the EOCD.
# zipfile._EndRecData64 honours the ZIP64 record whenever this locator is
# present, overriding the 32-bit entry count and central-directory size --
# regardless of whether those 32-bit fields hold sentinels. Checking sentinels
# alone therefore misses ZIP64 archives that declare small 32-bit values.
ZIP64_LOCATOR_SIGNATURE = b"PK\x06\x07"
ZIP64_LOCATOR_STRUCT = struct.Struct("<4sLQL")

# Decompressed bytes pulled per read when materializing an archive member.
# ZipExtFile.read(n) does not bound the decompressor for non-DEFLATE members,
# so the budget has to be spent in chunks rather than in one large call.
ZIP_MEMBER_READ_CHUNK_BYTES = 64 * 1024

# Compression methods whose expansion this tool can actually bound.
#
# ZIP_STORED is not compressed. For ZIP_DEFLATED, CPython's
# ZipExtFile._read1 forwards max_length into decompress(), so a bounded read
# really is bounded. Every other method -- ZIP_BZIP2, ZIP_LZMA -- ignores
# max_length, and _read2 reads at least MIN_READ_SIZE of compressed input per
# call, so a single 4 KB block can still expand to tens of megabytes inside one
# decompress() call no matter how small the read chunk is. Those members are
# inventoried from metadata and never materialized.
BOUNDABLE_COMPRESSION_METHODS = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})

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


def _validate_limits(
    max_file_bytes: int,
    max_member_bytes: int,
    max_archive_bytes: int,
    max_archive_entries: int,
    max_central_directory_bytes: int,
    max_compression_ratio: float,
) -> None:
    values = {
        "max_file_bytes": max_file_bytes,
        "max_member_bytes": max_member_bytes,
        "max_archive_bytes": max_archive_bytes,
        "max_archive_entries": max_archive_entries,
        "max_central_directory_bytes": max_central_directory_bytes,
        "max_compression_ratio": max_compression_ratio,
    }
    invalid = []
    for name, value in values.items():
        if value <= 0:
            invalid.append(name)
        elif isinstance(value, float) and not math.isfinite(value):
            invalid.append(name)
    if invalid:
        raise InventoryError(f"Inventory limits must be finite and positive: {', '.join(sorted(invalid))}")


def _normalize_generated_at(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise InventoryError(f"generated_at must be a valid timezone-aware ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InventoryError("generated_at must include timezone information")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _open_regular_file(path: Path) -> BinaryIO:
    """Open a regular file without following a final symlink when supported."""
    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise InventoryError(f"Unable to open regular file safely: {path}") from exc

    try:
        current = os.fstat(fd)
        if not stat.S_ISREG(current.st_mode):
            raise InventoryError(f"Filesystem entry is not a regular file: {path}")
        return os.fdopen(fd, "rb")
    except Exception:
        os.close(fd)
        raise


def _sha256_stream(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: Path, max_bytes: int = DEFAULT_MAX_FILE_BYTES) -> str:
    with _open_regular_file(path) as stream:
        size = os.fstat(stream.fileno()).st_size
        if size > max_bytes:
            raise InventoryError(f"File exceeds configured hash limit: {path}")
        return _sha256_stream(stream)


def validate_output_path(root: Path, output: Path) -> Path:
    """Require generated reports to live outside the inventoried source tree."""
    root_resolved = root.resolve()
    output_resolved = output.resolve(strict=False)
    if output_resolved == root_resolved or output_resolved.is_relative_to(root_resolved):
        raise InventoryError("Output path must be outside the inventory source tree")
    return output_resolved


def write_report_exclusive(root: Path, output: Path, payload: str) -> Path:
    """Create one new report without following links or replacing an inode.

    Secure report creation requires POSIX-style directory-relative opens. On a
    platform without those primitives, callers must use stdout instead.
    """
    output_path = validate_output_path(root, output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        parent_path = output_path.parent.resolve(strict=True)
    except OSError as exc:
        raise InventoryError(f"Unable to prepare output directory: {output_path.parent}") from exc

    root_resolved = root.resolve()
    if parent_path == root_resolved or parent_path.is_relative_to(root_resolved):
        raise InventoryError("Output directory must remain outside the inventory source tree")

    if os.open not in os.supports_dir_fd or not hasattr(os, "O_DIRECTORY"):
        raise InventoryError("Secure output-file creation is unavailable on this platform; use stdout")

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    file_flags |= getattr(os, "O_BINARY", 0)

    parent_fd = -1
    file_fd = -1
    created = False
    try:
        parent_fd = os.open(parent_path, directory_flags)
        try:
            file_fd = os.open(output_path.name, file_flags, 0o600, dir_fd=parent_fd)
            created = True
        except FileExistsError as exc:
            raise InventoryError(f"Output path already exists and will not be replaced: {output_path}") from exc
        except OSError as exc:
            raise InventoryError(f"Unable to create output report safely: {output_path}") from exc

        current = os.fstat(file_fd)
        if not stat.S_ISREG(current.st_mode) or current.st_nlink != 1:
            raise InventoryError("New output report did not resolve to a single regular-file inode")

        with os.fdopen(file_fd, "w", encoding="utf-8", newline="\n") as stream:
            file_fd = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        return parent_path / output_path.name
    except Exception:
        if file_fd >= 0:
            os.close(file_fd)
        if created and parent_fd >= 0:
            try:
                os.unlink(output_path.name, dir_fd=parent_fd)
            except OSError:
                pass
        raise
    finally:
        if parent_fd >= 0:
            os.close(parent_fd)


def _is_safe_archive_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
        return False
    path = PurePosixPath(normalized)
    return all(part not in {"", ".", ".."} for part in path.parts)


def _zip_entry_mode(info: zipfile.ZipInfo) -> int:
    if info.create_system != 3:
        return 0
    return info.external_attr >> 16


def _zip_entry_is_symlink(info: zipfile.ZipInfo) -> bool:
    return stat.S_ISLNK(_zip_entry_mode(info))


def _zip_entry_is_special(info: zipfile.ZipInfo) -> bool:
    mode = _zip_entry_mode(info)
    if mode == 0:
        return False
    entry_type = stat.S_IFMT(mode)
    return entry_type not in {0, stat.S_IFREG, stat.S_IFDIR, stat.S_IFLNK}


def _zip_entry_is_executable(info: zipfile.ZipInfo) -> bool:
    mode = _zip_entry_mode(info)
    return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


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
        "archive_special_file",
        "archive_duplicate_path",
        "archive_member_too_large",
        "archive_total_too_large",
        "archive_entry_count_exceeded",
        "archive_central_directory_too_large",
        "archive_eocd_invalid",
        "archive_multidisk_unsupported",
        "archive_zip64_unsupported",
        "archive_compression_ratio",
        "archive_size_mismatch",
        "archive_read_error",
        "unsupported_archive",
        "filesystem_symlink",
        "non_regular_file",
        "walk_error",
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


def _artifact_id(
    source_kind: str,
    relative_path: str,
    sha256: str | None,
    size_bytes: int | None,
    archive_parent: str | None,
) -> str:
    material = (
        f"{source_kind}\0{archive_parent or ''}\0{relative_path}\0{sha256 or ''}\0"
        f"{size_bytes if size_bytes is not None else ''}"
    )
    return f"artifact:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:24]}"


def _read_sample(path: Path, max_bytes: int = TEXT_SCAN_BYTES) -> bytes:
    try:
        with _open_regular_file(path) as stream:
            return stream.read(max_bytes)
    except (OSError, InventoryError):
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
        "artifact_id": _artifact_id(source_kind, relative_path, sha256, size_bytes, archive_parent),
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


def _archive_error(relative_archive_path: str, size_bytes: int | None, flag: str) -> list[dict[str, Any]]:
    return [
        _base_artifact(
            source_kind="archive_error",
            relative_path=relative_archive_path,
            archive_parent=None,
            size_bytes=size_bytes,
            sha256=None,
            category="archive",
            security_flags=[flag],
            media_type="application/zip",
        )
    ]


def _read_member_bounded(stream: BinaryIO, max_bytes: int) -> bytes:
    """Read at most ``max_bytes + 1`` decompressed bytes from an archive member.

    ``ZipExtFile.read(n)`` does not bound the decompressor for non-DEFLATE
    members: CPython's ``ZipExtFile._read1`` forwards ``max_length`` into
    ``decompress()`` only for ``ZIP_DEFLATED``. Asking for the whole declared
    ``file_size`` in one call therefore lets a small LZMA or BZIP2 member expand
    without limit -- a 151 KB ZIP_LZMA archive declaring a 10 MB member drove
    peak RSS past 2 GB while every configured limit was in force.

    Spending the budget in chunks bounds each ``decompress()`` call to the
    expansion of one chunk of compressed input, and returns one byte more than
    the budget so the caller can tell "at the limit" from "over it".

    The budget is applied to bytes actually read, never to the central
    directory's declared size, because that declaration is attacker-supplied.
    """
    budget = max_bytes + 1
    out = bytearray()
    while len(out) < budget:
        chunk = stream.read(min(ZIP_MEMBER_READ_CHUNK_BYTES, budget - len(out)))
        if not chunk:
            break
        out.extend(chunk)
    return bytes(out)


def _zip_preflight(
    raw: BinaryIO,
    size_bytes: int,
    *,
    max_archive_entries: int,
    max_central_directory_bytes: int,
) -> str | None:
    """Bound ZIP metadata before ``zipfile.ZipFile`` materializes entries."""
    if size_bytes < ZIP_EOCD_STRUCT.size:
        return "archive_eocd_invalid"

    # Read the locator's width beyond the comment window so a ZIP64 locator
    # immediately preceding the EOCD is always inside `tail`.
    tail_size = min(
        size_bytes,
        ZIP_EOCD_STRUCT.size + ZIP_MAX_COMMENT_BYTES + ZIP64_LOCATOR_STRUCT.size,
    )
    try:
        raw.seek(size_bytes - tail_size)
        tail = raw.read(tail_size)
    except OSError:
        return "archive_read_error"

    eocd_index = tail.rfind(ZIP_EOCD_SIGNATURE)
    if eocd_index < 0 or len(tail) - eocd_index < ZIP_EOCD_STRUCT.size:
        return "archive_eocd_invalid"

    # Reject ZIP64 on the locator, not just on sentinel values. zipfile reads
    # the ZIP64 record whenever the locator is present, so an archive can pass
    # small non-sentinel 32-bit counts here while zipfile materializes the far
    # larger ZIP64 counts -- bypassing every limit checked below.
    locator_index = eocd_index - ZIP64_LOCATOR_STRUCT.size
    if (
        locator_index >= 0
        and tail[locator_index:locator_index + len(ZIP64_LOCATOR_SIGNATURE)]
        == ZIP64_LOCATOR_SIGNATURE
    ):
        return "archive_zip64_unsupported"

    try:
        (
            signature,
            disk_number,
            central_directory_disk,
            entries_on_disk,
            total_entries,
            central_directory_size,
            central_directory_offset,
            comment_length,
        ) = ZIP_EOCD_STRUCT.unpack_from(tail, eocd_index)
    except struct.error:
        return "archive_eocd_invalid"

    if signature != ZIP_EOCD_SIGNATURE:
        return "archive_eocd_invalid"
    if eocd_index + ZIP_EOCD_STRUCT.size + comment_length != len(tail):
        return "archive_eocd_invalid"
    if disk_number != 0 or central_directory_disk != 0 or entries_on_disk != total_entries:
        return "archive_multidisk_unsupported"
    if (
        total_entries == ZIP64_SENTINEL_16
        or central_directory_size == ZIP64_SENTINEL_32
        or central_directory_offset == ZIP64_SENTINEL_32
    ):
        return "archive_zip64_unsupported"
    if total_entries > max_archive_entries:
        return "archive_entry_count_exceeded"
    if central_directory_size > max_central_directory_bytes:
        return "archive_central_directory_too_large"

    absolute_eocd_offset = size_bytes - tail_size + eocd_index
    if central_directory_offset + central_directory_size > absolute_eocd_offset:
        return "archive_eocd_invalid"
    return None


def inspect_zip(
    archive_path: Path,
    relative_archive_path: str,
    *,
    max_member_bytes: int = DEFAULT_MAX_MEMBER_BYTES,
    max_archive_bytes: int = DEFAULT_MAX_ARCHIVE_BYTES,
    max_archive_entries: int = DEFAULT_MAX_ARCHIVE_ENTRIES,
    max_central_directory_bytes: int = DEFAULT_MAX_CENTRAL_DIRECTORY_BYTES,
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO,
) -> list[dict[str, Any]]:
    _validate_limits(
        1,
        max_member_bytes,
        max_archive_bytes,
        max_archive_entries,
        max_central_directory_bytes,
        max_compression_ratio,
    )
    try:
        raw = _open_regular_file(archive_path)
    except InventoryError:
        return _archive_error(relative_archive_path, None, "archive_read_error")

    with raw:
        size_bytes = os.fstat(raw.fileno()).st_size
        preflight_error = _zip_preflight(
            raw,
            size_bytes,
            max_archive_entries=max_archive_entries,
            max_central_directory_bytes=max_central_directory_bytes,
        )
        if preflight_error:
            return _archive_error(relative_archive_path, size_bytes, preflight_error)

        try:
            raw.seek(0)
            archive = zipfile.ZipFile(raw)
        except (OSError, zipfile.BadZipFile):
            return _archive_error(relative_archive_path, size_bytes, "unsupported_archive")

        with archive:
            infos = archive.infolist()
            if len(infos) > max_archive_entries:
                return _archive_error(relative_archive_path, size_bytes, "archive_entry_count_exceeded")

            normalized_names = [info.filename.replace("\\", "/") for info in infos]
            if len(normalized_names) != len(set(normalized_names)):
                return _archive_error(relative_archive_path, size_bytes, "archive_duplicate_path")

            total_uncompressed = sum(info.file_size for info in infos)
            archive_total_exceeded = total_uncompressed > max_archive_bytes
            artifacts: list[dict[str, Any]] = []

            for info in sorted(infos, key=lambda item: item.filename):
                is_symlink = _zip_entry_is_symlink(info)
                if info.is_dir() and not is_symlink:
                    continue

                flags: list[str] = []
                normalized = info.filename.replace("\\", "/")
                if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
                    flags.append("archive_absolute_path")
                elif not _is_safe_archive_name(normalized):
                    flags.append("archive_path_traversal")

                if is_symlink:
                    flags.append("archive_symlink")
                if _zip_entry_is_special(info):
                    flags.append("archive_special_file")
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

                executable = _zip_entry_is_executable(info)
                if executable:
                    flags.append("archive_executable")

                if info.compress_type not in BOUNDABLE_COMPRESSION_METHODS:
                    # Expansion cannot be bounded for this method; inventory it
                    # from metadata rather than decompressing it.
                    flags.append("archive_unboundable_compression")

                digest: str | None = None
                sample = b""
                read_blocked = bool(
                    {
                        "archive_absolute_path",
                        "archive_path_traversal",
                        "archive_symlink",
                        "archive_special_file",
                        "archive_member_too_large",
                        "archive_total_too_large",
                        "archive_compression_ratio",
                        "archive_unboundable_compression",
                        "nested_archive",
                    }.intersection(flags)
                )
                if not read_blocked:
                    try:
                        with archive.open(info, "r") as stream:
                            data = _read_member_bounded(stream, max_member_bytes)
                        if len(data) > max_member_bytes:
                            # The member expanded past the budget regardless of
                            # what the central directory declared.
                            flags.append("archive_member_too_large")
                        elif len(data) != info.file_size:
                            flags.append("archive_size_mismatch")
                        else:
                            digest = hashlib.sha256(data).hexdigest()
                            sample = data[:TEXT_SCAN_BYTES]
                    except (OSError, RuntimeError, zipfile.BadZipFile):
                        flags.append("archive_read_error")

                if _potential_secret(normalized, sample):
                    flags.append("potential_secret")

                artifacts.append(
                    _base_artifact(
                        source_kind="archive_member",
                        relative_path=normalized,
                        archive_parent=relative_archive_path,
                        size_bytes=info.file_size,
                        sha256=digest,
                        category=classify_path(
                            normalized,
                            executable=executable,
                            archive=suffix in ARCHIVE_SUFFIXES,
                        ),
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
    max_archive_entries: int = DEFAULT_MAX_ARCHIVE_ENTRIES,
    max_central_directory_bytes: int = DEFAULT_MAX_CENTRAL_DIRECTORY_BYTES,
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO,
) -> dict[str, Any]:
    _validate_limits(
        max_file_bytes,
        max_member_bytes,
        max_archive_bytes,
        max_archive_entries,
        max_central_directory_bytes,
        max_compression_ratio,
    )
    normalized_generated_at = _normalize_generated_at(generated_at)
    root = root.resolve()
    if not root.is_dir():
        raise InventoryError(f"Inventory root is not a directory: {root}")

    artifacts: list[dict[str, Any]] = []

    def record_walk_error(error: OSError) -> None:
        error_path = Path(error.filename) if error.filename else root
        try:
            relative = error_path.relative_to(root).as_posix()
        except ValueError:
            relative = error_path.name or "."
        artifacts.append(
            _base_artifact(
                source_kind="filesystem",
                relative_path=relative,
                archive_parent=None,
                size_bytes=None,
                sha256=None,
                category="unknown",
                security_flags=["walk_error"],
            )
        )

    for current, dirnames, filenames in os.walk(
        root,
        followlinks=False,
        onerror=record_walk_error,
    ):
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

            try:
                path_stat = path.lstat()
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

            if stat.S_ISLNK(path_stat.st_mode):
                artifacts.append(
                    _base_artifact(
                        source_kind="filesystem",
                        relative_path=relative,
                        archive_parent=None,
                        size_bytes=None,
                        sha256=None,
                        category="unknown",
                        security_flags=["filesystem_symlink"],
                    )
                )
                continue

            if not stat.S_ISREG(path_stat.st_mode):
                artifacts.append(
                    _base_artifact(
                        source_kind="filesystem",
                        relative_path=relative,
                        archive_parent=None,
                        size_bytes=None,
                        sha256=None,
                        category="unknown",
                        security_flags=["non_regular_file"],
                    )
                )
                continue

            mode = path_stat.st_mode
            size = path_stat.st_size
            executable = bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            suffix = path.suffix.lower()
            archive = suffix in ARCHIVE_SUFFIXES
            flags: list[str] = []
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

            artifacts.append(
                _base_artifact(
                    source_kind="filesystem",
                    relative_path=relative,
                    archive_parent=None,
                    size_bytes=size,
                    sha256=digest,
                    category=classify_path(relative, executable=executable, archive=archive),
                    security_flags=flags,
                )
            )

            if suffix == ".zip" and "hash_limit_exceeded" not in flags and "hash_error" not in flags:
                artifacts.extend(
                    inspect_zip(
                        path,
                        relative,
                        max_member_bytes=max_member_bytes,
                        max_archive_bytes=max_archive_bytes,
                        max_archive_entries=max_archive_entries,
                        max_central_directory_bytes=max_central_directory_bytes,
                        max_compression_ratio=max_compression_ratio,
                    )
                )
            elif archive and suffix != ".zip":
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
        if digest and artifact["source_kind"] in {"filesystem", "archive_member"}:
            duplicate_map.setdefault(digest, []).append(artifact["artifact_id"])
    duplicate_groups = []
    for digest, ids in sorted(duplicate_map.items()):
        unique_ids = sorted(set(ids))
        if len(unique_ids) > 1:
            duplicate_groups.append({"sha256": digest, "artifact_ids": unique_ids})

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
        "generated_at": normalized_generated_at,
        "source_root_name": root.name,
        "read_only": True,
        "artifacts": artifacts,
        "duplicate_groups": duplicate_groups,
        "migration_applied": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inventory legacy Aurora/GUMAS artifacts without mutation")
    parser.add_argument("root", type=Path, help="Directory to inventory")
    parser.add_argument("--output", type=Path, help="New report path outside the source tree; existing paths are rejected")
    parser.add_argument("--generated-at", help="Optional timezone-aware ISO-8601 timestamp for deterministic fixtures")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--max-member-bytes", type=int, default=DEFAULT_MAX_MEMBER_BYTES)
    parser.add_argument("--max-archive-bytes", type=int, default=DEFAULT_MAX_ARCHIVE_BYTES)
    parser.add_argument("--max-archive-entries", type=int, default=DEFAULT_MAX_ARCHIVE_ENTRIES)
    parser.add_argument(
        "--max-central-directory-bytes",
        type=int,
        default=DEFAULT_MAX_CENTRAL_DIRECTORY_BYTES,
    )
    parser.add_argument("--max-compression-ratio", type=float, default=DEFAULT_MAX_COMPRESSION_RATIO)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = inventory_tree(
            args.root,
            generated_at=args.generated_at,
            max_file_bytes=args.max_file_bytes,
            max_member_bytes=args.max_member_bytes,
            max_archive_bytes=args.max_archive_bytes,
            max_archive_entries=args.max_archive_entries,
            max_central_directory_bytes=args.max_central_directory_bytes,
            max_compression_ratio=args.max_compression_ratio,
        )
        payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.output:
            write_report_exclusive(args.root, args.output, payload)
        else:
            print(payload, end="")
    except InventoryError as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
