from fastapi.testclient import TestClient

from chapter04.app.main import app


def test_error_handler_and_validation():
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/error-demo/throw")
    assert response.status_code == 500
    assert "тестовое исключение" in response.json()["error"]
    assert "X-Process-Time" in response.headers

    response = client.post("/api/error-demo/validate", json={"name": "", "age": 200})
    assert response.status_code == 400
    assert response.json()["errors"] == {"name": "Имя обязательно", "age": "Возраст должен быть от 0 до 150"}
