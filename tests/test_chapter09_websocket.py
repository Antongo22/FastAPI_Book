from fastapi.testclient import TestClient

from chapter09.app.main import app, manager


def test_websocket_broadcast():
    manager.active_connections.clear()
    client = TestClient(app)
    with client.websocket_connect("/ws") as first:
        first_connected = first.receive_json()
        with client.websocket_connect("/ws") as second:
            second.receive_json()
            first.send_text("hello")
            first_message = first.receive_json()
            second_message = second.receive_json()
            assert first_message["message"] == "hello"
            assert second_message["message"] == "hello"
            assert first_message["connection_id"] == first_connected["connection_id"]
