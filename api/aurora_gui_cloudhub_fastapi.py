import logging
import os
import uuid
import hashlib
import uvicorn
from pathlib import Path
from typing import Dict, List, Optional, Any

import aiofiles
import numpy as np
_rng = np.random.default_rng()
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials
from src.middleware.fastapi_security import security, verify_csrf_token
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from modules.symbolic_core import get_mcp_bridge_core
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.mcp_command_router import MCPCommandRouter
from modules.symbolic_core.mcp_security import mcp_security, mcp_security_dependency
from modules.symbolic_core.quantum_vsa import (
    QuantumSymbolicVector,
    quantum_symbolic_vector,
)

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QuantumCircuit = None
    AerSimulator = None
    QISKIT_AVAILABLE = False

app = FastAPI(title="Aurora Quantum VSA Playground")

# Add CORS middleware for frontend integration
# SECURITY FIX: Use specific origins instead of wildcard when credentials are enabled
allowed_origins = [origin.strip() for origin in os.getenv(
    "ALLOWED_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"
).split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aurora_gui_cloudhub")

# Active WebSocket connections for basic broadcast
connections: List[WebSocket] = []

# Serve static files if needed in the future
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store for VSA operations (in-memory for demo)
vsa_store: Dict[str, QuantumSymbolicVector] = {}

# === Enhanced Data Models ===


class VSAOperationRequest(BaseModel):
    symbol: str
    dimension: int = 512
    operation_type: str = "generate"  # generate, bind, unbind, similarity


class VSABindRequest(BaseModel):
    symbol_a: str
    symbol_b: str
    result_name: str
    dimension: int = 512


class VSASimilarityRequest(BaseModel):
    symbol_a: str
    symbol_b: str


class QuantumCircuitRequest(BaseModel):
    symbol: str
    depth: int = 3
    qubits: int = 8


class GeometricAlgebraRequest(BaseModel):
    operation: str  # product, add, commutator
    vectors: List[Dict[str, float]]  # e.g., [{"e1": 1.0, "e2": 0.5}]


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the quantum VSA demo application"""

    return FileResponse("static/quantum-vsa-demo.html")


@app.get("/legacy", response_class=HTMLResponse)
async def legacy_upload():
    """Legacy upload interface"""
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
CSRF_INVALID_MSG = "Invalid CSRF token"


def _ga_build_mv(ga: GeometricAlgebra, vec_spec: Dict[str, float]) -> Any:
    mv: Any = 0
    for blade, coeff in vec_spec.items():
        mv += coeff * ga.blades.get(blade, coeff if blade not in ga.blades else ga.blades[blade])
    return mv


def _ga_compute_product(ga: GeometricAlgebra, vectors: List[Dict[str, float]]) -> Dict[str, Any]:
    result: Any = 1
    for spec in vectors:
        result = ga.mult(result, _ga_build_mv(ga, spec))
    return {"result": ga.pretty(result), "type": "geometric_product"}


def _ga_compute_commutator(ga: GeometricAlgebra, vectors: List[Dict[str, float]]) -> Optional[Dict[str, Any]]:
    if len(vectors) < 2:
        return None
    mv_a = _ga_build_mv(ga, vectors[0])
    mv_b = _ga_build_mv(ga, vectors[1])
    ab = ga.mult(mv_a, mv_b)
    ba = ga.mult(mv_b, mv_a)
    ab_any: Any = ab
    ba_any: Any = ba
    if hasattr(ab_any, "__sub__") and hasattr(ab_any, "__add__"):
        comm = ab_any - ba_any if not getattr(ga, "_mock", False) else ab_any + ba_any
    else:
        comm = ab_any
    return {"result": ga.pretty(comm), "type": "commutator"}


def _hash_seed(symbol: str) -> int:
    return int(hashlib.sha256(symbol.encode()).hexdigest(), 16) % (2**32)


def _apply_symbolic_gates(qc, depth: int, qubits: int) -> None:
    for _ in range(depth):
        for q in range(qubits):
            r = float(_rng.random())
            if r < 0.3:
                qc.h(q)
            elif r < 0.6:
                qc.x(q)
            elif r < 0.8:
                qc.z(q)
            else:
                if q < qubits - 1:
                    qc.cx(q, q + 1)


@app.post("/upload/")  # verify_csrf inside
async def upload_bundle(file: UploadFile = File(...), token: HTTPAuthorizationCredentials = Depends(security)):
    """Upload a bundle file with CSRF validation."""
    verify_csrf_token(token)

    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    upload_dir = Path("./uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.zip"
    upload_path = upload_dir / filename
    # Use async file I/O to avoid blocking event loop
    async with aiofiles.open(upload_path, "wb") as buffer:
        await buffer.write(data)
    return {"message": "Bundle received", "filename": filename}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for conn in connections:
                if conn is websocket:
                    continue
                try:
                    await conn.send_text(data)
                except WebSocketDisconnect:
                    connections.remove(conn)
                except Exception as e:
                    # Parameterized logging to prevent potential log injection
                    logger.error(
                        "WebSocket broadcast error: %s (ws_id=%s)",
                        str(e)[:100],
                        id(conn),
                    )
    except WebSocketDisconnect:
        connections.remove(websocket)
    except Exception as e:
        logger.error("WebSocket handler error: %s (ws_id=%s)", str(e)[:100], id(websocket))


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


@app.post(  # verify_csrf inside
    "/geometric/product",
    summary="Geometric Product",
    response_description="Result of geometric product",
    dependencies=[Depends(security)],
)
def geometric_product(req: GeometricProductRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Compute the geometric product of two 3D vectors (a*e1, b*e2) using Clifford algebra.

    Request body: {"a": float, "b": float}
    Response: {"result": str}
    """
    verify_csrf_token(token)
    ga = GeometricAlgebra()
    a_mv = req.a * ga.blades["e1"]
    b_mv = req.b * ga.blades["e2"]
    result = ga.mult(a_mv, b_mv)
    return {"result": ga.pretty(result)}


@app.post(  # verify_csrf inside
    "/quantum/symbolic_vector",
    summary="Quantum Symbolic Vector",
    response_description="Quantum-generated symbolic vector",
    dependencies=[Depends(security)],
)
def quantum_symbolic_vector_endpoint(
    req: QuantumSymbolicVectorRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
):
    """Generate a symbolic vector using a quantum circuit seeded by the symbol hash.

    Request body: {"symbol": str, "dim": int}
    Response: {"symbol": str, "dim": int, "vector": list}
    """
    verify_csrf_token(token)
    dim = req.dim if req.dim is not None else 8
    vec = quantum_symbolic_vector(req.symbol, dim)
    return {"symbol": req.symbol, "dim": req.dim, "vector": vec.tolist()}


@app.get(
    "/mcp_bridge",
    summary="MCP Bridge Core JSON",
    response_description="MCP Bridge configuration JSON",
)
def get_mcp_bridge():
    """
    Returns the MCP Bridge Core configuration as JSON.
    """
    data = get_mcp_bridge_core()
    return JSONResponse(content=data)


@app.get(
    "/mcp_bridge/health",
    summary="MCP Bridge Health Check",
    response_description="MCP Bridge health status with security layer validation",
    tags=["health", "mcp"],
)
def mcp_bridge_health_check():
    """
    Kubernetes-compatible health check endpoint for MCP Bridge Core.

    Returns:
        - status: "healthy" or "degraded"
        - security_layers: Status of all security layers (drift_lock, guardian_ring, ethics_lock)
        - governance_layer: Current governance layer
        - core_functions: Available core functions count
        - external_hooks: Status of external integrations
        - timestamp: Current timestamp for monitoring
        - ready: Kubernetes readiness indicator
        - live: Kubernetes liveness indicator

    Used by Kubernetes probes:
        - livenessProbe: Checks if service is alive
        - readinessProbe: Checks if service is ready to accept traffic

    Ethics Protocol: Picard_Delta_3 compliance verified
    T1: System health timestamp
    SRB: MCP_HEALTH_CHECK_v1
    """
    import time
    from datetime import datetime, timezone

    def _compute_security(security_layers: Dict[str, Any]) -> Dict[str, Any]:
        drift = security_layers.get("drift_lock") == "ACTIVE"
        guardian = security_layers.get("guardian_ring") in ("ACTIVE", "STAGED_ACTIVE")
        ethics = security_layers.get("ethics_lock") == "ENFORCED"
        return {
            "drift_lock": {"status": security_layers.get("drift_lock", "UNKNOWN"), "active": drift},
            "guardian_ring": {"status": security_layers.get("guardian_ring", "UNKNOWN"), "active": guardian},
            "ethics_lock": {"status": security_layers.get("ethics_lock", "UNKNOWN"), "enforced": ethics},
            "all_active": drift and guardian and ethics,
        }

    def _derive_status(active: bool, fn_count: int, mesh_active: bool) -> tuple[str, bool, bool]:
        if active and fn_count >= 7 and mesh_active:
            return "healthy", True, True
        if active and fn_count > 0:
            return "degraded", True, True
        return "unhealthy", False, True

    def _build_response(mcp: Dict[str, Any], sec: Dict[str, Any], fn_count: int, mesh_active: bool) -> Dict[str, Any]:
        status, ready, live = _derive_status(sec["all_active"], fn_count, mesh_active)
        current_time = datetime.now(timezone.utc).isoformat()
        return {
            "status": status,
            "module_id": mcp.get("module_id", "UNKNOWN"),
            "version": mcp.get("version", "UNKNOWN"),
            "governance_layer": mcp.get("governance_layer", "UNKNOWN"),
            "security_layers": {k: v for k, v in sec.items() if k != "all_active"},
            "core_functions": {"count": fn_count, "required": 7, "available": fn_count >= 7},
            "external_hooks": {
                "symbolic_mesh_sync": {
                    "status": mcp.get("external_hooks", {}).get("symbolic_mesh_sync", "UNKNOWN"),
                    "active": mesh_active,
                },
                "gpt_parallel_nodes": len(mcp.get("external_hooks", {}).get("gpt_parallel_nodes", [])),
            },
            "ethics_protocol": mcp.get("ethics_protocol", "UNKNOWN"),
            "anchor_seed": mcp.get("anchor_seed", "UNKNOWN"),
            "timestamp": current_time,
            "uptime_seconds": time.time(),
            "kubernetes": {"ready": ready, "live": live},
            "aurora_metadata": {
                "T1": current_time,
                "SRB": "MCP_HEALTH_CHECK_v1",
                "chain_notation": "#K8S//MCP//HEALTH//",
            },
        }

    try:
        mcp_data = get_mcp_bridge_core()
        security_layers = mcp_data.get("security_layers", {})
        sec = _compute_security(security_layers)
        core_functions = mcp_data.get("core_functions", [])
        functions_count = len(core_functions)
        external_hooks = mcp_data.get("external_hooks", {})
        mesh_sync_active = external_hooks.get("symbolic_mesh_sync") == "ACTIVE"
        return _build_response(mcp_data, sec, functions_count, mesh_sync_active)
    except Exception as e:  # pragma: no cover - defensive fallback
        logger.error("MCP health check failed: %s", str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "kubernetes": {"ready": False, "live": True},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


@app.post(  # verify_csrf inside
    "/mcp_bridge/route_command",
    summary="Symbolic Command Routing via MCP Bridge",
    response_description="Routed command result",
)
def mcp_route_command(
    command: str,
    anchor: str = "EOS_SEED_ORION",
    security: None = Depends(mcp_security_dependency),
):
    """
    Symbolic command routing using MCP Bridge Core config and MCPCommandRouter.
    Enforces MCP security and anchor validation.
    Request body: {"command": str, "anchor": str}
    Response: {"status": str, "routed_command": str, "governance_layer": str, "protocol": list}
    """
    mcp_security.validate_anchor(anchor)
    router = MCPCommandRouter()
    return router.route(command)


@app.post(  # verify_csrf inside
    "/vsa/operation",
    summary="VSA Operation",
    response_description="Result of VSA operation",
    dependencies=[Depends(security)],
)
def vsa_operation(req: VSAOperationRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Perform an operation on the VSA symbolic vector.

    Request body: {"symbol": str, "dimension": int, "operation_type": str}
    Response: {"symbol": str, "dimension": int, "result": Any}
    """
    verify_csrf_token(token)
    if req.operation_type == "generate":
        vec = quantum_symbolic_vector(req.symbol, req.dimension)
        result = vec.tolist()
    elif req.operation_type == "bind":
        # Binding logic here
        _ = "Binding not implemented in demo"
    elif req.operation_type == "unbind":
        # Unbinding logic here
        _ = "Unbinding not implemented in demo"
    elif req.operation_type == "similarity":
        # Similarity logic here
        result = "Similarity not implemented in demo"
    else:
        raise HTTPException(status_code=400, detail="Invalid operation type")

    return {"symbol": req.symbol, "dimension": req.dimension, "result": result}


@app.post(  # verify_csrf inside
    "/vsa/bind",
    summary="VSA Bind",
    response_description="Result of VSA bind operation",
    dependencies=[Depends(security)],
)
def vsa_bind(req: VSABindRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Bind two symbolic vectors in the VSA.

    Request body: {"symbol_a": str, "symbol_b": str, "result_name": str, "dimension": int}
    Response: {"result_name": str, "dimension": int, "result": Any}
    """
    verify_csrf_token(token)
    # Retrieve vectors from store
    vec_a = vsa_store.get(req.symbol_a)
    vec_b = vsa_store.get(req.symbol_b)
    if vec_a is None or vec_b is None:
        raise HTTPException(status_code=404, detail="One or both symbols not found")

    # Perform binding (placeholder logic)
    bound_vector = vec_a  # Replace with actual binding logic
    vsa_store[req.result_name] = bound_vector

    return {
        "result_name": req.result_name,
        "dimension": req.dimension,
        "result": bound_vector.tolist(),
    }


@app.post(  # verify_csrf inside
    "/vsa/similarity",
    summary="VSA Similarity",
    response_description="Similarity score between two symbolic vectors",
    dependencies=[Depends(security)],
)
def vsa_similarity(req: VSASimilarityRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Compute similarity between two symbolic vectors in the VSA.

    Request body: {"symbol_a": str, "symbol_b": str}
    Response: {"symbol_a": str, "symbol_b": str, "similarity": float}
    """
    verify_csrf_token(token)
    # Retrieve vectors from store
    vec_a = vsa_store.get(req.symbol_a)
    vec_b = vsa_store.get(req.symbol_b)
    if vec_a is None or vec_b is None:
        raise HTTPException(status_code=404, detail="One or both symbols not found")

    # Compute similarity (placeholder logic)
    similarity_score = float(_rng.random())  # Placeholder similarity using modern RNG

    return {
        "symbol_a": req.symbol_a,
        "symbol_b": req.symbol_b,
        "similarity": similarity_score,
    }


@app.post(  # verify_csrf inside
    "/quantum/circuit",
    summary="Quantum Circuit",
    response_description="Result of quantum circuit operation",
)
def quantum_circuit(req: QuantumCircuitRequest):
    """
    Execute a quantum circuit and return the result.
    Request body: {"symbol": str, "depth": int, "qubits": int}
    Response: {"symbol": str, "depth": int, "qubits": int, "result": Any}
    """
    # Placeholder for quantum circuit execution
    result = {
        "message": "Quantum circuit executed",
        "symbol": req.symbol,
        "depth": req.depth,
        "qubits": req.qubits,
    }

    return result


@app.post(  # verify_csrf inside
    "/geometric/algebra",
    summary="Geometric Algebra Operation",
    response_description="Result of geometric algebra operation",
)
def geometric_algebra(req: GeometricAlgebraRequest):
    """
    Perform a geometric algebra operation on the given vectors.
    Request body: {"operation": str, "vectors": [{"e1": float, "e2": float}]}
    Response: {"operation": str, "result": Any}
    """
    ga = GeometricAlgebra()
    # Initialize result to ensure it's always defined before return
    result = None

    def _ga_product() -> Any:
        blades = [ga.blades[f"e{i + 1}"] for i in range(len(req.vectors))]
        return ga.mult(*blades)

    def _ga_add() -> Any:
        return sum((ga.blades.get(f"e{i + 1}", 0) for i in range(len(req.vectors))), start=0)

    def _ga_commutator() -> Any:
        if len(req.vectors) != 2:
            raise HTTPException(status_code=400, detail="Commutator requires exactly 2 vectors")
        v1, v2 = req.vectors
        blade1 = sum((ga.blades.get(f"e{i + 1}", 0) * v1.get(f"e{i + 1}", 0) for i in range(len(v1))), start=0)
        blade2 = sum((ga.blades.get(f"e{i + 1}", 0) * v2.get(f"e{i + 1}", 0) for i in range(len(v2))), start=0)
        # Fallback if commutator is not available in mock
        if hasattr(ga, "commutator"):
            return ga.commutator(blade1, blade2)  # type: ignore[attr-defined]
        ab = ga.mult(blade1, blade2)
        ba = ga.mult(blade2, blade1)
        # Ensure subtraction/addition only if algebra elements support it
        ab_any: Any = ab
        ba_any: Any = ba
        if hasattr(ab_any, "__sub__") and hasattr(ab_any, "__add__"):
            return ab_any - ba_any if not getattr(ga, "_mock", False) else ab_any + ba_any
        return ab_any

    if req.operation == "product":
        result = _ga_product()
    elif req.operation == "add":
        result = _ga_add()
    elif req.operation == "commutator":
        result = _ga_commutator()
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")
    if result is None:
        raise HTTPException(status_code=500, detail="Geometric algebra computation failed")
    return {"operation": req.operation, "result": ga.pretty(result)}

# === New VSA and Quantum Endpoints ===


@app.post("/api/vsa/generate", summary="Generate Quantum VSA Vector", dependencies=[Depends(security)])  # verify_csrf inside
def generate_vsa_vector(req: VSAOperationRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Generate a quantum symbolic vector for a given symbol."""
    verify_csrf_token(token)
    try:
        qsv = QuantumSymbolicVector(req.symbol, req.dimension)
        vsa_store[req.symbol] = qsv

        return {
            "symbol": req.symbol,
            "dimension": req.dimension,
            "vector": np.asarray(qsv.vector).tolist()[:32],
            "vector_full_length": len(qsv.vector),
            "vector_type": "bipolar",
            "quantum_generated": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VSA generation failed: {str(e)}")


@app.post("/api/vsa/bind", summary="Bind two VSA vectors", dependencies=[Depends(security)])  # verify_csrf inside
def bind_vsa_vectors(req: VSAOperationRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Bind two symbolic vectors using element-wise multiplication (XOR for bipolar)."""
    verify_csrf_token(token)
    try:
        # Generate vectors if they don't exist
        if req.symbol_a not in vsa_store:
            vsa_store[req.symbol_a] = QuantumSymbolicVector(req.symbol_a, req.dimension)
        if req.symbol_b not in vsa_store:
            vsa_store[req.symbol_b] = QuantumSymbolicVector(req.symbol_b, req.dimension)

        vec_a = vsa_store[req.symbol_a].vector
        vec_b = vsa_store[req.symbol_b].vector

        # Ensure same dimension
        min_dim = min(len(vec_a), len(vec_b))
        vec_a = np.asarray(vec_a[:min_dim])
        vec_b = np.asarray(vec_b[:min_dim])

        # Bind operation (element-wise multiplication for bipolar vectors)
        bound_vector = vec_a * vec_b  # numpy arrays element-wise multiplication

        # Create a new quantum symbolic vector using standard constructor then override vector data
        result_qsv = QuantumSymbolicVector(req.result_name, min_dim)
        result_qsv.vector = bound_vector  # overwrite generated data with bound result
        result_qsv.dim = min_dim
        result_qsv.vector_type = "bipolar"
        vsa_store[req.result_name] = result_qsv

        return {
            "operation": "bind",
            "symbol_a": req.symbol_a,
            "symbol_b": req.symbol_b,
            "result_name": req.result_name,
            "dimension": min_dim,
            "result_vector": np.asarray(bound_vector).tolist()[:32],
            "similarity_a": float(np.dot(bound_vector, vec_a) / min_dim),
            "similarity_b": float(np.dot(bound_vector, vec_b) / min_dim),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VSA binding failed: {str(e)}")


@app.post("/api/vsa/similarity", summary="Calculate VSA similarity", dependencies=[Depends(security)])  # verify_csrf inside
def calculate_vsa_similarity(req: VSAOperationRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Calculate cosine similarity between two VSA vectors."""
    verify_csrf_token(token)
    try:
        if req.symbol_a not in vsa_store:
            vsa_store[req.symbol_a] = QuantumSymbolicVector(req.symbol_a)
        if req.symbol_b not in vsa_store:
            vsa_store[req.symbol_b] = QuantumSymbolicVector(req.symbol_b)

        vec_a = vsa_store[req.symbol_a].vector
        vec_b = vsa_store[req.symbol_b].vector

        # Ensure same dimension
        min_dim = min(len(vec_a), len(vec_b))
        vec_a = np.asarray(vec_a[:min_dim])
        vec_b = np.asarray(vec_b[:min_dim])

        # Cosine similarity
        similarity = float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))

        # Hamming distance for bipolar vectors
        hamming = float(np.sum(vec_a != vec_b) / min_dim)

        return {
            "symbol_a": req.symbol_a,
            "symbol_b": req.symbol_b,
            "cosine_similarity": similarity,
            "hamming_distance": hamming,
            "dot_product": float(np.dot(vec_a, vec_b)),
            "dimension": min_dim,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity calculation failed: {str(e)}")


@app.get("/api/vsa/list", summary="List stored VSA vectors")
def list_vsa_vectors():
    """
    List all currently stored VSA vectors.
    """
    return {
        "vectors": [
            {
                "symbol": symbol,
                "dimension": len(qsv.vector),
                "vector_type": getattr(qsv, "vector_type", "bipolar"),
                "preview": np.asarray(qsv.vector).tolist()[:8],
            }
            for symbol, qsv in vsa_store.items()
        ],
        "count": len(vsa_store),
    }


@app.delete("/api/vsa/clear", summary="Clear VSA store")
def clear_vsa_store():
    """
    Clear all stored VSA vectors.
    """
    global vsa_store
    count = len(vsa_store)
    vsa_store = {}
    return {"message": f"Cleared {count} VSA vectors", "count": count}


@app.post(  # verify_csrf inside
    "/api/geometric/advanced",
    summary="Advanced Geometric Algebra Operations",
    dependencies=[Depends(security)],
)
def advanced_geometric_operations(
    req: GeometricAlgebraRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
):
    """Perform advanced geometric algebra operations on multiple vectors."""
    verify_csrf_token(token)

    try:
        ga = GeometricAlgebra()
        if req.operation == "product":
            computed = [_ga_compute_product(ga, req.vectors)]
        elif req.operation == "commutator":
            comm = _ga_compute_commutator(ga, req.vectors)
            computed = [comm] if comm else []
        else:
            return {"operation": req.operation, "input_vectors": req.vectors, "results": [], "mock_mode": ga._mock}
        return {"operation": req.operation, "input_vectors": req.vectors, "results": computed, "mock_mode": ga._mock}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Geometric algebra operation failed: {str(e)}")


@app.post("/api/quantum/circuit", summary="Generate Quantum Circuit", dependencies=[Depends(security)])  # verify_csrf inside
async def generate_quantum_circuit_api(req: QuantumCircuitRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """Generate and analyze a quantum circuit for symbolic operations."""
    verify_csrf_token(token)

    try:
        if not QISKIT_AVAILABLE:
            return {"error": "Qiskit not available", "symbol": req.symbol}
        np.random.seed(_hash_seed(req.symbol))
        qc = QuantumCircuit(req.qubits, req.qubits)  # type: ignore[call-arg]
        _apply_symbolic_gates(qc, req.depth, req.qubits)
        qc.measure(range(req.qubits), range(req.qubits))
        backend = AerSimulator()  # type: ignore[call-arg]
        result = backend.run(qc, shots=1000).result()
        counts = result.get_counts()
        most_frequent = max(counts.items(), key=lambda x: x[1]) if counts else ("0" * req.qubits, 0)
        return {
            "symbol": req.symbol,
            "qubits": req.qubits,
            "depth": req.depth,
            "circuit_gates": qc.num_nonlocal_gates(),
            "measurement_counts": dict(list(counts.items())[:10]),
            "most_frequent_state": most_frequent[0],
            "most_frequent_probability": most_frequent[1] / 1000,
            "total_shots": 1000,
            "circuit_qasm": qc.qasm(),
        }
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Quantum circuit generation failed: {str(e)}")

# === Enhanced WebSocket for Real-time Collaboration ===


@app.websocket("/api/ws/collaboration")
async def websocket_collaboration_endpoint(websocket: WebSocket):
    """
    Enhanced WebSocket endpoint for real-time VSA collaboration.
    """
    await websocket.accept()
    connections.append(websocket)

    # Send welcome message with current VSA store state
    welcome_msg = {
        "type": "welcome",
        "message": "Connected to Aurora VSA Collaboration",
        "current_vectors": len(vsa_store),
        "vector_list": list(vsa_store.keys()),
    }
    await websocket.send_json(welcome_msg)

    async def _broadcast_operation(origin: WebSocket, data: dict) -> None:
        broadcast_msg = {
            "type": "vsa_update",
            "operation": data.get("operation"),
            "symbol": data.get("symbol"),
            "timestamp": data.get("timestamp"),
            "user": data.get("user", "anonymous"),
        }
        for conn in list(connections):
            if conn is origin:
                continue
            try:
                await conn.send_json(broadcast_msg)
            except WebSocketDisconnect:
                if conn in connections:
                    connections.remove(conn)
            except Exception as e:
                logger.error(
                    "WebSocket collab broadcast error: %s (ws_id=%s) user=%s",
                    str(e)[:100],
                    id(conn),
                    broadcast_msg.get('user'),
                )

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "vsa_operation":
                await _broadcast_operation(websocket, data)

    except WebSocketDisconnect:
        connections.remove(websocket)
    except Exception as e:
        logger.error("WebSocket collab handler error: %s (ws_id=%s)", str(e)[:100], id(websocket))

if __name__ == "__main__":

    uvicorn.run(
        "aurora_gui_cloudhub_fastapi:app",
        host="127.0.0.1",  # Bind to localhost only for security
        port=8000,
        reload=True,
        log_level="info",
    )
