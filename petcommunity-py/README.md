# PetCommunity API — Python + FastAPI

AI-powered информационный портал для сообщества владельцев домашних животных.

## Структура проекта

```
petcommunity-py/
├── main.py                        # Точка входа: FastAPI + Socket.io (ASGI)
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py                # Pydantic Settings (все переменные из .env)
│   └── database.py                # Async SQLAlchemy engine + get_db dependency
└── app/
    ├── models/                    # SQLAlchemy ORM-модели
    │   ├── user.py                # User, RefreshToken
    │   ├── pet.py                 # Pet, HealthRecord, BehaviourLog
    │   ├── forum.py               # Post, Comment, Like, Tag, PostTag
    │   └── ai_chat.py             # AiChat
    ├── schemas/                   # Pydantic v2 схемы (валидация + OpenAPI)
    │   ├── auth.py
    │   ├── pet.py
    │   ├── forum.py
    │   └── ai.py
    ├── controllers/               # Бизнес-логика
    │   ├── auth_controller.py     # register, login, refresh (rotation), logout
    │   ├── pets_controller.py     # CRUD питомцев, медкарта, дневник + analyzeLog
    │   ├── forum_controller.py    # Посты, лайки, комментарии деревом, FTS-поиск
    │   └── ai_controller.py      # Anthropic Claude с контекстом питомца
    ├── routers/                   # FastAPI роутеры (только маршруты)
    │   ├── auth.py
    │   ├── pets.py
    │   ├── forum.py
    │   └── ai.py
    ├── middleware/
    │   └── auth.py                # get_current_user, get_optional_user, require_role
    └── utils/
        └── migrate.py             # Создание таблиц через SQLAlchemy metadata
```

## Быстрый старт

```bash
# 1. Создать виртуальное окружение
python -m venv venv && source venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить переменные окружения
cp .env.example .env
# Заполнить: DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY

# 4. Создать таблицы
python -m app.utils.migrate

# 5. Запустить сервер
python main.py
# или:
uvicorn main:socket_app --reload --port 8000
```

## API Docs (автоматически из Pydantic-схем)

- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

## Эндпоинты

### Auth  `POST /api/v1/auth`
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Вход |
| POST | `/auth/refresh` | Обновить access token (rotation) |
| POST | `/auth/logout` | Выход |
| GET  | `/auth/me` | Текущий пользователь |

### Pets  `/api/v1/pets`
| Метод | Путь | Описание |
|-------|------|----------|
| GET    | `/pets/` | Мои питомцы |
| POST   | `/pets/` | Добавить питомца |
| GET    | `/pets/{id}` | Профиль питомца |
| PUT    | `/pets/{id}` | Обновить |
| DELETE | `/pets/{id}` | Удалить |
| GET    | `/pets/{id}/health` | Медкарта (`?record_type=vaccination&from_date=`) |
| POST   | `/pets/{id}/health` | Добавить запись |
| DELETE | `/pets/{id}/health/{record_id}` | Удалить запись |
| GET    | `/pets/{id}/behaviour` | Дневник поведения (`?days=30`) |
| POST   | `/pets/{id}/behaviour` | Записать → алерты |

### Forum  `/api/v1/forum`
| Метод | Путь | Описание |
|-------|------|----------|
| GET    | `/forum/` | Посты (`?search=&species=cat&tag=питание`) |
| POST   | `/forum/` | Создать пост |
| GET    | `/forum/{id}` | Пост |
| PUT    | `/forum/{id}` | Редактировать |
| DELETE | `/forum/{id}` | Удалить |
| POST   | `/forum/{id}/like` | Лайк / снять |
| GET    | `/forum/{id}/comments` | Комментарии (дерево) |
| POST   | `/forum/{id}/comments` | Добавить комментарий |
| DELETE | `/forum/{id}/comments/{cid}` | Удалить комментарий |

### AI  `/api/v1/ai`
| Метод | Путь | Описание |
|-------|------|----------|
| POST   | `/ai/chat` | Сообщение (`{ message, pet_id? }`) |
| GET    | `/ai/chat` | История (`?pet_id=&limit=50`) |
| DELETE | `/ai/chat` | Очистить историю |
| GET    | `/ai/hints` | Подсказки (`?species=cat`) |

## Соответствие статье Pet's Mind (Le Chen, Yu Cao, 2025)

| Система из статьи | Реализация |
|---|---|
| AI Nutrition Expert | `ai_controller.py` — Anthropic Claude, контекст питомца, история диалога |
| Health Tracking | `pets_controller.py` — медкарта + дневник поведения с алертами |
| Community Forum | `forum_controller.py` — посты, теги, FTS (PostgreSQL), дерево комментариев |
