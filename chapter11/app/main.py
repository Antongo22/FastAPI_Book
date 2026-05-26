from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio


BASE_DIR = Path(__file__).resolve().parent.parent

fastapi_app = FastAPI(
    title="Глава 11: Auth Socket.IO",
    description="JWT protected Socket.IO",
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


import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
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


def authorize_socketio(auth: dict | None) -> str | None:
    token = (auth or {}).get("access_token") or (auth or {}).get("token")
    if not token:
        return None
    try:
        return verify_token(str(token))
    except HTTPException:
        return None


authorized_clients: dict[str, str] = {}


@fastapi_app.post("/api/auth/login")
async def login(request: LoginRequest):
    if not request.username or not request.password:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    return {"access_token": create_access_token(request.username), "token_type": "bearer", "username": request.username}


@fastapi_app.get("/api/socket/info")
async def socket_info():
    return {"authorized_connections": len(authorized_clients), "users": list(authorized_clients.values())}


@sio.event
async def connect(sid, environ, auth):
    username = authorize_socketio(auth)
    if username is None:
        return False
    authorized_clients[sid] = username
    await sio.emit("authorized", {"sid": sid, "username": username}, to=sid)


@sio.event
async def disconnect(sid):
    authorized_clients.pop(sid, None)


@sio.event
async def authorized_message(sid, data):
    username = authorized_clients.get(sid)
    if username is None:
        return
    await sio.emit("authorized_message", {
        "event": "authorized_message",
        "sid": sid,
        "username": username,
        "message": data.get("message", ""),
    })


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
