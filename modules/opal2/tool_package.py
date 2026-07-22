"""Deterministic, inspect-only packaging for portable OPAL2 tool artifacts."""

from __future__ import annotations

import hashlib
import json
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile, ZipInfo

from .tool_contract import JsonObject, Opal2Tool, ToolManifest

PACKAGE_FORMAT = "opaltool"
PACKAGE_SPEC_VERSION = "0.1"
CORE_API = "opal2.core.v1"
PACKAGE_MANIFEST_PATH = "opaltool.json"
INPUT_SCHEMA_PATH = "schemas/input.schema.json"
OUTPUT_SCHEMA_PATH = "schemas/output.schema.json"
REQUIRED_SCHEMA_PATHS = frozenset({INPUT_SCHEMA_PATH, OUTPUT_SCHEMA_PATH})
MAX_PACKAGE_FILES = 64
MAX_PACKAGE_BYTES = 5 * 1024 * 1024


class ToolPackageError(ValueError):
    """Raised when an OPAL2 package cannot be built or verified safely."""


@dataclass(frozen=True)
class VerifiedToolPackage:
    """Verified metadata for an inert OPAL2 package artifact."""

    path: Path
    package_manifest: Mapping[str, Any]
    tool_manifest: ToolManifest
    archive_sha256: str

    def to_dict(self) -> JsonObject:
        """Return the verification receipt as JSON-compatible data."""

        return {
            "path": str(self.path),
            "format": self.package_manifest["format"],
            "spec_version": self.package_manifest["spec_version"],
            "tool_id": self.tool_manifest.tool_id,
            "tool_version": self.tool_manifest.version,
            "entrypoint": self.package_manifest["entrypoint"],
            "activation": self.package_manifest["activation"],
            "archive_sha256": self.archive_sha256,
            "verified_files": len(self.package_manifest["integrity"]["files"]),
        }


