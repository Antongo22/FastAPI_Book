from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 8: Refresh Tokens",
    description="Token rotation and revoke",
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


import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


SECRET_KEY = "fastapi-book-development-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserRecord(BaseModel):
    username: str
    email: str
    password_hash: str
    role: str = "user"


class StoredRefreshToken(BaseModel):
    token: str
    username: str
    expires_at: datetime
    revoked: bool = False
    revoked_at: datetime | None = None


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    role: str
    access_token_expires: datetime
    refresh_token_expires: datetime


USERS: dict[str, UserRecord] = {}
REFRESH_TOKENS: dict[str, StoredRefreshToken] = {}


def create_access_token(user: UserRecord) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.username, "username": user.username, "role": user.role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires


def create_refresh_token(user: UserRecord) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    REFRESH_TOKENS[token] = StoredRefreshToken(token=token, username=user.username, expires_at=expires)
    return token, expires


def revoke_refresh_token(stored: StoredRefreshToken) -> None:
    stored.revoked = True
    stored.revoked_at = datetime.utcnow()


def authenticate_user(username: str, password: str) -> UserRecord:
    user = USERS.get(username)
    if user is None or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    return user


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserRecord:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = str(payload["sub"])
    except (JWTError, KeyError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from error
    user = USERS.get(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if any(user.email == request.email for user in USERS.values()):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user = UserRecord(
        username=request.username,
        email=request.email,
        password_hash=pwd_context.hash(request.password),
        role="user",
    )
    USERS[user.username] = user
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(user)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, username=user.username, role=user.role, access_token_expires=access_expires, refresh_token_expires=refresh_expires)


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(user)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, username=user.username, role=user.role, access_token_expires=access_expires, refresh_token_expires=refresh_expires)


@app.post("/api/auth/refresh", response_model=AuthResponse)
async def refresh(request: RefreshTokenRequest):
    stored = REFRESH_TOKENS.get(request.refresh_token)
    if stored is None or stored.revoked or stored.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    revoke_refresh_token(stored)
    user = USERS.get(stored.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(user)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, username=user.username, role=user.role, access_token_expires=access_expires, refresh_token_expires=refresh_expires)


@app.post("/api/auth/revoke")
async def revoke(request: RefreshTokenRequest):
    stored = REFRESH_TOKENS.get(request.refresh_token)
    if stored is not None and not stored.revoked:
        revoke_refresh_token(stored)
    return {"message": "Refresh token отозван"}


@app.post("/api/auth/logout")
async def logout(user: UserRecord = Depends(get_current_user)):
    count = 0
    for stored in REFRESH_TOKENS.values():
        if stored.username == user.username and not stored.revoked:
            revoke_refresh_token(stored)
            count += 1
    return {"message": f"Все сессии завершены. Отозвано токенов: {count}"}
