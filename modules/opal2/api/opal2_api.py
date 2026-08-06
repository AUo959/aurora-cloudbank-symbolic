#!/usr/bin/env python3
"""Opal2 Modular System - FastAPI Integration.

This module is intentionally a standalone FastAPI application rather than a
sub-router mounted in api/aurora_api.py.  Reasons:
  - Opal2 owns a WebSocket endpoint (/ws) that benefits from an independent
    event-loop scope and server lifecycle.
  - Its render/generate/cache routes carry distinct auth patterns (CSRF on
    mutating ops, open health/stats) that would complicate the main router.
  - The standalone topology was the original design; mounting would require
    prefixing all paths and updating downstream clients.

To run Opal2 alongside the main Aurora API, start it as a separate process
(e.g. `uvicorn modules.opal2.api.opal2_api:app --port 8001`).
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from src.middleware.fastapi_security import verify_csrf_token

from modules.symbolic_core.symbolic_core import SymbolicCore

from modules.opal2.glyph_cache import GlyphCache
from modules.opal2.glyph_core import GlyphCore
from modules.opal2.plugin_system import PluginSystem
from modules.opal2.quantum_renderer import QuantumRenderer
from modules.opal2.tool_contract import (
    ToolExecutionContext,
    ToolInputError,
    ToolOutputError,
    json_ready,
)
from modules.opal2.tool_registry import ToolNotFoundError, ToolRegistry
from modules.opal2.tools import (
    GLYPH_RENDER_TOOL_ID,
    GlyphRenderTool,
    RegexWorkshopTool,
)

security = HTTPBearer()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OPAL2 Tool Foundry",
    description="Portable tool registry and runtime with regex and symbolic visualization reference tools",
    version="2.2.0",
)

glyph_core = GlyphCore()
glyph_cache = GlyphCache()
quantum_renderer = QuantumRenderer()
plugin_system = PluginSystem()
symbolic_core = SymbolicCore()
tool_registry = ToolRegistry((GlyphRenderTool(quantum_renderer), RegexWorkshopTool()))

active_connections: List[WebSocket] = []


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


class RenderRequest(BaseModel):
    """Request model for quantum rendering."""

    glyph_data: Dict[str, Any] = Field(..., description="Glyph configuration data")
    renderer_type: str = Field(
        default="webgl", description="Renderer type (webgl, canvas, svg)"
    )
    dimensions: Dict[str, int] = Field(
        default_factory=lambda: {"width": 800, "height": 600},
        description="Render dimensions",
    )
    quantum_params: Optional[Dict[str, float]] = Field(
        default=None, description="Quantum enhancement parameters"
    )
    cache_key: Optional[str] = Field(
        default=None, description="Cache key for optimization"
    )


class GlyphGenerationRequest(BaseModel):
    """Request model for glyph generation."""

    symbolic_expression: str = Field(..., description="Symbolic expression to render")
    style_params: Dict[str, Any] = Field(
        default_factory=dict, description="Style parameters"
    )
    quantum_enhancement: bool = Field(
        default=True, description="Enable quantum enhancement"
    )


class WebSocketMessage(BaseModel):
    """WebSocket message model."""

    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=_utc_now)


class ToolRunRequest(BaseModel):
    """Portable request envelope for a registered OPAL2 tool."""

    payload: Dict[str, Any] = Field(default_factory=dict)
    policy_profile: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@app.get("/")
async def root() -> Dict[str, Any]:
    """Return system status."""

    return {
        "system": "OPAL2 Tool Foundry",
        "version": "2.2.0",
        "status": "operational",
        "timestamp": _utc_now_iso(),
        "components": {
            "glyph_core": "active",
            "quantum_renderer": "active",
            "plugin_system": "active",
            "cache_system": "active",
            "tool_registry": "active",
        },
        "tools": [manifest["tool_id"] for manifest in tool_registry.list_manifests()],
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Return the health of core components."""

    try:
        health_status = {
            "glyph_core": await test_glyph_core(),
            "quantum_renderer": await test_quantum_renderer(),
            "plugin_system": await test_plugin_system(),
            "cache_system": await test_cache_system(),
            "tool_registry": test_tool_registry(),
        }
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.exception("Health check failed", exc_info=exc)
        return {
            "healthy": False,
            "components": {},
            "timestamp": _utc_now_iso(),
            "error": "internal error",
        }

    all_healthy = all(status["healthy"] for status in health_status.values())
    return {
        "healthy": all_healthy,
        "components": health_status,
        "timestamp": _utc_now_iso(),
    }