def build_opaltool_package(
    tool: Opal2Tool,
    destination: str | Path,
    *,
    entrypoint: str,
    implementation_files: Mapping[str, bytes | str],
    fixture_files: Mapping[str, Mapping[str, Any]] | None = None,
) -> VerifiedToolPackage:
    """Build a reproducible package without granting it execution trust."""

    package_path = _validated_destination(destination, entrypoint)
    payloads = _prepare_payloads(tool, implementation_files, fixture_files or {})
    integrity = {
        name: {"sha256": _sha256(data), "size": len(data)}
        for name, data in sorted(payloads.items())
    }
    package_manifest = {
        "format": PACKAGE_FORMAT,
        "spec_version": PACKAGE_SPEC_VERSION,
        "core_api": CORE_API,
        "entrypoint": entrypoint,
        "activation": "inspect-only",
        "tool": tool.manifest.to_dict(),
        "integrity": {"algorithm": "sha256", "files": integrity},
    }
    members = {PACKAGE_MANIFEST_PATH: _json_bytes(package_manifest), **payloads}
    _validate_package_limits(members)

    package_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(package_path, "x", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(members.items()):
            archive.writestr(_zip_info(name), data)
    return verify_opaltool_package(package_path)


def _validated_destination(destination: str | Path, entrypoint: str) -> Path:
    package_path = Path(destination)
    if package_path.exists():
        raise ToolPackageError(
            f"refusing to overwrite existing package: {package_path}"
        )
    if package_path.suffix != ".opaltool":
        raise ToolPackageError("package destination must use the .opaltool suffix")
    _validate_entrypoint(entrypoint)
    return package_path


def _validate_package_limits(members: Mapping[str, bytes]) -> None:
    if len(members) > MAX_PACKAGE_FILES:
        raise ToolPackageError(f"package exceeds the file limit of {MAX_PACKAGE_FILES}")
    if sum(len(data) for data in members.values()) > MAX_PACKAGE_BYTES:
        raise ToolPackageError(
            f"package exceeds the size limit of {MAX_PACKAGE_BYTES} bytes"
        )


def verify_opaltool_package(path: str | Path) -> VerifiedToolPackage:
    """Verify archive structure and digests without extracting or importing code."""

    package_path = Path(path)
    if package_path.suffix != ".opaltool":
        raise ToolPackageError("package path must use the .opaltool suffix")
    try:
        with ZipFile(package_path) as archive:
            members = _read_members(archive)
    except (BadZipFile, OSError, RuntimeError) as exc:
        raise ToolPackageError(f"invalid OPAL2 package: {exc}") from exc

    try:
        package_manifest = json.loads(members[PACKAGE_MANIFEST_PATH])
    except KeyError as exc:
        raise ToolPackageError(f"package is missing {PACKAGE_MANIFEST_PATH}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ToolPackageError("package manifest is not valid UTF-8 JSON") from exc
    if not isinstance(package_manifest, Mapping):
        raise ToolPackageError("package manifest must be an object")

    tool_manifest = _validate_package_manifest(package_manifest, members)
    return VerifiedToolPackage(
        path=package_path,
        package_manifest=dict(package_manifest),
        tool_manifest=tool_manifest,
        archive_sha256=_hash_file(package_path),
    )


def export_builtin_tool(tool_id: str, destination: str | Path) -> VerifiedToolPackage:
    """Export an explicitly allowlisted built-in tool as an inert package."""

    from .tools.regex_workshop import REGEX_WORKSHOP_TOOL_ID, RegexWorkshopTool

    if tool_id != REGEX_WORKSHOP_TOOL_ID:
        raise ToolPackageError(f"built-in tool is not package-enabled: {tool_id}")
    source_path = Path(__file__).parent / "tools" / "regex_workshop.py"
    return build_opaltool_package(
        RegexWorkshopTool(),
        destination,
        entrypoint="modules.opal2.tools.regex_workshop:RegexWorkshopTool",
        implementation_files={"src/regex_workshop.py": source_path.read_bytes()},
        fixture_files={
            "fixtures/basic.json": {
                "input": {
                    "template": "exact",
                    "value": "station[808]",
                    "samples": [
                        {"text": "station[808]", "expected_match": True},
                        {"text": "station808", "expected_match": False},
                    ],
                },
                "expected": {
                    "pattern": r"\Astation\[808\]\Z",
                    "all_expectations_met": True,
                },
            }
        },
    )


def _prepare_payloads(
    tool: Opal2Tool,
    implementation_files: Mapping[str, bytes | str],
    fixture_files: Mapping[str, Mapping[str, Any]],
) -> dict[str, bytes]:
    if not implementation_files:
        raise ToolPackageError("package requires at least one implementation file")
    payloads = {
        INPUT_SCHEMA_PATH: _json_bytes(tool.manifest.input_schema),
        OUTPUT_SCHEMA_PATH: _json_bytes(tool.manifest.output_schema),
    }
    for name, content in implementation_files.items():
        _validate_member_name(name, required_prefix="src/")
        payloads[name] = (
            content.encode("utf-8") if isinstance(content, str) else content
        )
    for name, fixture in fixture_files.items():
        _validate_member_name(name, required_prefix="fixtures/")
        payloads[name] = _json_bytes(fixture)
    return payloads


def _read_members(archive: ZipFile) -> dict[str, bytes]:
    infos = archive.infolist()
    if len(infos) > MAX_PACKAGE_FILES:
        raise ToolPackageError(f"package exceeds the file limit of {MAX_PACKAGE_FILES}")

    members: dict[str, bytes] = {}
    total_size = 0
    for info in infos:
        if info.filename in members:
            raise ToolPackageError(
                f"package contains duplicate member: {info.filename}"
            )
        data = _read_member(archive, info)
        total_size += len(data)
        if total_size > MAX_PACKAGE_BYTES:
            raise ToolPackageError(
                f"package exceeds the size limit of {MAX_PACKAGE_BYTES} bytes"
            )
        members[info.filename] = data
    return members


def _read_member(archive: ZipFile, info: ZipInfo) -> bytes:
    _validate_member_name(info.filename)
    file_mode = info.external_attr >> 16
    if stat.S_IFMT(file_mode) == stat.S_IFLNK:
        raise ToolPackageError(f"package member must not be a symlink: {info.filename}")
    with archive.open(info) as member_file:
        data = member_file.read(MAX_PACKAGE_BYTES + 1)
    if len(data) > MAX_PACKAGE_BYTES:
        raise ToolPackageError(
            f"package exceeds the size limit of {MAX_PACKAGE_BYTES} bytes"
        )
    return data


def _validate_package_manifest(
    package: Mapping[str, Any], members: Mapping[str, bytes]
) -> ToolManifest:
    _validate_package_header(package)
    tool_manifest = _tool_manifest_from_mapping(package.get("tool"))
    declared_files = _declared_integrity_files(package, members)
    _verify_declared_files(declared_files, members)
    input_schema, output_schema = _load_packaged_schemas(members)
    if (
        input_schema != tool_manifest.input_schema
        or output_schema != tool_manifest.output_schema
    ):
        raise ToolPackageError("packaged schemas do not match the tool manifest")
    return tool_manifest


def _validate_package_header(package: Mapping[str, Any]) -> None:
    if package.get("format") != PACKAGE_FORMAT:
        raise ToolPackageError(f"unsupported package format: {package.get('format')}")
    if package.get("spec_version") != PACKAGE_SPEC_VERSION:
        raise ToolPackageError(
            f"unsupported package spec version: {package.get('spec_version')}"
        )
    if package.get("core_api") != CORE_API:
        raise ToolPackageError(f"unsupported core API: {package.get('core_api')}")
    if package.get("activation") != "inspect-only":
        raise ToolPackageError("package activation must remain inspect-only")
    _validate_entrypoint(package.get("entrypoint"))


def _declared_integrity_files(
    package: Mapping[str, Any], members: Mapping[str, bytes]
) -> Mapping[str, Any]:
    integrity = package.get("integrity")
    if not isinstance(integrity, Mapping) or integrity.get("algorithm") != "sha256":
        raise ToolPackageError("package integrity algorithm must be sha256")
    declared_files = integrity.get("files")
    if not isinstance(declared_files, Mapping):
        raise ToolPackageError("package integrity files must be an object")
    if set(members) != {PACKAGE_MANIFEST_PATH, *declared_files}:
        raise ToolPackageError("package contents do not match the integrity manifest")
    if not REQUIRED_SCHEMA_PATHS.issubset(declared_files):
        raise ToolPackageError("package is missing required schema members")
    _validate_payload_layout(declared_files)
    return declared_files


def _validate_payload_layout(declared_files: Mapping[str, Any]) -> None:
    if not any(name.startswith("src/") for name in declared_files):
        raise ToolPackageError("package requires at least one implementation member")
    unsupported = [
        name for name in declared_files if not _is_supported_payload_name(name)
    ]
    if unsupported:
        raise ToolPackageError(f"unsupported package payload: {min(unsupported)}")


def _is_supported_payload_name(name: str) -> bool:
    return (
        name in REQUIRED_SCHEMA_PATHS
        or name.startswith("src/")
        or name.startswith("fixtures/")
    )


def _verify_declared_files(
    declared_files: Mapping[str, Any], members: Mapping[str, bytes]
) -> None:
    for name, receipt in declared_files.items():
        _validate_member_name(name)
        if not isinstance(receipt, Mapping):
            raise ToolPackageError(f"integrity receipt must be an object: {name}")
        data = members[name]
        if receipt.get("size") != len(data) or receipt.get("sha256") != _sha256(data):
            raise ToolPackageError(f"package integrity verification failed: {name}")


def _load_packaged_schemas(
    members: Mapping[str, bytes],
) -> tuple[Any, Any]:
    try:
        input_schema = json.loads(members[INPUT_SCHEMA_PATH])
        output_schema = json.loads(members[OUTPUT_SCHEMA_PATH])
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ToolPackageError("packaged schemas must be valid UTF-8 JSON") from exc
    return input_schema, output_schema


def _tool_manifest_from_mapping(value: Any) -> ToolManifest:
    if not isinstance(value, Mapping):
        raise ToolPackageError("tool manifest must be an object")

    tool_id = _manifest_string(value, "tool_id")
    name = _manifest_string(value, "name")
    version = _manifest_string(value, "version")
    description = _manifest_string(value, "description")
    capabilities = _manifest_string_tuple(value, "capabilities")
    input_schema = _manifest_mapping(value, "input_schema")
    output_schema = _manifest_mapping(value, "output_schema")
    runtime = _manifest_optional_string(value, "runtime", "python")
    deterministic = _manifest_bool(value, "deterministic", False)
    side_effects = _manifest_string_tuple(value, "side_effects", ())
    policy_profiles = _manifest_string_tuple(value, "policy_profiles", ())
    export_targets = _manifest_string_tuple(value, "export_targets", ("python",))

    try:
        return ToolManifest(
            tool_id=tool_id,
            name=name,
            version=version,
            description=description,
            capabilities=capabilities,
            input_schema=input_schema,
            output_schema=output_schema,
            runtime=runtime,
            deterministic=deterministic,
            side_effects=side_effects,
            policy_profiles=policy_profiles,
            export_targets=export_targets,
        )
    except (TypeError, ValueError) as exc:
        raise ToolPackageError(f"invalid tool manifest: {exc}") from exc


def _manifest_string(value: Mapping[str, Any], field_name: str) -> str:
    field_value = value.get(field_name)
    if not isinstance(field_value, str):
        raise ToolPackageError(f"tool manifest field '{field_name}' must be a string")
    return field_value


def _manifest_optional_string(
    value: Mapping[str, Any], field_name: str, default: str
) -> str:
    field_value = value.get(field_name, default)
    if not isinstance(field_value, str):
        raise ToolPackageError(f"tool manifest field '{field_name}' must be a string")
    return field_value


def _manifest_string_tuple(
    value: Mapping[str, Any],
    field_name: str,
    default: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    if field_name not in value:
        if default is None:
            raise ToolPackageError(f"tool manifest is missing field: {field_name}")
        return default
    field_value = value[field_name]
    if not isinstance(field_value, list) or any(
        not isinstance(item, str) for item in field_value
    ):
        raise ToolPackageError(
            f"tool manifest field '{field_name}' must be an array of strings"
        )
    return tuple(field_value)


def _manifest_mapping(value: Mapping[str, Any], field_name: str) -> Mapping[str, Any]:
    field_value = value.get(field_name)
    if not isinstance(field_value, Mapping):
        raise ToolPackageError(f"tool manifest field '{field_name}' must be an object")
    return field_value


def _manifest_bool(value: Mapping[str, Any], field_name: str, default: bool) -> bool:
    field_value = value.get(field_name, default)
    if not isinstance(field_value, bool):
        raise ToolPackageError(f"tool manifest field '{field_name}' must be a boolean")
    return field_value


def _validate_entrypoint(value: Any) -> None:
    if not isinstance(value, str) or value.count(":") != 1:
        raise ToolPackageError("entrypoint must use module:object syntax")
    module_name, object_name = value.split(":", 1)
    if (
        not module_name
        or not object_name
        or not all(part.isidentifier() for part in module_name.split("."))
    ):
        raise ToolPackageError("entrypoint must use module:object syntax")
    if not object_name.isidentifier():
        raise ToolPackageError("entrypoint object must be a valid identifier")


def _validate_member_name(name: Any, *, required_prefix: str | None = None) -> None:
    if not isinstance(name, str):
        raise ToolPackageError(f"unsafe package member name: {name}")
    if _has_unsafe_member_text(name) or _has_unsafe_member_path(name):
        raise ToolPackageError(f"unsafe package member name: {name}")
    if required_prefix and not name.startswith(required_prefix):
        raise ToolPackageError(
            f"package member must be under {required_prefix}: {name}"
        )


def _has_unsafe_member_text(name: str) -> bool:
    return not name or "\\" in name or "\x00" in name


def _has_unsafe_member_path(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        path.is_absolute()
        or path.as_posix() != name
        or name.endswith("/")
        or not path.parts
        or ".." in path.parts
    )


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as package_file:
        for chunk in iter(lambda: package_file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
