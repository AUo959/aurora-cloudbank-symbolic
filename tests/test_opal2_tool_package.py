"""Tests for deterministic, inert OPAL2 package artifacts."""

import hashlib
import json
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from modules.opal2.tool_package import (
    PACKAGE_MANIFEST_PATH,
    ToolPackageError,
    build_opaltool_package,
    export_builtin_tool,
    verify_opaltool_package,
)
from modules.opal2.tools.regex_workshop import (
    REGEX_WORKSHOP_TOOL_ID,
    RegexWorkshopTool,
)


def _read_package_members(package_path):
    with ZipFile(package_path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _write_package_members(package_path, members):
    package_path.unlink()
    with ZipFile(package_path, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)


def _replace_package_manifest(members, package):
    members[PACKAGE_MANIFEST_PATH] = json.dumps(package, sort_keys=True).encode()


@pytest.mark.unit
@pytest.mark.opal2
def test_builtin_regex_package_is_reproducible_and_verifiable(tmp_path):
    first = tmp_path / "regex-first.opaltool"
    second = tmp_path / "regex-second.opaltool"

    first_receipt = export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, first)
    second_receipt = export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, second)

    assert first.read_bytes() == second.read_bytes()  # nosec B101 - pytest assertion
    assert first_receipt.archive_sha256 == second_receipt.archive_sha256  # nosec B101 - pytest assertion
    assert first_receipt.tool_manifest.tool_id == REGEX_WORKSHOP_TOOL_ID  # nosec B101 - pytest assertion
    assert first_receipt.package_manifest["activation"] == "inspect-only"  # nosec B101 - pytest assertion
    assert first_receipt.to_dict()["verified_files"] == 4  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_package_contains_manifest_schemas_and_implementation(tmp_path):
    package_path = tmp_path / "regex.opaltool"
    export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, package_path)

    with ZipFile(package_path) as archive:
        names = set(archive.namelist())
        package = json.loads(archive.read(PACKAGE_MANIFEST_PATH))

    assert names == {  # nosec B101 - pytest assertion
        PACKAGE_MANIFEST_PATH,
        "schemas/input.schema.json",
        "schemas/output.schema.json",
        "src/regex_workshop.py",
        "fixtures/basic.json",
    }
    assert package["format"] == "opaltool"  # nosec B101 - pytest assertion
    assert package["core_api"] == "opal2.core.v1"  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_package_verifier_rejects_tampered_payload(tmp_path):
    package_path = tmp_path / "tampered.opaltool"
    export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, package_path)

    members = _read_package_members(package_path)
    members["src/regex_workshop.py"] = b"tampered"
    _write_package_members(package_path, members)

    with pytest.raises(ToolPackageError, match="integrity verification failed"):
        verify_opaltool_package(package_path)


@pytest.mark.unit
@pytest.mark.opal2
def test_package_verifier_rejects_path_traversal(tmp_path):
    package_path = tmp_path / "unsafe.opaltool"
    with ZipFile(package_path, "w") as archive:
        archive.writestr("../escape.py", "pass")

    with pytest.raises(ToolPackageError, match="unsafe package member"):
        verify_opaltool_package(package_path)


@pytest.mark.unit
@pytest.mark.opal2
def test_package_verifier_rejects_normalized_member_alias(tmp_path):
    package_path = tmp_path / "normalized-alias.opaltool"
    with ZipFile(package_path, "w") as archive:
        archive.writestr("src//tool.py", "pass")

    with pytest.raises(ToolPackageError, match="unsafe package member"):
        verify_opaltool_package(package_path)


@pytest.mark.unit
@pytest.mark.opal2
def test_package_builder_requires_explicit_new_destination(tmp_path):
    package_path = tmp_path / "existing.opaltool"
    package_path.write_bytes(b"existing")
    tool = RegexWorkshopTool()

    with pytest.raises(ToolPackageError, match="refusing to overwrite"):
        build_opaltool_package(
            tool,
            package_path,
            entrypoint="modules.opal2.tools.regex_workshop:RegexWorkshopTool",
            implementation_files={"src/regex_workshop.py": "pass"},
        )


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.parametrize(
    "field_name, field_value, expected_error",
    [
        ("core_api", "opal2.core.v99", "unsupported core API"),
        ("activation", "execute", "activation must remain inspect-only"),
    ],
)
def test_package_verifier_rejects_incompatible_header(
    tmp_path, field_name, field_value, expected_error
):
    package_path = tmp_path / "incompatible.opaltool"
    export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, package_path)
    members = _read_package_members(package_path)
    package = json.loads(members[PACKAGE_MANIFEST_PATH])
    package[field_name] = field_value
    _replace_package_manifest(members, package)
    _write_package_members(package_path, members)

    with pytest.raises(ToolPackageError, match=expected_error):
        verify_opaltool_package(package_path)


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.parametrize(
    "field_name, field_value, expected_error",
    [
        ("capabilities", "regex-generation", "array of strings"),
        ("side_effects", ["network", 42], "array of strings"),
        ("deterministic", "yes", "must be a boolean"),
        ("runtime", ["python"], "must be a string"),
    ],
)
def test_package_verifier_rejects_malformed_tool_manifest(
    tmp_path, field_name, field_value, expected_error
):
    package_path = tmp_path / "malformed-manifest.opaltool"
    export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, package_path)
    members = _read_package_members(package_path)
    package = json.loads(members[PACKAGE_MANIFEST_PATH])
    package["tool"][field_name] = field_value
    _replace_package_manifest(members, package)
    _write_package_members(package_path, members)

    with pytest.raises(ToolPackageError, match=expected_error):
        verify_opaltool_package(package_path)


@pytest.mark.unit
@pytest.mark.opal2
def test_package_verifier_requires_implementation_payload(tmp_path):
    package_path = tmp_path / "missing-implementation.opaltool"
    export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, package_path)
    members = _read_package_members(package_path)
    package = json.loads(members[PACKAGE_MANIFEST_PATH])
    members.pop("src/regex_workshop.py")
    package["integrity"]["files"].pop("src/regex_workshop.py")
    _replace_package_manifest(members, package)
    _write_package_members(package_path, members)

    with pytest.raises(ToolPackageError, match="implementation member"):
        verify_opaltool_package(package_path)


@pytest.mark.unit
@pytest.mark.opal2
def test_package_verifier_rejects_undeclared_payload_class(tmp_path):
    package_path = tmp_path / "unsupported-payload.opaltool"
    export_builtin_tool(REGEX_WORKSHOP_TOOL_ID, package_path)
    members = _read_package_members(package_path)
    package = json.loads(members[PACKAGE_MANIFEST_PATH])
    unsupported_data = b"not part of the package contract"
    members["docs/note.txt"] = unsupported_data
    package["integrity"]["files"]["docs/note.txt"] = {
        "sha256": hashlib.sha256(unsupported_data).hexdigest(),
        "size": len(unsupported_data),
    }
    _replace_package_manifest(members, package)
    _write_package_members(package_path, members)

    with pytest.raises(ToolPackageError, match="unsupported package payload"):
        verify_opaltool_package(package_path)