@app.post(
    "/render",
    responses={
        400: {"description": "Unsupported renderer or invalid render payload"},
        500: {"description": "Registered glyph-render tool failed"},
    },
)
async def render_glyph(
    request: RenderRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Render a glyph with CSRF validation."""
    verify_csrf_token(token)
    return await _render_glyph_impl(request)


@app.post("/generate")
async def generate_glyph(
    request: GlyphGenerationRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Generate a glyph with CSRF validation."""
    verify_csrf_token(token)
    return await _generate_glyph_impl(request)


@app.get("/plugins")
async def list_plugins() -> Dict[str, Any]:
    """List available renderer plugins."""

    plugins = plugin_system.list_plugins()
    return {"plugins": plugins, "count": len(plugins)}


@app.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """List trusted tools registered with the OPAL2 foundry."""

    tools = tool_registry.list_manifests()
    return {"tools": tools, "count": len(tools)}


@app.get("/tools/{tool_id}", responses={404: {"description": "Tool not found"}})
async def get_tool(tool_id: str) -> Dict[str, Any]:
    """Return the portable manifest for one registered tool."""

    try:
        return {"tool": tool_registry.get_manifest(tool_id).to_dict()}
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/tools/{tool_id}/run",
    responses={
        404: {"description": "Tool not found"},
        422: {"description": "Tool input contract violation"},
        500: {"description": "Tool output contract violation"},
    },
)
async def run_tool(
    tool_id: str,
    request: ToolRunRequest,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> Dict[str, Any]:
    """Execute one explicitly registered tool with CSRF validation."""

    verify_csrf_token(token)
    context = ToolExecutionContext(
        policy_profile=request.policy_profile, metadata=request.metadata
    )
    try:
        result = await tool_registry.run(tool_id, request.payload, context)
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ToolInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ToolOutputError as exc:
        logger.exception(
            "Registered OPAL2 tool violated its output contract", exc_info=exc
        )
        raise HTTPException(
            status_code=500, detail="tool output contract violation"
        ) from exc
    return result.to_dict()


@app.get("/cache/stats")
async def cache_stats() -> Dict[str, Any]:
    """Return cache statistics."""

    return await glyph_cache.get_stats()


@app.delete("/cache/clear")
async def clear_cache(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Clear the glyph cache with CSRF validation."""
    verify_csrf_token(token)
    cleared_count = await glyph_cache.clear_async()
    return {"success": True, "cleared_items": cleared_count}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time updates."""

    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            message = json.loads(await websocket.receive_text())
            if message.get("type") == "ping":
                await websocket.send_text(
                    json.dumps({"type": "pong", "timestamp": _utc_now_iso()})
                )
            elif message.get("type") == "subscribe":
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscribed",
                            "channel": message.get("channel"),
                            "timestamp": _utc_now_iso(),
                        }
                    )
                )
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def notify_clients(message: Dict[str, Any]) -> None:
    """Notify all connected WebSocket clients."""

    if not active_connections:
        return

    payload = json.dumps(message, default=str)
    for connection in active_connections.copy():
        try:
            await connection.send_text(payload)
        except Exception:  # pragma: no cover - best-effort cleanup
            logger.debug("Removing stale WebSocket connection", exc_info=True)
            active_connections.remove(connection)


async def _render_glyph_impl(request: RenderRequest) -> Dict[str, Any]:
    cache_key = request.cache_key or f"render_{uuid.uuid4().hex[:8]}"

    cached_result = await glyph_cache.get_async(cache_key)
    if cached_result:
        return {
            "success": True,
            "cached": True,
            "result": cached_result,
            "cache_key": cache_key,
        }

    try:
        tool_result = await tool_registry.run(
            GLYPH_RENDER_TOOL_ID,
            {
                "glyph_data": request.glyph_data,
                "renderer": request.renderer_type,
                "dimensions": request.dimensions,
                "quantum_params": request.quantum_params or {},
            },
            ToolExecutionContext(metadata={"compatibility_route": "/render"}),
        )
    except ToolInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (ToolNotFoundError, ToolOutputError) as exc:
        logger.exception("Registered OPAL2 glyph tool failed", exc_info=exc)
        raise HTTPException(
            status_code=500, detail="glyph render tool execution failed"
        ) from exc

    await glyph_cache.set_async(cache_key, tool_result.output)
    await notify_clients(
        {
            "type": "render_complete",
            "data": {
                "cache_key": cache_key,
                "renderer_type": request.renderer_type,
                "dimensions": request.dimensions,
            },
        }
    )

    return {
        "success": True,
        "cached": False,
        "result": tool_result.output,
        "cache_key": cache_key,
        "tool_run": {
            "run_id": tool_result.run_id,
            "tool_id": tool_result.tool_id,
            "tool_version": tool_result.tool_version,
            "duration_ms": tool_result.duration_ms,
            "provenance": dict(tool_result.provenance),
        },
    }


