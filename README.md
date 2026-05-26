# Учебник по Python FastAPI

Полное руководство для начинающих разработчиков по изучению FastAPI. Проект повторяет идею `Asp_Book`: каждая глава является отдельным запускаемым приложением с теорией, демонстрацией, практической задачей и ответом.

## Структура проекта

- **Gateway** (порт 8000) - главная страница с навигацией по главам
- **Chapter 01** (порт 8001) - Начало работы: FastAPI, middleware, REST API, OpenAPI
- **Chapter 02** (порт 8002) - Dependency Injection через `Depends`
- **Chapter 03** (порт 8003) - HTTP Requests через `httpx`
- **Chapter 04** (порт 8004) - Error Handling и custom middleware
- **Chapter 05** (порт 8005) - Jinja2 UI, формы и валидация
- **Chapter 06** (порт 8006) - SQLAlchemy, DTO, Alembic, SQLite, CRUD
- **Chapter 07** (порт 8007) - Authentication vs Authorization, JWT
- **Chapter 08** (порт 8008) - Refresh Tokens
- **Chapter 09** (порт 8009) - WebSockets
- **Chapter 10** (порт 8010) - Высокоуровневый WebSocket-чат вместо SignalR
- **Chapter 11** (порт 8011) - Авторизация WebSocket-соединений
- **Chapter 12** (порт 8012) - Тестирование API, сервисов и БД

## Требования

- Python 3.12 или выше
- Docker и Docker Compose для запуска всех глав

## Локальный запуск одной главы

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn chapter01.app.main:app --reload --port 8001
```

Документация API доступна по адресам `/docs` и `/swagger`.

## Запуск всех глав через Docker Compose

```bash
docker compose up --build
```

Если Docker Desktop ограничен по памяти, используйте последовательную сборку:

```bash
./scripts/compose-up.sh
```

## Проверка качества

```bash
./scripts/validate.sh
```

Скрипт выполняет компиляцию Python-файлов, импорт ключевых приложений и `pytest`.

## Полезные команды

```bash
uvicorn gateway.app.main:app --reload --port 8000
uvicorn chapter06.app.main:app --reload --port 8006
pytest
docker compose config
```

## Alembic в главе 6

Глава 6 создаёт таблицы автоматически для удобства демо, но содержит минимальную Alembic-конфигурацию. Из папки проекта можно выполнить:

```bash
cd chapter06
alembic upgrade head
```

## Рекомендации по изучению

Изучайте главы последовательно, запускайте примеры через Swagger UI, меняйте код и проверяйте поведение тестами.
