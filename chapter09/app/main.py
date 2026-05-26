from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 9: WebSockets",
    description="Raw WebSocket chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/swagger", include_in_schema=False)
async def swagger():
    return RedirectResponse(url="/docs")


from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        self.active_connections[connection_id] = websocket
        await websocket.send_json({"event": "connected", "connection_id": connection_id})
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        self.active_connections.pop(connection_id, None)

    async def broadcast(self, payload: dict) -> None:
        disconnected: list[str] = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                disconnected.append(connection_id)
        for connection_id in disconnected:
            self.disconnect(connection_id)


manager = ConnectionManager()


@app.get("/api/websocket/info")
async def websocket_info():
    return {"endpoint": "/ws", "connections": len(manager.active_connections)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast({"event": "message", "connection_id": connection_id, "message": message})
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        await manager.broadcast({"event": "disconnected", "connection_id": connection_id})
