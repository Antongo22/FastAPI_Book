from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="FastAPI Book Gateway", version="1.0.0", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

CHAPTERS = [
    {"number": 1, "port": 8001, "title": "Начало работы", "text": "FastAPI, middleware, REST API и OpenAPI."},
    {"number": 2, "port": 8002, "title": "Dependency Injection", "text": "Depends, request-scoped зависимости и singleton-сервисы."},
    {"number": 3, "port": 8003, "title": "HTTP Requests", "text": "Асинхронные запросы к внешним API через httpx."},
    {"number": 4, "port": 8004, "title": "Error Handling", "text": "Exception handlers, validation errors и custom middleware."},
    {"number": 5, "port": 8005, "title": "Jinja2 UI", "text": "Шаблоны, формы, binding и серверная валидация."},
    {"number": 6, "port": 8006, "title": "SQLAlchemy", "text": "DTO, SQLite, Alembic и CRUD операции."},
    {"number": 7, "port": 8007, "title": "JWT Authorization", "text": "Регистрация, вход, bearer token и protected endpoint."},
    {"number": 8, "port": 8008, "title": "Refresh Tokens", "text": "Обновление access token, revoke и logout."},
    {"number": 9, "port": 8009, "title": "WebSockets", "text": "Низкоуровневый чат и broadcast сообщений."},
    {"number": 10, "port": 8010, "title": "SignalR-подобный чат", "text": "Connection manager, direct send и groups."},
    {"number": 11, "port": 8011, "title": "Auth WebSockets", "text": "Проверка JWT перед WebSocket-соединением."},
    {"number": 12, "port": 8012, "title": "Тестирование", "text": "API, сервисный слой, WebSocket и in-memory БД."},
]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request, "chapters": CHAPTERS})
