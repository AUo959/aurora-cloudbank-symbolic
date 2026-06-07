"""
main FastAPI app for Aurora CloudBank Symbolic

Exposes endpoints for quantum and geometric algebra modules.

Enhanced with Claude Sonnet 4 capabilities and ChatGPT Agent Mode integration.
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager

# Install log-injection filter as early as possible so all subsequent loggers
# inherit it.  Import is guarded so a missing data_guardian doesn't crash startup.
try:
    from modules.data_guardian.log_sanitizer import SanitizingLogFilter as _SanitizingLogFilter
    logging.getLogger().addFilter(_SanitizingLogFilter())
except Exception:  # pragma: no cover - graceful degradation
    pass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Literal

from api import env_bootstrap  # noqa: F401
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.observability import get_telemetry, get_r2_telemetry
from src.middleware.body_size import MaxBodySizeMiddleware, _default_max_bytes
from src.middleware.exception_handler import validation_handler
from src.middleware.idempotency import IdempotencyMiddleware
from src.middleware.pii_middleware import PIIMiddleware
from src.middleware.request_id import RequestIDMiddleware
from src.runtime.shutdown import ShutdownCoordinator
try:
    from src.middleware.telemetry_middleware import MetricsMiddleware
    _METRICS_MIDDLEWARE_AVAILABLE = True
except Exception as _mm_exc:  # pragma: no cover - graceful degradation
    logging.getLogger("aurora_api").warning("MetricsMiddleware unavailable: %s", _mm_exc)
    _METRICS_MIDDLEWARE_AVAILABLE = False

from modules.symbolic_core.geometric_algebra import GeometricAlgebra
try:
    from modules.hr.rd_api import router as rd_router
    RD_PIPELINE_AVAILABLE = True
except Exception as e:  # pragma: no cover - optional import
    logging.getLogger("aurora_api").warning("RD Pipeline API not available: %s", e)
    RD_PIPELINE_AVAILABLE = False
from modules.symbolic_core.sonnet4_integration_hub import enable_sonnet4_globally, sonnet4_hub

# Import ChatGPT Agent Mode integration
from src.integrations.chatgpt_agent_mode import chatgpt_agent_integration

# Import Gemini Agent Mode integration
try:
    from src.integrations.gemini_agent_integration import gemini_agent_integration
    GEMINI_AGENT_AVAILABLE = True
except ImportError:
    logging.getLogger("aurora_api").warning("Gemini Agent not available - Gemini features disabled")
    GEMINI_AGENT_AVAILABLE = False

# Import centralized security configuration
from src.middleware.fastapi_security import (
    limiter,
    security,
    verify_csrf_token,
    verify_ws_token,
    validate_ws_tool,
    sanitize_request_id,
    sanitize_session_id
)
from src.middleware.csrf_middleware import GlobalCsrfMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import APIRouter
from src.security.oauth2 import get_current_active_user, User  # authentication dependency
from src.agents.crew.base_agent import get_crew_agent, get_all_crew_agents

# Action Guard: fire-and-forget ethics/compliance evaluation on response paths
try:
    from src.monitoring.action_guard import evaluate_response as _evaluate_response
    ACTION_GUARD_AVAILABLE = True
except Exception as _action_guard_exc:  # pragma: no cover - graceful degradation
    logging.getLogger("aurora_api").warning("ActionGuard not available: %s", _action_guard_exc)
    ACTION_GUARD_AVAILABLE = False

    def _evaluate_response(*_args, **_kwargs) -> None:  # type: ignore[misc]
        """No-op fallback when action_guard cannot be imported."""

# Crew Agents API Router (Phase 3 minimal implementation)
crew_router = APIRouter(prefix="/api/crew", tags=["crew"])


@crew_router.get("/all")
async def list_all_crew(user: User = Depends(get_current_active_user)):
    """List all registered crew agents with condensed status.

    Security: Requires active user (OAuth2 token).
    """
    agents = get_all_crew_agents().values()
    return {
        "count": len(list(agents)),
        "agents": [
            {
                "surname": a.surname,
                "role": a.role.value,
                "status": a.status,
                "clearance": a.clearance.value,
                "t1_state": a.t1_state,
                "srb_resolution": a.srb_resolution,
            }
            for a in agents
        ],
    }


@crew_router.post("/{surname}/process")
@limiter.limit("30/minute")  # Crew collaboration - moderate rate per IP
async def process_agent_task(
    surname: str,
    task: Dict[str, Any],
    request: Request,
    user: User = Depends(get_current_active_user),
):
    """Process a task with a specific crew agent.

    Body: {"task_type": str, "context": {}, "priority": str}
    Returns task execution including DLP placeholders.
    """
    agent = get_crew_agent(surname)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Crew agent '{surname}' not found")
    result = await agent.process_request(task)
    _evaluate_response(
        "agent_task",
        result,
        metadata={"endpoint": f"/api/crew/{surname}/process", "surname": surname},
        agent_id=surname,
        context_tag=f"crew_agent_{surname}",
    )
    return result


@crew_router.post("/collaborate")
@limiter.limit("30/minute")  # Crew collaboration - moderate rate per IP
async def collaborate_agents(
    payload: Dict[str, Any],
    request: Request,
    user: User = Depends(get_current_active_user),
):
    """Collaborate two agents on a task.

    Body: {"primary": "Thorne", "secondary": "Markov", "task": {...}}
    Returns collaboration result combining contributions.
    """
    primary = get_crew_agent(payload.get("primary"))
    secondary = get_crew_agent(payload.get("secondary"))
    if not primary or not secondary:
        raise HTTPException(status_code=404, detail="One or both agents not found")
    task_def = payload.get("task", {})
    result = await primary.collaborate_with(secondary, task_def)
    return result

# (Moved time/hash imports into helper to satisfy lint ordering)

# Import AuMemManager API integration
try:
    from modules.aumemmanager.api_integration import router as aumemmanager_router
    AUMEMMANAGER_AVAILABLE = True
    AUMEMMANAGER_ROUTER = aumemmanager_router
except ImportError:
    logging.getLogger("aurora_api").warning("AuMemManager not available - some memory features disabled")
    AUMEMMANAGER_AVAILABLE = False
    AUMEMMANAGER_ROUTER = None

# Import Memory Retrieval API integration
try:
    from modules.memory_retrieval.api import router as memory_retrieval_router
    MEMORY_RETRIEVAL_AVAILABLE = True
    MEMORY_RETRIEVAL_ROUTER = memory_retrieval_router
except ImportError:
    logging.getLogger("aurora_api").warning("Memory Retrieval not available - memory retrieval features disabled")
    MEMORY_RETRIEVAL_AVAILABLE = False
    MEMORY_RETRIEVAL_ROUTER = None

# Import Data Guardian API integration
try:
    from modules.data_guardian.api import router as data_guardian_router
    DATA_GUARDIAN_AVAILABLE = True
    DATA_GUARDIAN_ROUTER = data_guardian_router
except ImportError:
    logging.getLogger("aurora_api").warning("Data Guardian not available - PII detection/redaction features disabled")
    DATA_GUARDIAN_AVAILABLE = False
    DATA_GUARDIAN_ROUTER = None

# Import Insight Ledger API integration
try:
    from modules.insight_ledger.api import initialize_ledger
    from modules.insight_ledger.api import router as insight_ledger_router
    INSIGHT_LEDGER_AVAILABLE = True
    INSIGHT_LEDGER_ROUTER = insight_ledger_router
except ImportError:
    logging.getLogger("aurora_api").warning("Insight Ledger not available - audit trail features disabled")
    INSIGHT_LEDGER_AVAILABLE = False
    INSIGHT_LEDGER_ROUTER = None
    initialize_ledger = None

# Import Quantum Simulator API integration
try:
    from modules.quantum_simulator.api import router as quantum_simulator_router
    QUANTUM_SIMULATOR_AVAILABLE = True
    QUANTUM_SIMULATOR_ROUTER = quantum_simulator_router
except ImportError:
    logging.getLogger("aurora_api").warning("Quantum Simulator not available - quantum simulation features disabled")
    QUANTUM_SIMULATOR_AVAILABLE = False
    QUANTUM_SIMULATOR_ROUTER = None

# Import Thread Transfer Bridge integration
try:
    from modules.reflective_autonomy.thread_transfer import (
        get_bridge_instance
    )
    THREAD_BRIDGE_AVAILABLE = True
except ImportError:
    logging.getLogger("aurora_api").warning(
        "Thread Transfer Bridge not available - cross-thread continuity features disabled"
    )
    THREAD_BRIDGE_AVAILABLE = False
    get_bridge_instance = None
    initialize_bridge = None

# Import Thread Transfer Bridge v2 integration
try:
    from modules.reflective_autonomy.thread_transfer.v2 import (
        get_node_registry,
        get_drift_predictor,
        get_pattern_analyzer,
        get_auto_corrector,
        get_layer_manager,
        get_hierarchy_validator,
        get_repository_synchronizer,
        get_cross_repository_bridge,
        BridgeLayer,
        DriftFeatures,
    )
    THREAD_BRIDGE_V2_AVAILABLE = True
except ImportError:
    logging.getLogger("aurora_api").warning(
        "Thread Transfer Bridge v2 not available - distributed/predictive features disabled"
    )
    THREAD_BRIDGE_V2_AVAILABLE = False

# Import Event Coordination Registry API integration
try:
    from src.coordination.event_api import router as event_coordination_router
    EVENT_COORDINATION_AVAILABLE = True
    EVENT_COORDINATION_ROUTER = event_coordination_router
except ImportError:
    logging.getLogger("aurora_api").warning(
        "Event Coordination not available - multi-agent coordination features disabled"
    )
    EVENT_COORDINATION_AVAILABLE = False
    EVENT_COORDINATION_ROUTER = None

# Import Fleet Bridge API integration
try:
    from src.integrations.fleet_bridge import router as fleet_bridge_router
    FLEET_BRIDGE_AVAILABLE = True
    FLEET_BRIDGE_ROUTER = fleet_bridge_router
except ImportError:
    logging.getLogger("aurora_api").warning("Fleet Bridge not available - Python-JS fleet sync features disabled")
    FLEET_BRIDGE_AVAILABLE = False
    FLEET_BRIDGE_ROUTER = None

# Import Relay Manager API integration
try:
    from src.aurora.relays.api_routes import router as relay_manager_router
    RELAY_MANAGER_AVAILABLE = True
    RELAY_MANAGER_ROUTER = relay_manager_router
except ImportError:
    logging.getLogger("aurora_api").warning("Relay Manager not available - L1-L3 boundary enforcement disabled")
    RELAY_MANAGER_AVAILABLE = False
    RELAY_MANAGER_ROUTER = None

# from modules.symbolic_core.quantum_vsa import QuantumVSA  # Uncomment if available

# Import Memory Retrieval API router
try:
    from modules.memory_retrieval.router import router as memory_retrieval_router
    MEMORY_RETRIEVAL_AVAILABLE = True
    MEMORY_RETRIEVAL_ROUTER = memory_retrieval_router
except ImportError:
    logging.getLogger("aurora_api").warning("Memory Retrieval not available - memory retrieval features disabled")
    MEMORY_RETRIEVAL_AVAILABLE = False
    MEMORY_RETRIEVAL_ROUTER = None

# Structured logger (avoids f-string interpolation for security)
logger = logging.getLogger("aurora_api")


# ================================
# Initialize HALO/PAS Drift Controller
# ================================
HALO_PAS_CONTROLLER = None
HALO_PAS_AVAILABLE = False
try:
    from src.aurora.continuity import HALOPASController
    HALO_PAS_CONTROLLER = HALOPASController(interval=0.25)
    HALO_PAS_AVAILABLE = True
    logger.info("✅ HALO/PAS Drift Controller initialized successfully")
except ImportError as e:
    logger.warning("⚠️ HALO/PAS Controller not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to initialize HALO/PAS Controller: %s", e)


# ================================
# Application Lifecycle Management
# ================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with startup and shutdown logic."""
    # Startup
    logger.info("Aurora API starting up...")

    # Validate application configuration — exits non-zero if critical vars missing
    from src.config.settings import load_settings
    _settings = load_settings(exit_on_error=True)
    if _settings:
        logger.info("Configuration validated (build_phase=%s)", _settings.aurora_build_phase)

    logger.info("Rate limiter active: AI=20/min, crew=30/min, quantum=10/min, memory_write=60/min")

    # Warn when in-process monitoring state cannot be shared across workers.
    _worker_count = int(os.environ.get("WEB_CONCURRENCY", "1"))
    if _worker_count > 1:
        logger.warning(
            "⚠️  WEB_CONCURRENCY=%d detected. The monitoring, ethics, and audit modules "
            "use in-process state that is NOT shared across uvicorn workers. "
            "Run with WEB_CONCURRENCY=1 (or a single-worker deployment) to avoid "
            "state divergence. See docs/operations/single-worker-constraint.md for details.",
            _worker_count,
        )

    shutdown_coordinator = ShutdownCoordinator()

    # Initialize telemetry systems
    try:
        aurora_telemetry = get_telemetry(service_name="aurora-cloudbank-api")
        r2_telemetry = get_r2_telemetry(service_name="aurora-r2-agent")
        logger.info(
            "✅ Telemetry systems initialized (Aurora: %s, R2: %s)",
            aurora_telemetry.enabled,
            r2_telemetry.enabled,
        )
    except Exception as e:
        logger.warning("⚠️ Failed to initialize telemetry: %s", e)

    # Start background metrics pusher for live DriftDetector feeds
    try:
        from src.monitoring.metrics_pusher import start_background_pusher
        start_background_pusher(interval_seconds=30)
        logger.info("Background metrics pusher started (feeds DriftDetector every 30s)")
    except Exception as e:
        logger.warning("Failed to start background metrics pusher: %s", e)

    # Start HALO/PAS drift controller if available
    if HALO_PAS_AVAILABLE and HALO_PAS_CONTROLLER:
        try:
            await HALO_PAS_CONTROLLER.start()
            logger.info("✅ HALO/PAS Drift Controller started")
            shutdown_coordinator.register_flush(HALO_PAS_CONTROLLER.stop, name="HALO/PAS stop")
        except Exception as e:
            logger.error("❌ Failed to start HALO/PAS Controller: %s", e)

    # Periodic retention cleanup: evict old violations/alerts/interventions from memory
    _cleanup_interval = int(os.getenv("AURORA_RETENTION_CLEANUP_INTERVAL_SECONDS", "3600"))

    async def _retention_cleanup_loop() -> None:
        from src.monitoring.dashboard_api import run_monitoring_cleanup
        while True:
            await asyncio.sleep(_cleanup_interval)
            try:
                run_monitoring_cleanup()
            except Exception as _exc:  # noqa: BLE001
                logger.debug("Retention cleanup cycle error: %s", _exc)

    _cleanup_task = asyncio.create_task(_retention_cleanup_loop(), name="retention_cleanup")
    shutdown_coordinator.register(_cleanup_task, name="retention_cleanup")
    logger.info("✅ Retention cleanup task started (interval=%ds)", _cleanup_interval)

    # Register telemetry snapshot as a shutdown flush
    def _telemetry_flush() -> None:
        try:
            telemetry = get_telemetry()
            snapshot = telemetry.get_metrics_snapshot(context_tag="shutdown_metrics")
            logger.info(
                "📊 Final telemetry: %d operations, %d features tracked",
                len(snapshot.performance_metrics),
                len(snapshot.adoption_metrics),
            )
        except Exception as exc:
            logger.debug("Telemetry snapshot failed: %s", exc)

    shutdown_coordinator.register_flush(_telemetry_flush, name="telemetry snapshot")

    # Register shutdown manifest as a flush
    def _manifest_flush() -> None:
        try:
            import json as _json
            manifest = build_shutdown_manifest()
            manifest_path = os.path.join(os.getcwd(), "shutdown_manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                _json.dump(manifest, f, ensure_ascii=False, indent=2)
            logger.info(
                "🧾 Shutdown manifest written (%s components, hash=%s)",
                len(manifest.get("components", {})),
                manifest.get("hash"),
            )
        except Exception as exc:
            logger.warning("⚠️ Failed to generate shutdown manifest: %s", exc)

    shutdown_coordinator.register_flush(_manifest_flush, name="shutdown manifest")

    # ── Structured startup-complete record ──────────────────────────────────────
    _optional_modules = {
        "aumemmanager": AUMEMMANAGER_AVAILABLE,
        "data_guardian": DATA_GUARDIAN_AVAILABLE,
        "insight_ledger": INSIGHT_LEDGER_AVAILABLE,
        "quantum_simulator": QUANTUM_SIMULATOR_AVAILABLE,
        "halo_pas": HALO_PAS_AVAILABLE,
    }
    logger.info(
        "Aurora API startup complete — routes=%d optional_modules=%s",
        len(app.routes),
        {k: v for k, v in _optional_modules.items() if not v},  # log only degraded ones
    )

    yield

    # Shutdown — coordinator cancels tasks, shuts down executors, runs flushes
    logger.info(
        "Aurora API shutting down (tasks=%d flushes=%d executors=%d)...",
        shutdown_coordinator.pending_task_count,
        shutdown_coordinator.registered_flush_count,
        shutdown_coordinator.registered_executor_count,
    )
    await shutdown_coordinator.shutdown(timeout=10.0)
    logger.info("Aurora API shutdown complete.")


def build_shutdown_manifest() -> Dict[str, Any]:
    """Generate a master shutdown manifest capturing terminal system state.

    Minimal Phase 1 helper – later phases will add memory seals, quantum session
    flush records, and extended DLP lineage exports.
    """
    # Localized imports (lint: keep module-level imports at file head only)
    from src.core.time_utils import utc_now, utc_iso  # type: ignore
    import hashlib  # type: ignore
    import json  # type: ignore

    telemetry_snapshot = {}
    try:
        telemetry = get_telemetry()
        snap = telemetry.get_metrics_snapshot(context_tag="shutdown_manifest")
        telemetry_snapshot = {
            "performance_metrics": len(snap.performance_metrics),
            "adoption_metrics": len(snap.adoption_metrics),
            "features_tracked": list(snap.adoption_metrics.keys()),
        }
    except Exception as e:  # pragma: no cover - graceful degradation
        telemetry_snapshot = {"error": str(e)}

    halo_pas_state: Dict[str, Any] = {
        "available": HALO_PAS_AVAILABLE,
        "active": False,
    }
    try:
        if HALO_PAS_AVAILABLE and HALO_PAS_CONTROLLER:
            halo_pas_state["active"] = HALO_PAS_CONTROLLER.running
            halo_pas_state["interval"] = getattr(HALO_PAS_CONTROLLER, "interval", None)
    except Exception as e:  # pragma: no cover
        halo_pas_state["error"] = str(e)

    crew_summary: Dict[str, Any] = {"count": 0, "agents": []}
    try:
        agents = get_all_crew_agents().values()
        crew_summary["count"] = len(list(agents))
        crew_summary["agents"] = [a.surname for a in agents]
    except Exception as e:  # pragma: no cover
        crew_summary["error"] = str(e)

    manifest: Dict[str, Any] = {
        "generated_at": utc_iso(),
        "epoch_ms": int(utc_now().timestamp() * 1000),
        "components": {
            "telemetry": telemetry_snapshot,
            "halo_pas": halo_pas_state,
            "crew_agents": crew_summary,
        },
    }
    # Deterministic hash
    serialized = json.dumps(manifest, sort_keys=True).encode("utf-8")
    manifest["hash"] = hashlib.sha256(serialized).hexdigest()
    return manifest


# Create FastAPI app with lifespan context manager
app = FastAPI(
    title="Aurora CloudBank Symbolic API - Sonnet 4 Enhanced",
    description="Quantum-enhanced symbolic governance system with ChatGPT Agent Mode integration",
    version="1.0.0",
    lifespan=lifespan
)

# ================================
# Rate Limiting Middleware & Handlers
# ================================
try:
    # Attach limiter state and middleware for global rate limiting enforcement
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    logger.info("✅ SlowAPI rate limiting middleware enabled")
except Exception as e:  # pragma: no cover - graceful degradation if slowapi misconfigured
    logger.warning("⚠️ Failed to enable rate limiting middleware: %s", e)

# Body-size guard: registered before RequestIDMiddleware so oversized requests
# are rejected before ID assignment and inner middleware run.
app.add_middleware(MaxBodySizeMiddleware, max_bytes=_default_max_bytes())

# Idempotency middleware: caches and replays responses for state-changing
# requests that carry an Idempotency-Key header. Registered before
# RequestIDMiddleware so the ID is already set when idempotency logic fires.
app.add_middleware(IdempotencyMiddleware)

# Global CSRF enforcement: applies to all state-changing routes except the
# allowlist defined in csrf_middleware._CSRF_ALLOWLIST.
app.add_middleware(GlobalCsrfMiddleware)
logger.info("✅ Global CSRF middleware registered")

# PII detection middleware: scans request/response JSON bodies for PII.
# Audit-only by default; set AURORA_PII_REDACT_RESPONSES=true to enable redaction.
app.add_middleware(PIIMiddleware)

# Request-ID middleware: must be registered last so it wraps everything and
# its ContextVar is set before any inner middleware runs.
app.add_middleware(RequestIDMiddleware)

# Metrics middleware: record per-request latency/status for DriftDetector.
# Registered after RequestIDMiddleware so request-ID context is available.
if _METRICS_MIDDLEWARE_AVAILABLE:
    app.add_middleware(MetricsMiddleware)
    logger.info("MetricsMiddleware registered for live drift detection")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):  # pragma: no cover - simple handler
    """Unified JSON response for rate limit violations with standard headers."""
    # Default retry window (seconds) for per-minute limits
    retry_after = 60
    token_limit = os.getenv("RATE_LIMIT_AUTH_TOKEN_PER_MIN")
    headers = {"Retry-After": str(retry_after)}
    if token_limit:
        headers["X-RateLimit-Limit"] = token_limit
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded", "path": request.url.path},
        headers=headers,
    )


