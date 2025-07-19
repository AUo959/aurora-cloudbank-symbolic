#!/usr/bin/env python3
"""
Opal2 Modular System - FastAPI Integration
Enhanced quantum visualization API with modular renderer support
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Using native Python math instead of numpy for better performance
import math
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ...symbolic.symbolic_core import SymbolicCore
from ..glyph_cache import GlyphCache
from ..glyph_core import GlyphCore
from ..plugin_system import PluginSystem
from ..quantum_renderer import QuantumRenderer

app = FastAPI(
    title="Opal2 Modular Visualization System",
    description="Quantum-enhanced modular visualization with real-time rendering",
    version="2.0.0",
)

# Initialize core components
glyph_core = GlyphCore()
glyph_cache = GlyphCache()
quantum_renderer = QuantumRenderer()
plugin_system = PluginSystem()
symbolic_core = SymbolicCore()

# Active WebSocket connections
active_connections: List[WebSocket] = []


class RenderRequest(BaseModel):
    """Request model for quantum rendering"""

    glyph_data: Dict[str, Any] = Field(..., description="Glyph configuration data")
    renderer_type: str = Field(
        default="webgl", description="Renderer type (webgl, canvas, svg)"
    )
    dimensions: Dict[str, int] = Field(
        default={"width": 800, "height": 600}, description="Render dimensions"
    )
    quantum_params: Optional[Dict[str, float]] = Field(
        default=None, description="Quantum enhancement parameters"
    )
    cache_key: Optional[str] = Field(
        default=None, description="Cache key for optimization"
    )


class GlyphGenerationRequest(BaseModel):
    """Request model for glyph generation"""

    symbolic_expression: str = Field(..., description="Symbolic expression to render")
    style_params: Dict[str, Any] = Field(default={}, description="Style parameters")
    quantum_enhancement: bool = Field(
        default=True, description="Enable quantum enhancement"
    )


class WebSocketMessage(BaseModel):
    """WebSocket message model"""

    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now)


@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "system": "Opal2 Modular Visualization System",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "glyph_core": "active",
            "quantum_renderer": "active",
            "plugin_system": "active",
            "cache_system": "active",
        },
    }


@app.get("/health")
async def health_check():
    """System health check endpoint"""
    try:
        # Test core components
        health_status = {
            "glyph_core": await test_glyph_core(),
            "quantum_renderer": await test_quantum_renderer(),
            "plugin_system": await test_plugin_system(),
            "cache_system": await test_cache_system(),
        }

        all_healthy = all(status["healthy"] for status in health_status.values())

        return {
            "healthy": all_healthy,
            "components": health_status,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        import logging

        logging.error("Health check failed: %s", str(e), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"healthy": False, "error": "An internal error has occurred."},
        )


@app.post("/render")
async def render_glyph(request: RenderRequest):
    """Render a glyph with specified parameters"""
    try:
        # Generate cache key if not provided
        if not request.cache_key:
            request.cache_key = f"render_{uuid.uuid4().hex[:8]}"

        # Check cache first
        cached_result = await glyph_cache.get_async(request.cache_key)
        if cached_result:
            return {
                "success": True,
                "cached": True,
                "result": cached_result,
                "cache_key": request.cache_key,
            }

        # Get renderer plugin
        renderer_plugin = plugin_system.get_plugin(f"{request.renderer_type}_renderer")
        if not renderer_plugin:
            raise HTTPException(
                status_code=400,
                detail=f"Renderer type '{request.renderer_type}' not available",
            )

        # Render the glyph
        render_result = await quantum_renderer.render_async(
            glyph_data=request.glyph_data,
            renderer=renderer_plugin,
            dimensions=request.dimensions,
            quantum_params=request.quantum_params or {},
        )

        # Cache the result
        await glyph_cache.set_async(request.cache_key, render_result)

        # Notify WebSocket clients
        await notify_clients(
            {
                "type": "render_complete",
                "data": {
                    "cache_key": request.cache_key,
                    "renderer_type": request.renderer_type,
                    "dimensions": request.dimensions,
                },
            }
        )

        return {
            "success": True,
            "cached": False,
            "result": render_result,
            "cache_key": request.cache_key,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def generate_glyph(request: GlyphGenerationRequest):
    """Generate a new glyph from symbolic expression"""
    try:
        # Parse symbolic expression
        parsed_expression = symbolic_core.parse_expression(request.symbolic_expression)

        # Generate glyph with quantum enhancement
        glyph_data = await glyph_core.generate_async(
            expression=parsed_expression,
            style_params=request.style_params,
            quantum_enhancement=request.quantum_enhancement,
        )

        # Generate cache key
        cache_key = f"glyph_{uuid.uuid4().hex[:8]}"

        # Cache the glyph
        await glyph_cache.set_async(cache_key, glyph_data)

        return {
            "success": True,
            "glyph_data": glyph_data,
            "cache_key": cache_key,
            "expression": request.symbolic_expression,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plugins")
async def list_plugins():
    """List available renderer plugins"""
    plugins = plugin_system.list_plugins()
    return {"plugins": plugins, "count": len(plugins)}


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    stats = await glyph_cache.get_stats()
    return stats


@app.delete("/cache/clear")
async def clear_cache():
    """Clear the glyph cache"""
    cleared_count = await glyph_cache.clear_async()
    return {"success": True, "cleared_items": cleared_count}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Listen for client messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(
                    json.dumps(
                        {"type": "pong", "timestamp": datetime.now().isoformat()}
                    )
                )
            elif message.get("type") == "subscribe":
                # Handle subscription logic
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscribed",
                            "channel": message.get("channel"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def notify_clients(message: Dict[str, Any]):
    """Notify all connected WebSocket clients"""
    if active_connections:
        message_str = json.dumps(message, default=str)
        for connection in active_connections.copy():
            try:
                await connection.send_text(message_str)
            except BaseException:
                active_connections.remove(connection)


# Component health test functions
async def test_glyph_core():
    """Test glyph core functionality"""
    try:
        # Simple test generation
        test_result = await glyph_core.test_generation()
        return {"healthy": True, "test_result": test_result}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def test_quantum_renderer():
    """Test quantum renderer functionality"""
    try:
        test_result = await quantum_renderer.test_render()
        return {"healthy": True, "test_result": test_result}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def test_plugin_system():
    """Test plugin system functionality"""
    try:
        plugin_count = len(plugin_system.list_plugins())
        return {"healthy": True, "plugin_count": plugin_count}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def test_cache_system():
    """Test cache system functionality"""
    try:
        stats = await glyph_cache.get_stats()
        return {"healthy": True, "stats": stats}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


# Mount static files for web interface
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/demo", response_class=HTMLResponse)
async def demo_interface():
    """Demo web interface for Opal2 system"""
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

                    // Generate glyph
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

                        // Render glyph
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
                            document.getElementById('render-area').innerHTML = renderResult.result;
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

    uvicorn.run(app, host="0.0.0.0", port=8000)
