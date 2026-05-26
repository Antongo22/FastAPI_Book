from fastapi.testclient import TestClient

from chapter02.app.main import app


def test_lifetime_shapes():
    client = TestClient(app)
    payload = client.get("/api/dependency-injection/lifetimes").json()
    assert payload["scoped"]["service1"]["id"] == payload["scoped"]["service2"]["id"]
    assert payload["singleton"]["service1"]["id"] == payload["singleton"]["service2"]["id"]
    assert payload["transient"]["service1"]["id"] != payload["transient"]["service2"]["id"]
