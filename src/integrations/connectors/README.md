# External Tool Connector Framework

> A flexible, Aurora-compatible architecture for R-2 agents to integrate with external tools, APIs, and services.

## 🎯 Overview

The External Tool Connector Framework provides a standardized way for Aurora CloudBank agents to interact with external services while maintaining symbolic governance, DLP tracking, and ethical compliance. The framework includes:

- **Plugin Architecture**: Extensible connector system with base interfaces
- **Built-in Resilience**: Circuit breakers, rate limiting, retry logic, connection pooling
- **Authentication Support**: OAuth, API keys, bearer tokens, basic auth
- **Health Monitoring**: Comprehensive status tracking and metrics
- **Aurora Integration**: Full DLP tracking and symbolic anchor support
- **Built-in Connectors**: GitHub, with templates for Slack, Jira, AWS, and more

## 🚀 Quick Start

### Installation

The framework is part of the Aurora CloudBank repository. No additional installation needed.

### Basic Usage

```python
from src.integrations.connectors import ConnectorConfig
from src.integrations.connectors.builtin import GitHubConnector

# Configure connector
config = ConnectorConfig(
    name="github_prod",
    version="1.0.0",
    connector_type="github",
    auth_config={"token": "your_github_token"},
    rate_limit_rpm=5000
)

# Create and use connector
github = GitHubConnector(config)
await github.connect()

# Get repository info
result = await github.execute("get_repository", {
    "owner": "AUo959",
    "repo": "aurora-cloudbank-symbolic"
})

# List issues
issues = await github.execute("list_issues", {
    "owner": "AUo959",
    "repo": "aurora-cloudbank-symbolic",
    "state": "open"
})

await github.disconnect()
```

## 📋 Features

### Core Components

#### BaseConnector
Abstract base class with Aurora integration:
- ✅ DLP tracking with context tags
- ✅ T1/SRB anchor protocols
- ✅ Symbolic hash validation
- ✅ Async-first design
- ✅ Ethics validation

#### ConnectorRegistry
Centralized discovery and management:
- ✅ Type registration and instantiation
- ✅ Connector discovery with filtering
- ✅ Lifecycle management
- ✅ Statistics and monitoring

#### Authentication Framework
Multiple auth patterns:
- ✅ API Key authentication
- ✅ OAuth 2.0 flow
- ✅ Bearer token
- ✅ Basic HTTP auth
- ✅ Custom authentication

#### Resilience Components
Production-ready fault tolerance:
- ✅ **CircuitBreaker**: Prevent cascading failures
- ✅ **RateLimiter**: Token bucket rate limiting
- ✅ **RetryPolicy**: Exponential backoff with jitter
- ✅ **ConnectionPool**: Connection pooling and reuse

#### Health Monitoring
Comprehensive observability:
- ✅ Connector status tracking
- ✅ Performance metrics
- ✅ Health history
- ✅ System-wide health overview

## 📚 Documentation

- **[Developer Guide](./CONNECTOR_FRAMEWORK_GUIDE.md)** - Complete development guide with examples
- **[SDK/Toolkit](./CONNECTOR_SDK.md)** - Templates and utilities for custom connectors
- **[Quick Reference](./CONNECTOR_QUICK_REFERENCE.md)** - API reference and common patterns
- **[Examples](../examples/connector_integration_example.py)** - Working integration examples

## 🔧 Architecture

```
src/integrations/connectors/
├── __init__.py                 # Public API exports
├── base.py                     # BaseConnector interface
├── registry.py                 # ConnectorRegistry
├── auth.py                     # Authentication framework
├── circuit_breaker.py          # Circuit breaker pattern
├── health.py                   # Health monitoring
├── pooling.py                  # Rate limiting & connection pooling
├── retry.py                    # Retry logic with backoff
└── builtin/                    # Built-in connectors
    ├── __init__.py
    └── github_connector.py     # GitHub API integration
```

## 🎨 Design Principles

1. **Aurora-Native**: Full DLP tracking and symbolic governance
2. **Graceful Degradation**: Works without optional dependencies
3. **Async-First**: Built on Python's asyncio
4. **Fault-Tolerant**: Circuit breakers, retries, rate limiting
5. **Observable**: Comprehensive health monitoring and metrics
6. **Extensible**: Plugin architecture for custom connectors
7. **Secure**: Multiple authentication patterns, vault integration
8. **Testable**: 100% test coverage with unit and integration tests

## 🧪 Testing

Run the test suite:

```bash
# All connector tests
pytest tests/test_connector_framework.py -v

# Specific test class
pytest tests/test_connector_framework.py::TestConnectorFramework -v

# With markers
pytest -m unit tests/test_connector_framework.py
pytest -m integration tests/test_connector_framework.py
```

Test coverage includes:
- ✅ 20+ test cases
- ✅ Unit tests for all components
- ✅ Integration tests
- ✅ Aurora DLP validation
- ✅ Resilience pattern testing

## 📊 Built-in Connectors

### GitHub Connector
Full GitHub API integration:
- Get repository information
- List/create issues
- List/get pull requests
- Rate limiting (5000 req/min)
- Circuit breaker protection
- Mock mode for testing

### Coming Soon
- **Slack**: Messaging and notifications
- **Jira**: Project management
- **AWS**: Cloud resource management
- **More**: See [SDK Guide](./CONNECTOR_SDK.md) for custom connectors

