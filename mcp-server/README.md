# Petcare MCP Server

Starter Python MCP server for a petcare product. It exposes tool groups for:

- PostgreSQL reads and parameterized statements
- S3 uploads, downloads, object metadata, and presigned URLs
- external HTTP service calls behind an allowlist

This version is intentionally conservative:

- read-heavy by default
- parameterized SQL only
- external requests restricted to approved base URLs
- S3 access scoped to a configured bucket

## Structure

```text
petcare_mcp/
  config.py
  server.py
  tools/
    db.py
    s3.py
    external.py
```

## Setup

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

Stdio transport:

```bash
petcare-mcp
```

Streamable HTTP transport:

```bash
MCP_TRANSPORT=streamable-http petcare-mcp
```

## Suggested first tools for Petcare

- `db_query_select` for pet profiles, care plans, reminders, and audit reads
- `s3_create_presigned_upload_url` for profile photos and documents
- `external_fetch_json` for partner APIs like vet search or reminder providers

## Notes

- Keep business rules in your app and expose only the minimum safe operations here.
- If you later want petcare-specific tools, add wrapper tools such as `get_pet_profile`, `list_health_records`, or `create_care_reminder` on top of the generic DB layer.


[README.md](https://github.com/user-attachments/files/27092206/README.md)
# Petcare MCP Server

## Что это

`mcp-server` — это стартовая серверная прослойка для интеграции AI-ассистента с проектом `Petcare` через Model Context Protocol.

Текущая реализация не завязана жёстко на одну конкретную бизнес-сущность портала.  
Она решает базовую инженерную задачу: дать модели безопасный и управляемый доступ к инфраструктурным ресурсам проекта:

- PostgreSQL
- S3-хранилищу
- внешним HTTP/API сервисам

Идея этой версии: сначала собрать устойчивый технический фундамент, а уже потом поверх него вводить прикладные инструменты уровня питомцев, медкарты, сообщества и ухода.

## Что сделано в текущей версии

В этой версии реализован базовый MCP server на Python со следующими блоками.

### 1. DB tools

Файл: `petcare_mcp/tools/db.py`

Что уже есть:
- `db_query_select`
- `db_execute_statement`

Что это даёт:
- безопасное выполнение одиночных SQL-запросов
- ограничение на `SELECT` для чтения
- отдельный инструмент для `INSERT/UPDATE/DELETE`
- параметризованные запросы вместо ручной подстановки строк

Для чего это полезно:
- чтение профилей питомцев
- чтение медкарты
- работа с напоминаниями
- выборка данных для AI-ассистента

### 2. S3 tools

Файл: `petcare_mcp/tools/s3.py`

Что уже есть:
- `s3_create_presigned_upload_url`
- `s3_create_presigned_download_url`
- `s3_get_object_metadata`
- `s3_put_text_object`
- `s3_get_text_object`
- `s3_put_base64_object`

Что это даёт:
- загрузку и скачивание файлов через presigned URL
- хранение документов и изображений
- работу с текстовыми и бинарными данными

Для чего это полезно:
- загрузка документов питомца
- хранение фото питомца
- работа с вложениями, которые потом может анализировать AI

### 3. External tools

Файл: `petcare_mcp/tools/external.py`

Что уже есть:
- `external_fetch_json`
- `external_fetch_text`

Что это даёт:
- вызовы внешних API
- ограничение только на заранее разрешённые base URL
- централизованную точку интеграции с внешними сервисами

Для чего это полезно:
- поиск ветклиник
- обращение к внешним petcare API
- интеграция с notification-сервисами или партнёрскими системами

### 4. Конфигурация и запуск

Файлы:
- `petcare_mcp/config.py`
- `petcare_mcp/server.py`
- `.env.example`
- `pyproject.toml`

Что уже есть:
- конфигурация через `.env`
- поддержка `stdio`
- поддержка `streamable-http`
- единая точка запуска сервера

## Технические ограничения текущей версии

Важно понимать, что эта версия пока инфраструктурная, а не прикладная.

Сейчас сервер:
- ещё не знает ничего о сущностях `Pet`, `HealthRecord`, `ForumPost`, `Reminder`
- не реализует прикладные permission checks уровня пользователя и владельца питомца
- не повторяет бизнес-логику backend-а
- не является финальным MCP для пользовательского сценария портала

То есть на данный момент это:
- не “готовый AI-слой сообщества владельцев домашних животных”
- а “стартовый инструментальный слой для интеграции AI с backend-ресурсами”

## Почему это сделано именно так

Такой подход выбран специально, чтобы:

- сначала стабилизировать доступ к данным и внешним ресурсам
- не зашивать бизнес-логику портала прямо в первую версию MCP
- упростить тестирование интеграций
- сделать сервер расширяемым без переписывания основы

Проще говоря:

1. Сначала делаем базовый MCP-каркас.
2. Потом добавляем предметные инструменты портала.
3. Потом ограничиваем их ролями, правами доступа и user-context.

## Что будет доработано в следующей версии

Следующая версия должна стать уже прикладной, то есть ориентированной именно на функции портала.

### Планируемые domain-specific tools

#### Pets
- `get_pet_profile`
- `list_user_pets`
- `create_pet_profile`
- `update_pet_profile`

#### Health
- `list_health_records`
- `add_health_record`
- `list_behaviour_logs`
- `add_behaviour_log`
- `get_health_summary`

#### Community
- `list_community_posts`
- `get_post`
- `create_post`
- `add_comment`
- `toggle_like`

#### Care
- `create_care_reminder`
- `list_care_reminders`
- `mark_care_task_done`
- `get_care_schedule`

#### Documents
- `create_pet_document_upload_url`
- `save_pet_document_metadata`
- `list_pet_documents`
- `get_pet_document_download_url`

#### External Services
- `find_vet_clinics`
- `get_petcare_reference_info`
- `send_notification`

## Что изменится архитектурно в следующей версии

Сейчас слой выглядит так:

- generic DB access
- generic S3 access
- generic external API access

Следующая версия должна перейти к модели:

- pet domain tools
- health domain tools
- community domain tools
- care domain tools
- document domain tools

То есть MCP будет работать не на уровне:
- “выполни SQL”
- “создай presigned URL”
- “сходи во внешний endpoint”

А на уровне:
- “получи профиль питомца”
- “добавь запись в медкарту”
- “создай напоминание по уходу”
- “загрузи документ питомца”
- “найди ветклинику”

Именно это и сделает его соответствующим тематике проекта:
`Информационный портал для формирования сообщества домашних животных`.

## Структура проекта

```text
petcare_mcp/
  config.py
  server.py
  tools/
    db.py
    s3.py
    external.py
```

В следующей версии структура, скорее всего, будет расширена до чего-то такого:

```text
petcare_mcp/
  config.py
  server.py
  tools/
    pets.py
    health.py
    community.py
    care.py
    documents.py
    external_services.py
  services/
    db.py
    s3.py
    external_api.py
  schemas/
    pets.py
    health.py
    community.py
    care.py
    documents.py
```

## Установка

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Запуск

Через `stdio` transport:

```bash
petcare-mcp
```

Через `streamable-http` transport:

```bash
MCP_TRANSPORT=streamable-http petcare-mcp
```

## Переменные окружения

Основные настройки в `.env`:

- `POSTGRES_DSN` — строка подключения к PostgreSQL
- `POSTGRES_MAX_ROWS` — ограничение числа строк в ответе
- `AWS_REGION` — регион AWS
- `S3_BUCKET` — bucket для хранения файлов
- `S3_PRESIGN_EXPIRY_SECONDS` — срок действия presigned URL
- `ALLOWED_EXTERNAL_BASE_URLS` — allowlist внешних сервисов
- `EXTERNAL_REQUEST_TIMEOUT_SECONDS` — таймаут запросов

## Итог

Текущая версия — это инженерная основа MCP-интеграции для `Petcare`.

Она уже решает базовые задачи:
- доступ к БД
- доступ к S3
- вызов внешних сервисов

Но следующая версия должна стать прикладной:
- с инструментами под питомцев
- под здоровье
- под сообщество
- под уход
- под документы

То есть сейчас это хороший `foundation layer`, а следующая итерация должна стать уже `product-facing MCP layer`.
