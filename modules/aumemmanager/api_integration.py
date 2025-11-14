"""
AuMemManager API Integration for Aurora CloudBank
FastAPI endpoints for hierarchical memory management with quantum-symbolic capabilities
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time

from modules.aumemmanager import (
    HierarchicalMemoryManager,
    MemoryType
)

# Global memory manager instance (in production, this would be properly managed)
memory_manager = HierarchicalMemoryManager(max_active_memories=1000)

# Create router for AuMemManager endpoints
router = APIRouter(prefix="/memory", tags=["AuMemManager"])

# Pydantic models for API requests/responses


class MemoryCreateRequest(BaseModel):
    content: Any = Field(..., description="Memory content (any JSON-serializable data)")
    memory_type: str = Field(..., description="Type of memory (agent, faction, narrative, etc.)")
    owner: str = Field(..., description="Owner of the memory")
    importance: float = Field(1.0, ge=0.0, le=10.0, description="Importance score (0-10)")
    tags: Optional[List[str]] = Field(default=[], description="Tags for categorization")
    quantum_properties: Optional[Dict[str, Any]] = Field(default=None, description="Quantum vector properties")
    aurora_anchors: Optional[List[str]] = Field(default=None, description="Aurora CloudBank symbolic anchors")
    cultural_score: float = Field(0.0, ge=0.0, le=1.0, description="CASK cultural relevance score")

class MemoryRetrievalRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query (1-500 characters, HIGH-5 validated)"
    )
    owner: Optional[str] = Field(
        default=None,
        pattern=r'^[a-zA-Z0-9_-]+$',
        max_length=64,
        description="Filter by owner (alphanumeric, HIGH-5 validated)"
    )
    memory_type: Optional[str] = Field(default=None, description="Filter by memory type")
    top_k: int = Field(
        5,
        ge=1,
        le=100,
        description="Number of results to return (1-100, HIGH-5 range expanded)"
    )
    include_quantum: bool = Field(True, description="Include quantum vector data")
    cultural_filter: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum cultural score filter (0.0-1.0, HIGH-5 validated)"
    )

class QuantumVectorRequest(BaseModel):
    vector_id: str = Field(..., description="Quantum vector identifier")
    magnitude: float = Field(..., description="Vector magnitude")
    phase: float = Field(..., description="Vector phase")
    aurora_anchors: Optional[List[str]] = Field(default=None, description="Aurora symbolic anchors")
    dlp_classification: str = Field("DLP_L1_OK", description="DLP security classification")

class TrajectoryRequest(BaseModel):
    vector_id: str = Field(..., description="Quantum vector identifier")
    target_magnitude: float = Field(..., description="Target magnitude")
    target_phase: float = Field(..., description="Target phase")
    trajectory_type: str = Field("quantum_optimal", description="Trajectory computation type")

class MemoryResponse(BaseModel):
    id: str
    content: Any
    memory_type: str
    owner: str
    importance: float
    strength: float
    access_count: int
    status: str
    symbolic_anchors: List[str]
    cask_cultural_score: float
    quantum_vector: Optional[Dict[str, Any]]

class SystemMetricsResponse(BaseModel):
    total_memories: int
    active_memories: int
    compressed_memories: int
    archived_memories: int
    quantum_vectors: int
    entangled_pairs: int
    aurora_anchor_coverage: int
    average_cultural_score: float
    quantum_network_density: float

@router.post("/create", response_model=Dict[str, str])


async def create_memory(request: MemoryCreateRequest):
    """Create a new memory item with quantum-symbolic capabilities"""
    try:
        # Convert string memory type to enum
        try:
            memory_type = MemoryType(request.memory_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid memory type: {request.memory_type}")

        memory_id = memory_manager.add_memory(
            content=request.content,
            memory_type=memory_type,
            owner=request.owner,
            importance=request.importance,
            tags=request.tags,
            quantum_properties=request.quantum_properties,
            aurora_anchors=request.aurora_anchors,
            cultural_score=request.cultural_score
        )

        return {
            "memory_id": memory_id,
            "status": "created",
            "message": f"Memory created successfully with ID: {memory_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {str(e)}")

@router.post("/retrieve", response_model=List[MemoryResponse])


async def retrieve_memories(request: MemoryRetrievalRequest):
    """Retrieve memories using attention-based scoring"""
    try:
        # Convert string memory type to enum if provided
        memory_type = None
        if request.memory_type:
            try:
                memory_type = MemoryType(request.memory_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid memory type: {request.memory_type}")

        memories = memory_manager.retrieve_memories(
            query=request.query,
            owner=request.owner,
            memory_type=memory_type,
            top_k=request.top_k,
            include_quantum=request.include_quantum,
            cultural_filter=request.cultural_filter
        )

        # Convert to response format
        response_memories = []
        for memory in memories:
            quantum_data = None
            if memory.quantum_vector and request.include_quantum:
                quantum_data = {
                    "vector_id": memory.quantum_vector.vector_id,
                    "magnitude": memory.quantum_vector.magnitude,
                    "phase": memory.quantum_vector.phase,
                    "coherence_time": memory.quantum_vector.coherence_time,
                    "entanglement_links": memory.quantum_vector.entanglement_links,
                    "symbolic_anchors": memory.quantum_vector.symbolic_anchors
                }

            response_memories.append(MemoryResponse(
                id=memory.id,
                content=memory.content,
                memory_type=memory.memory_type.value,
                owner=memory.owner,
                importance=memory.importance,
                strength=memory.strength,
                access_count=memory.access_count,
                status=memory.status.value,
                symbolic_anchors=memory.symbolic_anchors,
                cask_cultural_score=memory.cask_cultural_score,
                quantum_vector=quantum_data
            ))

        return response_memories

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memories: {str(e)}")

@router.post("/quantum/create_vector", response_model=Dict[str, Any])


async def create_quantum_vector(request: QuantumVectorRequest):
    """Create a quantum-symbolic vector for memory management"""
    try:
        qv = memory_manager.flight_controller.create_quantum_vector(
            vector_id=request.vector_id,
            magnitude=request.magnitude,
            phase=request.phase,
            aurora_anchors=request.aurora_anchors,
            dlp_classification=request.dlp_classification
        )

        return {
            "vector_id": qv.vector_id,
            "magnitude": qv.magnitude,
            "phase": qv.phase,
            "coherence_time": qv.coherence_time,
            "symbolic_anchors": qv.symbolic_anchors,
            "status": "created"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create quantum vector: {str(e)}")

@router.post("/quantum/entangle", response_model=Dict[str, str])


async def entangle_vectors(vector1_id: str, vector2_id: str):
    """Create quantum entanglement between two vectors"""
    try:
        success = memory_manager.flight_controller.entangle_vectors(vector1_id, vector2_id)

        if success:
            return {
                "status": "entangled",
                "vector1_id": vector1_id,
                "vector2_id": vector2_id,
                "message": f"Successfully entangled vectors {vector1_id} and {vector2_id}"
            }
        else:
            raise HTTPException(status_code=404, detail="One or both vectors not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to entangle vectors: {str(e)}")

@router.post("/quantum/trajectory", response_model=Dict[str, Any])


async def compute_trajectory(request: TrajectoryRequest):
    """Compute quantum vector trajectory using flight control"""
    try:
        target_state = {
            "magnitude": request.target_magnitude,
            "phase": request.target_phase
        }

        trajectory = memory_manager.flight_controller.compute_trajectory(
            vector_id=request.vector_id,
            target_state=target_state,
            trajectory_type=request.trajectory_type
        )

        return {
            "vector_id": request.vector_id,
            "trajectory_type": request.trajectory_type,
            "waypoints": len(trajectory),
            "trajectory": trajectory,
            "status": "computed"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute trajectory: {str(e)}")

@router.get("/metrics", response_model=SystemMetricsResponse)


async def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        metrics = memory_manager.get_metrics()

        return SystemMetricsResponse(
            total_memories=metrics.get('total_memories', 0),
            active_memories=metrics.get('active_memories', 0),
            compressed_memories=metrics.get('compressed_memories', 0),
            archived_memories=metrics.get('archived_memories', 0),
            quantum_vectors=metrics.get('quantum_vectors', 0),
            entangled_pairs=metrics.get('entangled_pairs', 0),
            aurora_anchor_coverage=metrics.get('aurora_anchor_coverage', 0),
            average_cultural_score=metrics.get('average_cultural_score', 0.0),
            quantum_network_density=metrics.get('quantum_network_density', 0.0)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.post("/lifecycle/batch_process", response_model=Dict[str, Any])


async def batch_process_lifecycle():
    """Process memory lifecycle operations (decay, compression, cleanup)"""
    try:
        results = memory_manager.batch_process_lifecycle()

        return {
            "status": "completed",
            "timestamp": time.time(),
            "results": results,
            "message": "Batch lifecycle processing completed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process lifecycle: {str(e)}")

@router.post("/compress", response_model=Dict[str, Any])


async def compress_memories(
    compression_ratio: float = Query(0.5, ge=0.1, le=0.9, description="Compression ratio"),
    importance_threshold: float = Query(5.0, ge=0.0, le=10.0, description="Importance threshold")
):
    """Manually trigger memory compression"""
    try:
        results = memory_manager.compress_memories(
            compression_ratio=compression_ratio,
            importance_threshold=importance_threshold
        )

        return {
            "status": "completed",
            "compression_ratio": compression_ratio,
            "importance_threshold": importance_threshold,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compress memories: {str(e)}")

@router.get("/export", response_model=Dict[str, Any])


async def export_system_state():
    """Export complete system state"""
    try:
        state = memory_manager.export_state()
        return {
            "status": "exported",
            "export_timestamp": state["export_timestamp"],
            "system_state": state
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export state: {str(e)}")

@router.get("/quantum/network_analysis", response_model=Dict[str, Any])


async def get_quantum_network_analysis():
    """Get detailed quantum entanglement network analysis"""
    try:
        analysis = memory_manager.flight_controller.get_entanglement_network_analysis()
        return {
            "status": "analyzed",
            "timestamp": time.time(),
            "network_analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze quantum network: {str(e)}")

# Health check endpoint
@router.get("/health")


async def health_check():
    """Health check for AuMemManager system"""
    try:
        metrics = memory_manager.get_metrics()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "active_memories": metrics.get('active_memories', 0),
            "quantum_vectors": metrics.get('quantum_vectors', 0),
            "system_uptime": time.time() - metrics.get('last_cleanup', time.time())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
