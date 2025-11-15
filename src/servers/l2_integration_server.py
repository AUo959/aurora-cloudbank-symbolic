#!/usr/bin/env python3
"""
Aurora L2 Integration Server
Aurora CloudBank v3.5.1_macroready

FastAPI server providing L2 Meta-Agent Integration with real-time dashboard.

This server provides:
- Health monitoring endpoints
- Aurora Custom GPT integration (when available)
- L2 Meta-Agent bridge API for agent management
- Real-time agent constellation dashboard
- CSRF-protected secure endpoints

Key Endpoints:
    GET  /health                            - System health check
    GET  /                                  - Agent constellation dashboard
    POST /api/aurora/command                - Command routing to Aurora GPT
    GET  /api/aurora/status                 - Aurora GPT integration status
    POST /api/bridge/gpt/connect/{agent_id} - Connect Custom GPT agent
    POST /api/bridge/gpt/message/{agent_id} - Relay messages to agents
    GET  /api/bridge/constellation/status   - Full constellation status

Security:
    - All POST endpoints require CSRF token validation
    - Bearer token authentication via HTTPAuthorizationCredentials
    - Request tracking middleware for audit trails

DLP Protocol:
    - context_tag: "l2_integration_server"
    - All operations tracked for lineage
    - Ethics validation: Picard_Delta_3 ✅
"""

import argparse
import logging
import os
import sys

# Import our L2 bridge
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from src.integrations.chatgpt_agent_mode import AURORA_CUSTOM_GPT, auroraCustomGptBridge
from src.middleware.fastapi_security import security, verify_csrf_token, sanitize_session_id

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import Aurora Custom GPT bridge for explicit integration
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "integrations"))
        AURORA_CUSTOM_GPT_AVAILABLE = True
        auroraCustomGptBridge = auroraCustomGptBridge  # Ensure variable is bound
        AURORA_CUSTOM_GPT = AURORA_CUSTOM_GPT  # Ensure variable is bound
        logging.info("Aurora Custom GPT bridge integration available")
    except ImportError as e:
        AURORA_CUSTOM_GPT_AVAILABLE = False
        auroraCustomGptBridge = None
        AURORA_CUSTOM_GPT = None
        logging.warning("Aurora Custom GPT bridge not available: %s", str(e))
except ImportError:
    # Fallback for testing

    class MockBridge:
        """
        Mock L2 Bridge for testing and development environments.
        
        Provides stub implementations of L2 Meta-Agent bridge functionality
        when the full integration is not available. All methods return success
        responses with minimal data for compatibility.
        
        Methods:
            activate_agent(agent_id, phrase): Simulate agent activation
            get_constellation_status(): Return empty constellation status
            relay_message(agent_id, target, message, type): Mock message relay
            get_agent_status(agent_id): Return mock agent status
        
        Attributes:
            agents: Empty dict for agent tracking compatibility
        
        Note: This is a development/testing fallback. Production deployments
        should use the full L2 bridge implementation.
        """
        
        def __init__(self):
            """Initialize mock bridge with empty agent registry."""
            self.agents = {}

        async def activate_agent(self, agent_id, _phrase):
            """
            Mock agent activation for testing.
            
            Args:
                agent_id: Unique identifier for the agent to activate
                _phrase: Activation phrase (unused in mock, prefixed with _ to indicate intentional)
            
            Returns:
                Dict with success=True and the agent_id
            """
            return {"success": True, "agent_id": agent_id}

        def get_constellation_status(self):
            """
            Get empty constellation status for testing.
            
            Returns:
                Dict with constellation name and zero agents
            """
            return {"constellation": "L2_META_AGENTS", "totalAgents": 0}
        
        async def relay_message(self, agent_id, target, message, message_type):
            """
            Mock message relay for testing.
            
            Args:
                agent_id: Source agent identifier
                target: Target destination
                message: Message content
                message_type: Type of message
            
            Returns:
                Dict with success=True and relay confirmation
            """
            return {
                "success": True,
                "agent_id": agent_id,
                "target": target,
                "relayed": True
            }
        
        def get_agent_status(self, agent_id):
            """
            Get mock status for an agent.
            
            Args:
                agent_id: Agent identifier
            
            Returns:
                Dict with basic status information
            """
            return {
                "agent_id": agent_id,
                "status": "active",
                "connected": True
            }

    l2_bridge = MockBridge()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security constants
