# Aurora Interoperability Support Guide

This document outlines how the project integrates with key tooling and services, beginning with server configuration and code linting. It then highlights priorities for maintaining smooth interoperability across the ecosystem.

## 1. Uvicorn Integration

- **FastAPI Servers**: Several modules expose FastAPI apps. Example startup command from the Sonnet 4 status guide:

  ```bash
  uvicorn aurora_api:app --host 0.0.0.0 --port 8000
  ```

- **Docker Support**: The `Dockerfile_aurora_gui_cloudhub` runs the GUI service with Uvicorn:

  ```Dockerfile
  CMD ["uvicorn", "aurora_gui_cloudhub_fastapi:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

- **Startup Scripts**: Scripts like `enable_sonnet4.sh` launch the API with Uvicorn if it is not already running.
- **Customization Tips**:
  - Host and port can be overridden with environment variables (`UVICORN_HOST`, `UVICORN_PORT`).
  - Use `--reload` for hot-reloading during development.

## 2. Flake8 Linting

- **Configuration**: The `.flake8` file sets basic options:

  ```ini
  [flake8]
  max-line-length = 120
  exclude = deploykit_tmp/*,.venv/*
  ```

- **Pre-commit**: Flake8 runs automatically via `.pre-commit-config.yaml` to ensure consistent style before commits.
- **CI Pipeline**: GitHub Actions (`python-ci.yml` and `enhanced-ci.yml`) install flake8 and run lint checks on every push.
- **Local Usage**: Run `flake8 .` at the repository root to check for issues before committing.

## 3. General Interoperability Priorities

1. **Python ↔️ Node Integration**
   - The Node.js command node (`services/command_node/`) operates alongside Python services using Docker Compose.
   - Ensure APIs remain stable so both ecosystems can communicate reliably.
2. **Instance Bridge**
   - `modules/instance_bridge` provides WebSocket relay tools for cross-instance messaging.
   - Run `python -m modules.instance_bridge.bridge_server` to start the relay service.
3. **Environment Consistency**
   - Use the provided `Dockerfile_aurora_gui_cloudhub` and `docker-compose.yml` to mirror production locally.
   - Python dependencies are listed in `requirements.txt` and Node dependencies in `package.json`.
4. **Testing & Validation**
   - The CI workflows run both Python and Node tests. Keep tests passing to maintain interoperability guarantees.
5. **Future Enhancements**
   - Consider standardizing configuration via environment files for all services.
   - Expand schema validation in `modules/symbolic_core` to aid external integrations.

This guide should serve as a starting point for ensuring the Aurora ecosystem remains interoperable across tools and services.
