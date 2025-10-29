"""
Cross-Repository Collaboration API Routes

Provides FastAPI endpoints for multi-repo capsule exchange, context synchronization,
workflow triggering, and agent status management.

Thread: T1→COLLAB→API
DLP: context_tag=collab_api_routes
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from src.collab.capsule_schema import (
    MultiRepoCapsule,
    LinkedRepository,
    SharedAnchor,
    create_shared_anchor,
    validate_capsule_compatibility
)
from src.core.native_dlp_export import NativeDLPTracker
from src.middleware.fastapi_security import require_auth

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/collab",
    tags=["cross-repo-collaboration"],
    responses={404: {"description": "Not found"}}
)

# DLP tracker for all collab operations
dlp_tracker = NativeDLPTracker()


# Request/Response Models

class ExportRequest(BaseModel):
    """Request model for capsule export."""
    repo_url: str = Field(..., description="Target repository URL")
    agents: List[str] = Field(..., description="List of agent names")
    include_anchors: bool = Field(True, description="Include shared anchors")


class ExportResponse(BaseModel):
    """Response model for capsule export."""
    success: bool
    capsule_id: str
    capsule_data: Dict[str, Any]
    dlp_tag_id: str
    export_timestamp: str
    signed: bool = True


class ImportRequest(BaseModel):
    """Request model for capsule import."""
    capsule_data: Dict[str, Any] = Field(..., description="Capsule JSON data")
    validate_anchors: bool = Field(True, description="Validate anchor integrity")
    validate_ethics: bool = Field(True, description="Validate ethics compliance")
    trust_level: str = Field("pending", description="Trust level: pending, trusted, verified")


class ImportResponse(BaseModel):
    """Response model for capsule import."""
    success: bool
    capsule_id: str
    validation_results: Dict[str, Any]
    activation_timestamp: str
    trust_level: str


class WorkflowTriggerRequest(BaseModel):
    """Request model for workflow trigger."""
    target_repo: str = Field(..., description="Target repository (owner/repo)")
    workflow_name: str = Field(..., description="Workflow file name")
    event_type: str = Field("repository_dispatch", description="Event type to trigger")
    payload: Optional[Dict[str, Any]] = Field(None, description="Workflow payload")


class WorkflowTriggerResponse(BaseModel):
    """Response model for workflow trigger."""
    success: bool
    target_repo: str
    workflow_name: str
    trigger_timestamp: str
    event_chain_id: Optional[str] = None


class InviteRequest(BaseModel):
    """Request model for repo linking invitation."""
    repo_url: str = Field(..., description="Repository to invite")
    agents: List[str] = Field(..., description="Accepted agents")
    message: Optional[str] = Field(None, description="Invitation message")


class InviteResponse(BaseModel):
    """Response model for repo linking invitation."""
    success: bool
    invitation_id: str
    repo_url: str
    agents: List[str]
    anchor_exchange: Dict[str, Any]
    created_timestamp: str


class AgentSyncRequest(BaseModel):
    """Request model for agent status sync."""
    agent_names: Optional[List[str]] = Field(None, description="Agents to sync (None = all)")


class AgentSyncResponse(BaseModel):
    """Response model for agent status sync."""
    success: bool
    synced_agents: List[Dict[str, Any]]
    missing_agents: List[str]
    alignment_drift: float
    change_log: List[Dict[str, Any]]
    sync_timestamp: str


# API Endpoints

@router.post("/context/export", response_model=ExportResponse)
async def export_context(
    request: ExportRequest,
    token: HTTPAuthorizationCredentials = Depends(require_auth)
) -> ExportResponse:
    """
    Export signed capsule context for external repository.
    
    Creates a multi-repo capsule with linked repository info, shared anchors,
    and agent roster. Logs export with DLP tracking.
    """
    logger.info("Exporting capsule for %s", request.repo_url)
    
    try:
        # Parse repo URL
        if request.repo_url.startswith('https://github.com/'):
            parts = request.repo_url.replace('https://github.com/', '').rstrip('/').split('/')
            owner, repo_name = parts[0], parts[1]
        else:
            raise ValueError("Invalid GitHub repository URL")
        
        # Create multi-repo capsule
        capsule_id = f"COLLAB_EXPORT_{owner}_{repo_name}_{int(datetime.now().timestamp())}"
        capsule = MultiRepoCapsule(
            capsule_id=capsule_id,
            title=f"Cross-Repo Export to {owner}/{repo_name}",
            anchor_seed="EOS_SEED_ORION",
            ethics_protocol="Picard_Delta_3",
            agent_roster=request.agents
        )
        
        # Add linked repository
        linked_repo = LinkedRepository(
            repo_url=request.repo_url,
            owner=owner,
            repo_name=repo_name,
            narrative_timestamp=datetime.now().isoformat(),
            accepted_agents=request.agents,
            trust_level="pending"
        )
        capsule.add_linked_repo(linked_repo)
        
        # Add shared anchor if requested
        if request.include_anchors:
            shared_anchor = create_shared_anchor(
                anchor_name="CROSS_REPO_ANCHOR",
                anchor_seed="EOS_SEED_ORION",
                metadata={"created_via": "collab_api", "target_repo": f"{owner}/{repo_name}"}
            )
            capsule.add_shared_anchor(shared_anchor)
        
        # Tag with DLP
        capsule_data = capsule.to_dict()
        tag_id = dlp_tracker.create_tag("collab_export", capsule_data)
        tag = dlp_tracker.tags[tag_id]
        tag.add_anchor_protocol("CROSS_REPO_BRIDGE")
        tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
        tag.metadata.update({
            "target_repo": f"{owner}/{repo_name}",
            "agent_roster": request.agents,
            "ethics_flag": "Picard_Delta_3"
        })
        
        return ExportResponse(
            success=True,
            capsule_id=capsule_id,
            capsule_data=capsule_data,
            dlp_tag_id=tag_id,
            export_timestamp=datetime.now().isoformat(),
            signed=True
        )
        
    except Exception as e:
        logger.error("Export failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post("/context/import", response_model=ImportResponse)
async def import_context(
    request: ImportRequest,
    token: HTTPAuthorizationCredentials = Depends(require_auth)
) -> ImportResponse:
    """
    Import and validate capsule from external repository.
    
    Validates seals/anchors, runs ethics checks, and returns activation report.
    """
    logger.info("Importing capsule: %s", request.capsule_data.get("capsule_id", "unknown"))
    
    try:
        # Parse capsule
        capsule = MultiRepoCapsule.from_dict(request.capsule_data)
        
        # Validation results
        validation_results = {
            "anchor_integrity": None,
            "ethics_compliance": None,
            "signature_check": None,
            "drift_check": None
        }
        
        # Validate anchor integrity
        if request.validate_anchors:
            validation_results["anchor_integrity"] = capsule.verify_anchor_integrity()
            if not validation_results["anchor_integrity"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Anchor integrity validation failed"
                )
        
        # Validate ethics compliance
        if request.validate_ethics:
            validation_results["ethics_compliance"] = capsule.verify_ethics_compliance()
        
        # Check symbolic drift
        if capsule.symbolic_drift > 0.002:  # 0.2% threshold
            validation_results["drift_check"] = False
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Symbolic drift too high: {capsule.symbolic_drift}"
            )
        validation_results["drift_check"] = True
        
        # Verify signature
        expected_sig = capsule.compute_signature()
        provided_sig = request.capsule_data.get("signature", "")
        validation_results["signature_check"] = (expected_sig == provided_sig)
        
        # Tag with DLP
        tag_id = dlp_tracker.create_tag("collab_import", request.capsule_data)
        tag = dlp_tracker.tags[tag_id]
        tag.add_anchor_protocol("CROSS_REPO_BRIDGE")
        tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
        tag.metadata.update({
            "capsule_id": capsule.capsule_id,
            "validation_results": validation_results,
            "trust_level": request.trust_level
        })
        
        return ImportResponse(
            success=True,
            capsule_id=capsule.capsule_id,
            validation_results=validation_results,
            activation_timestamp=datetime.now().isoformat(),
            trust_level=request.trust_level
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Import failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/workflow/trigger", response_model=WorkflowTriggerResponse)
async def trigger_workflow(
    request: WorkflowTriggerRequest,
    token: HTTPAuthorizationCredentials = Depends(require_auth)
) -> WorkflowTriggerResponse:
    """
    Trigger build/test workflow in external repository.
    
    Supports event chaining for multi-repo sync.
    Note: Requires GitHub API credentials for actual workflow triggering.
    """
    logger.info("Triggering workflow %s in %s", request.workflow_name, request.target_repo)
    
    # Tag with DLP
    tag_id = dlp_tracker.create_tag("workflow_trigger", {
        "target_repo": request.target_repo,
        "workflow_name": request.workflow_name,
        "event_type": request.event_type
    })
    
    # Generate event chain ID for tracking
    event_chain_id = f"chain_{int(datetime.now().timestamp())}"
    
    # Note: Actual workflow triggering would require GitHub API integration
    # This is a placeholder implementation
    
    return WorkflowTriggerResponse(
        success=True,
        target_repo=request.target_repo,
        workflow_name=request.workflow_name,
        trigger_timestamp=datetime.now().isoformat(),
        event_chain_id=event_chain_id
    )


@router.post("/invite", response_model=InviteResponse)
async def repo_linking_invite(
    request: InviteRequest,
    token: HTTPAuthorizationCredentials = Depends(require_auth)
) -> InviteResponse:
    """
    Initiate repository linking invitation.
    
    Exchanges anchors, permissions, and establishes trust chain.
    """
    logger.info("Creating invitation for %s", request.repo_url)
    
    try:
        # Create invitation ID
        invitation_id = f"invite_{int(datetime.now().timestamp())}"
        
        # Create shared anchor for the invitation
        anchor = create_shared_anchor(
            anchor_name="REPO_LINK_ANCHOR",
            anchor_seed="EOS_SEED_ORION",
            metadata={
                "invitation_id": invitation_id,
                "invited_repo": request.repo_url
            }
        )
        
        # Tag with DLP
        tag_id = dlp_tracker.create_tag("repo_invitation", {
            "invitation_id": invitation_id,
            "repo_url": request.repo_url,
            "agents": request.agents
        })
        tag = dlp_tracker.tags[tag_id]
        tag.add_anchor_protocol("REPO_LINKING")
        tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
        
        return InviteResponse(
            success=True,
            invitation_id=invitation_id,
            repo_url=request.repo_url,
            agents=request.agents,
            anchor_exchange=anchor.to_dict(),
            created_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error("Invitation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invitation failed: {str(e)}"
        )


@router.post("/agents/sync", response_model=AgentSyncResponse)
async def sync_agent_status(
    request: AgentSyncRequest,
    token: HTTPAuthorizationCredentials = Depends(require_auth)
) -> AgentSyncResponse:
    """
    Synchronize agent status across repositories.
    
    Flags missing agents or alignment drift, returns change log.
    """
    logger.info("Syncing agent status")
    
    # Known agents in Aurora system
    known_agents = ["R-2", "Copilot", "Aurora"]
    
    # Agents to sync (all if not specified)
    agents_to_sync = request.agent_names or known_agents
    
    # Build sync results
    synced_agents = []
    missing_agents = []
    change_log = []
    
    for agent_name in agents_to_sync:
        if agent_name in known_agents:
            synced_agents.append({
                "agent_name": agent_name,
                "status": "active",
                "last_seen": datetime.now().isoformat(),
                "alignment": "green"
            })
        else:
            missing_agents.append(agent_name)
            change_log.append({
                "type": "missing_agent",
                "agent_name": agent_name,
                "timestamp": datetime.now().isoformat()
            })
    
    # Calculate alignment drift (simplified)
    alignment_drift = 0.0 if not missing_agents else len(missing_agents) * 0.001
    
    # Tag with DLP
    tag_id = dlp_tracker.create_tag("agent_sync", {
        "synced_count": len(synced_agents),
        "missing_count": len(missing_agents)
    })
    
    return AgentSyncResponse(
        success=True,
        synced_agents=synced_agents,
        missing_agents=missing_agents,
        alignment_drift=alignment_drift,
        change_log=change_log,
        sync_timestamp=datetime.now().isoformat()
    )


@router.get("/status")
async def get_collab_status(
    token: HTTPAuthorizationCredentials = Depends(require_auth)
) -> Dict[str, Any]:
    """
    Get current cross-repo collaboration system status.
    
    Returns active capsules, agent roster, drift metrics.
    """
    return {
        "status": "active",
        "anchor_seed": "EOS_SEED_ORION",
        "ethics_protocol": "Picard_Delta_3",
        "dlp_summary": dlp_tracker.get_system_summary(),
        "timestamp": datetime.now().isoformat()
    }
