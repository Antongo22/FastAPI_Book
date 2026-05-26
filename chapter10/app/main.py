from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio


BASE_DIR = Path(__file__).resolve().parent.parent

fastapi_app = FastAPI(
    title="Глава 10: Socket.IO чат",
    description="Groups and direct messages",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
fastapi_app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@fastapi_app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@fastapi_app.get("/swagger", include_in_schema=False)
async def swagger():
    return RedirectResponse(url="/docs")


from collections import defaultdict
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect


class ChatManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.groups: dict[str, set[str]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, group: str) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        self.connections[connection_id] = websocket
        self.groups[group].add(connection_id)
        await websocket.send_json({"event": "connected", "connection_id": connection_id, "group": group})
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        self.connections.pop(connection_id, None)
        for members in self.groups.values():
            members.discard(connection_id)

    async def send_to_connection(self, connection_id: str, payload: dict) -> bool:
        websocket = self.connections.get(connection_id)
        if websocket is None:
            return False
        await websocket.send_json(payload)
        return True

    async def broadcast(self, payload: dict, exclude: str | None = None) -> None:
        for connection_id in list(self.connections):
            if connection_id != exclude:
                await self.send_to_connection(connection_id, payload)

    async def send_to_group(self, group: str, payload: dict) -> None:
        for connection_id in list(self.groups[group]):
            await self.send_to_connection(connection_id, payload)


manager = ChatManager()


@fastapi_app.get("/api/chat/info")
async def chat_info():
    return {
        "raw_websocket_connections": len(manager.connections),
        "socketio_connections": len(socketio_clients),
        "groups": {name: len(members) for name, members in manager.groups.items()},
        "socketio_rooms": {name: len(members) for name, members in socketio_rooms.items()},
    }


@fastapi_app.websocket("/ws/chat")
async def chat_socket(websocket: WebSocket, group: str = "general"):
    connection_id = await manager.connect(websocket, group)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action", "broadcast")
            payload = {"event": "message", "from": connection_id, "user": data.get("user", "anonymous"), "message": data.get("message", "")}
            if action == "send_to_connection":
                await manager.send_to_connection(data["connection_id"], payload)
            elif action == "send_to_group":
                await manager.send_to_group(data.get("group", group), payload)
            elif action == "join":
                manager.groups[data.get("group", group)].add(connection_id)
                await manager.send_to_connection(connection_id, {"event": "joined", "group": data.get("group", group)})
            else:
                await manager.broadcast(payload)
    except WebSocketDisconnect:
        manager.disconnect(connection_id)


socketio_clients: dict[str, str] = {}
socketio_rooms: dict[str, set[str]] = defaultdict(set)


@sio.event
async def connect(sid, environ):
    socketio_clients[sid] = "anonymous"
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def disconnect(sid):
    socketio_clients.pop(sid, None)
    for members in socketio_rooms.values():
        members.discard(sid)


@sio.event
async def set_name(sid, data):
    username = data.get("username", "anonymous")
    socketio_clients[sid] = username
    await sio.emit("name_set", {"sid": sid, "username": username}, to=sid)


@sio.event
async def join_room(sid, data):
    room = data.get("room", "general")
    await sio.enter_room(sid, room)
    socketio_rooms[room].add(sid)
    await sio.emit("joined_room", {"room": room}, to=sid)


@sio.event
async def leave_room(sid, data):
    room = data.get("room", "general")
    await sio.leave_room(sid, room)
    socketio_rooms[room].discard(sid)
    await sio.emit("left_room", {"room": room}, to=sid)


@sio.event
async def chat_message(sid, data):
    room = data.get("room")
    payload = {
        "event": "chat_message",
        "from": socketio_clients.get(sid, "anonymous"),
        "message": data.get("message", ""),
        "room": room,
    }
    if room:
        await sio.emit("chat_message", payload, room=room)
    else:
        await sio.emit("chat_message", payload)


@sio.event
async def direct_message(sid, data):
    target_sid = data.get("sid")
    payload = {
        "event": "direct_message",
        "from": socketio_clients.get(sid, "anonymous"),
        "message": data.get("message", ""),
    }
    if target_sid:
        await sio.emit("direct_message", payload, to=target_sid)


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
