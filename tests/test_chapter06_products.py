from fastapi.testclient import TestClient

from chapter06.app.main import Base, app, get_db
from tests.conftest import make_sqlite_override


def test_products_crud():
    _, override = make_sqlite_override(Base, get_db)
    app.dependency_overrides[get_db] = override
    try:
        client = TestClient(app)
        response = client.post("/api/products", json={"name": "Book", "description": "FastAPI", "price": "19.90", "stock": 3})
        assert response.status_code == 201
        product = response.json()
        assert product["name"] == "Book"

        response = client.get(f"/api/products/{product['id']}")
        assert response.status_code == 200
        assert response.json()["stock"] == 3

        response = client.put(f"/api/products/{product['id']}", json={"stock": 5})
        assert response.status_code == 204

        response = client.get("/api/products")
        assert response.json()[0]["stock"] == 5

        response = client.delete(f"/api/products/{product['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/products/{product['id']}").status_code == 404
    finally:
        app.dependency_overrides.clear()
