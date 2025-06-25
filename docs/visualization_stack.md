# Visualization Stack

To visualize Aurora's simulations with real-time 3D rendering, audio, and physics, while integrating the existing Python and Node.js services, follow these guidelines.

## 1. Graphics and Rendering
- **Game Engine**: Use an open-source engine with Python-friendly scripting. [Godot Engine](https://godotengine.org) offers 3D/2D rendering, an editor, and integrates Bullet Physics. Its MIT license aligns with this repository.
- **Modeling and Assets**: Create or edit models in **Blender** and store them in open formats such as `glTF` or `FBX`.
- **Cross-Platform Rendering**: Godot 4 uses Vulkan and can export to desktop, web, and mobile for future deployment flexibility.

## 2. Physics and Simulation
- **Physics Engine**: Rely on Godot's built-in physics (Bullet for 3D). Keep simulation logic separate from physics calls in case a different engine is used later.

## 3. Audio
- **Audio Server**: Godot includes positional audio and mixing. Libraries like OpenAL or FMOD can be added if advanced features are required.

## 4. Integration with Existing Services
- **FastAPI and Node.js**: Continue generating simulation data in the existing Python modules. Expose updates via REST or WebSocket endpoints so the game engine can fetch or receive them.
- **Engine Scripts**: Write Godot scripts that poll these endpoints or subscribe over WebSockets and update the game state accordingly.

## 5. Development Workflow
- **Docker Compose**: Use the current docker-compose setup to orchestrate Python, Node.js, and game engine services for reproducible local and cloud deployments.
- **Version Control**: Track large models, textures, and audio using Git LFS.
- **Automated Builds**: Add a GitHub Actions workflow to build or pack the game project and run headless tests.

## 6. Next Steps
- **Prototype**: Start with a small Godot project that loads simple geometry and communicates with the services via HTTP or WebSocket.
- **Data Format**: Define a consistent JSON format for simulation state. Keep it engine-agnostic so other tools can reuse it.
- **Asset Pipeline**: Configure Blender export scripts that convert models to your engine’s preferred format and commit them to version control.
- **Documentation**: Document API endpoints in `docs/` and illustrate how the engine queries them.
- **Testing**: Expand unit tests for both Python and Node.js modules. Future integration tests can run the engine in headless mode.

## 7. Advanced Capabilities
- **Networked Multiplayer**: If multiple participants interact in the simulation, plan for WebSocket or UDP networking using Godot’s high-level API or custom networking layers.
- **VR/AR Support**: Godot offers experimental VR and AR capabilities if immersive experiences are required.
- **Telemetry**: Use the existing telemetry system to record simulation events and user actions for analysis.

By adopting an MIT-licensed engine like Godot, integrating it with current services, and establishing clear asset and data pipelines, you will create a flexible foundation for future simulation and visualization work without locking into proprietary tools.
