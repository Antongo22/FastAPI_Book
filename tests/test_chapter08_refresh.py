from fastapi.testclient import TestClient

from chapter08.app.main import REFRESH_TOKENS, USERS, app


def test_refresh_token_rotation():
    USERS.clear()
    REFRESH_TOKENS.clear()
    client = TestClient(app)
    response = client.post("/api/auth/register", json={"username": "ivan", "email": "ivan@example.com", "password": "secret"})
    assert response.status_code == 200
    first_refresh = response.json()["refresh_token"]

    response = client.post("/api/auth/refresh", json={"refresh_token": first_refresh})
    assert response.status_code == 200
    second_refresh = response.json()["refresh_token"]
    assert second_refresh != first_refresh
    assert REFRESH_TOKENS[first_refresh].revoked is True
    assert REFRESH_TOKENS[first_refresh].revoked_at is not None

    response = client.post("/api/auth/refresh", json={"refresh_token": first_refresh})
    assert response.status_code == 401
