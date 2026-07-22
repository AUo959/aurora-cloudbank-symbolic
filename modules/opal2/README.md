# OPAL2 Tool Foundry

> **Current direction:** OPAL2 is the standalone **Tool Foundry** for building,
> registering, validating, and running portable tools. The visualization stack
> in this directory is its first reference tool, not the full product identity.
> See [OPAL2 Tool Foundry Architecture](../../docs/architecture/OPAL2_FOUNDRY_ARCHITECTURE.md).

## Current implementation status

Phase 1 provides a portable tool manifest, explicit trusted-tool registry,
execution provenance, and the `opal2.glyph.render` reference tool. Phase 2 adds
the deterministic `opal2.regex.workshop` tool and the first `.opaltool`
transport format. The standalone API exposes tool discovery and execution
under `/tools` while preserving the existing `/generate`, `/render`, cache,
plugin, and WebSocket routes.

`.opaltool` version 0.1 supports deterministic export and integrity inspection
only. Package activation, publisher signatures, isolated workers, and the
Aurora adapter remain planned work. The legacy dynamic plugin loader is not a
trusted package-installation boundary. See
[OPAL2 Tool Package Specification](../../docs/architecture/OPAL2_TOOL_PACKAGE_SPEC.md).

## Glyph visualization reference tool

The surviving OPAL2 visualization stack is a quantum-enhanced rendering
framework developed in Aurora CloudBank. It supplies the first foundry tool and
retains its rendering, plugin, cache, configuration, and WebSocket surfaces for
compatibility.

## 🚀 Key Features

### 🌟 **Quantum-Enhanced Rendering**

- **Quantum Coherence Visualization**: Real-time quantum state visualization with coherence matrices
- **Entanglement Rendering**: Visual representation of quantum entanglement between particles
- **Superposition States**: Multi-state visualization with amplitude and phase information
- **Quantum Field Visualization**: Interactive quantum field rendering with particle effects

### 🔧 **Modular Plugin Architecture**

- **Dynamic Plugin Loading**: Hot-swappable renderer plugins
- **Built-in Renderers**: WebGL, Canvas 2D, SVG, and Quantum Field renderers
- **Custom Plugin Support**: Easy development of custom visualization plugins
- **Plugin Validation**: Automatic plugin validation and dependency management

### ⚙️ **Advanced Configuration Management**

- **Hot-Reload Support**: Real-time configuration updates without restart
- **Schema Validation**: Comprehensive configuration validation with custom rules
- **Multiple Formats**: Support for YAML, JSON, and TOML configuration files
- **Change Callbacks**: Event-driven configuration change handling

### 🌐 **FastAPI Integration**

- **RESTful API**: Complete API for rendering and glyph management
- **WebSocket Support**: Real-time updates and interactive visualization
- **Async Operations**: Non-blocking rendering and cache operations
- **Demo Interface**: Built-in web interface for testing and demonstration

## 📁 **Architecture Overview**

```
modules/opal2/
├── api/
│   └── opal2_api.py           # FastAPI integration with WebSocket support
├── glyph_core.py              # Core glyph generation and processing
├── glyph_cache.py             # Persistent glyph caching system
├── quantum_renderer.py        # Advanced quantum-enhanced rendering engine
├── plugin_system.py           # Dynamic plugin loading and management
├── config_manager.py          # Configuration management with validation
└── tests/
    └── test_opal2_system.py   # Comprehensive test suite
```

## 🔧 **Quick Start**

### 1. Installation

```bash
# Install required dependencies
pip install -r requirements.txt

# Install additional dependencies for Opal2
pip install fastapi uvicorn websockets watchdog pyyaml toml
```

### 2. Configuration Setup

```python
from modules.opal2.config_manager import ConfigurationManager

# Initialize configuration manager
config_manager = ConfigurationManager()

# Create default configurations
config_manager.create_default_config("opal2_graphics")
config_manager.create_default_config("plugin_system")
config_manager.create_default_config("api")
```

### 3. Basic Usage

```python
from modules.opal2.quantum_renderer import QuantumRenderer
from modules.opal2.plugin_system import PluginSystem

# Initialize components
renderer = QuantumRenderer()
plugin_system = PluginSystem()

# Create glyph data
glyph_data = {
    "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
    "indices": [0, 1, 2, 3],
    "dimensions": 2
}

# Render with quantum enhancement
result = await renderer.render_async(
    glyph_data=glyph_data,
    renderer="webgl",
    dimensions={"width": 800, "height": 600},
    quantum_params={"coherence_factor": 0.8}
)
```

### 4. API Server

```python
from modules.opal2.api.opal2_api import app
import uvicorn

# Run the API server
uvicorn.run(app, host="127.0.0.1", port=8001)
```

## 📚 **API Documentation**

### Core Endpoints

#### `POST /render`

Render a glyph with quantum enhancement.

**Request Body:**

