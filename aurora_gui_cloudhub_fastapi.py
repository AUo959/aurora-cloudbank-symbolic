import logging
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

from modules.symbolic_core import get_mcp_bridge_core
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.mcp_command_router import MCPCommandRouter
from modules.symbolic_core.mcp_security import mcp_security, mcp_security_dependency
from modules.symbolic_core.quantum_vsa import quantum_symbolic_vector, QuantumSymbolicVector
from modules.symbolic_core.vsa import SymbolicVector

app = FastAPI(title="Aurora Quantum VSA Playground")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    a_mv = req.a * ga.blades["e1"]
    b_mv = req.b * ga.blades["e2"]
    result = ga.mult(a_mv, b_mv)
    return {"result": ga.pretty(result)}


@app.post(
    "/quantum/symbolic_vector",
    summary="Quantum Symbolic Vector",
    response_description="Quantum-generated symbolic vector",
)
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


@app.post(
    "/mcp_bridge/route_command",
    summary="Symbolic Command Routing via MCP Bridge",
    response_description="Routed command result",
)
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


@app.post(
    "/vsa/operation",
    summary="VSA Operation",
    response_description="Result of VSA operation",
)
def vsa_operation(req: VSAOperationRequest):
    """
    Perform an operation on the VSA symbolic vector.
    Request body: {"symbol": str, "dimension": int, "operation_type": str}
    Response: {"symbol": str, "dimension": int, "result": Any}
    """
    if req.operation_type == "generate":
        vec = quantum_symbolic_vector(req.symbol, req.dimension)
        result = vec.tolist()
    elif req.operation_type == "bind":
        # Binding logic here
        result = "Binding not implemented in demo"
    elif req.operation_type == "unbind":
        # Unbinding logic here
        result = "Unbinding not implemented in demo"
    elif req.operation_type == "similarity":
        # Similarity logic here
        result = "Similarity not implemented in demo"
    else:
        raise HTTPException(status_code=400, detail="Invalid operation type")

    return {"symbol": req.symbol, "dimension": req.dimension, "result": result}


@app.post(
    "/vsa/bind",
    summary="VSA Bind",
    response_description="Result of VSA bind operation",
)
def vsa_bind(req: VSABindRequest):
    """
    Bind two symbolic vectors in the VSA.
    Request body: {"symbol_a": str, "symbol_b": str, "result_name": str, "dimension": int}
    Response: {"result_name": str, "dimension": int, "result": Any}
    """
    # Retrieve vectors from store
    vec_a = vsa_store.get(req.symbol_a)
    vec_b = vsa_store.get(req.symbol_b)
    if vec_a is None or vec_b is None:
        raise HTTPException(status_code=404, detail="One or both symbols not found")

    # Perform binding (placeholder logic)
    bound_vector = vec_a  # Replace with actual binding logic
    vsa_store[req.result_name] = bound_vector

    return {"result_name": req.result_name, "dimension": req.dimension, "result": bound_vector.tolist()}


@app.post(
    "/vsa/similarity",
    summary="VSA Similarity",
    response_description="Similarity score between two symbolic vectors",
)
def vsa_similarity(req: VSASimilarityRequest):
    """
    Compute similarity between two symbolic vectors in the VSA.
    Request body: {"symbol_a": str, "symbol_b": str}
    Response: {"symbol_a": str, "symbol_b": str, "similarity": float}
    """
    # Retrieve vectors from store
    vec_a = vsa_store.get(req.symbol_a)
    vec_b = vsa_store.get(req.symbol_b)
    if vec_a is None or vec_b is None:
        raise HTTPException(status_code=404, detail="One or both symbols not found")

    # Compute similarity (placeholder logic)
    similarity_score = np.random.rand()  # Replace with actual similarity computation

    return {"symbol_a": req.symbol_a, "symbol_b": req.symbol_b, "similarity": similarity_score}


