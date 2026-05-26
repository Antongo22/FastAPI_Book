import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from chapter11.app.main import app, manager


def test_authorized_websocket_rejects_missing_token_and_accepts_valid_token():
    manager.connections.clear()
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/authorized"):
            pass

    token = client.post("/api/auth/login", json={"username": "maria", "password": "secret"}).json()["access_token"]
    with client.websocket_connect(f"/ws/authorized?access_token={token}") as websocket:
        connected = websocket.receive_json()
        assert connected["username"] == "maria"
        websocket.send_text("secure hello")
        message = websocket.receive_json()
        assert message["message"] == "secure hello"
