"""Opal2 Plugin System - Base Plugin Interface (clean minimal version)

Provides the foundation for the Opal2 modular plugin architecture.
Supports hot-swappable rendering plugins with validation and security.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PluginType(Enum):
    """Types of plugins supported by the Opal2 system."""

    RENDERER = "renderer"
    EXPORTER = "exporter"
    FILTER = "filter"
    INPUT_PROCESSOR = "input_processor"


class PluginStatus(Enum):
    """Plugin operational status."""

    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """Metadata for plugin description and validation."""

    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=list)
    api_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "plugin_type": self.plugin_type.value,
            "dependencies": self.dependencies,
            "supported_formats": self.supported_formats,
            "api_version": self.api_version,
        }


class BasePlugin(ABC):
    """Abstract base class for all Opal2 plugins."""

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.status = PluginStatus.INACTIVE
        self.config: Dict[str, Any] = {}
        self._initialization_time = time.time()
        self._metrics = {
            "operations_count": 0,
            "total_execution_time": 0.0,
            "error_count": 0,
            "last_execution_time": 0.0,
        }

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        ...

    @abstractmethod
    def process(self, input_data: Any, options: Dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def cleanup(self) -> bool:
        ...

    def get_supported_formats(self) -> List[str]:
        return self.metadata.supported_formats

    def get_performance_metrics(self) -> Dict[str, Any]:
        ops = max(1, self._metrics["operations_count"])
        avg = self._metrics["total_execution_time"] / ops
        return {
            **self._metrics,
            "avg_execution_time": avg,
            "uptime": time.time() - self._initialization_time,
        }

    def _update_metrics(self, execution_time: float, success: bool = True) -> None:
        self._metrics["operations_count"] += 1
        self._metrics["total_execution_time"] += execution_time
        self._metrics["last_execution_time"] = execution_time
        if not success:
            self._metrics["error_count"] += 1


class RendererPlugin(BasePlugin):
    """Base class for rendering plugins."""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.render_cache: Dict[str, Any] = {}

    @abstractmethod
    def render(self, render_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def process(self, input_data: Any, options: Dict[str, Any]) -> Any:
        start = time.time()
        try:
            result = self.render(input_data, options)
            self._update_metrics(time.time() - start, True)
            return result
        except Exception:
            self._update_metrics(time.time() - start, False)
            raise

    def clear_cache(self) -> None:
        self.render_cache.clear()


class ExporterPlugin(BasePlugin):
    """Base class for export plugins."""

    @abstractmethod
    def export(self, data: Dict[str, Any], output_format: str, options: Dict[str, Any]) -> bytes:
        ...

    def process(self, input_data: Any, options: Dict[str, Any]) -> Any:
        start = time.time()
        try:
            fmt = options.get("format", "default")
            return self.export(input_data, fmt, options)
        finally:
            self._update_metrics(time.time() - start, True)


class FilterPlugin(BasePlugin):
    """Base class for filter/effect plugins."""

    @abstractmethod
    def apply_filter(self, data: Dict[str, Any], filter_params: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def process(self, input_data: Any, options: Dict[str, Any]) -> Any:
        start = time.time()
        try:
            result = self.apply_filter(input_data, options)
            self._update_metrics(time.time() - start, True)
            return result
        except Exception:
            self._update_metrics(time.time() - start, False)
            raise


class PluginRegistry:
    """Registry for managing Opal2 plugins."""

    def __init__(self) -> None:
        self.plugins: Dict[str, BasePlugin] = {}
        self.by_type: Dict[PluginType, List[str]] = {t: [] for t in PluginType}

    def register_plugin(self, plugin: BasePlugin) -> bool:
        name = plugin.metadata.name
        if name in self.plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        self.plugins[name] = plugin
        self.by_type[plugin.metadata.plugin_type].append(name)
        plugin.status = PluginStatus.ACTIVE
        return True

    def unregister_plugin(self, plugin_name: str) -> bool:
        if plugin_name not in self.plugins:
            return False
        plugin = self.plugins.pop(plugin_name)
        self.by_type[plugin.metadata.plugin_type].remove(plugin_name)
        plugin.status = PluginStatus.INACTIVE
        try:
            plugin.cleanup()
        except Exception:
            pass
        return True

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": n,
                "type": p.metadata.plugin_type.value,
                "status": p.status.value,
                "version": p.metadata.version,
            }
            for n, p in self.plugins.items()
        ]

# EOF - end of file
