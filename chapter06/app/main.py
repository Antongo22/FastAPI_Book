from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 6: SQLModel",
    description="SQLite, SQLModel, Alembic, CRUD",
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
from datetime import datetime
from decimal import Decimal

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Column, DateTime, Field, Numeric, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'chapter06.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def make_async_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite://") and not database_url.startswith("sqlite+aiosqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return database_url


def make_sync_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return database_url


ASYNC_DATABASE_URL = make_async_database_url(DATABASE_URL)
SYNC_DATABASE_URL = make_sync_database_url(DATABASE_URL)


def make_async_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url in {"sqlite+aiosqlite://", "sqlite+aiosqlite:///:memory:"}:
        kwargs["poolclass"] = StaticPool
    return create_async_engine(database_url, **kwargs)


engine = make_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = SQLModel


class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="general", max_length=80)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0, sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0, ge=0)


class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))


class ProductRead(ProductBase):
    id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


@app.get("/api/products", response_model=list[ProductRead])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.exec(select(Product).order_by(Product.id))
    return result.all()


@app.get("/api/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(request: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = Product(**request.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@app.put("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(product_id: int, request: ProductUpdate, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