# Fallback header injection if exception handler not applied (SlowAPI may short-circuit in some contexts)
@app.middleware("http")
async def rate_limit_header_middleware(request: Request, call_next):  # pragma: no cover - deterministic
    response = await call_next(request)
    if response.status_code == 429 and "Retry-After" not in response.headers:
        response.headers["Retry-After"] = "60"
        token_limit = os.getenv("RATE_LIMIT_AUTH_TOKEN_PER_MIN")
        if token_limit and "X-RateLimit-Limit" not in response.headers:
            response.headers["X-RateLimit-Limit"] = token_limit
    return response


# ================================
# Telemetry Middleware
# ================================

@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    """
    Middleware to automatically trace all HTTP requests with telemetry.

    Captures:
    - Request path and method
    - Response status code
    - Request duration
    - Errors during processing

    DLP: request_tracing_middleware
    """
    telemetry = get_telemetry()

    # Create operation name from method and path
    operation_name = f"{request.method}_{request.url.path.replace('/', '_').strip('_')}"

    # Trace the request
    with telemetry.trace_operation(
        operation_name,
        attributes={
            "http.method": request.method,
            "http.url": str(request.url.path),
            "http.client": request.client.host if request.client else "unknown"
        }
    ):
        try:
            _req_start = time.perf_counter()
            response = await call_next(request)

            # Record feature usage based on endpoint
            if request.url.path.startswith("/geometric"):
                telemetry.record_feature_usage("geometric_algebra_api")
            elif request.url.path.startswith("/agent"):
                telemetry.record_feature_usage("agent_mode_api")
            elif request.url.path.startswith("/memory"):
                telemetry.record_feature_usage("memory_api")
            elif request.url.path.startswith("/quantum"):
                telemetry.record_feature_usage("quantum_api")

            # Check per-endpoint performance budget
            try:
                from src.observability.performance_budgets import check_budget_violation
                _duration_ms = (time.perf_counter() - _req_start) * 1000
                _violation = check_budget_violation(
                    request.method,
                    str(request.url.path),
                    _duration_ms,
                    response.status_code >= 500,
                )
                if _violation:
                    logger.warning("PERF BUDGET VIOLATION: %s", _violation)
            except Exception:
                pass

            return response
        except Exception as e:
            # Record error explicitly before re-raising for visibility
            logger.error("Request processing error: %s", e)
            raise


