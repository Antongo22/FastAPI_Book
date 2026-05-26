from fastapi.testclient import TestClient

from chapter08.app.main import Base, app, get_db
from tests.conftest import make_sqlite_override


def test_refresh_token_rotation():
    _, override = make_sqlite_override(Base, get_db)
    app.dependency_overrides[get_db] = override
    try:
        client = TestClient(app)
        response = client.post("/api/auth/register", json={"username": "ivan", "email": "ivan@example.com", "password": "secret"})
        assert response.status_code == 200
        first_refresh = response.json()["refresh_token"]

        response = client.post("/api/auth/refresh", json={"refresh_token": first_refresh})
        assert response.status_code == 200
        second_refresh = response.json()["refresh_token"]
        assert second_refresh != first_refresh

        response = client.post("/api/auth/refresh", json={"refresh_token": first_refresh})
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
