from fastapi.testclient import TestClient

from chapter01.app.main import app as chapter01_app
from chapter02.app.main import app as chapter02_app
from chapter03.app.main import app as chapter03_app
from chapter04.app.main import app as chapter04_app
from chapter05.app.main import app as chapter05_app
from chapter06.app.main import app as chapter06_app
from chapter07.app.main import app as chapter07_app
from chapter08.app.main import app as chapter08_app
from chapter09.app.main import app as chapter09_app
from chapter10.app.main import app as chapter10_app
from chapter11.app.main import app as chapter11_app
from chapter12.app.main import app as chapter12_app
from gateway.app.main import app as gateway_app


CHAPTER_APPS = [
    chapter01_app,
    chapter02_app,
    chapter03_app,
    chapter04_app,
    chapter05_app,
    chapter06_app,
    chapter07_app,
    chapter08_app,
    chapter09_app,
    chapter10_app,
    chapter11_app,
    chapter12_app,
]


def test_gateway_page_renders_chapter_cards():
    response = TestClient(gateway_app).get("/")
    assert response.status_code == 200
    assert "Учебник по Python FastAPI" in response.text
    assert response.text.count("chapter-card") == 12


def test_all_chapter_pages_render_navigation_and_deep_sections():
    for app in CHAPTER_APPS:
        response = TestClient(app).get("/")
        assert response.status_code == 200
        assert "← На главную" in response.text
        assert "Как проходит запрос" in response.text
        assert "Разбор кода" in response.text
        assert "Endpoint-ы для проверки" in response.text
        assert "Если совсем по-простому" in response.text
        assert "Построчный разбор" in response.text
        assert "Типичные ошибки новичков" in response.text
        assert "Полное решение задачи" in response.text
        assert "Короткая версия решения" in response.text


def test_chapter_form_render():
    response = TestClient(chapter05_app).get("/contact")
    assert response.status_code == 200
    assert "Форма контакта" in response.text
    assert "← На главную" in response.text
