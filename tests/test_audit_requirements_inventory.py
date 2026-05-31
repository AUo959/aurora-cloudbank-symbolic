from pathlib import Path

from scripts.audit_requirements_inventory import collect_missing_references


def test_current_requirements_inventory_references_are_valid() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    assert collect_missing_references(repo_root) == []


def test_missing_requirements_reference_is_reported(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi>=0.128.8\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("Install from requirements-missing.txt\n", encoding="utf-8")

    missing = collect_missing_references(tmp_path, ("README.md",))

    assert len(missing) == 1
    assert missing[0].path == Path("README.md")
    assert missing[0].line_number == 1
    assert missing[0].reference == "requirements-missing.txt"
