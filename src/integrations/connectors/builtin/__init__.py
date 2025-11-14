"""
Built-in Connectors for Common External Tools

Provides ready-to-use connectors for popular services:
- GitHub API
- Slack API
- Jira API
- AWS Services
"""

from .github_connector import GitHubConnector

__all__ = ["GitHubConnector"]
