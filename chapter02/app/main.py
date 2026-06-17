from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 2: Dependency Injection",
    description="Depends and lifetimes",
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


import logging
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Depends, Query


logger = logging.getLogger("chapter02")


@dataclass
class InstanceService:
    service_type: str
    id: str


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    environment: str


@dataclass(frozen=True)
class SingletonDiService:
    id: str
    name: str


@dataclass
class UserContext:
    username: str
    role: str


singleton_service = InstanceService("singleton", str(uuid4()))
app_settings = AppSettings(app_name="FastAPI Book Chapter 02", environment="development")
singleton_di_service = SingletonDiService(id=str(uuid4()), name="created-once")


def get_scoped_service() -> InstanceService:
    return InstanceService("scoped", str(uuid4()))


def get_singleton_service() -> InstanceService:
    return singleton_service


def get_transient_service() -> InstanceService:
    return InstanceService("transient", str(uuid4()))


def get_settings() -> AppSettings:
    return app_settings


def get_singleton_di_service() -> SingletonDiService:
    return singleton_di_service


def get_logger() -> logging.Logger:
    return logger


def get_current_user(
    username: str = Query("guest"),
    role: str = Query("student"),
) -> UserContext:
    return UserContext(username=username, role=role)


def shape(service: InstanceService) -> dict[str, str]:
    return {"id": service.id, "type": service.service_type}


@app.get("/api/dependency-injection/lifetimes")
async def lifetimes(
    scoped1: InstanceService = Depends(get_scoped_service),
    scoped2: InstanceService = Depends(get_scoped_service),
    singleton1: InstanceService = Depends(get_singleton_service),
    singleton2: InstanceService = Depends(get_singleton_service),
    transient1: InstanceService = Depends(get_transient_service, use_cache=False),
    transient2: InstanceService = Depends(get_transient_service, use_cache=False),
):
    return {
        "scoped": {
            "service1": shape(scoped1),
            "service2": shape(scoped2),
            "explanation": "Depends кеширует одинаковую зависимость в пределах запроса.",
        },
        "singleton": {
            "service1": shape(singleton1),
            "service2": shape(singleton2),
            "explanation": "Глобальный объект живет всё время работы приложения.",
        },
        "transient": {
            "service1": shape(transient1),
            "service2": shape(transient2),
            "explanation": "use_cache=False создает новый экземпляр при каждом вызове.",
        },
    }


@app.get("/api/dependency-injection/singleton-demo")
async def singleton_demo(service: SingletonDiService = Depends(get_singleton_di_service)):
    return {
        "id": service.id,
        "name": service.name,
        "explanation": "Один объект создан на уровне модуля, а dependency каждый раз возвращает ссылку на него.",
    }


@app.get("/api/dependency-injection/settings-demo")
async def settings_demo(settings: AppSettings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "explanation": "Endpoint получил settings через Depends(get_settings).",
    }


@app.get("/api/dependency-injection/current-user")
async def current_user(user: UserContext = Depends(get_current_user)):
    return {
        "username": user.username,
        "role": user.role,
        "explanation": "Dependency прочитала query-параметры и собрала UserContext.",
    }


@app.get("/api/dependency-injection/logger-demo")
async def logger_demo(
    message: str = "Тестовое сообщение",
    app_logger: logging.Logger = Depends(get_logger),
):
    app_logger.info("Получен запрос на логирование: %s", message)
    app_logger.warning("Это предупреждение через logging")
    return {"message": "Сообщения залогированы. Проверьте консоль.", "logged_message": message}
