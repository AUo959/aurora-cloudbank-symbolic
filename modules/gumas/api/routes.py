"""
GUMAS Ethics API Routes

Provides ethics validation, compliance checking, and rule management.

DLP: gumas_ethics_api
T1: Initial implementation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.monitoring.ethics_engine import (
    EthicsEngine,
    ActionContext,
    EthicsViolation,
    EthicsRule,
    ViolationSeverity,
    RuleCategory
)
from src.core.native_dlp_export import NativeDLPTracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gumas", tags=["GUMAS Ethics"])
dlp_tracker = NativeDLPTracker()

# Initialize global ethics engine
ethics_engine = EthicsEngine()


# Pydantic Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    rules_loaded: int
    violations_recorded: int
    timestamp: str


class EvaluateActionRequest(BaseModel):
    """Request to evaluate an action"""
    agent_id: str = Field(..., description="Agent performing the action")
    action_type: str = Field(..., description="Type of action to evaluate")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    context_tag: Optional[str] = Field(None, description="DLP context tag")


class EvaluateActionResponse(BaseModel):
    """Response from action evaluation"""
    compliant: bool
    should_block: bool
    violations: List[Dict[str, Any]]
    evaluation_timestamp: str
    context_tag: Optional[str] = None


class ViolationQueryRequest(BaseModel):
    """Query parameters for violations"""
    agent_id: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


class AddRuleRequest(BaseModel):
    """Request to add a new ethics rule"""
    id: str
    name: str
    description: str
    category: str
    severity: str
    auto_block: bool
    conditions: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuleResponse(BaseModel):
    """Response containing rule information"""
    id: str
    name: str
    description: str
    category: str
    severity: str
    auto_block: bool
    conditions: List[str]
    metadata: Dict[str, Any]


# API Routes
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for GUMAS Ethics API
    
    DLP: gumas_health
    """
    try:
        return HealthResponse(
            status="healthy",
            service="gumas_ethics_api",
            rules_loaded=len(ethics_engine.rules),
            violations_recorded=len(ethics_engine.violations),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=EvaluateActionResponse)
async def evaluate_action(request: EvaluateActionRequest) -> EvaluateActionResponse:
    """
    Evaluate an action against ethics rules
    
    Returns list of violations (if any) and whether action should be blocked.
    
    DLP: gumas_evaluate_action
    """
    try:
        # Create action context
        context = ActionContext(
            agent_id=request.agent_id,
            action_type=request.action_type,
            parameters=request.parameters,
            context_tag=request.context_tag
        )
        
        # Evaluate action
        violations = ethics_engine.evaluate_action(context)
        
        # Convert violations to dict
        violations_data = [v.to_dict() for v in violations]
        
        # Check if should block
        should_block = ethics_engine.check_should_block(violations)
        
        # Track with DLP
        dlp_tracker.create_tag(
            operation="gumas_evaluate_action",
            data={
                "agent_id": request.agent_id,
                "action_type": request.action_type,
                "violation_count": len(violations),
                "blocked": should_block
            }
        )
        
        return EvaluateActionResponse(
            compliant=len(violations) == 0,
            should_block=should_block,
            violations=violations_data,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
            context_tag=request.context_tag
        )
        
    except Exception as e:
        logger.error("Action evaluation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/violations", response_model=List[Dict[str, Any]])
