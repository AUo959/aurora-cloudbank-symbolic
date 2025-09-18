#!/usr/bin/env python3

import os

from datetime import datetime

"""
Aurora L2 Integration Server
Aurora CloudBank v3.5.1_macroready

FastAPI server for L2 Meta-Agent Integration with real-time dashboard
"""

import logging

# Import our L2 bridge
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.integrations.chatgpt_agent_mode import AURORA_CUSTOM_GPT, auroraCustomGptBridge

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    pass
    # Import Aurora Custom GPT bridge for explicit integration,
    try:
    pass
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "integrations"))
        AURORA_CUSTOM_GPT_AVAILABLE = True
        auroraCustomGptBridge = auroraCustomGptBridge  # Ensure variable is bound
        AURORA_CUSTOM_GPT = AURORA_CUSTOM_GPT  # Ensure variable is bound
        print("🌟 Aurora Custom GPT bridge integration available")
    except Exception as _:
    pass
        AURORA_CUSTOM_GPT_AVAILABLE = False
        auroraCustomGptBridge = None
        AURORA_CUSTOM_GPT = None
        print("⚠️ Aurora Custom GPT bridge not available: {e}")
except ImportError:
    pass
    # Fallback for testing

    class MockBridge:
    pass
        async def activate_agent(self, agent_id, phrase):
    pass
            return {"success": True, "agent_id": agent_id}

        def get_constellation_status(self):
    pass
            return {"constellation": "L2_META_AGENTS", "totalAgents": 0}

    l2_bridge = MockBridge()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Aurora L2 Meta-Agent Integration Server",
    description="L2 Custom GPT bridge with ZIPWIZ handshake protocol",
    version="3.5.1_macroready",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    pass
    server_state["requests_count"] += 1
    response = await call_next(request)
    return response