# HIGH-5: NoSQL Injection Prevention - Input Validation Helper
def validate_identifier(identifier: str, param_name: str) -> str:
    """
    Validate identifiers (node_id, repo_id, bridge_id, etc.) to prevent injection attacks.

    HIGH-5: NoSQL injection prevention pattern
    - Alphanumeric + hyphens/underscores only
    - Max length: 64 characters
    - No path traversal sequences
    - No special characters that could enable injection

    Args:
        identifier: The identifier string to validate
        param_name: Name of the parameter (for error messages)

    Returns:
        Validated identifier string

    Raises:
        HTTPException: If identifier is invalid (400 Bad Request)
    """
    import re

    if not identifier or len(identifier) > 64:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name}: must be 1-64 characters"
        )

    if not re.match(r'^[a-zA-Z0-9_-]+$', identifier):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name}: alphanumeric, hyphens, underscores only"
        )

    # Block path traversal attempts
    if '..' in identifier or '/' in identifier or '\\' in identifier:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name}: path traversal detected"
        )

    return identifier


# Include AuMemManager API routes if available
if AUMEMMANAGER_AVAILABLE and AUMEMMANAGER_ROUTER:
    try:
        app.include_router(AUMEMMANAGER_ROUTER)
        logger.info("AuMemManager API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate AuMemManager API routes: %s", e)
        AUMEMMANAGER_AVAILABLE = False

# Include Memory Retrieval API routes if available
if MEMORY_RETRIEVAL_AVAILABLE and MEMORY_RETRIEVAL_ROUTER:
    try:
        app.include_router(MEMORY_RETRIEVAL_ROUTER)
        logger.info("Memory Retrieval API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Memory Retrieval API routes: %s", e)
        MEMORY_RETRIEVAL_AVAILABLE = False

# Include Data Guardian API routes if available
if DATA_GUARDIAN_AVAILABLE and DATA_GUARDIAN_ROUTER:
    try:
        app.include_router(DATA_GUARDIAN_ROUTER)
        logger.info("Data Guardian API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Data Guardian API routes: %s", e)
        DATA_GUARDIAN_AVAILABLE = False

# Include Insight Ledger API routes if available
if INSIGHT_LEDGER_AVAILABLE and INSIGHT_LEDGER_ROUTER:
    try:
        app.include_router(INSIGHT_LEDGER_ROUTER)
        if initialize_ledger:
            _ledger_instance = initialize_ledger(storage_path="./data/insight_ledger")
            try:
                _integrity = _ledger_instance.verify_integrity()
                if _integrity.get("chain_intact"):
                    logger.info(
                        "Ledger integrity verified on startup: %d entries",
                        _integrity.get("verified_entries", 0),
                    )
                else:
                    logger.warning(
                        "Ledger integrity check FAILED on startup: %d failed entries; errors: %s",
                        len(_integrity.get("failed_entries", [])),
                        _integrity.get("errors", []),
                    )
            except Exception as _integrity_err:
                logger.warning("Ledger integrity check raised an exception on startup: %s", _integrity_err)
        logger.info("Insight Ledger API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Insight Ledger API routes: %s", e)
        INSIGHT_LEDGER_AVAILABLE = False

# Include Quantum Simulator API routes if available
if QUANTUM_SIMULATOR_AVAILABLE and QUANTUM_SIMULATOR_ROUTER:
    try:
        app.include_router(QUANTUM_SIMULATOR_ROUTER)
        logger.info("Quantum Simulator API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Quantum Simulator API routes: %s", e)
        QUANTUM_SIMULATOR_AVAILABLE = False

# Include Memory Retrieval API routes if available
if MEMORY_RETRIEVAL_AVAILABLE and MEMORY_RETRIEVAL_ROUTER:
    try:
        app.include_router(MEMORY_RETRIEVAL_ROUTER)
        logger.info("Memory Retrieval API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Memory Retrieval API routes: %s", e)
        MEMORY_RETRIEVAL_AVAILABLE = False

# Include RD Productization Pipeline API routes if available
if RD_PIPELINE_AVAILABLE:
    try:
        app.include_router(rd_router)
        logger.info("RD Productization Pipeline API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate RD Pipeline API routes: %s", e)
        RD_PIPELINE_AVAILABLE = False

# Include HR System API routes (staffing & character generation)
try:
    from modules.hr_system.api.hr_routes import router as hr_system_router
    app.include_router(hr_system_router)
    logger.info("✅ HR System API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ HR System not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate HR System API routes: %s", e)

# Include Cross-Repo Collaboration API routes
try:
    from src.collab.api_routes import router as collab_router
    app.include_router(collab_router)
    logger.info("Cross-Repo Collaboration API routes integrated successfully")
except ImportError as e:
    logger.warning("Cross-Repo Collaboration not available: %s", e)
except Exception as e:
    logger.error("Failed to integrate Cross-Repo Collaboration API routes: %s", e)

# Include Subroutine API routes
try:
    from src.subroutines.api import router as subroutine_router
    from src.subroutines.api_enhanced import router as subroutine_enhanced_router
    app.include_router(subroutine_router)
    app.include_router(subroutine_enhanced_router)
    logger.info("Subroutine API routes integrated successfully (base + enhanced)")
    SUBROUTINE_AVAILABLE = True
except ImportError as e:
    logger.warning("Subroutine system not available: %s", e)
    SUBROUTINE_AVAILABLE = False
except Exception as e:
    logger.error("Failed to integrate Subroutine API routes: %s", e)
    SUBROUTINE_AVAILABLE = False

# Include Event Coordination API routes if available
if EVENT_COORDINATION_AVAILABLE and EVENT_COORDINATION_ROUTER:
    try:
        app.include_router(EVENT_COORDINATION_ROUTER)
        logger.info("Event Coordination API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Event Coordination API routes: %s", e)
        EVENT_COORDINATION_AVAILABLE = False

