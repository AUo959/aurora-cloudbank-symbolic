"""
Dashboard API Integration

FastAPI routes for drift/ethics monitoring dashboard.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = None
    HTTPException = None
    Query = None
    BaseModel = object
    Field = lambda **kwargs: None

from .monitoring_system import MonitoringSystem, AlertConfig, AlertLevel
from .ethics_engine import ActionContext
from src.core.time_utils import utc_now, utc_iso

logger = logging.getLogger(__name__)


# Pydantic models for API
class BehaviorMetricsInput(BaseModel):
    """Input for recording behavior metrics"""
    agent_id: str = Field(..., description="Agent identifier")
    metrics: Dict[str, float] = Field(..., description="Metric values")
    context_tag: Optional[str] = Field(None, description="DLP context tag")


class BaselineInput(BaseModel):
    """Input for establishing baseline"""
    agent_id: str = Field(..., description="Agent identifier")
    historical_data: Dict[str, List[float]] = Field(..., description="Historical metric values")


class ActionEvaluationInput(BaseModel):
    """Input for action evaluation"""
    agent_id: str = Field(..., description="Agent identifier")
    action_type: str = Field(..., description="Type of action")
    parameters: Dict[str, Any] = Field(..., description="Action parameters")
    context_tag: Optional[str] = Field(None, description="DLP context tag")


class ComplianceReportQuery(BaseModel):
    """Query parameters for compliance report"""
    since_hours: Optional[int] = Field(168, description="Hours to look back (default: 168 = 1 week)")
    agent_id: Optional[str] = Field(None, description="Specific agent ID")


# Global monitoring system instance
# Note: Using module-level global for simplicity in FastAPI integration.
# For production with complex testing requirements, consider:
# - Dependency injection with FastAPI's Depends()
# - Application state via app.state
# - Context managers for proper lifecycle management
_monitoring_system: Optional[MonitoringSystem] = None


def get_monitoring_system(
    storage_dir: Optional[Path] = None,
    ethics_rules_path: Optional[Path] = None
) -> MonitoringSystem:
    """Get or create global monitoring system instance"""
    global _monitoring_system
    
    if _monitoring_system is None:
        # Use default paths if not provided
        if storage_dir is None:
            import os
            storage_dir = Path(os.getenv("MONITORING_STORAGE_DIR", "./monitoring_data"))
        
        if ethics_rules_path is None:
            import os
            # Try environment variable first, then default path
            ethics_path_str = os.getenv("ETHICS_RULES_PATH", "./ethics/validation_engine/validation_rules.json")
            ethics_path = Path(ethics_path_str)
            if ethics_path.exists():
                ethics_rules_path = ethics_path
        
        _monitoring_system = MonitoringSystem(
            storage_dir=storage_dir,
            ethics_rules_path=ethics_rules_path
        )
    
    return _monitoring_system


def create_monitoring_router(
    storage_dir: Optional[Path] = None,
    ethics_rules_path: Optional[Path] = None
) -> Optional[APIRouter]:
    """
    Create FastAPI router for monitoring dashboard
    
    Args:
        storage_dir: Directory for persistent storage
        ethics_rules_path: Path to ethics rules configuration
    
    Returns:
        APIRouter with monitoring endpoints (None if FastAPI not available)
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI not available - monitoring routes disabled")
        return None
    
    router = APIRouter(prefix="/monitoring", tags=["monitoring"])
    
    # Initialize monitoring system
    monitoring = get_monitoring_system(storage_dir, ethics_rules_path)
    
    @router.get("/health")
    async def health_check():
        """Health check for monitoring system"""
        return {
            "status": "healthy",
            "timestamp": utc_iso(),
            "audit_chain_valid": monitoring.audit_logger.verify_chain()
        }
    
    @router.post("/baseline")
    async def establish_baseline(input: BaselineInput):
        """Establish behavioral baseline for an agent"""
        try:
            monitoring.establish_agent_baseline(
                agent_id=input.agent_id,
                historical_data=input.historical_data
            )
            
            return {
                "success": True,
                "agent_id": input.agent_id,
                "metrics_count": len(input.historical_data),
                "timestamp": utc_iso()
            }
        except Exception as e:
            logger.error("Failed to establish baseline: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/behavior/record")
    async def record_behavior(input: BehaviorMetricsInput):
        """Record behavioral metrics for an agent"""
        try:
            monitoring.record_agent_behavior(
                agent_id=input.agent_id,
                metrics=input.metrics,
                context_tag=input.context_tag
            )
            
            return {
                "success": True,
                "agent_id": input.agent_id,
                "metrics_recorded": len(input.metrics),
                "timestamp": utc_iso()
            }
        except Exception as e:
            logger.error("Failed to record behavior: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/behavior/check")
    async def check_behavior(
        agent_id: str = Query(..., description="Agent identifier"),
        context_tag: Optional[str] = Query(None, description="DLP context tag")
    ):
        """Check agent behavior for drift"""
        try:
            result = monitoring.check_agent_behavior(
                agent_id=agent_id,
                context_tag=context_tag
            )
            
            return result
        except Exception as e:
            logger.error("Failed to check behavior: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/action/evaluate")
    async def evaluate_action(input: ActionEvaluationInput):
        """Evaluate action against ethics rules"""
        try:
            result = monitoring.evaluate_action(
                agent_id=input.agent_id,
                action_type=input.action_type,
                parameters=input.parameters,
                context_tag=input.context_tag
            )
            
            return result
        except Exception as e:
            logger.error("Failed to evaluate action: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/agent/{agent_id}/status")
    async def get_agent_status(agent_id: str):
        """Get comprehensive status for an agent"""
        try:
            status = monitoring.get_agent_status(agent_id)
            return status
        except Exception as e:
            logger.error("Failed to get agent status: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/alerts")
    async def get_alerts(
        agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
        level: Optional[str] = Query(None, description="Filter by alert level"),
        since_hours: Optional[int] = Query(24, description="Hours to look back")
    ):
        """Get drift alerts"""
        try:
            since = utc_now() - timedelta(hours=since_hours)
            
            from .drift_detector import DriftLevel
            drift_level = DriftLevel(level) if level else None
            
            alerts = monitoring.drift_detector.get_alerts(
                agent_id=agent_id,
                level=drift_level,
                since=since
            )
            
            return {
                "alerts": [a.to_dict() for a in alerts],
                "count": len(alerts),
                "since": since.isoformat()
            }
        except Exception as e:
            logger.error("Failed to get alerts: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/violations")
    async def get_violations(
        agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
        severity: Optional[str] = Query(None, description="Filter by severity"),
        since_hours: Optional[int] = Query(24, description="Hours to look back")
    ):
        """Get ethics violations"""
        try:
            since = utc_now() - timedelta(hours=since_hours)
            
            from .ethics_engine import ViolationSeverity
            violation_severity = ViolationSeverity(severity) if severity else None
            
            violations = monitoring.ethics_engine.get_violations(
                agent_id=agent_id,
                severity=violation_severity,
                since=since
            )
            
            return {
                "violations": [v.to_dict() for v in violations],
                "count": len(violations),
                "since": since.isoformat()
            }
        except Exception as e:
            logger.error("Failed to get violations: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/audit")
    async def get_audit_log(
        agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
        event_type: Optional[str] = Query(None, description="Filter by event type"),
        since_hours: Optional[int] = Query(24, description="Hours to look back")
    ):
        """Get audit log entries"""
        try:
            since = utc_now() - timedelta(hours=since_hours)
            
            from .audit_logger import AuditEventType
            audit_type = AuditEventType(event_type) if event_type else None
            
            entries = monitoring.audit_logger.get_entries(
                agent_id=agent_id,
                event_type=audit_type,
                since=since
            )
            
            return {
                "entries": [e.to_dict() for e in entries],
                "count": len(entries),
                "chain_valid": monitoring.audit_logger.verify_chain(),
                "since": since.isoformat()
            }
        except Exception as e:
            logger.error("Failed to get audit log: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/compliance/report")
    async def get_compliance_report(
        since_hours: Optional[int] = Query(168, description="Hours to look back"),
        agent_id: Optional[str] = Query(None, description="Specific agent ID")
    ):
        """Generate compliance report"""
        try:
            since = utc_now() - timedelta(hours=since_hours)
            
            report = monitoring.generate_compliance_report(
                since=since,
                agent_id=agent_id
            )
            
            return report
        except Exception as e:
            logger.error("Failed to generate compliance report: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/export")
    async def export_state():
        """Export full monitoring system state"""
        try:
            state = monitoring.export_state()
            return state
        except Exception as e:
            logger.error("Failed to export state: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/dashboard/stats")
    async def get_dashboard_stats():
        """Get overall dashboard statistics"""
        try:
            agent_ids = monitoring.behavior_monitor.get_agent_ids()
            since_24h = utc_now() - timedelta(hours=24)
            
            total_alerts = len(monitoring.drift_detector.get_alerts(since=since_24h))
            total_violations = len(monitoring.ethics_engine.get_violations(since=since_24h))
            total_interventions = len([
                i for i in monitoring.interventions
                if datetime.fromisoformat(i.timestamp) >= since_24h
            ])
            
            return {
                "agents_monitored": len(agent_ids),
                "alerts_24h": total_alerts,
                "violations_24h": total_violations,
                "interventions_24h": total_interventions,
                "audit_entries": len(monitoring.audit_logger.entries),
                "audit_chain_valid": monitoring.audit_logger.verify_chain(),
                "timestamp": utc_iso()
            }
        except Exception as e:
            logger.error("Failed to get dashboard stats: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
    
    logger.info("Monitoring API router created with %d routes", len(router.routes))
    
    return router
