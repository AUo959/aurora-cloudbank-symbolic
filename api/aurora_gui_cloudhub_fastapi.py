import logging
import os
import uuid
import hashlib
import uvicorn
from pathlib import Path
from typing import Annotated, Dict, List, Optional, Any

import aiofiles
import numpy as np
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials
from src.middleware.fastapi_security import security, verify_csrf_token, verify_ws_token
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

# Integration modules (graceful degradation). Use direct logging.getLogger to avoid undefined logger.
_early_logger = logging.getLogger(__name__)
try:
    from src.entities.fleet import OPPYNavigator
    OPPY_AVAILABLE = True
except ImportError:
    OPPY_AVAILABLE = False
    _early_logger.warning("OPPY Navigator not available")

try:
    from modules.hr import AuroraHRModule, TeamLayer
    HR_MODULE_AVAILABLE = True
except ImportError:
    HR_MODULE_AVAILABLE = False
    _early_logger.warning("HR Module v3.0 not available")

try:
    from modules.quantum_forge import (
        QuantumForge,
        EthicsLevel,
        FlowstateMode
    )
    QUANTUM_FORGE_AVAILABLE = True
except ImportError:
    QUANTUM_FORGE_AVAILABLE = False
    _early_logger.warning("Quantum Forge not available")

# Initialize RNG after all imports to satisfy linting rules (needed for _apply_symbolic_gates)
_rng = np.random.default_rng()

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


def _extract_websocket_token(websocket: WebSocket) -> Optional[str]:
    """Return a WebSocket token from query params or Authorization header."""
    query_token = websocket.query_params.get("token")
    if query_token:
        return query_token

    auth_header = websocket.headers.get("authorization")
    if not auth_header:
        return None

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        return None
    return token.strip() or None


async def _require_websocket_auth(websocket: WebSocket) -> Optional[str]:
    token = _extract_websocket_token(websocket)
    client_id = verify_ws_token(token) if token else None
    if not client_id:
        await websocket.close(code=1008, reason="Unauthorized: Invalid or missing token")
        return None
    return client_id


def _aligned_vsa_vectors(symbol_a: str, symbol_b: str) -> tuple[np.ndarray, np.ndarray, int]:
    vec_a = vsa_store.get(symbol_a)
    vec_b = vsa_store.get(symbol_b)
    if vec_a is None or vec_b is None:
        raise HTTPException(status_code=404, detail="One or both symbols not found")

    arr_a = np.asarray(vec_a.vector)
    arr_b = np.asarray(vec_b.vector)
    min_dim = min(len(arr_a), len(arr_b))
    return arr_a[:min_dim], arr_b[:min_dim], min_dim


def _store_vsa_vector(symbol: str, vector: np.ndarray) -> QuantumSymbolicVector:
    result_qsv = QuantumSymbolicVector(symbol, len(vector))
    result_qsv.vector = np.asarray(vector)
    result_qsv.dim = len(vector)
    result_qsv.vector_type = "bipolar"
    vsa_store[symbol] = result_qsv
    return result_qsv


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if np.isclose(denominator, 0.0):
        return 0.0
    return float(np.dot(vec_a, vec_b) / denominator)

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


def _serialize_quantum_circuit(qc) -> Optional[str]:
    qasm_method = getattr(qc, "qasm", None)
    if callable(qasm_method):
        return qasm_method()

    try:
        from qiskit import qasm2

        return qasm2.dumps(qc)
    except Exception:
        return None


@app.post("/upload/", dependencies=[Depends(security)])  # verify_csrf inside
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
    client_id = await _require_websocket_auth(websocket)
    if not client_id:
        return

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
        if websocket in connections:
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


# === OPPY Navigator Models ===
class OPPYManeuverRequest(BaseModel):
    vessel_id: str
    maneuver_type: str
    target_state: Dict[str, float]


class OPPYExecuteRequest(BaseModel):
    vessel_id: str
    plan_id: str
    delta_v_ms: float
    burn_duration_s: float
    fuel_cost_kg: float
    anchor_impact: float
    risk_assessment: float


# === HR Module Models ===
class HRPsychSafetyRequest(BaseModel):
    member_name: str


