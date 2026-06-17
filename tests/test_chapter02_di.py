from fastapi.testclient import TestClient

from chapter02.app.main import app


def test_lifetime_shapes():
    client = TestClient(app)
    payload = client.get("/api/dependency-injection/lifetimes").json()
    assert payload["scoped"]["service1"]["id"] == payload["scoped"]["service2"]["id"]
    assert payload["singleton"]["service1"]["id"] == payload["singleton"]["service2"]["id"]
    assert payload["transient"]["service1"]["id"] != payload["transient"]["service2"]["id"]


def test_dependency_examples_are_runnable():
    client = TestClient(app)

    singleton_first = client.get("/api/dependency-injection/singleton-demo").json()
    singleton_second = client.get("/api/dependency-injection/singleton-demo").json()
    assert singleton_first["id"] == singleton_second["id"]
    assert singleton_first["name"] == "created-once"

    settings = client.get("/api/dependency-injection/settings-demo").json()
    assert settings["app_name"] == "FastAPI Book Chapter 02"
    assert settings["environment"] == "development"

    user = client.get(
        "/api/dependency-injection/current-user",
        params={"username": "anna", "role": "admin"},
    ).json()
    assert user["username"] == "anna"
    assert user["role"] == "admin"

    logger_response = client.get(
        "/api/dependency-injection/logger-demo",
        params={"message": "hello"},
    ).json()
    assert logger_response["logged_message"] == "hello"
