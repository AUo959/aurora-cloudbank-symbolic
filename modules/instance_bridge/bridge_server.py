from typing import Dict, Set

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Aurora Instance Bridge")


class ConnectionManager:
    """Manage websocket connections across channels."""

    def __init__(self) -> None:
        self.active_channels: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        await websocket.accept()
        self.active_channels.setdefault(channel, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        if channel in self.active_channels:
            self.active_channels[channel].discard(websocket)
            if not self.active_channels[channel]:
                del self.active_channels[channel]

    async def broadcast(self, channel: str, message: str, sender: WebSocket) -> None:
        for connection in list(self.active_channels.get(channel, [])):
            if connection is not sender:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{channel}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, channel: str, client_id: str) -> None:
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(channel, f"{client_id}: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