INVALID_CSRF_TOKEN_MSG = 'Invalid CSRF token'

# Initialize FastAPI app
app = FastAPI(
    title="Aurora L2 Integration Server",
    description="L2 Meta-Agent Integration with real-time dashboard",
    version="1.0.0",
)

# Add CORS middleware
# SECURITY FIX: Use specific origins instead of wildcard when credentials are enabled
allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Server state
server_state = {
    "start_time": datetime.now(),
    "requests_count": 0,
    "active_connections": 0,
    "version": "v3.5.1_macroready",
}

# Middleware to track requests


@app.middleware("http")
async def track_requests(request: Request, call_next):
    server_state["requests_count"] += 1
    response = await call_next(request)
    return response


# Mount static files for dashboard
dashboard_dir = Path(__file__).parent.parent / "dashboard"
if dashboard_dir.exists():
    app.mount("/static", StaticFiles(directory=str(dashboard_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main agent constellation dashboard"""
    try:
        dashboard_path = Path(__file__).parent.parent / "dashboard" / "agent_constellation.html"
        if dashboard_path.exists():
            return HTMLResponse(content=dashboard_path.read_text())
        else:
            return HTMLResponse(
                content="""
                <html>
                    <head><title>Aurora Dashboard</title></head>
                    <body style="background: #1a1a2e; color: white; font-family: monospace; "
                          "padding: 50px; text-align: center;">
                        <h1>🌟 Aurora L2 Integration Server</h1>
                        <p>Server is running but dashboard files not found.</p>
                        <p>API Documentation: <a href="/api/docs" style="color: #64b5f6;">/api/docs</a></p>
                        <p>Constellation Status: <a href="/api/bridge/constellation/status"
                           style="color: #64b5f6;">/api/bridge/constellation/status</a></p>
                    </body>
                </html>
                """,
                status_code=200,
            )
    except Exception as e:
        logger.error("Dashboard error: %s", str(str(e))[:100])
        return HTMLResponse(f"<h1>Dashboard Error: {str(e)}</h1>", status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - server_state["start_time"]).total_seconds()
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": server_state["version"],
        "requests": server_state["requests_count"],
        "timestamp": datetime.now().isoformat(),
        "aurora_custom_gpt_available": AURORA_CUSTOM_GPT_AVAILABLE,
    }

# Aurora Custom GPT Integration Endpoints
if AURORA_CUSTOM_GPT_AVAILABLE:
    # CSRF token verification occurs inside the handler
    @app.post("/api/aurora/command")
    async def aurora_custom_gpt_command(request_data: dict, token: HTTPAuthorizationCredentials = Depends(security)):
        """Receive command from Aurora Custom GPT and route to command node with CSRF validation."""
        verify_csrf_token(token)

        server_state["requests_count"] += 1
        logger.info("Aurora Custom GPT command request")

        try:
            command = request_data.get("command", {})
            context = request_data.get("context", {})

            # Initialize Aurora Custom GPT integration if not already done
            if not auroraCustomGptBridge.integrationActive:
                logger.info("Initializing Aurora Custom GPT integration")
                init_result = await auroraCustomGptBridge.initializeCommandNodeIntegration()
                if not init_result["success"]:
                    raise HTTPException(status_code=500, detail=f"Aurora integration failed: {init_result['error']}")

            # Route command through Aurora Custom GPT bridge
            result = await auroraCustomGptBridge.routeCommandFromCustomGpt(command, context)

            # Secure logging to prevent log injection
            logger.info("Aurora command processed with status: %s", str(result.get('success', 'unknown'))[:50])

            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])

        except Exception as e:
            # Secure logging to prevent log injection
            logger.error("Aurora command failed: %s", str(e)[:100])
            raise HTTPException(status_code=500, detail="Aurora command processing failed")

    @app.get("/api/aurora/status")
    async def aurora_custom_gpt_status():
        """Get Aurora Custom GPT integration status"""
        server_state["requests_count"] += 1
        logger.info("Aurora Custom GPT status request")

        try:
            integration_status = auroraCustomGptBridge.getIntegrationStatus()
            constellation_status = await auroraCustomGptBridge.getConstellationStatus()

            return {
                "aurora_integration": integration_status,
                "constellation": constellation_status,
                "custom_gpt_config": AURORA_CUSTOM_GPT,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error("Aurora status request failed: %s", str(str(e))[:100])
            raise HTTPException(status_code=500, detail="Aurora status retrieval failed")

    # CSRF token verification occurs inside the handler
    @app.post("/api/aurora/initialize")
    async def initialize_aurora_integration(token: HTTPAuthorizationCredentials = Depends(security)):
        """Initialize Aurora Custom GPT integration with CSRF validation."""
        verify_csrf_token(token)

        server_state["requests_count"] += 1
        logger.info("Aurora Custom GPT initialization request")

        try:
            result = await auroraCustomGptBridge.initializeCommandNodeIntegration()

            if result["success"]:
                logger.info("Aurora Custom GPT integration initialized successfully")
                return {
                    "message": "Aurora Custom GPT integration initialized successfully",
                    "integration": result,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                raise HTTPException(status_code=500, detail=f"Integration failed: {result['error']}")

        except Exception as e:
            logger.error("Aurora initialization failed: %s", str(str(e))[:100])
            raise HTTPException(status_code=500, detail="Aurora initialization failed")

else:

    @app.get("/api/aurora/status")
    async def aurora_unavailable():
        """Aurora Custom GPT integration not available"""
        server_state["requests_count"] += 1
        return {
            "error": "Aurora Custom GPT integration not available",
            "available": False,
            "message": "Aurora Custom GPT bridge module not found",
            "timestamp": datetime.now().isoformat(),
        }

# L2 Meta-Agent Bridge Endpoints

# CSRF token verification occurs inside the handler
@app.post("/api/bridge/gpt/connect/{agent_id}")
async def connect_custom_gpt(
    agent_id: str,
    request_data: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Connect a Custom GPT agent to the Aurora mesh.
    
    Establishes a new connection for a Custom GPT agent to the L2 Meta-Agent
    constellation. Requires valid activation phrase and CSRF token.
    
    Args:
        agent_id: Unique identifier for the Custom GPT agent
        request_data: Dict containing:
            - activationPhrase (required): Phrase to activate the agent
            - capabilities (optional): List of agent capabilities
        token: Bearer token for CSRF validation
    
    Returns:
        JSONResponse with:
            - success: Boolean indicating connection status
            - agent_id: Echo of the agent identifier
            - server_info: Version and timestamp data
    
    Raises:
        HTTPException 400: Missing or invalid activation phrase
        HTTPException 403: Invalid CSRF token
        HTTPException 500: Internal server error during connection
    
    Security:
        - CSRF token validation required
        - Agent ID sanitized to prevent injection
        - Request logged with lineage tracking
    
    DLP: context_tag="bridge_gpt_connect"
    """
    verify_csrf_token(token)
    agent_id = sanitize_session_id(agent_id)

    try:
        # Secure logging to prevent log injection
        logger.info("Connection request for agent: %s", str(agent_id)[:50])

        activation_phrase = request_data.get("activationPhrase")
        request_data.get("capabilities", [])

        if not activation_phrase:
            raise HTTPException(status_code=400, detail="Missing activation phrase")

        result = await l2_bridge.activate_agent(agent_id, activation_phrase)

        if result["success"]:
            logger.info("Custom GPT %s connected successfully", str(agent_id)[:100])
            return JSONResponse(
                status_code=200,
                content={
                    **result,
                    "server_info": {"version": server_state["version"], "timestamp": datetime.now().isoformat()},
                },
            )
        else:
            error_msg = str(result.get('error'))
            # Sanitize potential log injection vectors
            error_msg = error_msg.replace('\r\n', '').replace('\n', '').replace('\r', '')[:100]
            logger.warning("Custom GPT %s connection failed: %s", str(agent_id)[:100], error_msg)
            raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Custom GPT connection failed for %s: %s", str(agent_id)[:100], str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# CSRF token verification occurs inside the handler
@app.post("/api/bridge/gpt/message/{agent_id}")
async def relay_message(
    agent_id: str,
    request_data: Dict[str, Any],
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Relay message from Custom GPT agent with CSRF validation."""
    verify_csrf_token(token)
    agent_id = sanitize_session_id(agent_id)

    try:
        logger.info("Message relay request from: %s", str(agent_id)[:100])

        message = request_data.get("message")
        target = request_data.get("target", "Aurora")
        message_type = request_data.get("type", "direct")

        if not message:
            raise HTTPException(status_code=400, detail="Missing message content")

        result = await l2_bridge.relay_message(agent_id, target, message, message_type)

        if result["success"]:
            logger.info("Message relayed successfully from %s", str(agent_id)[:100])
            return JSONResponse(status_code=200, content=result)
        else:
            error_msg = str(result.get('error'))
            # Sanitize potential log injection vectors
            error_msg = error_msg.replace('\r\n', '').replace('\n', '').replace('\r', '')[:100]
            logger.warning("Message relay failed from %s: %s", str(agent_id)[:100], error_msg)
            raise HTTPException(status_code=400, detail=result.get("error", "Message relay failed"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Message relay failed for %s: %s", str(agent_id)[:100], str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/bridge/constellation/status")
async def get_constellation_status():
    """Get status of the entire agent constellation"""
    try:
        logger.info("Constellation status request")

        status = l2_bridge.get_constellation_status()

        # Add server information
        status["server_info"] = {
            "uptime": (datetime.now() - server_state["start_time"]).total_seconds(),
            "requests_count": server_state["requests_count"],
            "version": server_state["version"],
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(status_code=200, content=status)

    except Exception as e:
        logger.error("Status retrieval failed: %s", str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.get("/api/bridge/gpt/status/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get detailed status of a specific agent"""
    try:
        logger.info("Agent status request for: %s", str(agent_id)[:100])

        result = l2_bridge.get_agent_status(agent_id)

        if result.get("success", True):
            return JSONResponse(status_code=200, content=result)
        else:
            raise HTTPException(status_code=404, detail=result.get("error", f"Agent {agent_id} not found"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Agent status retrieval failed for %s: %s", str(agent_id)[:100], str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

# CSRF token verification occurs inside the handler
@app.post("/api/bridge/gpt/heartbeat/{agent_id}")
async def update_heartbeat(agent_id: str, token: HTTPAuthorizationCredentials = Depends(security)):
    """Update agent heartbeat timestamp with CSRF validation."""
    verify_csrf_token(token)
    agent_id = sanitize_session_id(agent_id)

    try:
        # Update heartbeat in bridge
        if hasattr(l2_bridge, "agents") and agent_id in l2_bridge.agents:
            l2_bridge.agents[agent_id].last_heartbeat = datetime.now()

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "agent_id": agent_id,
                    "heartbeat": datetime.now().isoformat(),
                    "status": l2_bridge.agents[agent_id].status,
                },
            )
        else:
            raise HTTPException(status_code=404, detail="Agent not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Heartbeat update failed for %s: %s", str(agent_id)[:100], str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Heartbeat update failed: {str(e)}")

# CSRF token verification occurs inside the handler
@app.post("/api/bridge/gpt/disconnect/{agent_id}")
async def disconnect_agent(agent_id: str, token: HTTPAuthorizationCredentials = Depends(security)):
    """Disconnect an agent from the constellation with CSRF validation."""
    verify_csrf_token(token)
    agent_id = sanitize_session_id(agent_id)

    try:
        logger.info("Disconnect request for: %s", str(agent_id)[:100])

        result = await l2_bridge.disconnect_agent(agent_id)

        if result["success"]:
            logger.info("Agent %s disconnected successfully", str(agent_id)[:100])
            return JSONResponse(status_code=200, content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Disconnect failed"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Disconnect failed for %s: %s", str(agent_id)[:100], str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Disconnect failed: {str(e)}")

# Additional API endpoints

@app.get("/api/agents")
async def list_agents():
    """List all available agents"""
    try:
        if hasattr(l2_bridge, "agents"):
            agents = []
            for agent_id, agent in l2_bridge.agents.items():
                agents.append(
                    {
                        "agent_id": agent_id,
                        "role": agent.role,
                        "type": agent.type,
                        "description": agent.description,
                        "capabilities": agent.capabilities,
                        "status": agent.status,
                        "api_endpoint": agent.api_endpoint,
                    }
                )
            return {"agents": agents, "total": len(agents)}
        else:
            return {"agents": [], "total": 0}
    except Exception as e:
        logger.error("Agent listing failed: %s", str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"Agent listing failed: {str(e)}")

@app.get("/api/orion-core")
async def get_orion_core_info():
    """Get ORION Core configuration information"""
    try:
        if hasattr(l2_bridge, "orion_core_config"):
            return {
                "orion_core": l2_bridge.orion_core_config,
                "handshake_sequence": l2_bridge.handshake_sequence,
                "activation_phrases": l2_bridge.activation_phrases,
                "server_version": server_state["version"],
            }
        else:
            return {
                "orion_core": {
                    "anchor_seed": "EOS_SEED_ORION",
                    "ethics_protocol": "Picard_Delta_3",
                    "version": "v3.5.1_macroready",
                }
            }
    except Exception as e:
        logger.error("ORION Core info retrieval failed: %s", str(str(e))[:100])
        raise HTTPException(status_code=500, detail=f"ORION Core info failed: {str(e)}")

# Server lifecycle events

@app.on_event("startup")
async def startup_event():
    """Server startup event"""
    logger.info("🌟 Aurora L2 Integration Server starting up")
    logger.info("Version: %s", str(server_state['version'])[:100])
    logger.info("Dashboard URL: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/api/docs")
    logger.info("Health Check: http://localhost:8000/health")

    # Initialize any background tasks here

@app.on_event("shutdown")
async def shutdown_event():
    """Server shutdown event"""
    logger.info("Aurora L2 Integration Server shutting down")

    # Cleanup any resources here
    if hasattr(l2_bridge, "agents"):
        for agent_id in l2_bridge.agents:
            try:
                await l2_bridge.disconnect_agent(agent_id)
            except Exception as e:
                logger.error("Error disconnecting %s: %s", str(agent_id)[:100], str(str(e))[:100])

# Main entry point

def main():
    """Main entry point for the server"""

    parser = argparse.ArgumentParser(description="Aurora L2 Integration Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("🌟 AURORA L2 META-AGENT INTEGRATION SERVER")
    logger.info("=" * 60)
    logger.info("Version: %s", server_state['version'])
    logger.info("Dashboard: http://%s:%s", args.host, args.port)
    logger.info("API Docs: http://%s:%s/api/docs", args.host, args.port)
    logger.info("Health: http://%s:%s/health", args.host, args.port)
    logger.info("=" * 60)

    uvicorn.run(
        "l2_integration_server:app", host=args.host, port=args.port, reload=args.reload, log_level=args.log_level
    )

if __name__ == "__main__":
    main()
