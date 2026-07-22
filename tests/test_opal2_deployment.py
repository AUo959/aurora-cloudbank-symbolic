"""Static deployment-contract tests for the standalone OPAL2 service."""

import re
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

    assert service["profiles"] == ["opal2"]  # nosec B101 - pytest assertion
    assert service["build"]["dockerfile"] == "Dockerfile.opal2"  # nosec B101 - pytest assertion
    assert service["ports"] == ["127.0.0.1:8001:8001"]  # nosec B101 - pytest assertion
    assert set(service["environment"]) == {  # nosec B101 - pytest assertion
        "CSRF_SECRET_KEY",
        "WS_AUTH_SECRET",
    }
    assert "localhost:8001/health" in " ".join(  # nosec B101 - pytest assertion
        service["healthcheck"]["test"]
    )
    assert "depends_on" not in service  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_image_runs_non_root_on_the_canonical_port():
    """The dedicated image must preserve the standalone API entrypoint."""

    dockerfile = (REPO_ROOT / "Dockerfile.opal2").read_text()

    assert "USER opal2user" in dockerfile  # nosec B101 - pytest assertion
    assert "EXPOSE 8001" in dockerfile  # nosec B101 - pytest assertion
    assert "requirements-opal2.lock" in dockerfile  # nosec B101 - pytest assertion
    assert "--only-binary=:all:" in dockerfile  # nosec B101 - pytest assertion
    assert "--require-hashes" in dockerfile  # nosec B101 - pytest assertion
    assert "@sha256:" in dockerfile  # nosec B101 - pytest assertion
    assert '"modules.opal2.api.opal2_api:app"' in dockerfile  # nosec B101 - pytest assertion
    assert '"--port", "8001"' in dockerfile  # nosec B101 - pytest assertion
    assert "localhost:8001/health" in dockerfile  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_runtime_dependencies_are_separate_from_the_monolith():
    """The microservice image must install only its declared runtime surface."""

    requirements = (
        REPO_ROOT / "requirements-opal2.txt"
    ).read_text().splitlines()
    dependency_names = {
        re.split(r"[\[<>=!~]", line, maxsplit=1)[0]
        for line in requirements
        if line and not line.startswith("#")
    }

    assert dependency_names == {  # nosec B101 - pytest assertion
        "fastapi",
        "numpy",
        "pydantic",
        "pyyaml",
        "slowapi",
        "starlette",
        "uvicorn",
    }

    lockfile = (REPO_ROOT / "requirements-opal2.lock").read_text()
    assert "--hash=sha256:" in lockfile  # nosec B101 - pytest assertion
    assert "fastapi==" in lockfile  # nosec B101 - pytest assertion
    assert "numpy==" in lockfile  # nosec B101 - pytest assertion
    assert "slowapi==" in lockfile  # nosec B101 - pytest assertion
