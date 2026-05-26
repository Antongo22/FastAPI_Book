from fastapi.testclient import TestClient

from chapter01.app.main import app


def test_calculator_add_and_divide():
    client = TestClient(app)
    response = client.post("/api/calculator/add", json={"a": 7, "b": 5})
    assert response.status_code == 200
    assert response.json() == {"result": 12, "operation": "add"}

    response = client.post("/api/calculator/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert response.json()["detail"] == "Деление на ноль невозможно"
