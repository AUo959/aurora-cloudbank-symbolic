"""Tests for the root declaration gate (scripts/check_root_declaration.py)."""
from __future__ import annotations

import textwrap

from scripts.check_root_declaration import (
    check,
    dependency_files_of,
    load_registry,
    root_objects_of,
)

REGISTRY_DOC = textwrap.dedent(
    """\
    version: 1
    root_objects:
      - "src"
      - "docs"
      - "requirements.txt"
    dependency_files:
      - "requirements.txt"
    """
)


def write_registry(tmp_path, doc=REGISTRY_DOC):
    path = tmp_path / "root_registry.yaml"
    path.write_text(doc, encoding="utf-8")
    return path


def registry_set(tmp_path):
    return load_registry(write_registry(tmp_path))


def test_declared_set_matches_tracked_set(tmp_path):
    tracked = ["src/aurora/x.py", "docs/guide.md", "requirements.txt"]
    assert check(tracked, registry_set(tmp_path)) == []


def test_undeclared_root_object_fails(tmp_path):
    tracked = ["src/x.py", "docs/a.md", "requirements.txt", "scratchpad/notes.md"]
    violations = check(tracked, registry_set(tmp_path))
    assert any("UNDECLARED root objects" in v and "scratchpad" in v for v in violations)


def test_stale_declaration_fails(tmp_path):
    tracked = ["src/x.py", "requirements.txt"]  # docs/ removed from tree
    violations = check(tracked, registry_set(tmp_path))
    assert any("STALE declarations" in v and "docs" in v for v in violations)


def test_new_dependency_file_fails(tmp_path):
    tracked = ["src/x.py", "docs/a.md", "requirements.txt", "requirements-nexus.txt"]
    violations = check(tracked, registry_set(tmp_path))
    assert any("UNDECLARED dependency files" in v and "requirements-nexus.txt" in v for v in violations)


def test_removed_dependency_file_fails(tmp_path):
    tracked = ["src/x.py", "docs/a.md"]  # requirements.txt gone
    violations = check(tracked, registry_set(tmp_path))
    assert any("STALE dependency-file declarations" in v for v in violations)


def test_lock_files_count_as_dependency_files():
    assert dependency_files_of({"requirements-opal2.lock", "requirements.txt", "setup.py"}) == {
        "requirements-opal2.lock",
        "requirements.txt",
    }


def test_nested_paths_collapse_to_root_object():
    assert root_objects_of(["src/aurora/deep/mod.py", "src/main.py", "README.md"]) == {
        "src",
        "README.md",
    }


def test_mini_parser_handles_registry_without_pyyaml(tmp_path, monkeypatch):
    import builtins

    real_import = builtins.__import__

    def no_yaml(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("no yaml")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_yaml)
    registry = load_registry(write_registry(tmp_path))
    assert registry["root_objects"] == {"src", "docs", "requirements.txt"}
    assert registry["dependency_files"] == {"requirements.txt"}
