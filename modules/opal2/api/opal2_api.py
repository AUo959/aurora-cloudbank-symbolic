#!/usr/bin/env python3
"""
Opal2 Modular System - FastAPI Integration
Enhanced quantum visualization API with modular renderer support
"""
import logging
import uvicorn
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from modules.opal2.glyph_core import GlyphCore
from modules.opal2.glyph_cache import GlyphCache
from modules.opal2.engines.quantum_renderer import QuantumRenderer
from modules.opal2.plugin_system import PluginSystem
from modules.opal2.symbolic_core import SymbolicCore

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
    style_params: Dict[str, Any] = Field(
        default={}, description="Style parameters"
    )
    quantum_enhancement: bool = Field(
        default=True, description="Enable quantum enhancement"
    )

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    action: str = Field(..., description="Message action type")
    data: Dict[str, Any] = Field(default={}, description="Message payload")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return JSONResponse(
            content={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "glyph_core": "operational",
                    "quantum_renderer": "operational",
                    "plugin_system": "operational",
                },
            }
        )
    except Exception as e:
        logging.error("Health check failed: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
