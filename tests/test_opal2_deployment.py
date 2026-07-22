"""Static deployment-contract tests for the standalone OPAL2 service."""

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_compose_service_is_explicit_and_standalone():
    """Compose must expose OPAL2 only through its opt-in standalone profile."""

    compose = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text())
    service = compose["services"]["opal2"]

    assert service["profiles"] == ["opal2"]
    assert service["build"]["dockerfile"] == "Dockerfile.opal2"
    assert service["ports"] == ["127.0.0.1:8001:8001"]
    assert set(service["environment"]) == {"CSRF_SECRET_KEY", "WS_AUTH_SECRET"}
    assert "localhost:8001/health" in " ".join(service["healthcheck"]["test"])
    assert "depends_on" not in service


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_image_runs_non_root_on_the_canonical_port():
    """The dedicated image must preserve the standalone API entrypoint."""

    dockerfile = (REPO_ROOT / "Dockerfile.opal2").read_text()

    assert "USER opal2user" in dockerfile
    assert "EXPOSE 8001" in dockerfile
    assert "requirements-opal2.txt" in dockerfile
    assert "requirements.txt" not in dockerfile.replace(
        "requirements-opal2.txt", ""
    )
    assert '"modules.opal2.api.opal2_api:app"' in dockerfile
    assert '"--port", "8001"' in dockerfile
    assert "localhost:8001/health" in dockerfile


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_runtime_dependencies_are_separate_from_the_monolith():
    """The microservice image must install only its declared runtime surface."""

    requirements = (
        REPO_ROOT / "requirements-opal2.txt"
    ).read_text().splitlines()
    dependency_names = {
        line.split("<", 1)[0].split(">", 1)[0].split("[", 1)[0]
        for line in requirements
        if line and not line.startswith("#")
    }

    assert dependency_names == {
        "fastapi",
        "numpy",
        "pydantic",
        "pyyaml",
        "slowapi",
        "starlette",
        "uvicorn",
    }
