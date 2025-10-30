"""
DLP Auto-Tracking Middleware
Automatically creates DLP tags and Insight Ledger entries for API operations

Anchor: T1-DLP-AUTO-001
Context: R-2 Synergy Audit - Opportunity #2 Implementation
"""

import time
from typing import Callable, Optional, Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Import with graceful fallback
try:
    from src.core.native_dlp_export import NativeDLPTracker
except ImportError:
    # Mock for testing environments
    class NativeDLPTracker:
        def __init__(self):
            self.tags = {}
            self.operation_counter = 0
        
        def create_tag(self, operation: str, data: dict, tag_id: Optional[str] = None) -> str:
            self.operation_counter += 1
            result_tag_id = tag_id or f"dlp_mock_{self.operation_counter}"
            self.tags[result_tag_id] = {"operation": operation, "data": data}
            return result_tag_id

try:
    from modules.insight_ledger.api import get_ledger
    from modules.insight_ledger.schemas import InsightRecord
    INSIGHT_LEDGER_AVAILABLE = True
except ImportError:
    INSIGHT_LEDGER_AVAILABLE = False
    get_ledger = None
    InsightRecord = None


class DLPAutoTrackingMiddleware(BaseHTTPMiddleware):
    """
    Automatic DLP tracking middleware for FastAPI
    
    Features:
    - Creates DLP tags for every API request/response
    - Records significant operations to Insight Ledger
    - Links request/response tags in provenance chains
    - Minimal performance overhead (<5ms)
    - Configurable tracking levels
    
    Usage:
        from src.middleware.dlp_auto_tracker import add_dlp_tracking
        
        app = FastAPI()
        add_dlp_tracking(app, tracking_level="standard")
    """
    
    # Operations to exclude from tracking (health checks, static assets)
    EXCLUDE_PATHS: Set[str] = {
        "/health", 
        "/api/health", 
        "/metrics", 
        "/static", 
        "/favicon.ico",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
    
    # Tracking levels
    LEVEL_MINIMAL = "minimal"    # Only writes and errors
    LEVEL_STANDARD = "standard"  # Writes, errors, and significant reads
    LEVEL_VERBOSE = "verbose"    # Everything
    
    def __init__(
        self, 
        app, 
        tracking_level: str = "standard",
        enable_ledger: bool = True
    ):
        """
        Initialize DLP auto-tracking middleware
        
        Args:
            app: FastAPI application
            tracking_level: One of "minimal", "standard", "verbose"
            enable_ledger: Whether to record to Insight Ledger
        """
        super().__init__(app)
        self.dlp_tracker = NativeDLPTracker()
        self.insight_ledger = None
        self.tracking_level = tracking_level
        self.enable_ledger = enable_ledger and INSIGHT_LEDGER_AVAILABLE
        
        # Statistics
        self.total_requests = 0
        self.total_tracked = 0
        self.total_ledger_records = 0
        self.total_overhead_ms = 0.0
        
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and create DLP/audit records"""
        
        # Skip excluded paths
        if self._should_exclude(request):
            return await call_next(request)
        
        self.total_requests += 1
        start_time = time.time()
        tracking_start = time.time()
        
        # Create DLP tag for request
        request_data = self._extract_request_data(request)
        request_tag_id = self.dlp_tracker.create_tag(
            operation=f"api_request_{request.method}_{self._normalize_path(request.url.path)}",
            data=request_data,
            tag_id=f"request_{int(time.time() * 1000)}"
        )
        self.total_tracked += 1
        
        # Process request
        response = await call_next(request)
        
        # Create DLP tag for response
        elapsed_ms = (time.time() - start_time) * 1000
        response_data = self._extract_response_data(response, elapsed_ms)
        
        response_tag_id = self.dlp_tracker.create_tag(
            operation=f"api_response_{response.status_code}",
            data=response_data,
            tag_id=f"response_{int(time.time() * 1000)}"
        )
        
        # Link request and response tags
        response_tag = self.dlp_tracker.tags.get(response_tag_id)
        if response_tag:
            response_tag.add_dependency(request_tag_id)
        
        # Record to Insight Ledger for significant operations
        if self.enable_ledger and self._should_record_to_ledger(request, response):
            await self._record_to_insight_ledger(
                request, response, request_tag_id, response_tag_id, elapsed_ms
            )
        
        # Add DLP headers to response
        response.headers["X-DLP-Request-Tag"] = request_tag_id
        response.headers["X-DLP-Response-Tag"] = response_tag_id
        
        # Track overhead
        tracking_overhead = (time.time() - tracking_start) * 1000
        self.total_overhead_ms += tracking_overhead
        response.headers["X-DLP-Overhead-Ms"] = f"{tracking_overhead:.2f}"
        
        return response
    
    def _should_exclude(self, request: Request) -> bool:
        """Check if path should be excluded from tracking"""
        path = request.url.path
        return any(path.startswith(excluded) for excluded in self.EXCLUDE_PATHS)
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for DLP tag operation names"""
        # Replace path parameters with placeholders
        parts = path.split("/")
        normalized_parts = []
        for part in parts:
            if part and part[0].isdigit():
                normalized_parts.append("{id}")
            else:
                normalized_parts.append(part)
        return "/".join(normalized_parts)
    
    def _extract_request_data(self, request: Request) -> dict:
        """Extract relevant request data for DLP tracking"""
        return {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params) if request.query_params else {},
            "client_host": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type", "unknown")
        }
    
    def _extract_response_data(self, response: Response, elapsed_ms: float) -> dict:
        """Extract relevant response data for DLP tracking"""
        return {
            "status_code": response.status_code,
            "elapsed_ms": round(elapsed_ms, 2),
            "content_type": response.headers.get("content-type", "unknown"),
            "content_length": response.headers.get("content-length", "unknown")
        }
    
    def _should_record_to_ledger(self, request: Request, response: Response) -> bool:
        """Determine if operation should be recorded to audit trail"""
        if self.tracking_level == self.LEVEL_MINIMAL:
            # Only record write operations and errors
            return (
                request.method in {"POST", "PUT", "PATCH", "DELETE"} or 
                response.status_code >= 400
            )
        elif self.tracking_level == self.LEVEL_VERBOSE:
            # Record everything
            return True
        else:  # LEVEL_STANDARD
            # Record writes, errors, and significant reads
            path = request.url.path
            return (
                request.method in {"POST", "PUT", "PATCH", "DELETE"} or
                response.status_code >= 400 or
                "/memory/" in path or
                "/ledger/" in path or
                "/simulate/" in path or
                "/agent/" in path
            )
    
    async def _record_to_insight_ledger(
        self, 
        request: Request, 
        response: Response,
        request_tag_id: str,
        response_tag_id: str,
        elapsed_ms: float
    ):
        """Record operation to Insight Ledger"""
        if not INSIGHT_LEDGER_AVAILABLE:
            return
        
        # Lazy initialize ledger
        if self.insight_ledger is None:
            try:
                self.insight_ledger = get_ledger()
            except Exception as e:
                print(f"⚠️  Failed to initialize Insight Ledger: {e}")
                self.enable_ledger = False
                return
        
        try:
            # Determine DLP classification based on status code and method
            if response.status_code >= 500:
                dlp_classification = "DLP_L3_ERROR"
            elif response.status_code >= 400:
                dlp_classification = "DLP_L2_CLIENT_ERROR"
            else:
                dlp_classification = "DLP_L1_OK"
            
            insight = InsightRecord(
                insight_type=f"api_{request.method.lower()}",
                content={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "elapsed_ms": round(elapsed_ms, 2),
                    "client": request.client.host if request.client else "unknown"
                },
                actor=request.client.host if request.client else "system",
                tags=[
                    request.method.lower(), 
                    "api", 
                    "auto_tracked",
                    f"status_{response.status_code}"
                ],
                aurora_anchors=[request_tag_id, response_tag_id],
                dlp_classification=dlp_classification
            )
            
            self.insight_ledger.record_insight(insight)
            self.total_ledger_records += 1
            
        except Exception as e:
            # Don't fail the request if ledger recording fails
            print(f"⚠️  Failed to record to Insight Ledger: {e}")
    
    def get_statistics(self) -> dict:
        """Get middleware statistics"""
        avg_overhead = (
            self.total_overhead_ms / self.total_requests 
            if self.total_requests > 0 
            else 0
        )
        
        return {
            "total_requests": self.total_requests,
            "total_tracked": self.total_tracked,
            "total_ledger_records": self.total_ledger_records,
            "average_overhead_ms": round(avg_overhead, 3),
            "tracking_level": self.tracking_level,
            "ledger_enabled": self.enable_ledger,
            "dlp_tags_created": len(self.dlp_tracker.tags)
        }


def add_dlp_tracking(
    app, 
    tracking_level: str = "standard",
    enable_ledger: bool = True
):
    """
    Add DLP auto-tracking middleware to FastAPI app
    
    Args:
        app: FastAPI application
        tracking_level: "minimal", "standard", or "verbose"
        enable_ledger: Whether to enable Insight Ledger recording
    
    Example:
        from fastapi import FastAPI
        from src.middleware.dlp_auto_tracker import add_dlp_tracking
        
        app = FastAPI()
        add_dlp_tracking(app, tracking_level="standard")
    """
    middleware = DLPAutoTrackingMiddleware(
        app=app, 
        tracking_level=tracking_level,
        enable_ledger=enable_ledger
    )
    app.add_middleware(
        DLPAutoTrackingMiddleware,
        tracking_level=tracking_level,
        enable_ledger=enable_ledger
    )
    return middleware
