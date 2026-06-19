from fastapi.testclient import TestClient
from html import unescape

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

TASK_ANSWER_MARKERS = [
    ("chapter01", chapter01_app, ["power"]),
    ("chapter02", chapter02_app, ["pretty-log", "get_log_prefix"]),
    ("chapter03", chapter03_app, ["get_post_comments", "/comments"]),
    ("chapter04", chapter04_app, ["NotReadyError", "not-ready"]),
    ("chapter05", chapter05_app, ["RegistrationForm", "/register", "register.html"]),
    ("chapter06", chapter06_app, ["category"]),
    ("chapter07", chapter07_app, ["require_admin", "admin_area"]),
    ("chapter08", chapter08_app, ["revoked_at"]),
    ("chapter09", chapter09_app, ["/who"]),
    ("chapter10", chapter10_app, ["leave_room", "left_room"]),
    ("chapter11", chapter11_app, ["admin_message"]),
    ("chapter12", chapter12_app, ["delete_group", "group_deleted"]),
]

FULL_ANSWER_CONTEXT_MARKERS = [
    (chapter01_app, ["from typing import Annotated", "app = FastAPI", "async def power"]),
    (chapter02_app, ["import logging", "app = FastAPI", "def get_log_prefix", "async def pretty_log"]),
    (chapter03_app, ["import httpx", "JSONPLACEHOLDER", "class ExternalApiService", "async def get_post_comments"]),
    (chapter04_app, ["import time", "app = FastAPI", "class NotReadyError", "async def not_ready"]),
    (chapter05_app, ["from pathlib import Path", "Jinja2Templates", "class RegistrationForm", "<!doctype html>"]),
    (chapter06_app, ["import os", "class Product", "class ProductDto", "def upgrade()"]),
    (chapter07_app, ["import os", "OAuth2PasswordBearer", "def require_admin", "async def admin_area"]),
    (chapter08_app, ["import secrets", "class RefreshToken", "revoked_at", "def revoke_token"]),
    (chapter09_app, ["from uuid import uuid4", "class ConnectionManager", 'message == "/who"']),
    (chapter10_app, ["import socketio", "socketio_rooms", "async def leave_room", "app = socketio.ASGIApp"]),
    (chapter11_app, ["import socketio", "def verify_user_token", "async def admin_message", "app = socketio.ASGIApp"]),
    (chapter12_app, ["import socketio", "class ChatService", "def delete_group", "from fastapi.testclient import TestClient"]),
]


def html_section(text: str, start_marker: str, end_marker: str) -> str:
    return text.split(start_marker, maxsplit=1)[1].split(end_marker, maxsplit=1)[0]


def test_gateway_page_renders_chapter_cards():
    response = TestClient(gateway_app).get("/")
    assert response.status_code == 200
    assert "Учебник по Python FastAPI" in response.text
    assert "Тест сокетов" in response.text
    assert "http://localhost:8010/socket-tester" in response.text
    assert response.text.count("chapter-card") == 12


def test_all_chapter_pages_render_navigation_and_deep_sections():
    for app in CHAPTER_APPS:
        response = TestClient(app).get("/")
        assert response.status_code == 200
        assert "← На главную" in response.text
        assert "Учебник" in response.text
        assert "Учебный план" in response.text
        assert "Структура файлов главы" in response.text
        assert "Команды запуска" in response.text
        assert "Как проходит запрос" in response.text
        assert "Разбор кода" in response.text
        assert "Endpoint-ы для проверки" in response.text
        assert "Если совсем по-простому" in response.text
        assert "Построчный разбор" in response.text
        assert "Типичные ошибки новичков" in response.text
        removed_code_notice = "Код урока, " + "не ответ"
        assert removed_code_notice not in response.text
        assert ">Задача<" in response.text
        assert "Порядок работы" in response.text
        assert "Критерии готовности" in response.text
        assert "Практика по уровням" not in response.text
        assert "Контрольные вопросы" in response.text
        assert "Полное решение задачи" in response.text
        assert "Единственная" not in response.text
        assert "единственной" not in response.text
        assert "Короткая версия решения" not in response.text
        assert "Разбор решения" in response.text


def test_code_tab_does_not_show_task_answers():
    for service, app, markers in TASK_ANSWER_MARKERS:
        response = TestClient(app).get("/")
        assert response.status_code == 200
        code_tab = html_section(response.text, '<section id="code"', '<section id="task"')

        for marker in markers:
            assert marker not in code_tab, f"{service} leaks task answer marker into code tab: {marker}"


def test_answers_include_full_code_context_not_only_fragments():
    for app, markers in FULL_ANSWER_CONTEXT_MARKERS:
        response = TestClient(app).get("/")
        assert response.status_code == 200
        answers = unescape(html_section(response.text, '<section id="answers"', "</body>"))

        for marker in markers:
            assert marker in answers, f"answer is missing full-code context marker: {marker}"


def test_chapter01_page_explains_headers():
    response = TestClient(chapter01_app).get("/")
    assert response.status_code == 200
    assert "Headers подробнее" in response.text
    assert "Content-Type" in response.text
    assert "/api/headers/demo" in response.text