```json
{
  "glyph_data": {
    "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
    "indices": [0, 1, 2, 3]
  },
  "renderer_type": "webgl",
  "dimensions": {"width": 800, "height": 600},
  "quantum_params": {
    "coherence_factor": 0.8,
    "entanglement_strength": 0.6
  }
}
```

**Response:**

```json
{
  "success": true,
  "result": "...",
  "cache_key": "render_abc123",
  "quantum_metrics": {
    "coherence_score": 0.85,
    "entanglement_score": 0.6,
    "quantum_fidelity": 0.92
  }
}
```

#### `POST /generate`

Generate a new glyph from symbolic expression.

**Request Body:**

```json
{
  "symbolic_expression": "x^2 + y^2",
  "style_params": {"color": "blue", "width": 2},
  "quantum_enhancement": true
}
```

#### `GET /plugins`

List available renderer plugins.

**Response:**

```json
{
  "plugins": {
    "webgl_renderer": {
      "name": "webgl_renderer",
      "version": "1.0.0",
      "status": "loaded"
    }
  }
}
```

#### `WebSocket /ws`

Real-time updates and interactive visualization.

**Message Types:**

- `ping/pong`: Keep-alive messages
- `render_complete`: Rendering completion notifications
- `subscribe`: Channel subscription

## 🔌 **Plugin Development**

### Creating a Custom Renderer Plugin

```python
from modules.opal2.plugin_system import RendererPlugin, PluginInfo, PluginType

class MyCustomRenderer(RendererPlugin):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="my_custom_renderer",
            version="1.0.0",
            author="Your Name",
            description="Custom visualization renderer",
            plugin_type=PluginType.RENDERER,
            capabilities=["custom_effects", "high_performance"]
        )

    async def render(self, data: Dict[str, Any], context: Dict[str, Any]) -> str:
        # Your custom rendering logic here
        return "custom_rendered_output"

    def get_supported_formats(self) -> List[str]:
        return ["custom_format"]

# Register the plugin
plugin_system = PluginSystem()
plugin_system.register_plugin("my_custom_renderer", MyCustomRenderer())
```

### Plugin Configuration

> **Compatibility surface only:** these settings belong to the legacy
> visualization plugin loader. They do not provide package signatures,
> sandboxing, or activation trust for `.opaltool` artifacts. Keep dynamic
> loading disabled for untrusted code.

```yaml
# config/plugin_system.yaml
plugins:
  auto_load: true
  directories:
    - "plugins"
    - "modules/opal2/plugins"
  blacklist: []
  whitelist: []

security:
  allow_dynamic_loading: false
  require_signatures: false
  sandbox_mode: false
```

## ⚙️ **Configuration Reference**

### Opal2 Graphics Configuration

```yaml
# config/opal2_graphics.yaml
renderer:
  default_engine: "webgl"
  quantum_enhancement: true
  performance_mode: "balanced"  # fast, balanced, quality

canvas:
  width: 800
  height: 600
  background_color: "#000000"

quantum:
  coherence_factor: 0.8
  entanglement_strength: 0.6
  superposition_depth: 3
  decoherence_rate: 0.1

effects:
  particle_systems: true
  field_visualization: true
  interference_patterns: true
```

### API Configuration

The current standalone runtime is launched on port 8001. The CORS and rate
limiting fields below are forward-looking configuration schema examples; they
are not enforcement controls in the Phase 2.1 API.

```yaml
# config/api.yaml
server:
  host: "127.0.0.1"
  port: 8001
  debug: false

cors:
  enabled: true
  origins: ["*"]

rate_limiting:
  enabled: true
  requests_per_minute: 60

websocket:
  enabled: true
  max_connections: 100
```

## 🧪 **Testing**

### Running Tests

```bash
# Run all tests
pytest tests/test_opal2_system.py -v

# Run specific test categories
pytest tests/test_opal2_system.py::TestQuantumRenderer -v
pytest tests/test_opal2_system.py::TestPluginSystem -v
pytest tests/test_opal2_system.py::TestConfigurationManager -v

# Run integration tests
pytest tests/test_opal2_system.py::TestIntegration -v

# Run performance tests
pytest tests/test_opal2_system.py::TestPerformance -v
```

### Test Coverage

The test suite covers:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **Performance Tests**: Load and concurrent rendering tests
- **API Tests**: FastAPI endpoint testing
- **Plugin Tests**: Plugin system functionality

## 🎨 **Quantum Rendering Features**

### Coherence Visualization

```python
quantum_params = {
    "coherence_factor": 0.8,  # 0.0 to 1.0
    "coherence_preservation": True
}
```

### Entanglement Rendering

```python
quantum_params = {
    "entanglement_strength": 0.6,  # 0.0 to 1.0
    "entanglement_rendering": True
}
```

### Superposition States

```python
quantum_params = {
    "superposition_depth": 3,  # Number of states
    "superposition_visualization": True
}
```

### Quantum Field Effects

