# PetCare MCP API

Backend-сервис для pet-care платформы на **FastAPI** с MCP-подходом: функциональность разделена на независимые tools для питомцев, документов и ветеринарных клиник.

Проект использует **PostgreSQL**, **JWT-аутентификацию**, **MinIO S3-хранилище**, **Docker Compose** и автоматически генерируемую документацию API через **Swagger / OpenAPI**.

## Стек

- Python 3.12
- FastAPI
- PostgreSQL + asyncpg
- SQLAlchemy Async
- JWT / PyJWT
- MinIO + boto3
- Redis
- Celery
- Docker Compose
- Swagger / OpenAPI

## Что Реализовано

- MCP-style архитектура с динамической регистрацией tools
- Tools: `pets`, `documents`, `clinics`
- JWT-аутентификация
- Проверка владельца питомца и документа
- Работа с PostgreSQL
- Работа с MinIO как S3-compatible storage
- Единый формат ответов API
- Typed errors: `NOT_FOUND`, `FORBIDDEN`, `TIMEOUT`, `VALIDATION_ERROR`
- Middleware timeout на 5 секунд
- Dockerfile и docker-compose
- OpenAPI / Swagger документация
- Smoke tests
- LLM adapter pattern для подключения Gemma-compatible модели

## Запуск

Склонировать репозиторий:

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

Запустить проект:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Swagger:

```text
http://localhost:8000/docs
```

MinIO:

```text
http://localhost:9001
login: petcare
password: petcare123
```

Остановить проект:

```bash
docker compose -f docker/docker-compose.yml down
```

## Авторизация

Получить JWT token:

```http
POST /auth/login
```

Body:

```json
{
  "user_id": "user-1",
  "password": "petcare-demo-password"
}
```

В Swagger нажать **Authorize** и вставить:

```text
Bearer <access_token>
```

## Основные Endpoints

```http
POST /auth/login

GET  /mcp/pets/{pet_id}/details
GET  /mcp/pets/{pet_id}/short

GET  /mcp/pets/{pet_id}/documents
GET  /mcp/pets/{pet_id}/documents/by-date
POST /mcp/documents/extract

GET  /mcp/clinics/city
GET  /mcp/clinics/location
POST /mcp/clinics/filter-available
GET  /mcp/clinics/{vet_id}/contacts
GET  /mcp/clinics/location-by-name

POST /mcp/execute
```

## Формат Ответов

Успех:

```json
{
  "data": {},
  "error": null
}
```

Ошибка:

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "description"
  }
}
```

## Архитектура

```text
app/
  api/              routes, middleware
  core/             config, JWT, exceptions
  infrastructure/   db session, S3 client
  mcp/              registry, router
  tools/            MCP tools
  services/         business logic
  repository/       SQL queries
  llm/              LLM adapters
```

Поток запроса:

```text
HTTP endpoint
-> JWT auth
-> MCPRouter
-> ToolRegistry
-> Tool
-> Service
-> Repository / S3
-> Response
```


## Тесты

```bash
docker compose -f docker/docker-compose.yml run --rm --no-deps api python -m unittest discover -s tests -v
```

## Важное Замечание

Проект запускается локально через Docker. Это локальный деплой на компьютере разработчика:

```text
http://localhost:8000
```

Чтобы проект был доступен в интернете, его нужно развернуть на удаленном сервере или cloud-платформе.

Классический CRUD сейчас реализован не полностью: backend построен по исходному MCP ТЗ, где были required read/search/extract endpoints. Для полного CRUD нужно добавить create/update/delete операции.
