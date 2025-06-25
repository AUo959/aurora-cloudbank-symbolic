"""
main FastAPI app for Aurora CloudBank Symbolic
Exposes endpoints for quantum and geometric algebra modules.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
# from modules.symbolic_core.quantum_vsa import QuantumVSA  # Uncomment if available

app = FastAPI(title="Aurora CloudBank Symbolic API")

ga = GeometricAlgebra()

class VectorRequest(BaseModel):
    x: float
    y: float
    z: float

class MultivectorRequest(BaseModel):
    a: str
    b: str

@app.post("/geometric/vector")
def create_vector(req: VectorRequest):
    v = ga.blades['e1'] * req.x + ga.blades['e2'] * req.y + ga.blades['e3'] * req.z
    return {"vector": str(v)}

@app.post("/geometric/mult")
def geometric_product(req: MultivectorRequest):
    try:
        a = eval(req.a, {**ga.blades})
        b = eval(req.b, {**ga.blades})
        result = ga.mult(a, b)
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Example quantum endpoint (stub)
# @app.post("/quantum/vsa")
# def quantum_vsa_endpoint(...):
#     ...
