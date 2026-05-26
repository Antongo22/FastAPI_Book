from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 1: FastAPI basics",
    description="Middleware, REST API, OpenAPI",
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


from fastapi import HTTPException
from pydantic import BaseModel


class CalculationRequest(BaseModel):
    a: float
    b: float


@app.middleware("http")
async def add_lesson_header(request, call_next):
    response = await call_next(request)
    response.headers["X-FastAPI-Book-Chapter"] = "01"
    return response


@app.post("/api/calculator/add")
async def add(request: CalculationRequest):
    return {"result": request.a + request.b, "operation": "add"}


@app.post("/api/calculator/subtract")
async def subtract(request: CalculationRequest):
    return {"result": request.a - request.b, "operation": "subtract"}


@app.post("/api/calculator/multiply")
async def multiply(request: CalculationRequest):
    return {"result": request.a * request.b, "operation": "multiply"}


@app.post("/api/calculator/divide")
async def divide(request: CalculationRequest):
    if request.b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    return {"result": request.a / request.b, "operation": "divide"}
