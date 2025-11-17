"""
Example: Integrating Connector Framework with ChatGPT Agent Mode

This example demonstrates how to expose external tool connectors
to ChatGPT agents through Aurora's agent mode integration.
"""

import logging

logger = logging.getLogger(__name__)

import asyncio
from typing import Any, Dict

from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration
from src.integrations.connectors import (
    ConnectorConfig,
    connector_registry,
)
from src.integrations.connectors.builtin import GitHubConnector


async def register_connector_tools(agent_integration: ChatGPTAgentModeIntegration):
    """
    Register connector operations as ChatGPT agent tools.

    This allows agents to discover and use external tool connectors
    through the standardized tool interface.
    """

    # Register GitHub connector type
    connector_registry.register_connector_type("github", GitHubConnector)

    # Create GitHub connector configuration
    github_config = ConnectorConfig(
        name="github_agent",
        version="1.0.0",
        connector_type="github",
        auth_config={"token": "your_github_token_here"},  # In production: use env vars
        rate_limit_rpm=5000,
        metadata={
            "auth_type": "bearer_token",
            "base_url": "https://api.github.com"
        }
    )

    # Create connector instance
    github_connector = await connector_registry.create_connector("github", github_config)

    # Connect to GitHub
    await github_connector.connect()

    # Define tool handlers that wrap connector operations
    async def github_get_repository(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get GitHub repository information"""
        result = await github_connector.execute("get_repository", parameters)
        return result

    async def github_list_issues(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List GitHub repository issues"""
        result = await github_connector.execute("list_issues", parameters)
        return result

    async def github_create_issue(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new GitHub issue"""
        result = await github_connector.execute("create_issue", parameters)
        return result

    async def github_list_pull_requests(parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List GitHub pull requests"""
        result = await github_connector.execute("list_pull_requests", parameters)
        return result

    # Register tools with agent integration
    agent_integration.tools_registry["github_get_repository"] = {
        "name": "github_get_repository",
        "description": "Get information about a GitHub repository",
        "parameters": {
            "owner": {"type": "string", "required": True, "description": "Repository owner"},
            "repo": {"type": "string", "required": True, "description": "Repository name"}
        },
        "handler": github_get_repository
    }

    agent_integration.tools_registry["github_list_issues"] = {
        "name": "github_list_issues",
        "description": "List issues in a GitHub repository",
        "parameters": {
            "owner": {"type": "string", "required": True, "description": "Repository owner"},
            "repo": {"type": "string", "required": True, "description": "Repository name"},
            "state": {"type": "string", "required": False, "description": "Issue state (open/closed)"}
        },
        "handler": github_list_issues
    }

    agent_integration.tools_registry["github_create_issue"] = {
        "name": "github_create_issue",
        "description": "Create a new issue in a GitHub repository",
        "parameters": {
            "owner": {"type": "string", "required": True, "description": "Repository owner"},
            "repo": {"type": "string", "required": True, "description": "Repository name"},
            "title": {"type": "string", "required": True, "description": "Issue title"},
            "body": {"type": "string", "required": False, "description": "Issue body"}
        },
        "handler": github_create_issue
    }

    agent_integration.tools_registry["github_list_pull_requests"] = {
        "name": "github_list_pull_requests",
        "description": "List pull requests in a GitHub repository",
        "parameters": {
            "owner": {"type": "string", "required": True, "description": "Repository owner"},
            "repo": {"type": "string", "required": True, "description": "Repository name"},
            "state": {"type": "string", "required": False, "description": "PR state (open/closed)"}
        },
        "handler": github_list_pull_requests
    }

    logger.info("GitHub connector tools registered with ChatGPT Agent Mode")
    return github_connector


async def example_usage():
    """
    Example of how agents can discover and use connector tools.
    """

    # Initialize agent integration
    agent = ChatGPTAgentModeIntegration()

    # Register connector tools
    github_connector = await register_connector_tools(agent)

    # Discover available tools (what agents see)
    tools_info = await agent.discover_tools()
    print(f"\n📋 Available tools: {len(tools_info['tools'])} total")

    # Check if GitHub tools are available
    github_tools = [
        tool for tool in tools_info['tools']
        if tool.startswith('github_')
    ]
    print(f"🔧 GitHub tools: {', '.join(github_tools)}")

    # Example: Agent executes a GitHub operation
    print("\n🤖 Agent executing: github_get_repository")
    result = await agent.execute_tool("github_get_repository", {
        "owner": "octocat",
        "repo": "Hello-World"
    })

    if result["success"]:
        logger.info(f"Repository retrieved: {result['result'].get('full_name', 'N/A')}")
        print(f"📊 DLP tracking: {result['context_tag']}")
    else:
        logger.error(f"Error: {result.get('error')}")

    # Example: List issues
    print("\n🤖 Agent executing: github_list_issues")
    issues_result = await agent.execute_tool("github_list_issues", {
        "owner": "octocat",
        "repo": "Hello-World",
        "state": "open"
    })

    if issues_result["success"]:
        issues = issues_result["result"]
        logger.info(f"Found {len(issues)} open issues")
    else:
        logger.error(f"Error: {issues_result.get('error')}")

    # Cleanup
    await github_connector.disconnect()
    print("\n🔌 Disconnected from GitHub")


async def example_multi_connector():
    """
    Example of registering multiple connectors for different services.

    This demonstrates how agents can work with multiple external tools
    simultaneously through the connector framework.
    """

    agent = ChatGPTAgentModeIntegration()

    # Register multiple connectors
    connectors = []

    # GitHub connector
    github_config = ConnectorConfig(
        name="github",
        version="1.0.0",
        connector_type="github",
        auth_config={"token": "github_token"}
    )
    connector_registry.register_connector_type("github", GitHubConnector)
    github = await connector_registry.create_connector("github", github_config)
    await github.connect()
    connectors.append(("GitHub", github))

    # You could add more connectors here:
    # - Slack connector for messaging
    # - Jira connector for project management
    # - AWS connector for cloud resources
    # - etc.

    logger.info("Registered {len(connectors)} connectors")

    # Check overall health
    from src.integrations.connectors.health import HealthMonitor

    health_monitor = HealthMonitor()

    for name, connector in connectors:
        health = await health_monitor.check_connector_health(connector)
        print(f"💚 {name}: {health['health_status']}")

    # Cleanup
    for name, connector in connectors:
        await connector.disconnect()


async def example_connector_discovery():
    """
    Example of dynamic connector discovery.

    Shows how agents can discover available connectors and their capabilities.
    """

    # Discover all registered connectors
    all_connectors = connector_registry.discover_connectors()

    print(f"\n🔍 Discovered {len(all_connectors)} connectors:")
    for conn_info in all_connectors:
        print(f"  - {conn_info['name']} ({conn_info['type']}) - {conn_info['status']}")

    # Filter by type
    github_connectors = connector_registry.discover_connectors(
        filters={"type": "github"}
    )

    print(f"\n🐙 GitHub connectors: {len(github_connectors)}")

    # Filter by status
    active_connectors = connector_registry.discover_connectors(
        filters={"status": "connected"}
    )

    print(f"\n✅ Active connectors: {len(active_connectors)}")

    # Get registry status
    registry_status = connector_registry.get_registry_status()
    print(f"\n📊 Registry Status:")
    print(f"  Total connectors: {registry_status['total_connectors']}")
    print(f"  Total types: {registry_status['total_connector_types']}")
    print(f"  Types: {', '.join(registry_status['registered_types'])}")


if __name__ == "__main__":
    print("=" * 60)
    print("🌌 Aurora CloudBank - Connector Framework Integration Example")
    print("=" * 60)

    # Run basic example
    print("\n📝 Example 1: Basic GitHub Connector Integration")
    asyncio.run(example_usage())

    # Run multi-connector example
    print("\n" + "=" * 60)
    print("📝 Example 2: Multi-Connector Setup")
    print("=" * 60)
    asyncio.run(example_multi_connector())

    # Run discovery example
    print("\n" + "=" * 60)
    print("📝 Example 3: Connector Discovery")
    print("=" * 60)
    asyncio.run(example_connector_discovery())

    print("\n" + "=" * 60)
    logger.info("Examples completed successfully")
    print("=" * 60)
