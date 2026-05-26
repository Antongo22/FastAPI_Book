from fastapi.testclient import TestClient

from chapter12.app.main import Base, app, get_db
from tests.conftest import make_sqlite_override


def test_chat_groups_and_messages():
    _, override = make_sqlite_override(Base, get_db)
    app.dependency_overrides[get_db] = override
    try:
        client = TestClient(app)
        group = client.post("/api/chat/groups", json={"name": "general"}).json()
        assert group["name"] == "general"

        response = client.post("/api/chat/messages", json={"text": "hello", "sender": "anna", "group_id": group["id"]})
        assert response.status_code == 200
        assert response.json()["sender"] == "anna"

        messages = client.get(f"/api/chat/messages?group_id={group['id']}").json()
        assert len(messages) == 1
        assert messages[0]["text"] == "hello"

        response = client.post("/api/chat/messages", json={"text": "bad", "sender": "anna", "group_id": 999})
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_chat_realtime_info_documents_socketio_events():
    response = TestClient(app).get("/api/chat/realtime")

    assert response.status_code == 200
    assert response.json()["socketio_path"] == "/socket.io"
    assert "chat_message" in response.json()["events"]