# Include Fleet Bridge API routes if available
if FLEET_BRIDGE_AVAILABLE and FLEET_BRIDGE_ROUTER:
    try:
        app.include_router(FLEET_BRIDGE_ROUTER)
        logger.info("Fleet Bridge API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Fleet Bridge API routes: %s", e)
        FLEET_BRIDGE_AVAILABLE = False

# Include Relay Manager API routes if available
if RELAY_MANAGER_AVAILABLE and RELAY_MANAGER_ROUTER:
    try:
        app.include_router(RELAY_MANAGER_ROUTER)
        logger.info("Relay Manager API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Relay Manager API routes: %s", e)
        RELAY_MANAGER_AVAILABLE = False

# Include Synergy Dashboard API routes
try:
    from src.synergy import synergy_router, dashboard_router
    app.include_router(synergy_router)
    app.include_router(dashboard_router)
    logger.info("Synergy Dashboard API routes integrated successfully")
except ImportError as e:
    logger.warning("Synergy Dashboard not available: %s", e)
except Exception as e:
    logger.error("Failed to integrate Synergy Dashboard API routes: %s", e)

# Include Resilience Sentinel API routes
try:
    from modules.resilience_sentinel.api import router as sentinel_router
    app.include_router(sentinel_router)
    logger.info("✅ Resilience Sentinel API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ Resilience Sentinel not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate Resilience Sentinel routes: %s", e)

# Include Monitoring Dashboard API routes
try:
    from src.monitoring.dashboard_api import create_monitoring_router
    monitoring_router = create_monitoring_router()
    if monitoring_router:
        app.include_router(monitoring_router)
        logger.info("✅ Monitoring Dashboard API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ Monitoring Dashboard not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate Monitoring Dashboard routes: %s", e)

# Include GUMAS Ethics API routes
try:
    from modules.gumas.api import router as gumas_router
    app.include_router(gumas_router)
    logger.info("✅ GUMAS Ethics API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ GUMAS Ethics not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate GUMAS Ethics routes: %s", e)

# Include Authentication (OAuth2/RBAC) API routes
try:
    from src.security.auth_routes import router as auth_router
    app.include_router(auth_router)
    logger.info("✅ Authentication (OAuth2/RBAC) API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ Authentication routes not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate Authentication API routes: %s", e)

# Include R2 Telemetry API routes
try:
    from api.r2_telemetry_routes import router as r2_telemetry_router
    app.include_router(r2_telemetry_router)

    # Crew Agents router inclusion (Phase 3)
    app.include_router(crew_router)
    logger.info("✅ R2 Telemetry API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ R2 Telemetry routes not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate R2 Telemetry routes: %s", e)

# Include L2 Meta-Agent Bridge API routes
try:
    from src.api.l2_meta_agent_api import router as l2_meta_agent_router
    app.include_router(l2_meta_agent_router)
    logger.info("✅ L2 Meta-Agent Bridge API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ L2 Meta-Agent Bridge not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate L2 Meta-Agent Bridge routes: %s", e)

# Include Drift Metrics API routes (Phase 2: Drift Prometheus Exporter)
try:
    from src.observability.drift_metrics_api import router as drift_metrics_router
    app.include_router(drift_metrics_router)
    logger.info("✅ Drift Metrics API routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ Drift Metrics routes not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate Drift Metrics routes: %s", e)

# Include Playground backend routes
try:
    from src.playground import playground_router

    app.include_router(playground_router)
    logger.info("✅ Playground backend routes integrated successfully")
except ImportError as e:
    logger.warning("⚠️ Playground backend not available: %s", e)
except Exception as e:
    logger.error("❌ Failed to integrate Playground backend routes: %s", e)

# Initialize Ethics Gate for high-impact operations
try:
    from src.aurora.ethics import EthicsGate, GUMASEthicsClient
    ethics_gate = EthicsGate(
        client=GUMASEthicsClient(base_url="http://localhost:8000"),
        threshold=0.7
    )
    ETHICS_GATE_AVAILABLE = True
    logger.info("✅ Ethics Gate initialized successfully")
except ImportError as e:
    logger.warning("⚠️ Ethics Gate not available: %s", e)
    ETHICS_GATE_AVAILABLE = False
    ethics_gate = None
except Exception as e:
    logger.error("❌ Failed to initialize Ethics Gate: %s", e)
    ETHICS_GATE_AVAILABLE = False
    ethics_gate = None

ga = GeometricAlgebra()


# Central CSRF fastapi dependency wrapper so scanner detects protection at decorator level
def csrf_dependency(token: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI dependency enforcing CSRF token validation for state-changing endpoints."""
    verify_csrf_token(token)
    return True


def parse_multivector(expression: str, blades: dict):
    """Safely parse a multivector expression.

    Complexity reduction: Split validation and accumulation into helpers.
    """
    def _tokenize(expr: str) -> list[str]:
        return expr.split()

    def _validate(tokens: list[str], allowed: set[str]) -> None:
        for token in tokens:
            if token not in allowed and not token.isnumeric():
                raise ValueError(f"Invalid token in expression: {token}")

    def _accumulate(tokens: list[str]) -> any:
        result = None
        for token in tokens:
            if token in blades:
                result = blades[token] if result is None else result + blades[token]
            elif token.isnumeric():
                numeric = float(token)
                result = numeric if result is None else result + numeric
        return result

    tokens = _tokenize(expression)
    _validate(tokens, set(blades.keys()))
    return _accumulate(tokens)


def _sanitize_tools_info(info: Dict[str, Any]) -> Dict[str, Any]:
    """Remove non-serializable entries (e.g., callable handlers) from tools payload."""
    if not isinstance(info, dict):
        return {"tools": {}, "error": "invalid_tools_info"}
    sanitized = dict(info)
    tools = sanitized.get("tools")
    if isinstance(tools, dict):
        clean_tools = {}
        for name, tool in tools.items():
            if isinstance(tool, dict):
                clean_tools[name] = {k: v for k, v in tool.items() if k != "handler"}
            else:
                clean_tools[name] = tool
        sanitized["tools"] = clean_tools
    return sanitized


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


class AgentToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None


class AgentSessionRequest(BaseModel):
    action: Literal["create", "update", "get", "delete", "share", "fork"]
    session_id: Optional[str] = None
    state_data: Optional[Dict[str, Any]] = Field(default=None)
    share_token: Optional[str] = None

    @field_validator('state_data')
    @classmethod
    def validate_state_data(cls, v):
        """Validate state_data to prevent NoSQL/dictionary injection attacks"""
        if v is None:
            return v

        # Whitelist allowed keys to prevent injection
        ALLOWED_KEYS = {"preference", "context", "metadata", "theme", "settings", "config", "options"}
        invalid_keys = set(v.keys()) - ALLOWED_KEYS
        if invalid_keys:
            raise ValueError(f"Invalid state_data keys: {invalid_keys}. Allowed keys: {ALLOWED_KEYS}")

        # Check for dangerous injection patterns
        dangerous_patterns = ["$where", "$regex", "__proto__", "constructor", "prototype"]
        for key, value in v.items():
            key_str = str(key)
            value_str = str(value)
            if any(pattern in key_str or pattern in value_str for pattern in dangerous_patterns):
                raise ValueError("Dangerous pattern detected in state_data: potential injection attempt")

        return v


# verify_csrf inside
@app.post("/geometric/vector", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("60/minute")  # Computational operation
def create_vector(req: VectorRequest, request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    verify_csrf_token(token)
    v = ga.blades["e1"] * req.x + ga.blades["e2"] * req.y + ga.blades["e3"] * req.z

    return {"vector": str(v)}


# verify_csrf inside
@app.post("/geometric/mult", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("60/minute")  # Computational operation
@validation_handler()
def geometric_product(
    req: MultivectorRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    verify_csrf_token(token)
    a = parse_multivector(req.a, ga.blades)
    b = parse_multivector(req.b, ga.blades)
    result = ga.mult(a, b)
    return {"result": str(result)}


# verify_csrf inside
@app.post("/sonnet4/enable", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")  # State-changing operation
async def enable_sonnet4(
    req: Sonnet4EnableRequest = None,
    request: Request = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Enable Claude Sonnet 4 for all clients or specific client"""
    verify_csrf_token(token)

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

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to enable Sonnet 4")


@app.get("/sonnet4/status")
@limiter.limit("200/minute")  # Read-only operation
def get_sonnet4_status(request: Request):
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
@limiter.limit("200/minute")  # Read-only operation - client status
def get_client_sonnet4_status(client_id: str, request: Request):
    """Get Claude Sonnet 4 status for specific client"""
    return sonnet4_hub.get_client_status(client_id)


@app.get("/live")
@limiter.limit("600/minute")
def liveness(request: Request):
    """Kubernetes liveness probe — confirms the process is alive."""
    return {"status": "ok"}


@app.get("/ready")
@limiter.limit("300/minute")
def readiness(request: Request):
    """Kubernetes readiness probe — confirms the app is ready to serve traffic.

    Returns 503 if core dependencies are unavailable.
    """
    issues = []
    if not AUMEMMANAGER_AVAILABLE:
        issues.append("aumemmanager unavailable")
    if not DATA_GUARDIAN_AVAILABLE:
        issues.append("data_guardian unavailable")

    if issues:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "issues": issues,
                     "timestamp": datetime.now(timezone.utc).isoformat()},
        )
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health")
@limiter.limit("300/minute")
def health_check(request: Request):
    """Full health report — component status for monitoring dashboards."""
    return {
        "status": "healthy",
        "service": "Aurora CloudBank Symbolic API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "aumemmanager": AUMEMMANAGER_AVAILABLE,
            "data_guardian": DATA_GUARDIAN_AVAILABLE,
            "insight_ledger": INSIGHT_LEDGER_AVAILABLE,
            "quantum_simulator": QUANTUM_SIMULATOR_AVAILABLE,
            "gemini_agent": GEMINI_AGENT_AVAILABLE,
            "sonnet4": sonnet4_hub.sonnet4_config.enabled,
        },
    }


