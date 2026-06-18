from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def paragraphs(items: list[str]) -> str:
    return "\n".join(f"<p>{item}</p>" for item in items)


def list_items(items: list[str]) -> str:
    return "\n".join(f"<li>{item}</li>" for item in items)


def endpoint_cards(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f'<article class="endpoint-card"><strong><code>{escape(method)}</code></strong><span>{description}</span></article>'
        for method, description in items
    )


def code_block(code: str) -> str:
    return f"<pre><code>{{% raw %}}{escape(code.strip())}{{% endraw %}}</code></pre>"


def definition_items(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f"<dt>{term}</dt><dd>{description}</dd>"
        for term, description in items
    )


def render_solution_sections(sections: list[dict[str, object]]) -> str:
    rendered = []
    for index, section in enumerate(sections, start=1):
        body = section.get("body", "")
        code = section.get("code")
        items = section.get("items")
        checks = section.get("checks")
        block = [f'<article class="info-box"><h2>{index}. {section["title"]}</h2>']
        if body:
            block.append(f"<p>{body}</p>")
        if items:
            block.append(f'<ul class="flow-list">{list_items(items)}</ul>')
        if code:
            block.append(code_block(str(code)))
        if checks:
            block.append(f'<div class="endpoint-grid">{endpoint_cards(checks)}</div>')
        block.append("</article>")
        rendered.append("\n".join(block))
    return "\n".join(rendered)


def render_extra_sections(sections: list[dict[str, object]]) -> str:
    rendered = []
    for section in sections:
        block = [f'<article class="info-box"><h2>{section["title"]}</h2>']
        body = section.get("body")
        items = section.get("items")
        code = section.get("code")
        if body:
            block.append(paragraphs([body] if isinstance(body, str) else list(body)))
        if items:
            block.append(f'<ul class="flow-list">{list_items([items] if isinstance(items, str) else list(items))}</ul>')
        if code:
            block.append(code_block(str(code)))
        block.append("</article>")
        rendered.append("\n".join(block))
    return "\n".join(rendered)


def task_check_cards(service: str) -> str:
    criteria = TASK_CRITERIA.get(service)
    if criteria:
        return endpoint_cards(criteria)

    checks: list[tuple[str, str]] = []
    for section in FULL_SOLUTIONS[service]:
        section_checks = section.get("checks")
        if section_checks:
            checks.extend(section_checks)  # type: ignore[arg-type]
    if not checks:
        checks = [
            ("Код добавлен", "Изменения внесены в файлы, перечисленные в задаче."),
            ("Ручная проверка", "Сценарий из полного ответа выполняется без ошибки."),
            ("Тесты", "Проверки проекта проходят после изменения."),
        ]
    return endpoint_cards(checks)


def render_single_task(service: str, data: dict) -> str:
    first_solution = FULL_SOLUTIONS[service][0]
    plan_items = PRACTICE_STEPS.get(service, first_solution.get("items", []))
    plan_html = f'<ul class="flow-list">{list_items(plan_items)}</ul>' if plan_items else ""
    return f"""
                <article class="info-box">
                    <h2>Задача</h2>
                    <p>Сначала попробуйте решить без вкладки “Ответы”. Ниже есть подсказки и критерии, но нет готового кода.</p>
                    <div class="callout">{data["task"]}</div>
                </article>

                <article class="info-box">
                    <h2>Порядок работы без готового кода</h2>
                    {plan_html}
                </article>

                <article class="info-box">
                    <h2>Критерии готовности</h2>
                    <p>Задача считается сделанной только когда выполняются все проверки ниже.</p>
                    <div class="endpoint-grid">
                        {task_check_cards(service)}
                    </div>
                </article>
"""


def titled_code_blocks(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f'<article class="info-box command-box"><h2>{title}</h2>{code_block(code)}</article>'
        for title, code in items
    )


def render_file_structure(items: list[tuple[str, str]]) -> str:
    return definition_items(
        [(f"<code>{escape(path)}</code>", description) for path, description in items]
    )


