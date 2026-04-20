# app/routers/pets.py
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import pets_controller as ctrl
from app.middleware.auth import CurrentUser, get_current_user
from app.schemas.pet import (
    BehaviourLogCreate,
    BehaviourLogOut,
    BehaviourLogResponse,
    HealthRecordCreate,
    HealthRecordOut,
    PetCreate,
    PetOut,
    PetUpdate,
)
from config.database import get_db

router = APIRouter(prefix="/pets", tags=["Pets"])


# ─── Pets CRUD ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[PetOut])
async def list_pets(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.list_pets(current_user.id, db)


@router.post("/", response_model=PetOut, status_code=201)
async def create_pet(
    data: PetCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.create_pet(current_user.id, data, db)


@router.get("/{pet_id}", response_model=PetOut)
async def get_pet(pet_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await ctrl.get_pet(pet_id, db)


@router.put("/{pet_id}", response_model=PetOut)
async def update_pet(
    pet_id: uuid.UUID,
    data: PetUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.update_pet(pet_id, current_user.id, data, db)


@router.delete("/{pet_id}")
async def delete_pet(
    pet_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.delete_pet(pet_id, current_user.id, db)


# ─── Health Records ───────────────────────────────────────────────────────────

@router.get("/{pet_id}/health", response_model=list[HealthRecordOut])
async def get_health_records(
    pet_id: uuid.UUID,
    record_type: str | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.get_health_records(pet_id, db, record_type, from_date, to_date)


@router.post("/{pet_id}/health", response_model=HealthRecordOut, status_code=201)
async def add_health_record(
    pet_id: uuid.UUID,
    data: HealthRecordCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.add_health_record(pet_id, current_user.id, data, db)


@router.delete("/{pet_id}/health/{record_id}")
async def delete_health_record(
    pet_id: uuid.UUID,
    record_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.delete_health_record(pet_id, record_id, current_user.id, db)


# ─── Behaviour Diary ──────────────────────────────────────────────────────────

@router.get("/{pet_id}/behaviour", response_model=list[BehaviourLogOut])
async def get_behaviour_logs(
    pet_id: uuid.UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.get_behaviour_logs(pet_id, db, days)


@router.post("/{pet_id}/behaviour", response_model=BehaviourLogResponse, status_code=201)
async def log_behaviour(
    pet_id: uuid.UUID,
    data: BehaviourLogCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.log_behaviour(pet_id, current_user.id, data, db)
