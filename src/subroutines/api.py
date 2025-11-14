"""
Subroutine API Router
=====================
Anchor: SUBROUTINE-API-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

FastAPI router for subroutine management and execution.
Provides endpoints for registering, querying, and monitoring subroutines.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import time

from src.subroutines.registry import (
    get_subroutine_registry,
    Subroutine,
    SubroutineAuthor,
    SubroutineStatus,
    SubroutineCategory,
    SubroutineDependency
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subroutines", tags=["subroutines"])


# Pydantic Models for API
class SubroutineAuthorCreate(BaseModel):
    """Author information for subroutine creation"""
    name: str = Field(..., description="Author name")
    team: str = Field(..., description="Team name")
    email: Optional[str] = Field(None, description="Author email")
    role: Optional[str] = Field(None, description="Author role")


class SubroutineDependencyCreate(BaseModel):
    """Dependency specification for subroutine"""
    subroutine_id: str = Field(..., description="Dependency subroutine ID")
    version_constraint: str = Field(..., description="Version constraint (e.g., '>=1.0.0')")
    required: bool = Field(True, description="Whether dependency is required")


class SubroutineCreate(BaseModel):
    """Create subroutine request"""
    id: str = Field(..., description="Unique subroutine ID")
    name: str = Field(..., description="Human-readable name")
    version: str = Field(..., description="Semantic version (e.g., '1.0.0')")
    description: str = Field(..., description="Subroutine description")
    author: SubroutineAuthorCreate
    category: str = Field(..., description="Category (validation, monitoring, etc.)")
    module_path: str = Field(..., description="Python module path")
    class_name: str = Field(..., description="Class name")
    entry_point: str = Field(..., description="Method name to call")
    dependencies: List[SubroutineDependencyCreate] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    documentation_url: Optional[str] = None
    examples: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dlp_anchor: Optional[str] = None


class SubroutineExecutionRequest(BaseModel):
    """Execute subroutine request"""
    subroutine_id: str = Field(..., description="Subroutine ID to execute")
    inputs: Dict[str, Any] = Field(..., description="Input parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional execution metadata")


class SubroutineStatusUpdate(BaseModel):
    """Update subroutine status"""
    status: str = Field(..., description="New status (draft, active, deprecated, archived)")


class SubroutineSearchRequest(BaseModel):
    """Search subroutines"""
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[str] = Field(None, description="Filter by status")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_subroutine(request: SubroutineCreate) -> Dict[str, Any]:
    """
    Register a new subroutine in the system.
    
    Returns:
        Registered subroutine details
    """
    try:
        registry = get_subroutine_registry()
        
        # Convert category string to enum
        try:
            category_enum = SubroutineCategory[request.category.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {request.category}"
            )
        
        # Create subroutine
        from datetime import datetime, UTC
        subroutine = Subroutine(
            id=request.id,
            name=request.name,
            version=request.version,
            description=request.description,
            author=SubroutineAuthor(
                name=request.author.name,
                team=request.author.team,
                email=request.author.email,
                role=request.author.role
            ),
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            status=SubroutineStatus.DRAFT,
            category=category_enum,
            module_path=request.module_path,
            class_name=request.class_name,
            entry_point=request.entry_point,
            dependencies=[
                SubroutineDependency(
                    subroutine_id=dep.subroutine_id,
                    version_constraint=dep.version_constraint,
                    required=dep.required
                )
                for dep in request.dependencies
            ],
            integrations=request.integrations,
            documentation_url=request.documentation_url,
            examples=request.examples,
            tags=request.tags,
            metadata=request.metadata,
            dlp_anchor=request.dlp_anchor
        )
        
        # Register
        if not registry.register(subroutine):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Subroutine '{request.id}' already registered"
            )
        
        return {
            "success": True,
            "message": f"Subroutine '{request.id}' registered successfully",
            "subroutine": subroutine.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to register subroutine: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/list")
async def list_subroutines(
    category: Optional[str] = None,
    status_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all registered subroutines with optional filters.
    
    Args:
        category: Filter by category
        status_filter: Filter by status
        
    Returns:
        List of subroutines
    """
    try:
        registry = get_subroutine_registry()
        
        # Apply filters
        if category:
            try:
                cat_enum = SubroutineCategory[category.upper()]
                subroutines = registry.list_by_category(cat_enum)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {category}"
                )
        elif status_filter:
            try:
                status_enum = SubroutineStatus[status_filter.upper()]
                subroutines = registry.list_by_status(status_enum)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status_filter}"
                )
        else:
            subroutines = registry.list_all()
        
        return {
            "success": True,
            "count": len(subroutines),
            "subroutines": [s.to_dict() for s in subroutines]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list subroutines: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List failed: {str(e)}"
        )


@router.get("/get/{subroutine_id}")
async def get_subroutine(subroutine_id: str) -> Dict[str, Any]:
    """
    Get details for a specific subroutine.
    
    Args:
        subroutine_id: Subroutine unique ID
        
    Returns:
        Subroutine details
    """
    try:
        registry = get_subroutine_registry()
        subroutine = registry.get(subroutine_id)
        
        if not subroutine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subroutine '{subroutine_id}' not found"
            )
        
        return {
            "success": True,
            "subroutine": subroutine.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get subroutine: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get failed: {str(e)}"
        )