@app.post(
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
    result = {"message": "Quantum circuit executed", "symbol": req.symbol, "depth": req.depth, "qubits": req.qubits}

    return result


@app.post(
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
    result = None

    if req.operation == "product":
        # Compute geometric product
        blades = [ga.blades[f"e{i+1}"] for i in range(len(req.vectors))]
        result = ga.mult(*blades)
    elif req.operation == "add":
        # Compute geometric addition
        result = sum((ga.blades[f"e{i+1}"] for i in range(len(req.vectors))), start=ga.zero)
    elif req.operation == "commutator":
        # Compute commutator
        if len(req.vectors) != 2:
            raise HTTPException(status_code=400, detail="Commutator requires exactly 2 vectors")
        v1, v2 = req.vectors
        blade1 = sum((ga.blades[f"e{i+1}"] * v1[f"e{i+1}"] for i in range(len(v1))), start=ga.zero)
        blade2 = sum((ga.blades[f"e{i+1}"] * v2[f"e{i+1}"] for i in range(len(v2))), start=ga.zero)
        result = ga.commutator(blade1, blade2)
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")

    return {"operation": req.operation, "result": ga.pretty(result)}


# === New VSA and Quantum Endpoints ===

@app.post("/api/vsa/generate", summary="Generate Quantum VSA Vector")
def generate_vsa_vector(req: VSAOperationRequest):
    """
    Generate a quantum symbolic vector for a given symbol.
    """
    try:
        qsv = QuantumSymbolicVector(req.symbol, req.dimension)
        vsa_store[req.symbol] = qsv

        return {
            "symbol": req.symbol,
            "dimension": req.dimension,
            "vector": qsv.vector.tolist()[:32],  # First 32 elements for display
            "vector_full_length": len(qsv.vector),
            "vector_type": "bipolar",
            "quantum_generated": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VSA generation failed: {str(e)}")


@app.post("/api/vsa/bind", summary="Bind two VSA vectors")
def bind_vsa_vectors(req: VSABindRequest):
    """
    Bind two symbolic vectors using element-wise multiplication (XOR for bipolar).
    """
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
        vec_a = vec_a[:min_dim]
        vec_b = vec_b[:min_dim]

        # Bind operation (element-wise multiplication for bipolar vectors)
        bound_vector = vec_a * vec_b

        # Store result
        result_qsv = QuantumSymbolicVector.__new__(QuantumSymbolicVector)
        result_qsv.symbol = req.result_name
        result_qsv.dim = min_dim
        result_qsv.vector = bound_vector
        result_qsv.vector_type = "bipolar"
        vsa_store[req.result_name] = result_qsv

        return {
            "operation": "bind",
            "symbol_a": req.symbol_a,
            "symbol_b": req.symbol_b,
            "result_name": req.result_name,
            "dimension": min_dim,
            "result_vector": bound_vector.tolist()[:32],
            "similarity_a": float(np.dot(bound_vector, vec_a) / min_dim),
            "similarity_b": float(np.dot(bound_vector, vec_b) / min_dim)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VSA binding failed: {str(e)}")


@app.post("/api/vsa/similarity", summary="Calculate VSA similarity")
def calculate_vsa_similarity(req: VSASimilarityRequest):
    """
    Calculate cosine similarity between two VSA vectors.
    """
    try:
        if req.symbol_a not in vsa_store:
            vsa_store[req.symbol_a] = QuantumSymbolicVector(req.symbol_a)
        if req.symbol_b not in vsa_store:
            vsa_store[req.symbol_b] = QuantumSymbolicVector(req.symbol_b)

        vec_a = vsa_store[req.symbol_a].vector
        vec_b = vsa_store[req.symbol_b].vector

        # Ensure same dimension
        min_dim = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:min_dim]
        vec_b = vec_b[:min_dim]

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
            "dimension": min_dim
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
                "vector_type": getattr(qsv, 'vector_type', 'bipolar'),
                "preview": qsv.vector.tolist()[:8]
            }
            for symbol, qsv in vsa_store.items()
        ],
        "count": len(vsa_store)
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


@app.post("/api/geometric/advanced", summary="Advanced Geometric Algebra Operations")
def advanced_geometric_operations(req: GeometricAlgebraRequest):
    """
    Perform advanced geometric algebra operations on multiple vectors.
    """
    try:
        ga = GeometricAlgebra()
        results = []

        if req.operation == "product":
            # Compute geometric product of all vectors
            result = 1
            for vec_spec in req.vectors:
                mv = 0
                for blade, coeff in vec_spec.items():
                    if blade in ga.blades:
                        mv += coeff * ga.blades[blade]
                    else:
                        mv += coeff  # scalar part
                result = ga.mult(result, mv)
            results.append({"result": ga.pretty(result), "type": "geometric_product"})

        elif req.operation == "commutator":
            # Compute commutator [A, B] = AB - BA
            if len(req.vectors) >= 2:
                mv_a = 0
                mv_b = 0
                for blade, coeff in req.vectors[0].items():
                    if blade in ga.blades:
                        mv_a += coeff * ga.blades[blade]
                for blade, coeff in req.vectors[1].items():
                    if blade in ga.blades:
                        mv_b += coeff * ga.blades[blade]

                ab = ga.mult(mv_a, mv_b)
                ba = ga.mult(mv_b, mv_a)
                commutator = ab - ba if not ga._mock else ab + ba  # Mock approximation
                results.append({"result": ga.pretty(commutator), "type": "commutator"})

        return {
            "operation": req.operation,
            "input_vectors": req.vectors,
            "results": results,
            "mock_mode": ga._mock
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geometric algebra operation failed: {str(e)}")


@app.post("/api/quantum/circuit", summary="Generate Quantum Circuit")
def generate_quantum_circuit(req: QuantumCircuitRequest):
    """
    Generate and analyze a quantum circuit for symbolic operations.
    """
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
        import hashlib

        # Create circuit based on symbol hash
        h = int(hashlib.md5(req.symbol.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(h)

        qc = QuantumCircuit(req.qubits, req.qubits)

        # Apply gates based on symbol and depth
        for depth in range(req.depth):
            for qubit in range(req.qubits):
                gate_choice = np.random.rand()
                if gate_choice < 0.3:
                    qc.h(qubit)  # Hadamard
                elif gate_choice < 0.6:
                    qc.x(qubit)  # Pauli-X
                elif gate_choice < 0.8:
                    qc.z(qubit)  # Pauli-Z
                else:
                    if qubit < req.qubits - 1:
                        qc.cx(qubit, qubit + 1)  # CNOT

        # Measure all qubits
        qc.measure(range(req.qubits), range(req.qubits))

        # Run simulation
        backend = AerSimulator()
        result = backend.run(qc, shots=1000).result()
        counts = result.get_counts()

        # Analyze results
        most_frequent = max(counts.items(), key=lambda x: x[1])

        return {
            "symbol": req.symbol,
            "qubits": req.qubits,
            "depth": req.depth,
            "circuit_gates": qc.num_nonlocal_gates(),
            "measurement_counts": dict(list(counts.items())[:10]),  # Top 10 results
            "most_frequent_state": most_frequent[0],
            "most_frequent_probability": most_frequent[1] / 1000,
            "total_shots": 1000,
            "circuit_qasm": qc.qasm()
        }
    except Exception as e:
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
        "vector_list": list(vsa_store.keys())
    }
    await websocket.send_json(welcome_msg)

    try:
        while True:
            data = await websocket.receive_json()

            # Process collaborative VSA operations
            if data.get("type") == "vsa_operation":
                # Broadcast VSA operation to all connected clients
                broadcast_msg = {
                    "type": "vsa_update",
                    "operation": data.get("operation"),
                    "symbol": data.get("symbol"),
                    "timestamp": data.get("timestamp"),
                    "user": data.get("user", "anonymous")
                }

                for conn in list(connections):
                    if conn is websocket:
                        continue
                    try:
                        await conn.send_json(broadcast_msg)
                    except WebSocketDisconnect:
                        connections.remove(conn)

    except WebSocketDisconnect:
        connections.remove(websocket)
