from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def protect_jinja(value: object) -> str:
    return str(value).replace("{", "&#123;").replace("}", "&#125;")


def paragraphs(items: list[str]) -> str:
    return "\n".join(f"<p>{protect_jinja(item)}</p>" for item in items)


def list_items(items: list[str]) -> str:
    return "\n".join(f"<li>{protect_jinja(item)}</li>" for item in items)


def endpoint_cards(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f'<article class="endpoint-card"><strong><code>{protect_jinja(escape(method))}</code></strong><span>{protect_jinja(description)}</span></article>'
        for method, description in items
    )


def code_block(code: str) -> str:
    return f"<pre><code>{{% raw %}}{escape(code.strip())}{{% endraw %}}</code></pre>"


def definition_items(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f"<dt>{protect_jinja(term)}</dt><dd>{protect_jinja(description)}</dd>"
        for term, description in items
    )


def render_solution_sections(sections: list[dict[str, object]]) -> str:
    rendered = []
    for index, section in enumerate(sections, start=1):
        body = section.get("body", "")
        code = section.get("code")
        items = section.get("items")
        checks = section.get("checks")
        block = [f'<article class="info-box"><h2>{index}. {protect_jinja(section["title"])}</h2>']
        if body:
            block.append(f"<p>{protect_jinja(body)}</p>")
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
        block = [f'<article class="info-box"><h2>{protect_jinja(section["title"])}</h2>']
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
                    <div class="callout">{protect_jinja(data["task"])}</div>
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
        f'<article class="info-box command-box"><h2>{protect_jinja(title)}</h2>{code_block(code)}</article>'
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

from fastapi import Depends, FastAPI, Query


app = FastAPI(
    title="Глава 2: Dependency Injection",
    description="Depends and lifetimes",
    version="1.0.0",
)
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
import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel


JSONPLACEHOLDER = "https://jsonplaceholder.typicode.com"


app = FastAPI(
    title="Глава 3: HTTP Requests",
    description="httpx AsyncClient",
    version="1.0.0",
)


class CreatePostRequest(BaseModel):
    title: str
    body: str
    user_id: int


class ExternalApiService:
    def __init__(self, base_url: str = JSONPLACEHOLDER):
        self.base_url = base_url

    async def get_post(self, post_id: int) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}")
            response.raise_for_status()
            return response.json()

    async def create_post(self, request: CreatePostRequest) -> dict:
        payload = {"title": request.title, "body": request.body, "userId": request.user_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.post("/posts", json=payload)
            response.raise_for_status()
            return response.json()


def get_external_api_service() -> ExternalApiService:
    return ExternalApiService()


def map_http_error(error: httpx.HTTPError) -> HTTPException:
    status_code = 502
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
    return HTTPException(status_code=status_code, detail=str(error))


@app.get("/api/http-client/post/{post_id}")
async def get_post(post_id: int, service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.get_post(post_id)
    except httpx.HTTPError as error:
        raise map_http_error(error) from error
        ''',
        "code_notes": [
            "Клиент создаётся внутри <code>async with</code>, поэтому соединения корректно закрываются.",
            "В больших приложениях клиент можно держать дольше через lifespan, но для учебного примера локальный context manager проще.",
            "Endpoint не знает URL внешнего API: это ответственность сервиса.",
        ],
        "task": "Потренируйтесь на реальном открытом тестовом API, а не на локальной заглушке. Используйте JSONPlaceholder: <code>https://jsonplaceholder.typicode.com/posts/1/comments</code>. Добавьте в свой сервис метод, который ходит во внешний endpoint <code>/posts/{post_id}/comments</code>, и откройте его через ваш FastAPI endpoint <code>GET /api/http-client/post/{post_id}/comments</code>.",
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
import time

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(
    title="Глава 4: Error Handling",
    description="Exception handlers and middleware",
    version="1.0.0",
)


class DemoError(Exception):
    pass


class ValidationRequest(BaseModel):
    name: str = ""
    age: int = 0


@app.middleware("http")
async def request_logging_middleware(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started:.6f}"
    return response


@app.exception_handler(DemoError)
async def demo_error_handler(request, exc: DemoError):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url.path)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Validation failed", "details": exc.errors()})


@app.get("/api/error-demo/badrequest")
async def bad_request_demo():
    raise HTTPException(status_code=400, detail="Это пример BadRequest ответа")
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
        "title": "Глава 5: Jinja2 basics",
        "subtitle": "Минимальные серверные шаблоны: переменные, условие if, цикл for и передача данных из FastAPI в HTML.",
        "outcome": "После главы вы понимаете, как Python готовит данные, а Jinja2 показывает их через {{ }}, {% if %} и {% for %}.",
        "concepts": [
            "<strong>Jinja2Templates</strong> - подключение папки HTML-шаблонов.",
            "<strong>TemplateResponse</strong> - ответ, который рендерит шаблон на сервере.",
            "<strong>context</strong> - обычный Python-словарь с данными для шаблона.",
            "<strong>{{ variable }}</strong> - вставка значения переменной в HTML.",
            "<strong>{% if condition %}</strong> - показать кусок HTML только при выполнении условия.",
            "<strong>{% for item in items %}</strong> - повторить кусок HTML для каждого элемента списка.",
        ],
        "flow": [
            "Пользователь открывает <code>/jinja-demo</code>.",
            "Endpoint собирает простой словарь: заголовок, имя ученика, список тем и флаг подсказки.",
            "FastAPI вызывает <code>templates.TemplateResponse(...)</code>.",
            "Jinja2 открывает файл <code>jinja_demo.html</code> и подставляет значения из словаря.",
            "<code>{{ title }}</code> печатает одну строку.",
            "<code>{% if show_hint %}</code> решает, показывать ли блок подсказки.",
            "<code>{% for topic in topics %}</code> создаёт один пункт списка для каждой темы.",
            "Браузер получает уже готовый HTML. В браузере Python-код не выполняется.",
        ],
        "endpoints": [
            ("GET /", "Страница урока."),
            ("GET /jinja-demo", "Минимальная HTML-страница с переменными, if и for."),
            ("GET /api/template-data", "Те же данные в JSON, чтобы сравнить Python-словарь и HTML-вывод."),
        ],
        "code": '''
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Глава 5: Jinja2 basics",
    description="Templates and context",
    version="1.0.0",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


LESSON_TOPICS = [
    {"name": "Переменная", "template": "{{ title }}"},
    {"name": "Условие if", "template": "{% if show_hint %}"},
    {"name": "Цикл for", "template": "{% for topic in topics %}"},
]


@app.get("/jinja-demo", response_class=HTMLResponse, include_in_schema=False)
async def jinja_demo(request: Request):
    return templates.TemplateResponse(
        request,
        "jinja_demo.html",
        {
            "title": "Jinja2 demo",
            "student_name": "Анна",
            "topics": LESSON_TOPICS,
            "show_hint": True,
        },
    )
        ''',
        "code_notes": [
            "Python здесь отвечает за данные: он создаёт строки, список и флаг <code>show_hint</code>.",
            "Jinja2 отвечает за отображение: где напечатать строку, где повторить блок, где спрятать блок.",
            "HTML в этой главе специально простой. Главная тема - связь endpoint-а и шаблона.",
        ],
        "task": "Добавьте в demo список <code>homework_steps</code> из трёх строк и выведите его в <code>jinja_demo.html</code> через цикл <code>{% for step in homework_steps %}</code>. Никаких форм, паролей и валидации: только передать список из Python в Jinja2 и показать его на странице.",
        "answer": '''
"homework_steps": [
    "Открыть страницу /jinja-demo",
    "Найти блок со списком",
    "Понять, откуда пришёл каждый пункт",
]
        ''',
        "answer_notes": [
            "Список добавляется в context рядом с <code>topics</code>.",
            "В шаблоне нужен обычный Jinja-цикл: открыть <code>{% for %}</code>, вывести <code>{{ step }}</code>, закрыть <code>{% endfor %}</code>.",
        ],
    },
    "chapter06": {
        "number": 6,
        "port": 8006,
        "title": "Глава 6: SQLModel, SQLite и CRUD",
        "subtitle": "SQLModel-модели, Field, Session, select, CRUD endpoint-ы и минимальная Alembic-миграция.",
        "outcome": "После главы вы умеете связать FastAPI с SQLite через SQLModel и понимаете, как одна модель может описывать и таблицу, и JSON-схему.",
        "concepts": [
            "<strong>SQLModel</strong> - библиотека поверх Pydantic и SQLAlchemy: один стиль моделей для API и таблиц.",
            "<strong>table=True</strong> - признак, что класс должен стать таблицей в базе данных.",
            "<strong>Field</strong> - описание поля: валидация для API и настройки колонки для базы.",
            "<strong>Session</strong> - рабочая область для операций с БД: читать, добавить, commit, refresh, удалить.",
            "<strong>select</strong> - SQLModel-способ собрать запрос к таблице.",
            "<strong>Column(JSON)</strong> - когда поле нужно хранить в базе как JSON-структуру.",
            "<strong>Relationship</strong> - связь между таблицами, например продукт и отзывы.",
            "<strong>Alembic</strong> - инструмент миграций схемы БД.",
        ],
        "theory_blocks": [
            {
                "title": "Alembic команды пошагово",
                "body": [
                    "Миграция - это Python-файл с инструкциями для изменения структуры базы данных. Например: добавить колонку, удалить колонку, создать таблицу.",
                    "Команды Alembic запускаются из папки главы <code>chapter06</code>, потому что там лежит <code>alembic.ini</code>.",
                    "<code>alembic revision</code> создаёт новый файл миграции. <code>alembic upgrade head</code> применяет миграции к базе. <code>alembic downgrade -1</code> откатывает последнюю миграцию назад.",
                ],
                "code": '''
cd chapter06

# Посмотреть, на какой миграции сейчас находится база
alembic current

# Создать пустой файл миграции, куда вы вручную вставите upgrade/downgrade
alembic revision -m "add product category"

# Применить все новые миграции до последней версии
alembic upgrade head

# Посмотреть историю миграций
alembic history

# Откатить последнюю миграцию назад
alembic downgrade -1
                ''',
            },
        ],
        "flow": [
            "При старте приложения создаётся SQLModel engine для SQLite.",
            "Класс <code>Product(SQLModel, table=True)</code> описывает таблицу <code>products</code>.",
            "Классы <code>ProductCreate</code>, <code>ProductUpdate</code> и <code>ProductRead</code> описывают внешний JSON API.",
            "Dependency <code>get_db</code> открывает SQLModel <code>Session</code> на время запроса.",
            "Endpoint получает Session через <code>Depends</code>.",
            "Для чтения списка используется <code>db.exec(select(Product))</code>.",
            "После <code>db.commit()</code> SQLModel через SQLAlchemy записывает изменения в SQLite.",
            "Когда меняется структура таблицы, команда <code>alembic upgrade head</code> применяет миграцию к файлу базы данных.",
        ],
        "endpoints": [
            ("GET /api/products", "Список продуктов."),
            ("GET /api/products/{product_id}", "Один продукт или 404."),
            ("POST /api/products", "Создание продукта с SQLModel-валидацией."),
            ("PUT /api/products/{product_id}", "Частичное обновление полей."),
            ("DELETE /api/products/{product_id}", "Удаление продукта."),
        ],
        "code": '''
import os
from datetime import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, status
from sqlalchemy.pool import StaticPool
from sqlmodel import Column, DateTime, Field, Numeric, Session, SQLModel, create_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter06.db")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)

app = FastAPI(
    title="Глава 6: SQLModel",
    description="SQLite, SQLModel, CRUD",
    version="1.0.0",
)


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))


class ProductRead(SQLModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int


class ProductCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0)
    stock: int = Field(default=0, ge=0)


def get_db():
    with Session(engine) as db:
        yield db


@app.post("/api/products", response_model=ProductRead, status_code=201)
async def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
        ''',
        "code_notes": [
            "<code>SQLModel, table=True</code> делает класс таблицей, а не только Pydantic-схемой.",
            "<code>Field</code> задаёт правила поля: primary key, длину строки, ограничения чисел и настройки колонки.",
            "<code>with Session(engine)</code> гарантирует закрытие Session после запроса.",
            "<code>response_model</code> не отдаёт наружу лишние поля таблицы.",
            "В учебном режиме таблицы создаются автоматически, а Alembic показан как правильный путь для реального проекта.",
        ],
        "task": "Добавьте поле <code>category</code> в SQLModel-таблицу продукта, модели <code>ProductCreate</code>, <code>ProductUpdate</code>, <code>ProductRead</code> и Alembic-миграцию. Проверьте, что оно возвращается в <code>GET /api/products</code>.",
        "answer": '''
category: str = Field(default="general", max_length=80)


class ProductRead(SQLModel):
    id: int
    name: str
    category: str
    ...
        ''',
        "answer_notes": [
            "Менять нужно и SQLModel-таблицу, и входные/выходные модели, иначе поле либо не сохранится, либо не попадёт в публичный ответ.",
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
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
USERS: dict[str, dict] = {}


app = FastAPI(
    title="Глава 7: JWT Authorization",
    description="Authentication and authorization",
    version="1.0.0",
)


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(username: str, role: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from error
    user = USERS.get(str(username))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    user = USERS.get(request.username)
    if user is None or not pwd_context.verify(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    token, expires = create_access_token(user["username"], user["role"])
    return {"token": token, "token_type": "bearer", "expires": expires}


@app.get("/api/protected")
async def protected(user: dict = Depends(get_current_user)):
    return {"message": "Это защищенный endpoint", "username": user["username"], "role": user["role"]}
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
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter08.db")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 7


app = FastAPI(
    title="Глава 8: Refresh Tokens",
    description="Token rotation and revoke",
    version="1.0.0",
)


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(user: User) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {"sub": str(user.id), "username": user.username, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires


def create_refresh_token(db: Session, user: User) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=token, user_id=user.id, expires_at=expires))
    db.commit()
    return token, expires


@app.post("/api/auth/refresh")
async def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    stored = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    if stored is None or stored.revoked or stored.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=401, detail="Недействительный refresh token")

    stored.revoked = True
    user = db.get(User, stored.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(db, user)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires": access_expires,
        "refresh_token_expires": refresh_expires,
    }
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
from uuid import uuid4

from fastapi import FastAPI, WebSocket


app = FastAPI(
    title="Глава 9: WebSockets",
    description="Raw WebSocket chat",
    version="1.0.0",
)


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


manager = ConnectionManager()
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
from collections import defaultdict

from fastapi import FastAPI
import socketio


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI(title="Глава 10: Socket.IO chat")
app = socketio.ASGIApp(
    sio,
    other_asgi_app=fastapi_app,
    socketio_path="socket.io",
)

socketio_clients: dict[str, str] = {}
socketio_rooms: dict[str, set[str]] = defaultdict(set)

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
    for members in socketio_rooms.values():
        members.discard(sid)
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
import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
import socketio


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
fastapi_app = FastAPI(title="Глава 11: Auth Socket.IO")


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return str(payload["sub"])
    except (JWTError, KeyError) as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error


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


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
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
import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool
import socketio


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter12.db")


fastapi_app = FastAPI(title="Глава 12: Socket.IO и тестирование")
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class ChatGroup(Base):
    __tablename__ = "chat_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="group")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    sender: Mapped[str] = mapped_column(String(120), nullable=False)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("chat_groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    group: Mapped[ChatGroup | None] = relationship(back_populates="messages")


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1)
    sender: str = Field(min_length=1)
    group_id: int | None = None


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def send_message(self, text: str, sender: str, group_id: int | None = None) -> Message:
        message = Message(text=text, sender=sender, group_id=group_id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


socketio_clients: dict[str, str] = {}


def message_to_dict(message: Message) -> dict:
    return {
        "id": message.id,
        "text": message.text,
        "sender": message.sender,
        "group_id": message.group_id,
        "created_at": message.created_at.isoformat(),
    }


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


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
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
            "title": "Полный API-код после изменения",
            "code": '''