@router.post("/search")
async def search_subroutines(request: SubroutineSearchRequest) -> Dict[str, Any]:
    """
    Search subroutines by query, category, status, or tags.
    
    Returns:
        List of matching subroutines
    """
    try:
        registry = get_subroutine_registry()
        
        # Convert string filters to enums
        category_enum = None
        if request.category:
            try:
                category_enum = SubroutineCategory[request.category.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {request.category}"
                )
        
        status_enum = None
        if request.status:
            try:
                status_enum = SubroutineStatus[request.status.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {request.status}"
                )
        
        # Search
        results = registry.search(
            query=request.query or "",
            category=category_enum,
            status=status_enum,
            tags=request.tags
        )
        
        return {
            "success": True,
            "count": len(results),
            "results": [s.to_dict() for s in results]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Search failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.put("/status/{subroutine_id}")
async def update_subroutine_status(
    subroutine_id: str,
    request: SubroutineStatusUpdate
) -> Dict[str, Any]:
    """
    Update subroutine status.
    
    Args:
        subroutine_id: Subroutine ID
        request: New status
        
    Returns:
        Updated subroutine
    """
    try:
        registry = get_subroutine_registry()
        
        # Convert status string to enum
        try:
            status_enum = SubroutineStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {request.status}"
            )
        
        # Update
        if not registry.update_status(subroutine_id, status_enum):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subroutine '{subroutine_id}' not found"
            )
        
        subroutine = registry.get(subroutine_id)
        return {
            "success": True,
            "message": f"Status updated to {request.status}",
            "subroutine": subroutine.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update status: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update failed: {str(e)}"
        )


@router.post("/execute")
async def execute_subroutine(request: SubroutineExecutionRequest) -> Dict[str, Any]:
    """
    Execute a subroutine with provided inputs.
    
    Args:
        request: Execution request with subroutine ID and inputs
        
    Returns:
        Execution result
    """
    try:
        registry = get_subroutine_registry()
        subroutine = registry.get(request.subroutine_id)
        
        if not subroutine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subroutine '{request.subroutine_id}' not found"
            )
        
        if subroutine.status != SubroutineStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subroutine '{request.subroutine_id}' is not active (status: {subroutine.status.value})"
            )
        
        # Dynamic import and execution
        start_time = time.time()
        success = False
        outputs = {}
        error = None
        
        try:
            # Import module
            import importlib
            module = importlib.import_module(subroutine.module_path)
            cls = getattr(module, subroutine.class_name)
            
            # Instantiate (assuming no-arg constructor or defaults)
            instance = cls()
            
            # Execute entry point
            method = getattr(instance, subroutine.entry_point)
            result = method(**request.inputs)
            
            # Handle different return types
            if hasattr(result, 'success'):
                success = result.success
                outputs = result.__dict__ if hasattr(result, '__dict__') else {'result': str(result)}
            else:
                success = True
                outputs = {'result': result}
        
        except Exception as e:
            error = str(e)
            logger.error("Subroutine execution failed: %s", error)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Record execution
        registry.record_execution(
            subroutine_id=request.subroutine_id,
            inputs=request.inputs,
            outputs=outputs,
            success=success,
            duration_ms=duration_ms,
            error=error,
            metadata=request.metadata
        )
        
        return {
            "success": success,
            "subroutine_id": request.subroutine_id,
            "duration_ms": duration_ms,
            "outputs": outputs,
            "error": error
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Execution failed: %s", str(e))
        # Don't expose internal error details to users
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Execution failed. Please check logs for details."
        )


@router.get("/stats")
async def get_registry_stats() -> Dict[str, Any]:
    """
    Get registry statistics.
    
    Returns:
        Registry statistics including counts by category and status
    """
    try:
        registry = get_subroutine_registry()
        stats = registry.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        logger.error("Failed to get stats: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats failed: {str(e)}"
        )


@router.get("/export")
async def export_registry() -> Dict[str, Any]:
    """
    Export full registry state.
    
    Returns:
        Complete registry export with all subroutines
    """
    try:
        registry = get_subroutine_registry()
        export_data = registry.export_registry()
        
        return {
            "success": True,
            "export": export_data
        }
    
    except Exception as e:
        logger.error("Export failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for subroutine system.
    
    Returns:
        Health status
    """
    try:
        registry = get_subroutine_registry()
        stats = registry.get_stats()
        
        return {
            "success": True,
            "status": "healthy",
            "active_subroutines": stats['active_subroutines'],
            "total_subroutines": stats['total_subroutines'],
            "total_executions": stats['total_executions']
        }
    
    except Exception as e:
        logger.error("Health check failed: %s", str(e))
        # Don't expose internal error details in health check responses
        return {
            "success": False,
            "status": "unhealthy",
            "error": "Health check failed. See logs for details."
        }