## 🔐 Security

### Best Practices
- ✅ Never hardcode credentials
- ✅ Use environment variables
- ✅ Enable vault integration
- ✅ Validate all operations
- ✅ Monitor and audit access
- ✅ Follow least privilege principle

### Ethics Validation
```python
async def validate_operation(self, operation: str, parameters: Dict) -> bool:
    # Custom validation logic
    if operation == "delete_all_data":
        return False  # Ethical violation
    return await super().validate_operation(operation, parameters)
```

## 🤝 Integration with ChatGPT Agent Mode

The connector framework integrates seamlessly with Aurora's ChatGPT Agent Mode:

```python
from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration
from src.integrations.connectors.builtin import GitHubConnector

# Initialize agent
agent = ChatGPTAgentModeIntegration()

# Create connector
github = GitHubConnector(config)
await github.connect()

# Register connector operations as agent tools
agent.tools_registry["github_get_repo"] = {
    "name": "github_get_repo",
    "description": "Get GitHub repository info",
    "handler": lambda p: github.execute("get_repository", p)
}

# Agents can now discover and use GitHub operations
tools = await agent.discover_tools()
result = await agent.execute_tool("github_get_repo", params)
```

See [integration example](../examples/connector_integration_example.py) for complete code.

## 📈 Performance

### Optimizations
- Async/await for non-blocking I/O
- Connection pooling for resource efficiency
- Rate limiting to respect service limits
- Circuit breakers to fail fast
- Retry logic for transient failures
- Batch operations support

### Metrics
All components provide status and metrics:
```python
# Rate limiter
status = limiter.get_status()
# Returns: available_tokens, total_requests, throttled_requests, etc.

# Circuit breaker
status = circuit_breaker.get_status()
# Returns: state, failure_count, success_count, etc.

# Health monitor
health = monitor.get_all_health_status()
# Returns: overall_health, status_distribution, etc.
```

## 🛠️ Development

### Creating Custom Connectors

1. **Use the template** from [SDK Guide](./CONNECTOR_SDK.md)
2. **Implement required methods**: connect, disconnect, execute, health_check
3. **Add authentication**: Choose auth pattern
4. **Include resilience**: Rate limiting, retries, circuit breakers
5. **Test thoroughly**: Unit and integration tests
6. **Document**: Usage, config, operations
7. **Register**: Add to registry

See [SDK Guide](./CONNECTOR_SDK.md) for complete template and checklist.

### Contributing

To contribute a new connector:

1. Fork the repository
2. Create a feature branch
3. Implement connector following SDK guide
4. Add comprehensive tests
5. Update documentation
6. Submit pull request

## 📝 Examples

### Example 1: Basic Usage
```python
config = ConnectorConfig(name="github", version="1.0.0", connector_type="github")
connector = GitHubConnector(config)
await connector.connect()
result = await connector.execute("get_repository", {"owner": "user", "repo": "repo"})
await connector.disconnect()
```

### Example 2: With Health Monitoring
```python
monitor = HealthMonitor()
health = await monitor.check_connector_health(connector)
if health["health_status"] == "healthy":
    result = await connector.execute("operation", params)
```

### Example 3: Registry-Based
```python
connector_registry.register_connector_type("github", GitHubConnector)
connector = await connector_registry.create_connector("github", config)
```

See [examples directory](../examples/) for more.

## 📖 API Reference

### BaseConnector Methods
- `async connect() -> bool` - Establish connection
- `async disconnect() -> bool` - Graceful disconnect
- `async execute(operation, parameters) -> Dict` - Execute operation
- `async health_check() -> Dict` - Health status
- `get_dlp_metadata() -> Dict` - DLP tracking info
- `get_capabilities() -> Dict` - Connector capabilities

### ConnectorRegistry Methods
- `register_connector_type(type, class)` - Register type
- `create_connector(type, config)` - Create instance
- `discover_connectors(filters)` - Find connectors
- `get_registry_status()` - Registry stats

See [Quick Reference](./CONNECTOR_QUICK_REFERENCE.md) for complete API.

## 🐛 Troubleshooting

### Common Issues

**Connection fails:**
```python
# Check status and health
print(connector.status)
health = await connector.health_check()
```

**Rate limited:**
```python
# Check and adjust rate limiter
status = connector._rate_limiter.get_status()
config.rate_limit_rpm = 120  # Increase limit
```

**Circuit breaker open:**
```python
# Check state and reset
status = connector._circuit_breaker.get_status()
connector._circuit_breaker.reset()
```

See [Quick Reference](./CONNECTOR_QUICK_REFERENCE.md) for more troubleshooting.

## 📜 License

Part of Aurora CloudBank Symbolic project. See repository LICENSE file.

## 🌟 Acknowledgments

Built with Aurora's canonical patterns:
- DLP tracking and symbolic anchors
- Picard_Delta_3 ethics protocol
- EOS_SEED_ORION continuity standard
- Graceful degradation patterns
- 120-char line limit compliance

## 📞 Support

- **Documentation**: See [docs/](./CONNECTOR_FRAMEWORK_GUIDE.md)
- **Examples**: See [examples/](../examples/)
- **Issues**: Create GitHub issue
- **Contributing**: See CONTRIBUTING.md

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Maintainer**: Aurora CloudBank Team
