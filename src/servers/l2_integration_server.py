#!/usr/bin/env python3
"""
Aurora L2 Integration Server
Aurora CloudBank v3.5.1_macroready

FastAPI server for L2 Meta-Agent Integration with real-time dashboard
"""

import argparse
import logging
import os
import sys

# Import our L2 bridge
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from src.integrations.chatgpt_agent_mode import auroraCustomGptBridge
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.integrations.chatgpt_agent_mode import AURORA_CUSTOM_GPT

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import Aurora Custom GPT bridge for explicit integration
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "integrations"))
        AURORA_CUSTOM_GPT_AVAILABLE = True
        auroraCustomGptBridge = auroraCustomGptBridge  # Ensure variable is bound
        AURORA_CUSTOM_GPT = AURORA_CUSTOM_GPT  # Ensure variable is bound
        print("🌟 Aurora Custom GPT bridge integration available")
    except ImportError as e:
        AURORA_CUSTOM_GPT_AVAILABLE = False
        auroraCustomGptBridge = None
        AURORA_CUSTOM_GPT = None
        print(f"⚠️ Aurora Custom GPT bridge not available: {e}")
except ImportError:
    # Fallback for testing

    class MockBridge:

        async def activate_agent(self, agent_id, phrase):
            return {"success": True, "agent_id": agent_id}

        def get_constellation_status(self):
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
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
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

    @app.post("/api/aurora/command")
    async def aurora_custom_gpt_command(request_data: dict):
        """Receive command from Aurora Custom GPT and route to command node"""
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

            logger.info(f"Aurora command processed: {result['success']}")

            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])

        except Exception as e:
            logger.error(f"Aurora command failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

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
            logger.error(f"Aurora status request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/aurora/initialize")
    async def initialize_aurora_integration():
        """Initialize Aurora Custom GPT integration"""
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
            logger.error(f"Aurora initialization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/bridge/gpt/connect/{agent_id}")


async def connect_custom_gpt(agent_id: str, request_data: Dict[str, Any]):
    """Connect a Custom GPT agent to the Aurora mesh"""
    try:
        logger.info(f"Connection request for agent: {agent_id}")

        activation_phrase = request_data.get("activationPhrase")
        request_data.get("capabilities", [])

        if not activation_phrase:
            raise HTTPException(status_code=400, detail="Missing activation phrase")

        result = await l2_bridge.activate_agent(agent_id, activation_phrase)

        if result["success"]:
            logger.info(f"Custom GPT {agent_id} connected successfully")
            return JSONResponse(
                status_code=200,
                content={
                    **result,
                    "server_info": {"version": server_state["version"], "timestamp": datetime.now().isoformat()},
                },
            )
        else:
            logger.warning(f"Custom GPT {agent_id} connection failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom GPT connection failed for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/bridge/gpt/message/{agent_id}")


async def relay_message(agent_id: str, request_data: Dict[str, Any]):
    """Relay message from Custom GPT agent"""
    try:
        logger.info(f"Message relay request from: {agent_id}")

        message = request_data.get("message")
        target = request_data.get("target", "Aurora")
        message_type = request_data.get("type", "direct")

        if not message:
            raise HTTPException(status_code=400, detail="Missing message content")

        result = await l2_bridge.relay_message(agent_id, target, message, message_type)

        if result["success"]:
            logger.info(f"Message relayed successfully from {agent_id}")
            return JSONResponse(status_code=200, content=result)
        else:
            logger.warning(f"Message relay failed from {agent_id}: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Message relay failed"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Message relay failed for {agent_id}: {str(e)}")
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
        logger.error(f"Status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.get("/api/bridge/gpt/status/{agent_id}")


async def get_agent_status(agent_id: str):
    """Get detailed status of a specific agent"""
    try:
        logger.info(f"Agent status request for: {agent_id}")

        result = l2_bridge.get_agent_status(agent_id)

        if result.get("success", True):
            return JSONResponse(status_code=200, content=result)
        else:
            raise HTTPException(status_code=404, detail=result.get("error", f"Agent {agent_id} not found"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent status retrieval failed for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.post("/api/bridge/gpt/heartbeat/{agent_id}")


async def update_heartbeat(agent_id: str):
    """Update agent heartbeat timestamp"""
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
        logger.error(f"Heartbeat update failed for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Heartbeat update failed: {str(e)}")

@app.post("/api/bridge/gpt/disconnect/{agent_id}")


async def disconnect_agent(agent_id: str):
    """Disconnect an agent from the constellation"""
    try:
        logger.info(f"Disconnect request for: {agent_id}")

        result = await l2_bridge.disconnect_agent(agent_id)

        if result["success"]:
            logger.info(f"Agent {agent_id} disconnected successfully")
            return JSONResponse(status_code=200, content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Disconnect failed"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disconnect failed for {agent_id}: {str(e)}")
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
        logger.error(f"Agent listing failed: {str(e)}")
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
        logger.error(f"ORION Core info retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ORION Core info failed: {str(e)}")

# Server lifecycle events

@app.on_event("startup")


async def startup_event():
    """Server startup event"""
    logger.info("🌟 Aurora L2 Integration Server starting up")
    logger.info(f"Version: {server_state['version']}")
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
                logger.error(f"Error disconnecting {agent_id}: {str(e)}")

# Main entry point

def main():
    """Main entry point for the server"""

    parser = argparse.ArgumentParser(description="Aurora L2 Integration Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🌟 AURORA L2 META-AGENT INTEGRATION SERVER")
    print("=" * 60)
    print(f"🚀 Version: {server_state['version']}")
    print(f"🌐 Dashboard: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/api/docs")
    print(f"🔍 Health: http://{args.host}:{args.port}/health")
    print("=" * 60)

    uvicorn.run(
        "l2_integration_server:app", host=args.host, port=args.port, reload=args.reload, log_level=args.log_level
    )

if __name__ == "__main__":
    main()
