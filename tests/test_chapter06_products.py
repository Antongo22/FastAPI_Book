import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel.ext.asyncio.session import AsyncSession

from chapter06.app.main import Base, app, get_db


def make_async_sqlite_override():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async def create_schema():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestingSessionLocal() as db:
            yield db

    return engine, override_get_db


def test_products_crud():
    engine, override = make_async_sqlite_override()
    app.dependency_overrides[get_db] = override
    try:
        with TestClient(app) as client:
            response = client.post("/api/products", json={"name": "Book", "description": "FastAPI", "price": "19.90", "stock": 3})
            assert response.status_code == 201
            product = response.json()
            assert product["name"] == "Book"
            assert product["category"] == "general"

            response = client.get(f"/api/products/{product['id']}")
            assert response.status_code == 200
            assert response.json()["stock"] == 3

            response = client.put(f"/api/products/{product['id']}", json={"stock": 5, "category": "books"})
            assert response.status_code == 204

            response = client.get("/api/products")
            assert response.json()[0]["stock"] == 5
            assert response.json()[0]["category"] == "books"

            response = client.delete(f"/api/products/{product['id']}")
            assert response.status_code == 204
            assert client.get(f"/api/products/{product['id']}").status_code == 404
    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())