import logging
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Depends, FastAPI, Query


app = FastAPI(
    title="Глава 2: Dependency Injection",
    description="Depends and lifetimes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
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


def get_log_prefix() -> str:
    return "[DI LOG]"


def get_current_user(
    username: str = Query("guest"),
    role: str = Query("student"),
) -> UserContext:
    return UserContext(username=username, role=role)


def shape(service: InstanceService) -> dict[str, str]:
    return {"id": service.id, "type": service.service_type}


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
        "scoped": {
            "service1": shape(scoped1),
            "service2": shape(scoped2),
            "explanation": "Depends кеширует одинаковую зависимость в пределах запроса.",
        },
        "singleton": {
            "service1": shape(singleton1),
            "service2": shape(singleton2),
            "explanation": "Глобальный объект живет всё время работы приложения.",
        },
        "transient": {
            "service1": shape(transient1),
            "service2": shape(transient2),
            "explanation": "use_cache=False создает новый экземпляр при каждом вызове.",
        },
    }


@app.get("/api/dependency-injection/singleton-demo")
async def singleton_demo(service: SingletonDiService = Depends(get_singleton_di_service)):
    return {
        "id": service.id,
        "name": service.name,
        "explanation": "Один объект создан на уровне модуля, а dependency каждый раз возвращает ссылку на него.",
    }


@app.get("/api/dependency-injection/settings-demo")
async def settings_demo(settings: AppSettings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "explanation": "Endpoint получил settings через Depends(get_settings).",
    }


@app.get("/api/dependency-injection/current-user")
async def current_user(user: UserContext = Depends(get_current_user)):
    return {
        "username": user.username,
        "role": user.role,
        "explanation": "Dependency прочитала query-параметры и собрала UserContext.",
    }


@app.get("/api/dependency-injection/logger-demo")
async def logger_demo(
    message: str = "Тестовое сообщение",
    app_logger: logging.Logger = Depends(get_logger),
):
    app_logger.info("Получен запрос на логирование: %s", message)
    app_logger.warning("Это предупреждение через logging")
    return {"message": "Сообщения залогированы. Проверьте консоль.", "logged_message": message}


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
            "body": "Решение должно реально сходить в открытый внешний сервис JSONPlaceholder. Не создавайте локальный список комментариев и не возвращайте заранее написанный JSON: смысл задачи - потренироваться на стороннем HTTP API.",
            "items": [
                "Публичный base URL уже есть в главе: <code>JSONPLACEHOLDER = \"https://jsonplaceholder.typicode.com\"</code>.",
                "Метод сервиса должен вызвать внешний путь <code>/posts/{post_id}/comments</code> через <code>httpx.AsyncClient</code>.",
                "FastAPI endpoint должен остаться тонким: принять <code>post_id</code>, вызвать метод сервиса и обработать <code>httpx.HTTPError</code>.",
                "Для ошибок используйте тот же <code>map_http_error</code>, что и в остальных endpoint-ах главы.",
            ],
        },
        {
            "title": "Полный API-код после изменения",
            "code": '''
import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Глава 3: HTTP Requests",
    description="httpx AsyncClient",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
JSONPLACEHOLDER = "https://jsonplaceholder.typicode.com"


class CreatePostRequest(BaseModel):
    title: str
    body: str
    user_id: int


class ExternalApiService:
    def __init__(self, base_url: str = JSONPLACEHOLDER):
        self.base_url = base_url

    async def get_post(self, post_id: int) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}")
            response.raise_for_status()
            return response.json()

    async def get_posts(self) -> list[dict]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get("/posts")
            response.raise_for_status()
            return response.json()

    async def create_post(self, request: CreatePostRequest) -> dict:
        payload = {"title": request.title, "body": request.body, "userId": request.user_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.post("/posts", json=payload)
            response.raise_for_status()
            return response.json()

    async def get_post_comments(self, post_id: int) -> list[dict]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}/comments")
            response.raise_for_status()
            return response.json()


def get_external_api_service() -> ExternalApiService:
    return ExternalApiService()


def map_http_error(error: httpx.HTTPError) -> HTTPException:
    status_code = 502
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
    return HTTPException(status_code=status_code, detail=str(error))


@app.get("/api/http-client/direct/{post_id}")
async def get_post_direct(post_id: int):
    try:
        async with httpx.AsyncClient(base_url=JSONPLACEHOLDER, timeout=10.0) as client:
            response = await client.get(f"/posts/{post_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


@app.get("/api/http-client/post/{post_id}")
async def get_post(post_id: int, service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.get_post(post_id)
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


@app.get("/api/http-client/posts")
async def get_posts(service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.get_posts()
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


@app.post("/api/http-client/post")
async def create_post(request: CreatePostRequest, service: ExternalApiService = Depends(get_external_api_service)):
    try:
        return await service.create_post(request)
    except httpx.HTTPError as error:
        raise map_http_error(error) from error


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
                ("Внешний API напрямую", "Откройте <code>https://jsonplaceholder.typicode.com/posts/1/comments</code> и убедитесь, что сторонний сервис возвращает JSON."),
                ("GET /api/http-client/post/1/comments", "Ваш endpoint возвращает список комментариев к посту 1 из JSONPlaceholder."),
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
            "title": "Полный API-код после изменения",
            "code": '''
import time

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(
    title="Глава 4: Error Handling",
    description="Exception handlers and middleware",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class NotReadyError(Exception):
    pass


class DemoError(Exception):
    pass


class ValidationRequest(BaseModel):
    name: str = ""
    age: int = 0


@app.middleware("http")
async def request_logging_middleware(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started:.6f}"
    return response


@app.exception_handler(DemoError)
async def demo_error_handler(request, exc: DemoError):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url.path)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "details": exc.errors()},
    )


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


@app.get("/api/error-demo/throw")
async def throw_exception():
    raise DemoError("Это тестовое исключение для демонстрации обработки ошибок")


@app.get("/api/error-demo/badrequest")
async def bad_request_demo():
    raise HTTPException(status_code=400, detail="Это пример BadRequest ответа")


@app.post("/api/error-demo/validate")
async def validate_demo(request: ValidationRequest):
    errors: dict[str, str] = {}
    if not request.name:
        errors["name"] = "Имя обязательно"
    if request.age < 0 or request.age > 150:
        errors["age"] = "Возраст должен быть от 0 до 150"
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})
    return {"message": "Валидация прошла успешно", "data": request.model_dump()}


@app.get("/api/error-demo/success")
async def success():
    return {"message": "Запрос выполнен успешно"}
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
            "body": "Нужно сделать одну простую вещь: передать из Python ещё один список и вывести его в HTML через Jinja-цикл. Это тренирует главный навык главы: endpoint готовит данные, шаблон их показывает.",
            "items": [
                "Добавить ключ <code>homework_steps</code> в context, который получает шаблон.",
                "В <code>chapter05/templates/jinja_demo.html</code> добавить блок <code>{% for step in homework_steps %}</code>.",
                "<code>/api/template-data</code> не менять: задача про HTML-шаблон, а не про расширение JSON API.",
            ],
        },
        {
            "title": "Полный код chapter05/app/main.py",
            "code": '''
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

LESSON_TOPICS = [
    {
        "name": "Переменная",
        "template": "{{ title }}",
        "description": "Jinja2 берёт значение из context и вставляет его в HTML.",
    },
    {
        "name": "Условие if",
        "template": "{% if show_hint %}",
        "description": "Блок показывается только тогда, когда значение истинное.",
    },
    {
        "name": "Цикл for",
        "template": "{% for topic in topics %}",
        "description": "Один HTML-фрагмент повторяется для каждого элемента списка.",
    },
]

HOMEWORK_STEPS = [
    "Открыть страницу /jinja-demo",
    "Найти блок Домашние шаги",
    "Сравнить пункты на странице с Python-списком",
]

app = FastAPI(
    title="Глава 5: Jinja2 basics",
    description="Templates, variables, if, for",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/swagger", include_in_schema=False)
async def swagger():
    return RedirectResponse(url="/docs")


def demo_context(request: Request) -> dict:
    return {
        "request": request,
        "title": "Jinja2 demo",
        "student_name": "Анна",
        "topics": LESSON_TOPICS,
        "homework_steps": HOMEWORK_STEPS,
        "show_hint": True,
    }


@app.get("/jinja-demo", response_class=HTMLResponse, include_in_schema=False)
async def jinja_demo(request: Request):
    return templates.TemplateResponse(request, "jinja_demo.html", demo_context(request))


@app.get("/api/template-data")
async def template_data():
    return {
        "title": "Jinja2 demo",
        "student_name": "Анна",
        "topics": LESSON_TOPICS,
        "show_hint": True,
    }
            ''',
        },
        {
            "title": "Полный шаблон chapter05/templates/jinja_demo.html",
            "code": '''
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
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
            <h1>{{ title }}</h1>
            <p>Привет, {{ student_name }}. Эту строку собрал серверный шаблон Jinja2.</p>
        </section>

        {% if show_hint %}
        <section class="info-box">
            <h2>Подсказка</h2>
            <p>Все значения ниже пришли из Python-словаря, который endpoint передал в template context.</p>
        </section>
        {% endif %}

        <section class="info-box">
            <h2>Что показывает шаблон</h2>
            <ul class="flow-list">
                {% for topic in topics %}
                <li>
                    <strong>{{ topic.name }}</strong>
                    <code>{{ topic.template }}</code>
                    <span>{{ topic.description }}</span>
                </li>
                {% endfor %}
            </ul>
        </section>

        <section class="info-box">
            <h2>Домашние шаги</h2>
            <ol class="flow-list">
                {% for step in homework_steps %}
                <li>{{ step }}</li>
                {% endfor %}
            </ol>
        </section>
    </main>
</body>
</html>
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("GET /jinja-demo", "На странице есть блок <code>Домашние шаги</code> и три пункта из списка."),
                ("GET /api/template-data", "JSON остаётся базовым и не содержит <code>homework_steps</code>."),
            ],
        },
    ],
    "chapter06": [
        {
            "title": "Что меняем",
            "body": "Поле <code>category</code> должно пройти через общую SQLModel-схему, таблицу, модель создания, модель обновления, модель ответа и миграцию.",
            "items": [
                "Создать <code>ProductBase</code> с общими полями продукта.",
                "Сделать <code>Product</code>, <code>ProductCreate</code> и <code>ProductRead</code> наследниками <code>ProductBase</code>.",
                "В <code>ProductUpdate</code> оставить optional-поля для частичного обновления.",
                "Создать Alembic migration с <code>op.add_column</code>.",
                "Запустить <code>alembic upgrade head</code> из папки <code>chapter06</code>.",
            ],
        },
        {
            "title": "Последовательность работы",
            "body": "Делайте именно в таком порядке. Если сначала запустить Alembic, а потом менять SQLModel-код, будет сложно понять, какая часть уже готова, а какая ещё нет.",
            "items": [
                "1. Откройте файл <code>chapter06/app/main.py</code> и сначала поправьте Python-код: добавьте <code>ProductBase</code>, наследование схем и поле <code>category</code>.",
                "2. Проверьте глазами, что <code>Product</code>, <code>ProductCreate</code> и <code>ProductRead</code> наследуются от <code>ProductBase</code>, а <code>ProductUpdate</code> содержит optional-поле <code>category</code>.",
                "3. Перейдите в папку главы командой <code>cd chapter06</code>. Alembic-команды запускаем отсюда, потому что здесь лежит <code>alembic.ini</code>.",
                "4. Выполните <code>alembic current</code>, чтобы увидеть, на какой миграции сейчас находится база.",
                "5. Создайте новую миграцию: <code>alembic revision -m \"add product category\"</code>.",
                "6. Откройте созданный файл в <code>chapter06/alembic/versions/</code>. Alembic уже добавит туда переменные <code>revision</code> и <code>down_revision</code>.",
                "7. Вставьте в этот файл содержимое функций <code>upgrade()</code> и <code>downgrade()</code> из ответа. Если файл создан командой Alembic, не обязательно переписывать сгенерированный <code>revision</code>.",
                "8. Выполните <code>alembic upgrade head</code>, чтобы реально добавить колонку <code>category</code> в SQLite-таблицу.",
                "9. Выполните <code>alembic current</code> ещё раз. Теперь база должна быть на новой миграции.",
                "10. Запустите приложение и проверьте <code>POST /api/products</code>, затем <code>GET /api/products</code>.",
            ],
        },
        {
            "title": "Полный код SQLModel-части",
            "code": '''
import os
from datetime import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.pool import StaticPool
from sqlmodel import Column, DateTime, Field, Numeric, Session, SQLModel, create_engine, select


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter06.db")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)


app = FastAPI(
    title="Глава 6: SQLModel",
    description="SQLite, SQLModel, Alembic, CRUD",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(default="general", max_length=80)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(gt=0, sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0, ge=0)


class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, nullable=False))


class ProductRead(ProductBase):
    id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)


def init_db() -> None:
    SQLModel.metadata.create_all(bind=engine)


def get_db():
    with Session(engine) as db:
        yield db


init_db()


@app.get("/api/products", response_model=list[ProductRead])
async def get_products(db: Session = Depends(get_db)):
    return db.exec(select(Product).order_by(Product.id)).all()


