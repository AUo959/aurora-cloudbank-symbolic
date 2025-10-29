"""
src/integrations/base_agent_integration.py

Defines the base class for all AI agent integrations (e.g., ChatGPT, Gemini, Claude).
This promotes a unified, interoperable architecture for exposing system tools to different AI models.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Awaitable, Optional

class BaseAgentIntegration(ABC):
    """
    An abstract base class for AI agent integrations.
    
    It provides a standardized way to register, manage, and expose tools
    to different large language models.
    """
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    def _register_default_tools(self):
        """
        Abstract method to be implemented by subclasses.
        This method should register the specific tools available for that agent.
        """
        pass

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Awaitable[Dict]],
        description: str,
        parameters: Dict[str, Any]
    ):
        """
        Registers a tool for the agent.
        
        Args:
            name: The name of the tool.
            handler: The async function that handles the tool's execution.
            description: A description of what the tool does.
            parameters: A JSON schema describing the tool's parameters.
        """
        self._tools[name] = {
            "name": name,
            "handler": handler,
            "description": description,
            "parameters": parameters,
        }

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Lists all registered tools, with handler details sanitized."""
        return [self._sanitize_tool_info(tool) for tool in self._tools.values()]

    def _sanitize_tool_info(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Removes the handler function from the tool info to avoid exposing
        internal implementation details in API responses.
        """
        sanitized_info = tool_info.copy()
        sanitized_info.pop("handler", None)
        return sanitized_info