LESSONS = {
    "chapter01": {
        "number": 1,
        "port": 8001,
        "title": "Глава 1: Начало работы с FastAPI",
        "subtitle": "Как работает REST API, зачем нужен Uvicorn, как FastAPI принимает JSON-запрос и возвращает JSON-ответ.",
        "outcome": "После главы вы понимаете полный путь REST-запроса, умеете запустить FastAPI через Uvicorn и прочитать учебный main.py без подсказок из исходников.",
        "concepts": [
            "<strong>REST</strong> - стиль построения API, где клиент обращается к понятным URL, использует HTTP-методы и получает ответ со status code.",
            "<strong>HTTP request</strong> - запрос клиента: method, path, headers и иногда body. Например: <code>POST /api/calculator/add</code> с JSON-телом.",
            "<strong>HTTP response</strong> - ответ сервера: status code, headers и body. Например: <code>200 OK</code> и JSON <code>{\"result\": 15}</code>.",
            "<strong>HTTP method</strong> - действие запроса. <code>GET</code> обычно читает данные, <code>POST</code> отправляет данные на сервер.",
            "<strong>Path</strong> - адрес внутри сайта или API. В <code>http://localhost:8001/api/calculator/add</code> path - это <code>/api/calculator/add</code>.",
            "<strong>JSON body</strong> - данные, которые клиент отправляет серверу. В этой главе body выглядит так: <code>{\"a\": 10, \"b\": 5}</code>.",
            "<strong>Header</strong> - строка служебной информации в request или response. Header не является основными данными, но помогает клиенту и серверу договориться о формате, авторизации, кеше и других деталях.",
            "<strong>Status code</strong> - короткий числовой итог запроса: <code>200</code> успех, <code>400</code> плохие данные клиента, <code>422</code> ошибка валидации, <code>500</code> ошибка сервера.",
            "<strong>FastAPI app</strong> - объект приложения, который хранит маршруты, middleware и настройки документации.",
            "<strong>Path operation</strong> - Python-функция с декоратором <code>@app.get</code>, <code>@app.post</code> и так далее.",
            "<strong>Pydantic model</strong> - контракт входного JSON: какие поля обязательны и каких типов они должны быть.",
            "<strong>Middleware</strong> - код вокруг каждого запроса. Он может логировать, добавлять заголовки или измерять время.",
            "<strong>ASGI</strong> - интерфейс, по которому Uvicorn передаёт HTTP-запросы в FastAPI-приложение.",
            "<strong>Uvicorn</strong> - сервер, который слушает порт, принимает HTTP-запросы из браузера или curl и передаёт их объекту <code>app</code>.",
            "<strong>OpenAPI</strong> - схема API, из которой FastAPI строит Swagger UI на <code>/docs</code>.",
        ],
        "theory_blocks": [
            {
                "title": "REST без магии",
                "body": [
                    "REST API можно представить как набор адресов, куда клиент отправляет запросы. У каждого запроса есть действие: прочитать, создать, изменить или удалить данные.",
                    "В этой главе мы не создаём сложные ресурсы вроде users или orders, а делаем калькулятор. Но принцип тот же: у нас есть понятные URL, HTTP-метод <code>POST</code>, JSON-вход и JSON-ответ.",
                    "Важно: REST - это не библиотека и не отдельный сервер. Это способ договориться, как клиент и backend общаются через обычный HTTP.",
                ],
            },
            {
                "title": "Из чего состоит HTTP request",
                "items": [
                    "<strong>Method</strong>: что клиент хочет сделать. В примере это <code>POST</code>, потому что клиент отправляет данные для вычисления.",
                    "<strong>URL</strong>: полный адрес, например <code>http://localhost:8001/api/calculator/add</code>.",
                    "<strong>Path</strong>: часть URL без домена и порта, например <code>/api/calculator/add</code>.",
                    "<strong>Headers</strong>: служебные подсказки. Header <code>Content-Type: application/json</code> говорит серверу, что body написан в JSON.",
                    "<strong>Body</strong> и <strong>headers</strong> - разные вещи. Body несёт данные калькулятора, headers объясняют, как эти данные читать.",
                    "<strong>Body</strong>: данные запроса. Для сложения это <code>{\"a\": 10, \"b\": 5}</code>.",
                ],
            },
            {
                "title": "Из чего состоит HTTP response",
                "items": [
                    "<strong>Status code</strong>: короткий результат запроса. <code>200</code> значит успех, <code>400</code> - ошибка в данных клиента, <code>422</code> - JSON не прошёл проверку Pydantic.",
                    "<strong>Headers</strong>: служебная информация ответа. В главе middleware добавляет header <code>X-FastAPI-Book-Chapter: 01</code>.",
                    "<strong>Body</strong>: полезные данные ответа. В успешном калькуляторе это JSON <code>{\"result\": 15, \"operation\": \"add\"}</code>.",
                ],
            },
            {
                "title": "Headers подробнее",
                "body": [
                    "Header - это пара <code>name: value</code>. Например: <code>Content-Type: application/json</code>. Имя header-а говорит, о какой настройке речь, а значение даёт конкретную информацию.",
                    "Request headers отправляет клиент. В этой главе клиент отправляет <code>Content-Type</code>, а браузер или curl также могут отправить <code>User-Agent</code>.",
                    "Response headers отправляет сервер. Uvicorn добавляет технический header <code>server: uvicorn</code>, FastAPI добавляет <code>content-type: application/json</code>, а наш middleware добавляет <code>x-fastapi-book-chapter: 01</code>.",
                    "Headers часто не видны на странице, потому что браузер показывает body. Чтобы увидеть их руками, используйте <code>curl -i</code>: он печатает status line, headers и body.",
                ],
                "items": [
                    "<code>Content-Type</code> - формат body. Для JSON обычно <code>application/json</code>.",
                    "<code>Accept</code> - какой формат ответа клиент хотел бы получить.",
                    "<code>Authorization</code> - header для token-а. Он подробно появится в главах про JWT.",
                    "<code>User-Agent</code> - кто делает запрос: браузер, curl, мобильное приложение или другой клиент.",
                    "<code>X-...</code> - часто так называют свои custom headers, например <code>X-Demo-Client</code> или <code>X-FastAPI-Book-Chapter</code>.",
                ],
            },
            {
                "title": "Зачем нужен Uvicorn",
                "body": [
                    "FastAPI - это framework для описания приложения: какие есть endpoint-ы, какие модели данных, какая документация и какая логика выполняется.",
                    "Но объект <code>app = FastAPI()</code> сам не открывает порт и не принимает сетевые запросы. Для этого нужен ASGI-сервер. В нашем проекте это Uvicorn.",
                    "Когда вы запускаете <code>uvicorn chapter01.app.main:app --reload --port 8001</code>, Uvicorn импортирует Python-модуль, берёт переменную <code>app</code>, слушает порт <code>8001</code> и передаёт запросы в FastAPI.",
                    "Если совсем коротко: Uvicorn - это дверь с улицы в ваше FastAPI-приложение.",
                ],
            },
        ],
        "flow": [
            "Вы запускаете сервер командой <code>uvicorn chapter01.app.main:app --reload --port 8001</code>.",
            "Uvicorn импортирует модуль <code>chapter01.app.main</code> и находит в нём переменную <code>app</code>.",
            "Uvicorn начинает слушать порт <code>8001</code>. Это значит: он ждёт HTTP-запросы на <code>http://localhost:8001</code>.",
            "Клиент отправляет <code>POST /api/calculator/add</code> с header <code>Content-Type: application/json</code> и body <code>{\"a\": 10, \"b\": 5}</code>.",
            "Uvicorn принимает сетевой запрос и передаёт его FastAPI-приложению через ASGI.",
            "FastAPI смотрит на method <code>POST</code> и path <code>/api/calculator/add</code>, затем выбирает функцию <code>add</code>.",
            "Перед вызовом функции FastAPI читает JSON body и просит Pydantic собрать <code>CalculationRequest</code>.",
            "Pydantic проверяет, что поля <code>a</code> и <code>b</code> есть и являются числами. Если нет - FastAPI вернёт <code>422</code>, не заходя в endpoint.",
            "Endpoint получает готовый объект <code>request</code> и возвращает обычный Python-словарь.",
            "Middleware добавляет заголовок <code>X-FastAPI-Book-Chapter: 01</code> в ответ.",
            "FastAPI превращает словарь в JSON, выставляет status code <code>200</code>, а Uvicorn отправляет ответ клиенту.",
        ],
        "endpoints": [
            ("POST /api/calculator/add", "Сложение двух чисел."),
            ("POST /api/calculator/subtract", "Вычитание второго числа из первого."),
            ("POST /api/calculator/multiply", "Умножение двух чисел."),
            ("POST /api/calculator/divide", "Деление с ручной проверкой деления на ноль."),
            ("GET /api/headers/demo", "Показывает, как FastAPI читает request headers и как middleware добавляет response header."),
        ],
        "code_title": "Ключевые фрагменты API без решения задачи",
        "code": '''
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Глава 1: FastAPI basics",
    description="Middleware, REST API, OpenAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class CalculationRequest(BaseModel):
    a: float
    b: float


@app.middleware("http")
async def add_lesson_header(request, call_next):
    response = await call_next(request)
    response.headers["X-FastAPI-Book-Chapter"] = "01"
    return response


@app.post("/api/calculator/add")
async def add(request: CalculationRequest):
    return {"result": request.a + request.b, "operation": "add"}


@app.post("/api/calculator/divide")
async def divide(request: CalculationRequest):
    if request.b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    return {"result": request.a / request.b, "operation": "divide"}


@app.get("/api/headers/demo")
async def headers_demo(
    user_agent: Annotated[str | None, Header()] = None,
    x_demo_client: Annotated[str | None, Header()] = None,
):
    return {
        "user_agent": user_agent,
        "x_demo_client": x_demo_client,
        "note": "Response header X-FastAPI-Book-Chapter добавляет middleware.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("chapter01.app.main:app", host="127.0.0.1", port=8001, reload=True)
        ''',
        "code_notes": [
            "Сам FastAPI-объект <code>app</code> не слушает порт. Порт слушает Uvicorn, а FastAPI описывает, что делать с запросами.",
            "Строка <code>chapter01.app.main:app</code> читается так: импортируй модуль <code>chapter01.app.main</code> и возьми из него переменную <code>app</code>.",
            "<code>BaseModel</code> говорит FastAPI читать тело запроса как JSON и проверять его до вызова endpoint-а.",
            "<code>Header()</code> говорит FastAPI взять значение не из JSON body, а из HTTP headers.",
            "HTML-страница урока в реальном файле использует шаблоны и static-файлы, но в разборе они не показаны, потому что к REST API калькулятора не относятся.",
            "Здесь показаны не все операции калькулятора, а повторяющийся принцип. Полный ответ к задаче находится только во вкладке <strong>Ответы</strong>.",
            "Если поле отсутствует или тип не подходит, endpoint даже не будет вызван: FastAPI вернёт validation error.",
            "<code>HTTPException</code> используется для ожидаемых ошибок клиента, где вы сами выбираете status code.",
            "<code>--reload</code> нужен только для разработки: Uvicorn перезапускает приложение после изменения файлов.",
        ],
        "task": "Добавьте endpoint <code>POST /api/calculator/power</code>, который возводит <code>a</code> в степень <code>b</code>. Он должен возвращать тот же формат ответа: <code>result</code> и <code>operation</code>.",
        "answer": '''
@app.post("/api/calculator/power")
async def power(request: CalculationRequest):
    return {"result": request.a ** request.b, "operation": "power"}
        ''',
        "answer_notes": [
            "Новая операция использует уже существующую модель, потому что входной контракт такой же.",
            "Swagger UI автоматически покажет новый endpoint после перезапуска приложения.",
            "Uvicorn-команда не меняется, потому что мы не создавали новый файл и не переименовывали переменную <code>app</code>.",
        ],
    },
    "chapter02": {
        "number": 2,
        "port": 8002,
        "title": "Глава 2: Dependency Injection",
        "subtitle": "Как FastAPI сам готовит сервисы для endpoint-а: Depends, dependency graph, request cache, query-параметры в dependency и singleton-style объекты.",
        "outcome": "После главы вы понимаете, зачем нужен Depends, почему dependency передают без скобок, как FastAPI вызывает зависимости и чем отличаются scoped, transient и singleton-style объекты.",
        "concepts": [
            "<strong>Dependency</strong> - обычная Python-функция, которая готовит значение для endpoint-а: сервис, настройки, логгер, пользователя, DB session или что-то ещё.",
            "<strong>Depends</strong> - пометка в параметрах функции: “FastAPI, вызови вот эту dependency и положи результат сюда”.",
            "<strong>Injection point</strong> - параметр endpoint-а, куда FastAPI подставляет результат dependency.",
            "<strong>Dependency graph</strong> - цепочка зависимостей. Dependency может сама зависеть от других dependency.",
            "<strong>Request cache</strong> - одинаковая dependency по умолчанию вызывается один раз за один HTTP-запрос и переиспользуется внутри этого запроса.",
            "<strong>use_cache=False</strong> - отключает request cache для конкретной dependency и заставляет FastAPI вызвать её заново.",
            "<strong>Singleton-style</strong> - обычный объект Python на уровне модуля. Он создаётся при импорте файла и живёт всё время процесса.",
            "<strong>Singleton DI provider</strong> - dependency-функция, которая не создаёт новый объект, а возвращает заранее созданный singleton.",
            "<strong>Query in dependency</strong> - dependency может принимать query-параметры так же, как endpoint.",
            "<strong>Inversion of Control</strong> - endpoint не создаёт зависимость сам, а просит фреймворк подготовить её.",
        ],
        "theory_blocks": [
            {
                "title": "Зачем вообще нужен Dependency Injection",
                "body": [
                    "Без DI endpoint быстро превращается в большую функцию: внутри создаётся логгер, читаются настройки, открывается база, проверяется пользователь, создаётся сервис и только потом выполняется бизнес-логика.",
                    "С DI endpoint становится короче. Он объявляет, что ему нужно, а FastAPI готовит эти вещи до вызова endpoint-а.",
                    "Это похоже на заказ в кафе: вы не идёте на кухню и не готовите ингредиенты сами. Вы говорите, что вам нужно, а кухня приносит готовое блюдо. В коде endpoint говорит: “мне нужен logger”, “мне нужен current user”, “мне нужны settings”.",
                    "Главная польза для новичка: код легче читать. В endpoint-е видно входные данные и действие, а подготовка объектов лежит в отдельных маленьких функциях.",
                ],
            },
            {
                "title": "Без DI и с DI",
                "body": [
                    "В маленьком примере разница кажется лишней. Но когда зависимостей становится больше, ручное создание объектов внутри endpoint-а начинает мешать.",
                    "DI выносит подготовку объекта в отдельную функцию. Эту функцию можно переиспользовать в нескольких endpoint-ах и подменять в тестах.",
                ],
                "code": '''
# Плохо для роста проекта: endpoint сам решает, как создать сервис.
@app.get("/without-di")
async def without_di():
    service = ReportService()
    return service.build()


# Лучше: endpoint просит готовый сервис.
def get_report_service() -> ReportService:
    return ReportService()


@app.get("/with-di")
async def with_di(service: ReportService = Depends(get_report_service)):
    return service.build()
                ''',
            },
            {
                "title": "Depends не вызывает функцию сразу",
                "body": [
                    "Запись <code>Depends(get_scoped_service)</code> выглядит непривычно, потому что после имени функции нет скобок.",
                    "Это специально. Мы передаём FastAPI саму функцию, а не результат функции. FastAPI вызовет её позже, когда придёт HTTP-запрос.",
                ],
                "items": [
                    "<code>Depends(get_scoped_service)</code> - правильно: FastAPI сам вызовет dependency.",
                    "<code>Depends(get_scoped_service())</code> - почти всегда ошибка: функция вызовется сразу при загрузке приложения.",
                    "Если dependency принимает параметры, FastAPI сам попробует взять их из query, path, headers, body или других dependency.",
                ],
            },
            {
                "title": "Как FastAPI вызывает зависимости",
                "items": [
                    "FastAPI получает HTTP-запрос.",
                    "Смотрит, какой endpoint подходит по method и path.",
                    "Читает параметры endpoint-а и видит <code>Depends(...)</code>.",
                    "Строит dependency graph: какие функции нужно вызвать и в каком порядке.",
                    "Вызывает dependency-функции, проверяет их параметры и кеширует результат, если кеш включён.",
                    "Подставляет готовые объекты в параметры endpoint-а.",
                    "Только после этого запускает тело endpoint-функции.",
                ],
            },
            {
                "title": "Время жизни объектов простыми словами",
                "items": [
                    "<strong>Scoped в этой главе</strong>: dependency создаёт объект один раз за HTTP-запрос. Если один endpoint просит её два раза, FastAPI отдаёт один и тот же объект.",
                    "<strong>Transient в этой главе</strong>: dependency вызывается каждый раз заново через <code>use_cache=False</code>. Поэтому два параметра получают разные id.",
                    "<strong>Singleton-style в этой главе</strong>: объект создан заранее на уровне модуля. Все запросы получают ссылку на один и тот же объект.",
                    "В FastAPI нет встроенных lifetime-ов в стиле больших DI-контейнеров. Здесь мы показываем поведение, которое чаще всего нужно новичку понимать на практике.",
                ],
            },
            {
                "title": "Как прописать singleton DI",
                "body": [
                    "В FastAPI singleton обычно не “регистрируют” отдельной командой. Его чаще делают обычным Python-кодом: создают объект один раз на уровне модуля, а dependency-функция возвращает этот объект.",
                    "Главное правило: объект создаётся вне dependency. Если создать объект внутри dependency, это уже не singleton, потому что функция будет создавать новый объект при вызове.",
                    "Такой подход хорошо подходит для неизменяемых настроек, клиентов, лёгких сервисов без опасного общего состояния. Если сервис хранит изменяемые данные, нужно понимать, что эти данные будут общими для всех запросов.",
                ],
                "code": '''
@dataclass(frozen=True)
class SingletonDiService:
    id: str
    name: str


# 1. Создаём объект один раз, когда Python импортирует файл.
singleton_di_service = SingletonDiService(
    id=str(uuid4()),
    name="created-once",
)


# 2. Provider dependency возвращает уже готовый объект.
def get_singleton_di_service() -> SingletonDiService:
    return singleton_di_service


# 3. Endpoint просит singleton через Depends.
@app.get("/api/dependency-injection/singleton-demo")
async def singleton_demo(
    service: SingletonDiService = Depends(get_singleton_di_service),
):
    return {"id": service.id, "name": service.name}
                ''',
            },
            {
                "title": "Что dependency может читать",
                "body": "Dependency - это не только создание класса. Она может принимать почти всё то же, что endpoint: query-параметры, path-параметры, headers, cookies, Request и результаты других dependency.",
                "items": [
                    "<code>get_current_user(username: str = Query(\"guest\"))</code> читает query-параметр <code>?username=...</code>.",
                    "<code>get_logger()</code> возвращает общий logger, чтобы endpoint не создавал его вручную.",
                    "<code>get_settings()</code> возвращает настройки приложения.",
                    "В следующих главах тот же принцип будет использоваться для базы данных, JWT и защищённых endpoint-ов.",
                ],
            },
            {
                "title": "Когда Depends не нужен",
                "items": [
                    "Если значение используется только в одной строке и не требует подготовки, обычный параметр endpoint-а проще.",
                    "Если объект не нужно переиспользовать и не нужно подменять в тестах, отдельная dependency может быть лишней.",
                    "Если логика стала большой, endpoint начал создавать много объектов или эту подготовку надо повторять в нескольких местах - это хороший кандидат на dependency.",
                ],
            },
        ],
        "flow": [
            "Клиент вызывает <code>GET /api/dependency-injection/lifetimes</code>.",
            "FastAPI находит endpoint <code>lifetimes</code> по method и path.",
            "Перед запуском функции FastAPI смотрит на параметры endpoint-а.",
            "В параметрах есть <code>Depends(get_scoped_service)</code>, <code>Depends(get_singleton_service)</code> и <code>Depends(get_transient_service, use_cache=False)</code>.",
            "FastAPI вызывает <code>get_scoped_service</code> один раз и кладёт один результат сразу в <code>scoped1</code> и <code>scoped2</code>.",
            "FastAPI вызывает <code>get_singleton_service</code>; функция возвращает заранее созданный объект <code>singleton_service</code>.",
            "FastAPI вызывает <code>get_transient_service</code> два раза, потому что для этих параметров стоит <code>use_cache=False</code>.",
            "Endpoint получает уже готовые объекты. Внутри endpoint-а мы не пишем <code>get_scoped_service()</code> вручную.",
            "Endpoint возвращает id объектов, чтобы в Swagger было видно, какие id совпали, а какие отличаются.",
            "На endpoint-е <code>current-user</code> dependency дополнительно читает query-параметры <code>username</code> и <code>role</code>.",
        ],
        "endpoints": [
            ("GET /api/dependency-injection/lifetimes", "Показывает scoped, singleton и transient идентификаторы."),
            ("GET /api/dependency-injection/singleton-demo", "Отдельный пример, как прописать singleton DI через объект на уровне модуля и provider-функцию."),
            ("GET /api/dependency-injection/settings-demo", "Показывает dependency, которая возвращает настройки приложения."),
            ("GET /api/dependency-injection/current-user", "Показывает dependency, которая читает query-параметры и собирает объект пользователя."),
            ("GET /api/dependency-injection/logger-demo", "Демонстрирует logging через dependency для логгера."),
        ],
        "code_title": "Основные DI-примеры без ответа задачи",
        "code": '''
import logging
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Depends, Query


logger = logging.getLogger("chapter02")


@dataclass
class InstanceService:
    service_type: str
    id: str


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    environment: str


@dataclass(frozen=True)
class SingletonDiService:
    id: str
    name: str


@dataclass
class UserContext:
    username: str
    role: str


singleton_service = InstanceService("singleton", str(uuid4()))
app_settings = AppSettings(app_name="FastAPI Book Chapter 02", environment="development")
singleton_di_service = SingletonDiService(id=str(uuid4()), name="created-once")


def get_scoped_service() -> InstanceService:
    return InstanceService("scoped", str(uuid4()))


def get_singleton_service() -> InstanceService:
    return singleton_service


def get_transient_service() -> InstanceService:
    return InstanceService("transient", str(uuid4()))


def get_settings() -> AppSettings:
    return app_settings


def get_singleton_di_service() -> SingletonDiService:
    return singleton_di_service


def get_logger() -> logging.Logger:
    return logger


def get_current_user(
    username: str = Query("guest"),
    role: str = Query("student"),
) -> UserContext:
    return UserContext(username=username, role=role)


@app.get("/api/dependency-injection/lifetimes")
async def lifetimes(
    scoped1: InstanceService = Depends(get_scoped_service),
    scoped2: InstanceService = Depends(get_scoped_service),
    singleton1: InstanceService = Depends(get_singleton_service),
    singleton2: InstanceService = Depends(get_singleton_service),
    transient1: InstanceService = Depends(get_transient_service, use_cache=False),
    transient2: InstanceService = Depends(get_transient_service, use_cache=False),
):
    return {
        "scoped_same": scoped1.id == scoped2.id,
        "singleton_same": singleton1.id == singleton2.id,
        "transient_different": transient1.id != transient2.id,
    }


@app.get("/api/dependency-injection/singleton-demo")
async def singleton_demo(service: SingletonDiService = Depends(get_singleton_di_service)):
    return {"id": service.id, "name": service.name}


@app.get("/api/dependency-injection/settings-demo")
async def settings_demo(settings: AppSettings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/api/dependency-injection/current-user")
async def current_user(user: UserContext = Depends(get_current_user)):
    return {"username": user.username, "role": user.role}


@app.get("/api/dependency-injection/logger-demo")
async def logger_demo(
    message: str = "Тестовое сообщение",
    app_logger: logging.Logger = Depends(get_logger),
):
    app_logger.info("Получен запрос на логирование: %s", message)
    return {"logged_message": message}
        ''',
        "code_notes": [
            "Dependency - это обычная функция. В примере <code>get_scoped_service</code>, <code>get_singleton_service</code>, <code>get_transient_service</code> и <code>get_current_user</code> - обычные функции Python.",
            "Одинаковый <code>Depends(get_scoped_service)</code> кешируется в рамках одного HTTP-запроса, поэтому <code>scoped1</code> и <code>scoped2</code> получают один id.",
            "<code>singleton_service</code> создан заранее на уровне модуля, поэтому все вызовы <code>get_singleton_service</code> возвращают один объект.",
            "Singleton DI записывается в три шага: создать объект вне dependency, написать provider, подключить provider через <code>Depends</code>.",
            "Если вызвать <code>/api/dependency-injection/singleton-demo</code> несколько раз, поле <code>id</code> останется тем же самым, пока приложение не перезапустится.",
            "<code>use_cache=False</code> явно отключает кеш, поэтому transient получает разные id.",
            "<code>get_current_user</code> показывает важный трюк: dependency может сама принимать query-параметры и собрать из них удобный объект.",
            "В реальном проекте dependency часто возвращает репозиторий, DB session, настройки, logger или текущего пользователя.",
            "Код практической задачи здесь специально не показан. Полное решение находится только во вкладке <strong>Ответы</strong>.",
        ],
        "task": "Сделайте простой DI для красивого вывода логов. Новый endpoint <code>GET /api/dependency-injection/pretty-log</code> должен принять query-параметр <code>message</code> и вернуть JSON с полем <code>formatted_message</code> в формате <code>[DI LOG] текст_сообщения</code>. Префикс <code>[DI LOG]</code> должен прийти из dependency, а не быть написан прямо внутри endpoint-а.",
        "answer": '''
def get_log_prefix() -> str:
    return "[DI LOG]"


@app.get("/api/dependency-injection/pretty-log")
async def pretty_log(
    message: str = "hello",
    prefix: str = Depends(get_log_prefix),
    app_logger: logging.Logger = Depends(get_logger),
):
    formatted_message = f"{prefix} {message}"
    app_logger.info(formatted_message)
    return {"formatted_message": formatted_message}
        ''',
        "answer_notes": [
            "Задача специально простая: dependency возвращает обычную строку, чтобы было видно, что DI работает не только с классами.",
            "Endpoint получает prefix через <code>Depends(get_log_prefix)</code>, а logger через уже существующий <code>Depends(get_logger)</code>.",
            "В ответе возвращается готовая строка, поэтому результат легко проверить в Swagger без чтения консоли.",
        ],
    },
    "chapter03": {
        "number": 3,
        "port": 8003,
        "title": "Глава 3: HTTP Requests",
        "subtitle": "Асинхронные запросы к внешним API через httpx и сервисный слой.",
        "outcome": "После главы вы понимаете, как не блокировать event loop и как отделять endpoint от внешней интеграции.",
        "concepts": [
            "<strong>httpx.AsyncClient</strong> - асинхронный HTTP-клиент для outbound-запросов.",
            "<strong>Timeout</strong> - обязательная защита от зависания внешнего сервиса.",
            "<strong>Service layer</strong> - класс, который скрывает детали внешнего API от контроллера.",
            "<strong>raise_for_status</strong> - перевод HTTP 4xx/5xx во внутреннее исключение.",
            "<strong>Error mapping</strong> - преобразование ошибок внешнего API в понятный ответ вашего API.",
        ],
        "flow": [
            "Клиент вызывает ваш endpoint, например <code>/api/http-client/post/1</code>.",
            "Endpoint получает <code>ExternalApiService</code> через dependency.",
            "Сервис открывает <code>httpx.AsyncClient</code> с base URL и timeout.",
            "Внешний ответ проверяется через <code>raise_for_status()</code>.",
            "JSON внешнего сервиса возвращается клиенту вашего API.",
            "При ошибке endpoint возвращает HTTP 502 или код внешнего ответа.",
        ],
        "endpoints": [
            ("GET /api/http-client/direct/{post_id}", "Прямой запрос к JSONPlaceholder без сервиса."),
            ("GET /api/http-client/post/{post_id}", "То же самое через сервисный слой."),
            ("GET /api/http-client/posts", "Получение списка постов."),
            ("POST /api/http-client/post", "Создание демо-поста во внешнем API."),
        ],
        "code": '''
class ExternalApiService:
    async def get_post(self, post_id: int) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}")
            response.raise_for_status()
            return response.json()
        ''',
        "code_notes": [
            "Клиент создаётся внутри <code>async with</code>, поэтому соединения корректно закрываются.",
            "В больших приложениях клиент можно держать дольше через lifespan, но для учебного примера локальный context manager проще.",
            "Endpoint не знает URL внешнего API: это ответственность сервиса.",
        ],
        "task": "Добавьте метод и endpoint для получения комментариев поста: <code>GET /api/http-client/post/{post_id}/comments</code>.",
        "answer": '''
async def get_post_comments(self, post_id: int) -> list[dict]:
    async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
        response = await client.get(f"/posts/{post_id}/comments")
        response.raise_for_status()
        return response.json()
        ''',
        "answer_notes": [
            "Метод должен жить в сервисе, чтобы endpoint оставался тонким.",
            "Обработку <code>httpx.HTTPError</code> можно переиспользовать из существующих endpoint-ов.",
        ],
    },
    "chapter04": {
        "number": 4,
        "port": 8004,
        "title": "Глава 4: Error Handling",
        "subtitle": "HTTPException, custom exception handlers, validation errors и middleware для времени обработки.",
        "outcome": "После главы вы умеете отделять ожидаемые ошибки от неожиданных исключений и возвращать единый JSON-формат.",
        "concepts": [
            "<strong>HTTPException</strong> - ожидаемая ошибка с выбранным HTTP status code.",
            "<strong>Custom exception</strong> - доменное исключение, для которого можно зарегистрировать handler.",
            "<strong>RequestValidationError</strong> - ошибка валидации входных данных FastAPI/Pydantic.",
            "<strong>Middleware</strong> - общий код вокруг запроса, здесь он добавляет <code>X-Process-Time</code>.",
            "<strong>JSONResponse</strong> - ручное формирование тела и status code.",
        ],
        "flow": [
            "Запрос проходит через middleware, который сохраняет время старта.",
            "Endpoint либо возвращает успешный результат, либо бросает исключение.",
            "FastAPI ищет самый подходящий exception handler.",
            "Handler превращает исключение в JSON-ответ.",
            "Middleware добавляет заголовок времени обработки уже к готовому ответу.",
            "Клиент получает предсказуемую структуру ошибки.",
        ],
        "endpoints": [
            ("GET /api/error-demo/throw", "Искусственно бросает custom exception."),
            ("GET /api/error-demo/badrequest", "Возвращает ожидаемый BadRequest через HTTPException."),
            ("POST /api/error-demo/validate", "Проверяет бизнес-валидацию name и age."),
            ("GET /api/error-demo/success", "Контрольный успешный ответ."),
        ],
        "code": '''
@app.exception_handler(DemoError)
async def demo_error_handler(request, exc: DemoError):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url.path)},
    )
        ''',
        "code_notes": [
            "Handler принимает исходный request, поэтому может добавить path, correlation id или user id.",
            "Для бизнес-ошибок лучше возвращать 400/404/409, а не скрывать их как 500.",
            "Глобальные handlers помогают держать одинаковый формат ошибок во всём API.",
        ],
        "task": "Создайте исключение <code>NotReadyError</code> и handler, который возвращает HTTP 503 с сообщением <code>Сервис временно недоступен</code>.",
        "answer": '''
class NotReadyError(Exception):
    pass


@app.exception_handler(NotReadyError)
async def not_ready_handler(request, exc: NotReadyError):
    return JSONResponse(status_code=503, content={"error": "Сервис временно недоступен"})
        ''',
        "answer_notes": [
            "HTTP 503 подходит для временной недоступности зависимости или сервиса.",
            "Если ошибка ожидаемая, её полезно покрыть тестом на status code и JSON-body.",
        ],
    },
    "chapter05": {
        "number": 5,
        "port": 8005,
        "title": "Глава 5: Jinja2 UI",
        "subtitle": "Серверные HTML-шаблоны, формы, Form-параметры и Pydantic-валидация вместо Razor Pages.",
        "outcome": "После главы вы понимаете, как FastAPI отдаёт HTML, принимает формы и показывает ошибки пользователю.",
        "concepts": [
            "<strong>Jinja2Templates</strong> - подключение папки HTML-шаблонов.",
            "<strong>TemplateResponse</strong> - ответ, который рендерит шаблон на сервере.",
            "<strong>request</strong> - обязательный объект в context для Starlette templates.",
            "<strong>Form</strong> - чтение данных из HTML-формы вместо JSON-body.",
            "<strong>Pydantic validation</strong> - единая проверка формы перед сохранением или отправкой.",
        ],
        "flow": [
            "Пользователь открывает <code>/contact</code>, FastAPI рендерит HTML-форму.",
            "Браузер отправляет <code>POST /contact</code> с <code>application/x-www-form-urlencoded</code>.",
            "FastAPI передаёт поля в параметры <code>Form</code>.",
            "Pydantic-модель проверяет пустые строки и формат email.",
            "При ошибке тот же шаблон рендерится со status 400 и списком ошибок.",
            "При успехе страница показывает сообщение о принятой форме.",
        ],
        "endpoints": [
            ("GET /", "Страница урока."),
            ("GET /contact", "HTML-форма контакта."),
            ("POST /contact", "Обработка формы и вывод ошибок."),
            ("POST /api/contact", "JSON API-версия той же проверки."),
        ],
        "code": '''
@app.post("/contact", response_class=HTMLResponse, include_in_schema=False)
async def submit_contact(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    message: str = Form(""),
):
    values = {"name": name, "email": email, "message": message}
    ContactForm(**values)
        ''',
        "code_notes": [
            "HTML-форма и JSON API могут использовать одну Pydantic-модель, чтобы правила не расходились.",
            "Ошибки формы лучше возвращать на ту же страницу, сохраняя введённые пользователем значения.",
            "Для файлов и сложных форм понадобится <code>python-multipart</code>, он уже есть в requirements.",
        ],
        "task": "Добавьте страницу регистрации с полями <code>username</code>, <code>email</code>, <code>password</code> и серверной проверкой, что пароль не короче 6 символов.",
        "answer": '''
class RegistrationForm(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def password_is_long_enough(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Пароль должен быть не короче 6 символов")
        return value
        ''',
        "answer_notes": [
            "GET-handler должен показывать пустую форму, POST-handler - валидировать и возвращать тот же шаблон.",
            "Не храните пароль в открытом виде: в auth-главах он будет хешироваться.",
        ],
    },
    "chapter06": {
        "number": 6,
        "port": 8006,
        "title": "Глава 6: SQLAlchemy, DTO и SQLite",
        "subtitle": "Engine, Session, ORM-модель, Pydantic DTO, CRUD endpoint-ы и минимальная Alembic-миграция.",
        "outcome": "После главы вы умеете связать FastAPI с SQLite и отделять публичные DTO от внутренних ORM-классов.",
        "concepts": [
            "<strong>Engine</strong> - подключение SQLAlchemy к базе данных.",
            "<strong>Session</strong> - unit of work: через неё читаем, добавляем, изменяем и удаляем строки.",
            "<strong>DeclarativeBase</strong> - база для ORM-классов.",
            "<strong>Mapped / mapped_column</strong> - типизированное описание колонок SQLAlchemy 2.",
            "<strong>DTO</strong> - Pydantic-модели для входного и выходного JSON.",
            "<strong>Alembic</strong> - инструмент миграций схемы БД.",
        ],
        "flow": [
            "При старте приложения создаётся engine и sessionmaker.",
            "Dependency <code>get_db</code> открывает Session на время запроса.",
            "Endpoint получает Session через <code>Depends</code>.",
            "ORM-модель <code>Product</code> описывает таблицу <code>products</code>.",
            "Pydantic DTO проверяет входные данные и форматирует выходной JSON.",
            "После commit SQLAlchemy записывает изменения в SQLite.",
        ],
        "endpoints": [
            ("GET /api/products", "Список продуктов."),
            ("GET /api/products/{product_id}", "Один продукт или 404."),
            ("POST /api/products", "Создание продукта с DTO-валидацией."),
            ("PUT /api/products/{product_id}", "Частичное обновление полей."),
            ("DELETE /api/products/{product_id}", "Удаление продукта."),
        ],
        "code": '''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/products", response_model=ProductDto, status_code=201)
async def create_product(request: CreateProductDto, db: Session = Depends(get_db)):
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
        ''',
        "code_notes": [
            "<code>yield</code> dependency гарантирует закрытие Session после запроса.",
            "<code>response_model</code> не отдаёт наружу лишние ORM-поля.",
            "В учебном режиме таблицы создаются автоматически, а Alembic показан как правильный путь для реального проекта.",
        ],
        "task": "Добавьте поле <code>category</code> в продукт, DTO и Alembic-миграцию. Проверьте, что оно возвращается в <code>GET /api/products</code>.",
        "answer": '''
category: Mapped[str] = mapped_column(String(80), default="general")


class ProductDto(BaseModel):
    id: int
    name: str
    category: str
    ...
        ''',
        "answer_notes": [
            "Менять нужно и ORM-модель, и DTO, иначе поле либо не сохранится, либо не попадёт в публичный ответ.",
            "В миграции используйте <code>op.add_column</code>, а в downgrade - <code>op.drop_column</code>.",
        ],
    },
    "chapter07": {
        "number": 7,
        "port": 8007,
        "title": "Глава 7: Authentication и Authorization",
        "subtitle": "Регистрация, вход, password hashing, JWT access token и protected endpoint.",
        "outcome": "После главы вы понимаете разницу между проверкой личности и проверкой прав доступа.",
        "concepts": [
            "<strong>Authentication</strong> - подтверждаем, кто пользователь.",
            "<strong>Authorization</strong> - решаем, разрешено ли пользователю действие.",
            "<strong>Password hash</strong> - пароль нельзя хранить открытым текстом.",
            "<strong>JWT</strong> - подписанный token с claims вроде <code>sub</code>, <code>role</code> и <code>exp</code>.",
            "<strong>OAuth2PasswordBearer</strong> - dependency, которая читает Bearer token из заголовка Authorization.",
        ],
        "flow": [
            "Пользователь регистрируется через <code>/api/auth/register</code>.",
            "Пароль хешируется, а не сохраняется как есть.",
            "Сервер выпускает JWT с username, role и временем истечения.",
            "Клиент передаёт token в заголовке <code>Authorization: Bearer ...</code>.",
            "Dependency декодирует и проверяет подпись JWT.",
            "Protected endpoint получает текущего пользователя или возвращает 401.",
        ],
        "endpoints": [
            ("POST /api/auth/register", "Создание пользователя и выдача token-а."),
            ("POST /api/auth/login", "Проверка пароля и выдача token-а."),
            ("GET /api/protected", "Endpoint, доступный только с валидным Bearer token."),
        ],
        "code": '''
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    user = USERS.get(str(username))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
        ''',
        "code_notes": [
            "Token не шифруется, а подписывается: содержимое можно прочитать, но нельзя незаметно изменить без secret key.",
            "В demo пользователи хранятся в памяти, поэтому после перезапуска они пропадают.",
            "Для role-based доступа добавьте отдельную dependency, которая проверяет <code>user['role']</code>.",
        ],
        "task": "Добавьте endpoint <code>GET /api/admin</code>, доступный только пользователю с ролью <code>admin</code>.",
        "answer": '''
def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@app.get("/api/admin")
async def admin(user: dict = Depends(require_admin)):
    return {"message": "admin area"}
        ''',
        "answer_notes": [
            "401 означает, что пользователь не аутентифицирован; 403 - пользователь известен, но прав не хватает.",
            "Проверку роли лучше вынести в dependency, чтобы переиспользовать в нескольких endpoint-ах.",
        ],
    },
    "chapter08": {
        "number": 8,
        "port": 8008,
        "title": "Глава 8: Refresh Tokens",
        "subtitle": "Короткий access token, долгоживущий refresh token, rotation, revoke и logout.",
        "outcome": "После главы вы понимаете, зачем разделять access и refresh token и почему refresh token нужно хранить на сервере.",
        "concepts": [
            "<strong>Access token</strong> - короткоживущий JWT для доступа к API.",
            "<strong>Refresh token</strong> - случайная строка, которая хранится в БД и выпускает новую пару token-ов.",
            "<strong>Rotation</strong> - при refresh старый refresh token отзывается и создаётся новый.",
            "<strong>Revoke</strong> - ручное прекращение действия refresh token-а.",
            "<strong>Logout</strong> - отзыв всех активных refresh token-ов пользователя.",
        ],
        "flow": [
            "Register/login создаёт пользователя и выдаёт access + refresh token.",
            "Access token живёт недолго и отправляется в Bearer header.",
            "Refresh token хранится в таблице <code>refresh_tokens</code>.",
            "При <code>/api/auth/refresh</code> сервер проверяет token, срок действия и revoked flag.",
            "Старый refresh token отзывается, новая пара token-ов возвращается клиенту.",
            "Повторное использование старого refresh token-а возвращает HTTP 401.",
        ],
        "endpoints": [
            ("POST /api/auth/register", "Создание пользователя и первой пары token-ов."),
            ("POST /api/auth/login", "Вход и выдача новой пары token-ов."),
            ("POST /api/auth/refresh", "Rotation refresh token-а."),
            ("POST /api/auth/revoke", "Отзыв конкретного refresh token-а."),
            ("POST /api/auth/logout", "Отзыв всех token-ов текущего пользователя."),
        ],
        "code": '''
stored = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
if stored is None or stored.revoked or stored.expires_at <= datetime.utcnow():
    raise HTTPException(status_code=401, detail="Недействительный refresh token")

stored.revoked = True
access_token, access_expires = create_access_token(user)
refresh_token, refresh_expires = create_refresh_token(db, user)
        ''',
        "code_notes": [
            "Refresh token не является JWT: это opaque value, смысл которого известен только серверу.",
            "Rotation помогает обнаруживать и блокировать повторное использование украденного token-а.",
            "В production refresh token обычно хранится в HttpOnly cookie или защищённом хранилище клиента.",
        ],
        "task": "Добавьте поле <code>revoked_at</code>, чтобы видеть, когда token был отозван.",
        "answer": '''
revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


stored.revoked = True
stored.revoked_at = datetime.utcnow()
        ''',
        "answer_notes": [
            "Не забудьте обновить миграцию или создать новую Alembic revision.",
            "Тест должен проверять не только HTTP 401, но и заполнение <code>revoked_at</code> в БД.",
        ],
    },
    "chapter09": {
        "number": 9,
        "port": 8009,
        "title": "Глава 9: WebSockets",
        "subtitle": "Постоянное двустороннее соединение, connection manager, receive loop и broadcast.",
        "outcome": "После главы вы умеете принять WebSocket-соединение, хранить клиентов и рассылать сообщения всем участникам.",
        "concepts": [
            "<strong>WebSocket</strong> - протокол для постоянного двустороннего обмена.",
            "<strong>accept()</strong> - явное принятие соединения сервером.",
            "<strong>receive_text()</strong> - ожидание следующего сообщения клиента.",
            "<strong>WebSocketDisconnect</strong> - штатное отключение клиента.",
            "<strong>ConnectionManager</strong> - объект, который хранит активные подключения.",
        ],
        "flow": [
            "Клиент подключается к <code>ws://localhost:8009/ws</code>.",
            "Сервер вызывает <code>websocket.accept()</code> и создаёт connection id.",
            "Подключение сохраняется в словаре активных клиентов.",
            "Сервер входит в бесконечный цикл приема сообщений.",
            "Каждое сообщение рассылается всем текущим клиентам.",
            "При отключении connection id удаляется из manager-а.",
        ],
        "endpoints": [
            ("GET /api/websocket/info", "Показывает endpoint и количество подключений."),
            ("WS /ws", "Простой broadcast-чат."),
        ],
        "code_title": "ConnectionManager для WebSocket-чата",
        "code": '''
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        self.active_connections[connection_id] = websocket
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
        })
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        self.active_connections.pop(connection_id, None)

    async def broadcast(self, payload: dict) -> None:
        for websocket in list(self.active_connections.values()):
            await websocket.send_json(payload)
        ''',
        "code_notes": [
            "WebSocket endpoint не возвращает HTTP response, он живёт пока открыто соединение.",
            "Broadcast должен учитывать отключившихся клиентов, иначе отправка может падать.",
            "Для масштабирования на несколько процессов нужен внешний broker, например Redis Pub/Sub.",
        ],
        "task": "Добавьте команду <code>/who</code>, которая отправляет текущему клиенту количество активных подключений.",
        "answer": '''
if message == "/who":
    await websocket.send_json({
        "event": "connections",
        "count": len(manager.active_connections),
    })
else:
    await manager.broadcast(...)
        ''',
        "answer_notes": [
            "Команды, предназначенные только отправителю, не нужно рассылать через broadcast.",
            "Так появляется первая серверная логика поверх обычного транспорта.",
        ],
    },
    "chapter10": {
        "number": 10,
        "port": 8010,
        "title": "Глава 10: Socket.IO чат",
        "subtitle": "Socket.IO events, sid, rooms, broadcast и direct messages.",
        "outcome": "После главы вы понимаете, как подключить Socket.IO к FastAPI и обмениваться real-time событиями.",
        "concepts": [
            "<strong>Socket.IO</strong> - real-time библиотека с событиями, комнатами и автоматическим протоколом поверх HTTP/WebSocket transport.",
            "<strong>sid</strong> - server-side id конкретного Socket.IO-подключения.",
            "<strong>event</strong> - именованное сообщение, например <code>chat_message</code> или <code>join_room</code>.",
            "<strong>room</strong> - комната, куда можно добавить несколько подключений и отправлять события группе.",
            "<strong>emit</strong> - отправка события одному клиенту, комнате или всем подключённым клиентам.",
        ],
        "flow": [
            "Клиент подключается через Socket.IO к <code>http://localhost:8010</code> с path <code>/socket.io</code>.",
            "Сервер получает событие <code>connect</code>, запоминает <code>sid</code> и отправляет клиенту событие <code>connected</code>.",
            "Клиент отправляет событие <code>set_name</code>, чтобы сервер связал <code>sid</code> с именем пользователя.",
            "Клиент отправляет <code>join_room</code>, и сервер добавляет подключение в комнату.",
            "Клиент отправляет <code>chat_message</code>, а сервер делает <code>emit</code> всем или выбранной комнате.",
            "При <code>disconnect</code> сервер очищает локальные словари подключений и комнат.",
        ],
        "endpoints": [
            ("GET /api/chat/info", "Состояние подключений и групп."),
            ("Socket.IO /socket.io", "Основной real-time endpoint для событий чата."),
            ("WS /ws/chat", "Низкоуровневый WebSocket endpoint для ручного JSON-протокола."),
        ],
        "code_title": "Базовые Socket.IO события урока",
        "code": '''
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI(title="Глава 10: Socket.IO chat")
app = socketio.ASGIApp(
    sio,
    other_asgi_app=fastapi_app,
    socketio_path="socket.io",
)

socketio_clients: dict[str, str] = {}

@sio.event
async def connect(sid, environ, auth):
    socketio_clients[sid] = "anonymous"
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def set_name(sid, data):
    username = data.get("username") or "anonymous"
    socketio_clients[sid] = username
    await sio.emit("name_set", {"username": username}, to=sid)


@sio.event
async def direct_message(sid, data):
    target_sid = data.get("sid")
    payload = {
        "event": "direct_message",
        "from": socketio_clients.get(sid, "anonymous"),
        "message": data.get("message", ""),
    }
    if target_sid:
        await sio.emit("direct_message", payload, to=target_sid)


@sio.event
async def disconnect(sid):
    socketio_clients.pop(sid, None)
        ''',
        "code_notes": [
            "Socket.IO работает событиями: клиент и сервер договариваются об именах событий и структуре payload.",
            "Комнаты удобнее ручного хранения списков получателей: сервер вызывает <code>enter_room</code> и отправляет событие в room.",
            "В этой главе также оставлен raw WebSocket endpoint, чтобы было видно, чем ручной протокол отличается от событий Socket.IO.",
        ],
        "task": "Добавьте Socket.IO событие <code>leave_room</code>, которое удаляет подключение из комнаты и отправляет клиенту событие <code>left_room</code>.",
        "answer": '''
@sio.event
async def leave_room(sid, data):
    room = data.get("room", "general")
    await sio.leave_room(sid, room)
    socketio_rooms[room].discard(sid)
    await sio.emit("left_room", {"room": room}, to=sid)
        ''',
        "answer_notes": [
            "Метод <code>leave_room</code> убирает sid из внутренней комнаты Socket.IO.",
            "Локальный словарь <code>socketio_rooms</code> нужен только для учебного endpoint-а <code>/api/chat/info</code>.",
        ],
    },
    "chapter11": {
        "number": 11,
        "port": 8011,
        "title": "Глава 11: Авторизация Socket.IO",
        "subtitle": "JWT в Socket.IO auth payload, отказ в connect и события от подтверждённого пользователя.",
        "outcome": "После главы вы умеете принимать Socket.IO-подключение только с валидным JWT и не доверять username из клиента.",
        "concepts": [
            "<strong>Socket.IO auth</strong> - объект, который клиент передаёт при подключении: <code>{ access_token: token }</code>.",
            "<strong>connect event</strong> - место, где сервер решает принять или отклонить подключение.",
            "<strong>return False</strong> - способ отказать Socket.IO-клиенту при невалидном token-е.",
            "<strong>JWT claims</strong> - username и роль можно брать из подписанного token-а.",
            "<strong>Authorized event</strong> - каждое сообщение содержит пользователя, которого подтвердил сервер.",
        ],
        "flow": [
            "Клиент получает access token через <code>/api/auth/login</code>.",
            "Клиент подключается к Socket.IO endpoint-у <code>/socket.io</code> и передаёт token в <code>auth</code>.",
            "Сервер декодирует JWT и проверяет подпись и срок действия.",
            "Если token плохой, обработчик <code>connect</code> возвращает <code>False</code>, и Socket.IO отказывает клиенту.",
            "Если token валиден, сервер сохраняет <code>sid -> username</code> и отправляет событие <code>authorized</code>.",
            "Событие <code>authorized_message</code> берёт username из серверного словаря, а не из клиентского payload.",
        ],
        "endpoints": [
            ("POST /api/auth/login", "Демо-выдача access token-а."),
            ("GET /api/socket/info", "Количество авторизованных Socket.IO-подключений."),
            ("Socket.IO /socket.io", "Защищённые события <code>authorized</code> и <code>authorized_message</code>."),
        ],
        "code": '''
def authorize_socketio(auth: dict | None) -> str | None:
    token = (auth or {}).get("access_token") or (auth or {}).get("token")
    if not token:
        return None
    try:
        return verify_token(str(token))
    except HTTPException:
        return None


@sio.event
async def connect(sid, environ, auth):
    username = authorize_socketio(auth)
    if username is None:
        return False
    authorized_clients[sid] = username
    await sio.emit("authorized", {"sid": sid, "username": username}, to=sid)
        ''',
        "code_notes": [
            "Важно проверять token в <code>connect</code>, до обработки любых пользовательских событий.",
            "Клиенту нельзя доверять username из сообщения: он должен быть взят из JWT.",
            "Token передаётся в Socket.IO auth payload, а не в query string raw WebSocket URL.",
        ],
        "task": "Добавьте claim <code>role</code> в token и запретите событие <code>admin_message</code> всем, кроме admin.",
        "answer": '''
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
role = payload.get("role")
if role != "admin":
    return
        ''',
        "answer_notes": [
            "Authorization для Socket.IO - это не только проверка token-а при connect, но и проверка доступа к конкретному событию.",
            "Для сложных правил лучше вынести проверку в отдельную функцию.",
        ],
    },
    "chapter12": {
        "number": 12,
        "port": 8012,
        "title": "Глава 12: Socket.IO чат, БД и тестирование",
        "subtitle": "Chat API, SQLAlchemy storage, service layer, Socket.IO events и тестовая SQLite-БД.",
        "outcome": "После главы вы умеете хранить сообщения чата в БД, отдавать их через REST и отправлять новые сообщения через Socket.IO.",
        "concepts": [
            "<strong>TestClient</strong> - синхронный клиент для тестирования ASGI-приложения.",
            "<strong>dependency_overrides</strong> - замена production dependency тестовой реализацией.",
            "<strong>sqlite:// + StaticPool</strong> - одна in-memory БД на весь тестовый engine.",
            "<strong>Service layer</strong> - класс <code>ChatService</code>, который можно проверять отдельно.",
            "<strong>Socket.IO chat event</strong> - событие <code>chat_message</code> сохраняет сообщение через тот же service layer.",
        ],
        "flow": [
            "REST endpoint создаёт группу через <code>ChatService.create_group</code>.",
            "Socket.IO клиент подключается к <code>/socket.io</code> и отправляет <code>join_group</code>.",
            "Клиент отправляет событие <code>chat_message</code> с <code>text</code>, <code>sender</code> и <code>group_id</code>.",
            "Socket.IO handler открывает SQLAlchemy Session и вызывает <code>ChatService.send_message</code>.",
            "Сообщение сохраняется в SQLite и превращается в простой JSON через <code>message_to_dict</code>.",
            "Сервер делает <code>emit</code> в комнату группы, а REST endpoint может потом вернуть ту же запись из БД.",
        ],
        "endpoints": [
            ("POST /api/chat/groups", "Создание группы."),
            ("GET /api/chat/groups", "Список групп."),
            ("POST /api/chat/messages", "Отправка сообщения."),
            ("GET /api/chat/messages?group_id=...", "Получение сообщений, опционально по группе."),
            ("GET /api/chat/realtime", "Справка по Socket.IO events главы."),
            ("Socket.IO /socket.io", "События <code>set_name</code>, <code>join_group</code>, <code>chat_message</code>, <code>list_messages</code>."),
        ],
        "code": '''
@sio.event
async def chat_message(sid, data):
    sender = data.get("sender") or socketio_clients.get(sid, "anonymous")
    text = data.get("text") or data.get("message", "")
    group_id = data.get("group_id")
    with SessionLocal() as db:
        service = ChatService(db)
        message = service.send_message(text=text, sender=sender, group_id=group_id)
        payload = {"event": "chat_message", "message": message_to_dict(message)}
    room = f"group:{group_id}" if group_id is not None else "global"
    await sio.emit("chat_message", payload, room=room)
        ''',
        "code_notes": [
            "Socket.IO handler использует тот же <code>ChatService</code>, что и REST API, поэтому бизнес-правила не дублируются.",
            "Для каждого Socket.IO события открывается короткая Session и закрывается после сохранения сообщения.",
            "REST API и Socket.IO смотрят на одну таблицу, поэтому сообщение, отправленное через событие, видно через <code>GET /api/chat/messages</code>.",
        ],
        "task": "Добавьте удаление группы чата: метод <code>ChatService.delete_group</code>, endpoint <code>DELETE /api/chat/groups/{group_id}</code>, Socket.IO событие <code>delete_group</code> и тест, который доказывает, что сообщения удалённой группы больше не возвращаются.",
        "answer": '''
@sio.event
async def delete_group(sid, data):
    group_id = int(data["group_id"])
    with SessionLocal() as db:
        service = ChatService(db)
        service.delete_group(group_id)
    await sio.emit("group_deleted", {"group_id": group_id})
        ''',
        "answer_notes": [
            "Сначала напишите тест на ожидаемое поведение service method, затем подключайте Socket.IO событие.",
            "Решите явно: сообщения удаляются каскадно или получают <code>group_id=None</code>. Для учебного чата проще каскадное удаление.",
        ],
    },
}


