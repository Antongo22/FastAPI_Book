from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


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


@app.get("/api/headers/demo")
async def headers_demo(
    user_agent: Annotated[str | None, Header()] = None,
    x_demo_client: Annotated[str | None, Header()] = None,
):
    return {
        "user_agent": user_agent,
        "x_demo_client": x_demo_client,
        "note": "Response header X-FastAPI-Book-Chapter добавляет middleware.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("chapter01.app.main:app", host="127.0.0.1", port=8001, reload=True)