def test_chapter01_answers_skip_template_setup_noise():
    response = TestClient(chapter01_app).get("/")
    assert response.status_code == 200
    answers = html_section(response.text, '<section id="answers"', "</body>")

    assert "Полный API-код после изменения" in answers
    assert "StaticFiles" not in answers
    assert "Jinja2Templates" not in answers
    assert "app.mount" not in answers


def test_chapter02_page_expands_dependency_injection_for_beginners():
    response = TestClient(chapter02_app).get("/")
    assert response.status_code == 200

    assert "Зачем вообще нужен Dependency Injection" in response.text
    assert "Без DI и с DI" in response.text
    assert "Depends не вызывает функцию сразу" in response.text
    assert "Как прописать singleton DI" in response.text
    assert "Время жизни объектов простыми словами" in response.text
    assert "/api/dependency-injection/singleton-demo" in response.text
    assert "get_singleton_di_service" in response.text
    assert "/api/dependency-injection/settings-demo" in response.text
    assert "/api/dependency-injection/current-user" in response.text
    assert "Query-параметры внутри dependency" in response.text
    assert "get_request_id" not in response.text
    assert "request-id" not in response.text


def test_chapter02_practice_and_answers_are_distinct():
    response = TestClient(chapter02_app).get("/")
    assert response.status_code == 200

    practice = html_section(response.text, '<section id="task"', '<section id="answers"')
    answers = html_section(response.text, '<section id="answers"', "</body>")

    assert "Порядок работы без готового кода" in practice
    assert "Сделайте простой DI для красивого вывода логов" in practice
    assert "def get_log_prefix" not in practice
    assert "formatted_message = f" not in practice
    assert "Где должен лежать код" not in practice

    assert "Где должен лежать код" in answers
    assert "def get_log_prefix" in answers
    assert "formatted_message = f" in answers


def test_chapter03_task_uses_real_public_external_api():
    response = TestClient(chapter03_app).get("/")
    assert response.status_code == 200

    practice = html_section(response.text, '<section id="task"', '<section id="answers"')
    answers = html_section(response.text, '<section id="answers"', "</body>")

    assert "https://jsonplaceholder.typicode.com/posts/1/comments" in practice
    assert "реальном открытом тестовом API" in practice
    assert "Не возвращайте локальный список" in practice
    assert "не на локальной заглушке" in practice

    assert "JSONPLACEHOLDER" in answers
    assert "/posts/{post_id}/comments" in answers


def test_chapter01_code_tab_is_api_lesson_not_page_shell():
    response = TestClient(chapter01_app).get("/")
    assert response.status_code == 200
    code_tab = html_section(response.text, '<section id="code"', '<section id="task"')

    assert "Ключевые фрагменты API без решения задачи" in code_tab
    assert "Полный учебный код приложения" not in code_tab
    assert "StaticFiles" not in code_tab
    assert "Jinja2Templates" not in code_tab
    assert "BASE_DIR" not in code_tab
    assert "app.mount" not in code_tab


def test_socket_code_tabs_do_not_repeat_full_answer_blocks():
    chapter09_response = TestClient(chapter09_app).get("/")
    chapter10_response = TestClient(chapter10_app).get("/")

    assert chapter09_response.status_code == 200
    assert chapter10_response.status_code == 200

    chapter09_code = html_section(chapter09_response.text, '<section id="code"', '<section id="task"')
    chapter10_code = html_section(chapter10_response.text, '<section id="code"', '<section id="task"')

    assert "Полный receive loop после изменения" not in chapter09_code
    assert "async def websocket_endpoint" not in chapter09_code
    assert "while True" not in chapter09_code
    assert "receive_text" not in chapter09_code

    assert "Полный блок Socket.IO событий для комнат" not in chapter10_code
    assert "async def leave_room" not in chapter10_code
    assert "async def join_room" not in chapter10_code
    assert "async def chat_message" not in chapter10_code


def test_chapter_form_render():
    response = TestClient(chapter05_app).get("/contact")
    assert response.status_code == 200
    assert "Форма контакта" in response.text
    assert "← На главную" in response.text


def test_chapter10_uses_socketio_wording_without_old_comparison():
    chapter_response = TestClient(chapter10_app).get("/")
    gateway_response = TestClient(gateway_app).get("/")
    old_comparison_term = "Signal" + "R"

    assert chapter_response.status_code == 200
    assert gateway_response.status_code == 200
    assert "Socket.IO" in chapter_response.text
    assert "Socket.IO чат" in gateway_response.text
    assert old_comparison_term not in chapter_response.text
    assert old_comparison_term not in gateway_response.text


def test_chapter10_socket_tester_page_renders_defaults():
    response = TestClient(chapter10_app).get("/socket-tester")

    assert response.status_code == 200
    assert "Тест сокетов" in response.text
    assert "http://localhost:8010" in response.text
    assert "/socket.io" in response.text
    assert "ws://localhost:8010/ws/chat?group=general" in response.text
