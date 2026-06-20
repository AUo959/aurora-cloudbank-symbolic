# Combined Visualization Package

This guide consolidates the previous visualization documents into a single blueprint for deploying Aurora's simulation graphics.

## 1. Goals

- Provide real-time 3D visuals, physics and audio for Aurora simulations.
- Maintain tight integration with the existing Python and Node.js services.
- Offer a scalable and secure workflow that works locally and in the cloud.

## 2. Core Components

- **Godot 4 Engine** for rendering and physics with scripts written in GDScript or C#.
- **FastAPI services** (`aurora_gui_cloudhub_fastapi.py`) exposing REST and WebSocket APIs.
- **Node.js command node** for runtime orchestration and additional WebSocket channels.
- **Docker Compose** (and optional Kubernetes) to orchestrate these services consistently.

## 3. Asset Pipeline

- Create assets in **Blender** and export to `glTF`.
- Store large binaries using **Git LFS**.
- Maintain a `game/` directory for the Godot project and `game/assets` for models, textures and audio.

## 4. API Integration

- Define typed JSON schemas (e.g. `SymbolicVector`) for state updates.
- Use WebSockets for real-time data and REST for configuration or asset metadata.
- Require authentication tokens when connecting from the engine to backend services.

## 5. Development Workflow

- Use Docker Compose to run Python services, the Node command node and (optionally) a headless Godot container.
- GitHub Actions should run unit tests, headless Godot tests and build Docker images.
- Provide Blender export scripts and Godot export scripts so packaged builds are reproducible.

## 6. Observability

- Centralize logs from Python, Node.js and Godot using the existing telemetry logger.
- Add metrics collection via Prometheus and Grafana or an ELK stack.

## 7. Next Steps

1. Prototype a minimal Godot project that connects to the FastAPI WebSocket.
2. Expand the API schema and document all endpoints in this repository.
3. Build a simple demo scene that visualizes a symbolic simulation.

This combined package lays the groundwork for a robust, enterprise-ready visualization stack while remaining fully open source.
