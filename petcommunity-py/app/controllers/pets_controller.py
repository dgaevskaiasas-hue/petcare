# app/controllers/pets_controller.py
import uuid
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pet import BehaviourLog, HealthRecord, Pet
from app.schemas.pet import (
    BehaviourAlert,
    BehaviourLogCreate,
    BehaviourLogOut,
    BehaviourLogResponse,
    HealthRecordCreate,
    HealthRecordOut,
    PetCreate,
    PetOut,
    PetUpdate,
)


# ─── Pets ─────────────────────────────────────────────────────────────────────

async def list_pets(owner_id: uuid.UUID, db: AsyncSession) -> list[PetOut]:
    result = await db.scalars(select(Pet).where(Pet.owner_id == owner_id).order_by(Pet.created_at))
    return [PetOut.model_validate(p) for p in result.all()]


async def get_pet(pet_id: uuid.UUID, db: AsyncSession) -> PetOut:
    pet = await db.get(Pet, pet_id)
    if not pet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Питомец не найден")
    return PetOut.model_validate(pet)


async def create_pet(owner_id: uuid.UUID, data: PetCreate, db: AsyncSession) -> PetOut:
    pet = Pet(owner_id=owner_id, **data.model_dump())
    db.add(pet)
    await db.flush()
    return PetOut.model_validate(pet)


async def update_pet(pet_id: uuid.UUID, owner_id: uuid.UUID, data: PetUpdate, db: AsyncSession) -> PetOut:
    pet = await _get_owned_pet(pet_id, owner_id, db)
    for k, v in data.model_dump().items():
        setattr(pet, k, v)
    await db.flush()
    return PetOut.model_validate(pet)


async def delete_pet(pet_id: uuid.UUID, owner_id: uuid.UUID, db: AsyncSession) -> dict:
    pet = await _get_owned_pet(pet_id, owner_id, db)
    await db.delete(pet)
    return {"message": "Питомец удалён"}


# ─── Health Records ───────────────────────────────────────────────────────────

async def get_health_records(
    pet_id: uuid.UUID, db: AsyncSession,
    record_type: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[HealthRecordOut]:
    q = select(HealthRecord).where(HealthRecord.pet_id == pet_id)
    if record_type: q = q.where(HealthRecord.record_type == record_type)
    if from_date:   q = q.where(HealthRecord.recorded_at >= from_date)
    if to_date:     q = q.where(HealthRecord.recorded_at <= to_date)
    q = q.order_by(HealthRecord.recorded_at.desc())
    result = await db.scalars(q)
    return [HealthRecordOut.model_validate(r) for r in result.all()]


async def add_health_record(
    pet_id: uuid.UUID, owner_id: uuid.UUID,
    data: HealthRecordCreate, db: AsyncSession,
) -> HealthRecordOut:
    await _get_owned_pet(pet_id, owner_id, db)
    record = HealthRecord(pet_id=pet_id, **data.model_dump())
    db.add(record)
    await db.flush()
    return HealthRecordOut.model_validate(record)


async def delete_health_record(
    pet_id: uuid.UUID, record_id: uuid.UUID,
    owner_id: uuid.UUID, db: AsyncSession,
) -> dict:
    await _get_owned_pet(pet_id, owner_id, db)
    record = await db.get(HealthRecord, record_id)
    if not record or record.pet_id != pet_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Запись не найдена")
    await db.delete(record)
    return {"message": "Запись удалена"}


# ─── Behaviour Diary ──────────────────────────────────────────────────────────

async def get_behaviour_logs(
    pet_id: uuid.UUID, db: AsyncSession, days: int = 30,
) -> list[BehaviourLogOut]:
    since = date.today() - timedelta(days=days)
    result = await db.scalars(
        select(BehaviourLog)
        .where(BehaviourLog.pet_id == pet_id, BehaviourLog.logged_at >= since)
        .order_by(BehaviourLog.logged_at.desc())
    )
    return [BehaviourLogOut.model_validate(r) for r in result.all()]


async def log_behaviour(
    pet_id: uuid.UUID, owner_id: uuid.UUID,
    data: BehaviourLogCreate, db: AsyncSession,
) -> BehaviourLogResponse:
    await _get_owned_pet(pet_id, owner_id, db)
    log = BehaviourLog(pet_id=pet_id, **data.model_dump())
    db.add(log)
    await db.flush()
    alerts = _analyze_log(data)
    return BehaviourLogResponse(log=BehaviourLogOut.model_validate(log), alerts=alerts)


def _analyze_log(data: BehaviourLogCreate) -> list[BehaviourAlert]:
    """Анализатор поведения — возвращает алерты по записи дневника."""
    alerts = []
    metrics = [v for v in [data.appetite, data.activity, data.mood] if v is not None]
    if sum(1 for v in metrics if v <= 2) >= 2:
        alerts.append(BehaviourAlert(
            level="warning",
            message="Несколько показателей ниже нормы. Рекомендуется визит к ветеринару.",
        ))
    if data.appetite == 1:
        alerts.append(BehaviourAlert(level="danger", message="Полный отказ от еды — требует внимания."))
    if data.stool == "absent":
        alerts.append(BehaviourAlert(level="warning", message="Отсутствие стула — обратите внимание."))
    return alerts


# ─── Private helper ───────────────────────────────────────────────────────────

async def _get_owned_pet(pet_id: uuid.UUID, owner_id: uuid.UUID, db: AsyncSession) -> Pet:
    pet = await db.get(Pet, pet_id)
    if not pet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Питомец не найден")
    if pet.owner_id != owner_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа")
    return pet
