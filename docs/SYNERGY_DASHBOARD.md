# Aurora Synergy Dashboard

## Overview

The Synergy Dashboard provides system-wide visibility into Aurora's component ecosystem through centralized registry management, dependency tracking, and health monitoring.

**Key Features:**
- Component registration (manual and auto-discovery)
- Dependency graph mapping with conflict detection
- RESTful API for programmatic access
- Health status monitoring
- DLP-compliant audit trails
- OpenTelemetry integration ready

## Quick Start

### Basic Registration

```python
from src.synergy import get_registry, ComponentDependency, ComponentStatus

registry = get_registry()

# Register a component
component = registry.register_component(
    name="my-service",
    version="1.0.0",
    description="My Aurora service",
    dependencies=[
        ComponentDependency(name="core-lib", version="2.0.0")
    ],
    api_endpoints=["/api/my-service"],
    status=ComponentStatus.ACTIVE
)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from src.synergy import synergy_router

app = FastAPI()
app.include_router(synergy_router)

# Now available:
# GET  /synergy/components
# POST /synergy/components
# GET  /synergy/components/{name}
# PUT  /synergy/components/{name}/status
# GET  /synergy/dependencies/{name}
# GET  /synergy/conflicts
# GET  /synergy/export
# GET  /synergy/health
```

## Architecture

### Component Registry

The `ComponentRegistry` provides centralized tracking of all Aurora components:

```python
from src.synergy import get_registry

registry = get_registry()

# List all components
components = registry.list_components()

# Filter by status
active = registry.list_components(status=ComponentStatus.ACTIVE)

# Get specific component
component = registry.get_component("my-service")
```

### Dependency Tracking

Automatic dependency graph construction with cycle detection:

```python
# Get direct dependencies
deps = registry.get_dependencies("my-service")

# Get transitive dependencies
all_deps = registry.get_dependencies("my-service", recursive=True)

# Find what depends on this component
dependents = registry.get_dependents("core-lib")

# Detect conflicts
conflicts = registry.detect_conflicts()
```

### Component Metadata

Each component includes comprehensive metadata:

```python
@dataclass
class ComponentMetadata:
    name: str                    # Unique identifier
    version: str                 # Semantic version
    description: str             # Human-readable description
    module_path: Optional[str]   # Python module path
    dependencies: List           # Component dependencies
    api_endpoints: List[str]     # FastAPI routes
    status: ComponentStatus      # Health status
    registered_at: float         # Registration timestamp
    last_updated: float          # Last modification time
    metadata: Dict               # Custom metadata
    context_tag: Optional[str]   # DLP audit tag
```

## API Reference

### REST Endpoints

#### List Components
```http
GET /synergy/components?status=active
```

**Response:**
```json
[
  {
    "name": "aurora-core",
    "version": "2.0.0",
    "description": "Core Aurora functionality",
    "status": "active",
    "dependencies": [...],
    "api_endpoints": ["/api/core"],
    "registered_at": 1730249600.0,
    "last_updated": 1730249600.0
  }
]
```

#### Register Component
```http
POST /synergy/components
Content-Type: application/json

{
  "name": "new-service",
  "version": "1.0.0",
  "description": "New Aurora service",
  "dependencies": [
    {
      "name": "core-lib",
      "version": "2.0.0",
      "dependency_type": "runtime",
      "required": true
    }
  ],
  "api_endpoints": ["/api/new-service"],
  "status": "active"
}
```

#### Get Component Details
```http
GET /synergy/components/{name}
```

#### Update Component Status
```http
PUT /synergy/components/{name}/status
Content-Type: application/json

{
  "status": "degraded"
}
```

#### Get Dependencies
```http
GET /synergy/dependencies/{name}?recursive=true
```

**Response:**
```json
{
  "component": "my-service",
  "dependencies": ["core-lib", "utils"],
  "dependents": ["other-service"],
  "recursive": true
}
```

#### Detect Conflicts
```http
GET /synergy/conflicts
```

**Response:**
```json
[
  {
    "type": "circular_dependency",
    "component": "service-a",
    "description": "Circular dependency detected involving service-a"
  },
  {
    "type": "missing_dependency",
    "component": "service-b",
    "missing": "nonexistent-lib",
    "description": "service-b depends on unregistered component nonexistent-lib"
  }
]
```

#### Export Registry
```http
GET /synergy/export?context_tag=backup_20251030
```

#### Registry Health
```http
GET /synergy/health
```

**Response:**
```json
{
  "total_components": 15,
  "status_distribution": {
    "active": 12,
    "degraded": 2,
    "error": 1
  },
  "conflicts": 0,
  "healthy": true
}
```

## Component Status

Components can have the following statuses:

- **ACTIVE** - Fully operational
- **INACTIVE** - Not currently running
- **DEGRADED** - Operating but with issues
- **ERROR** - Experiencing failures
- **UNKNOWN** - Status not determined

## Dependency Types

Dependencies are classified by type:

- **RUNTIME** - Required at runtime
- **BUILD** - Required for building
- **OPTIONAL** - Enhances functionality but not required
- **DEV** - Development/testing only

## Auto-Discovery

The registry can automatically discover components by scanning module directories:

