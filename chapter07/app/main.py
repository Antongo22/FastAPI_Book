from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 7: JWT Authorization",
    description="Authentication and authorization",
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

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
USERS: dict[str, dict] = {}


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    username: str
    role: str
    expires: datetime


def create_access_token(username: str, role: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from error
    user = USERS.get(str(username))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if any(user["email"] == request.email for user in USERS.values()):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    USERS[request.username] = {
        "username": request.username,
        "email": request.email,
        "password_hash": pwd_context.hash(request.password),
        "role": "user",
    }
    token, expires = create_access_token(request.username, "user")
    return AuthResponse(token=token, username=request.username, role="user", expires=expires)


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    user = USERS.get(request.username)
    if user is None or not pwd_context.verify(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    token, expires = create_access_token(user["username"], user["role"])
    return AuthResponse(token=token, username=user["username"], role=user["role"], expires=expires)


@app.get("/api/protected")
async def protected(user: dict = Depends(get_current_user)):
    return {"message": "Это защищенный endpoint", "username": user["username"], "role": user["role"]}
