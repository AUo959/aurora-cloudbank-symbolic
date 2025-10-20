"""Compatibility shim for legacy PluginSystem imports."""

from modules.opal2.plugin_system import (  # noqa: F401
    CanvasRendererPlugin,
    PluginInfo,
    PluginInterface,
    PluginStatus,
    PluginSystem,
    PluginType,
    QuantumFieldRendererPlugin,
    RendererPlugin,
    SVGRendererPlugin,
    WebGLRendererPlugin,
)

__all__ = [
    "CanvasRendererPlugin",
    "PluginInfo",
    "PluginInterface",
    "PluginStatus",
    "PluginSystem",
    "PluginType",
    "QuantumFieldRendererPlugin",
    "RendererPlugin",
    "SVGRendererPlugin",
    "WebGLRendererPlugin",
]