```python
renderer_type = "quantum_field"
quantum_params = {
    "field_intensity": 0.8,
    "particle_density": 0.5,
    "field_visualization": True
}
```

## 🔄 **Hot-Reload Configuration**

```python
from modules.opal2.config_manager import ConfigurationManager

# Enable hot-reload
config_manager = ConfigurationManager()
config_manager.enable_hot_reload()

# Register change callback
def on_config_change(event):
    print(f"Configuration changed: {event.changed_keys}")
    # Update components with new configuration

config_manager.register_change_callback("opal2_graphics", on_config_change)
```

## 📈 **Performance Optimization**

### Caching Strategy

- **Glyph Cache**: Persistent caching of generated glyphs
- **Render Cache**: Caching of rendered outputs
- **Plugin Cache**: Caching of loaded plugins

### Async Operations

- **Non-blocking Rendering**: Async rendering pipeline
- **Concurrent Processing**: Multiple simultaneous renders
- **WebSocket Updates**: Real-time progress updates

### Memory Management

- **Efficient Data Structures**: Optimized data handling
- **Garbage Collection**: Automatic cleanup of unused resources
- **Resource Pooling**: Reuse of rendering resources

## 🔒 **Current Security Boundary**

- Mutating HTTP routes require the standalone CSRF bearer-token contract.
- The service refuses missing `CSRF_SECRET_KEY` and `WS_AUTH_SECRET` values.
- Foundry tools are registered explicitly in-process; no arbitrary package is
  discovered or imported.
- `.opaltool` 0.1 verification checks deterministic structure, SHA-256
  integrity, size limits, and path/symlink safety without extracting or
  executing package code.
- Publisher signatures, dependency/SBOM validation, rate limiting, CORS
  policy, isolated workers, and third-party activation remain deferred. The
  legacy plugin loader is not a security boundary.

## 🚀 **Production Deployment**

### Docker Compose

OPAL2 has a dedicated non-root image and an opt-in profile. It remains a
separate process, installs the bounded `requirements-opal2.txt` runtime set
through the generated `requirements-opal2.lock` hash lock, and publishes only
to loopback by default. Regenerate the lock with `make opal2-lock` after an
intentional dependency change.

```bash
export CSRF_SECRET_KEY="$(openssl rand -hex 32)"
export WS_AUTH_SECRET="$(openssl rand -hex 32)"
docker compose --profile opal2 up --build opal2

curl --fail http://127.0.0.1:8001/health
curl --fail http://127.0.0.1:8001/tools
```

### Environment Variables

```bash
export OPAL2_CONFIG_DIR="/app/config"
export OPAL2_PLUGIN_DIR="/app/plugins"
export OPAL2_CACHE_DIR="/app/cache"
export OPAL2_LOG_LEVEL="INFO"
export CSRF_SECRET_KEY="<strong deployment secret>"
export WS_AUTH_SECRET="<strong deployment secret>"
```

The four `OPAL2_*` path/log variables document the intended configuration
surface; the Phase 2.1 service does not yet consume all of them.

## 📋 **Foundry Roadmap**

### Phase 1: executable Foundry spine ✅

- [x] Portable manifest and tool contract
- [x] Explicit trusted registry and execution provenance
- [x] Glyph renderer reference adapter and standalone HTTP routes

### Phase 2 / 2.1: generality, packaging, and landing ✅

- [x] Deterministic regex workshop as a non-renderer reference tool
- [x] Deterministic inspect-only `.opaltool` 0.1 export and verification
- [x] Dedicated standalone container, Compose profile, and fail-closed CI gate
- [ ] Authoring scaffold and full schema-conformance harness
- [ ] Aurora policy adapter rather than direct runtime imports

### Phase 3: portability and trust

- [ ] Publisher identity, asymmetric signatures, dependency lock, and SBOM
- [ ] Isolated execution with capability and resource controls
- [ ] Neutral and Aurora clean-room conformance with matching provenance

### Phase 4: workshop at scale

- [ ] Scaffold/build/test/run/export/publish workflows
- [ ] External artifact registry and queue-backed workers
- [ ] Independent neutral core package after conformance is green

Visualization enhancements such as 3D rendering, collaboration, and AI glyph
generation remain possible reference-tool work, not the OPAL2 product
definition.

## 🤝 **Contributing**

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/test_opal2_system.py

# Run linting
flake8 modules/opal2/
black modules/opal2/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Write tests for new features

## 📄 **License**

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 **Acknowledgments**

- Aurora CloudBank Symbolic team
- Quantum computing research community
- FastAPI and modern Python ecosystem
- Contributors and testers

## 📞 **Support**

For questions, issues, or contributions:

- Open an issue on GitHub
- Join our Discord community
- Email: <support@aurora-cloudbank.dev>

---

**Built with ❤️ by the Aurora CloudBank team**

*Quantum-enhanced visualization for the future of symbolic computing*
