from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

LESSON_TOPICS = [
    {
        "name": "Переменная",
        "template": "{{ title }}",
        "description": "Jinja2 берёт значение из context и вставляет его в HTML.",
    },
    {
        "name": "Условие if",
        "template": "{% if show_hint %}",
        "description": "Блок показывается только тогда, когда значение истинное.",
    },
    {
        "name": "Цикл for",
        "template": "{% for topic in topics %}",
        "description": "Один HTML-фрагмент повторяется для каждого элемента списка.",
    },
]

app = FastAPI(
    title="Глава 5: Jinja2 basics",
    description="Templates, variables, if, for",
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


def demo_context(request: Request) -> dict:
    return {
        "request": request,
        "title": "Jinja2 demo",
        "student_name": "Анна",
        "topics": LESSON_TOPICS,
        "show_hint": True,
    }


@app.get("/jinja-demo", response_class=HTMLResponse, include_in_schema=False)
async def jinja_demo(request: Request):
    return templates.TemplateResponse(request, "jinja_demo.html", demo_context(request))


@app.get("/api/template-data")
async def template_data():
    return {
        "title": "Jinja2 demo",
        "student_name": "Анна",
        "topics": LESSON_TOPICS,
        "show_hint": True,
    }
