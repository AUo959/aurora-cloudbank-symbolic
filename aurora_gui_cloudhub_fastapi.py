from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
from typing import List
import uvicorn
import logging
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.quantum_vsa import quantum_symbolic_vector
from modules.symbolic_core.vsa import SymbolicVector
from pydantic import BaseModel
from typing import Optional
import json
from modules.symbolic_core import get_mcp_bridge_core
from modules.symbolic_core.mcp_command_router import MCPCommandRouter
from modules.symbolic_core.mcp_security import mcp_security_dependency, mcp_security
from fastapi import Depends

app = FastAPI(title="Aurora Cloud GUI – ZIP Wizard Dashboard")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aurora_gui_cloudhub")

# Active WebSocket connections for basic broadcast
connections: List[WebSocket] = []

# Serve static files if needed in the future
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aurora ZIP Wizard GUI (Cloud)</title>
        <style>
            body { font-family: sans-serif; background: #0f0f1a; color: #ffffff; padding: 30px; }
            input, button { font-size: 1rem; padding: 0.5em; margin: 0.5em 0; }
            .frame { background: #1a1a2a; padding: 20px; border-radius: 8px; max-width: 600px; }
        </style>
    </head>
    <body>
        <div class="frame">
            <h1>🧬 Aurora ZIP Wizard (Cloud GUI)</h1>
            <p>This is the symbolic continuity dashboard. Upload a ZIP Wizard bundle to inspect or relay.</p>
            <form action='/upload/' enctype='multipart/form-data' method='post'>
                <input name='file' type='file' accept='.zip' />
                <button type='submit'>Upload Bundle</button>
            </form>
        </div>
    </body>
    </html>
    """


MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MiB


@app.post("/upload/")
async def upload_bundle(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    upload_dir = Path("./uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.zip"
    upload_path = upload_dir / filename
    with open(upload_path, "wb") as buffer:
        buffer.write(data)
    return {"message": "Bundle received", "filename": filename}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for conn in list(connections):
                if conn is websocket:
                    continue
                try:
                    await conn.send_text(data)
                except WebSocketDisconnect:
                    connections.remove(conn)
    except WebSocketDisconnect:
        connections.remove(websocket)


@app.on_event("startup")
async def startup_event():
    logger.info("Aurora Cloud GUI FastAPI service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Aurora Cloud GUI FastAPI service shutting down...")


class GeometricProductRequest(BaseModel):
    a: float
    b: float


class QuantumSymbolicVectorRequest(BaseModel):
    symbol: str
    dim: Optional[int] = 8


@app.post("/geometric/product", summary="Geometric Product", response_description="Result of geometric product")
def geometric_product(req: GeometricProductRequest):
    """
    Compute the geometric product of two 3D vectors (a*e1, b*e2) using Clifford algebra.
    Request body: {"a": float, "b": float}
    Response: {"result": str}
    """
    ga = GeometricAlgebra()
    a_mv = req.a * ga.blades['e1']
    b_mv = req.b * ga.blades['e2']
    result = ga.mult(a_mv, b_mv)
    return {"result": ga.pretty(result)}


@app.post("/quantum/symbolic_vector", summary="Quantum Symbolic Vector", response_description="Quantum-generated symbolic vector")
def quantum_symbolic_vector_endpoint(req: QuantumSymbolicVectorRequest):
    """
    Generate a symbolic vector using a quantum circuit seeded by the symbol hash.
    Request body: {"symbol": str, "dim": int}
    Response: {"symbol": str, "dim": int, "vector": list}
    """
    vec = quantum_symbolic_vector(req.symbol, req.dim)
    return {"symbol": req.symbol, "dim": req.dim, "vector": vec.tolist()}


@app.get("/mcp_bridge", summary="MCP Bridge Core JSON", response_description="MCP Bridge configuration JSON")
def get_mcp_bridge():
    """
    Returns the MCP Bridge Core configuration as JSON.
    """
    data = get_mcp_bridge_core()
    return JSONResponse(content=data)


@app.post("/mcp_bridge/route_command", summary="Symbolic Command Routing via MCP Bridge", response_description="Routed command result")
def mcp_route_command(command: str, anchor: str = "EOS_SEED_ORION", security: None = Depends(mcp_security_dependency)):
    """
    Symbolic command routing using MCP Bridge Core config and MCPCommandRouter.
    Enforces MCP security and anchor validation.
    Request body: {"command": str, "anchor": str}
    Response: {"status": str, "routed_command": str, "governance_layer": str, "protocol": list}
    """
    mcp_security.validate_anchor(anchor)
    router = MCPCommandRouter()
    return router.route(command)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