async def get_violations(request: ViolationQueryRequest) -> List[Dict[str, Any]]:
    """
    Get violations with optional filtering
    
    DLP: gumas_violations_query
    """
    try:
        # Parse severity and category if provided
        severity = ViolationSeverity(request.severity) if request.severity else None
        category = RuleCategory(request.category) if request.category else None
        
        # Get filtered violations
        violations = ethics_engine.get_violations(
            agent_id=request.agent_id,
            severity=severity,
            category=category
        )
        
        # Limit results
        violations = violations[-request.limit:]
        
        # Convert to dict
        violations_data = [v.to_dict() for v in violations]
        
        # Track with DLP
        dlp_tracker.create_tag(
            operation="gumas_violations_query",
            data={"violation_count": len(violations_data)}
        )
        
        return violations_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")
    except Exception as e:
        logger.error("Violations query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=List[RuleResponse])
async def get_rules() -> List[RuleResponse]:
    """
    Get all configured ethics rules
    
    DLP: gumas_rules_list
    """
    try:
        rules_data = []
        
        for rule in ethics_engine.rules.values():
            rules_data.append(RuleResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                category=rule.category.value,
                severity=rule.severity.value,
                auto_block=rule.auto_block,
                conditions=rule.conditions,
                metadata=rule.metadata
            ))
        
        # Track with DLP
        dlp_tracker.create_tag(
            operation="gumas_rules_list",
            data={"rule_count": len(rules_data)}
        )
        
        return rules_data
        
    except Exception as e:
        logger.error("Rules list failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(rule_id: str) -> RuleResponse:
    """
    Get specific rule by ID
    
    DLP: gumas_rule_detail
    """
    try:
        if rule_id not in ethics_engine.rules:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
        
        rule = ethics_engine.rules[rule_id]
        
        return RuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            category=rule.category.value,
            severity=rule.severity.value,
            auto_block=rule.auto_block,
            conditions=rule.conditions,
            metadata=rule.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Rule detail failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules", response_model=RuleResponse, status_code=201)
async def add_rule(request: AddRuleRequest) -> RuleResponse:
    """
    Add a new ethics rule
    
    DLP: gumas_add_rule
    """
    try:
        # Check if rule already exists
        if request.id in ethics_engine.rules:
            raise HTTPException(
                status_code=409,
                detail=f"Rule {request.id} already exists"
            )
        
        # Parse category and severity
        try:
            category = RuleCategory(request.category)
            severity = ViolationSeverity(request.severity)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")
        
        # Create rule
        rule = EthicsRule(
            id=request.id,
            name=request.name,
            description=request.description,
            category=category,
            severity=severity,
            auto_block=request.auto_block,
            conditions=request.conditions,
            metadata=request.metadata
        )
        
        # Add to engine
        ethics_engine.add_rule(rule)
        
        # Track with DLP
        dlp_tracker.create_tag(
            operation="gumas_add_rule",
            data={"rule_id": request.id, "rule_name": request.name}
        )
        
        return RuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            category=rule.category.value,
            severity=rule.severity.value,
            auto_block=rule.auto_block,
            conditions=rule.conditions,
            metadata=rule.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Add rule failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: str):
    """
    Delete an ethics rule
    
    DLP: gumas_delete_rule
    """
    try:
        if rule_id not in ethics_engine.rules:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
        
        ethics_engine.remove_rule(rule_id)
        
        # Track with DLP
        dlp_tracker.create_tag(
            operation="gumas_delete_rule",
            data={"rule_id": rule_id}
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete rule failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/{rule_id}/register-evaluator")
async def register_custom_evaluator(
    rule_id: str,
    condition: str = Query(..., description="Condition pattern to register evaluator for")
):
    """
    Register a custom condition evaluator for a rule
    
    Note: This endpoint is for documentation purposes. Custom evaluators
    must be registered programmatically via the EthicsEngine API.
    
    DLP: gumas_register_evaluator
    """
    raise HTTPException(
        status_code=501,
        detail="Custom evaluators must be registered programmatically. "
               "See EthicsEngine.register_evaluator() documentation."
    )


@router.delete("/violations", status_code=204)
async def clear_violations(
    before: Optional[str] = Query(None, description="Clear violations before this ISO timestamp")
):
    """
    Clear old violations
    
    DLP: gumas_clear_violations
    """
    try:
        before_dt = datetime.fromisoformat(before) if before else None
        ethics_engine.clear_violations(before=before_dt)
        
        # Track with DLP
        dlp_tracker.create_tag(
            operation="gumas_clear_violations",
            data={"before": before}
        )
        
        return None
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp: {e}")
    except Exception as e:
        logger.error("Clear violations failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[str])
async def get_categories() -> List[str]:
    """
    Get all available rule categories
    
    DLP: gumas_categories
    """
    return [cat.value for cat in RuleCategory]


@router.get("/severities", response_model=List[str])
async def get_severities() -> List[str]:
    """
    Get all available violation severity levels
    
    DLP: gumas_severities
    """
    return [sev.value for sev in ViolationSeverity]
