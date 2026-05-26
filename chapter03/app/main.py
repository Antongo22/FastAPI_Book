from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 3: HTTP Requests",
    description="httpx AsyncClient",
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


import httpx
from fastapi import Depends, HTTPException
from pydantic import BaseModel


JSONPLACEHOLDER = "https://jsonplaceholder.typicode.com"


class CreatePostRequest(BaseModel):
    title: str
    body: str
    user_id: int


class ExternalApiService:
    def __init__(self, base_url: str = JSONPLACEHOLDER):
        self.base_url = base_url

    async def get_post(self, post_id: int) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}")
            response.raise_for_status()
            return response.json()

    async def get_posts(self) -> list[dict]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get("/posts")
            response.raise_for_status()
            return response.json()

    async def create_post(self, request: CreatePostRequest) -> dict:
        payload = {"title": request.title, "body": request.body, "userId": request.user_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.post("/posts", json=payload)
            response.raise_for_status()
            return response.json()


def get_external_api_service() -> ExternalApiService:
    return ExternalApiService()


def map_http_error(error: httpx.HTTPError) -> HTTPException:
    status_code = 502
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
    return HTTPException(status_code=status_code, detail=str(error))


@app.get("/api/http-client/direct/{post_id}")
async def get_post_direct(post_id: int):
    try:
        async with httpx.AsyncClient(base_url=JSONPLACEHOLDER, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


@app.get("/api/http-client/post/{post_id}")
async def get_post(post_id: int, service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.get_post(post_id)
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


@app.get("/api/http-client/posts")
async def get_posts(service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.get_posts()
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


@app.post("/api/http-client/post")
async def create_post(request: CreatePostRequest, service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.create_post(request)
    except httpx.HTTPError as error:
        raise map_http_error(error) from error
