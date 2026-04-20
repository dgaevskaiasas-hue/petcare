# app/utils/migrate.py
"""
Создаёт все таблицы в БД через SQLAlchemy metadata.
Запуск: python -m app.utils.migrate
"""
import asyncio

from config.database import Base, engine

# Импортируем все модели, чтобы они попали в metadata
from app.models.user import User, RefreshToken       # noqa: F401
from app.models.pet import Pet, HealthRecord, BehaviourLog  # noqa: F401
from app.models.forum import Post, Comment, Like, Tag, PostTag  # noqa: F401
from app.models.ai_chat import AiChat               # noqa: F401


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Все таблицы созданы")


if __name__ == "__main__":
    asyncio.run(create_tables())