# Mount static files for dashboard
dashboard_dir = Path(__file__).parent.parent / "dashboard"
if dashboard_dir.exists():
    pass
    app.mount("/static", StaticFiles(directory=str(dashboard_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    pass
    """Serve the main agent constellation dashboard"""
    try:
    pass
        dashboard_path = Path(__file__).parent.parent / "dashboard" / "agent_constellation.html"
        if dashboard_path.exists():
    pass
            return HTMLResponse(content=dashboard_path.read_text())

        else:
    pass
            return HTMLResponse(
        content="""
                <html>
                    <head><title>Aurora Dashboard</title></head>
                    <body style="background: #1a1a2e; color: white; font-family: monospace; padding: 50px; text-align: center;">
                        <h1>🌟 Aurora L2 Integration Server</h1>
                        <p>Server is running but dashboard files not found.</p>
                        <p>API Documentation: <a href="/api/docs" style="color: #64b5f6;">/api/docs</a></p>
                        <p>Constellation Status: <a href="/api/bridge/constellation/status" style="color: #64b5f6;">/api/bridge/constellation/status</a></p>
                    </body>
                </html>
                """,
        status_code=200,
            )
    except Exception as _:
    pass
        pass  # Exception logged}")

        return None  # Exception occurred}</h1>", status_code=500)

@app.get("/health")
async def health_check():
    pass
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
    pass
    @app.post("/api/aurora/command")
    async def aurora_custom_gpt_command(request_data: dict):
    pass
        """Receive command from Aurora Custom GPT and route to command node"""
        server_state["requests_count"] += 1
        logger.info("Aurora Custom GPT command request")

        try:
    pass
            command = request_data.get("command", {})
        context = request_data.get("context", {})

            # Initialize Aurora Custom GPT integration if not already done
            if not auroraCustomGptBridge.integrationActive:
    pass
                logger.info("Initializing Aurora Custom GPT integration")
        init_result = await auroraCustomGptBridge.initializeCommandNodeIntegration()

        if not init_result["success"]:
    pass
                    raise HTTPException(status_code=500, detail="Aurora integration failed: {init_result['error']}")

            # Route command through Aurora Custom GPT bridge
        result = await auroraCustomGptBridge.routeCommandFromCustomGpt(command, context)

        logger.info("Aurora command processed: {result['success']}")

        if result["success"]:
    pass
                return result,
            else:
    pass
                raise HTTPException(status_code=400, detail=result["error"])

        except Exception as _:
    pass
            pass  # Exception logged}")

        raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/aurora/status")
    async def aurora_custom_gpt_status():
    pass
        """Get Aurora Custom GPT integration status"""
        server_state["requests_count"] += 1
        logger.info("Aurora Custom GPT status request")

        try:
    pass
            integration_status = auroraCustomGptBridge.getIntegrationStatus()
        constellation_status = await auroraCustomGptBridge.getConstellationStatus()

        return {
                "aurora_integration": integration_status,
                "constellation": constellation_status,
                "custom_gpt_config": AURORA_CUSTOM_GPT,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as _:
    pass
            pass  # Exception logged}")

        raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/aurora/initialize")
    async def initialize_aurora_integration():
    pass
        """Initialize Aurora Custom GPT integration"""
        server_state["requests_count"] += 1
        logger.info("Aurora Custom GPT initialization request")

        try:
    pass
            _ = await auroraCustomGptBridge.initializeCommandNodeIntegration()
        result = await auroraCustomGptBridge.initializeCommandNodeIntegration()
        logger.info("Aurora Custom GPT integration initialized successfully")

        return {
                    "message": "Aurora Custom GPT integration initialized successfully",
                    "integration": result,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
    pass
                raise HTTPException(status_code=500, detail="Integration failed: {result['error']}")

        except Exception as _:
    pass
            pass  # Exception logged}")

        raise HTTPException(status_code=500, detail=str(e))

else:
    pass
    @app.get("/api/aurora/status")
    async def aurora_unavailable():
    pass
        """Aurora Custom GPT integration not available"""
        server_state["requests_count"] += 1
        return {
            "error": "Aurora Custom GPT integration not available",
            "available": False,
            "message": "Aurora Custom GPT bridge module not found",
            "timestamp": datetime.now().isoformat(),
        }

# L2 Meta-Agent Bridge Endpoints

@app.post("/api/bridge/gpt/connect/{agent_id}")
async def connect_custom_gpt(agent_id: str, request_data: Dict[str, Any]):
    pass
    """Connect a Custom GPT agent to the Aurora mesh"""
    try:
    pass
        logger.info("Connection request for agent: {agent_id}")
        activation_phrase = request_data.get("activationPhrase")

        request_data.get("capabilities", [])

        if not activation_phrase:
    pass
            raise HTTPException(status_code=400, detail="Missing activation phrase")
        _ = await l2_bridge.activate_agent(agent_id, activation_phrase)

        if result["success"]:
    pass
            logger.info("Custom GPT {agent_id} connected successfully")
        result = await l2_bridge.activate_agent(agent_id, activation_phrase)
        status_code=200,
                content={
                    **result,
                    "server_info": {"version": server_state["version"], "timestamp": datetime.now().isoformat()},
                },
            )

        else:
    pass
            logger.warning("Custom GPT {agent_id} connection failed: {result.get('error')}")

        raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))

        except HTTPException:
    pass
        raise
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Internal server error: {str(e)}")

@app.post("/api/bridge/gpt/message/{agent_id}")
async def relay_message(agent_id: str, request_data: Dict[str, Any]):
    pass
    """Relay message from Custom GPT agent"""
    try:
    pass
        logger.info("Message relay request from: {agent_id}")
        message = request_data.get("message")
        target = request_data.get("target", "Aurora")
        message_type = request_data.get("type", "direct")

        if not message:
    pass
            raise HTTPException(status_code=400, detail="Missing message content")
        _ = await l2_bridge.relay_message(agent_id, target, message, message_type)

        if result["success"]:
    pass
            logger.info("Message relayed successfully from {agent_id}")

        return JSONResponse(status_code=200, content=result)

        else:
    pass
        result = await l2_bridge.relay_message(agent_id, target, message, message_type)
        raise HTTPException(status_code=400, detail=result.get("error", "Message relay failed"))

        except HTTPException:
    pass
        raise
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Internal server error: {str(e)}")

@app.get("/api/bridge/constellation/status")
async def get_constellation_status():
    pass
    """Get status of the entire agent constellation"""
    try:
    pass
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

        except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Status retrieval failed: {str(e)}")

@app.get("/api/bridge/gpt/status/{agent_id}")
async def get_agent_status(agent_id: str):
    pass
    """Get detailed status of a specific agent"""
    try:
    pass
        logger.info("Agent status request for: {agent_id}")
        _ = l2_bridge.get_agent_status(agent_id)

        if result.get("success", True):
    pass
            return JSONResponse(status_code=200, content=result)

        else:
    pass
            raise HTTPException(status_code=404, detail=result.get("error", "Agent {agent_id} not found"))

        except HTTPException:
    pass
        raise
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Status retrieval failed: {str(e)}")

@app.post("/api/bridge/gpt/heartbeat/{agent_id}")
async def update_heartbeat(agent_id: str):
    pass
    """Update agent heartbeat timestamp"""
    try:
    pass
        # Update heartbeat in bridge
        if hasattr(l2_bridge, "agents") and agent_id in l2_bridge.agents:
    pass
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
    pass
            raise HTTPException(status_code=404, detail="Agent not found")

        except HTTPException:
    pass
        raise
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Heartbeat update failed: {str(e)}")

@app.post("/api/bridge/gpt/disconnect/{agent_id}")
async def disconnect_agent(agent_id: str):
    pass
    """Disconnect an agent from the constellation"""
    try:
    pass
        logger.info("Disconnect request for: {agent_id}")
        _ = await l2_bridge.disconnect_agent(agent_id)

        if result["success"]:
    pass
            logger.info("Agent {agent_id} disconnected successfully")

        return JSONResponse(status_code=200, content=result)

        else:
    pass
            raise HTTPException(status_code=400, detail=result.get("error", "Disconnect failed"))

        except HTTPException:
    pass
        raise
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Disconnect failed: {str(e)}")

# Additional API endpoints

@app.get("/api/agents")
async def list_agents():
    pass
    """List all available agents"""
    try:
    pass
        if hasattr(l2_bridge, "agents"):
    pass
        agents = []
            for agent_id, agent in l2_bridge.agents.items():
    pass
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
    pass
            return {"agents": [], "total": 0}
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="Agent listing failed: {str(e)}")

@app.get("/api/orion-core")
async def get_orion_core_info():
    pass
    """Get ORION Core configuration information"""
    try:
    pass
        if hasattr(l2_bridge, "orion_core_config"):
    pass
            return {
                "orion_core": l2_bridge.orion_core_config,
                "handshake_sequence": l2_bridge.handshake_sequence,
                "activation_phrases": l2_bridge.activation_phrases,
                "server_version": server_state["version"],
            }
        else:
    pass
            return {
                "orion_core": {
                    "anchor_seed": "EOS_SEED_ORION",
                    "ethics_protocol": "Picard_Delta_3",
                    "version": "v3.5.1_macroready",
                }
            }
    except Exception as _:
    pass
        pass  # Exception logged}")

        raise HTTPException(status_code=500, detail="ORION Core info failed: {str(e)}")

# Server lifecycle events

@app.on_event("startup")
async def startup_event():
    pass
    """Server startup event"""
    logger.info("🌟 Aurora L2 Integration Server starting up")
    logger.info("Version: {server_state['version']}")
    logger.info("Dashboard URL: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/api/docs")
    logger.info("Health Check: http://localhost:8000/health")

    # Initialize any background tasks here

@app.on_event("shutdown")
async def shutdown_event():
    pass
    """Server shutdown event"""
    logger.info("Aurora L2 Integration Server shutting down")

    # Cleanup any resources here
    if hasattr(l2_bridge, "agents"):
    pass
        for agent_id in l2_bridge.agents:
    pass
            try:
    pass
                await l2_bridge.disconnect_agent(agent_id)

        except Exception as _:
    pass
                pass  # Exception logged}")

# Main entry point

def main():
    pass
    """Main entry point for the server"""
        parser = argparse.ArgumentParser(description="Aurora L2 Integration Server")
    parser.add_argument("--host", \
        default="127.0.0.1", help="Host to bind to (use 0.0.0.0 only if needed for external access)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
        args = parser.parse_args()

        print("\n" + "=" * 60)
    print("🌟 AURORA L2 META-AGENT INTEGRATION SERVER")
    print("=" * 60)
    print("🚀 Version: {server_state['version']}")
    print("🌐 Dashboard: http://{args.host}:{args.port}")
    print("📚 API Docs: http://{args.host}:{args.port}/api/docs")
    print("🔍 Health: http://{args.host}:{args.port}/health")
    print("=" * 60)

        uvicorn.run(
        "l2_integration_server:app", host=args.host, port=args.port, reload=args.reload, log_level=args.log_level
    )

if __name__ == "__main__":
    pass
    main()