# Compatibility alias for Docker healthcheck (docker-compose points to /api/health)
@app.get("/api/health")
@limiter.limit("300/minute")
def health_check_api(request: Request):
    return health_check(request)


# ================================
# Telemetry and Observability Endpoints
# ================================

@app.get("/metrics")
@limiter.limit("300/minute")  # Prometheus scraping - frequent monitoring
def prometheus_metrics(request: Request):
    """
    Prometheus metrics endpoint for standard telemetry.

    Returns metrics in Prometheus text exposition format for:
    - Operation counts and durations
    - Feature usage statistics
    - Error counts by type

    DLP: telemetry_export_metrics
    """
    from fastapi.responses import PlainTextResponse
    try:
        telemetry = get_telemetry()
        prometheus_data = telemetry.export_prometheus_format()
        return PlainTextResponse(content=prometheus_data, media_type="text/plain; version=0.0.4")
    except Exception as e:
        logger.error("Failed to export Prometheus metrics: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/telemetry/snapshot")
@limiter.limit("60/minute")  # Snapshot retrieval - moderate usage
def telemetry_snapshot(request: Request, context_tag: Optional[str] = None):
    """
    Get current telemetry metrics snapshot.

    Returns structured metrics including:
    - Performance statistics (operation times, counts)
    - Adoption metrics (feature usage)
    - Error metrics

    Args:
        context_tag: Optional DLP context tag for lineage tracking

    DLP: telemetry_snapshot_export
    """
    try:
        telemetry = get_telemetry()
        snapshot = telemetry.get_metrics_snapshot(context_tag=context_tag)
        return {
            "timestamp": snapshot.timestamp,
            "performance_metrics": snapshot.performance_metrics,
            "adoption_metrics": snapshot.adoption_metrics,
            "error_metrics": snapshot.error_metrics,
            "context_tag": snapshot.context_tag
        }
    except Exception as e:
        logger.error("Failed to get telemetry snapshot: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# ================================
# HALO/PAS Continuity Endpoints
# ================================

@app.get("/continuity/halo_pas/status")
@limiter.limit("60/minute")  # Status check - moderate monitoring
async def get_halo_pas_status(request: Request):
    """
    Get HALO/PAS drift controller status with drift statistics.

    Returns real-time drift measurements across L1/L2/L3 timeline layers.
    DLP: halo_pas_drift_controller_v1
    Anchors: T1, SRB, EOS_SEED_ORION
    """
    if not HALO_PAS_AVAILABLE or HALO_PAS_CONTROLLER is None:
        raise HTTPException(
            status_code=503,
            detail="HALO/PAS Drift Controller not available"
        )

    try:
        status = HALO_PAS_CONTROLLER.export_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error("Failed to get HALO/PAS status: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ================================
# ChatGPT Agent Mode Endpoints
# ================================

@app.get("/agent/tools")
@limiter.limit("30/minute")  # Agent tools - moderate rate for tool discovery
async def get_agent_tools(request: Request):
    """
    Discover available agent tools and capabilities for ChatGPT Agent Mode
    Returns OpenAPI-compatible tool definitions
    """
    try:
        tools_info = await chatgpt_agent_integration.discover_tools()
        tools_info = _sanitize_tools_info(tools_info)
        return JSONResponse(content=tools_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/agent/execute", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("20/minute")  # AI inference - stricter rate limit per IP
async def execute_agent_tool(
    req: AgentToolRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute agent tool with validated parameters and Aurora symbolic anchoring
    Supports all registered tools: symbolic_processing, geometric_algebra, session_management, system_status
    """
    bound_session_id = sanitize_session_id(req.session_id)
    verify_csrf_token(token, session_id=bound_session_id)

    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name=req.tool_name,
            parameters=req.parameters,
            session_id=req.session_id
        )
        _evaluate_response(
            "agent_execute",
            result,
            metadata={"endpoint": "/agent/execute", "tool_name": req.tool_name},
            context_tag=f"agent_execute_{req.tool_name}",
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/agent/session", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")  # State-changing operation - session management
async def manage_agent_session(
    req: AgentSessionRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Manage agent session state and context persistence
    Actions: create, update, get, delete
    """
    verify_csrf_token(token, session_id=sanitize_session_id(req.session_id))

    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name="session_management",
            parameters={
                "action": req.action,
                "session_id": req.session_id,
                "state_data": req.state_data or {}
            }
        )
        # Helper: sanitize recovery suggestions (internal only)

        def sanitize_recovery_suggestions(suggestions):
            sanitized = []
            for s in suggestions:
                if not isinstance(s, str):
                    continue
                s = s.strip()
                # Remove lines that look like stack traces or file paths
                if any(x in s for x in ["Traceback", "File ", ".py", "/", "\\"]):
                    continue
                # Optionally, truncate to 200 chars
                if len(s) > 200:
                    s = s[:200] + "..."
                sanitized.append(s)
            return sanitized
        if not result.get("success", False):
            # Optionally: log result["error"] and other fields here, e.g., using logging module.
            recovery_suggestions = result.get("recovery_suggestions", [])
            safe_recovery_suggestions = sanitize_recovery_suggestions(recovery_suggestions)
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Session management failed.",
                    # Optionally log: result.get("error") server-side here.
                    "recovery_suggestions": safe_recovery_suggestions,
                },
            )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception:
        # Intentionally avoid leaking internal exception details
        raise HTTPException(status_code=500, detail="Session management failed.")


@app.get("/agent/status")
@limiter.limit("200/minute")  # Read-only operation - agent status
async def get_agent_status(request: Request):
    """Get current agent system status and health information"""
    try:
        status = await chatgpt_agent_integration.get_agent_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.websocket("/agent/stream")
async def agent_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent communication
    Supports streaming responses and persistent connections

    SECURITY: Requires authentication token in query params
    """
    # SECURITY FIX: Require authentication before accepting connection
    token = websocket.query_params.get("token")
    client_id = verify_ws_token(token) if token else None

    if not client_id:
        await websocket.close(code=1008, reason="Unauthorized: Invalid or missing token")
        return

    # Accept connection only after authentication
    await websocket.accept()

    def _initial_ws_message(cid: str) -> dict:
        return {
            "type": "connection_established",
            "timestamp": "2025-01-01T00:00:00Z",
            "symbolic_anchor": "EOS_SEED_ORION",
            "ethics_protocol": "Picard_Delta_3",
            "agent_mode": "chatgpt_agent_mode",
            "context_tag": "websocket_agent_stream",
            "client_id": cid,
        }

    async def _handle_tool_execution(websocket: WebSocket, data: dict, request_id: str) -> None:
        tool_name = data.get("tool_name", "").strip()
        if not validate_ws_tool(tool_name):
            await websocket.send_json({
                "type": "error",
                "error": f"Tool '{tool_name}' is not allowed via WebSocket",
                "request_id": request_id,
            })
            return

        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict):
            await websocket.send_json({
                "type": "error",
                "error": "Invalid parameters format (must be object)",
                "request_id": request_id,
            })
            return

        try:
            result = await chatgpt_agent_integration.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                session_id=sanitize_session_id(data.get("session_id")),
            )
            await websocket.send_json({
                "type": "tool_result",
                "result": result,
                "request_id": request_id,
            })
        except Exception:
            await websocket.send_json({
                "type": "error",
                "error": "Tool execution failed",
                "request_id": request_id,
            })

    async def _handle_ping(websocket: WebSocket, request_id: str) -> None:
        await websocket.send_json({
            "type": "pong",
            "timestamp": "2025-01-01T00:00:00Z",
            "request_id": request_id,
        })

    try:
        await websocket.send_json(_initial_ws_message(client_id))

        while True:
            data = await websocket.receive_json()
            request_id = sanitize_request_id(data.get("request_id"))
            msg_type = data.get("type")

            if msg_type == "tool_execution":
                await _handle_tool_execution(websocket, data, request_id)
            elif msg_type == "ping":
                await _handle_ping(websocket, request_id)

            else:
                await websocket.send_json({
                    "type": "error",
                    "error": "Unknown message type",
                    "supported_types": ["tool_execution", "ping"],
                    "request_id": request_id,
                })

    except Exception:
        await websocket.close(code=1011, reason="Internal error")


# ================================
# Gemini Agent Mode Endpoints
# ================================

@app.get("/agent/gemini/tools")
@limiter.limit("30/minute")  # Agent tools - Gemini tool discovery
async def get_gemini_agent_tools(request: Request):
    """
    Discover available agent tools for Gemini Agent Mode.
    """
    if not GEMINI_AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini Agent not available")
    try:
        tools_info = gemini_agent_integration.list_tools()
        return JSONResponse(content={"tools": tools_info})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to discover Gemini tools")


# verify_csrf inside
@app.post("/agent/gemini/execute", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("20/minute")  # AI inference - stricter rate limit per IP
async def execute_gemini_agent_tool(
    req: AgentToolRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute a Gemini agent tool, respecting the Symbolic Sandbox Protocol (SSP).
    A 'dry_run' parameter is used to get an impact report before committing.
    """
    verify_csrf_token(token)
    if not GEMINI_AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini Agent not available")

    try:
        result = await gemini_agent_integration.handle_tool_call(
            tool_name=req.tool_name,
            params=req.parameters
        )
        _evaluate_response(
            "agent_gemini_execute",
            result,
            metadata={"endpoint": "/agent/gemini/execute", "tool_name": req.tool_name},
            context_tag=f"gemini_execute_{req.tool_name}",
        )
        return JSONResponse(content=result)
    except ValueError as e:
        logging.error("Gemini tool not found: %s", e)
        raise HTTPException(status_code=404, detail="Tool not found")
    except Exception as e:
        logging.error("Gemini tool execution error: %s", e)
        raise HTTPException(status_code=500, detail="Tool execution failed")


# ==============================================================================
# THREAD TRANSFER BRIDGE ENDPOINTS
# ==============================================================================

@app.get("/api/thread-bridge/status")
@limiter.limit("20/minute")
async def thread_bridge_status_endpoint(request: Request):
    """
    Get Thread Transfer Bridge status

    Returns current bridge status, drift metrics, and companion thread health.
    """
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )

    try:
        bridge = get_bridge_instance()
        status = bridge.get_status()

        return {
            "success": True,
            "status": status.status,
            "drift": status.drift,
            "drift_alert_level": status.drift_alert_level,
            "companion_threads": status.companion_threads,
            "synchronized_threads": status.synchronized_threads,
            "last_handshake": status.last_handshake.isoformat() if status.last_handshake else None,
            "continuity_seal": status.continuity_seal,
            "anchor_seed": status.anchor_seed,
            "ethics_protocol": status.ethics_protocol,
            "context_tag": "thread_bridge_status",
            "timestamp": "2025-10-28T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


class HandshakeRequest(BaseModel):
    """Request model for thread handshake"""
    thread_id: str


# verify_csrf inside
@app.post("/api/thread-bridge/handshake", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def thread_bridge_handshake_endpoint(
    request: HandshakeRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Initiate handshake sequence with a companion thread

    Executes the 5-stage handshake: INIT → VERIFY_ANCHOR → LOCK_DRIFT →
    ALIGN_ETHICS → SYNC_COMPLETE
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )

    try:
        bridge = get_bridge_instance()
        result = bridge.handshake(request.thread_id)

        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result.get("error"),
                    "stages": result.get("stages", []),
                    "context_tag": "thread_bridge_handshake_failed"
                }
            )

        return {
            "success": True,
            "thread_id": result["thread_id"],
            "timestamp": result["timestamp"].isoformat(),
            "stages": result["stages"],
            "context_tag": "thread_bridge_handshake_success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


class ValidateRequest(BaseModel):
    """Request model for continuity validation"""
    source: str
    target: str


# verify_csrf inside
@app.post("/api/thread-bridge/validate", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("30/minute")
async def thread_bridge_validate_endpoint(
    request: ValidateRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate continuity between two threads before transfer

    Checks anchor alignment, drift levels, and ethics compatibility.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )

    try:
        bridge = get_bridge_instance()
        validation = bridge.validate_continuity(request.source, request.target)

        return {
            "success": True,
            "valid": validation.get("valid"),
            "source": validation["source"],
            "target": validation["target"],
            "timestamp": validation["timestamp"].isoformat(),
            "checks": validation["checks"],
            "error": validation.get("error"),
            "context_tag": "thread_bridge_validation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/thread-bridge/companions")
@limiter.limit("30/minute")
async def thread_bridge_companions_endpoint(request: Request):
    """
    Get list of all companion threads with their status

    Returns detailed information about each companion thread including
    alignment status, drift levels, and last sync timestamp.
    """
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )

    try:
        bridge = get_bridge_instance()
        companions = bridge.get_companion_threads()

        return {
            "success": True,
            "companion_threads": companions,
            "count": len(companions),
            "anchor_seed": bridge.capsule.get("anchor_seed"),
            "context_tag": "thread_bridge_companions"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


class TransferRequest(BaseModel):
    """Request model for context transfer"""
    source: str
    target: str
    context_data: Dict[str, Any]


# verify_csrf inside
@app.post("/api/thread-bridge/transfer", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def thread_bridge_transfer_endpoint(
    request: TransferRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Transfer context from source thread to target thread

    Performs full validation, ethics checks, and secure state transfer
    between companion threads.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )

    try:
        bridge = get_bridge_instance()
        result = bridge.transfer_context(
            source=request.source,
            target=request.target,
            context_data=request.context_data
        )

        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result.get("error"),
                    "validation": result.get("validation"),
                    "context_tag": "thread_bridge_transfer_failed"
                }
            )

        return {
            "success": True,
            "source": result["source"],
            "target": result["target"],
            "timestamp": result["timestamp"].isoformat(),
            "bytes_transferred": result["bytes_transferred"],
            "drift_delta": result["drift_delta"],
            "continuity_seal": result["continuity_seal"],
            "context_tag": "thread_bridge_transfer_success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# THREAD TRANSFER BRIDGE V2 ENDPOINTS
# ============================================================================

# Pydantic models for v2 endpoints
class NodeRegisterRequest(BaseModel):
    hostname: str
    port: int
    region: str
    capacity: int
    version: str = "2.0.0"
    capabilities: Optional[list] = None


class DriftPredictionRequest(BaseModel):
    drift_velocity: float
    drift_acceleration: float
    handshake_count: int
    average_handshake_duration: float
    failed_handshake_ratio: float
    time_of_day: float
    day_of_week: int
    thread_age_hours: float
    anchor_changes: int
    sync_frequency: float
    node_count: int
    thread_id: str


class LayerBridgeRequest(BaseModel):
    bridge_id: str
    layer: str  # L1, L2, or L3
    source_id: str
    target_id: str
    thread_id: str


class RepositoryRegisterRequest(BaseModel):
    repo_id: str
    repo_path: str
    branch: str = "main"


# ------------------------------------------------------------------------
# Phase 1: Distributed Node Management (6 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/nodes/register", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("30/minute")
async def v2_register_node(
    node_request: NodeRegisterRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Register a new bridge node in the distributed constellation.

    Requires: hostname, port, region, capacity, version
    Returns: Node metadata with unique node_id
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        registry = get_node_registry()
        node = await registry.register_node(
            hostname=node_request.hostname,
            port=node_request.port,
            region=node_request.region,
            capacity=node_request.capacity,
            version=node_request.version,
            capabilities=node_request.capabilities or []
        )

        return {
            "success": True,
            "node": {
                "node_id": node.node_id,
                "hostname": node.hostname,
                "port": node.port,
                "region": node.region,
                "capacity": node.capacity,
                "status": node.status.value,
                "version": node.version,
                "anchor_hash": node.anchor_hash
            },
            "context_tag": "v2_node_registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/v2/nodes/{node_id}", dependencies=[Depends(security)])
@limiter.limit("30/minute")
async def v2_unregister_node(
    node_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Unregister a bridge node from the constellation.

    Gracefully removes node from registry and load balancing pool.

    SECURITY: CSRF protection via token validation (HIGH-4 remediation)
    ETHICS: Ethics gate evaluation before node deletion
    """
    # HIGH-4: Verify CSRF token before node deletion
    verify_csrf_token(token)

    # HIGH-5: Validate node_id parameter to prevent injection
    node_id = validate_identifier(node_id, "node_id")

    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    # Ethics Gate: Evaluate node deletion action
    if ETHICS_GATE_AVAILABLE and ethics_gate:
        try:
            from src.aurora.ethics import EthicsViolation

            action = {
                "type": "delete_node",
                "node_id": node_id,
                "resource": "bridge_node",
                "operation": "unregister"
            }

            context = {
                "agent_id": "api_user",
                "route": f"/api/v2/nodes/{node_id}",
                "source": "api_endpoint",
                "method": "DELETE"
            }

            verdict = await ethics_gate.evaluate(action, context)

            if not verdict.allowed:
                # Log detailed reason server-side
                logger.warning(
                    "Ethics gate blocked node deletion: %s (score=%.2f, node_id=%s)",
                    verdict.reason,
                    verdict.score,
                    node_id,
                    extra={
                        "node_id": node_id,
                        "verdict": verdict.to_dict(),
                        "aurora_module": "api_v2_nodes"
                    }
                )
                # Return generic error to client
                raise HTTPException(
                    status_code=403,
                    detail="Node deletion not permitted by ethics policy"
                )

            # Log approval
            logger.info(
                "Ethics gate approved node deletion: node_id=%s (score=%.2f)",
                node_id,
                verdict.score,
                extra={
                    "node_id": node_id,
                    "verdict": verdict.to_dict(),
                    "aurora_module": "api_v2_nodes"
                }
            )

        except EthicsViolation as e:
            # Block on ethics violation
            logger.warning(
                "Ethics violation on node deletion: %s",
                e.message,
                extra={
                    "node_id": node_id,
                    "verdict": e.verdict.to_dict() if e.verdict else {},
                    "aurora_module": "api_v2_nodes"
                }
            )
            raise HTTPException(
                status_code=403,
                detail="Node deletion not permitted by ethics policy"
            )
        except Exception as e:
            # Log but don't block on evaluation errors (already handled in ethics_gate)
            logger.error(
                "Ethics evaluation error for node deletion: %s",
                e,
                extra={"node_id": node_id, "aurora_module": "api_v2_nodes"},
                exc_info=True
            )

    try:
        registry = get_node_registry()
        success = await registry.unregister_node(node_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

        return {
            "success": True,
            "node_id": node_id,
            "context_tag": "v2_node_unregistered"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/nodes/{node_id}/health")
@limiter.limit("60/minute")
async def v2_get_node_health(node_id: str, request: Request):
    """
    Get detailed health status for a specific node.

    Returns: 4-metric health check (heartbeat, API, anchor, drift)
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        registry = get_node_registry()
        node = await registry.get_node(node_id)

        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

        return {
            "success": True,
            "node_id": node.node_id,
            "status": node.status.value,
            "is_healthy": node.is_healthy(),
            "current_load": node.current_load,
            "available_capacity": node.available_capacity(),
            "load_percentage": node.load_percentage(),
            "last_heartbeat": node.last_heartbeat.isoformat(),
            "context_tag": "v2_node_health"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/nodes")
@limiter.limit("60/minute")
async def v2_list_nodes(request: Request):
    """
    List all registered bridge nodes.

    Returns: Array of node metadata with current status and load
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        registry = get_node_registry()
        nodes = await registry.get_online_nodes()

        return {
            "success": True,
            "count": len(nodes),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "hostname": node.hostname,
                    "port": node.port,
                    "region": node.region,
                    "status": node.status.value,
                    "current_load": node.current_load,
                    "capacity": node.capacity,
                    "available_capacity": node.available_capacity(),
                    "version": node.version
                }
                for node in nodes
            ],
            "context_tag": "v2_nodes_listed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/cluster/health")
@limiter.limit("30/minute")
async def v2_get_cluster_health(request: Request):
    """
    Get overall cluster health status.

    Returns: Aggregate metrics across all nodes
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        registry = get_node_registry()
        cluster_health = await registry.get_cluster_health()

        return {
            "success": True,
            "cluster_health": cluster_health,
            "context_tag": "v2_cluster_health"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/consensus/elect", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def v2_trigger_election(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Trigger a Raft consensus leader election.

    WARNING: Use only for testing or emergency recovery.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    return {
        "success": False,
        "message": "Consensus election must be triggered via node registry",
        "context_tag": "v2_consensus_election_unavailable"
    }


# ------------------------------------------------------------------------
# Phase 2: Cross-Repository Sync (4 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/repos/register", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("20/minute")
async def v2_register_repository(
    request: RepositoryRegisterRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Register a Git repository for cross-repo synchronization.

    Enables anchor propagation and thread continuity across repos.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        synchronizer = get_repository_synchronizer()
        repo_info = await synchronizer.register_repository(
            repo_id=request.repo_id,
            repo_path=request.repo_path,
            branch=request.branch
        )

        return {
            "success": True,
            "repository": {
                "repo_id": repo_info.repo_id,
                "repo_path": repo_info.repo_path,
                "branch": repo_info.branch,
                "status": repo_info.status.value,
                "last_sync": repo_info.last_sync.isoformat() if repo_info.last_sync else None
            },
            "context_tag": "v2_repo_registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/repos/{repo_id}/sync", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def v2_sync_repository(
    repo_id: str,
    direction: str = "bidirectional",
    request: Request = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Synchronize a registered repository.

    Pulls latest changes and pushes local anchors.
    Direction: push, pull, or bidirectional
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        synchronizer = get_repository_synchronizer()

        # Map string to SyncDirection enum
        from modules.reflective_autonomy.thread_transfer.v2 import SyncDirection
        direction_map = {
            "push": SyncDirection.PUSH,
            "pull": SyncDirection.PULL,
            "bidirectional": SyncDirection.BIDIRECTIONAL
        }
        sync_dir = direction_map.get(direction.lower(), SyncDirection.BIDIRECTIONAL)

        result = await synchronizer.sync_repository(repo_id, sync_dir)

        return {
            "success": result["success"],
            "repo_id": repo_id,
            "direction": direction,
            "message": result.get("message", "Sync completed"),
            "context_tag": "v2_repo_synced"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/bridges/cross-repo", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def v2_create_cross_repo_bridge(
    source_repo: str,
    target_repo: str,
    thread_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a cross-repository bridge for thread continuity.

    Initiates 7-stage handshake between repositories.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        cross_repo_bridge = get_cross_repository_bridge()
        # Generate a unique bridge id for this cross-repo bridge
        import uuid as _uuid
        new_bridge_id = _uuid.uuid4().hex

        bridge_obj = await cross_repo_bridge.create_bridge(
            bridge_id=new_bridge_id,
            source_repo_id=source_repo,
            target_repo_id=target_repo,
            thread_id=thread_id
        )

        return {
            "success": True,
            "bridge_id": bridge_obj.bridge_id if hasattr(bridge_obj, "bridge_id") else new_bridge_id,
            "source_repo": source_repo,
            "target_repo": target_repo,
            "thread_id": thread_id,
            "context_tag": "v2_cross_repo_bridge_created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/bridges/{bridge_id}/handshake", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def v2_execute_cross_repo_handshake(
    bridge_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute 7-stage cross-repository handshake.

    Completes thread transfer between repositories with full validation.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        cross_repo_bridge = get_cross_repository_bridge()

        result = await cross_repo_bridge.execute_handshake(bridge_id)

        return {
            "success": result["success"],
            "bridge_id": bridge_id,
            "stages_completed": result.get("stages_completed", 0),
            "drift_percentage": result.get("drift_percentage", 0.0),
            "context_tag": "v2_cross_repo_handshake_executed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# ------------------------------------------------------------------------
# Phase 3: Drift Prediction (5 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/drift/predict", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("30/minute")
async def v2_predict_drift(
    drift_request: DriftPredictionRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Predict future drift based on current features.

    Uses LSTM model with 11-feature input for 24-hour prediction.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        predictor = get_drift_predictor()

        features = DriftFeatures(
            drift_velocity=drift_request.drift_velocity,
            drift_acceleration=drift_request.drift_acceleration,
            handshake_count=drift_request.handshake_count,
            average_handshake_duration=drift_request.average_handshake_duration,
            failed_handshake_ratio=drift_request.failed_handshake_ratio,
            time_of_day=drift_request.time_of_day,
            day_of_week=drift_request.day_of_week,
            thread_age_hours=drift_request.thread_age_hours,
            anchor_changes=drift_request.anchor_changes,
            sync_frequency=drift_request.sync_frequency,
            node_count=drift_request.node_count
        )

        prediction = await predictor.predict_drift(features, drift_request.thread_id)

        return {
            "success": True,
            "thread_id": drift_request.thread_id,
            "predicted_drift": prediction.predicted_drift,
            "severity": prediction.severity.value,
            "confidence": prediction.confidence.value,
            "prediction_horizon_hours": prediction.prediction_horizon_hours,
            "recommendations": prediction.recommendations,
            "context_tag": "v2_drift_predicted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/drift/patterns")
@limiter.limit("30/minute")
async def v2_analyze_patterns(request: Request):
    """
    Analyze historical drift patterns.

    Returns detected patterns: stable, trending, cyclical, volatile, anomalous
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        analyzer = get_pattern_analyzer()
        patterns = await analyzer.analyze_patterns()

        return {
            "success": True,
            "patterns": [
                {
                    "pattern_type": p.pattern_type.value,
                    "confidence": p.confidence,
                    "description": p.description,
                    "metadata": p.metadata
                }
                for p in patterns
            ],
            "context_tag": "v2_patterns_analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/drift/observe", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("60/minute")
async def v2_record_observation(
    drift: float,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Record a drift observation for pattern analysis.

    Adds data point to historical drift tracking.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        from datetime import datetime
        analyzer = get_pattern_analyzer()
        analyzer.add_observation(datetime.now(), drift)

        return {
            "success": True,
            "drift": drift,
            "timestamp": datetime.now().isoformat(),
            "context_tag": "v2_observation_recorded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/drift/accuracy")
@limiter.limit("30/minute")
async def v2_get_prediction_accuracy(request: Request):
    """
    Get prediction accuracy metrics.

    Returns: Historical accuracy statistics for drift predictions
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        predictor = get_drift_predictor()
        accuracy = await predictor.get_prediction_accuracy()

        return {
            "success": True,
            "accuracy": accuracy,
            "context_tag": "v2_prediction_accuracy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/corrections/apply", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def v2_apply_correction(
    thread_id: str,
    predicted_drift: float,
    current_drift: float,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Apply auto-correction actions based on drift prediction.

    Evaluates correction strategies and executes if drift exceeds threshold.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        corrector = get_auto_corrector()

        actions = await corrector.evaluate_correction(
            predicted_drift=predicted_drift,
            current_drift=current_drift,
            thread_id=thread_id,
            metadata={}
        )

        return {
            "success": True,
            "thread_id": thread_id,
            "actions_recommended": len(actions),
            "actions": [
                {
                    "strategy": action.strategy.value,
                    "priority": action.priority,
                    "description": action.description
                }
                for action in actions
            ],
            "context_tag": "v2_corrections_evaluated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# ------------------------------------------------------------------------
# Phase 4: Layer Management (6 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/layers/bridge", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("20/minute")
async def v2_create_layer_bridge(
    layer_request: LayerBridgeRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a multi-layer bridge (L1/L2/L3).

    L1: Thread-to-thread (5 stages, 0.0% max drift)
    L2: Repo-to-repo (7 stages, 0.1% max drift)
    L3: Cluster-to-cluster (9 stages, 0.5% max drift, PKI required)
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        layer_manager = get_layer_manager()

        # Map string to BridgeLayer enum
        layer_map = {
            "L1": BridgeLayer.L1,
            "L2": BridgeLayer.L2,
            "L3": BridgeLayer.L3
        }
        layer = layer_map.get(layer_request.layer.upper())

        if not layer:
            raise HTTPException(status_code=400, detail=f"Invalid layer: {layer_request.layer}")

        bridge = await layer_manager.create_bridge(
            bridge_id=layer_request.bridge_id,
            layer=layer,
            source_id=layer_request.source_id,
            target_id=layer_request.target_id,
            thread_id=layer_request.thread_id
        )

        return {
            "success": True,
            "bridge": {
                "bridge_id": bridge.bridge_id,
                "layer": bridge.layer.value,
                "source_id": bridge.source_id,
                "target_id": bridge.target_id,
                "thread_id": bridge.thread_id,
                "status": bridge.status
            },
            "context_tag": "v2_layer_bridge_created"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/layers/{bridge_id}/handshake", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def v2_execute_layered_handshake(
    bridge_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute layer-specific handshake protocol.

    Completes all stages for the bridge's layer with proper validation.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        layer_manager = get_layer_manager()

        result = await layer_manager.execute_layered_handshake(bridge_id)

        return {
            "success": result["success"],
            "bridge_id": bridge_id,
            "stages_completed": result.get("stages_completed", 0),
            "drift_percentage": result.get("drift_percentage", 0.0),
            "context_tag": "v2_layered_handshake_executed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/layers/validate", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("30/minute")
async def v2_validate_hierarchy(
    thread_id: str,
    strict_mode: bool = False,
    request: Request = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate multi-layer hierarchy for a thread.

    Checks: layer completion, drift tolerance, PKI (L3), dependencies
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        layer_manager = get_layer_manager()
        validator = get_hierarchy_validator()

        bridges = layer_manager.list_bridges(thread_id=thread_id)
        report = await validator.validate_hierarchy(
            bridges=bridges,
            thread_id=thread_id,
            strict_mode=strict_mode
        )

        return {
            "success": True,
            "valid": report.valid,
            "thread_id": thread_id,
            "layer_status": report.layer_status,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "layer": issue.layer,
                    "code": issue.code,
                    "message": issue.message
                }
                for issue in report.issues
            ],
            "context_tag": "v2_hierarchy_validated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/layers/bridges")
@limiter.limit("60/minute")
async def v2_list_layer_bridges(thread_id: Optional[str] = None, layer: Optional[str] = None, request: Request = None):
    """
    List all layer bridges, optionally filtered by thread_id or layer.

    Returns array of bridge metadata with current status.
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        layer_manager = get_layer_manager()

        # Parse layer filter if provided
        layer_enum = None
        if layer:
            layer_map = {
                "L1": BridgeLayer.L1,
                "L2": BridgeLayer.L2,
                "L3": BridgeLayer.L3
            }
            layer_enum = layer_map.get(layer.upper())

        bridges = layer_manager.list_bridges(thread_id=thread_id, layer=layer_enum)

        return {
            "success": True,
            "count": len(bridges),
            "bridges": [
                {
                    "bridge_id": b.bridge_id,
                    "layer": b.layer.value,
                    "source_id": b.source_id,
                    "target_id": b.target_id,
                    "thread_id": b.thread_id,
                    "status": b.status,
                    "created_at": b.created_at.isoformat() if hasattr(b, 'created_at') else None
                }
                for b in bridges
            ],
            "context_tag": "v2_layer_bridges_listed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v2/layers/statistics")
@limiter.limit("60/minute")
async def v2_get_layer_statistics(request: Request):
    """
    Get layer management statistics.

    Returns: Counts by layer, status, and aggregate metrics
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        layer_manager = get_layer_manager()
        stats = layer_manager.get_layer_statistics()

        return {
            "success": True,
            "statistics": stats,
            "context_tag": "v2_layer_statistics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# verify_csrf inside
@app.post("/api/v2/layers/cascade-validate", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("20/minute")
async def v2_cascade_validate(
    thread_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform cascading validation across all layers for a thread.

    Validates L1 → L2 → L3 dependencies and cross-layer consistency.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )

    try:
        layer_manager = get_layer_manager()
        validator = get_hierarchy_validator()

        bridges = layer_manager.list_bridges(thread_id=thread_id)
        report = await validator.validate_hierarchy(
            bridges=bridges,
            thread_id=thread_id,
            strict_mode=True  # Cascade validation always strict
        )

        return {
            "success": True,
            "valid": report.valid,
            "thread_id": thread_id,
            "cascade_result": "PASS" if report.valid else "FAIL",
            "layer_status": report.layer_status,
            "critical_issues": [
                {
                    "layer": issue.layer,
                    "code": issue.code,
                    "message": issue.message
                }
                for issue in report.issues
                if issue.severity.value == "critical"
            ],
            "context_tag": "v2_cascade_validated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# Example quantum endpoint (stub)
# @app.post(  # verify_csrf inside"/quantum/vsa")
# @app.post(  # verify_csrf inside"/quantum/vsa")

# def quantum_vsa_endpoint(...):
#     ...


# ------------------------------------------------------------------------
# PatchWeaver: Ethics-Gated State Patching (Admin Only)
# ------------------------------------------------------------------------

# Import PatchWeaver components
try:
    from src.aurora.patching.patchweaver import PatchWeaver
    from src.core.native_dlp_export import NativeDLPTracker
    from src.monitoring.ethics_engine import EthicsEngine
    import json
    from pathlib import Path

    PATCHWEAVER_AVAILABLE = True

    # Initialize PatchWeaver state backend (file-based for v1)
    PATCHWEAVER_STATE_FILE = Path("./data/patchweaver_state.json")
    PATCHWEAVER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _load_patchweaver_state() -> Dict[str, Any]:
        """Load PatchWeaver state from JSON file"""
        if PATCHWEAVER_STATE_FILE.exists():
            try:
                return json.loads(PATCHWEAVER_STATE_FILE.read_text())
            except Exception as e:
                logger.error("Failed to load PatchWeaver state: %s", e)
                return {}
        return {}

    def _save_patchweaver_state(state: Dict[str, Any]) -> None:
        """Save PatchWeaver state to JSON file"""
        try:
            PATCHWEAVER_STATE_FILE.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logger.error("Failed to save PatchWeaver state: %s", e)
            raise

    # Initialize PatchWeaver instance with ethics gate
    _patchweaver_ethics = EthicsEngine()
    _patchweaver_dlp = NativeDLPTracker()
    _patchweaver = PatchWeaver(
        load_state=_load_patchweaver_state,
        save_state=_save_patchweaver_state,
        ethics_gate=_patchweaver_ethics,
        dlp_tracker=_patchweaver_dlp
    )

    logger.info("PatchWeaver initialized successfully")

except ImportError as e:
    logger.warning("PatchWeaver not available: %s", e)
    PATCHWEAVER_AVAILABLE = False
except Exception as e:
    logger.error("Failed to initialize PatchWeaver: %s", e)
    PATCHWEAVER_AVAILABLE = False


class PatchWeaverRequest(BaseModel):
    """Request model for PatchWeaver operations"""
    patch: Dict[str, Any] = Field(
        ...,
        description="Patch operations with 'set' and/or 'delete' keys"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context for ethics validation and DLP tracking"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patch": {
                    "set": {
                        "config/setting": "value",
                        "simulation/status": "active"
                    },
                    "delete": [
                        "deprecated_key"
                    ]
                },
                "context": {
                    "agent_id": "admin_user",
                    "context_tag": "config_update",
                    "reason": "Update production configuration"
                }
            }
        }
    )


@app.post("/admin/patchweaver/apply", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("5/minute")  # Strict rate limiting for admin operations
async def apply_patchweaver_patch(
    req: PatchWeaverRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Apply a state patch with ethics validation and DLP tracking.

    **Admin-only endpoint** - Requires authentication, CSRF token, and strict rate limiting.

    Patch format:
    - `set`: Dictionary of path/value pairs to set (creates nested structures)
    - `delete`: List of paths to delete (idempotent)

    Path format: Use `/` to separate nested keys, e.g., `"config/setting"` → `state["config"]["setting"]`

    Returns:
    - `applied`: Whether patch was successfully applied
    - `reason`: "ok" or error/block reason
    - `before_hash`: State hash before patch
    - `after_hash`: State hash after patch
    - `modified_paths`: List of paths that were modified
    - `timestamp`: ISO timestamp of operation

    Security:
    - All patches validated by ethics gate
    - Full DLP audit trail with anchors (T1/SRB, EOS_SEED_ORION, Picard_Delta_3)
    - CSRF protection required
    - Strict rate limiting (5 requests/minute)
    """
    verify_csrf_token(token)

    if not PATCHWEAVER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PatchWeaver service not available"
        )

    try:
        # Ensure agent_id is in context for ethics validation
        if "agent_id" not in req.context:
            req.context["agent_id"] = "api_user"

        # Apply patch via PatchWeaver
        result = _patchweaver.apply_patch(
            patch=req.patch,
            context=req.context
        )

        # Return result as JSON
        return {
            "success": result.applied,
            **result.to_dict()
        }

    except Exception as e:
        logger.error("PatchWeaver operation failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/admin/patchweaver/history", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("10/minute")
async def get_patchweaver_history(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security),
    limit: Optional[int] = 20
):
    """
    Get history of PatchWeaver operations.

    **Admin-only endpoint** - Returns recent patch operations with full DLP metadata.

    Query parameters:
    - `limit`: Maximum number of operations to return (default: 20)

    Returns list of patch operations with:
    - Operation metadata
    - DLP tags and anchors
    - Modified paths
    - Hashes before/after
    - Timestamps
    """
    verify_csrf_token(token)

    if not PATCHWEAVER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PatchWeaver service not available"
        )

    try:
        history = _patchweaver.get_patch_history()

        # Apply limit
        if limit:
            history = history[-limit:]

        return {
            "success": True,
            "count": len(history),
            "operations": history
        }

    except Exception as e:
        logger.error("Failed to retrieve PatchWeaver history: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.post("/admin/patchweaver/verify", dependencies=[Depends(security), Depends(verify_csrf_token)])
@limiter.limit("20/minute")
async def verify_patchweaver_state(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security),
    expected_hash: str = None
):
    """
    Verify current state hash against expected value.

    **Admin-only endpoint** - Validates state integrity.

    Request body:
    - `expected_hash`: SHA256 hash to verify against

    Returns:
    - `valid`: Whether current state matches expected hash
    - `current_hash`: Current state hash
    - `expected_hash`: Hash that was checked
    """
    verify_csrf_token(token)

    if not PATCHWEAVER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PatchWeaver service not available"
        )

    if not expected_hash:
        raise HTTPException(
            status_code=400,
            detail="expected_hash parameter required"
        )

    try:
        # Verify hash
        valid = _patchweaver.verify_state_hash(expected_hash)

        # Get current hash
        current_state = _patchweaver.load_state()
        current_hash = _patchweaver._compute_hash(current_state)

        return {
            "success": True,
            "valid": valid,
            "current_hash": current_hash,
            "expected_hash": expected_hash
        }

    except Exception as e:
        logger.error("State verification failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ================================
# Performance Budgets Endpoint
# ================================

@app.get("/api/performance-budgets")
@limiter.limit("60/minute")
async def get_performance_budgets(request: Request):
    """Returns the documented per-endpoint performance budgets.

    Each entry specifies p95/p99 latency targets in milliseconds and the
    maximum acceptable error rate as a percentage.  These values are checked
    at runtime by the telemetry middleware and logged as warnings when exceeded.
    """
    from src.observability.performance_budgets import list_budgets
    return {
        "budgets": list_budgets(),
        "note": "p95/p99 latency targets in ms; error rate in percent",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("AURORA_HOST", "0.0.0.0"),
        port=int(os.getenv("AURORA_PORT", "8000")),
        timeout_keep_alive=int(os.getenv("AURORA_KEEPALIVE", "30")),
        limit_concurrency=int(os.getenv("AURORA_MAX_CONCURRENCY", "256")),
        limit_max_requests=int(os.getenv("AURORA_MAX_REQUESTS", "10000")),
        proxy_headers=True,
        forwarded_allow_ips=os.getenv("AURORA_TRUSTED_PROXIES", "127.0.0.1"),
    )
