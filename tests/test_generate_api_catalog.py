import json
from pathlib import Path

from scripts import generate_api_catalog as generator


def test_default_output_directory_is_tracked_docs_api() -> None:
    assert generator.DEFAULT_OUTPUT_DIR == generator.project_root / "docs" / "api"


def test_relative_output_directory_uses_invocation_cwd(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(generator, "invocation_cwd", tmp_path)
    assert generator.resolve_output_dir("preview") == (tmp_path / "preview").resolve()


def test_generate_catalog_records_source_metadata(monkeypatch, tmp_path: Path) -> None:
    schema = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.2.3", "description": "test"},
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }
    source_commit = "0123456789abcdef0123456789abcdef01234567"
    monkeypatch.setattr(generator.app, "openapi", lambda: schema)
    monkeypatch.setattr(generator, "get_source_commit", lambda: source_commit)

    catalog = generator.generate_api_catalog(tmp_path)

    assert catalog["source_commit"] == source_commit
    assert catalog["generated_at"] == catalog["generated"]
    assert catalog["total_routes"] == 1

    saved_schema = json.loads((tmp_path / "api_schema.json").read_text(encoding="utf-8"))
    saved_catalog = json.loads((tmp_path / "API_CATALOG.json").read_text(encoding="utf-8"))
    saved_markdown = (tmp_path / "API_CATALOG.md").read_text(encoding="utf-8")

    assert saved_schema["x-source-commit"] == source_commit
    assert saved_schema["x-generated-at"] == catalog["generated_at"]
    assert saved_catalog == catalog
    assert f"**Source Commit:** `{source_commit}`" in saved_markdown
