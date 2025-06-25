from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
from typing import List
import uvicorn
import logging

app = FastAPI(title="Aurora Cloud GUI – ZIP Wizard Dashboard")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aurora_gui_cloudhub")

# Active WebSocket connections for basic broadcast
connections: List[WebSocket] = []

# Serve static files if needed in the future
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aurora ZIP Wizard GUI (Cloud)</title>
        <style>
            body { font-family: sans-serif; background: #0f0f1a; color: #ffffff; padding: 30px; }
            input, button { font-size: 1rem; padding: 0.5em; margin: 0.5em 0; }
            .frame { background: #1a1a2a; padding: 20px; border-radius: 8px; max-width: 600px; }
        </style>
    </head>
    <body>
        <div class="frame">
            <h1>🧬 Aurora ZIP Wizard (Cloud GUI)</h1>
            <p>This is the symbolic continuity dashboard. Upload a ZIP Wizard bundle to inspect or relay.</p>
            <form action='/upload/' enctype='multipart/form-data' method='post'>
                <input name='file' type='file' accept='.zip' />
                <button type='submit'>Upload Bundle</button>
            </form>
        </div>
    </body>
    </html>
    """


MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MiB


@app.post("/upload/")
async def upload_bundle(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    upload_dir = Path("./uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.zip"
    upload_path = upload_dir / filename
    with open(upload_path, "wb") as buffer:
        buffer.write(data)
    return {"message": "Bundle received", "filename": filename}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for conn in list(connections):
                if conn is websocket:
                    continue
                try:
                    await conn.send_text(data)
                except WebSocketDisconnect:
                    connections.remove(conn)
    except WebSocketDisconnect:
        connections.remove(websocket)


@app.on_event("startup")
async def startup_event():
    logger.info("Aurora Cloud GUI FastAPI service starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Aurora Cloud GUI FastAPI service shutting down...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
