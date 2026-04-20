# app/controllers/ai_controller.py
# AI-ассистент — аналог AI Nutrition Expert (Pet's Mind, Le Chen & Yu Cao, 2025)
# Anthropic Claude с контекстом питомца и историей диалога
import uuid
from datetime import date

import anthropic
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_chat import AiChat
from app.models.pet import Pet
from app.schemas.ai import ChatHistoryItem, ChatMessageRequest, ChatMessageResponse
from config.settings import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ты — AI-ассистент по уходу за домашними животными на платформе PetCommunity.
Помогай владельцам с вопросами о питании, здоровье, поведении и уходе за питомцами.
При серьёзных симптомах рекомендуй обратиться к ветеринару. Не ставь диагнозы.
Отвечай на русском языке, дружелюбно и лаконично."""


def _pet_context(pet: Pet) -> str:
    """Строим контекстный блок для system prompt."""
    if not pet:
        return ""
    age_str = ""
    if pet.birth_date:
        years = (date.today() - pet.birth_date).days // 365
        age_str = f", {years} лет"
    return (
        f"\n\nКонтекст питомца: {pet.name}, {pet.species}"
        f"{f' ({pet.breed})' if pet.breed else ''}{age_str}"
        f"{f', {pet.sex}' if pet.sex else ''}"
        f"{', кастрирован/стерилизован' if pet.is_neutered else ''}"
        f"{f'. Заметки: {pet.notes}' if pet.notes else ''}."
    )


async def send_message(
    user_id: uuid.UUID,
    data: ChatMessageRequest,
    db: AsyncSession,
) -> ChatMessageResponse:
    # Контекст питомца
    pet = None
    if data.pet_id:
        pet = await db.get(Pet, data.pet_id)
        if pet and pet.owner_id != user_id:
            pet = None  # чужой питомец — не показываем

    # История диалога (последние 20 сообщений, старые первыми)
    history_rows = await db.scalars(
        select(AiChat)
        .where(AiChat.user_id == user_id, AiChat.pet_id == data.pet_id)
        .order_by(AiChat.created_at.desc())
        .limit(20)
    )
    history = [
        {"role": h.role, "content": h.content}
        for h in reversed(history_rows.all())
    ]

    # Сохраняем сообщение пользователя
    db.add(AiChat(user_id=user_id, pet_id=data.pet_id, role="user", content=data.message))
    await db.flush()

    # Вызов LLM
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT + _pet_context(pet),
            messages=[*history, {"role": "user", "content": data.message}],
        )
        reply = response.content[0].text
    except Exception as e:
        reply = "Сервис временно недоступен. Попробуйте позже."

    # Сохраняем ответ
    saved = AiChat(user_id=user_id, pet_id=data.pet_id, role="assistant", content=reply)
    db.add(saved)
    await db.flush()

    return ChatMessageResponse(id=saved.id, role="assistant", content=reply, created_at=saved.created_at)


async def get_history(
    user_id: uuid.UUID,
    pet_id: uuid.UUID | None,
    db: AsyncSession,
    limit: int = 50,
) -> list[ChatHistoryItem]:
    result = await db.scalars(
        select(AiChat)
        .where(AiChat.user_id == user_id, AiChat.pet_id == pet_id)
        .order_by(AiChat.created_at.asc())
        .limit(limit)
    )
    return [ChatHistoryItem.model_validate(r) for r in result.all()]


async def clear_history(user_id: uuid.UUID, pet_id: uuid.UUID | None, db: AsyncSession) -> dict:
    rows = await db.scalars(
        select(AiChat).where(AiChat.user_id == user_id, AiChat.pet_id == pet_id)
    )
    for row in rows.all():
        await db.delete(row)
    return {"message": "История очищена"}


# Подсказки-промпты (hint prompts — как в статье Pet's Mind)
HINTS: dict[str, list[str]] = {
    "cat": [
        "Чем кормить котёнка до 1 года?",
        "Почему кот отказывается от еды?",
        "Как часто нужно вакцинировать кошку?",
        "Какие симптомы требуют срочного визита к врачу?",
    ],
    "dog": [
        "Сколько раз в день кормить взрослую собаку?",
        "Можно ли собаке давать кости?",
        "Как справиться с тревогой разлуки у щенка?",
        "Когда делать первую прививку щенку?",
    ],
}
HINTS["default"] = [
    "Как составить рацион для питомца?",
    "Как часто нужен осмотр у ветеринара?",
    "Какие витамины нужны моему питомцу?",
    "Признаки здорового питомца?",
]


def get_hints(species: str | None) -> list[str]:
    return HINTS.get(species or "default", HINTS["default"])
