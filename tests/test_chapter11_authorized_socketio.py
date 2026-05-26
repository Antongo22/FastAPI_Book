from fastapi.testclient import TestClient

from chapter11.app.main import app, authorize_socketio, authorized_clients


def test_authorized_socketio_auth_helper_rejects_missing_and_accepts_valid_token():
    authorized_clients.clear()
    client = TestClient(app)

    assert authorize_socketio(None) is None
    assert authorize_socketio({"access_token": "bad-token"}) is None

    token = client.post("/api/auth/login", json={"username": "maria", "password": "secret"}).json()["access_token"]
    assert authorize_socketio({"access_token": token}) == "maria"


def test_authorized_socketio_info_endpoint():
    authorized_clients.clear()
    authorized_clients["sid-1"] = "maria"

    response = TestClient(app).get("/api/socket/info")

    assert response.status_code == 200
    assert response.json() == {"authorized_connections": 1, "users": ["maria"]}
