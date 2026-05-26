from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 5: Jinja2 UI",
    description="Templates, forms, validation",
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


from fastapi import Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError, field_validator


class ContactForm(BaseModel):
    name: str
    email: str
    message: str

    @field_validator("name", "email", "message")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Поле обязательно")
        return value.strip()

    @field_validator("email")
    @classmethod
    def email_has_at(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Email должен содержать @")
        return value


@app.get("/contact", response_class=HTMLResponse, include_in_schema=False)
async def contact_page(request: Request):
    return templates.TemplateResponse(request, "contact.html", {"request": request, "errors": {}, "values": {}, "sent": False})


@app.post("/contact", response_class=HTMLResponse, include_in_schema=False)
async def submit_contact(request: Request, name: str = Form(""), email: str = Form(""), message: str = Form("")):
    values = {"name": name, "email": email, "message": message}
    try:
        ContactForm(**values)
    except ValidationError as error:
        errors = {str(item["loc"][0]): item["msg"] for item in error.errors()}
        return templates.TemplateResponse(request, "contact.html", {"request": request, "errors": errors, "values": values, "sent": False}, status_code=400)
    return templates.TemplateResponse(request, "contact.html", {"request": request, "errors": {}, "values": values, "sent": True})


@app.post("/api/contact")
async def api_contact(form: ContactForm):
    return {"message": "Форма принята", "data": form.model_dump()}
