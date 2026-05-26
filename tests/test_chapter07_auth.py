from fastapi.testclient import TestClient

from chapter07.app.main import USERS, app


def test_jwt_auth_and_protected_route():
    USERS.clear()
    client = TestClient(app)
    response = client.post("/api/auth/register", json={"username": "anna", "email": "anna@example.com", "password": "secret"})
    assert response.status_code == 200
    token = response.json()["token"]

    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "anna"

    response = client.get("/api/protected")
    assert response.status_code == 401