@app.get("/api/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(request: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(product_id: int, request: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
            ''',
        },
        {
            "title": "Мини-пример JSON, Column и Relationship в SQLModel",
            "body": "Этот фрагмент не обязателен для поля <code>category</code>, но показывает импорт и синтаксис, который часто нужен в реальных моделях: JSON-колонка и связь между таблицами.",
            "code": '''
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    options: dict = Field(default_factory=dict, sa_column=Column(JSON))
    reviews: list["ProductReview"] = Relationship(back_populates="product")


class ProductReview(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    text: str
    product: Product | None = Relationship(back_populates="reviews")
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
            "title": "Команды Alembic для этой задачи",
            "body": "Сначала меняете SQLModel-код, затем создаёте файл миграции, вставляете туда <code>upgrade()</code> и <code>downgrade()</code> из ответа, после этого применяете миграцию. Для первого раза лучше использовать обычный <code>alembic revision -m</code>: так вы сами видите, какие строки меняют базу. Позже можно попробовать <code>alembic revision --autogenerate -m</code>, но автогенерацию всё равно нужно читать глазами.",
            "code": '''
cd chapter06

# 1. Проверить, видит ли Alembic текущую базу и текущую миграцию.
alembic current

# 2. Создать новый пустой файл миграции.
alembic revision -m "add product category"

# 3. Открыть созданный файл в chapter06/alembic/versions/
#    и вставить туда upgrade() и downgrade() из ответа выше.

# 4. Применить миграцию к SQLite-базе.
alembic upgrade head

# 5. Проверить, что база теперь находится на последней миграции.
alembic current

# 6. Если нужно откатиться на один шаг назад.
alembic downgrade -1

# 7. Посмотреть всю историю миграций.
alembic history
            ''',
        },
        {
            "title": "Как проверить",
            "checks": [
                ("POST /api/products", 'Body содержит <code>"category": "books"</code>.'),
                ("GET /api/products", "Каждый продукт возвращает поле <code>category</code>."),
                ("Alembic", "После <code>alembic upgrade head</code> команда <code>alembic current</code> показывает новую миграцию."),
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
            "title": "Полный API-код после изменения",
            "code": '''
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


app = FastAPI(
    title="Глава 7: JWT Authorization",
    description="Authentication and authorization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
USERS: dict[str, dict] = {}


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    username: str
    role: str
    expires: datetime


def create_access_token(username: str, role: str) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from error
    user = USERS.get(str(username))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if any(user["email"] == request.email for user in USERS.values()):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    role = "admin" if request.username == "admin" else "user"
    USERS[request.username] = {
        "username": request.username,
        "email": request.email,
        "password_hash": pwd_context.hash(request.password),
        "role": role,
    }
    token, expires = create_access_token(request.username, role)
    return AuthResponse(token=token, username=request.username, role=role, expires=expires)


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    user = USERS.get(request.username)
    if user is None or not pwd_context.verify(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    token, expires = create_access_token(user["username"], user["role"])
    return AuthResponse(token=token, username=user["username"], role=user["role"], expires=expires)


@app.get("/api/protected")
async def protected(user: dict = Depends(get_current_user)):
    return {"message": "Это защищенный endpoint", "username": user["username"], "role": user["role"]}


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
            "title": "Ключевое место для admin-роли",
            "body": "В полном коде выше это уже встроено в register. Отдельно выделено место, где обычный пользователь отличается от admin.",
            "items": [
                "Если username равен <code>admin</code>, учебный код выдаёт роль <code>admin</code>.",
                "Для всех остальных username роль остаётся <code>user</code>.",
                "Token создаётся уже с выбранной ролью, поэтому <code>require_admin</code> может проверить её позже.",
            ],
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
            "title": "Полный API-код после изменения",
            "code": '''
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


app = FastAPI(
    title="Глава 8: Refresh Tokens",
    description="Token rotation and revoke",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter08.db")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    role: str
    access_token_expires: datetime
    refresh_token_expires: datetime


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(user: User) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "username": user.username, "role": user.role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires


def create_refresh_token(db: Session, user: User) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=token, user_id=user.id, expires_at=expires))
    db.commit()
    return token, expires


def revoke_token(stored: RefreshToken) -> None:
    stored.revoked = True
    stored.revoked_at = datetime.utcnow()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from error
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


init_db()


@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    user = User(
        username=request.username,
        email=request.email,
        password_hash=pwd_context.hash(request.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(db, user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        role=user.role,
        access_token_expires=access_expires,
        refresh_token_expires=refresh_expires,
    )


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if user is None or not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(db, user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        role=user.role,
        access_token_expires=access_expires,
        refresh_token_expires=refresh_expires,
    )


@app.post("/api/auth/refresh", response_model=AuthResponse)
async def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    stored = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    if stored is None or stored.revoked or stored.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    revoke_token(stored)
    user = db.get(User, stored.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    access_token, access_expires = create_access_token(user)
    refresh_token, refresh_expires = create_refresh_token(db, user)
    db.commit()
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        role=user.role,
        access_token_expires=access_expires,
        refresh_token_expires=refresh_expires,
    )


@app.post("/api/auth/revoke")
async def revoke(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    stored = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    if stored is not None and not stored.revoked:
        revoke_token(stored)
        db.commit()
    return {"message": "Refresh token отозван"}


@app.post("/api/auth/logout")
async def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked.is_(False),
    ).all()
    for token in tokens:
        revoke_token(token)
    db.commit()
    return {"message": f"Все сессии завершены. Отозвано токенов: {len(tokens)}"}
            ''',
        },
        {
            "title": "Где использовать revoke_token",
            "body": "В полном коде выше helper <code>revoke_token</code> используется во всех местах, где refresh token становится недействительным.",
            "items": [
                "В <code>/api/auth/refresh</code> старый token отзывается перед выдачей новой пары token-ов.",
                "В <code>/api/auth/revoke</code> отзывается token, который прислал клиент.",
                "В <code>/api/auth/logout</code> отзываются все активные refresh token-ы текущего пользователя.",
            ],
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
            "title": "Полный WebSocket API-код после изменения",
            "code": '''
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI(
    title="Глава 9: WebSockets",
    description="Raw WebSocket chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        self.active_connections[connection_id] = websocket
        await websocket.send_json({"event": "connected", "connection_id": connection_id})
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        self.active_connections.pop(connection_id, None)

    async def broadcast(self, payload: dict) -> None:
        disconnected: list[str] = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                disconnected.append(connection_id)
        for connection_id in disconnected:
            self.disconnect(connection_id)


manager = ConnectionManager()


@app.get("/api/websocket/info")
async def websocket_info():
    return {"endpoint": "/ws", "connections": len(manager.active_connections)}


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
            "title": "Полный Socket.IO API-код после изменения",
            "code": '''
from collections import defaultdict
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import socketio


fastapi_app = FastAPI(
    title="Глава 10: Socket.IO чат",
    description="Groups and direct messages",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


class ChatManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.groups: dict[str, set[str]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, group: str) -> str:
        await websocket.accept()
        connection_id = str(uuid4())
        self.connections[connection_id] = websocket
        self.groups[group].add(connection_id)
        await websocket.send_json({"event": "connected", "connection_id": connection_id, "group": group})
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        self.connections.pop(connection_id, None)
        for members in self.groups.values():
            members.discard(connection_id)

    async def send_to_connection(self, connection_id: str, payload: dict) -> bool:
        websocket = self.connections.get(connection_id)
        if websocket is None:
            return False
        await websocket.send_json(payload)
        return True

    async def broadcast(self, payload: dict, exclude: str | None = None) -> None:
        for connection_id in list(self.connections):
            if connection_id != exclude:
                await self.send_to_connection(connection_id, payload)

    async def send_to_group(self, group: str, payload: dict) -> None:
        for connection_id in list(self.groups[group]):
            await self.send_to_connection(connection_id, payload)


manager = ChatManager()
socketio_clients: dict[str, str] = {}
socketio_rooms: dict[str, set[str]] = defaultdict(set)


@fastapi_app.get("/api/chat/info")
async def chat_info():
    return {
        "raw_websocket_connections": len(manager.connections),
        "socketio_connections": len(socketio_clients),
        "groups": {name: len(members) for name, members in manager.groups.items()},
        "socketio_rooms": {name: len(members) for name, members in socketio_rooms.items()},
    }


@fastapi_app.websocket("/ws/chat")
async def chat_socket(websocket: WebSocket, group: str = "general"):
    connection_id = await manager.connect(websocket, group)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action", "broadcast")
            payload = {
                "event": "message",
                "from": connection_id,
                "user": data.get("user", "anonymous"),
                "message": data.get("message", ""),
            }
            if action == "send_to_connection":
                await manager.send_to_connection(data["connection_id"], payload)
            elif action == "send_to_group":
                await manager.send_to_group(data.get("group", group), payload)
            elif action == "join":
                manager.groups[data.get("group", group)].add(connection_id)
                await manager.send_to_connection(
                    connection_id,
                    {"event": "joined", "group": data.get("group", group)},
                )
            else:
                await manager.broadcast(payload)
    except WebSocketDisconnect:
        manager.disconnect(connection_id)


@sio.event
async def connect(sid, environ):
    socketio_clients[sid] = "anonymous"
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def disconnect(sid):
    socketio_clients.pop(sid, None)
    for members in socketio_rooms.values():
        members.discard(sid)


@sio.event
async def set_name(sid, data):
    username = data.get("username", "anonymous")
    socketio_clients[sid] = username
    await sio.emit("name_set", {"sid": sid, "username": username}, to=sid)


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


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
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
            "title": "Полный Socket.IO auth API-код после изменения",
            "code": '''
import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
import socketio


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fastapi-book-development-secret")
ALGORITHM = "HS256"

fastapi_app = FastAPI(
    title="Глава 11: Auth Socket.IO",
    description="JWT protected Socket.IO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(username: str, role: str = "user") -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": username, "role": role, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def verify_user_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": str(payload["sub"]), "role": str(payload.get("role", "user"))}
    except (JWTError, KeyError) as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error


def authorize_socketio(auth: dict | None) -> dict | None:
    token = (auth or {}).get("access_token") or (auth or {}).get("token")
    if not token:
        return None
    try:
        return verify_user_token(str(token))
    except HTTPException:
        return None


authorized_clients: dict[str, dict] = {}


@fastapi_app.post("/api/auth/login")
async def login(request: LoginRequest):
    if not request.username or not request.password:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    role = "admin" if request.username == "admin" else "user"
    return {
        "access_token": create_access_token(request.username, role),
        "token_type": "bearer",
        "username": request.username,
        "role": role,
    }


@fastapi_app.get("/api/socket/info")
async def socket_info():
    return {
        "authorized_connections": len(authorized_clients),
        "users": [user["username"] for user in authorized_clients.values()],
    }


@sio.event
async def connect(sid, environ, auth):
    user = authorize_socketio(auth)
    if user is None:
        return False
    authorized_clients[sid] = user
    if user["role"] == "admin":
        await sio.enter_room(sid, "admins")
    await sio.emit("authorized", {"sid": sid, **user}, to=sid)


@sio.event
async def disconnect(sid):
    authorized_clients.pop(sid, None)


@sio.event
async def authorized_message(sid, data):
    user = authorized_clients.get(sid)
    if user is None:
        return
    await sio.emit("authorized_message", {
        "event": "authorized_message",
        "sid": sid,
        "username": user["username"],
        "message": data.get("message", ""),
    })


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


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
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
            "title": "Полный код приложения после изменения",
            "code": '''
import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool
import socketio


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chapter12.db")


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {"connect_args": connect_args}
    if database_url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class ChatGroup(Base):
    __tablename__ = "chat_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="group")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    sender: Mapped[str] = mapped_column(String(120), nullable=False)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("chat_groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    group: Mapped[ChatGroup | None] = relationship(back_populates="messages")


class MessageDto(BaseModel):
    id: int
    text: str
    sender: str
    group_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatGroupDto(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1)
    sender: str = Field(min_length=1)
    group_id: int | None = None


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def send_message(self, text: str, sender: str, group_id: int | None = None) -> Message:
        if group_id is not None and self.db.get(ChatGroup, group_id) is None:
            raise HTTPException(status_code=404, detail="Group not found")
        message = Message(text=text, sender=sender, group_id=group_id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, group_id: int | None = None) -> list[Message]:
        query = self.db.query(Message)
        if group_id is not None:
            query = query.filter(Message.group_id == group_id)
        return query.order_by(Message.created_at, Message.id).all()

    def create_group(self, name: str) -> ChatGroup:
        group = ChatGroup(name=name)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def get_groups(self) -> list[ChatGroup]:
        return self.db.query(ChatGroup).order_by(ChatGroup.id).all()

    def delete_group(self, group_id: int) -> None:
        group = self.db.get(ChatGroup, group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        self.db.query(Message).filter(Message.group_id == group_id).delete()
        self.db.delete(group)
        self.db.commit()


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


def message_to_dict(message: Message) -> dict:
    return {
        "id": message.id,
        "text": message.text,
        "sender": message.sender,
        "group_id": message.group_id,
        "created_at": message.created_at.isoformat(),
    }


init_db()

fastapi_app = FastAPI(
    title="Глава 12: Socket.IO и тестирование",
    description="API, service layer, Socket.IO, in-memory DB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socketio_clients: dict[str, str] = {}


@fastapi_app.post("/api/chat/messages", response_model=MessageDto)
async def send_message(request: SendMessageRequest, service: ChatService = Depends(get_chat_service)):
    return service.send_message(request.text, request.sender, request.group_id)


@fastapi_app.get("/api/chat/messages", response_model=list[MessageDto])
async def get_messages(group_id: int | None = None, service: ChatService = Depends(get_chat_service)):
    return service.get_messages(group_id)


@fastapi_app.post("/api/chat/groups", response_model=ChatGroupDto)
async def create_group(request: CreateGroupRequest, service: ChatService = Depends(get_chat_service)):
    return service.create_group(request.name)


@fastapi_app.get("/api/chat/groups", response_model=list[ChatGroupDto])
async def get_groups(service: ChatService = Depends(get_chat_service)):
    return service.get_groups()


@fastapi_app.delete("/api/chat/groups/{group_id}", status_code=204)
async def delete_group(group_id: int, service: ChatService = Depends(get_chat_service)):
    service.delete_group(group_id)


@fastapi_app.get("/api/chat/realtime")
async def realtime_info():
    return {
        "socketio_path": "/socket.io",
        "events": ["set_name", "join_group", "chat_message", "list_messages", "delete_group"],
        "connections": len(socketio_clients),
    }


@sio.event
async def connect(sid, environ):
    socketio_clients[sid] = "anonymous"
    await sio.enter_room(sid, "global")
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def disconnect(sid):
    socketio_clients.pop(sid, None)


@sio.event
async def set_name(sid, data):
    username = data.get("username", "anonymous")
    socketio_clients[sid] = username
    await sio.emit("name_set", {"sid": sid, "username": username}, to=sid)


@sio.event
async def join_group(sid, data):
    group_id = data.get("group_id")
    if group_id is not None:
        group_id = int(group_id)
    room = f"group:{group_id}" if group_id is not None else "global"
    await sio.enter_room(sid, room)
    await sio.emit("joined_group", {"room": room, "group_id": group_id}, to=sid)


@sio.event
async def chat_message(sid, data):
    sender = data.get("sender") or socketio_clients.get(sid, "anonymous")
    text = data.get("text") or data.get("message", "")
    group_id = data.get("group_id")
    if group_id is not None:
        group_id = int(group_id)
    with SessionLocal() as db:
        service = ChatService(db)
        message = service.send_message(text=text, sender=sender, group_id=group_id)
        payload = {"event": "chat_message", "message": message_to_dict(message)}
    room = f"group:{group_id}" if group_id is not None else "global"
    await sio.emit("chat_message", payload, room=room)


@sio.event
async def list_messages(sid, data):
    group_id = data.get("group_id")
    if group_id is not None:
        group_id = int(group_id)
    with SessionLocal() as db:
        service = ChatService(db)
        messages = [message_to_dict(message) for message in service.get_messages(group_id)]
    await sio.emit("messages", {"group_id": group_id, "items": messages}, to=sid)


@sio.event
async def delete_group(sid, data):
    group_id = int(data["group_id"])
    with SessionLocal() as db:
        service = ChatService(db)
        service.delete_group(group_id)
    await sio.emit("group_deleted", {"group_id": group_id})


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
app.dependency_overrides = fastapi_app.dependency_overrides
            ''',
        },
        {
            "title": "Полный тест",
            "code": '''
from fastapi.testclient import TestClient

from chapter12.app.main import Base, app, get_db
from tests.conftest import make_sqlite_override


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


ANSWER_WALKTHROUGHS = {
    "chapter01": [
        {
            "title": "Куда вставлять новый endpoint",
            "body": "Новый <code>power</code> ставится в тот же файл, где уже лежит калькулятор: <code>chapter01/app/main.py</code>. Его удобно разместить рядом с остальными маршрутами <code>/api/calculator/*</code>, потому что это часть того же API.",
            "items": [
                "<code>from typing import Annotated</code>, <code>FastAPI</code>, <code>Header</code>, <code>HTTPException</code> и <code>BaseModel</code> остаются наверху файла, потому что это зависимости всего приложения.",
                "<code>app = FastAPI(...)</code> должен быть создан один раз. Именно в этот объект FastAPI записывает все endpoint-ы.",
                "<code>CalculationRequest</code> уже описывает JSON body с полями <code>a</code> и <code>b</code>, поэтому новую модель для степени делать не нужно.",
                "<code>@app.post(\"/api/calculator/power\")</code> регистрирует новый POST-маршрут. Декоратор должен стоять прямо над функцией.",
            ],
        },
        {
            "title": "Почему функция выглядит именно так",
            "items": [
                "<code>async def power(...)</code> делает endpoint асинхронным, как остальные функции в главе. Для новичка важно привыкнуть: FastAPI спокойно работает с <code>async</code> endpoint-ами.",
                "<code>request: CalculationRequest</code> говорит FastAPI: прочитай JSON body, проверь поля <code>a</code> и <code>b</code>, а потом передай в функцию готовый Python-объект.",
                "<code>request.a ** request.b</code> - обычная операция Python для возведения в степень. Она стоит внутри <code>result</code>, потому что клиенту нужен результат вычисления.",
                "<code>\"operation\": \"power\"</code> сохраняет тот же формат ответа, что и остальные операции калькулятора. Клиенту проще работать, когда все операции отвечают одинаково.",
            ],
        },
        {
            "title": "Что не надо менять",
            "items": [
                "Команда запуска Uvicorn не меняется, потому что файл, модуль и переменная <code>app</code> остались прежними.",
                "Middleware с header-ом тоже не меняется: он автоматически сработает для нового endpoint-а, потому что оборачивает всё приложение.",
                "Swagger не нужно редактировать руками. FastAPI сам добавит новый маршрут в <code>/docs</code>, когда увидит новый декоратор.",
                "Статические файлы и Jinja2-шаблоны к этому заданию не относятся. Задача про JSON API, поэтому лишний UI-код только путает.",
            ],
        },
        {
            "title": "Как понять, что решение правильное",
            "items": [
                "Откройте <code>/docs</code> и найдите <code>POST /api/calculator/power</code>. Если его нет, значит приложение не перезапустилось или декоратор написан неверно.",
                "Отправьте <code>{\"a\": 2, \"b\": 3}</code>. Ответ должен содержать <code>\"result\": 8</code>.",
                "Отправьте <code>{\"a\": 5, \"b\": 0}</code>. Ответ должен содержать <code>\"result\": 1</code>, потому что любое число в нулевой степени равно 1.",
                "Если убрать поле <code>b</code>, FastAPI должен вернуть ошибку валидации. Это доказывает, что работает Pydantic-модель, а не ручной парсинг JSON.",
            ],
        },
    ],
    "chapter02": [
        {
            "title": "Куда добавлять dependency",
            "body": "В этой задаче dependency очень простая: она возвращает строку-префикс для логов. Её лучше поставить рядом с другими provider-функциями, например около <code>get_logger</code>.",
            "items": [
                "<code>def get_log_prefix() -> str</code> - обычная Python-функция. В FastAPI dependency не обязана быть классом.",
                "<code>return \"[DI LOG]\"</code> находится внутри dependency, чтобы endpoint не знал, какой именно префикс используется.",
                "Если завтра префикс изменится, вы поменяете одну dependency, а не все endpoint-ы, где нужен красивый лог.",
                "Тип <code>-> str</code> не обязателен для запуска, но новичку помогает понять, что именно dependency возвращает.",
            ],
        },
        {
            "title": "Как FastAPI подставляет prefix",
            "items": [
                "В параметре endpoint-а пишется <code>prefix: str = Depends(get_log_prefix)</code>.",
                "Важно: <code>get_log_prefix</code> передаётся без скобок. Если написать <code>get_log_prefix()</code>, функция вызовется сразу при импорте файла, а не во время запроса.",
                "FastAPI видит <code>Depends</code>, вызывает dependency перед выполнением endpoint-а и кладёт результат в переменную <code>prefix</code>.",
                "В этом же endpoint-е используется <code>app_logger: logging.Logger = Depends(get_logger)</code>. Это показывает, что endpoint может получить сразу несколько зависимостей.",
            ],
        },
        {
            "title": "Что делает endpoint",
            "items": [
                "<code>message: str = \"hello\"</code> - query-параметр. Если открыть endpoint без <code>?message=...</code>, будет использовано значение <code>hello</code>.",
                "<code>formatted_message = f\"{prefix} {message}\"</code> собирает итоговую строку из dependency-префикса и пользовательского текста.",
                "<code>app_logger.info(formatted_message)</code> показывает практический смысл DI: logger пришёл снаружи, endpoint его только использует.",
                "<code>return {\"formatted_message\": formatted_message}</code> нужен, чтобы результат был виден прямо в Swagger, даже если ученик не смотрит консоль.",
            ],
        },
        {
            "title": "Как проверять и где чаще ошибаются",
            "items": [
                "Проверьте <code>/api/dependency-injection/pretty-log?message=hello</code>. Должно вернуться <code>[DI LOG] hello</code>.",
                "Потом проверьте <code>message=FastAPI</code>. Меняется только текст после префикса.",
                "Если ответ возвращает только <code>hello</code>, значит dependency не используется при сборке строки.",
                "Если приложение падает при старте, проверьте, что <code>Depends</code> и <code>logging</code> импортированы, а <code>get_logger</code> действительно существует выше или ниже в модуле.",
            ],
        },
    ],
    "chapter03": [
        {
            "title": "Зачем нужен service layer",
            "body": "Задача добавляет запрос к реальному внешнему API JSONPlaceholder. Endpoint не должен сам знать все детали HTTP-клиента, поэтому логика запроса лежит в <code>ExternalApiService</code>.",
            "items": [
                "<code>JSONPLACEHOLDER</code> хранит базовый URL внешнего сервиса в одном месте.",
                "<code>ExternalApiService.__init__</code> принимает <code>base_url</code>, чтобы в тестах или будущем окружении можно было подменить внешний адрес.",
                "Метод <code>get_post_comments</code> лежит внутри сервиса, потому что это такая же внешняя операция, как получение поста.",
                "Endpoint остаётся тонким: он принимает <code>post_id</code>, получает сервис через dependency и возвращает результат сервиса.",
            ],
        },
        {
            "title": "Как работает httpx-код",
            "items": [
                "<code>async with httpx.AsyncClient(...)</code> открывает HTTP-клиент на время запроса и корректно закрывает соединения после выхода из блока.",
                "<code>base_url=self.base_url</code> позволяет писать короткий путь <code>/posts/{post_id}/comments</code>, а не полный URL каждый раз.",
                "<code>timeout=10.0</code> нужен, чтобы приложение не висело бесконечно, если внешний сервис тормозит.",
                "<code>await client.get(...)</code> отправляет GET-запрос асинхронно. Пока внешний API отвечает, event loop может обслуживать другие запросы.",
                "<code>response.raise_for_status()</code> превращает HTTP 4xx/5xx внешнего API в исключение, которое потом можно обработать единообразно.",
            ],
        },
        {
            "title": "Как endpoint связан с сервисом",
            "items": [
                "<code>post_id: int</code> берётся из path-параметра <code>/post/{post_id}/comments</code>.",
                "<code>service: ExternalApiService = Depends(get_external_api_service)</code> просит FastAPI создать или вернуть сервис.",
                "<code>return await service.get_post_comments(post_id)</code> отдаёт клиенту JSON, полученный из внешнего API.",
                "<code>except httpx.HTTPError as error</code> нужен, чтобы не показывать пользователю внутреннюю ошибку Python.",
                "<code>raise map_http_error(error) from error</code> сохраняет общий формат обработки ошибок, уже принятый в главе.",
            ],
        },
        {
            "title": "Как отличить реальную интеграцию от заглушки",
            "items": [
                "Сначала откройте <code>https://jsonplaceholder.typicode.com/posts/1/comments</code> напрямую. Вы должны увидеть список комментариев.",
                "Потом откройте локальный endpoint <code>/api/http-client/post/1/comments</code>. Структура ответа должна быть похожей.",
                "В коде не должно быть заранее написанного локального списка комментариев. Иначе задача не тренирует outbound HTTP.",
                "Если внешний сервис вернёт ошибку, ваш endpoint должен пройти через <code>map_http_error</code>, а не падать с traceback.",
            ],
        },
    ],
    "chapter04": [
        {
            "title": "Где создаётся новое исключение",
            "body": "<code>NotReadyError</code> лучше объявить рядом с другими custom exception-ами главы. Это не HTTP-ответ, а обычный Python-сигнал: внутри приложения произошла понятная ожидаемая ситуация.",
            "items": [
                "<code>class NotReadyError(Exception):</code> наследуется от базового <code>Exception</code>, чтобы его можно было бросать через <code>raise</code>.",
                "<code>pass</code> означает, что классу не нужны дополнительные поля. Сам тип исключения уже несёт смысл: сервис не готов.",
                "Отдельный класс лучше строки вроде <code>raise Exception(\"not ready\")</code>, потому что FastAPI может привязать handler именно к этому типу.",
                "Такой подход масштабируется: для разных ошибок можно сделать разные классы и разные HTTP-ответы.",
            ],
        },
        {
            "title": "Зачем нужен exception handler",
            "items": [
                "<code>@app.exception_handler(NotReadyError)</code> регистрирует функцию, которая будет ловить именно <code>NotReadyError</code>.",
                "Handler принимает <code>request</code>, чтобы при необходимости знать путь, пользователя, headers или request id.",
                "Handler принимает <code>exc</code>, потому что FastAPI передаёт само исключение. Даже если сейчас оно не используется, сигнатура остаётся стандартной.",
                "<code>JSONResponse</code> нужен, когда вы хотите вручную выбрать status code и тело ответа.",
            ],
        },
        {
            "title": "Почему status code 503",
            "items": [
                "<code>503 Service Unavailable</code> означает: сервер жив, но нужная часть сервиса временно недоступна.",
                "Это отличается от <code>500</code>: 500 говорит про неожиданную внутреннюю ошибку, а 503 - про ожидаемую временную недоступность.",
                "Сообщение <code>Сервис временно недоступен</code> должно лежать в JSON body, чтобы клиент мог показать его пользователю.",
                "Если добавить в ответ <code>path</code>, ученик видит, какой endpoint привёл к ошибке. Это удобно для отладки.",
            ],
        },
        {
            "title": "Как проверять",
            "items": [
                "Добавьте endpoint, который делает <code>raise NotReadyError()</code>, иначе handler не получится вызвать руками.",
                "Откройте <code>/api/error-demo/not-ready</code>. Статус должен быть <code>503</code>, а не <code>200</code> и не <code>500</code>.",
                "Проверьте JSON: там должно быть понятное поле с ошибкой, а не HTML-страница traceback.",
                "Проверьте другие endpoint-ы главы. Новый handler не должен ломать обычные успешные ответы.",
            ],
        },
    ],
    "chapter05": [
        {
            "title": "Что именно добавляем в Python",
            "body": "В Python-части не нужно создавать новую страницу, форму или модель. Нужно только подготовить ещё один список и положить его в context.",
            "items": [
                "<code>HOMEWORK_STEPS</code> - обычный Python-список строк. В нём нет магии Jinja2.",
                "Ключ <code>homework_steps</code> добавляется в словарь, который возвращает <code>demo_context</code>.",
                "<code>/api/template-data</code> специально не меняется, чтобы код урока и код ответа не сливались в одно и то же.",
                "Endpoint <code>/jinja-demo</code> не меняет бизнес-логику: он просто передаёт шаблону обновлённый context.",
            ],
        },
        {
            "title": "Что именно добавляем в шаблон",
            "items": [
                "Новый блок начинается с обычного заголовка <code>&lt;h2&gt;Домашние шаги&lt;/h2&gt;</code>.",
                "<code>&lt;ol&gt;</code> означает нумерованный список. Это базовый HTML: браузер сам поставит 1, 2, 3.",
                "<code>{% for step in homework_steps %}</code> говорит Jinja2: возьми список <code>homework_steps</code> и перебери его.",
                "<code>&lt;li&gt;{{ step }}&lt;/li&gt;</code> печатает один пункт списка.",
                "<code>{% endfor %}</code> закрывает цикл. Без закрытия Jinja2 не поймёт, где заканчивается повторяемый кусок.",
            ],
        },
        {
            "title": "Как работает for",
            "items": [
                "Если в списке три строки, HTML-блок внутри цикла появится три раза.",
                "На первом проходе <code>step</code> равен первой строке списка.",
                "На втором проходе <code>step</code> равен второй строке списка.",
                "На третьем проходе <code>step</code> равен третьей строке списка.",
                "После последнего элемента Jinja2 выходит из цикла и продолжает читать шаблон ниже.",
            ],
        },
        {
            "title": "Как проверить",
            "items": [
                "Откройте <code>http://localhost:8005/jinja-demo</code> и найдите блок <code>Домашние шаги</code>.",
                "Проверьте, что на странице видны все три пункта из <code>HOMEWORK_STEPS</code>.",
                "Откройте <code>http://localhost:8005/api/template-data</code> и проверьте, что там нет <code>homework_steps</code>.",
                "Если JSON содержит <code>homework_steps</code>, значит вы случайно перенесли ответ не только в шаблонную часть, но и в API endpoint.",
            ],
        },
    ],
    "chapter06": [
        {
            "title": "Где появляется новое поле category",
            "body": "Поле категории должно пройти через общий базовый класс, таблицу, модель создания, модель обновления, модель ответа, CRUD endpoint-ы и миграцию.",
            "items": [
                "<code>ProductBase.category</code> описывает общее поле один раз.",
                "<code>Product(ProductBase, table=True)</code> наследует поле и превращает его в колонку таблицы.",
                "<code>ProductCreate(ProductBase)</code> наследует поле и разрешает клиенту передать категорию при создании продукта.",
                "<code>ProductRead(ProductBase)</code> наследует поле и возвращает категорию наружу в JSON-ответе.",
                "<code>ProductUpdate.category</code> остаётся отдельным optional-полем, потому что при частичном обновлении клиент может прислать только одно поле.",
                "Если забыть модель ответа, поле будет в базе, но клиент его не увидит.",
            ],
        },
        {
            "title": "Почему нужен default и nullable",
            "items": [
                "<code>default=\"general\"</code> даёт понятное значение, если клиент не передал категорию.",
                "<code>nullable=False</code> говорит базе: у продукта всегда должна быть категория.",
                "<code>ProductBase</code> убирает повтор одинаковых полей между таблицей, схемой создания и схемой ответа.",
                "<code>ProductUpdate</code> не наследуется от <code>ProductBase</code>, потому что в update все поля optional, а в base часть полей обязательная.",
                "В учебной SQLite-БД таблицы создаются автоматически, но в реальном проекте структура меняется через миграции.",
                "Если в уже существующей таблице есть старые продукты, миграция должна дать им значение по умолчанию.",
            ],
        },
        {
            "title": "Зачем нужна Alembic migration",
            "items": [
                "<code>upgrade()</code> описывает движение вперёд: добавить колонку <code>category</code>.",
                "<code>downgrade()</code> описывает откат: удалить колонку, если миграцию нужно отменить.",
                "Миграция нужна не FastAPI, а базе данных. FastAPI сам не меняет production-схему при каждом запуске.",
                "Даже если demo-приложение вызывает <code>SQLModel.metadata.create_all</code>, главе важно показать правильный промышленный путь.",
            ],
        },
        {
            "title": "Что делают команды Alembic",
            "items": [
                "<code>cd chapter06</code> переводит терминал туда, где лежит <code>alembic.ini</code>. Без этого Alembic может не найти настройки.",
                "<code>alembic current</code> показывает, какая миграция уже применена к текущей базе.",
                "<code>alembic revision -m \"add product category\"</code> создаёт новый Python-файл миграции в <code>alembic/versions</code>.",
                "<code>alembic upgrade head</code> запускает функции <code>upgrade()</code> во всех новых миграциях и доводит базу до последней версии.",
                "<code>alembic downgrade -1</code> запускает <code>downgrade()</code> последней миграции и откатывает базу на один шаг назад.",
                "<code>alembic history</code> показывает список миграций, чтобы вы понимали порядок изменений базы.",
            ],
        },
        {
            "title": "Что проверять после изменения",
            "items": [
                "Создайте продукт без <code>category</code>. В ответе должно быть <code>category: \"general\"</code> или выбранное вами значение по умолчанию.",
                "Создайте продукт с <code>category: \"books\"</code>. Ответ должен вернуть именно <code>books</code>.",
                "Откройте список продуктов. Категория должна быть у каждого объекта.",
                "Запустите <code>cd chapter06</code>, затем <code>alembic upgrade head</code> и <code>alembic current</code>, чтобы проверить, что миграция применена.",
                "Запустите тесты CRUD с тестовой БД, чтобы убедиться, что изменения не завязаны на локальный файл SQLite.",
            ],
        },
    ],
    "chapter07": [
        {
            "title": "Чем authentication отличается от authorization в ответе",
            "body": "Login отвечает на вопрос “кто ты?”, а admin endpoint отвечает на вопрос “можно ли тебе сюда?”. Поэтому в решении появляются и token, и проверка роли.",
            "items": [
                "<code>RegisterRequest</code> получает роль пользователя при регистрации в учебном примере.",
                "<code>UserInDb</code> хранит роль на сервере вместе с username, email и hash пароля.",
                "<code>create_access_token</code> кладёт роль в JWT payload, чтобы сервер мог прочитать её позже.",
                "<code>get_current_user</code> проверяет token и возвращает пользователя, которому сервер доверяет.",
            ],
        },
        {
            "title": "Почему роль нельзя брать из запроса к admin endpoint",
            "items": [
                "Клиент может отправить любой JSON или query-параметр, например <code>role=admin</code>. Этому нельзя доверять.",
                "Роль должна прийти из проверенного источника: базы/памяти сервера или подписанного JWT.",
                "<code>jwt.decode</code> проверяет подпись token-а. Если token подделан, декодирование упадёт.",
                "После декодирования сервер ищет пользователя в <code>USERS</code>, чтобы убедиться, что такой пользователь всё ещё существует.",
            ],
        },
        {
            "title": "Как работает require_admin",
            "items": [
                "<code>require_admin</code> - отдельная dependency поверх <code>get_current_user</code>.",
                "Сначала FastAPI вызывает <code>get_current_user</code>, получает текущего пользователя, а потом передаёт его в <code>require_admin</code>.",
                "Если <code>user.role != \"admin\"</code>, dependency бросает <code>HTTPException(status_code=403)</code>.",
                "<code>403 Forbidden</code> означает: пользователь известен, но прав недостаточно.",
                "Если проверка пройдена, dependency возвращает user, и endpoint может спокойно выполнить admin-логику.",
            ],
        },
        {
            "title": "Что должен доказать тест или ручная проверка",
            "items": [
                "Обычный пользователь должен успешно логиниться, но получать <code>403</code> на <code>/api/admin</code>.",
                "Admin-пользователь должен получать <code>200</code> на <code>/api/admin</code>.",
                "Запрос без Bearer token должен получить <code>401</code>, потому что authentication не пройдена.",
                "Так ученик видит три разные ситуации: нет входа, вошёл без прав, вошёл с правами.",
            ],
        },
    ],
    "chapter08": [
        {
            "title": "Зачем нужно поле revoked_at",
            "body": "<code>revoked=True</code> говорит только факт: token отозван. <code>revoked_at</code> добавляет время, когда именно это произошло.",
            "items": [
                "Поле полезно для аудита: можно понять, когда пользователь вышел или когда token был заменён.",
                "<code>datetime | None</code> означает: у активного token-а времени отзыва нет, у отозванного - есть.",
                "<code>nullable=True</code> в базе соответствует этой идее: значение может быть пустым.",
                "Это поле должно появиться в SQLAlchemy-модели и в миграции, если БД уже существует.",
            ],
        },
        {
            "title": "Почему revoke лучше вынести в helper",
            "items": [
                "Refresh token отзывается в нескольких местах: при refresh rotation, ручном revoke и logout.",
                "Если в каждом месте писать <code>token.revoked = True</code> и <code>token.revoked_at = ...</code> вручную, легко забыть одно из полей.",
                "<code>revoke_token</code> делает оба действия вместе, поэтому поведение становится одинаковым.",
                "Helper принимает ORM-объект <code>RefreshToken</code>, меняет его поля, а commit остаётся у вызывающего кода.",
            ],
        },
        {
            "title": "Как меняется refresh flow",
            "items": [
                "Клиент отправляет старый refresh token в <code>/api/auth/refresh</code>.",
                "Сервер ищет token в таблице и проверяет, что он не отозван и не истёк.",
                "Старый token помечается как отозванный и получает <code>revoked_at</code>.",
                "После этого сервер создаёт новую пару: свежий access token и свежий refresh token.",
                "Если старый token попробуют использовать повторно, проверка <code>stored.revoked</code> должна вернуть ошибку.",
            ],
        },
        {
            "title": "Что проверять",
            "items": [
                "После refresh старый refresh token должен иметь <code>revoked=True</code> и непустой <code>revoked_at</code> в БД.",
                "После ручного <code>/api/auth/revoke</code> поле <code>revoked_at</code> тоже должно заполниться.",
                "После logout все активные refresh token-ы пользователя должны получить время отзыва.",
                "Тест должен смотреть не только HTTP status, но и состояние записи в базе.",
            ],
        },
    ],
    "chapter09": [
        {
            "title": "Где обрабатывать команду /who",
            "body": "Команда <code>/who</code> должна жить внутри receive loop WebSocket endpoint-а, сразу после получения текста от клиента и до broadcast.",
            "items": [
                "<code>message = await websocket.receive_text()</code> ждёт следующее сообщение текущего клиента.",
                "После этой строки можно проверить, является ли сообщение командой.",
                "<code>if message == \"/who\"</code> отделяет служебную команду от обычного текста чата.",
                "Команду нужно обработать до <code>manager.broadcast</code>, иначе она улетит всем как обычное сообщение.",
            ],
        },
        {
            "title": "Почему ответ отправляется только текущему клиенту",
            "items": [
                "<code>await websocket.send_json(...)</code> отправляет JSON именно в текущее соединение.",
                "<code>manager.broadcast(...)</code> рассылает payload всем активным соединениям.",
                "Количество подключений - это служебная информация для того, кто спросил. Остальным клиентам она не нужна.",
                "Так ученик видит разницу между личным ответом и общей рассылкой.",
            ],
        },
        {
            "title": "Откуда берётся count",
            "items": [
                "<code>manager.active_connections</code> - словарь всех открытых WebSocket-соединений.",
                "<code>len(manager.active_connections)</code> считает количество активных подключений прямо сейчас.",
                "Это учебная in-memory структура. Если запустить несколько процессов, у каждого будет свой словарь.",
                "Для одного учебного приложения на одном Uvicorn-процессе этого достаточно.",
            ],
        },
        {
            "title": "Как проверять",
            "items": [
                "Откройте один WebSocket-клиент и отправьте <code>/who</code>. Должен прийти JSON с <code>event: \"connections\"</code>.",
                "Откройте две вкладки и отправьте <code>/who</code> из одной. Ответ должен прийти только в эту вкладку.",
                "Отправьте обычный текст. Он должен по-прежнему прийти всем клиентам через broadcast.",
                "Если <code>/who</code> видят все вкладки, значит команда ошибочно отправляется через <code>broadcast</code>.",
            ],
        },
    ],
    "chapter10": [
        {
            "title": "Куда добавлять leave_room",
            "body": "<code>leave_room</code> - это Socket.IO event, поэтому он добавляется рядом с другими обработчиками <code>@sio.event</code>: <code>join_room</code>, <code>chat_message</code>, <code>direct_message</code>.",
            "items": [
                "<code>@sio.event</code> говорит Socket.IO: функция ниже обрабатывает событие с таким же именем, как функция.",
                "<code>async def leave_room(sid, data)</code> получает id подключения и payload события от клиента.",
                "<code>sid</code> нужен, чтобы удалить из комнаты именно текущее подключение.",
                "<code>data</code> нужен, чтобы прочитать имя комнаты, из которой клиент хочет выйти.",
            ],
        },
        {
            "title": "Как выбирается комната",
            "items": [
                "<code>room = data.get(\"room\", \"general\")</code> берёт комнату из payload.",
                "Значение <code>general</code> по умолчанию удобно для тестов: можно отправить пустой payload и всё равно получить предсказуемое поведение.",
                "Имя комнаты должно совпадать с тем, что используется в <code>join_room</code>.",
                "Если клиент вошёл в <code>python</code>, выходить тоже надо из <code>python</code>, иначе он останется подписанным на старую комнату.",
            ],
        },
        {
            "title": "Зачем две операции удаления",
            "items": [
                "<code>await sio.leave_room(sid, room)</code> удаляет подключение из внутренней комнаты Socket.IO.",
                "<code>socketio_rooms[room].discard(sid)</code> обновляет учебный словарь, который показывает состояние через <code>/api/chat/info</code>.",
                "Если забыть <code>sio.leave_room</code>, клиент всё ещё будет получать сообщения комнаты.",
                "Если забыть <code>discard</code>, реальная отправка может работать, но учебный endpoint будет показывать неправильное состояние.",
            ],
        },
        {
            "title": "Почему нужен ответ left_room",
            "items": [
                "<code>await sio.emit(\"left_room\", {\"room\": room}, to=sid)</code> отправляет подтверждение только клиенту, который вышел.",
                "Клиенту важно получить явный сигнал: сервер команду принял, комната изменена.",
                "Событие не рассылается всем, потому что это не сообщение чата, а служебное подтверждение.",
                "Проверять удобно на странице теста сокетов: подключиться, войти в комнату, выйти и увидеть <code>left_room</code> в логе.",
            ],
        },
    ],
    "chapter11": [
        {
            "title": "Где хранится роль",
            "body": "Роль должна попасть в JWT при создании token-а, а потом извлекаться сервером при Socket.IO connect. Клиент не должен сам объявлять себя admin в payload события.",
            "items": [
                "<code>LoginRequest</code> в учебном варианте может принимать username/password, а роль берётся из серверной demo-логики.",
                "<code>create_access_token</code> добавляет claim <code>role</code> в payload JWT.",
                "<code>jwt.encode</code> подписывает payload секретным ключом.",
                "После подписи клиент не может незаметно изменить <code>role</code>: подпись перестанет совпадать.",
            ],
        },
        {
            "title": "Как роль попадает в Socket.IO подключение",
            "items": [
                "Клиент передаёт token в Socket.IO <code>auth</code>, например <code>{ access_token: token }</code>.",
                "<code>connect</code> вызывает <code>authorize_socketio</code> до принятия пользовательских событий.",
                "<code>verify_user_token</code> декодирует JWT и возвращает данные пользователя, включая роль.",
                "Сервер сохраняет данные в словаре по <code>sid</code>, чтобы последующие events знали, кто подключён.",
            ],
        },
        {
            "title": "Как работает admin_message",
            "items": [
                "<code>admin_message</code> - отдельное Socket.IO событие, которому нужны права admin.",
                "Внутри handler-а сервер берёт пользователя по <code>sid</code>, а не из <code>data</code> клиента.",
                "Если <code>role != \"admin\"</code>, событие не выполняет admin-действие и может отправить отказ текущему клиенту.",
                "Если роль admin, сервер отправляет admin-сообщение выбранным получателям или текущему клиенту по логике главы.",
            ],
        },
        {
            "title": "Что проверять",
            "items": [
                "Подключение без token-а должно быть отклонено на этапе <code>connect</code>.",
                "Подключение с обычным пользователем должно проходить, но <code>admin_message</code> должен быть запрещён.",
                "Подключение с admin token-ом должно пройти и разрешить <code>admin_message</code>.",
                "Так ученик видит разницу между проверкой token-а и проверкой прав на конкретное событие.",
            ],
        },
    ],
    "chapter12": [
        {
            "title": "Почему удаление группы начинается с service layer",
            "body": "Удаление группы - бизнес-операция. Её должны использовать REST endpoint, Socket.IO event и тесты, поэтому логика живёт в <code>ChatService.delete_group</code>, а не копируется в каждом обработчике.",
            "items": [
                "<code>def delete_group(self, group_id: int)</code> принимает id группы, потому что это главный входной параметр операции.",
                "<code>self.db.get(ChatGroup, group_id)</code> ищет группу по primary key.",
                "Если группы нет, сервис бросает <code>HTTPException(status_code=404)</code>. Так REST сразу получит правильный HTTP-ответ.",
                "Если группа есть, сервис удаляет связанные сообщения и саму группу в одной транзакции.",
            ],
        },
        {
            "title": "Почему сначала удаляются сообщения",
            "items": [
                "Сообщения ссылаются на группу через <code>group_id</code>.",
                "Если удалить группу, а сообщения оставить, в базе появятся записи, которые указывают на несуществующую группу.",
                "В учебном решении выбран простой вариант: при удалении группы удаляются и её сообщения.",
                "<code>self.db.query(Message).filter(Message.group_id == group_id).delete()</code> удаляет все сообщения выбранной группы.",
                "После этого <code>self.db.delete(group)</code> удаляет саму группу, а <code>self.db.commit()</code> сохраняет изменения.",
            ],
        },
        {
            "title": "Как REST endpoint использует сервис",
            "items": [
                "<code>@fastapi_app.delete(\"/api/chat/groups/{group_id}\", status_code=204)</code> регистрирует HTTP DELETE endpoint.",
                "<code>group_id</code> берётся из URL path.",
                "<code>service: ChatService = Depends(get_chat_service)</code> даёт endpoint-у готовый сервис с DB session.",
                "<code>service.delete_group(group_id)</code> выполняет всю бизнес-логику.",
                "Функция ничего не возвращает, потому что status <code>204 No Content</code> означает успешное удаление без тела ответа.",
            ],
        },
        {
            "title": "Как Socket.IO event использует тот же сервис",
            "items": [
                "<code>async def delete_group(sid, data)</code> получает payload от Socket.IO клиента.",
                "<code>group_id = int(data[\"group_id\"])</code> явно превращает значение в число, потому что из JSON оно может прийти строкой.",
                "<code>with SessionLocal() as db</code> открывает короткую SQLAlchemy session на время события.",
                "<code>ChatService(db)</code> создаёт тот же сервис, который использует REST API.",
                "<code>await sio.emit(\"group_deleted\", {\"group_id\": group_id})</code> сообщает подключённым клиентам, что группа удалена.",
            ],
        },
        {
            "title": "Что доказывает тест",
            "items": [
                "<code>make_sqlite_override</code> подменяет обычную БД тестовой SQLite-БД, чтобы тест был изолированным.",
                "Тест создаёт группу, отправляет в неё сообщение, удаляет группу и потом запрашивает сообщения этой группы.",
                "Ожидаемый результат - пустой список. Это доказывает, что удаление затронуло не только группу, но и связанные сообщения.",
                "<code>app.dependency_overrides.clear()</code> в <code>finally</code> очищает подмену, чтобы она не влияла на другие тесты.",
            ],
        },
    ],
}


ANSWER_DEEP_DIVES = {
    "chapter01": [
        {
            "title": "Читаем полный ответ сверху вниз",
            "items": [
                "Сначала идут импорты. Они нужны до создания приложения, потому что Python должен знать, что такое <code>FastAPI</code>, <code>BaseModel</code>, <code>Header</code> и <code>HTTPException</code>.",
                "Потом создаётся <code>app = FastAPI(...)</code>. Это центральный объект: все декораторы <code>@app.get</code> и <code>@app.post</code> записывают маршруты именно в него.",
                "Дальше идут Pydantic-модели. В этой главе важна <code>CalculationRequest</code>: она превращает JSON body в Python-объект с полями <code>a</code> и <code>b</code>.",
                "После моделей идут middleware и endpoint-ы. Middleware работает вокруг всех маршрутов, а endpoint-ы отвечают за конкретные URL.",
                "Новый <code>power</code> ставится рядом с другими операциями калькулятора, потому что он использует тот же request body и тот же формат ответа.",
                "Блок <code>if __name__ == \"__main__\"</code> находится внизу, потому что это только удобный способ запустить файл напрямую. Он не участвует в обработке конкретного запроса.",
            ],
        },
        {
            "title": "Что происходит при POST /api/calculator/power",
            "items": [
                "Клиент отправляет HTTP method <code>POST</code>, path <code>/api/calculator/power</code> и JSON body, например <code>{\"a\": 2, \"b\": 3}</code>.",
                "Uvicorn принимает сетевой запрос и передаёт его в FastAPI-приложение <code>app</code>.",
                "FastAPI ищет маршрут, который совпадает и по method, и по path. Для этой задачи это декоратор <code>@app.post(\"/api/calculator/power\")</code>.",
                "Перед вызовом функции FastAPI смотрит на параметр <code>request: CalculationRequest</code> и понимает: нужно прочитать JSON body.",
                "Pydantic проверяет, что в body есть числа <code>a</code> и <code>b</code>. Если данных нет или тип неправильный, функция <code>power</code> даже не запускается.",
                "Если validation прошла, внутри функции <code>request.a</code> и <code>request.b</code> уже обычные Python-значения.",
                "Функция возвращает словарь, а FastAPI превращает его в JSON response.",
            ],
        },
        {
            "title": "Почему нельзя просто вернуть число",
            "items": [
                "Можно было бы вернуть только <code>8</code>, но тогда формат ответа отличался бы от остальных операций.",
                "В учебном API все операции возвращают объект с <code>result</code> и <code>operation</code>. Это контракт между сервером и клиентом.",
                "Контракт важнее удобства одной функции: клиент может одинаково читать <code>result</code> у add, divide и power.",
                "<code>operation</code> помогает увидеть, какой endpoint сработал, особенно когда ученик проверяет разные запросы в Swagger.",
                "Если в будущем появится frontend, ему будет проще рисовать историю операций, потому что ответ у всех операций одинаковой формы.",
            ],
        },
    ],
    "chapter02": [
        {
            "title": "Читаем DI-решение сверху вниз",
            "items": [
                "Сначала в файле уже есть imports: <code>logging</code>, <code>Depends</code>, <code>FastAPI</code> и другие вещи главы.",
                "Потом создаются объекты и функции, которые могут быть зависимостями: logger, settings, singleton service, request-scoped service.",
                "<code>get_log_prefix</code> добавляется в эту же зону, потому что это provider: маленькая функция, которая готовит значение для endpoint-а.",
                "Provider не обязан знать про HTTP. Он просто возвращает строку. Это делает код проще для проверки и переиспользования.",
                "Endpoint <code>pretty_log</code> добавляется в секцию маршрутов <code>/api/dependency-injection/*</code>.",
                "В сигнатуре endpoint-а рядом стоят обычный query-параметр <code>message</code> и dependency-параметры <code>prefix</code>, <code>app_logger</code>.",
            ],
        },
        {
            "title": "Что FastAPI делает перед входом в pretty_log",
            "items": [
                "FastAPI видит обычный параметр <code>message: str = \"hello\"</code> и ищет его в query string.",
                "FastAPI видит <code>Depends(get_log_prefix)</code> и вызывает <code>get_log_prefix()</code> сам.",
                "Результат <code>\"[DI LOG]\"</code> кладётся в переменную <code>prefix</code>.",
                "FastAPI видит <code>Depends(get_logger)</code>, вызывает logger dependency и кладёт результат в <code>app_logger</code>.",
                "Только после подготовки всех параметров вызывается тело функции <code>pretty_log</code>.",
                "Поэтому внутри endpoint-а уже не надо думать, откуда взять prefix и logger. Они уже пришли готовыми.",
            ],
        },
        {
            "title": "Почему это учебный пример DI, а не просто лишняя функция",
            "items": [
                "Да, для строки <code>[DI LOG]</code> dependency выглядит слишком простой. Именно поэтому новичку легко увидеть механизм без лишней бизнес-логики.",
                "Тот же принцип потом применяется к базе данных, текущему пользователю, настройкам, сервисам и проверкам прав.",
                "Endpoint не создаёт зависимость сам. Он объявляет, что ему нужно, а FastAPI готовит это снаружи.",
                "Так код легче тестировать: dependency можно заменить, не переписывая endpoint.",
                "Если ученик поймёт этот пример, ему проще будет понять <code>get_db</code>, <code>get_current_user</code> и service dependencies в следующих главах.",
            ],
        },
    ],
    "chapter03": [
        {
            "title": "Читаем HTTP-интеграцию сверху вниз",
            "items": [
                "<code>import httpx</code> нужен, потому что исходящий HTTP-запрос делает не FastAPI, а клиентская библиотека httpx.",
                "<code>JSONPLACEHOLDER</code> вынесен в константу, чтобы внешний адрес не был размазан по методам сервиса.",
                "<code>CreatePostRequest</code> относится к другому endpoint-у главы, но остаётся в полном ответе, чтобы файл был целиком рабочим.",
                "<code>ExternalApiService</code> собирает в одном месте все обращения к JSONPlaceholder.",
                "<code>get_external_api_service</code> - dependency, которая отдаёт endpoint-ам готовый service object.",
                "<code>map_http_error</code> стоит отдельно, потому что ошибку внешнего API надо превращать в ошибку вашего API единообразно.",
            ],
        },
        {
            "title": "Что происходит при запросе comments",
            "items": [
                "Клиент вызывает локальный URL <code>/api/http-client/post/1/comments</code>, а не внешний JSONPlaceholder напрямую.",
                "FastAPI берёт <code>post_id=1</code> из path.",
                "FastAPI вызывает <code>get_external_api_service</code> и передаёт результат в параметр <code>service</code>.",
                "Endpoint вызывает <code>await service.get_post_comments(post_id)</code>.",
                "Сервис открывает <code>httpx.AsyncClient</code> с <code>base_url=JSONPLACEHOLDER</code>.",
                "Сервис отправляет внешний запрос на <code>/posts/1/comments</code>.",
                "Внешний JSON возвращается из сервиса в endpoint, а endpoint отдаёт его клиенту.",
            ],
        },
        {
            "title": "Зачем нужен try/except вокруг await",
            "items": [
                "Внешний сервис может быть недоступен, вернуть 404, 500 или ответить слишком медленно.",
                "Если не перехватить <code>httpx.HTTPError</code>, клиент вашего API увидит внутреннюю ошибку приложения.",
                "<code>except httpx.HTTPError as error</code> ловит сетевые ошибки и ошибки status code после <code>raise_for_status()</code>.",
                "<code>map_http_error(error)</code> превращает техническую ошибку httpx в понятный <code>HTTPException</code> FastAPI.",
                "<code>from error</code> сохраняет связь исключений для отладки, но клиенту наружу отдаётся аккуратный HTTP-ответ.",
            ],
        },
    ],
    "chapter04": [
        {
            "title": "Читаем error handling сверху вниз",
            "items": [
                "Imports нужны для трёх разных задач: FastAPI-маршруты, JSON-ответы и типы ошибок.",
                "<code>app = FastAPI(...)</code> создаёт приложение, на которое потом навешиваются middleware, handlers и endpoints.",
                "Custom exception classes объявляются до handlers, чтобы decorators могли сослаться на эти классы.",
                "Middleware стоит отдельно, потому что оно не ловит одну конкретную ошибку, а оборачивает каждый запрос.",
                "Exception handlers стоят до или после endpoint-ов не так критично, но новичку проще читать их до endpoint-ов: сначала правила ошибок, потом места, где ошибки возникают.",
                "Endpoint <code>not_ready</code> нужен только для демонстрации: он специально бросает <code>NotReadyError</code>.",
            ],
        },
        {
            "title": "Что происходит при raise NotReadyError",
            "items": [
                "Endpoint начинает выполняться и доходит до строки <code>raise NotReadyError()</code>.",
                "Обычный <code>return</code> уже не выполняется: исключение прерывает функцию.",
                "FastAPI смотрит, есть ли handler для типа <code>NotReadyError</code>.",
                "Он находит функцию с decorator <code>@app.exception_handler(NotReadyError)</code>.",
                "Handler возвращает <code>JSONResponse</code> со status <code>503</code>.",
                "Middleware получает уже готовый ответ, добавляет header времени обработки и отдаёт его клиенту.",
            ],
        },
        {
            "title": "Что сломается, если убрать отдельные части",
            "items": [
                "Если убрать класс <code>NotReadyError</code>, endpoint не сможет его бросить.",
                "Если убрать decorator <code>@app.exception_handler(NotReadyError)</code>, ошибка станет обычной необработанной ошибкой.",
                "Если вернуть обычный dict из handler без <code>JSONResponse</code>, будет сложнее явно задать status <code>503</code>.",
                "Если поставить status <code>500</code>, клиент не поймёт, что это временная ожидаемая недоступность.",
                "Если не добавить endpoint для проверки, ученику придётся искусственно вызывать ошибку из тестов, а руками проверить будет сложнее.",
            ],
        },
    ],
    "chapter05": [
        {
            "title": "Читаем простой Jinja-ответ сверху вниз",
            "items": [
                "<code>Path</code> нужен только для аккуратного пути к папке <code>templates</code> в этой HTML-главе.",
                "<code>LESSON_TOPICS</code> и <code>HOMEWORK_STEPS</code> - обычные списки Python. Они могли бы прийти из базы данных, но для обучения список проще.",
                "<code>FastAPI(...)</code> создаёт приложение так же, как в API-главах.",
                "<code>Jinja2Templates(...)</code> говорит FastAPI, где искать HTML-файлы.",
                "<code>demo_context</code> собирает все данные страницы в одном месте, чтобы endpoint оставался коротким.",
            ],
        },
        {
            "title": "Что происходит при GET /jinja-demo",
            "items": [
                "Браузер просит адрес <code>/jinja-demo</code>.",
                "FastAPI находит функцию <code>jinja_demo</code> по decorator <code>@app.get(\"/jinja-demo\")</code>.",
                "Функция вызывает <code>demo_context(request)</code> и получает словарь с <code>title</code>, <code>student_name</code>, <code>topics</code>, <code>homework_steps</code> и <code>show_hint</code>.",
                "<code>TemplateResponse</code> берёт файл <code>jinja_demo.html</code>.",
                "Когда Jinja2 видит <code>{{ title }}</code>, он ищет ключ <code>title</code> в словаре и печатает значение.",
                "Когда Jinja2 видит <code>{% if show_hint %}</code>, он проверяет значение <code>show_hint</code>. У нас там <code>True</code>, поэтому подсказка появляется.",
                "Когда Jinja2 видит <code>{% for step in homework_steps %}</code>, он повторяет HTML для каждого пункта списка.",
            ],
        },
        {
            "title": "Почему for лучше копирования HTML",
            "items": [
                "Без цикла пришлось бы руками писать три одинаковых <code>&lt;li&gt;</code>.",
                "Если завтра пунктов станет пять, без цикла придётся редактировать HTML вручную.",
                "С циклом меняется только Python-список. Шаблон остаётся таким же.",
                "Это главный смысл серверных шаблонов: данные живут в Python, а внешний вид живёт в HTML-файле.",
                "Для новичка важно запомнить разделение: endpoint не должен собирать HTML строками, а шаблон не должен делать сложную бизнес-логику.",
            ],
        },
    ],
    "chapter06": [
        {
            "title": "Читаем SQLModel-ответ сверху вниз",
            "items": [
                "Imports SQLModel нужны для <code>SQLModel</code>, <code>Field</code>, <code>Session</code>, <code>select</code> и настроек колонок.",
                "<code>DATABASE_URL</code> задаёт адрес базы. По умолчанию используется SQLite-файл главы.",
                "<code>engine</code> знает, как подключаться к базе, а <code>Session(engine)</code> открывает рабочую сессию.",
                "<code>SQLModel.metadata</code> знает, какие таблицы описаны через <code>table=True</code>.",
                "<code>ProductBase</code> хранит общие поля, чтобы не копировать <code>name</code>, <code>category</code>, <code>description</code>, <code>price</code> и <code>stock</code> в несколько классов.",
                "<code>Product</code> наследуется от <code>ProductBase</code> и описывает таблицу, потому что у него есть <code>table=True</code>.",
                "<code>ProductCreate</code> и <code>ProductRead</code> тоже наследуются от <code>ProductBase</code>, но остаются JSON-схемами, потому что у них нет <code>table=True</code>.",
                "<code>ProductUpdate</code> стоит отдельно, потому что все его поля optional для частичного обновления.",
                "Endpoint-ы не должны напрямую знать все детали таблицы. Они работают через session и модели.",
            ],
        },
        {
            "title": "Почему category проходит через несколько классов",
            "items": [
                "<code>ProductBase.category</code> - одно место, где описано общее поле категории.",
                "SQLModel-таблица наследует это поле: без <code>Product(ProductBase, table=True)</code> колонка не появится в таблице.",
                "Create schema наследует это поле: без <code>ProductCreate(ProductBase)</code> клиент не сможет прислать категорию.",
                "Update schema отвечает за частичное изменение: без <code>ProductUpdate.category</code> категорию нельзя будет обновить.",
                "Read schema наследует это поле: без <code>ProductRead(ProductBase)</code> клиент не увидит категорию в ответе.",
                "Migration отвечает за реальную схему уже существующей базы: без Alembic production-база не узнает про новую колонку.",
            ],
        },
        {
            "title": "Что происходит при создании продукта",
            "items": [
                "Клиент отправляет <code>POST /api/products</code> с JSON body.",
                "FastAPI валидирует body через <code>ProductCreate</code>.",
                "Endpoint создаёт ORM-объект <code>Product(**request.model_dump())</code> или аналогичную конструкцию.",
                "SQLModel Session добавляет объект через <code>db.add</code>.",
                "<code>db.commit()</code> сохраняет строку в SQLite.",
                "<code>db.refresh(product)</code> подтягивает id и значения по умолчанию из базы.",
                "FastAPI возвращает объект через <code>ProductRead</code>, и в JSON появляется <code>category</code>.",
            ],
        },
    ],
    "chapter07": [
        {
            "title": "Читаем auth-ответ сверху вниз",
            "items": [
                "Imports нужны для JWT, password hashing, OAuth2 dependency, Pydantic-моделей и HTTP-ошибок.",
                "Константы <code>SECRET_KEY</code>, <code>ALGORITHM</code> и время жизни token-а определяют, как создаётся JWT.",
                "<code>pwd_context</code> отвечает за hash пароля. Даже в учебнике пароль не должен сравниваться как обычная строка.",
                "Pydantic-модели описывают вход и выход auth endpoint-ов.",
                "<code>create_access_token</code> собирает payload и подписывает JWT.",
                "<code>get_current_user</code> превращает Bearer token обратно в пользователя.",
                "<code>require_admin</code> добавляет вторую проверку: не просто вошёл, а вошёл с нужной ролью.",
            ],
        },
        {
            "title": "Что происходит при запросе /api/admin",
            "items": [
                "Клиент отправляет header <code>Authorization: Bearer ...</code>.",
                "OAuth2 dependency достаёт token из header-а.",
                "<code>get_current_user</code> декодирует token, проверяет подпись и ищет пользователя.",
                "Если token плохой, запрос заканчивается <code>401 Unauthorized</code>.",
                "Если token хороший, FastAPI передаёт user в <code>require_admin</code>.",
                "Если user не admin, dependency бросает <code>403 Forbidden</code>.",
                "Если user admin, endpoint <code>admin_area</code> выполняется и возвращает успешный JSON.",
            ],
        },
        {
            "title": "Почему 401 и 403 разные",
            "items": [
                "<code>401</code> означает: сервер не смог подтвердить личность пользователя.",
                "<code>403</code> означает: сервер знает пользователя, но не разрешает действие.",
                "Для новичка это важная граница: authentication проверяет вход, authorization проверяет права.",
                "Если всё возвращать как 401, будет непонятно, пользователь не вошёл или вошёл без нужной роли.",
                "Если всё возвращать как 403, клиент не поймёт, что ему сначала нужно получить token.",
            ],
        },
    ],
    "chapter08": [
        {
            "title": "Читаем refresh-token решение сверху вниз",
            "items": [
                "Imports включают JWT, hashing, SQLAlchemy, datetime и secrets, потому что глава работает и с token-ами, и с базой.",
                "Таблица <code>User</code> хранит пользователей, таблица <code>RefreshToken</code> хранит долгие refresh token-ы.",
                "<code>revoked</code> отвечает на вопрос “можно ли использовать token”.",
                "<code>revoked_at</code> отвечает на вопрос “когда token перестал быть действительным”.",
                "Helpers создают access/refresh token-ы и отзывают refresh token-ы.",
                "Endpoint-ы <code>login</code>, <code>refresh</code>, <code>revoke</code>, <code>logout</code> используют одни и те же helpers.",
            ],
        },
        {
            "title": "Что происходит при refresh rotation",
            "items": [
                "Клиент присылает старый refresh token.",
                "Сервер ищет его в таблице <code>refresh_tokens</code>.",
                "Сервер проверяет три условия: token найден, не отозван, срок действия не закончился.",
                "Если проверка не прошла, сервер возвращает <code>401</code>.",
                "Если проверка прошла, старый token получает <code>revoked=True</code> и <code>revoked_at=datetime.utcnow()</code>.",
                "Сервер создаёт новый access token и новый refresh token.",
                "Клиент должен сохранить новую пару и больше не использовать старый refresh token.",
            ],
        },
        {
            "title": "Почему revoked_at важен для обучения",
            "items": [
                "Без <code>revoked_at</code> ученик видит только boolean и не понимает историю события.",
                "С <code>revoked_at</code> можно открыть БД и увидеть, когда именно token был отозван.",
                "Это помогает отличить logout, manual revoke и refresh rotation, если потом добавить reason.",
                "Так появляется привычка хранить не только состояние, но и audit-информацию.",
                "В production такие поля помогают расследовать подозрительные повторные использования refresh token-а.",
            ],
        },
    ],
    "chapter09": [
        {
            "title": "Читаем WebSocket-ответ сверху вниз",
            "items": [
                "Imports нужны для <code>WebSocket</code>, <code>WebSocketDisconnect</code> и генерации id через <code>uuid4</code>.",
                "<code>ConnectionManager</code> держит словарь активных подключений.",
                "Метод <code>connect</code> принимает соединение, сохраняет его и отправляет клиенту служебное сообщение.",
                "Метод <code>disconnect</code> удаляет соединение, когда клиент ушёл.",
                "Метод <code>broadcast</code> проходит по всем соединениям и отправляет одинаковый payload.",
                "WebSocket endpoint содержит бесконечный receive loop, потому что соединение живёт дольше одного HTTP request.",
            ],
        },
        {
            "title": "Что происходит внутри receive loop",
            "items": [
                "<code>while True</code> означает: пока соединение открыто, сервер ждёт новые сообщения.",
                "<code>message = await websocket.receive_text()</code> останавливает выполнение до следующего сообщения клиента.",
                "После получения текста сервер проверяет, является ли он командой <code>/who</code>.",
                "Если это <code>/who</code>, сервер отвечает только текущему <code>websocket</code>.",
                "Если это обычный текст, сервер вызывает <code>manager.broadcast</code>.",
                "Если клиент закрывает вкладку, возникает <code>WebSocketDisconnect</code>, и endpoint переходит в cleanup.",
            ],
        },
        {
            "title": "Почему /who не должен быть broadcast",
            "items": [
                "<code>/who</code> - команда управления, а не сообщение чата.",
                "Если отправить её всем, другие пользователи увидят техническую команду, которую они не вводили.",
                "Личный ответ через <code>websocket.send_json</code> показывает, что сервер может отвечать не только broadcast-ом.",
                "Так глава готовит ученика к личным сообщениям, комнатам и авторизации в следующих главах.",
                "Обычные сообщения всё равно остаются broadcast, поэтому существующее поведение чата не ломается.",
            ],
        },
    ],
    "chapter10": [
        {
            "title": "Читаем Socket.IO-ответ сверху вниз",
            "items": [
                "<code>sio = socketio.AsyncServer(...)</code> создаёт сервер событий Socket.IO.",
                "<code>fastapi_app = FastAPI(...)</code> остаётся для обычных HTTP endpoint-ов главы.",
                "<code>app = socketio.ASGIApp(...)</code> объединяет Socket.IO и FastAPI в одно ASGI-приложение.",
                "<code>socketio_clients</code> хранит имена клиентов по <code>sid</code>.",
                "<code>socketio_rooms</code> хранит учебное состояние комнат, чтобы его можно было посмотреть через HTTP.",
                "Все функции с <code>@sio.event</code> - обработчики событий, которые клиент отправляет через Socket.IO.",
            ],
        },
        {
            "title": "Что происходит при leave_room",
            "items": [
                "Клиент отправляет событие <code>leave_room</code> с payload, например <code>{\"room\": \"python\"}</code>.",
                "Socket.IO вызывает Python-функцию <code>leave_room(sid, data)</code>.",
                "Функция читает комнату из <code>data</code>. Если комнаты нет, берёт <code>general</code>.",
                "<code>await sio.leave_room(sid, room)</code> меняет внутреннее состояние Socket.IO.",
                "<code>socketio_rooms[room].discard(sid)</code> меняет учебный словарь, который виден в <code>/api/chat/info</code>.",
                "<code>await sio.emit(\"left_room\", ...)</code> отправляет подтверждение текущему клиенту.",
            ],
        },
        {
            "title": "Почему здесь есть await",
            "items": [
                "Socket.IO операции могут делать async-ввод/вывод: отправлять события, менять комнату, взаимодействовать с transport.",
                "Поэтому handler объявлен как <code>async def</code>.",
                "<code>await sio.leave_room</code> и <code>await sio.emit</code> дают event loop возможность не блокировать другие подключения.",
                "Если забыть <code>await</code>, операция может не выполниться вовремя или появятся warnings про coroutine.",
                "Для real-time кода это особенно важно: один медленный клиент не должен останавливать остальных.",
            ],
        },
    ],
    "chapter11": [
        {
            "title": "Читаем авторизованный Socket.IO ответ сверху вниз",
            "items": [
                "JWT-константы и helpers идут в начале, потому что они нужны и HTTP login, и Socket.IO connect.",
                "<code>create_access_token</code> создаёт token с username и role.",
                "<code>verify_user_token</code> делает обратное: проверяет token и возвращает данные пользователя.",
                "<code>authorize_socketio</code> адаптирует проверку JWT под Socket.IO auth payload.",
                "<code>authorized_clients</code> хранит подтверждённых пользователей по <code>sid</code>.",
                "Socket.IO events после connect уже не должны доверять данным клиента о username/role.",
            ],
        },
        {
            "title": "Что происходит при connect",
            "items": [
                "Клиент подключается и передаёт <code>auth: { access_token: token }</code>.",
                "Socket.IO вызывает <code>connect(sid, environ, auth)</code>.",
                "<code>authorize_socketio</code> достаёт token из <code>auth</code>.",
                "<code>verify_user_token</code> проверяет подпись и срок действия JWT.",
                "Если token плохой, <code>connect</code> возвращает <code>False</code>, и подключение отклоняется.",
                "Если token хороший, сервер сохраняет пользователя в <code>authorized_clients</code> и отправляет <code>authorized</code>.",
            ],
        },
        {
            "title": "Почему admin_message проверяется отдельно",
            "items": [
                "Успешный connect означает только “пользователь известен”. Это authentication.",
                "Право отправлять admin-событие - отдельное правило. Это authorization.",
                "Обычный пользователь может быть валидно подключён, но всё равно не иметь права на <code>admin_message</code>.",
                "Поэтому handler события должен проверить <code>role</code> перед выполнением действия.",
                "Это тот же принцип, что <code>require_admin</code> в REST-главе, только применённый к Socket.IO event.",
            ],
        },
    ],
    "chapter12": [
        {
            "title": "Читаем итоговое решение сверху вниз",
            "items": [
                "Сначала идут imports для FastAPI, SQLAlchemy, Pydantic, datetime и Socket.IO.",
                "Потом создаются engine и SessionLocal, потому что они нужны всем операциям с БД.",
                "ORM-модели <code>ChatGroup</code> и <code>Message</code> описывают таблицы.",
                "Pydantic DTO описывают JSON-ответы REST API.",
                "<code>ChatService</code> содержит бизнес-логику: создать группу, отправить сообщение, получить сообщения, удалить группу.",
                "REST endpoint-ы вызывают service через dependency.",
                "Socket.IO events тоже создают service, но открывают session вручную на время события.",
            ],
        },
        {
            "title": "Что происходит при DELETE /api/chat/groups/{group_id}",
            "items": [
                "Клиент вызывает HTTP DELETE endpoint с id группы в URL.",
                "FastAPI достаёт <code>group_id</code> из path.",
                "Dependency <code>get_chat_service</code> создаёт service с DB session.",
                "Endpoint вызывает <code>service.delete_group(group_id)</code>.",
                "Service ищет группу. Если её нет, возвращается <code>404</code>.",
                "Service удаляет сообщения этой группы, потом саму группу, потом делает commit.",
                "Endpoint возвращает status <code>204</code>, потому что удаление прошло успешно и тело ответа не нужно.",
            ],
        },
        {
            "title": "Что происходит при Socket.IO delete_group",
            "items": [
                "Клиент отправляет Socket.IO event <code>delete_group</code> с <code>group_id</code>.",
                "Handler получает <code>data</code> и превращает <code>group_id</code> в int.",
                "Handler открывает SQLAlchemy session через <code>with SessionLocal() as db</code>.",
                "Handler создаёт <code>ChatService(db)</code> и вызывает тот же <code>delete_group</code>.",
                "После успешного удаления сервер отправляет событие <code>group_deleted</code>.",
                "REST и Socket.IO используют одну бизнес-логику, поэтому поведение не расходится.",
            ],
        },
        {
            "title": "Почему тест устроен именно так",
            "items": [
                "Тест сначала подменяет production-БД на тестовую через <code>dependency_overrides</code>.",
                "Потом создаёт группу через настоящий REST endpoint, а не руками через SQLAlchemy.",
                "Потом создаёт сообщение этой группы, чтобы проверить не пустой случай.",
                "Потом удаляет группу через новый DELETE endpoint.",
                "Потом запрашивает сообщения группы и ожидает пустой список.",
                "Так тест проверяет весь путь: API -> dependency -> service -> database -> API response.",
            ],
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
    "chapter03": [
        "Сначала проверьте внешний сервис без своего кода: откройте <code>https://jsonplaceholder.typicode.com/posts/1/comments</code> в браузере или выполните curl.",
        "Посмотрите на JSON: это список комментариев, у каждого есть <code>postId</code>, <code>id</code>, <code>name</code>, <code>email</code> и <code>body</code>.",
        "После этого добавляйте метод в <code>ExternalApiService</code>. Метод должен обращаться именно к внешнему пути <code>/posts/{post_id}/comments</code>.",
        "Не возвращайте локальный список и не копируйте пример JSON в код. Ваш FastAPI endpoint должен быть прокладкой между клиентом и открытым внешним API.",
        "В endpoint-е используйте существующую dependency <code>get_external_api_service</code>, чтобы сохранить учебную архитектуру главы.",
        "Проверьте два сценария: внешний URL напрямую и ваш локальный endpoint через Swagger.",
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
        ("Внешний API", "Перед кодом проверьте <code>https://jsonplaceholder.typicode.com/posts/1/comments</code> напрямую в браузере или curl."),
        ("GET /api/http-client/post/1/comments", "Ваш endpoint возвращает список комментариев из открытого тестового API JSONPlaceholder."),
        ("Service layer", "Endpoint вызывает метод <code>ExternalApiService.get_post_comments</code>, а не возвращает локальную заглушку."),
        ("Ошибки", "HTTP-ошибки внешнего API проходят через общий <code>map_http_error</code>."),
    ],
    "chapter04": [
        ("GET /api/error-demo/not-ready", "Возвращается HTTP 503."),
        ("JSON ошибки", "Ответ содержит сообщение <code>Сервис временно недоступен</code> и path запроса."),
        ("Остальные endpoint-ы", "Успешные endpoint-ы продолжают возвращать HTTP 200."),
    ],
    "chapter05": [
        ("GET /jinja-demo", "На странице появился блок <code>Домашние шаги</code>."),
        ("homework_steps", "Список приходит из Python context, а не написан вручную тремя отдельными HTML-строками."),
        ("for", "Пункты выводятся через <code>{% for step in homework_steps %}</code> и <code>{% endfor %}</code>."),
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
            "Самая простая схема такая: Python создаёт словарь, Jinja2 берёт значения из словаря и вставляет их в HTML.",
            "В этой главе мы специально не трогаем формы, регистрацию и сложную валидацию. Сначала нужно понять переменные, <code>if</code> и <code>for</code>.",
        ],
        "line_by_line": [
            ("<code>LESSON_TOPICS</code>", "Обычный Python-список словарей. Его удобно выводить циклом в HTML."),
            ("<code>templates.TemplateResponse(...)</code>", "Говорим FastAPI: возьми HTML-файл, подставь данные и верни готовую страницу."),
            ("<code>\"topics\": LESSON_TOPICS</code>", "Ключ <code>topics</code> станет доступен в шаблоне как переменная <code>topics</code>."),
            ("<code>{{ title }}</code>", "Две фигурные скобки печатают значение переменной."),
            ("<code>{% if show_hint %}</code>", "Конструкция с процентами не печатает текст, а управляет логикой шаблона."),
            ("<code>{% for topic in topics %}</code>", "Цикл берёт список <code>topics</code> и по очереди кладёт каждый элемент в переменную <code>topic</code>."),
        ],
        "mistakes": [
            "Забыть передать <code>request</code> в context. Для Starlette/FastAPI templates он нужен.",
            "Назвать ключ в Python <code>homework_steps</code>, а в шаблоне случайно написать <code>homework_step</code>. Jinja2 не найдёт такую переменную.",
            "Писать в шаблоне Python-синтаксис <code>for step in homework_steps:</code>. В Jinja2 нужно <code>{% for step in homework_steps %}</code>.",
        ],
    },
    "chapter06": {
        "plain": [
            "База данных хранит данные дольше, чем живёт один запрос. SQLModel помогает работать с таблицами как с Python-классами.",
            "SQLModel построен поверх SQLAlchemy и Pydantic: поэтому он умеет и таблицы описывать, и JSON проверять.",
            "Session - это рабочая область для операций с БД. Через неё мы добавляем, читаем, сохраняем и удаляем данные.",
            "Отдельные модели <code>ProductCreate</code>, <code>ProductUpdate</code>, <code>ProductRead</code> нужны, чтобы входной и выходной JSON были понятными.",
        ],
        "line_by_line": [
            ("<code>class Product(SQLModel, table=True)</code>", "Это SQLModel-класс, который станет таблицей <code>products</code>."),
            ("<code>id: int | None = Field(default=None, primary_key=True)</code>", "Первичный ключ. При создании продукта id ещё нет, поэтому стоит <code>None</code>."),
            ("<code>price: Decimal = Field(sa_column=Column(Numeric(10, 2)))</code>", "Для денег используем SQLAlchemy-колонку <code>Numeric</code>, но подключаем её через SQLModel <code>Field</code>."),
            ("<code>class ProductCreate(SQLModel)</code>", "Модель JSON body для создания продукта. Это не таблица, потому что нет <code>table=True</code>."),
            ("<code>def get_db()</code>", "Dependency-функция, которая выдаёт SQLModel Session на время запроса."),
            ("<code>with Session(engine) as db</code>", "Создаём новую Session и автоматически закрываем её после запроса."),
            ("<code>yield db</code>", "Отдаём Session endpoint-у."),
            ("<code>response_model=ProductRead</code>", "FastAPI отдаст наружу только поля, описанные в модели ответа."),
            ("<code>Product(**request.model_dump())</code>", "Берём проверенные поля из SQLModel request-модели и создаём объект таблицы."),
            ("<code>db.add(product)</code>", "Говорим Session: этот объект нужно вставить в таблицу."),
            ("<code>db.commit()</code>", "Фактически сохраняем изменения в базе."),
            ("<code>db.refresh(product)</code>", "Обновляем объект, чтобы получить id, выданный базой."),
            ("<code>db.exec(select(Product))</code>", "SQLModel-способ выполнить SELECT-запрос и получить продукты."),
            ("<code>alembic revision -m \"add product field\"</code>", "Создаёт файл миграции, но ещё не меняет базу."),
            ("<code>alembic upgrade head</code>", "Применяет миграции и реально меняет структуру базы."),
        ],
        "mistakes": [
            "Создать объект, но забыть <code>db.commit()</code>: данные не сохранятся.",
            "Поставить <code>table=True</code> на модель запроса <code>ProductCreate</code>. Тогда SQLModel решит, что это ещё одна таблица.",
            "Забыть добавить поле в <code>ProductRead</code>: в базе оно будет, но клиент его не увидит.",
            "Создать файл миграции, но забыть <code>alembic upgrade head</code>: код уже ждёт новую колонку, а база ещё старая.",
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
        "Разделяйте три слоя в голове: SQLModel-таблица описывает хранение, SQLModel-схемы описывают внешний JSON, Session выполняет операции с базой.",
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
        ("Проверить внешний API напрямую", "curl https://jsonplaceholder.typicode.com/posts/1"),
        ("Проверить внешний comments endpoint напрямую", "curl https://jsonplaceholder.typicode.com/posts/1/comments"),
        ("Получить внешний post через ваш FastAPI", "curl http://localhost:8003/api/http-client/post/1"),
    ],
    "chapter04": [
        ("Ожидаемая demo-ошибка", "curl -i http://localhost:8004/api/error-demo/custom"),
        ("Ошибка валидации", 'curl -i "http://localhost:8004/api/error-demo/validation?age=-1"'),
    ],
    "chapter05": [
        ("Открыть HTML-страницу", "open http://localhost:8005/jinja-demo"),
        ("Посмотреть исходные данные как JSON", "curl http://localhost:8005/api/template-data"),
    ],
    "chapter06": [
        ("Создать товар", 'curl -X POST http://localhost:8006/api/products \\\n  -H "Content-Type: application/json" \\\n  -d \'{"name":"Keyboard","description":"USB","price":"49.90","stock":10}\''),
        ("Получить список товаров", "curl http://localhost:8006/api/products"),
        ("Проверить текущую миграцию", "cd chapter06\nalembic current"),
        ("Создать и применить миграцию", 'cd chapter06\nalembic revision -m "add product category"\nalembic upgrade head'),
        ("Откатить последнюю миграцию", "cd chapter06\nalembic downgrade -1"),
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
        "Зачем шаблону нужен объект <code>request</code>?",
        "Чем отличается <code>{{ title }}</code> от <code>{% for topic in topics %}</code>?",
        "Почему список удобнее выводить через <code>for</code>, а не копировать <code>&lt;li&gt;</code> руками?",
        "Где лучше хранить данные для шаблона: в Python context или прямо в HTML?",
    ],
    "chapter06": [
        "Почему <code>Product</code> имеет <code>table=True</code>, а <code>ProductCreate</code> нет?",
        "Почему Session открывается и закрывается через dependency?",
        "Что произойдёт, если забыть <code>db.commit()</code>?",
        "Зачем в SQLModel иногда используют <code>sa_column=Column(...)</code>?",
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
        ("Лёгкий уровень", "Добавьте поле <code>category</code> в <code>Product</code> и <code>ProductRead</code>."),
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
        files.insert(2, ("chapter05/templates/jinja_demo.html", "Минимальный Jinja2-шаблон с переменной, условием if и циклом for."))
    if service == "chapter06":
        files.extend([
            ("chapter06/alembic.ini", "Настройки Alembic для миграций базы данных."),
            ("chapter06/alembic/env.py", "Код, который подключает Alembic к SQLModel metadata."),
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
        commands.append(("Alembic: текущая версия базы", "cd chapter06\nalembic current"))
        commands.append(("Alembic: создать файл миграции", 'cd chapter06\nalembic revision -m "add product category"'))
        commands.append(("Alembic: применить миграции", "cd chapter06\nalembic upgrade head"))
        commands.append(("Alembic: откатить последнюю миграцию", "cd chapter06\nalembic downgrade -1"))
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
    prev_link = f'http://localhost:{port - 1}' if number > 1 else "http://localhost:8000"
    next_link = f'http://localhost:{port + 1}' if number < 12 else "http://localhost:8000"
    prev_label = "Предыдущая глава" if number > 1 else "Главная"
    next_label = "Следующая глава" if number < 12 else "Главная"

    return f"""<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{protect_jinja(data["title"])}</title>
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
            <h1>{protect_jinja(data["title"])}</h1>
            <p>{protect_jinja(data["subtitle"])}</p>
            <div class="lesson-meta">
                <span><strong>Порт:</strong> {port}</span>
                <span><strong>Swagger:</strong> <code>http://localhost:{port}/docs</code></span>
                <span><strong>Результат:</strong> {protect_jinja(data["outcome"])}</span>
            </div>
        </section>

        <nav class="lesson-tabs" aria-label="Разделы главы">
            <button class="active" data-tab-target="#theory">Теория</button>
            <button data-tab-target="#code">Разбор кода</button>
            <button data-tab-target="#task">Практика</button>
            <button data-tab-target="#answers">Ответы</button>
        </nav>

        <section id="theory" class="tab-panel active">
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
                    <h2>{protect_jinja(data.get("code_title", "Ключевой фрагмент"))}</h2>
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
                    <h2>Полный разбор ответа</h2>
                    <p>Ниже решение разобрано по частям: что стоит на своём месте, зачем это нужно и какие ошибки чаще всего появляются, если часть кода пропустить.</p>
                </article>

                {render_extra_sections(ANSWER_WALKTHROUGHS[service])}

                {render_extra_sections(ANSWER_DEEP_DIVES[service])}

                <article class="info-box">
                    <h2>Короткое резюме решения</h2>
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


JINJA_DEMO_TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
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
            <h1>{{ title }}</h1>
            <p>Привет, {{ student_name }}. Эту строку собрал серверный шаблон Jinja2.</p>
        </section>

        {% if show_hint %}
        <section class="info-box">
            <h2>Подсказка</h2>
            <p>Все значения ниже пришли из Python-словаря, который endpoint передал в template context.</p>
        </section>
        {% endif %}

        <section class="info-box">
            <h2>Что показывает шаблон</h2>
            <ul class="flow-list">
                {% for topic in topics %}
                <li>
                    <strong>{{ topic.name }}</strong>
                    <code>{{ topic.template }}</code>
                    <span>{{ topic.description }}</span>
                </li>
                {% endfor %}
            </ul>
        </section>
    </main>
</body>
</html>
"""


def main() -> None:
    for service, data in LESSONS.items():
        (ROOT / service / "templates" / "index.html").write_text(render_lesson(service, data), encoding="utf-8")

    (ROOT / "chapter05" / "templates" / "jinja_demo.html").write_text(JINJA_DEMO_TEMPLATE, encoding="utf-8")


if __name__ == "__main__":
    main()
