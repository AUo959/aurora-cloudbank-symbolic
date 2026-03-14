import os
import secrets
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from modules.telemetry_logger import get_logger

logger = get_logger("aif_hub")


def _get_required_token() -> str:
    token = os.environ.get("AIF_TOKEN", "").strip()
    if not token or token == "change-me":
        raise RuntimeError("AIF_TOKEN must be set to a non-placeholder value before starting the AIF hub")
    return token


class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def reset(self) -> None:
        self.active_connections.clear()

    async def broadcast(self, message: str, sender: Optional[WebSocket] = None) -> None:
        for connection in list(self.active_connections):
            if connection is sender:
                continue
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    manager.reset()
    _get_required_token()
    logger.info("AIF hub starting")
    try:
        yield
    finally:
        manager.reset()
        logger.info("AIF hub shutting down")


app = FastAPI(title="Aurora Interlink Fabric Hub", lifespan=lifespan)


def _validate_token(websocket: WebSocket) -> None:
    token = websocket.headers.get("authorization", "")
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    if not secrets.compare_digest(token, _get_required_token()):
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

    uvicorn.run(
        app,
        host=os.environ.get("AIF_HOST", "127.0.0.1"),
        port=int(os.environ.get("AIF_PORT", "8090")),
    )
