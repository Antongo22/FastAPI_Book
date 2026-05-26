from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 11: Auth WebSockets",
    description="JWT protected WebSocket",
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


import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from pydantic import BaseModel


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return str(payload["sub"])
    except (JWTError, KeyError) as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error


class AuthorizedManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        self.connections[connection_id] = websocket
        await websocket.send_json({"event": "connected", "connection_id": connection_id, "username": username})
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        self.connections.pop(connection_id, None)

    async def broadcast(self, payload: dict) -> None:
        for websocket in list(self.connections.values()):
            await websocket.send_json(payload)


manager = AuthorizedManager()


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    if not request.username or not request.password:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    return {"access_token": create_access_token(request.username), "token_type": "bearer", "username": request.username}


@app.websocket("/ws/authorized")
async def authorized_socket(websocket: WebSocket, access_token: str | None = Query(default=None)):
    if not access_token:
        await websocket.close(code=1008)
        return
    try:
        username = verify_token(access_token)
    except HTTPException:
        await websocket.close(code=1008)
        return
    connection_id = await manager.connect(websocket, username)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast({"event": "message", "connection_id": connection_id, "username": username, "message": message})
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
