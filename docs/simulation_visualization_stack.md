# Simulation Visualization Stack

To render Aurora's simulations with real-time graphics and audio, use an open-source engine that integrates with the existing Python and Node.js services in this repository.

## Graphics and Rendering
- **Game engine**: Godot Engine (MIT License) supplies 3D and 2D rendering, a built-in editor, Python-like GDScript, Bullet Physics, and audio. It exports to desktop, web, and mobile.
- **Alternatives**: Unity or Unreal Engine offer advanced tooling but are not fully open source.
- **Modeling**: Create and edit assets with Blender. Export to open formats such as glTF or FBX.

## Physics and Simulation
- Start with Godot's built-in physics. Keep the core simulation logic decoupled so the engine can change without rewriting algorithms.

## Audio
- Godot includes positional audio and mixing. Additional libraries like OpenAL or FMOD can be integrated for more complex requirements.

## Integration with Existing Services
- Expose simulation data from Python modules through FastAPI or the Node.js command node. Use REST or WebSocket endpoints.
- In the engine, scripts poll or listen to those endpoints and update the world state.

## Development and Deployment Workflow
- Maintain orchestration with Docker Compose to run Python, Node.js, and the future engine service together.
- Track large assets with Git LFS.
- Add CI workflows that build and, if possible, run headless tests of the game project.

## Laying the Groundwork
- Prototype a small project that connects to your services.
- Define a JSON-based format for state updates.
- Set up export scripts in Blender to convert models automatically.
- Document endpoints and usage under the `docs/` directory.
- Expand unit tests and consider headless integration tests for the engine.

## Optional Capabilities
- Support multiplayer with WebSocket or UDP networking.
- Explore VR/AR via Godot's experimental features.
- Use the existing telemetry system to log simulation events and user interactions.
