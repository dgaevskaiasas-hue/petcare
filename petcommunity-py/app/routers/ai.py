# app/routers/ai.py
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import ai_controller as ctrl
from app.middleware.auth import CurrentUser, get_current_user
from app.schemas.ai import ChatHistoryItem, ChatMessageRequest, ChatMessageResponse
from config.database import get_db

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=ChatMessageResponse)
async def send_message(
    data: ChatMessageRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.send_message(current_user.id, data, db)


@router.get("/chat", response_model=list[ChatHistoryItem])
async def get_history(
    pet_id: uuid.UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.get_history(current_user.id, pet_id, db, limit)


@router.delete("/chat")
async def clear_history(
    pet_id: uuid.UUID | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.clear_history(current_user.id, pet_id, db)


@router.get("/hints", response_model=list[str])
async def get_hints(species: str | None = Query(None)):
    return ctrl.get_hints(species)