async def _generate_glyph_impl(request: GlyphGenerationRequest) -> Dict[str, Any]:
    parsed_expression = symbolic_core.parse_expression(request.symbolic_expression)
    glyph_data = await glyph_core.generate_async(
        expression={
            "symbol": request.symbolic_expression,
            "analysis": parsed_expression,
        },
        style_params=request.style_params,
        quantum_enhancement=request.quantum_enhancement,
    )
    glyph_data = json_ready(glyph_data)

    cache_key = f"glyph_{uuid.uuid4().hex[:8]}"
    await glyph_cache.set_async(cache_key, glyph_data)

    return {
        "success": True,
        "glyph_data": glyph_data,
        "cache_key": cache_key,
        "expression": request.symbolic_expression,
    }


async def test_glyph_core() -> Dict[str, Any]:
    try:
        result = await glyph_core.test_generation()
        return {"healthy": bool(result.get("success")), "test_result": result}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Glyph core health probe failed (%s)", type(exc).__name__)
        return {"healthy": False, "error": "internal error"}


async def test_quantum_renderer() -> Dict[str, Any]:
    try:
        result = await quantum_renderer.test_render()
        return {"healthy": bool(result.get("success")), "test_result": result}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Quantum renderer health probe failed (%s)", type(exc).__name__)
        return {"healthy": False, "error": "internal error"}


async def test_plugin_system() -> Dict[str, Any]:
    try:
        plugin_count = len(plugin_system.list_plugins())
        return {"healthy": True, "plugin_count": plugin_count}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Plugin system health probe failed (%s)", type(exc).__name__)
        return {"healthy": False, "error": "internal error"}


async def test_cache_system() -> Dict[str, Any]:
    try:
        stats = await glyph_cache.get_stats()
        return {"healthy": True, "stats": stats}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Cache system health probe failed (%s)", type(exc).__name__)
        return {"healthy": False, "error": "internal error"}


def test_tool_registry() -> Dict[str, Any]:
    try:
        tools = tool_registry.list_manifests()
        return {"healthy": bool(tools), "tool_count": len(tools)}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Tool registry health probe failed (%s)", type(exc).__name__)
        return {"healthy": False, "error": "internal error"}


def _verify_token(token: HTTPAuthorizationCredentials | None) -> None:
    verify_csrf_token(token)


_REPO_ROOT = Path(__file__).resolve().parents[3]
app.mount("/static", StaticFiles(directory=str(_REPO_ROOT / "static")), name="static")


@app.get("/demo", response_class=HTMLResponse)
async def demo_interface() -> str:
    """Demo web interface for Opal2 system."""

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Opal2 Modular Visualization Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .controls { margin-bottom: 20px; }
            .render-area { border: 1px solid #ccc; min-height: 400px; }
            input, select, button { margin: 5px; padding: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔮 Opal2 Modular Visualization System</h1>
            <div class="controls">
                <input type="text" id="expression" placeholder="Enter symbolic expression" />
                <select id="renderer">
                    <option value="webgl">WebGL</option>
                    <option value="canvas">Canvas</option>
                    <option value="svg">SVG</option>
                </select>
                <button onclick="generateAndRender()">Generate & Render</button>
            </div>
            <div id="render-area" class="render-area"></div>
            <div id="status"></div>
        </div>

        <script>
            async function generateAndRender() {
                const expression = document.getElementById('expression').value;
                const renderer = document.getElementById('renderer').value;
                const status = document.getElementById('status');

                try {
                    status.textContent = 'Generating glyph...';

                    const generateResponse = await fetch('/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            symbolic_expression: expression,
                            quantum_enhancement: true
                        })
                    });

                    const generateResult = await generateResponse.json();

                    if (generateResult.success) {
                        status.textContent = 'Rendering...';

                        const renderResponse = await fetch('/render', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                glyph_data: generateResult.glyph_data,
                                renderer_type: renderer,
                                dimensions: { width: 800, height: 600 }
                            })
                        });

                        const renderResult = await renderResponse.json();

                        if (renderResult.success) {
                            status.textContent = 'Render complete!';
                            // SECURITY: Avoid innerHTML injection, assign as textContent
                            const renderArea = document.getElementById('render-area');
                            if (typeof renderResult.result === 'string') {
                                renderArea.textContent = renderResult.result;
                            } else {
                                renderArea.textContent = JSON.stringify(renderResult.result);
                            }
                        } else {
                            status.textContent = 'Render failed: ' + renderResult.error;
                        }
                    } else {
                        status.textContent = 'Generation failed: ' + generateResult.error;
                    }
                } catch (error) {
                    status.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
