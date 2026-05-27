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


def test_headers_demo_reads_request_headers_and_middleware_adds_response_header():
    client = TestClient(app)
    response = client.get(
        "/api/headers/demo",
        headers={
            "User-Agent": "FastAPI-Book-Test",
            "X-Demo-Client": "pytest",
        },
    )

    assert response.status_code == 200
    assert response.json()["user_agent"] == "FastAPI-Book-Test"
    assert response.json()["x_demo_client"] == "pytest"
    assert response.headers["x-fastapi-book-chapter"] == "01"