```python
from pathlib import Path

# Scan default locations (src/, modules/)
discovered = registry.auto_discover_components()

# Scan custom paths
custom_paths = [Path("custom/components")]
discovered = registry.auto_discover_components(scan_paths=custom_paths)
```

**Component Markers:**

Add these to your Python modules for auto-discovery:

```python
# my_component.py

__component_name__ = "my-component"
__version__ = "1.0.0"
__description__ = "My Aurora component"
__dependencies__ = ["core-lib", "utils"]
```

## Conflict Detection

The registry automatically detects:

### Circular Dependencies
```
A → B → C → A  # Circular!
```

### Missing Dependencies
```
Component X depends on Y, but Y is not registered
```

### Version Conflicts
```
App A requires lib@1.0
App B requires lib@2.0
```

## DLP Integration

All registry operations support DLP context tags for audit trails:

```python
from src.core.native_dlp_export import NativeDLPTracker

dlp_tracker = NativeDLPTracker()
context_tag = dlp_tracker.create_tag(
    operation="component_registration",
    data={"component": "my-service"}
)

registry.register_component(
    name="my-service",
    version="1.0.0",
    description="Service",
    context_tag=context_tag
)
```

## Testing

Run the test suite:

```bash
# All Synergy tests
pytest -m synergy -v

# Registry tests only
pytest tests/test_component_registry.py -v

# API tests only
pytest tests/test_synergy_api.py -v

# With coverage
pytest tests/test_component_registry.py tests/test_synergy_api.py --cov=src/synergy
```

## Integration Examples

### With FastAPI Main App

```python
# aurora_api.py
from fastapi import FastAPI
from src.synergy import synergy_router, get_registry

app = FastAPI(title="Aurora CloudBank")

# Include Synergy Dashboard routes
app.include_router(synergy_router)

# Auto-register this API
@app.on_event("startup")
async def register_api():
    registry = get_registry()
    registry.register_component(
        name="aurora-api",
        version="2.0.0",
        description="Main Aurora FastAPI application",
        api_endpoints=["/api/*"],
        status=ComponentStatus.ACTIVE
    )
```

### With OpenTelemetry

```python
from src.observability import get_telemetry
from src.synergy import get_registry

telemetry = get_telemetry()
registry = get_registry()

# Track component usage with telemetry
with telemetry.trace_operation("component_access"):
    component = registry.get_component("my-service")
    telemetry.record_feature_usage(f"component_{component.name}")
```

### Periodic Health Checks

```python
import asyncio
from src.synergy import get_registry, ComponentStatus

async def health_monitor():
    """Periodic health check for registered components"""
    registry = get_registry()
    
    while True:
        for component in registry.list_components():
            # Check if component is responding
            is_healthy = await check_component_health(component)
            
            new_status = (
                ComponentStatus.ACTIVE if is_healthy 
                else ComponentStatus.DEGRADED
            )
            
            registry.update_component_status(component.name, new_status)
        
        await asyncio.sleep(60)  # Check every minute
```

## Best Practices

### 1. Register at Startup

Register components when they initialize:

```python
@app.on_event("startup")
async def startup():
    registry = get_registry()
    registry.register_component(...)
```

### 2. Use Semantic Versioning

Follow semver for component versions:
```
1.0.0 - Major.Minor.Patch
```

### 3. Document Dependencies

Explicitly declare all dependencies:
```python
dependencies=[
    ComponentDependency("core", "2.0.0", required=True),
    ComponentDependency("plugin", "1.0.0", required=False)
]
```

### 4. Monitor Status

Update component status based on health:
```python
try:
    # Component work
    registry.update_component_status("my-service", ComponentStatus.ACTIVE)
except Exception:
    registry.update_component_status("my-service", ComponentStatus.ERROR)
```

### 5. Include Context Tags

Add DLP context for audit trails:
```python
registry.register_component(..., context_tag=dlp_tag)
```

## Troubleshooting

### Component Not Found

```python
component = registry.get_component("my-service")
if component is None:
    # Not registered - register it
    registry.register_component(...)
```

### Circular Dependency Detected

```python
conflicts = registry.detect_conflicts()
for conflict in conflicts:
    if conflict["type"] == "circular_dependency":
        print(f"Circular dep: {conflict['component']}")
        # Redesign dependencies to break cycle
```

### Missing Dependencies

```python
conflicts = registry.detect_conflicts()
missing = [c for c in conflicts if c["type"] == "missing_dependency"]
for issue in missing:
    # Register missing dependency
    registry.register_component(
        name=issue["missing"],
        version="1.0.0",
        description="Missing dependency"
    )
```

## Roadmap

Future enhancements:

- [ ] Interactive dependency graph visualization (D3.js/Mermaid)
- [ ] Version conflict resolution suggestions
- [ ] Component health scoring
- [ ] Automated dependency updates
- [ ] Integration with package managers
- [ ] Real-time WebSocket updates
- [ ] Export to architectural diagram formats (PlantUML, etc.)
- [ ] Component marketplace/catalog

## Contributing

When adding components to the registry:

1. Use semantic versioning
2. Document all dependencies
3. Include API endpoints if applicable
4. Add DLP context tags
5. Update component status based on health
6. Test dependency graph integrity

## License

Part of Aurora CloudBank Symbolic project. See main project LICENSE.
