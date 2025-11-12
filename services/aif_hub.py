import logging

logger = logging.getLogger(__name__)

import os
import secrets
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from modules.telemetry_logger import get_logger

app = FastAPI(title="Aurora Interlink Fabric Hub")
logger = get_logger("aif_hub")

# SECURITY: Generate secure random token if none provided via environment
AIF_TOKEN = os.environ.get("AIF_TOKEN")
if not AIF_TOKEN or AIF_TOKEN == "change-me":
    # Generate cryptographically secure random token
    AIF_TOKEN = secrets.token_urlsafe(32)
    logger.warning("No secure AIF_TOKEN provided. Generated random token for this session.")
    logger.info("Generated AIF_TOKEN: %s", AIF_TOKEN[:8] + "..." + AIF_TOKEN[-4:])  # Only log partial token for security
    logger.warning("WARNING: Using generated AIF_TOKEN: {AIF_TOKEN}")
    print("   Set AIF_TOKEN environment variable for production use.")


class ConnectionManager:
    """Manage active WebSocket connections."""

    import uvicorn

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str, sender: WebSocket | None = None) -> None:
        for connection in list(self.active_connections):
            if connection is sender:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


def _validate_token(websocket: WebSocket) -> None:
    token = websocket.headers.get("authorization", "")
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    if token != AIF_TOKEN:
        logger.warning("Unauthorized WebSocket connection attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    _validate_token(websocket)
    await manager.connect(websocket)
    logger.info("Client connected to AIF hub")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info("Anchor received: %s", data)
            await manager.broadcast(data, sender=websocket)
    except WebSocketDisconnect:
        logger.info("Client disconnected from AIF hub")
        manager.disconnect(websocket)


if __name__ == "__main__":
    # SECURITY: Bind to localhost only for security (change to 0.0.0.0 only if external access needed)
    uvicorn.run(app, host="127.0.0.1", port=8090)
