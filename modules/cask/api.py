"""CASK read-only REST API (issue #780).

Exposes the CASK design-surface data as JSON endpoints so the analysis
corpus is discoverable at runtime alongside other Aurora modules.
"""

import logging

from fastapi import APIRouter, HTTPException

from modules.cask.analysis import (
    generate_technical_specifications,
    generate_vs_sota_comparison,
    generate_risk_assessment,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cask", tags=["CASK"])

# Static topology metadata derived from charts.py component layout.
# Returns structured JSON; the rendered Plotly figure is available via
# the CLI tool (scripts/cask_tool.py).
_TOPOLOGY = {
    "layers": [
        {"id": "knowledge", "label": "Knowledge", "y": 5},
        {"id": "processing", "label": "Processing", "y": 2.8},
        {"id": "validation_runtime", "label": "Validation & Runtime", "y": 0.8},
    ],
    "components": [
        {"name": "Global Cross-Linguistic Database", "layer": "knowledge", "status": "design"},
        {"name": "Ethics & Value Systems Index", "layer": "knowledge", "status": "design"},
        {"name": "Cultural Cognition Framework", "layer": "knowledge", "status": "runtime"},
        {"name": "Historical Institutional Systems", "layer": "knowledge", "status": "design"},
        {"name": "Language-to-Symbolic Fusion Layer", "layer": "knowledge", "status": "design"},
        {"name": "Symbolic Vector Chain Compressor (SVCC)", "layer": "processing", "status": "design"},
        {"name": "GPT Native Encoding Layer", "layer": "processing", "status": "design"},
        {"name": "Agent Simulation Generation Module", "layer": "processing", "status": "design"},
        {"name": "Recursive Ethics Validator", "layer": "validation_runtime", "status": "runtime"},
        {"name": "ORION Simulation Runtime", "layer": "validation_runtime", "status": "design"},
    ],
    "total_components": 10,
    "runtime_components": 2,
    "design_components": 8,
}


@router.get("/specs/technical", summary="CASK technical specifications per component")
async def get_technical_specs():
    """Return the technical specification for each of the ten CASK components."""
    try:
        df = generate_technical_specifications()
        records = list(df.to_dict("records"))
        return {"data": records, "total": len(records), "source": "technical_specifications"}
    except ImportError as exc:
        logger.warning("CASK: pandas unavailable for specs/technical")
        raise HTTPException(status_code=503, detail="pandas is required for CASK analysis") from exc
    except Exception as exc:
        logger.exception("CASK get_technical_specs error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/specs/vs-sota", summary="CASK comparison against state of the art")
async def get_vs_sota():
    """Return CASK's innovation advantages vs the current state of the art per domain."""
    try:
        df = generate_vs_sota_comparison()
        records = list(df.to_dict("records"))
        return {"data": records, "total": len(records), "source": "vs_sota_comparison"}
    except ImportError as exc:
        logger.warning("CASK: pandas unavailable for specs/vs-sota")
        raise HTTPException(status_code=503, detail="pandas is required for CASK analysis") from exc
    except Exception as exc:
        logger.exception("CASK get_vs_sota error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/specs/risk", summary="CASK project risk assessment")
async def get_risk():
    """Return the risk assessment matrix: category, probability, impact, and mitigation."""
    try:
        df = generate_risk_assessment()
        records = list(df.to_dict("records"))
        return {"data": records, "total": len(records), "source": "risk_assessment"}
    except ImportError as exc:
        logger.warning("CASK: pandas unavailable for specs/risk")
        raise HTTPException(status_code=503, detail="pandas is required for CASK analysis") from exc
    except Exception as exc:
        logger.exception("CASK get_risk error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/topology", summary="CASK component topology metadata")
async def get_topology():
    """Return the layered component topology as structured JSON.

    Components are arranged in three layers with vertical y-positions: knowledge
    (y=5), processing (y=2.8), and validation/runtime (y=0.8).  ``status`` is
    ``'runtime'`` for components with a concrete implementation in this release,
    ``'design'`` otherwise.
    """
    return _TOPOLOGY