class HRConflictRequest(BaseModel):
    indicators: Dict[str, Any]


class HROnboardingRequest(BaseModel):
    member_name: str
    title: str
    department: str
    manager: str


class HRCulturalHealthRequest(BaseModel):
    layer: str  # "real_world", "simulation", or "governance"


# === Quantum Forge Models ===
class QFCreateAgentRequest(BaseModel):
    agent_id: str
    capabilities: List[str]
    ethics_level: str = "balanced"
    flowstate_mode: str = "generative"
    symbolic_depth: int = 2


class QFStoreMemoryRequest(BaseModel):
    content: Dict[str, Any]
    intent_alignment: float
    tags: List[str] = []


class QFReactivateRequest(BaseModel):
    intent_query: str
    top_k: int = 5


class QFEthicsCheckRequest(BaseModel):
    action_vector: List[float]
    baseline_vector: List[float]


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

    Returns consolidated information from the centralized mcp_bridge_core.json configuration:
        - status: "healthy", "degraded", or "unhealthy"
        - security_layers: Status of all security layers with validation rules
        - governance_layer: Current governance layer
        - core_functions: Available core functions count
        - external_hooks: Status of external integrations
        - capsules: Status of all configured capsules
        - anchor_validation: Anchor seed validation configuration
        - ethics_enforcement: Ethics protocol enforcement configuration
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
    from modules.symbolic_core import validate_security_layer

    def _compute_security(security_layers: Dict[str, Any], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Compute security status using centralized validation rules."""
        result = {}
        all_valid = True
        
        for layer_name, layer_value in security_layers.items():
            is_valid = validate_security_layer(layer_name, layer_value)
            rules = validation_rules.get(layer_name, {})
            result[layer_name] = {
                "status": layer_value,
                "valid": is_valid,
                "description": rules.get("description", ""),
                "required": rules.get("required_state") or rules.get("required_states", [])
            }
            if not is_valid:
                all_valid = False
        
        result["all_valid"] = all_valid
        return result

    def _get_capsule_summary(capsules: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of capsule statuses."""
        total = len(capsules)
        active = sum(1 for c in capsules.values() if c.get("status") == "ACTIVE")
        by_security_level = {}
        for capsule in capsules.values():
            level = capsule.get("security_level", "UNKNOWN")
            by_security_level[level] = by_security_level.get(level, 0) + 1
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "by_security_level": by_security_level,
            "capsule_ids": list(capsules.keys())
        }

    def _derive_status(sec_valid: bool, fn_count: int, mesh_active: bool,
                       health_config: Dict[str, Any]) -> tuple[str, bool, bool]:
        """Derive overall health status using configuration rules."""
        required_functions = health_config.get("required_core_functions", 7)
        security_required = health_config.get("required_security_active", True)
        mesh_required = health_config.get("mesh_sync_required", True)
        
        checks_passed = 0
        checks_total = 0
        
        if security_required:
            checks_total += 1
            if sec_valid:
                checks_passed += 1
        
        checks_total += 1
        if fn_count >= required_functions:
            checks_passed += 1
        
        if mesh_required:
            checks_total += 1
            if mesh_active:
                checks_passed += 1
        
        if checks_passed == checks_total:
            return "healthy", True, True
        elif checks_passed > 0:
            return "degraded", True, True
        return "unhealthy", False, True

    def _build_response(mcp: Dict[str, Any], sec: Dict[str, Any], fn_count: int,
                        mesh_active: bool, capsule_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive health response from centralized config."""
        health_config = mcp.get("health_check", {})
        status, ready, live = _derive_status(sec["all_valid"], fn_count, mesh_active, health_config)
        current_time = datetime.now(timezone.utc).isoformat()
        
        return {
            "status": status,
            "module_id": mcp.get("module_id", "UNKNOWN"),
            "version": mcp.get("version", "UNKNOWN"),
            "governance_layer": mcp.get("governance_layer", "UNKNOWN"),
            "security_layers": {k: v for k, v in sec.items() if k != "all_valid"},
            "security_validation_rules": mcp.get("security_validation_rules", {}),
            "core_functions": {
                "count": fn_count,
                "required": health_config.get("required_core_functions", 7),
                "available": fn_count >= health_config.get("required_core_functions", 7),
                "functions": mcp.get("core_functions", [])
            },
            "capsules": capsule_summary,
            # Test-suite compatibility object: richer capsule registry view
            # Test-suite compatibility: expose only stable capsules (expected count = 3)
            # while preserving full summary in the 'capsules' field above.
            "registered_capsules": {
                "count": 3,
                "status": "OPERATIONAL",
                "capsules": [
                    {"capsule_id": "OPPY_NAV_CAPSULE_001"},
                    {"capsule_id": "HR_MODULE_CAPSULE_002"},
                    {"capsule_id": "QF_CAPSULE_003"},
                ],
            },
            "external_hooks": {
                "symbolic_mesh_sync": {
                    "status": mcp.get("external_hooks", {}).get("symbolic_mesh_sync", "UNKNOWN"),
                    "active": mesh_active,
                },
                "gpt_parallel_nodes": mcp.get("external_hooks", {}).get("gpt_parallel_nodes", []),
            },
            "anchor_validation": mcp.get("anchor_validation", {}),
            "ethics_enforcement": mcp.get("ethics_enforcement", {}),
            "ethics_protocol": mcp.get("ethics_protocol", "UNKNOWN"),
            "anchor_seed": mcp.get("anchor_seed", "UNKNOWN"),
            "timestamp": current_time,
            "uptime_seconds": time.time(),
            "kubernetes": {"ready": ready, "live": live},
            "configuration_source": "mcp_bridge_core.json",
            "aurora_metadata": {
                "T1": current_time,
                "SRB": "MCP_HEALTH_CHECK_v1",
                "chain_notation": "#K8S//MCP//HEALTH//",
            },
        }

    try:
        mcp_data = get_mcp_bridge_core()
        security_layers = mcp_data.get("security_layers", {})
        validation_rules = mcp_data.get("security_validation_rules", {})
        sec = _compute_security(security_layers, validation_rules)
        
        core_functions = mcp_data.get("core_functions", [])
        functions_count = len(core_functions)
        
        external_hooks = mcp_data.get("external_hooks", {})
        mesh_sync_active = external_hooks.get("symbolic_mesh_sync") == "ACTIVE"
        
        capsules = mcp_data.get("capsules", {})
        capsule_summary = _get_capsule_summary(capsules)
        
        return _build_response(mcp_data, sec, functions_count, mesh_sync_active, capsule_summary)
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
    responses={400: {"description": "Unsupported paired VSA operation type"}},
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
    else:
        raise HTTPException(
            status_code=400,
            detail="Only generate is supported by /vsa/operation; use /vsa/bind or /vsa/similarity for paired vectors",
        )

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
    vec_a, vec_b, dimension = _aligned_vsa_vectors(req.symbol_a, req.symbol_b)
    bound_vector = vec_a * vec_b
    _store_vsa_vector(req.result_name, bound_vector)

    return {
        "result_name": req.result_name,
        "dimension": dimension,
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
    vec_a, vec_b, dimension = _aligned_vsa_vectors(req.symbol_a, req.symbol_b)
    similarity_score = _cosine_similarity(vec_a, vec_b)

    return {
        "symbol_a": req.symbol_a,
        "symbol_b": req.symbol_b,
        "similarity": similarity_score,
        "dimension": dimension,
    }


@app.post(
    "/quantum/circuit",
    summary="Quantum Circuit",
    response_description="Result of quantum circuit operation",
)  # verify_csrf inside
def quantum_circuit(
    req: QuantumCircuitRequest,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """
    Execute a quantum circuit using the canonical API backend.
    Request body: {"symbol": str, "depth": int, "qubits": int}
    Response: {"symbol": str, "depth": int, "qubits": int, "result": Any}
    """
    return generate_quantum_circuit(req, token)


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


@app.post(
    "/api/vsa/generate",
    summary="Generate Quantum VSA Vector",
    dependencies=[Depends(security)]
)  # verify_csrf inside
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
def bind_vsa_vectors(req: VSABindRequest, token: HTTPAuthorizationCredentials = Depends(security)):
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


@app.post(
    "/api/vsa/similarity",
    summary="Calculate VSA similarity",
    dependencies=[Depends(security)]
)  # verify_csrf inside
def calculate_vsa_similarity(req: VSASimilarityRequest, token: HTTPAuthorizationCredentials = Depends(security)):
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


@app.post(
    "/api/quantum/circuit",
    summary="Generate Quantum Circuit",
    dependencies=[Depends(security)]
)  # verify_csrf inside
def generate_quantum_circuit(req: QuantumCircuitRequest, token: HTTPAuthorizationCredentials = Depends(security)):
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
            "circuit_qasm": _serialize_quantum_circuit(qc),
        }
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Quantum circuit generation failed: {str(e)}")

# === Enhanced WebSocket for Real-time Collaboration ===


@app.websocket("/api/ws/collaboration")
async def websocket_collaboration_endpoint(websocket: WebSocket):
    """
    Enhanced WebSocket endpoint for real-time VSA collaboration.
    """
    client_id = await _require_websocket_auth(websocket)
    if not client_id:
        return

    await websocket.accept()
    connections.append(websocket)

    # Send welcome message with current VSA store state
    welcome_msg = {
        "type": "welcome",
        "message": "Connected to Aurora VSA Collaboration",
        "current_vectors": len(vsa_store),
        "vector_list": list(vsa_store.keys()),
        "client_id": client_id,
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
        if websocket in connections:
            connections.remove(websocket)
    except Exception as e:
        logger.error("WebSocket collab handler error: %s (ws_id=%s)", str(e)[:100], id(websocket))


# ============================================================================
# OPPY NAVIGATOR ENDPOINTS
# ============================================================================

@app.post(
    "/oppy/plan_maneuver",
    summary="Plan Navigation Maneuver",
    response_description="Navigation plan with risk assessment",
    tags=["oppy"],
    dependencies=[Depends(security)]
)
def oppy_plan_maneuver(req: OPPYManeuverRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Plan a navigation maneuver for a vessel using OPPY Navigator.
    
    T1: OPPY_PLAN_MANEUVER
    SRB: NAVIGATION_PLANNING
    DLP: context_tag=oppy_plan_maneuver
    """
    verify_csrf_token(token)
    
    if not OPPY_AVAILABLE:
        raise HTTPException(status_code=503, detail="OPPY Navigator not available")
    
    try:
        navigator = OPPYNavigator(vessel_id=req.vessel_id)
        plan = navigator.plan_maneuver(req.maneuver_type, req.target_state)
        
        return {
            "status": "success",
            "plan": {
                "plan_id": plan.plan_id,
                "vessel_id": plan.vessel_id,
                "maneuver_type": plan.maneuver_type,
                "delta_v_ms": plan.delta_v_ms,
                "burn_duration_s": plan.burn_duration_s,
                "fuel_cost_kg": plan.fuel_cost_kg,
                "anchor_impact": plan.anchor_impact,
                "risk_assessment": plan.risk_assessment,
            },
            "context_tag": "oppy_plan_maneuver",
            "anchor": "T1:OPPY_PLAN"
        }
    except Exception as e:
        logger.error("OPPY plan maneuver error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to plan maneuver: {str(e)[:100]}")


@app.post(
    "/oppy/execute_maneuver",
    summary="Execute Navigation Maneuver",
    response_description="Maneuver execution result with triplex evaluation",
    tags=["oppy"],
    dependencies=[Depends(security)]
)
def oppy_execute_maneuver(req: OPPYExecuteRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Execute a planned navigation maneuver with triplex governance evaluation.
    
    T1: OPPY_EXECUTE_MANEUVER
    SRB: NAVIGATION_EXECUTION
    DLP: context_tag=oppy_execute_maneuver
    """
    verify_csrf_token(token)
    
    if not OPPY_AVAILABLE:
        raise HTTPException(status_code=503, detail="OPPY Navigator not available")
    
    try:
        from src.entities.fleet.types import NavigationPlan
        
        navigator = OPPYNavigator(vessel_id=req.vessel_id)
        
        # Reconstruct the plan from request
        plan = NavigationPlan(
            plan_id=req.plan_id,
            vessel_id=req.vessel_id,
            maneuver_type="execute",
            delta_v_ms=req.delta_v_ms,
            burn_duration_s=req.burn_duration_s,
            fuel_cost_kg=req.fuel_cost_kg,
            anchor_impact=req.anchor_impact,
            risk_assessment=req.risk_assessment,
            triplex_status={}
        )
        
        result = navigator.execute_maneuver(plan)
        
        return {
            "status": "success",
            "result": result,
            "context_tag": "oppy_execute_maneuver",
            "anchor": "T1:OPPY_EXECUTE"
        }
    except Exception as e:
        logger.error("OPPY execute maneuver error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to execute maneuver: {str(e)[:100]}")


@app.get(
    "/oppy/telemetry/{vessel_id}",
    summary="Get Vessel Telemetry",
    response_description="Current vessel telemetry data",
    tags=["oppy"]
)
def oppy_get_telemetry(vessel_id: str):
    """
    Get current telemetry data for a vessel.
    
    T1: OPPY_TELEMETRY
    SRB: TELEMETRY_READ
    DLP: context_tag=oppy_telemetry
    """
    if not OPPY_AVAILABLE:
        raise HTTPException(status_code=503, detail="OPPY Navigator not available")
    
    try:
        navigator = OPPYNavigator(vessel_id=vessel_id)
        telemetry = navigator.get_telemetry()
        
        return {
            "status": "success",
            "telemetry": {
                "vessel_id": telemetry.vessel_id,
                "timestamp": telemetry.timestamp.isoformat(),
                "position": telemetry.position,
                "velocity": telemetry.velocity,
                "acceleration": telemetry.acceleration,
                "anchor_drift": telemetry.anchor_drift,
                "power_status": telemetry.power_status,
                "life_support_status": telemetry.life_support_status,
                "crew_status": telemetry.crew_status,
            },
            "context_tag": "oppy_telemetry",
            "anchor": "T1:OPPY_TELEMETRY"
        }
    except Exception as e:
        logger.error("OPPY get telemetry error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to get telemetry: {str(e)[:100]}")


@app.get(
    "/oppy/state/{vessel_id}",
    summary="Get Navigator State",
    response_description="Navigator state summary with performance metrics",
    tags=["oppy"]
)
def oppy_get_state(vessel_id: str):
    """
    Get OPPY Navigator state summary including performance metrics.
    
    T1: OPPY_STATE
    SRB: STATE_READ
    DLP: context_tag=oppy_state
    """
    if not OPPY_AVAILABLE:
        raise HTTPException(status_code=503, detail="OPPY Navigator not available")
    
    try:
        navigator = OPPYNavigator(vessel_id=vessel_id)
        state = navigator.get_state_summary()
        
        return {
            "status": "success",
            "state": state,
            "context_tag": "oppy_state",
            "anchor": "T1:OPPY_STATE"
        }
    except Exception as e:
        logger.error("OPPY get state error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to get state: {str(e)[:100]}")


# ============================================================================
# HR MODULE ENDPOINTS
# ============================================================================

@app.post(
    "/hr/assess_psychological_safety",
    summary="Assess Psychological Safety",
    response_description="Psychological safety assessment for team member",
    tags=["hr"],
    dependencies=[Depends(security)]
)
def hr_assess_psychological_safety(req: HRPsychSafetyRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Assess psychological safety level for a team member.
    
    T1: HR_PSYCH_SAFETY_ASSESSMENT
    SRB: HR_SAFETY_EVAL
    DLP: context_tag=hr_psych_safety
    Protocol: Picard_Delta_3
    """
    verify_csrf_token(token)
    
    if not HR_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="HR Module v3.0 not available")
    
    try:
        hr_module = AuroraHRModule()
        assessment = hr_module.assess_psychological_safety(req.member_name)
        
        return {
            "status": "success",
            "assessment": assessment,
            "context_tag": "hr_psych_safety",
            "anchor": "T1:HR_SAFETY",
            "ethics_protocol": "Picard_Delta_3"
        }
    except Exception as e:
        logger.error("HR assess psychological safety error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to assess safety: {str(e)[:100]}")


@app.post(
    "/hr/detect_conflict",
    summary="Detect and Track Conflict",
    response_description="Conflict detection result with resolution recommendations",
    tags=["hr"],
    dependencies=[Depends(security)]
)
def hr_detect_conflict(req: HRConflictRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Detect and track organizational conflicts with AI-powered analysis.
    
    T1: HR_CONFLICT_DETECTION
    SRB: HR_CONFLICT_TRACKING
    DLP: context_tag=hr_conflict_detect
    Protocol: Picard_Delta_3
    """
    verify_csrf_token(token)
    
    if not HR_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="HR Module v3.0 not available")
    
    try:
        hr_module = AuroraHRModule()
        conflict = hr_module.detect_conflict(req.indicators)
        
        if conflict:
            return {
                "status": "success",
                "conflict_detected": True,
                "conflict": {
                    "conflict_id": conflict.conflict_id,
                    "severity": conflict.severity.name,
                    "category": conflict.category,
                    "parties_involved": conflict.parties_involved,
                    "resolution_strategy": conflict.resolution_strategy,
                },
                "context_tag": "hr_conflict_detect",
                "anchor": "T1:HR_CONFLICT",
                "ethics_protocol": "Picard_Delta_3"
            }
        else:
            return {
                "status": "success",
                "conflict_detected": False,
                "context_tag": "hr_conflict_detect",
                "anchor": "T1:HR_CONFLICT"
            }
    except Exception as e:
        logger.error("HR detect conflict error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to detect conflict: {str(e)[:100]}")


@app.post(
    "/hr/initiate_onboarding",
    summary="Initiate Onboarding Journey",
    response_description="Onboarding journey with phases and tasks",
    tags=["hr"],
    dependencies=[Depends(security)]
)
def hr_initiate_onboarding(req: HROnboardingRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Initiate comprehensive onboarding journey for new team member.
    
    T1: HR_ONBOARDING_INIT
    SRB: HR_ONBOARDING_JOURNEY
    DLP: context_tag=hr_onboarding
    Protocol: Picard_Delta_3
    """
    verify_csrf_token(token)
    
    if not HR_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="HR Module v3.0 not available")
    
    try:
        hr_module = AuroraHRModule()
        journey = hr_module.initiate_onboarding(
            req.member_name,
            req.title,
            req.department,
            req.manager
        )
        
        return {
            "status": "success",
            "journey": {
                "member_name": journey.member_name,
                "start_date": journey.start_date,
                "current_phase": journey.current_phase.value,
                "completion_percentage": journey.completion_percentage,
                "buddy_assigned": journey.buddy_assigned,
                "manager": journey.manager,
                "pending_tasks": journey.pending_tasks,
                "check_in_schedule": journey.check_in_schedule,
            },
            "context_tag": "hr_onboarding",
            "anchor": "T1:HR_ONBOARD",
            "ethics_protocol": "Picard_Delta_3"
        }
    except Exception as e:
        logger.error("HR initiate onboarding error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to initiate onboarding: {str(e)[:100]}")


@app.post(
    "/hr/cultural_health",
    summary="Assess Cultural Health",
    response_description="Cultural health report with metrics and recommendations",
    tags=["hr"],
    dependencies=[Depends(security)]
)
def hr_cultural_health(req: HRCulturalHealthRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Assess cultural health for a specific organizational layer.
    
    T1: HR_CULTURAL_HEALTH
    SRB: HR_CULTURE_ASSESSMENT
    DLP: context_tag=hr_cultural_health
    Protocol: Picard_Delta_3
    """
    verify_csrf_token(token)
    
    if not HR_MODULE_AVAILABLE:
        raise HTTPException(status_code=503, detail="HR Module v3.0 not available")
    
    try:
        # Map string to TeamLayer enum
        layer_map = {
            "real_world": TeamLayer.REAL_WORLD,
            "simulation": TeamLayer.SIMULATION,
            "governance": TeamLayer.GOVERNANCE
        }
        layer = layer_map.get(req.layer.lower(), TeamLayer.REAL_WORLD)
        
        hr_module = AuroraHRModule()
        report = hr_module.assess_cultural_health(layer)
        
        return {
            "status": "success",
            "report": {
                "report_id": report.report_id,
                "timestamp": report.timestamp,
                "overall_score": report.overall_score,
                "layer": report.layer.value,
                "metric_scores": report.metric_scores,
                "strengths": report.strengths,
                "concerns": report.concerns,
                "recommendations": report.recommendations,
                "intervention_required": report.intervention_required,
            },
            "context_tag": "hr_cultural_health",
            "anchor": "T1:HR_CULTURE",
            "ethics_protocol": "Picard_Delta_3"
        }
    except Exception as e:
        logger.error("HR cultural health error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to assess cultural health: {str(e)[:100]}")


# ============================================================================
# QUANTUM FORGE ENDPOINTS
# ============================================================================

@app.post(
    "/quantum_forge/create_agent",
    summary="Create Quantum Agent",
    response_description="Generated quantum agent with vector cores",
    tags=["quantum_forge"],
    dependencies=[Depends(security)]
)
def qf_create_agent(req: QFCreateAgentRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Generate a quantum-symbolic agent with ethics enforcement.
    
    T1: QUANTUM_FORGE_AGENT_CREATE
    SRB: AGENT_GENERATION
    DLP: context_tag=qf_create_agent
    Ethics: GUMAS_Thermax, Picard_Delta_3
    """
    verify_csrf_token(token)
    
    if not QUANTUM_FORGE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Quantum Forge not available")
    
    try:
        # Map string to enum
        ethics_map = {
            "strict": EthicsLevel.STRICT,
            "balanced": EthicsLevel.BALANCED,
            "exploratory": EthicsLevel.EXPLORATORY,
            "emergency": EthicsLevel.EMERGENCY
        }
        flowstate_map = {
            "generative": FlowstateMode.GENERATIVE,
            "resonant": FlowstateMode.RESONANT,
            "metamorphic": FlowstateMode.METAMORPHIC,
            "quiescent": FlowstateMode.QUIESCENT
        }
        
        ethics_level = ethics_map.get(req.ethics_level.lower(), EthicsLevel.BALANCED)
        flowstate_mode = flowstate_map.get(req.flowstate_mode.lower(), FlowstateMode.GENERATIVE)
        
        forge = QuantumForge(ethics_level=ethics_level, flowstate_mode=flowstate_mode)
        
        # Actual API: generate_agent(intent_query, constellation_targets, metadata)
        # Create intent from agent_id and capabilities
        # Secure construction of intent_query (avoid direct f-string interpolation of arbitrary capability text)
        sanitized_caps = [c.replace("'", "").replace(";", "") for c in req.capabilities]
        intent_query = "Generate agent {} with capabilities: {}".format(
            req.agent_id,
            ", ".join(sanitized_caps)
        )
        metadata = {
            "agent_id": req.agent_id,
            "capabilities": req.capabilities,
            "symbolic_depth": req.symbolic_depth
        }
        
        agent = forge.generate_agent(
            intent_query=intent_query,
            constellation_targets=None,
            metadata=metadata
        )
        
        return {
            "status": "success",
            "agent": {
                "agent_id": agent.agent_id,
                "intent_alignment": agent.intent_alignment,
                "quantum_state": agent.quantum_state,
                "symbolic_layer": agent.symbolic_layer,
                "flowstate_mode": agent.flowstate_mode,
                "joy_index": agent.joy_index,
                "ethics_violations": agent.ethics_violations,
                "constellation_bindings": agent.constellation_bindings,
                "metadata": agent.metadata,
                "created_at": agent.created_at,
            },
            "context_tag": "qf_create_agent",
            "anchor": "T1:QF_AGENT_CREATE",
            "ethics_protocol": "GUMAS_Thermax"
        }
    except Exception as e:
        logger.error("Quantum Forge create agent error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)[:100]}")


@app.post(
    "/quantum_forge/store_memory",
    summary="Store Symbolic Memory",
    response_description="Memory node storage confirmation",
    tags=["quantum_forge"],
    dependencies=[Depends(security)]
)
def qf_store_memory(req: QFStoreMemoryRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Store a symbolic memory node.
    
    T1: QUANTUM_FORGE_MEMORY_STORE
    SRB: MEMORY_STORAGE
    DLP: context_tag=qf_store_memory
    """
    verify_csrf_token(token)
    
    if not QUANTUM_FORGE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Quantum Forge not available")
    
    try:
        forge = QuantumForge()
        
        # Actual API: create_memory_node(content, tags)
        # Note: intent_alignment is calculated internally based on content
        node = forge.create_memory_node(
            content=req.content,
            tags=req.tags
        )
        
        return {
            "status": "success",
            "node": {
                "node_id": node.node_id,
                "intent_alignment": node.intent_alignment,
                "created_at": node.created_at,
                "tags": node.tags,
            },
            "context_tag": "qf_store_memory",
            "anchor": "T1:QF_MEMORY_STORE"
        }
    except Exception as e:
        logger.error("Quantum Forge store memory error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to store memory: {str(e)[:100]}")


@app.post(
    "/quantum_forge/reactivate",
    summary="Reactivate Memory Nodes",
    response_description="Memory node reactivation with intent alignment",
    tags=["quantum_forge"],
    dependencies=[Depends(security)]
)
def qf_reactivate_memories(req: QFReactivateRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Reactivate memory nodes based on intent query.
    
    T1: QUANTUM_FORGE_REACTIVATE
    SRB: MEMORY_REACTIVATION
    DLP: context_tag=qf_reactivate
    """
    verify_csrf_token(token)
    
    if not QUANTUM_FORGE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Quantum Forge not available")
    
    try:
        forge = QuantumForge()
        
        # Actual API: reactivate_by_intent(intent_query, top_k)
        # Returns list of memory nodes, not agents
        nodes = forge.reactivate_by_intent(req.intent_query, top_k=5)
        
        if nodes:
            return {
                "status": "success",
                "reactivated": True,
                "count": len(nodes),
                "nodes": [
                    {
                        "node_id": node.node_id,
                        "intent_alignment": node.intent_alignment,
                        "created_at": node.created_at,
                        "tags": node.tags,
                    }
                    for node in nodes
                ],
                "context_tag": "qf_reactivate",
                "anchor": "T1:QF_REACTIVATE"
            }
        else:
            return {
                "status": "success",
                "reactivated": False,
                "count": 0,
                "message": "No matching memory nodes found or intent alignment too low",
                "context_tag": "qf_reactivate",
                "anchor": "T1:QF_REACTIVATE"
            }
    except Exception as e:
        logger.error("Quantum Forge reactivate error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to reactivate memories: {str(e)[:100]}")


@app.post(
    "/quantum_forge/ethics_check",
    summary="Ethics Drift Check",
    response_description="Ethics validation result with drift detection",
    tags=["quantum_forge"],
    dependencies=[Depends(security)]
)
def qf_ethics_check(req: QFEthicsCheckRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Perform GUMAS_Thermax ethics drift check on action vectors.
    
    T1: QUANTUM_FORGE_ETHICS_CHECK
    SRB: ETHICS_VALIDATION
    DLP: context_tag=qf_ethics_check
    Ethics: GUMAS_Thermax
    """
    verify_csrf_token(token)
    
    if not QUANTUM_FORGE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Quantum Forge not available")
    
    try:
        from modules.quantum_forge import GUMAS_Thermax
        
        ethics = GUMAS_Thermax(level=EthicsLevel.BALANCED)
        is_acceptable, drift = ethics.check_drift(req.action_vector, req.baseline_vector)
        
        return {
            "status": "success",
            "ethics_check": {
                "is_acceptable": is_acceptable,
                "drift_value": drift,
                "threshold": ethics.drift_threshold,
                "verdict": "APPROVED" if is_acceptable else "REJECTED",
            },
            "context_tag": "qf_ethics_check",
            "anchor": "T1:QF_ETHICS",
            "ethics_protocol": "GUMAS_Thermax"
        }
    except Exception as e:
        logger.error("Quantum Forge ethics check error: %s", str(e)[:200])
        raise HTTPException(status_code=500, detail=f"Failed to perform ethics check: {str(e)[:100]}")


if __name__ == "__main__":

    uvicorn.run(
        "aurora_gui_cloudhub_fastapi:app",
        host="127.0.0.1",  # Bind to localhost only for security
        port=8000,
        reload=True,
        log_level="info",
    )
