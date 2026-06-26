from fastapi.testclient import TestClient

from chapter07.app.main import USERS, app


def test_jwt_auth_and_protected_route():
    USERS.clear()
    client = TestClient(app)
    response = client.post("/api/auth/register", json={"username": "anna", "email": "anna@example.com", "password": "secret"})
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json()["access_token"] == token

    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "anna"

    response = client.get("/api/protected")
    assert response.status_code == 401


def test_json_login_still_accepts_username_and_password_body():
    USERS.clear()
    client = TestClient(app)
    client.post("/api/auth/register", json={"username": "ivan", "email": "ivan@example.com", "password": "secret"})

    response = client.post("/api/auth/login", json={"username": "ivan", "password": "secret"})

    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json()["access_token"] == token
    assert response.json()["token_type"] == "bearer"


def test_swagger_authorize_password_flow_can_login_with_form_data():
    USERS.clear()
    client = TestClient(app)
    client.post("/api/auth/register", json={"username": "maria", "email": "maria@example.com", "password": "secret"})

    response = client.post(
        "/api/auth/token",
        data={"username": "maria", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert response.json()["token"] == token
    assert response.json()["token_type"] == "bearer"

    response = client.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "maria"
