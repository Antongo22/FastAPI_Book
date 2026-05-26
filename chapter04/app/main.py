from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 4: Error Handling",
    description="Exception handlers and middleware",
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


import time

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class DemoError(Exception):
    pass


class ValidationRequest(BaseModel):
    name: str = ""
    age: int = 0


@app.middleware("http")
async def request_logging_middleware(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started:.6f}"
    return response


@app.exception_handler(DemoError)
async def demo_error_handler(request, exc: DemoError):
    return JSONResponse(status_code=500, content={"error": str(exc), "path": str(request.url.path)})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Validation failed", "details": exc.errors()})


@app.get("/api/error-demo/throw")
async def throw_exception():
    raise DemoError("Это тестовое исключение для демонстрации обработки ошибок")


@app.get("/api/error-demo/badrequest")
async def bad_request_demo():
    raise HTTPException(status_code=400, detail="Это пример BadRequest ответа")


@app.post("/api/error-demo/validate")
async def validate_demo(request: ValidationRequest):
    errors: dict[str, str] = {}
    if not request.name:
        errors["name"] = "Имя обязательно"
    if request.age < 0 or request.age > 150:
        errors["age"] = "Возраст должен быть от 0 до 150"
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})
    return {"message": "Валидация прошла успешно", "data": request.model_dump()}


@app.get("/api/error-demo/success")
async def success():
    return {"message": "Запрос выполнен успешно"}
