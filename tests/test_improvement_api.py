"""
Tests for Code Improvement Engine API
"""

import pytest
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient

from src.improvement.api import router


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
        json={"file_path": "/nonexistent/file.py"}
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
        json={"directory": "/nonexistent/directory"}
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