FULL_SOLUTIONS = {
    "chapter01": [
        {
            "title": "Что меняем",
            "body": "Задача просит добавить новую операцию калькулятора. Никакие новые модели не нужны: входные данные такие же, как у add/subtract/multiply/divide.",
            "items": [
                "Открыть файл <code>chapter01/app/main.py</code>.",
                "Найти блок endpoint-ов калькулятора.",
                "Добавить новый endpoint рядом с остальными операциями.",
                "Проверить через Swagger, что endpoint появился в группе calculator.",
            ],
        },
        {
            "title": "Полный API-код после изменения",
            "body": "Ниже не одна функция, а полный учебный API-файл без HTML-шаблонов и static-файлов. Для задачи калькулятора они не нужны, поэтому в ответе оставляем только FastAPI app, модели, middleware, endpoint-ы и запуск через Uvicorn.",
            "code": '''
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Глава 1: FastAPI basics",
    description="Middleware, REST API, OpenAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class CalculationRequest(BaseModel):
    a: float
    b: float


@app.middleware("http")
async def add_lesson_header(request, call_next):
    response = await call_next(request)
    response.headers["X-FastAPI-Book-Chapter"] = "01"
    return response


@app.post("/api/calculator/add")
async def add(request: CalculationRequest):
    return {"result": request.a + request.b, "operation": "add"}


@app.post("/api/calculator/subtract")
async def subtract(request: CalculationRequest):
    return {"result": request.a - request.b, "operation": "subtract"}


@app.post("/api/calculator/multiply")
async def multiply(request: CalculationRequest):
    return {"result": request.a * request.b, "operation": "multiply"}


@app.post("/api/calculator/divide")
async def divide(request: CalculationRequest):
    if request.b == 0:
        raise HTTPException(status_code=400, detail="Деление на ноль невозможно")
    return {"result": request.a / request.b, "operation": "divide"}


@app.get("/api/headers/demo")
async def headers_demo(
    user_agent: Annotated[str | None, Header()] = None,
    x_demo_client: Annotated[str | None, Header()] = None,
):
    return {
        "user_agent": user_agent,
        "x_demo_client": x_demo_client,
        "note": "Response header X-FastAPI-Book-Chapter добавляет middleware.",
    }


@app.post("/api/calculator/power")
async def power(request: CalculationRequest):
    return {"result": request.a ** request.b, "operation": "power"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("chapter01.app.main:app", host="127.0.0.1", port=8001, reload=True)
            ''',
        },
        {
            "title": "Как проверить",
            "body": "Запустите главу и выполните запросы через Swagger или curl.",
            "checks": [
                ("POST /api/calculator/power", 'Body: <code>{"a": 2, "b": 3}</code> → <code>{"result": 8, "operation": "power"}</code>'),
                ("POST /api/calculator/power", 'Body: <code>{"a": 5, "b": 0}</code> → <code>{"result": 1, "operation": "power"}</code>'),
            ],
        },
    ],
    "chapter02": [
        {
            "title": "Где должен лежать код",
            "body": "Ниже показан точный вариант решения. Вставьте dependency рядом с другими provider-функциями, а endpoint - рядом с остальными route-ами главы.",
            "items": [
                "Новые импорты не нужны: <code>Depends</code> и <code>logging</code> уже есть в файле.",
                "<code>get_log_prefix</code> можно поставить после <code>get_logger</code> или рядом с ним.",
                "Endpoint <code>pretty_log</code> можно поставить после <code>logger_demo</code> или рядом с другими endpoint-ами <code>/api/dependency-injection/*</code>.",
                "Важно: в endpoint-е префикс приходит из параметра <code>prefix</code>, а не создаётся внутри тела функции.",
            ],
        },
        {
            "title": "Полный код новой dependency и endpoint-а",
            "code": '''
def get_log_prefix() -> str:
    return "[DI LOG]"


@app.get("/api/dependency-injection/pretty-log")
async def pretty_log(
    message: str = "hello",
    prefix: str = Depends(get_log_prefix),
    app_logger: logging.Logger = Depends(get_logger),
):
    formatted_message = f"{prefix} {message}"
    app_logger.info(formatted_message)
    return {"formatted_message": formatted_message}
            ''',
        },
        {
            "title": "Как проверить",
            "body": "Вызовите endpoint с разными сообщениями. В JSON должна вернуться строка с префиксом, а в консоли приложения должна появиться такая же запись лога.",
            "checks": [
                ("GET /api/dependency-injection/pretty-log?message=hello", "Ответ содержит <code>{\"formatted_message\":\"[DI LOG] hello\"}</code>."),
                ("GET /api/dependency-injection/pretty-log?message=FastAPI", "Сообщение меняется, а префикс остаётся тем же."),
                ("Консоль", "В логах приложения видно готовую строку, которую собрал endpoint."),
            ],
        },
    ],
    "chapter03": [
        {
            "title": "Что добавляем",
            "body": "Добавляем новый метод во внешний сервис и отдельный endpoint. Endpoint остаётся тонким: он только вызывает сервис и обрабатывает ошибку.",
            "items": [
                "Добавить метод <code>get_post_comments</code> в <code>ExternalApiService</code>.",
                "Добавить route <code>GET /api/http-client/post/{post_id}/comments</code>.",
                "Использовать тот же <code>map_http_error</code>, что и в остальных методах.",
            ],
        },
        {
            "title": "Полный код метода сервиса и endpoint-а",
            "code": '''
class ExternalApiService:
    def __init__(self, base_url: str = JSONPLACEHOLDER):
        self.base_url = base_url

    async def get_post_comments(self, post_id: int) -> list[dict]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}/comments")
            response.raise_for_status()
            return response.json()


@app.get("/api/http-client/post/{post_id}/comments")
async def get_post_comments(
    post_id: int,
    service: ExternalApiService = Depends(get_external_api_service),
):
    try:
        return await service.get_post_comments(post_id)
    except httpx.HTTPError as error:
        raise map_http_error(error) from error
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("GET /api/http-client/post/1/comments", "Вернётся список комментариев к посту 1."),
                ("GET /api/http-client/post/999999/comments", "Внешний API может вернуть пустой список или ошибку, это зависит от сервиса."),
            ],
        },
    ],
    "chapter04": [
        {
            "title": "Что создаём",
            "body": "Добавляем новый тип ошибки, handler для него и demo-endpoint, чтобы можно было увидеть HTTP 503 в Swagger.",
            "items": [
                "Создать класс <code>NotReadyError</code>.",
                "Зарегистрировать <code>@app.exception_handler(NotReadyError)</code>.",
                "Добавить endpoint, который бросает эту ошибку для проверки.",
            ],
        },
        {
            "title": "Полный код ошибки, handler-а и проверки",
            "code": '''
class NotReadyError(Exception):
    pass


@app.exception_handler(NotReadyError)
async def not_ready_handler(request, exc: NotReadyError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "Сервис временно недоступен",
            "path": str(request.url.path),
        },
    )


@app.get("/api/error-demo/not-ready")
async def not_ready():
    raise NotReadyError()
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("GET /api/error-demo/not-ready", "HTTP 503 и JSON с <code>error</code>."),
                ("GET /api/error-demo/success", "HTTP 200, чтобы убедиться, что приложение в целом работает."),
            ],
        },
    ],
    "chapter05": [
        {
            "title": "Что добавляем",
            "body": "Для полноценной страницы регистрации нужны три части: Pydantic-модель формы, GET-handler для показа страницы и POST-handler для обработки отправки.",
            "items": [
                "Добавить модель <code>RegistrationForm</code> в <code>chapter05/app/main.py</code>.",
                "Добавить <code>GET /register</code> и <code>POST /register</code>.",
                "Создать шаблон <code>chapter05/templates/register.html</code>.",
            ],
        },
        {
            "title": "Полный код Python-части",
            "code": '''
class RegistrationForm(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username", "email", "password")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Поле обязательно")
        return value.strip()

    @field_validator("email")
    @classmethod
    def email_has_at(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Email должен содержать @")
        return value

    @field_validator("password")
    @classmethod
    def password_is_long_enough(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Пароль должен быть не короче 6 символов")
        return value


@app.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"request": request, "errors": {}, "values": {}, "registered": False},
    )


@app.post("/register", response_class=HTMLResponse, include_in_schema=False)
async def submit_register(
    request: Request,
    username: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
):
    values = {"username": username, "email": email, "password": password}
    try:
        RegistrationForm(**values)
    except ValidationError as error:
        errors = {str(item["loc"][0]): item["msg"] for item in error.errors()}
        return templates.TemplateResponse(
            request,
            "register.html",
            {"request": request, "errors": errors, "values": values, "registered": False},
            status_code=400,
        )
    return templates.TemplateResponse(
        request,
        "register.html",
        {"request": request, "errors": {}, "values": values, "registered": True},
    )
            ''',
        },
        {
            "title": "Минимальный шаблон register.html",
            "code": '''
<form method="post" action="/register">
    <label>Username
        <input name="username" value="{{ values.get('username', '') }}">
        {% if errors.get('username') %}<span class="error">{{ errors.get('username') }}</span>{% endif %}
    </label>
    <label>Email
        <input name="email" value="{{ values.get('email', '') }}">
        {% if errors.get('email') %}<span class="error">{{ errors.get('email') }}</span>{% endif %}
    </label>
    <label>Password
        <input name="password" type="password">
        {% if errors.get('password') %}<span class="error">{{ errors.get('password') }}</span>{% endif %}
    </label>
    <button type="submit">Зарегистрироваться</button>
</form>
            ''',
        },
    ],
    "chapter06": [
        {
            "title": "Что меняем",
            "body": "Поле <code>category</code> должно пройти через все слои: ORM-модель, DTO для ответа, DTO для создания, DTO для обновления и миграцию.",
            "items": [
                "В <code>Product</code> добавить колонку <code>category</code>.",
                "В <code>ProductDto</code> добавить поле <code>category</code>.",
                "В <code>CreateProductDto</code> добавить обязательное или default-поле.",
                "В <code>UpdateProductDto</code> добавить optional-поле.",
                "Создать Alembic migration с <code>op.add_column</code>.",
            ],
        },
        {
            "title": "Полный набор изменений в моделях",
            "code": '''
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="general")
    description: Mapped[str] = mapped_column(String(500), default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProductDto(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price: Decimal
    stock: int

    model_config = {"from_attributes": True}


class CreateProductDto(BaseModel):
    name: str = Field(min_length=1)
    category: str = "general"
    description: str = ""
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)


class UpdateProductDto(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
            ''',
        },
        {
            "title": "Полная Alembic migration",
            "code": '''
from alembic import op
import sqlalchemy as sa


revision = "0002_add_product_category"
down_revision = "0001_create_products"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "products",
        sa.Column("category", sa.String(length=80), nullable=False, server_default="general"),
    )


def downgrade():
    op.drop_column("products", "category")
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("POST /api/products", 'Body содержит <code>"category": "books"</code>.'),
                ("GET /api/products", "Каждый продукт возвращает поле <code>category</code>."),
            ],
        },
    ],
    "chapter07": [
        {
            "title": "Что меняем",
            "body": "Admin endpoint должен состоять из отдельной dependency проверки роли и самого endpoint-а. Для demo также нужен способ создать admin-пользователя.",
            "items": [
                "Добавить dependency <code>require_admin</code>.",
                "Добавить endpoint <code>GET /api/admin</code>.",
                "Для учебной проверки можно назначать role <code>admin</code> пользователю с username <code>admin</code>.",
            ],
        },
        {
            "title": "Полный код проверки admin-роли",
            "code": '''
def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@app.get("/api/admin")
async def admin_area(user: dict = Depends(require_admin)):
    return {
        "message": "Это admin endpoint",
        "username": user["username"],
        "role": user["role"],
    }
            ''',
        },
        {
            "title": "Как выдать admin-роль в учебном примере",
            "code": '''
role = "admin" if request.username == "admin" else "user"
USERS[request.username] = {
    "username": request.username,
    "email": request.email,
    "password_hash": pwd_context.hash(request.password),
    "role": role,
}
token, expires = create_access_token(request.username, role)
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("POST /api/auth/register", "Создайте пользователя <code>admin</code>, получите token."),
                ("GET /api/admin", "С admin token вернётся 200."),
                ("GET /api/admin", "С token обычного пользователя вернётся 403."),
            ],
        },
    ],
    "chapter08": [
        {
            "title": "Что меняем",
            "body": "Нужно добавить поле в ORM-модель refresh token-а и заполнять его во всех местах, где token отзывается.",
            "items": [
                "Добавить поле <code>revoked_at</code> в модель <code>RefreshToken</code>.",
                "Заполнять <code>revoked_at</code> в <code>/refresh</code>, когда старый token отзывается.",
                "Заполнять <code>revoked_at</code> в <code>/revoke</code>.",
                "Для logout обновлять все активные token-ы пользователя.",
            ],
        },
        {
            "title": "Полный фрагмент модели и revoke-логики",
            "code": '''
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped[User] = relationship(back_populates="refresh_tokens")


def revoke_token(stored: RefreshToken) -> None:
    stored.revoked = True
    stored.revoked_at = datetime.utcnow()
            ''',
        },
        {
            "title": "Где использовать revoke_token",
            "code": '''
# В /api/auth/refresh
revoke_token(stored)
access_token, access_expires = create_access_token(user)
refresh_token, refresh_expires = create_refresh_token(db, user)
db.commit()


# В /api/auth/revoke
if stored is not None and not stored.revoked:
    revoke_token(stored)
    db.commit()
            ''',
        },
    ],
    "chapter09": [
        {
            "title": "Что меняем",
            "body": "Команда <code>/who</code> должна обрабатываться внутри receive loop до broadcast. Это команда только для отправителя.",
            "items": [
                "Внутри цикла получить текст сообщения.",
                "Проверить, равно ли сообщение <code>/who</code>.",
                "Если да, отправить ответ только текущему WebSocket.",
                "Если нет, оставить обычный broadcast.",
            ],
        },
        {
            "title": "Полный receive loop после изменения",
            "code": '''
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()

            if message == "/who":
                await websocket.send_json({
                    "event": "connections",
                    "count": len(manager.active_connections),
                })
                continue

            await manager.broadcast({
                "event": "message",
                "connection_id": connection_id,
                "message": message,
            })
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        await manager.broadcast({"event": "disconnected", "connection_id": connection_id})
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("WS /ws", "Отправьте <code>/who</code> и получите count только в текущем клиенте."),
                ("WS /ws", "Отправьте обычный текст и получите broadcast у всех клиентов."),
            ],
        },
    ],
    "chapter10": [
        {
            "title": "Что меняем",
            "body": "Добавляем новое Socket.IO событие. Оно удаляет текущее подключение из комнаты и возвращает подтверждение только этому клиенту.",
            "items": [
                "В файл <code>chapter10/app/main.py</code> добавить обработчик <code>@sio.event</code>.",
                "Назвать функцию <code>leave_room</code>, чтобы имя функции совпало с именем события.",
                "Взять имя комнаты из payload или использовать <code>general</code>.",
                "Вызвать <code>sio.leave_room</code> и отправить событие <code>left_room</code> текущему клиенту.",
            ],
        },
        {
            "title": "Полный блок Socket.IO событий для комнат",
            "code": '''
@sio.event
async def join_room(sid, data):
    room = data.get("room", "general")
    await sio.enter_room(sid, room)
    socketio_rooms[room].add(sid)
    await sio.emit("joined_room", {"room": room}, to=sid)


@sio.event
async def leave_room(sid, data):
    room = data.get("room", "general")
    await sio.leave_room(sid, room)
    socketio_rooms[room].discard(sid)
    await sio.emit("left_room", {"room": room}, to=sid)


@sio.event
async def chat_message(sid, data):
    room = data.get("room")
    payload = {
        "event": "chat_message",
        "from": socketio_clients.get(sid, "anonymous"),
        "message": data.get("message", ""),
        "room": room,
    }
    if room:
        await sio.emit("chat_message", payload, room=room)
    else:
        await sio.emit("chat_message", payload)
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("Socket.IO join_room", 'Отправьте <code>{ room: "python" }</code> и получите событие <code>joined_room</code>.'),
                ("Socket.IO leave_room", 'Отправьте <code>{ room: "python" }</code> и получите событие <code>left_room</code>.'),
            ],
        },
    ],
    "chapter11": [
        {
            "title": "Что меняем",
            "body": "Нужно добавить роль в JWT и проверять её в Socket.IO событии, которое доступно только admin.",
            "items": [
                "Добавить claim <code>role</code> при создании access token-а.",
                "Вернуть из helper-а проверки token-а username и role.",
                "Сохранить данные пользователя в словаре <code>authorized_clients</code> при Socket.IO connect.",
                "Добавить событие <code>admin_message</code>.",
                "Если роль текущего <code>sid</code> не admin, отправить событие <code>forbidden</code> только этому клиенту.",
            ],
        },
        {
            "title": "Полный код token payload и admin-события",
            "code": '''
def create_access_token(username: str, role: str = "user") -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": username, "role": role, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def verify_user_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": str(payload["sub"]), "role": str(payload.get("role", "user"))}
    except (JWTError, KeyError) as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error


@sio.event
async def admin_message(sid, data):
    user = authorized_clients.get(sid)
    if user is None or user["role"] != "admin":
        await sio.emit("forbidden", {"reason": "admin role required"}, to=sid)
        return
    await sio.emit("admin_message", {
        "from": user["username"],
        "message": data.get("message", ""),
    }, room="admins")
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("Socket.IO connect", "Обычный пользователь подключается с <code>auth: { access_token }</code>."),
                ("Socket.IO admin_message", "Обычный пользователь получает событие <code>forbidden</code>."),
                ("Socket.IO admin_message", "Admin получает событие <code>admin_message</code>."),
            ],
        },
    ],
    "chapter12": [
        {
            "title": "Что меняем",
            "body": "Задача про удаление группы должна быть решена на всех уровнях: service method, REST endpoint, Socket.IO событие и тест.",
            "items": [
                "Добавить метод <code>delete_group</code> в <code>ChatService</code>.",
                "Решить, что делать с сообщениями группы. В учебном варианте удаляем их перед удалением группы.",
                "Добавить endpoint <code>DELETE /api/chat/groups/{group_id}</code>.",
                "Добавить Socket.IO событие <code>delete_group</code>, которое вызывает тот же service method.",
                "Написать тест: создать группу, сообщение, удалить группу, проверить 204 и пустой список сообщений.",
            ],
        },
        {
            "title": "Полный service method и endpoint",
            "code": '''
class ChatService:
    def delete_group(self, group_id: int) -> None:
        group = self.db.get(ChatGroup, group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        self.db.query(Message).filter(Message.group_id == group_id).delete()
        self.db.delete(group)
        self.db.commit()


@app.delete("/api/chat/groups/{group_id}", status_code=204)
async def delete_group(group_id: int, service: ChatService = Depends(get_chat_service)):
    service.delete_group(group_id)
            ''',
        },
        {
            "title": "Полное Socket.IO событие",
            "code": '''
@sio.event
async def delete_group(sid, data):
    group_id = int(data["group_id"])
    with SessionLocal() as db:
        service = ChatService(db)
        service.delete_group(group_id)
    await sio.emit("group_deleted", {"group_id": group_id})
            ''',
        },
        {
            "title": "Полный тест",
            "code": '''
def test_delete_group_removes_group_messages():
    _, override = make_sqlite_override(Base, get_db)
    app.dependency_overrides[get_db] = override
    try:
        client = TestClient(app)
        group = client.post("/api/chat/groups", json={"name": "general"}).json()
        client.post("/api/chat/messages", json={
            "text": "hello",
            "sender": "anna",
            "group_id": group["id"],
        })

        response = client.delete(f"/api/chat/groups/{group['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/chat/messages?group_id={group['id']}").json() == []
    finally:
        app.dependency_overrides.clear()
            ''',
        },
    ],
}


PRACTICE_STEPS = {
    "chapter02": [
        "Откройте <code>chapter02/app/main.py</code> и найдите существующий endpoint <code>logger_demo</code>. Он показывает, как endpoint уже получает logger через <code>Depends</code>.",
        "Сделайте новую dependency максимально простой: она должна возвращать одну строку-префикс для логов.",
        "В новом endpoint-е примите обычный query-параметр <code>message</code>. Для проверки удобно дать ему значение по умолчанию.",
        "Не пишите префикс прямо внутри endpoint-а. Смысл задачи - получить этот префикс через DI.",
        "Верните готовую строку в поле <code>formatted_message</code>, чтобы результат было видно в Swagger без чтения консоли.",
        "После этого откройте Swagger и попробуйте два значения <code>message</code>: <code>hello</code> и <code>FastAPI</code>.",
    ],
}


TASK_CRITERIA = {
    "chapter01": [
        ("POST /api/calculator/power", 'Body: <code>{"a": 2, "b": 3}</code> -> <code>{"result": 8, "operation": "power"}</code>.'),
        ("POST /api/calculator/power", 'Body: <code>{"a": 5, "b": 0}</code> -> <code>{"result": 1, "operation": "power"}</code>.'),
        ("Swagger", "Новый endpoint виден в документации после перезапуска приложения."),
    ],
    "chapter02": [
        ("GET /api/dependency-injection/pretty-log?message=hello", "Ответ содержит <code>formatted_message</code> со значением <code>[DI LOG] hello</code>."),
        ("Другой message", "При <code>message=FastAPI</code> endpoint возвращает <code>[DI LOG] FastAPI</code>."),
        ("DI", "Префикс приходит через dependency, а не записан напрямую внутри endpoint-а."),
    ],
    "chapter03": [
        ("GET /api/http-client/post/1/comments", "Возвращается список комментариев внешнего API."),
        ("Service layer", "Endpoint вызывает метод <code>ExternalApiService.get_post_comments</code>."),
        ("Ошибки", "HTTP-ошибки внешнего API проходят через общий <code>map_http_error</code>."),
    ],
    "chapter04": [
        ("GET /api/error-demo/not-ready", "Возвращается HTTP 503."),
        ("JSON ошибки", "Ответ содержит сообщение <code>Сервис временно недоступен</code> и path запроса."),
        ("Остальные endpoint-ы", "Успешные endpoint-ы продолжают возвращать HTTP 200."),
    ],
    "chapter05": [
        ("GET /register", "Открывается HTML-форма регистрации."),
        ("POST /register", "Пароль короче 6 символов возвращает страницу с ошибкой."),
        ("POST /register", "Валидные данные показывают успешную регистрацию."),
    ],
    "chapter06": [
        ("POST /api/products", "Можно создать продукт с полем <code>category</code>."),
        ("GET /api/products", "Ответ возвращает <code>category</code> у каждого продукта."),
        ("Alembic", "Миграция добавляет колонку <code>category</code> и умеет откатываться."),
    ],
    "chapter07": [
        ("GET /api/admin", "Обычный пользователь получает HTTP 403."),
        ("GET /api/admin", "Admin-пользователь получает HTTP 200."),
        ("Token", "Роль берётся из проверенного пользователя/token-а, а не из произвольного JSON клиента."),
    ],
    "chapter08": [
        ("Refresh rotation", "Старый refresh token получает <code>revoked=True</code> и заполненный <code>revoked_at</code>."),
        ("Revoke endpoint", "При ручном revoke также заполняется <code>revoked_at</code>."),
        ("Logout", "Все активные refresh token-ы пользователя получают время отзыва."),
    ],
    "chapter09": [
        ("WS /ws", "Сообщение <code>/who</code> возвращает текущему клиенту количество подключений."),
        ("Нет broadcast", "<code>/who</code> не рассылается всем клиентам как обычное сообщение."),
        ("Обычный текст", "Обычное сообщение по-прежнему уходит в broadcast."),
    ],
    "chapter10": [
        ("Socket.IO join_room", "Клиент отправляет <code>{ room: \"python\" }</code> и получает <code>joined_room</code>."),
        ("Socket.IO leave_room", "Клиент отправляет <code>{ room: \"python\" }</code> и получает <code>left_room</code>."),
        ("Room state", "После выхода sid удаляется из учебного словаря комнат."),
    ],
    "chapter11": [
        ("Socket.IO connect", "Пользователь подключается с <code>auth: { access_token }</code>."),
        ("admin_message", "Обычный пользователь получает событие <code>forbidden</code>."),
        ("admin_message", "Admin-пользователь получает событие <code>admin_message</code>."),
    ],
    "chapter12": [
        ("DELETE /api/chat/groups/{group_id}", "Удаление существующей группы возвращает HTTP 204."),
        ("GET /api/chat/messages", "После удаления группы сообщения этой группы больше не возвращаются."),
        ("Socket.IO delete_group", "Событие вызывает тот же <code>ChatService.delete_group</code> и отправляет <code>group_deleted</code>."),
    ],
}


BEGINNER_GUIDES = {
    "chapter01": {
        "plain": [
            "Эта глава показывает не только endpoint-ы, а весь минимальный backend-сервис: файл приложения, объект <code>app</code>, сервер Uvicorn, REST-запросы, JSON и ответы.",
            "Представьте обычный сайт: браузер просит HTML-страницу. REST API работает похоже, но вместо HTML чаще возвращает JSON, чтобы данные мог читать frontend, мобильное приложение или другой backend.",
            "FastAPI не запускается сам по себе как отдельная программа. FastAPI описывает приложение, а Uvicorn поднимает сервер, слушает порт и передаёт запросы в FastAPI.",
            "Главная цепочка этой главы: клиент отправил HTTP request → Uvicorn принял запрос → FastAPI нашёл endpoint → Pydantic проверил JSON → функция вернула словарь → клиент получил HTTP response.",
            "Если вы только начинаете Python: двоеточие <code>:</code> открывает блок кода, а отступы показывают, какие строки относятся к классу, функции или условию.",
        ],
        "line_by_line": [
            ("<code>from typing import Annotated</code>", "Импортируем способ добавить к типу Python подсказку FastAPI. Ниже он нужен для чтения headers."),
            ("<code>from fastapi import FastAPI, Header, HTTPException</code>", "Импортируем основные инструменты FastAPI: само приложение, чтение header-ов и ошибку HTTP."),
            ("<code>from pydantic import BaseModel</code>", "Импортируем базовый класс Pydantic. Он нужен, чтобы описывать и проверять JSON от клиента."),
            ("<code>app = FastAPI(...)</code>", "Создаём объект приложения. Именно его Uvicorn будет запускать и именно в нём FastAPI хранит маршруты."),
            ("<code>docs_url=\"/docs\"</code>", "Говорим FastAPI, где показать Swagger UI. Swagger позволяет руками отправлять запросы без отдельной программы."),
            ("<code>redoc_url=\"/redoc\"</code>", "Говорим FastAPI, где показать ReDoc. Это более спокойная страница документации для чтения схемы API."),
            ("<code>class CalculationRequest(BaseModel):</code>", "Создаём класс-описание входных данных. Это не вычисление, а схема: какие поля пользователь должен прислать в JSON."),
            ("<code>BaseModel</code>", "Базовый класс Pydantic. Благодаря ему FastAPI понимает, что тело запроса нужно проверить."),
            ("<code>a: float</code>", "Поле <code>a</code> обязательно. <code>float</code> значит число с дробной частью или без неё: <code>10</code>, <code>10.5</code>, <code>0</code>."),
            ("<code>b: float</code>", "Второе обязательное число. Если пользователь пришлёт строку, которую нельзя превратить в число, FastAPI вернёт ошибку валидации."),
            ("<code>@app.middleware(\"http\")</code>", "Регистрируем функцию, которая оборачивает каждый HTTP-запрос. Она срабатывает и для HTML-страницы, и для REST endpoint-ов."),
            ("<code>response = await call_next(request)</code>", "Передаём запрос дальше в FastAPI. Без этой строки endpoint не выполнится, потому что middleware остановит цепочку."),
            ("<code>response.headers[\"X-FastAPI-Book-Chapter\"] = \"01\"</code>", "Добавляем учебный HTTP header в ответ. Так видно, что middleware действительно прошёл после endpoint-а."),
            ("<code>@app.post(\"/api/calculator/add\")</code>", "Связываем HTTP method <code>POST</code> и path <code>/api/calculator/add</code> с функцией <code>add</code>."),
            ("<code>@app.post(\"/api/calculator/divide\")</code>", "Декоратор. Он говорит FastAPI: когда придёт POST-запрос на этот адрес, вызови функцию ниже."),
            ("<code>async def divide(...):</code>", "Объявляем асинхронную функцию endpoint-а. <code>async</code> нужно, чтобы FastAPI мог эффективно обслуживать много запросов."),
            ("<code>request: CalculationRequest</code>", "Параметр функции. FastAPI создаст объект <code>CalculationRequest</code> из JSON-тела запроса и положит его в переменную <code>request</code>."),
            ("<code>if request.b == 0:</code>", "Обычная проверка Python: если второе число равно нулю, делить нельзя."),
            ("<code>raise HTTPException(...)</code>", "Останавливаем выполнение функции и возвращаем клиенту ошибку HTTP 400. Это лучше, чем дать Python упасть с делением на ноль."),
            ("<code>return {\"result\": ...}</code>", "Возвращаем словарь. FastAPI сам превратит его в JSON-ответ."),
            ("<code>@app.get(\"/api/headers/demo\")</code>", "Учебный endpoint для просмотра request headers. Его удобно открыть в Swagger и попробовать разные значения."),
            ("<code>user_agent: Annotated[str | None, Header()]</code>", "Просим FastAPI взять header <code>User-Agent</code>. Если header отсутствует, значение будет <code>None</code>."),
            ("<code>x_demo_client: Annotated[str | None, Header()]</code>", "Просим FastAPI взять custom header <code>X-Demo-Client</code>. В параметре Python используется underscore, а в HTTP header - дефис."),
            ("<code>\"note\": \"Response header ...\"</code>", "Напоминаем, что тело ответа и headers ответа - разные места. Это поле находится в JSON body, а <code>X-FastAPI-Book-Chapter</code> находится в response headers."),
            ("<code>if __name__ == \"__main__\":</code>", "Этот блок запускается только если файл стартует напрямую командой <code>python chapter01/app/main.py</code>. При обычном импорте для тестов он не выполняется."),
            ("<code>uvicorn.run(...)</code>", "Программный способ запустить тот же сервер, который обычно запускают командой <code>uvicorn ...</code>."),
        ],
        "mistakes": [
            "Забыть двоеточие после <code>class</code>, <code>def</code> или <code>if</code>.",
            "Сделать неправильный отступ: в Python отступы заменяют фигурные скобки.",
            "Написать <code>request[\"b\"]</code> вместо <code>request.b</code>. Pydantic-модель здесь используется как объект с полями.",
            "Не проверить деление на ноль и получить внутреннюю ошибку сервера вместо понятного ответа 400.",
            "Думать, что <code>app = FastAPI()</code> само открывает порт. Порт открывает Uvicorn.",
            "Писать <code>uvicorn app</code> вместо полного пути <code>uvicorn chapter01.app.main:app</code>. Uvicorn должен знать, откуда импортировать объект приложения.",
            "Отправлять JSON без header <code>Content-Type: application/json</code> в ручных curl-запросах.",
            "Искать request headers внутри JSON body. Headers и body приходят в разных частях HTTP-запроса.",
            "Писать в Python параметр <code>x-demo-client</code>. В Python нельзя дефисы в имени переменной, поэтому пишем <code>x_demo_client</code>, а FastAPI сопоставляет это с header-ом <code>X-Demo-Client</code>.",
            "Путать path <code>/api/calculator/add</code> и полный URL <code>http://localhost:8001/api/calculator/add</code>. Path - это только часть после домена и порта.",
        ],
    },
    "chapter02": {
        "plain": [
            "Dependency Injection в FastAPI - это способ сказать: “мне для работы нужна вот эта штука, подготовь её за меня”.",
            "Endpoint не обязан сам создавать logger, settings, сервис, пользователя или подключение к базе. Он может попросить FastAPI сделать это через <code>Depends</code>.",
            "Самая важная мысль: dependency - обычная Python-функция. Магия только в том, что FastAPI вызывает её перед endpoint-ом и подставляет результат в параметр.",
            "Если видите <code>service: Service = Depends(get_service)</code>, читайте это так: “в переменную <code>service</code> положи результат функции <code>get_service</code>”.",
            "Скобки после <code>get_service</code> не ставятся, потому что функцию должен вызвать FastAPI во время запроса, а не Python при запуске файла.",
            "DI особенно полезен, когда одну и ту же подготовку надо использовать в нескольких endpoint-ах или подменить в тестах.",
        ],
        "line_by_line": [
            ("<code>import logging</code>", "Подключаем стандартный модуль логирования Python. Он нужен для примера с logger dependency."),
            ("<code>from dataclasses import dataclass</code>", "Импортируем удобный способ создавать простые классы-данные."),
            ("<code>from fastapi import Depends, Query</code>", "Берём <code>Depends</code> для DI и <code>Query</code> для чтения query-параметров внутри dependency."),
            ("<code>logger = logging.getLogger(...)</code>", "Создаём logger один раз на уровне модуля. Dependency потом будет возвращать этот объект."),
            ("<code>@dataclass</code>", "Просим Python автоматически сделать простой класс для хранения данных. Так не нужно вручную писать <code>__init__</code>."),
            ("<code>class InstanceService:</code>", "Учебный сервис с типом и id. По id удобно видеть, новый это объект или тот же самый."),
            ("<code>class AppSettings:</code>", "Учебные настройки приложения. Они показывают dependency, которая возвращает заранее созданный объект."),
            ("<code>class UserContext:</code>", "Учебный объект пользователя. В реальном проекте здесь могли бы быть id, email, роли и права."),
            ("<code>singleton_service = ...</code>", "Объект создаётся один раз при загрузке модуля. Потом dependency возвращает именно его."),
            ("<code>app_settings = ...</code>", "Настройки тоже создаются один раз. Это удобно, потому что они обычно не должны меняться во время запроса."),
            ("<code>def get_scoped_service()</code>", "Обычная функция Python. Её задача - создать и вернуть объект сервиса."),
            ("<code>-&gt; InstanceService</code>", "Подсказка типа. Она не создаёт объект сама, но помогает читать код и понимать, что функция возвращает."),
            ("<code>return InstanceService(...)</code>", "Создаём новый объект и сразу возвращаем его тому, кто вызвал функцию."),
            ("<code>def get_singleton_service()</code>", "Dependency не создаёт объект, а возвращает уже готовый <code>singleton_service</code>."),
            ("<code>def get_transient_service()</code>", "Создаёт новый объект каждый раз, когда FastAPI реально вызывает эту dependency."),
            ("<code>def get_settings()</code>", "Provider-функция для настроек. Endpoint не знает, где настройки созданы, он просто просит их через <code>Depends</code>."),
            ("<code>def get_logger()</code>", "Provider-функция для logger-а. Так endpoint не привязан к конкретному способу создания logger-а."),
            ("<code>Query(\"guest\")</code>", "Говорит FastAPI взять значение из query string. Если параметра нет, использовать <code>guest</code>."),
            ("<code>get_current_user(...)</code>", "Dependency может сама принимать данные запроса и собрать из них удобный объект."),
            ("<code>@app.get(...)</code>", "Регистрируем GET endpoint. Браузер или Swagger может вызвать его обычным GET-запросом."),
            ("<code>async def lifetimes(...)</code>", "Endpoint принимает не только данные запроса, но и зависимости."),
            ("<code>Depends(get_scoped_service)</code>", "FastAPI вызовет <code>get_scoped_service</code> и подставит результат в параметр."),
            ("<code>scoped1</code> и <code>scoped2</code>", "Оба параметра используют одну dependency. FastAPI по умолчанию кеширует результат в рамках одного запроса."),
            ("<code>singleton1</code> и <code>singleton2</code>", "Оба параметра получают один и тот же объект, потому что dependency возвращает глобальный <code>singleton_service</code>."),
            ("<code>use_cache=False</code>", "Отключаем кеш. Поэтому transient-сервис создаётся заново для каждого параметра."),
            ("<code>scoped1.id == scoped2.id</code>", "Сравниваем id, чтобы увидеть request cache прямо в JSON-ответе."),
            ("<code>settings: AppSettings = Depends(get_settings)</code>", "Endpoint просит настройки. FastAPI вызывает <code>get_settings</code> и кладёт результат в <code>settings</code>."),
            ("<code>Depends(get_current_user)</code>", "FastAPI сначала вызовет <code>get_current_user</code>, а уже готовый объект положит в параметр <code>user</code>."),
            ("<code>app_logger: logging.Logger = Depends(get_logger)</code>", "Endpoint получает logger через DI и не создаёт его внутри функции."),
            ("<code>return {\"username\": ...}</code>", "Endpoint возвращает обычный JSON, но данные для него пришли через dependency."),
        ],
        "mistakes": [
            "Вызвать dependency самому: <code>Depends(get_service())</code>. Нужно передавать функцию без скобок: <code>Depends(get_service)</code>.",
            "Думать, что <code>Depends</code> нужен только для классов. Dependency может вернуть строку, словарь, dataclass, logger, настройки или любой Python-объект.",
            "Ожидать, что FastAPI создаст новый объект при каждом параметре, хотя кеширование включено.",
            "Не понимать, что кеширование работает только внутри одного HTTP-запроса. Следующий запрос снова запускает scoped dependency.",
            "Хранить изменяемое состояние в singleton без понимания, что оно общее для всех запросов.",
            "Делать слишком много логики в dependency. Dependency должна готовить данные или сервис, а не выполнять всю бизнес-задачу endpoint-а.",
            "Путать query-параметр и dependency. В примере <code>username</code> приходит из query, а <code>UserContext</code> создаёт dependency.",
            "Использовать <code>use_cache=False</code> везде подряд. Обычно кеш FastAPI полезен, а отключать его нужно только когда точно нужен новый объект при каждом обращении.",
        ],
    },
    "chapter03": {
        "plain": [
            "Здесь приложение само становится клиентом другого API. Пользователь обращается к нам, а мы внутри делаем запрос на JSONPlaceholder.",
            "Важно не путать два направления: входящий запрос приходит в FastAPI, исходящий запрос отправляет <code>httpx</code>.",
            "Асинхронность нужна, чтобы сервер не простаивал, пока ждёт ответ внешнего сайта.",
        ],
        "line_by_line": [
            ("<code>class ExternalApiService:</code>", "Создаём класс-сервис. Он отвечает за общение с внешним API, чтобы endpoint был коротким."),
            ("<code>async def get_post(...)</code>", "Асинхронный метод. Его можно вызывать с <code>await</code>."),
            ("<code>post_id: int</code>", "Ожидаем целое число. Например, <code>1</code>, <code>2</code>, <code>10</code>."),
            ("<code>-&gt; dict</code>", "Подсказка: метод вернёт словарь Python."),
            ("<code>async with httpx.AsyncClient(...)</code>", "Открываем HTTP-клиент на время блока. После блока он корректно закрывается."),
            ("<code>base_url=self.base_url</code>", "Общий адрес внешнего сервиса задаётся один раз, дальше можно писать только путь."),
            ("<code>timeout=10.0</code>", "Если внешний сервис зависнет, мы не будем ждать вечно."),
            ("<code>await client.get(...)</code>", "Отправляем GET-запрос и ждём ответ."),
            ("<code>response.raise_for_status()</code>", "Если внешний API вернул ошибку 404/500, превращаем её в исключение."),
            ("<code>return response.json()</code>", "Берём JSON из ответа и возвращаем его как Python-объект."),
        ],
        "mistakes": [
            "Забыть <code>await</code> перед асинхронным запросом.",
            "Создавать запросы без timeout и зависнуть на плохом внешнем сервисе.",
            "Смешать логику внешнего API прямо с endpoint-ом, из-за чего код станет трудно тестировать.",
        ],
    },
    "chapter04": {
        "plain": [
            "Ошибка - это не всегда авария. Иногда это нормальная бизнес-ситуация: не найдено, неверные данные, сервис временно недоступен.",
            "FastAPI позволяет перехватывать исключения и возвращать понятный JSON вместо большого traceback.",
            "В этой главе мы учимся делать ошибки предсказуемыми для клиента.",
        ],
        "line_by_line": [
            ("<code>@app.exception_handler(DemoError)</code>", "Регистрируем обработчик для конкретного типа ошибки."),
            ("<code>async def demo_error_handler(request, exc)</code>", "Функция получит сам запрос и объект исключения."),
            ("<code>request</code>", "Из него можно взять путь, headers, query-параметры и другую информацию о запросе."),
            ("<code>exc</code>", "Это ошибка, которую кто-то бросил через <code>raise DemoError(...)</code>."),
            ("<code>JSONResponse(...)</code>", "Создаём ответ вручную: выбираем status code и тело JSON."),
            ("<code>status_code=500</code>", "Говорим клиенту, что произошла серверная ошибка."),
            ("<code>content={...}</code>", "Тело ответа. Клиент получит именно этот JSON."),
            ("<code>str(exc)</code>", "Превращаем исключение в строку, чтобы показать сообщение."),
            ("<code>str(request.url.path)</code>", "Добавляем путь, на котором произошла ошибка. Это помогает отладке."),
        ],
        "mistakes": [
            "Возвращать 200 OK при ошибке. Клиент тогда не поймёт, что запрос не удался.",
            "Показывать пользователю внутренний traceback и секретные детали сервера.",
            "Ловить вообще все исключения и скрывать настоящие баги без логирования.",
        ],
    },
    "chapter05": {
        "plain": [
            "До этого мы в основном возвращали JSON. Здесь FastAPI возвращает обычную HTML-страницу.",
            "Jinja2 - это шаблонизатор: HTML-файл с местами, куда сервер подставляет данные.",
            "Форма отправляет не JSON, а специальные form-поля. Поэтому используются параметры <code>Form</code>.",
        ],
        "line_by_line": [
            ("<code>@app.post(\"/contact\", response_class=HTMLResponse)</code>", "Этот endpoint принимает отправку формы и возвращает HTML, а не JSON."),
            ("<code>include_in_schema=False</code>", "Прячем HTML endpoint из Swagger, потому что это страница для браузера, а не API для клиента."),
            ("<code>request: Request</code>", "Объект запроса нужен Jinja2-шаблону."),
            ("<code>name: str = Form(\"\")</code>", "Берём поле <code>name</code> из HTML-формы. Если его нет, используем пустую строку."),
            ("<code>email: str = Form(\"\")</code>", "То же самое для email."),
            ("<code>message: str = Form(\"\")</code>", "То же самое для текста сообщения."),
            ("<code>values = {...}</code>", "Складываем введённые данные в словарь, чтобы при ошибке вернуть их обратно на страницу."),
            ("<code>ContactForm(**values)</code>", "Передаём словарь в Pydantic-модель. Две звёздочки означают 'развернуть словарь в именованные аргументы'."),
            ("<code>ValidationError</code>", "Если Pydantic нашёл ошибку, мы ловим её и показываем рядом с полями формы."),
        ],
        "mistakes": [
            "Забыть установить <code>python-multipart</code>, без него FastAPI не принимает формы.",
            "Не передать <code>request</code> в шаблон.",
            "При ошибке очистить форму, заставив пользователя вводить всё заново.",
        ],
    },
    "chapter06": {
        "plain": [
            "База данных хранит данные дольше, чем живёт один запрос. SQLAlchemy помогает работать с таблицами как с Python-объектами.",
            "Session - это рабочая область для операций с БД. Через неё мы добавляем, читаем, сохраняем и удаляем данные.",
            "DTO нужны, чтобы внешний JSON API не зависел напрямую от внутренней ORM-модели.",
        ],
        "line_by_line": [
            ("<code>def get_db()</code>", "Dependency-функция, которая выдаёт подключение к БД на время запроса."),
            ("<code>db = SessionLocal()</code>", "Создаём новую Session. Через неё endpoint будет работать с БД."),
            ("<code>try:</code>", "Начинаем блок, где Session отдаётся endpoint-у."),
            ("<code>yield db</code>", "Отдаём Session наружу. После завершения запроса выполнение вернётся сюда."),
            ("<code>finally:</code>", "Этот блок выполнится даже если в endpoint-е случилась ошибка."),
            ("<code>db.close()</code>", "Закрываем Session, чтобы не держать ресурсы."),
            ("<code>response_model=ProductDto</code>", "FastAPI отдаст наружу только поля, описанные в DTO."),
            ("<code>Product(**request.model_dump())</code>", "Берём проверенные поля из DTO и создаём ORM-объект."),
            ("<code>db.add(product)</code>", "Говорим Session: этот объект нужно вставить в таблицу."),
            ("<code>db.commit()</code>", "Фактически сохраняем изменения в базе."),
            ("<code>db.refresh(product)</code>", "Обновляем объект, чтобы получить id, выданный базой."),
        ],
        "mistakes": [
            "Создать объект, но забыть <code>db.commit()</code>: данные не сохранятся.",
            "Вернуть ORM-модель без DTO и случайно раскрыть лишние поля.",
            "Держать одну Session глобально на всё приложение.",
        ],
    },
    "chapter07": {
        "plain": [
            "Пользователь доказывает, кто он, через логин и пароль. После этого сервер выдаёт token.",
            "Token похож на пропуск: клиент показывает его при каждом защищённом запросе.",
            "Сервер проверяет подпись token-а и понимает, можно ли доверять данным внутри него.",
        ],
        "line_by_line": [
            ("<code>def get_current_user(...)</code>", "Dependency, которая пытается найти пользователя по Bearer token."),
            ("<code>token: str = Depends(oauth2_scheme)</code>", "FastAPI достаёт token из заголовка <code>Authorization</code>."),
            ("<code>jwt.decode(...)</code>", "Проверяем подпись JWT и читаем payload."),
            ("<code>SECRET_KEY</code>", "Секрет, которым token подписывался. Без него нельзя проверить подлинность."),
            ("<code>algorithms=[ALGORITHM]</code>", "Явно разрешаем алгоритм подписи, чтобы не принимать что попало."),
            ("<code>payload.get(\"sub\")</code>", "Берём subject token-а. В примере это username."),
            ("<code>USERS.get(...)</code>", "Ищем пользователя в demo-хранилище."),
            ("<code>if user is None</code>", "Если token указывает на несуществующего пользователя, возвращаем 401."),
            ("<code>return user</code>", "Если всё хорошо, endpoint получит готовый объект пользователя."),
        ],
        "mistakes": [
            "Хранить пароль в открытом виде вместо hash.",
            "Доверять username, который прислал клиент, вместо username из token-а.",
            "Путать 401 и 403: 401 - не вошёл, 403 - вошёл, но прав не хватает.",
        ],
    },
    "chapter08": {
        "plain": [
            "Access token должен жить недолго: если его украдут, ущерб ограничен временем жизни.",
            "Refresh token нужен, чтобы пользователь не вводил пароль каждые 15 минут.",
            "Refresh token хранится на сервере, поэтому его можно отозвать.",
        ],
        "line_by_line": [
            ("<code>db.query(RefreshToken)</code>", "Начинаем запрос к таблице refresh token-ов."),
            ("<code>.filter(...)</code>", "Ищем строку, где token совпадает с тем, что прислал клиент."),
            ("<code>.first()</code>", "Берём первую найденную строку или <code>None</code>."),
            ("<code>stored is None</code>", "Token вообще не найден в БД."),
            ("<code>stored.revoked</code>", "Token уже был отозван раньше."),
            ("<code>stored.expires_at &lt;= datetime.utcnow()</code>", "Срок действия token-а закончился."),
            ("<code>raise HTTPException(status_code=401)</code>", "Любая из этих проблем означает: клиент не может обновить сессию."),
            ("<code>stored.revoked = True</code>", "Старый refresh token больше нельзя использовать."),
            ("<code>create_access_token(user)</code>", "Создаём новый короткий access token."),
            ("<code>create_refresh_token(db, user)</code>", "Создаём новый refresh token и сохраняем его в БД."),
        ],
        "mistakes": [
            "Не отзывать старый refresh token при обновлении.",
            "Делать refresh token JWT без хранения на сервере, а потом не иметь возможности его отозвать.",
            "Хранить refresh token в небезопасном месте на клиенте.",
        ],
    },
    "chapter09": {
        "plain": [
            "Обычный HTTP-запрос короткий: клиент спросил, сервер ответил, соединение закончилось.",
            "WebSocket остаётся открытым. Клиент и сервер могут обмениваться сообщениями много раз.",
            "Для чата серверу нужно помнить, кто сейчас подключён.",
        ],
        "line_by_line": [
            ("<code>class ConnectionManager:</code>", "Создаём отдельный объект, который отвечает только за список подключений и отправку сообщений."),
            ("<code>self.active_connections</code>", "Словарь активных клиентов: ключ - id подключения, значение - объект <code>WebSocket</code>."),
            ("<code>async def connect(...)</code>", "Метод подключения. Он принимает WebSocket, сохраняет его и возвращает id клиента."),
            ("<code>await websocket.accept()</code>", "Сервер явно принимает WebSocket-соединение. Без этого обмен сообщениями не начнётся."),
            ("<code>connection_id = str(uuid4())</code>", "Создаём случайный id, чтобы отличать одно подключение от другого."),
            ("<code>await websocket.send_json(...)</code>", "Отправляем новому клиенту первое служебное сообщение: соединение принято, вот твой id."),
            ("<code>def disconnect(...)</code>", "Удаляем клиента из словаря, когда соединение закрыто."),
            ("<code>async def broadcast(...)</code>", "Проходим по всем активным клиентам и отправляем каждому одинаковый payload."),
            ("<code>list(self.active_connections.values())</code>", "Берём копию списка подключений, чтобы обход не ломался, если словарь изменится во время рассылки."),
        ],
        "mistakes": [
            "Забыть <code>await websocket.accept()</code> внутри connect.",
            "Не удалить отключившегося клиента из manager-а.",
            "Думать, что WebSocket endpoint можно проверить обычным curl как HTTP.",
        ],
    },
    "chapter10": {
        "plain": [
            "Socket.IO - это отдельная real-time технология, где общение строится вокруг событий: клиент отправляет событие, сервер обрабатывает его по имени.",
            "Вместо ручного поля <code>action</code> у каждого действия есть своё имя: <code>join_room</code>, <code>chat_message</code>, <code>direct_message</code>.",
            "Главная мысль: WebSocket может быть транспортом, а Socket.IO добавляет поверх него удобные события, комнаты и клиентскую библиотеку.",
        ],
        "line_by_line": [
            ("<code>sio = socketio.AsyncServer(...)</code>", "Создаём Socket.IO server, который умеет принимать асинхронные события."),
            ("<code>fastapi_app = FastAPI(...)</code>", "Создаём обычное FastAPI-приложение для HTTP endpoint-ов главы."),
            ("<code>socketio.ASGIApp(...)</code>", "Объединяем Socket.IO server и FastAPI-приложение в одно ASGI-приложение."),
            ("<code>socketio_path=\"socket.io\"</code>", "Указываем путь Socket.IO внутри ASGI-приложения. В браузере этот путь обычно выглядит как <code>/socket.io</code>."),
            ("<code>@sio.event</code>", "Декоратор регистрирует функцию как обработчик события. Имя функции становится именем события."),
            ("<code>async def connect(sid, environ, auth)</code>", "Срабатывает при новом подключении клиента."),
            ("<code>sid</code>", "Уникальный id подключения. Его выдаёт Socket.IO server."),
            ("<code>data</code>", "Payload события. Обычно это обычный словарь с данными от клиента."),
            ("<code>socketio_clients[sid] = \"anonymous\"</code>", "Сохраняем подключение с временным именем, пока пользователь не отправит своё имя."),
            ("<code>async def set_name(...)</code>", "Обрабатываем событие, которое меняет имя пользователя в учебном словаре."),
            ("<code>async def direct_message(...)</code>", "Обрабатываем событие личного сообщения."),
            ("<code>target_sid = data.get(\"sid\")</code>", "Берём id клиента, которому нужно отправить личное сообщение."),
            ("<code>await sio.emit(..., to=target_sid)</code>", "Отправляем событие только выбранному клиенту."),
            ("<code>async def disconnect(sid)</code>", "Срабатывает при отключении клиента и очищает учебное состояние."),
        ],
        "mistakes": [
            "Подключать Socket.IO клиент к raw WebSocket endpoint-у <code>/ws/chat</code>. Socket.IO использует свой протокол и path <code>/socket.io</code>.",
            "Путать имя события и поле внутри JSON. В Socket.IO событие называется отдельно, например <code>chat_message</code>.",
            "Забыть удалить sid из учебных словарей при <code>disconnect</code>.",
        ],
    },
    "chapter11": {
        "plain": [
            "Socket.IO-подключение тоже нужно защищать. Иначе любой клиент сможет отправлять события в чат.",
            "Token передаётся при подключении в объекте <code>auth</code>. Сервер проверяет token прямо в событии <code>connect</code>.",
            "Username берётся из JWT и хранится на сервере по <code>sid</code>, чтобы клиент не мог притвориться другим пользователем.",
        ],
        "line_by_line": [
            ("<code>def authorize_socketio(auth)</code>", "Helper получает auth payload от Socket.IO клиента и возвращает username или <code>None</code>."),
            ("<code>(auth or {}).get(\"access_token\")</code>", "Безопасно читаем token, даже если клиент вообще не передал auth."),
            ("<code>verify_token(str(token))</code>", "Проверяем подпись JWT и достаём username."),
            ("<code>@sio.event</code>", "Регистрируем Socket.IO событие."),
            ("<code>async def connect(sid, environ, auth)</code>", "Socket.IO вызывает эту функцию при попытке подключения."),
            ("<code>if username is None: return False</code>", "Отказываем клиенту в подключении, если token отсутствует или невалиден."),
            ("<code>authorized_clients[sid] = username</code>", "Запоминаем, какой подтверждённый пользователь стоит за этим подключением."),
            ("<code>await sio.emit(\"authorized\", ...)</code>", "Отправляем подтверждение только текущему клиенту."),
        ],
        "mistakes": [
            "Передавать token в query string raw WebSocket URL, хотя в этой главе используется Socket.IO auth payload.",
            "Брать username из события клиента вместо JWT.",
            "Проверять token только на первом HTTP login, но не проверять его при real-time подключении.",
        ],
    },
    "chapter12": {
        "plain": [
            "В финальной главе один и тот же чат работает двумя способами: через REST API и через Socket.IO события.",
            "REST endpoint и Socket.IO handler используют один <code>ChatService</code>, поэтому правила сохранения сообщений находятся в одном месте.",
            "Тесты по-прежнему подменяют БД через dependency override для REST, а Socket.IO часть показывает, как подключить real-time слой к тому же сервису.",
        ],
        "line_by_line": [
            ("<code>@sio.event</code>", "Регистрируем Socket.IO событие. Имя функции становится именем события для клиента."),
            ("<code>async def chat_message(sid, data)</code>", "Сервер обрабатывает событие <code>chat_message</code>, которое прислал Socket.IO клиент."),
            ("<code>sender = data.get(...)</code>", "Берём отправителя из payload или из имени, сохранённого при <code>set_name</code>."),
            ("<code>with SessionLocal() as db</code>", "Открываем короткую Session для работы с SQLite внутри real-time события."),
            ("<code>service = ChatService(db)</code>", "Используем тот же service layer, что и REST endpoint-ы."),
            ("<code>service.send_message(...)</code>", "Сохраняем сообщение в БД и получаем ORM-объект с id и created_at."),
            ("<code>message_to_dict(message)</code>", "Превращаем ORM-объект в простой JSON-friendly словарь."),
            ("<code>await sio.emit(..., room=room)</code>", "Отправляем сохранённое сообщение всем Socket.IO клиентам выбранной комнаты."),
        ],
        "mistakes": [
            "Дублировать сохранение сообщений отдельно для REST и Socket.IO вместо общего <code>ChatService</code>.",
            "Держать одну SQLAlchemy Session глобально для всех Socket.IO событий.",
            "Отправлять в событие ORM-объект напрямую, не превращая его в простой JSON-словарь.",
        ],
    },
}


CHAPTER_STUDY_NOTES = {
    "chapter01": [
        "Эта глава показывает самый маленький полезный FastAPI-сервис целиком: приложение, запуск через Uvicorn, маршруты, входную модель, middleware, ручную бизнес-проверку и JSON-ответ.",
        "REST API - это договор между клиентом и сервером. Клиент говорит: method, path, headers, body. Сервер отвечает: status code, headers, body.",
        "Не пытайтесь сразу запомнить все декораторы. Сначала поймите цепочку: Uvicorn принимает HTTP-запрос, FastAPI выбирает функцию по method и path, Pydantic проверяет JSON, функция возвращает словарь.",
        "После этой главы вы должны уметь прочитать показанный на странице <code>main.py</code> сверху вниз и объяснить, зачем нужна каждая часть: импорты, <code>app</code>, Uvicorn, модель, middleware и endpoint-ы.",
    ],
    "chapter02": [
        "Эта глава нужна, чтобы endpoint-ы не превращались в склад создания объектов. Сервисы готовятся отдельно, а endpoint только просит их через <code>Depends</code>.",
        "Главная сложность для новичка - не синтаксис, а момент вызова. Вы пишете <code>Depends(get_service)</code> без скобок, потому что FastAPI должен вызвать функцию во время HTTP-запроса.",
        "Вторая сложность - время жизни объекта. Один объект может создаваться на каждый запрос, на каждый параметр или жить всё время работы приложения.",
        "Смотрите на id в endpoint-е <code>lifetimes</code>: совпавшие id показывают переиспользование объекта, разные id показывают создание нового объекта.",
        "Singleton DI в этой главе прописан отдельным рецептом: объект создаётся один раз на уровне модуля, provider возвращает этот объект, endpoint получает его через <code>Depends</code>.",
        "Endpoint <code>current-user</code> важен для понимания будущих глав: dependency может читать данные запроса и собирать объект, который endpoint потом использует как готовый контекст.",
    ],
    "chapter03": [
        "Здесь ваше приложение впервые общается с чужим API. Это частая задача: забрать данные из внешнего сервиса, проверить ошибку и вернуть клиенту понятный результат.",
        "Держите в голове два запроса: клиент вызывает ваш FastAPI endpoint, а внутри endpoint-а ваш код вызывает JSONPlaceholder через <code>httpx</code>.",
        "Если внешний сервис недоступен, это не должно превращаться в непонятное падение. Поэтому в этой главе важны timeout, обработка HTTP-ошибок и сервисный слой.",
    ],
    "chapter04": [
        "Эта глава учит делать ошибки частью API-контракта. Клиенту нужен понятный status code и стабильный JSON, а не случайный traceback.",
        "Смотрите на обработчики исключений как на общий переводчик: внутри Python случилось исключение, наружу клиент получает аккуратный HTTP-ответ.",
        "После главы вы должны уметь отличать ошибку валидации, ожидаемую бизнес-ошибку и настоящую серверную ошибку.",
    ],
    "chapter05": [
        "Здесь FastAPI используется не только как JSON API, но и как сервер HTML-страниц. Это мост между backend-логикой и обычной формой в браузере.",
        "Jinja2 не заменяет Python. Python готовит данные, шаблон только показывает их в HTML и аккуратно выводит ошибки рядом с полями.",
        "Новичкам важно увидеть разницу между JSON body и HTML form-data: для формы нужны <code>Form</code> и пакет <code>python-multipart</code>.",
    ],
    "chapter06": [
        "В этой главе данные начинают жить в базе. Endpoint больше не просто считает результат, а создаёт, читает, изменяет и удаляет строки таблицы.",
        "Разделяйте три слоя в голове: ORM-модель описывает таблицу, Pydantic DTO описывает внешний JSON, Session выполняет операции с базой.",
        "Alembic показан как следующий шаг: в демо таблицы создаются автоматически, но в реальных проектах структуру БД меняют миграциями.",
    ],
    "chapter07": [
        "Эта глава отвечает на вопрос: как сервер понимает, кто делает запрос. Логин выдаёт token, защищённый endpoint доверяет только проверенному token-у.",
        "Не путайте authentication и authorization. Сначала пользователь доказывает личность, потом приложение решает, что ему разрешено.",
        "JWT кажется магией только до тех пор, пока вы не увидите payload, secret key, подпись и dependency, которая достаёт пользователя из token-а.",
    ],
    "chapter08": [
        "Access token живёт недолго, refresh token помогает получить новый access token без повторного ввода пароля.",
        "Главная идея главы - rotation: старый refresh token после обновления становится недействительным, а клиент получает новый.",
        "Сервер хранит refresh token в SQLite, поэтому может отозвать его при logout или при подозрительной активности.",
    ],
    "chapter09": [
        "WebSocket отличается от HTTP тем, что соединение остаётся открытым. Это подходит для чата, уведомлений и живых обновлений.",
        "Самое важное в первой WebSocket-главе - manager подключений: сервер должен помнить активные соединения и уметь рассылать сообщения.",
        "Не проверяйте эту главу как обычный REST endpoint. Здесь нужен WebSocket-клиент: браузерный JS, тестовый клиент или отдельный инструмент.",
    ],
    "chapter10": [
        "Здесь используется Socket.IO: отдельная real-time технология с событиями, комнатами и готовой клиентской библиотекой.",
        "Raw WebSocket endpoint в главе оставлен как низкоуровневый пример, а основной учебный сценарий показывает Socket.IO события.",
        "Обратите внимание на договорённость между клиентом и сервером: какие события существуют, какие поля есть в payload и куда сервер делает emit.",
    ],
    "chapter11": [
        "Socket.IO-соединения тоже нужно защищать. Иначе любой клиент сможет подключиться напрямую, минуя обычный login.",
        "Порядок важен: token проверяется в событии <code>connect</code>, до обработки любых пользовательских событий.",
        "Username берётся из JWT, а не из payload события. Это защищает от ситуации, где клиент просто пишет чужое имя.",
    ],
    "chapter12": [
        "Финальная глава собирает REST API, Socket.IO, базу, сервисный слой и тесты в один учебный пример.",
        "Главная мысль: REST и Socket.IO не должны иметь две разные бизнес-логики. Оба слоя вызывают <code>ChatService</code>.",
        "После этой главы вы должны уметь сохранить сообщение через real-time событие и увидеть ту же запись через REST endpoint.",
    ],
}


REQUEST_EXAMPLES = {
    "chapter01": [
        ("Сложение через REST", 'curl -X POST http://localhost:8001/api/calculator/add \\\n  -H "Content-Type: application/json" \\\n  -d \'{"a": 10, "b": 5}\''),
        ("Ошибка деления на ноль", 'curl -X POST http://localhost:8001/api/calculator/divide \\\n  -H "Content-Type: application/json" \\\n  -d \'{"a": 10, "b": 0}\''),
        ("Посмотреть status code и headers", 'curl -i -X POST http://localhost:8001/api/calculator/multiply \\\n  -H "Content-Type: application/json" \\\n  -d \'{"a": 3, "b": 4}\''),
        ("Передать custom request header", 'curl -i http://localhost:8001/api/headers/demo \\\n  -H "User-Agent: FastAPI-Book-Student" \\\n  -H "X-Demo-Client: lesson-01"'),
        ("Показать только response headers", 'curl -s -D - -o /dev/null http://localhost:8001/api/headers/demo \\\n  -H "X-Demo-Client: headers-only"'),
        ("Увидеть ошибку валидации 422", 'curl -i -X POST http://localhost:8001/api/calculator/add \\\n  -H "Content-Type: application/json" \\\n  -d \'{"a": "hello", "b": 5}\''),
    ],
    "chapter02": [
        ("Проверка lifetime-ов", "curl http://localhost:8002/api/dependency-injection/lifetimes"),
        ("Проверка singleton DI", "curl http://localhost:8002/api/dependency-injection/singleton-demo\ncurl http://localhost:8002/api/dependency-injection/singleton-demo"),
        ("Настройки через dependency", "curl http://localhost:8002/api/dependency-injection/settings-demo"),
        ("Query-параметры внутри dependency", "curl 'http://localhost:8002/api/dependency-injection/current-user?username=anna&role=admin'"),
        ("Логирование через dependency", "curl 'http://localhost:8002/api/dependency-injection/logger-demo?message=hello'"),
    ],
    "chapter03": [
        ("Получить внешний post", "curl http://localhost:8003/api/http-client/posts/1"),
        ("Получить комментарии post-а", "curl http://localhost:8003/api/http-client/posts/1/comments"),
    ],
    "chapter04": [
        ("Ожидаемая demo-ошибка", "curl -i http://localhost:8004/api/error-demo/custom"),
        ("Ошибка валидации", 'curl -i "http://localhost:8004/api/error-demo/validation?age=-1"'),
    ],
    "chapter05": [
        ("Отправить форму из terminal", 'curl -X POST http://localhost:8005/contact \\\n  -H "Content-Type: application/x-www-form-urlencoded" \\\n  -d "name=Anna&email=anna@example.com&message=Hello"'),
        ("Проверить HTML-страницу", "open http://localhost:8005/contact"),
    ],
    "chapter06": [
        ("Создать товар", 'curl -X POST http://localhost:8006/api/products \\\n  -H "Content-Type: application/json" \\\n  -d \'{"name":"Keyboard","description":"USB","price":"49.90","stock":10}\''),
        ("Получить список товаров", "curl http://localhost:8006/api/products"),
    ],
    "chapter07": [
        ("Регистрация", 'curl -X POST http://localhost:8007/api/auth/register \\\n  -H "Content-Type: application/json" \\\n  -d \'{"username":"anna","email":"anna@example.com","password":"secret123"}\''),
        ("Вход и token", 'curl -X POST http://localhost:8007/api/auth/login \\\n  -H "Content-Type: application/json" \\\n  -d \'{"username":"anna","password":"secret123"}\''),
    ],
    "chapter08": [
        ("Login с refresh token", 'curl -X POST http://localhost:8008/api/auth/login \\\n  -H "Content-Type: application/json" \\\n  -d \'{"username":"demo","password":"password"}\''),
        ("Обновление пары token-ов", 'curl -X POST http://localhost:8008/api/auth/refresh \\\n  -H "Content-Type: application/json" \\\n  -d \'{"refresh_token":"PASTE_REFRESH_TOKEN"}\''),
    ],
    "chapter09": [
        ("Быстрая проверка в консоли браузера", 'const ws = new WebSocket("ws://localhost:8009/ws");\nws.onmessage = event => console.log(event.data);\nws.onopen = () => ws.send("hello");'),
        ("Что должно произойти", "Откройте две вкладки с кодом выше. Сообщение из одной вкладки должно прийти в обе."),
    ],
    "chapter10": [
        ("Подключить Socket.IO клиент", 'const script = document.createElement("script");\nscript.src = "https://cdn.socket.io/4.7.5/socket.io.min.js";\nscript.onload = () => {\n  const socket = io("http://localhost:8010", { path: "/socket.io" });\n  socket.on("connected", data => console.log("connected", data));\n  socket.on("chat_message", data => console.log("message", data));\n  window.socket = socket;\n};\ndocument.head.append(script);'),
        ("Вступить в комнату и отправить сообщение", 'socket.emit("set_name", { username: "anna" });\nsocket.emit("join_room", { room: "python" });\nsocket.emit("chat_message", { room: "python", message: "Привет комнате" });'),
    ],
    "chapter11": [
        ("Получить access token", 'curl -X POST http://localhost:8011/api/auth/login \\\n  -H "Content-Type: application/json" \\\n  -d \'{"username":"demo","password":"password"}\''),
        ("Подключиться через Socket.IO с token-ом", 'const script = document.createElement("script");\nscript.src = "https://cdn.socket.io/4.7.5/socket.io.min.js";\nscript.onload = () => {\n  const token = "PASTE_ACCESS_TOKEN";\n  const socket = io("http://localhost:8011", {\n    path: "/socket.io",\n    auth: { access_token: token }\n  });\n  socket.on("authorized", data => console.log("authorized", data));\n  socket.on("authorized_message", data => console.log("message", data));\n  window.socket = socket;\n};\ndocument.head.append(script);'),
        ("Отправить авторизованное сообщение", 'socket.emit("authorized_message", { message: "Привет из защищённого Socket.IO" });'),
    ],
    "chapter12": [
        ("Создать группу", 'curl -X POST http://localhost:8012/api/chat/groups \\\n  -H "Content-Type: application/json" \\\n  -d \'{"name":"general"}\''),
        ("Отправить сообщение", 'curl -X POST http://localhost:8012/api/chat/messages \\\n  -H "Content-Type: application/json" \\\n  -d \'{"text":"hello","sender":"anna","group_id":1}\''),
        ("Отправить сообщение через Socket.IO", 'const socket = io("http://localhost:8012", { path: "/socket.io" });\nsocket.on("chat_message", data => console.log(data));\nsocket.emit("set_name", { username: "anna" });\nsocket.emit("join_group", { group_id: 1 });\nsocket.emit("chat_message", { text: "hello realtime", group_id: 1 });'),
    ],
}


CONTROL_QUESTIONS = {
    "chapter01": [
        "Что именно делает Uvicorn, если <code>app = FastAPI()</code> уже создан?",
        "Из каких основных частей состоит HTTP request?",
        "Из каких основных частей состоит HTTP response?",
        "Чем request headers отличаются от response headers?",
        "Зачем нужен header <code>Content-Type: application/json</code>?",
        "Где в ответе искать <code>X-FastAPI-Book-Chapter</code>: в JSON body или в response headers?",
        "Какая строка связывает URL <code>/api/calculator/divide</code> с Python-функцией?",
        "Почему при неправильном JSON FastAPI не заходит внутрь endpoint-а?",
        "Чем status code <code>400</code> отличается от <code>422</code> в этой главе?",
        "Чем <code>HTTPException(status_code=400)</code> лучше обычного падения Python?",
        "Где в браузере можно увидеть автоматически созданную схему запроса?",
    ],
    "chapter02": [
        "Что делает <code>Depends</code> и почему dependency передаётся без скобок?",
        "Что изменится, если случайно написать <code>Depends(get_service())</code>?",
        "В какой момент FastAPI вызывает dependency-функции: при запуске приложения или при HTTP-запросе?",
        "Какие три шага нужны, чтобы прописать singleton DI в этой главе?",
        "Почему singleton-объект создаётся вне функции <code>get_singleton_di_service</code>?",
        "Почему два request-scoped параметра могут получить один и тот же объект?",
        "Что делает <code>use_cache=False</code>?",
        "Когда опасно хранить состояние в singleton-style сервисе?",
        "Как по JSON-ответу понять, что transient dependency создалась заново?",
        "Как dependency <code>get_current_user</code> получает <code>username</code> и <code>role</code>?",
        "Почему dependency удобно подменять в тестах?",
    ],
    "chapter03": [
        "Как отличить входящий запрос к вашему API от исходящего запроса через <code>httpx</code>?",
        "Зачем нужен timeout при вызове внешнего сервиса?",
        "Что делает <code>raise_for_status()</code>?",
        "Почему внешний API лучше спрятать в отдельный service class?",
    ],
    "chapter04": [
        "Чем validation error отличается от вашей custom error?",
        "Почему клиенту важно получать стабильную JSON-форму ошибки?",
        "Где лучше логировать путь запроса и время выполнения?",
        "Когда стоит вернуть 400, 404, 422 и 500?",
    ],
    "chapter05": [
        "Почему для HTML-формы используется <code>Form</code>, а не Pydantic-модель тела JSON напрямую?",
        "Зачем шаблону нужен объект <code>request</code>?",
        "Как сохранить введённые значения после ошибки валидации?",
        "Почему endpoint формы можно скрыть из OpenAPI через <code>include_in_schema=False</code>?",
    ],
    "chapter06": [
        "Какая разница между ORM-моделью <code>Product</code> и DTO <code>ProductDto</code>?",
        "Почему Session открывается и закрывается через dependency?",
        "Что произойдёт, если забыть <code>db.commit()</code>?",
        "Зачем нужен Alembic, если демо создаёт таблицы автоматически?",
    ],
    "chapter07": [
        "Что означает поле <code>sub</code> внутри JWT payload?",
        "Почему пароль хранится как hash, а не обычная строка?",
        "Что делает dependency <code>get_current_user</code>?",
        "Чем 401 отличается от 403 в задачах безопасности?",
    ],
    "chapter08": [
        "Почему access token делают короткоживущим?",
        "Зачем хранить refresh token на сервере?",
        "Что такое rotation refresh token-а?",
        "Почему logout должен отзывать refresh token?",
    ],
    "chapter09": [
        "Почему WebSocket endpoint начинается с <code>@app.websocket</code>, а не с <code>@app.get</code>?",
        "Зачем manager хранит список активных соединений?",
        "Что делает <code>WebSocketDisconnect</code>?",
        "Почему broadcast должен быть асинхронным?",
    ],
    "chapter10": [
        "Чем Socket.IO событие отличается от обычного JSON-поля <code>action</code>?",
        "Что такое <code>sid</code> и почему его удобно использовать для прямой отправки?",
        "Зачем нужны комнаты Socket.IO?",
        "Чем <code>emit(..., room=room)</code> отличается от <code>emit(..., to=sid)</code>?",
    ],
    "chapter11": [
        "Почему token нужно проверять в Socket.IO событии <code>connect</code>?",
        "Почему username нельзя брать из payload события клиента?",
        "Что означает <code>return False</code> внутри Socket.IO connect handler?",
        "Как HTTP login связан с Socket.IO-подключением?",
    ],
    "chapter12": [
        "Почему REST API и Socket.IO handler должны использовать один <code>ChatService</code>?",
        "Где в Socket.IO событии открывается SQLAlchemy Session?",
        "Как сообщение, отправленное через Socket.IO, потом увидеть через REST endpoint?",
        "Почему тестовая БД должна быть отдельной от demo-БД?",
    ],
}


PRACTICE_LEVELS = {
    "chapter01": [
        ("Лёгкий уровень", "Добавьте endpoint <code>/api/calculator/modulo</code> и проверьте остаток от деления."),
        ("Средний уровень", "Сделайте проверку деления на ноль общей для <code>divide</code> и <code>modulo</code>."),
        ("Сложный уровень", "Добавьте историю последних операций в памяти приложения и endpoint для её просмотра."),
    ],
    "chapter02": [
        ("Лёгкий уровень", "Добавьте dependency, которая возвращает текущий timestamp запроса."),
        ("Средний уровень", "Добавьте сервис счётчика запросов и покажите разницу между scoped и singleton поведением."),
        ("Сложный уровень", "Сделайте dependency, которая читает request header и передаёт correlation id в логирующий сервис."),
    ],
    "chapter03": [
        ("Лёгкий уровень", "Добавьте endpoint для получения пользователя JSONPlaceholder по id."),
        ("Средний уровень", "Соберите post и комментарии в один общий JSON-ответ."),
        ("Сложный уровень", "Обработайте недоступность внешнего API и верните понятный ответ 503."),
    ],
    "chapter04": [
        ("Лёгкий уровень", "Добавьте новый custom exception для ситуации <code>Item not found</code>."),
        ("Средний уровень", "Сделайте единый формат ошибки с полями <code>error</code>, <code>path</code>, <code>status_code</code>."),
        ("Сложный уровень", "Добавьте request id в middleware и возвращайте его в каждом ошибочном ответе."),
    ],
    "chapter05": [
        ("Лёгкий уровень", "Добавьте поле <code>subject</code> в форму и отобразите его после отправки."),
        ("Средний уровень", "Покажите ошибки валидации рядом с каждым полем, не очищая форму."),
        ("Сложный уровень", "Добавьте список отправленных сообщений в памяти и страницу просмотра."),
    ],
    "chapter06": [
        ("Лёгкий уровень", "Добавьте поле <code>category</code> в DTO и ORM-модель."),
        ("Средний уровень", "Добавьте фильтрацию товаров по минимальной цене и наличию на складе."),
        ("Сложный уровень", "Создайте новую Alembic migration для добавленного поля и опишите команды запуска."),
    ],
    "chapter07": [
        ("Лёгкий уровень", "Добавьте endpoint <code>/api/protected/profile</code>, который возвращает текущего пользователя."),
        ("Средний уровень", "Добавьте роль <code>admin</code> и protected endpoint только для admin."),
        ("Сложный уровень", "Сделайте смену пароля с проверкой старого пароля и перевыпуском token-а."),
    ],
    "chapter08": [
        ("Лёгкий уровень", "Добавьте endpoint проверки активных refresh token-ов пользователя."),
        ("Средний уровень", "Сделайте logout со всеми refresh token-ами текущего пользователя."),
        ("Сложный уровень", "Добавьте хранение user agent или device name для каждого refresh token-а."),
    ],
    "chapter09": [
        ("Лёгкий уровень", "Добавьте системное сообщение при подключении нового клиента."),
        ("Средний уровень", "Добавьте имя пользователя в query string и включайте его в broadcast."),
        ("Сложный уровень", "Добавьте ограничение длины сообщения и отправку ошибки только отправителю."),
    ],
    "chapter10": [
        ("Лёгкий уровень", "Добавьте событие <code>leave_room</code> для выхода из комнаты."),
        ("Средний уровень", "Добавьте событие <code>my_rooms</code>, которое возвращает комнаты текущего <code>sid</code>."),
        ("Сложный уровень", "Сделайте <code>direct_message</code> по username, а не по техническому <code>sid</code>."),
    ],
    "chapter11": [
        ("Лёгкий уровень", "Добавьте событие <code>whoami</code>, которое возвращает username текущего <code>sid</code>."),
        ("Средний уровень", "Запретите отправку пустых сообщений через событие <code>authorized_message</code>."),
        ("Сложный уровень", "Добавьте роли в JWT и событие <code>admin_message</code> только для admin."),
    ],
    "chapter12": [
        ("Лёгкий уровень", "Добавьте событие <code>typing</code>, которое отправляет в комнату имя печатающего пользователя."),
        ("Средний уровень", "Добавьте событие <code>delete_group</code> и покройте удаление тестом service layer."),
        ("Сложный уровень", "Проверьте сценарий: Socket.IO сохраняет сообщение, REST API возвращает это сообщение из БД."),
    ],
}


TEST_FILES = {
    "chapter01": "tests/test_chapter01_calculator.py",
    "chapter02": "tests/test_chapter02_di.py",
    "chapter04": "tests/test_chapter04_errors.py",
    "chapter06": "tests/test_chapter06_products.py",
    "chapter07": "tests/test_chapter07_auth.py",
    "chapter08": "tests/test_chapter08_refresh.py",
    "chapter09": "tests/test_chapter09_websocket.py",
    "chapter11": "tests/test_chapter11_authorized_socketio.py",
    "chapter12": "tests/test_chapter12_chat.py",
}


def lesson_plan(service: str, data: dict) -> list[str]:
    if service == "chapter01":
        return [
            "На вкладке <strong>Разбор кода</strong> прочитайте полный учебный <code>main.py</code> сверху вниз: от импортов до запуска Uvicorn.",
            "На вкладке <strong>Теория</strong> сопоставьте REST-термины с реальным запросом: method, path, headers, body, status code и response body.",
            "Откройте Swagger UI и выполните все endpoint-ы из блока проверки. У каждого запроса поменяйте входные данные минимум два раза.",
            "Выполните curl-примеры с <code>-i</code>, чтобы увидеть не только JSON, но и HTTP status code с headers.",
            "Вернитесь на вкладку <strong>Практика</strong>, выполните лёгкое задание, затем среднее. Сложное задание можно оставить как самостоятельную мини-работу.",
            f"Запустите тесты этой темы: <code>{TEST_FILES.get(service, 'pytest')}</code>.",
        ]
    return [
        "Откройте главный файл приложения и найдите код из вкладки <strong>Разбор кода</strong>. Не переписывайте его вслепую: сопоставьте каждую строку с объяснением.",
        "Откройте Swagger UI и выполните все endpoint-ы из блока проверки. У каждого запроса поменяйте входные данные минимум два раза.",
        "Вернитесь на вкладку <strong>Практика</strong>, выполните лёгкое задание, затем среднее. Сложное задание можно оставить как самостоятельную мини-работу.",
        f"Запустите тесты, связанные с главой: <code>{TEST_FILES.get(service, 'pytest')}</code>. Если теста нет для конкретной главы, запустите общий <code>pytest</code>.",
    ]


def chapter_files(service: str, data: dict) -> list[tuple[str, str]]:
    files = [
        (f"{service}/app/main.py", "Главный учебный файл главы: FastAPI app, routes, модели, зависимости и сервисы."),
        (f"{service}/templates/index.html", "HTML-страница урока с теорией, разбором, практикой и ответами."),
        (f"{service}/static/site.css", "Общие стили страницы урока."),
        (f"{service}/static/site.js", "Переключение вкладок на странице урока."),
        (f"{service}/Dockerfile", "Инструкция сборки контейнера для этой главы."),
    ]
    if service == "chapter05":
        files.insert(2, ("chapter05/templates/contact.html", "Отдельная HTML-форма, которая показывает binding и ошибки валидации."))
    if service == "chapter06":
        files.extend([
            ("chapter06/alembic.ini", "Настройки Alembic для миграций базы данных."),
            ("chapter06/alembic/env.py", "Код, который подключает Alembic к SQLAlchemy metadata."),
            ("chapter06/alembic/versions/0001_create_products.py", "Пример первой миграции таблицы products."),
        ])
    test_file = TEST_FILES.get(service)
    if test_file:
        files.append((test_file, "Автоматические проверки поведения главы. Их полезно читать как примеры использования API."))
    files.append(("requirements.txt", "Один общий набор Python-зависимостей для всего учебника."))
    return files


def run_commands(service: str, data: dict) -> list[tuple[str, str]]:
    commands = [
        ("Создать окружение и поставить зависимости", "python3 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt"),
        ("Запустить только эту главу", f"uvicorn {service}.app.main:app --reload --port {data['port']}"),
        ("Открыть страницу и Swagger", f"open http://localhost:{data['port']}\nopen http://localhost:{data['port']}/docs"),
        ("Запустить все проверки проекта", "./scripts/validate.sh"),
    ]
    if service == "chapter01":
        commands.insert(2, (
            "Что означает команда Uvicorn",
            "uvicorn chapter01.app.main:app --reload --port 8001\n\n"
            "# uvicorn                 - запускает ASGI-сервер\n"
            "# chapter01.app.main      - Python-модуль, где лежит приложение\n"
            "# :app                    - переменная FastAPI() внутри этого модуля\n"
            "# --reload                - перезапуск при изменении файлов\n"
            "# --port 8001             - порт, на котором будет доступен сайт",
        ))
        commands.insert(3, (
            "Запустить эту же главу как Python-файл",
            "python chapter01/app/main.py",
        ))
    test_file = TEST_FILES.get(service)
    if test_file:
        insert_at = 5 if service == "chapter01" else 3
        commands.insert(insert_at, ("Запустить тесты этой темы", f"pytest {test_file}"))
    if service == "chapter06":
        commands.append(("Пример Alembic-команды", "cd chapter06\nalembic upgrade head"))
    if service.startswith("chapter0") or service in {"chapter10", "chapter11", "chapter12"}:
        commands.append(("Запустить все главы через Docker Compose", "docker compose up --build"))
    return commands


def browser_targets(data: dict) -> list[tuple[str, str]]:
    port = data["port"]
    targets = [
        (f"http://localhost:{port}", "Страница урока: теория, разбор кода, практика и ответы."),
        (f"http://localhost:{port}/docs", "Swagger UI: интерактивная документация, где удобно нажимать Try it out."),
        (f"http://localhost:{port}/redoc", "ReDoc: статичная документация для спокойного чтения схемы API."),
        ("http://localhost:8000", "Gateway: общая главная страница со всеми главами."),
    ]
    if data["number"] == 10:
        targets.insert(1, ("http://localhost:8010/socket-tester", "Тестер Socket.IO и raw WebSocket: можно ввести URL своего сервиса и отправить сообщение."))
    return targets


def render_lesson(service: str, data: dict) -> str:
    number = data["number"]
    port = data["port"]
    guide = BEGINNER_GUIDES[service]
    study_notes = CHAPTER_STUDY_NOTES[service]
    prev_link = f'http://localhost:{port - 1}' if number > 1 else "http://localhost:8000"
    next_link = f'http://localhost:{port + 1}' if number < 12 else "http://localhost:8000"
    prev_label = "Предыдущая глава" if number > 1 else "Главная"
    next_label = "Следующая глава" if number < 12 else "Главная"

    return f"""<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{data["title"]}</title>
    <link rel="stylesheet" href="/static/site.css">
</head>
<body>
    <main class="chapter-shell">
        <nav class="top-nav" aria-label="Навигация урока">
            <a class="nav-link light" href="http://localhost:8000">← На главную</a>
            <div class="top-nav__links">
                <a class="nav-link light" href="{prev_link}">{prev_label}</a>
                <a class="nav-link secondary" href="/docs">Swagger</a>
                <a class="nav-link light" href="/redoc">ReDoc</a>
                <a class="nav-link light" href="{next_link}">{next_label}</a>
            </div>
        </nav>

        <section class="hero">
            <h1>{data["title"]}</h1>
            <p>{data["subtitle"]}</p>
            <div class="lesson-meta">
                <span><strong>Порт:</strong> {port}</span>
                <span><strong>Swagger:</strong> <code>http://localhost:{port}/docs</code></span>
                <span><strong>Результат:</strong> {data["outcome"]}</span>
            </div>
        </section>

        <nav class="lesson-tabs" aria-label="Разделы главы">
            <button class="active" data-tab-target="#course">Учебник</button>
            <button data-tab-target="#theory">Теория</button>
            <button data-tab-target="#code">Разбор кода</button>
            <button data-tab-target="#task">Практика</button>
            <button data-tab-target="#answers">Ответы</button>
        </nav>

        <section id="course" class="tab-panel active">
            <div class="section-grid">
                <article class="info-box">
                    <h2>Как пользоваться этой главой</h2>
                    {paragraphs(study_notes)}
                    <div class="callout">Если вы только начинаете: не перепрыгивайте сразу к ответу. Сначала запустите пример, затем откройте код рядом с этой страницей и проговаривайте каждую строку обычными словами.</div>
                </article>

                <article class="info-box">
                    <h2>Учебный план</h2>
                    <ol class="flow-list">
                        {list_items(lesson_plan(service, data))}
                    </ol>
                </article>

                <article class="info-box">
                    <h2>Структура файлов главы</h2>
                    <dl class="line-breakdown">
                        {render_file_structure(chapter_files(service, data))}
                    </dl>
                </article>

                <article class="info-box">
                    <h2>Команды запуска</h2>
                    <p>Эти команды выполняются из корня проекта <code>FastAPI_Book</code>. Если виртуальное окружение уже создано, повторно создавать его не нужно.</p>
                </article>

                <div class="section-grid">
                    {titled_code_blocks(run_commands(service, data))}
                </div>

                <article class="info-box">
                    <h2>Что открыть в браузере</h2>
                    <div class="endpoint-grid">
                        {endpoint_cards(browser_targets(data))}
                    </div>
                </article>
            </div>
        </section>

        <section id="theory" class="tab-panel">
            <div class="section-grid">
                <article class="info-box">
                    <h2>Что разбираем в этой главе</h2>
                    <ul class="flow-list">
                        {list_items(data["concepts"])}
                    </ul>
                </article>

                {render_extra_sections(data.get("theory_blocks", []))}

                <article class="info-box">
                    <h2>Как проходит запрос</h2>
                    <ol class="flow-list">
                        {list_items(data["flow"])}
                    </ol>
                </article>

                <article class="info-box">
                    <h2>Endpoint-ы для проверки</h2>
                    <div class="endpoint-grid">
                        {endpoint_cards(data["endpoints"])}
                    </div>
                </article>

                <article class="info-box">
                    <h2>Примеры запросов</h2>
                    <p>Сначала выполните эти примеры как есть, затем поменяйте входные значения и посмотрите, где именно код меняет ответ.</p>
                </article>

                <div class="section-grid">
                    {titled_code_blocks(REQUEST_EXAMPLES[service])}
                </div>
            </div>
        </section>

        <section id="code" class="tab-panel">
            <div class="section-grid">
                <article class="info-box">
                    <h2>{data.get("code_title", "Ключевой фрагмент")}</h2>
                    {code_block(data["code"])}
                </article>

                <article class="info-box">
                    <h2>Если совсем по-простому</h2>
                    {paragraphs(guide["plain"])}
                </article>

                <article class="info-box">
                    <h2>Построчный разбор</h2>
                    <dl class="line-breakdown">
                        {definition_items(guide["line_by_line"])}
                    </dl>
                </article>

                <article class="info-box">
                    <h2>Что здесь важно</h2>
                    <ul class="flow-list">
                        {list_items(data["code_notes"])}
                    </ul>
                </article>

                <article class="info-box">
                    <h2>Типичные ошибки новичков</h2>
                    <ul class="flow-list">
                        {list_items(guide["mistakes"])}
                    </ul>
                </article>

                <article class="info-box">
                    <h2>Как проверить руками</h2>
                    <p>Откройте <a href="/docs">Swagger UI</a>, найдите endpoint-ы этой главы, нажмите <strong>Try it out</strong> и выполните запросы с разными входными данными. После этого вернитесь в код и сопоставьте каждый ответ с тем участком, который его формирует.</p>
                </article>
            </div>
        </section>

        <section id="task" class="tab-panel">
            <div class="section-grid">
                {render_single_task(service, data)}

                <article class="info-box">
                    <h2>Контрольные вопросы</h2>
                    <ol class="flow-list">
                        {list_items(CONTROL_QUESTIONS[service])}
                    </ol>
                </article>
            </div>
        </section>

        <section id="answers" class="tab-panel">
            <div class="section-grid">
                <article class="info-box">
                    <h2>Полное решение задачи</h2>
                    <p>Это ответ именно к задаче из вкладки “Практика”. Здесь показано, что менять, какой код вставлять, где он должен находиться и как проверить результат. Это не только одна функция, а весь минимальный контекст, чтобы новичок не гадал, куда вставлять кусок кода.</p>
                </article>

                {render_solution_sections(FULL_SOLUTIONS[service])}

                <article class="info-box">
                    <h2>Разбор решения</h2>
                    <ul class="flow-list">
                        {list_items(data["answer_notes"])}
                    </ul>
                </article>
            </div>
        </section>
    </main>
    <script src="/static/site.js"></script>
</body>
</html>
"""


CONTACT_TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Форма контакта</title>
    <link rel="stylesheet" href="/static/site.css">
</head>
<body>
    <main class="chapter-shell">
        <nav class="top-nav" aria-label="Навигация урока">
            <a class="nav-link light" href="http://localhost:8000">← На главную</a>
            <div class="top-nav__links">
                <a class="nav-link light" href="/">К уроку</a>
                <a class="nav-link secondary" href="/docs">Swagger</a>
            </div>
        </nav>

        <section class="hero">
            <h1>Форма контакта</h1>
            <p>Пример binding HTML-формы на сервере, сохранения введённых значений и вывода ошибок рядом с полями.</p>
        </section>

        {% if sent %}
        <section class="info-box success">
            <h2>Форма принята</h2>
            <p>Сообщение от {{ values.name }} принято: {{ values.message }}</p>
        </section>
        {% endif %}

        <section class="info-box">
            <h2>Данные формы</h2>
            <p>Отправьте пустые поля или email без символа @, чтобы увидеть серверную валидацию Pydantic.</p>
            <form method="post" action="/contact">
                <label>Имя
                    <input name="name" value="{{ values.get('name', '') }}">
                    {% if errors.get('name') %}<span class="error">{{ errors.get('name') }}</span>{% endif %}
                </label>
                <label>Email
                    <input name="email" value="{{ values.get('email', '') }}">
                    {% if errors.get('email') %}<span class="error">{{ errors.get('email') }}</span>{% endif %}
                </label>
                <label>Сообщение
                    <textarea name="message">{{ values.get('message', '') }}</textarea>
                    {% if errors.get('message') %}<span class="error">{{ errors.get('message') }}</span>{% endif %}
                </label>
                <button type="submit">Отправить</button>
            </form>
        </section>
    </main>
</body>
</html>
"""


def main() -> None:
    for service, data in LESSONS.items():
        (ROOT / service / "templates" / "index.html").write_text(render_lesson(service, data), encoding="utf-8")

    (ROOT / "chapter05" / "templates" / "contact.html").write_text(CONTACT_TEMPLATE, encoding="utf-8")


if __name__ == "__main__":
    main()
