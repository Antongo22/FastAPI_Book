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
from sqlmodel import Column, DateTime, Field, Numeric, Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter06.db")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)
Base = SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))


class ProductRead(SQLModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int


class ProductCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0)
    stock: int = Field(default=0, ge=0)


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)


def init_db() -> None:
    SQLModel.metadata.create_all(bind=engine)


def get_db():
    with Session(engine) as db:
        yield db


init_db()


@app.get("/api/products", response_model=list[ProductRead])
async def get_products(db: Session = Depends(get_db)):
    return db.exec(select(Product).order_by(Product.id)).all()


@app.get("/api/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(product_id: int, request: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
