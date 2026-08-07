"""
Tests for Code Improvement Engine API
"""

import pytest
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient

from src.improvement.api import router


@pytest.fixture(autouse=True)
def confine_analysis_to_tempdir(monkeypatch):
    """Point the API's safe root at the temp directory these fixtures write to.

    The routes used to admit any absolute path under a temp directory by
    skipping the containment check outright — a bypass in production code,
    reported by CodeQL as py/path-injection. That is gone.

    Instead the tests declare their own root. The containment check still runs
    on every request; it is simply enforcing a root that covers the fixture
    files (both `tmp_path` and `tempfile.NamedTemporaryFile` live here). The
    widened root is scoped to this test module — production keeps SAFE_ROOT,
    with no path exempt from the check.
    """
    monkeypatch.setenv("AURORA_IMPROVEMENT_ROOT", tempfile.gettempdir())


@pytest.fixture
def client():
    """Create test client with improvement router"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def temp_python_file():
    """Create temporary Python file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def example():
    max_items = 9999
    return max_items
""")
        temp_path = Path(f.name)
    
    yield temp_path
    
    if temp_path.exists():
        temp_path.unlink()


@pytest.mark.api
@pytest.mark.improvement
def test_health_endpoint(client):
    """Test engine health endpoint"""
    response = client.get("/improvements/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "patterns_registered" in data
    assert data["patterns_registered"] > 0


@pytest.mark.api
@pytest.mark.improvement
def test_list_categories(client):
    """Test listing improvement categories"""
    response = client.get("/improvements/categories")
    assert response.status_code == 200
    
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert "refactoring" in categories


@pytest.mark.api
@pytest.mark.improvement
def test_list_severities(client):
    """Test listing severity levels"""
    response = client.get("/improvements/severities")
    assert response.status_code == 200
    
    severities = response.json()
    assert isinstance(severities, list)
    assert len(severities) > 0
    assert "low" in severities


@pytest.mark.api
@pytest.mark.improvement
def test_list_patterns(client):
    """Test listing registered patterns"""
    response = client.get("/improvements/patterns")
    assert response.status_code == 200
    
    patterns = response.json()
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    assert all("name" in pat for pat in patterns)
    assert all("category" in pat for pat in patterns)


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_file_endpoint(client, temp_python_file):
    """Test file analysis endpoint"""
    response = client.post(
        "/improvements/analyze-file",
        json={"file_path": str(temp_python_file)}
    )
    
    assert response.status_code == 200
    suggestions = response.json()
    
    assert isinstance(suggestions, list)
    if len(suggestions) > 0:
        assert "file_path" in suggestions[0]
        assert "category" in suggestions[0]


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_file_not_found(client):
    """Test file analysis with non-existent file"""
    response = client.post(
        "/improvements/analyze-file",
        json={"file_path": "nonexistent/file.py"}  # Use relative path
    )
    
    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_file_with_filtering(client, temp_python_file):
    """Test file analysis with confidence filtering"""
    response = client.post(
        "/improvements/analyze-file",
        json={
            "file_path": str(temp_python_file)
        }
    )
    
    assert response.status_code == 200
    suggestions = response.json()
    
    # All suggestions should have confidence score
    for suggestion in suggestions:
        assert "confidence_score" in suggestion
        assert 0.0 <= suggestion["confidence_score"] <= 1.0


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_directory_endpoint(client, tmp_path):
    """Test directory analysis endpoint"""
    # Create test files
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text("def func(): x = 5000; return x")
    (test_dir / "file2.py").write_text("def func2(): y = 9999; return y")
    
    response = client.post(
        "/improvements/analyze-directory",
        json={"directory": str(test_dir)}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_files_analyzed" in data
    assert "total_suggestions" in data
    assert "suggestions" in data
    assert data["total_files_analyzed"] >= 2


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_directory_with_patterns(client, tmp_path):
    """Test directory analysis with pattern filter"""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text("def func(): x = 5000; return x")
    
    response = client.post(
        "/improvements/analyze-directory",
        json={
            "directory": str(test_dir)
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_files_analyzed" in data


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_directory_with_category_filter(client, tmp_path):
    """Test directory analysis with category filtering"""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text("def func(): x = 5000; return x")
    
    response = client.post(
        "/improvements/analyze-directory",
        json={
            "directory": str(test_dir),
            "categories": ["readability"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that filtering worked
    assert "suggestions" in data
    for file_suggestions in data["suggestions"].values():
        for suggestion in file_suggestions:
            assert suggestion["category"] == "readability"


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_directory_with_severity_filter(client, tmp_path):
    """Test directory analysis with severity filtering"""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text("def func(): x = 5000; return x")
    
    response = client.post(
        "/improvements/analyze-directory",
        json={
            "directory": str(test_dir),
            "severities": ["high", "critical"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that filtering worked
    assert "suggestions" in data
    for file_suggestions in data["suggestions"].values():
        for suggestion in file_suggestions:
            assert suggestion["severity"] in ["high", "critical"]


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_directory_not_found(client):
    """Test directory analysis with non-existent directory"""
    response = client.post(
        "/improvements/analyze-directory",
        json={"directory": "nonexistent/directory"}  # Use relative path
    )
    
    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.improvement
def test_analyze_directory_summary_statistics(client, tmp_path):
    """Test directory analysis summary includes statistics"""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text("def func(): x = 5000; return x")
    (test_dir / "file2.py").write_text("def func2(): y = 9999; return y")
    
    response = client.post(
        "/improvements/analyze-directory",
        json={"directory": str(test_dir)}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_files_analyzed" in data
    assert "total_suggestions" in data
    assert "by_category" in data
    assert "by_severity" in data
    assert data["total_files_analyzed"] >= 2


@pytest.mark.api
@pytest.mark.improvement
@pytest.mark.security
@pytest.mark.parametrize(
    "pattern",
    [
        "../*.py",
        "../../*.py",
        "**/../*.py",
        # Rooted but NOT absolute on Windows: PurePath("/etc/*.conf").is_absolute()
        # is False there because it carries no drive, so an is_absolute() check
        # alone let this through to rglob(), which raised NotImplementedError —
        # a 500 where a 400 belongs. Caught on windows-latest, not locally.
        "/etc/*.conf",
        # Drive-relative: no root, but a drive. Same blind spot (see #1337).
        "C:foo/*.py",
        "C:/x/*.py",
        # Backslash separators must be read as separators on every platform.
        r"..\..\*.py",
    ],
)
def test_file_patterns_cannot_escape_the_analyzed_directory(client, tmp_path, pattern):
    """A glob pattern must not read files outside the requested directory.

    `directory` is resolved through trusted enumeration, but `file_patterns`
    reached `Path.rglob()` unvalidated — and rglob honours "..". So
    {"directory": "proj", "file_patterns": ["../*.py"]} read proj's siblings,
    and "../../*.py" escaped the configured root entirely, echoing the matched
    absolute paths back in the response.
    """
    project = tmp_path / "proj"
    project.mkdir()
    (project / "a.py").write_text("max_items = 9999\n")

    # Sibling of the analyzed directory — must stay unreachable.
    (tmp_path / "sibling_secret.py").write_text("API_KEY = 'sk-live'\nmax_items = 9999\n")

    response = client.post(
        "/improvements/analyze-directory",
        json={"directory": str(project), "file_patterns": [pattern]},
    )

    # Rejected outright is the intended behaviour; a 200 is only acceptable if
    # nothing outside the directory came back.
    assert response.status_code == 400, (
        f"pattern {pattern!r} should be rejected, got {response.status_code}"
    )

    if response.status_code == 200:
        analyzed = response.json().get("suggestions", {})
        assert not [k for k in analyzed if "sibling_secret" in k], (
            f"pattern {pattern!r} escaped the analyzed directory: {list(analyzed)}"
        )


@pytest.mark.api
@pytest.mark.improvement
@pytest.mark.security
def test_engine_drops_matches_outside_the_directory(tmp_path):
    """The engine filters escaping matches even when handed a bad pattern.

    The API rejects these patterns, but analyze_directory() accepts patterns as
    an argument and cannot assume every caller validated them, so it confirms
    each match resolves inside the directory before reading it.
    """
    from src.improvement import get_improvement_engine

    project = tmp_path / "proj"
    project.mkdir()
    (project / "a.py").write_text("max_items = 9999\n")
    (tmp_path / "secret.py").write_text("API_KEY = 'sk-live'\nmax_items = 9999\n")

    engine = get_improvement_engine()

    contained = engine.analyze_directory(project, ["*.py"])
    assert any("a.py" in key for key in contained)

    escaped = engine.analyze_directory(project, ["../*.py"])
    assert not [key for key in escaped if "secret.py" in key], (
        f"engine returned files outside the directory: {list(escaped)}"
    )
