from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from chapter12.app.main import Base, ChatService, app, get_db, message_to_dict
from tests.conftest import make_sqlite_override


@pytest.fixture
def db_session():
    engine, _ = make_sqlite_override(Base, get_db)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def api_client():
    _, override = make_sqlite_override(Base, get_db)
    app.dependency_overrides[get_db] = override
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def test_message_to_dict_plain_test():
    message = SimpleNamespace(
        id=1,
        text="hello",
        sender="anna",
        group_id=None,
        created_at=datetime(2026, 1, 1, 12, 0),
    )

    result = message_to_dict(message)

    assert result["text"] == "hello"
    assert result["sender"] == "anna"
    assert result["created_at"] == "2026-01-01T12:00:00"


def test_chat_service_unit_saves_message(db_session):
    service = ChatService(db_session)
    group = service.create_group("unit")

    message = service.send_message(text="hello", sender="anna", group_id=group.id)

    assert message.id is not None
    assert service.get_messages(group.id)[0].text == "hello"


def test_chat_api_creates_message(api_client):
    group = api_client.post("/api/chat/groups", json={"name": "api"}).json()

    response = api_client.post(
        "/api/chat/messages",
        json={"text": "hello", "sender": "anna", "group_id": group["id"]},
    )

    assert response.status_code == 200
    assert response.json()["sender"] == "anna"


def test_chat_integration_group_message_flow(api_client):
    group = api_client.post("/api/chat/groups", json={"name": "integration"}).json()
    api_client.post(
        "/api/chat/messages",
        json={"text": "from integration", "sender": "student", "group_id": group["id"]},
    )

    response = api_client.get(f"/api/chat/messages?group_id={group['id']}")

    assert response.status_code == 200
    assert response.json()[0]["text"] == "from integration"


def test_chat_api_returns_404_for_missing_group(api_client):
    response = api_client.post(
        "/api/chat/messages",
        json={"text": "bad", "sender": "anna", "group_id": 999},
    )

    assert response.status_code == 404


def test_chat_api_lists_groups(api_client):
    api_client.post("/api/chat/groups", json={"name": "first"})
    api_client.post("/api/chat/groups", json={"name": "second"})

    response = api_client.get("/api/chat/groups")

    assert response.status_code == 200
    assert [group["name"] for group in response.json()] == ["first", "second"]
