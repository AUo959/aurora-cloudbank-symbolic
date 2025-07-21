import os
from typing import List

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from modules.telemetry_logger import get_logger

app = FastAPI(title="Aurora Interlink Fabric Hub")
logger = get_logger("aif_hub")

AIF_TOKEN = os.environ.get("AIF_TOKEN", "change-me")

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

    uvicorn.run(app, host="0.0.0.0", port=8090)
