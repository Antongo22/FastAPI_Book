from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio


BASE_DIR = Path(__file__).resolve().parent.parent

fastapi_app = FastAPI(
    title="Глава 12: Socket.IO и тестирование",
    description="API, service layer, Socket.IO, in-memory DB",
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
from datetime import datetime

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter12.db")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class ChatGroup(Base):
    __tablename__ = "chat_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="group")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    sender: Mapped[str] = mapped_column(String(120), nullable=False)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("chat_groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    group: Mapped[ChatGroup | None] = relationship(back_populates="messages")


class MessageDto(BaseModel):
    id: int
    text: str
    sender: str
    group_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatGroupDto(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1)
    sender: str = Field(min_length=1)
    group_id: int | None = None


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def send_message(self, text: str, sender: str, group_id: int | None = None) -> Message:
        if group_id is not None and self.db.get(ChatGroup, group_id) is None:
            raise HTTPException(status_code=404, detail="Group not found")
        message = Message(text=text, sender=sender, group_id=group_id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, group_id: int | None = None) -> list[Message]:
        query = self.db.query(Message)
        if group_id is not None:
            query = query.filter(Message.group_id == group_id)
        return query.order_by(Message.created_at, Message.id).all()

    def create_group(self, name: str) -> ChatGroup:
        group = ChatGroup(name=name)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def get_groups(self) -> list[ChatGroup]:
        return self.db.query(ChatGroup).order_by(ChatGroup.id).all()


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


init_db()


@fastapi_app.post("/api/chat/messages", response_model=MessageDto)
async def send_message(request: SendMessageRequest, service: ChatService = Depends(get_chat_service)):
    return service.send_message(request.text, request.sender, request.group_id)


@fastapi_app.get("/api/chat/messages", response_model=list[MessageDto])
async def get_messages(group_id: int | None = None, service: ChatService = Depends(get_chat_service)):
    return service.get_messages(group_id)


@fastapi_app.post("/api/chat/groups", response_model=ChatGroupDto)
async def create_group(request: CreateGroupRequest, service: ChatService = Depends(get_chat_service)):
    return service.create_group(request.name)


@fastapi_app.get("/api/chat/groups", response_model=list[ChatGroupDto])
async def get_groups(service: ChatService = Depends(get_chat_service)):
    return service.get_groups()


socketio_clients: dict[str, str] = {}


def message_to_dict(message: Message) -> dict:
    return {
        "id": message.id,
        "text": message.text,
        "sender": message.sender,
        "group_id": message.group_id,
        "created_at": message.created_at.isoformat(),
    }


@fastapi_app.get("/api/chat/realtime")
async def realtime_info():
    return {
        "socketio_path": "/socket.io",
        "events": ["set_name", "join_group", "chat_message", "list_messages"],
        "connections": len(socketio_clients),
    }


@sio.event
async def connect(sid, environ):
    socketio_clients[sid] = "anonymous"
    await sio.enter_room(sid, "global")
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def disconnect(sid):
    socketio_clients.pop(sid, None)


@sio.event
async def set_name(sid, data):
    username = data.get("username", "anonymous")
    socketio_clients[sid] = username
    await sio.emit("name_set", {"sid": sid, "username": username}, to=sid)


@sio.event
async def join_group(sid, data):
    group_id = data.get("group_id")
    if group_id is not None:
        group_id = int(group_id)
    room = f"group:{group_id}" if group_id is not None else "global"
    await sio.enter_room(sid, room)
    await sio.emit("joined_group", {"room": room, "group_id": group_id}, to=sid)


@sio.event
async def chat_message(sid, data):
    sender = data.get("sender") or socketio_clients.get(sid, "anonymous")
    text = data.get("text") or data.get("message", "")
    group_id = data.get("group_id")
    if group_id is not None:
        group_id = int(group_id)
    with SessionLocal() as db:
        service = ChatService(db)
        message = service.send_message(text=text, sender=sender, group_id=group_id)
        payload = {"event": "chat_message", "message": message_to_dict(message)}
    room = f"group:{group_id}" if group_id is not None else "global"
    await sio.emit("chat_message", payload, room=room)


@sio.event
async def list_messages(sid, data):
    group_id = data.get("group_id")
    if group_id is not None:
        group_id = int(group_id)
    with SessionLocal() as db:
        service = ChatService(db)
        messages = [message_to_dict(message) for message in service.get_messages(group_id)]
    await sio.emit("messages", {"group_id": group_id, "items": messages}, to=sid)


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
app.dependency_overrides = fastapi_app.dependency_overrides
