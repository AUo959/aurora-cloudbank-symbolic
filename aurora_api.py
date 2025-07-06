"""
main FastAPI app for Aurora CloudBank Symbolic
Exposes endpoints for quantum and geometric algebra modules.
Enhanced with Claude Sonnet 4 capabilities.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.sonnet4_integration_hub import (
    enable_sonnet4_globally,
    sonnet4_hub,
)

# from modules.symbolic_core.quantum_vsa import QuantumVSA  # Uncomment if available

app = FastAPI(title="Aurora CloudBank Symbolic API - Sonnet 4 Enhanced")

ga = GeometricAlgebra()


def parse_multivector(expression: str, blades: dict):
    """Safely parse a multivector expression."""
    allowed_symbols = set(blades.keys())
    tokens = expression.split()
    for token in tokens:
        if token not in allowed_symbols and not token.isnumeric():
            raise ValueError(f"Invalid token in expression: {token}")
    # Construct the multivector using the blades dictionary
    result = None
    for token in tokens:
        if token in blades:
            result = blades[token] if result is None else result + blades[token]
        elif token.isnumeric():
            result = float(token) if result is None else result + float(token)
    return result


class VectorRequest(BaseModel):
    x: float
    y: float
    z: float


class MultivectorRequest(BaseModel):
    a: str
    b: str


class Sonnet4EnableRequest(BaseModel):
    client_id: str = None
    enable_all: bool = True


@app.post("/geometric/vector")
def create_vector(req: VectorRequest):
    v = ga.blades["e1"] * req.x + ga.blades["e2"] * req.y + ga.blades["e3"] * req.z
    return {"vector": str(v)}


@app.post("/geometric/mult")
def geometric_product(req: MultivectorRequest):
    try:
        a = parse_multivector(req.a, ga.blades)
        b = parse_multivector(req.b, ga.blades)
        result = ga.mult(a, b)
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sonnet4/enable")
async def enable_sonnet4(req: Sonnet4EnableRequest = None):
    """Enable Claude Sonnet 4 for all clients or specific client"""
    try:
        if req and req.enable_all:
            results = await enable_sonnet4_globally()
            return {
                "status": "success",
                "message": "Claude Sonnet 4 enabled for all clients",
                "results": results,
                "global_status": sonnet4_hub.get_global_status(),
            }
        elif req and req.client_id:
            result = await sonnet4_hub._enable_sonnet4_for_client(req.client_id)
            return {
                "status": "success" if result else "error",
                "client_id": req.client_id,
                "enabled": result,
                "client_status": sonnet4_hub.get_client_status(req.client_id),
            }
        else:
            # Default: enable for all clients
            results = await enable_sonnet4_globally()
            return {
                "status": "success",
                "message": "Claude Sonnet 4 enabled for all clients (default action)",
                "results": results,
                "global_status": sonnet4_hub.get_global_status(),
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to enable Sonnet 4: {str(e)}"
        )


@app.get("/sonnet4/status")
def get_sonnet4_status():
    """Get Claude Sonnet 4 status"""
    return {
        "global_status": sonnet4_hub.get_global_status(),
        "configuration": {
            "enabled": sonnet4_hub.sonnet4_config.enabled,
            "enable_for_all_clients": sonnet4_hub.sonnet4_config.enable_for_all_clients,
            "model": sonnet4_hub.sonnet4_config.model,
            "preserve_4o_logic": sonnet4_hub.sonnet4_config.preserve_4o_logic,
            "fallback_model": sonnet4_hub.sonnet4_config.fallback_model,
        },
    }


@app.get("/sonnet4/clients/{client_id}")
def get_client_sonnet4_status(client_id: str):
    """Get Claude Sonnet 4 status for specific client"""
    return sonnet4_hub.get_client_status(client_id)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Aurora CloudBank Symbolic API",
        "sonnet4_enabled": sonnet4_hub.sonnet4_config.enabled,
        "timestamp": "2025-06-29",
    }


# Example quantum endpoint (stub)
# @app.post("/quantum/vsa")
# def quantum_vsa_endpoint(...):
#     ...
