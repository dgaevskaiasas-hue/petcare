# app/schemas/pet.py
import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


SpeciesType = Literal["cat", "dog", "bird", "rabbit", "other"]
RecordType  = Literal["vaccination", "analysis", "diagnosis", "prescription", "weight", "grooming"]
StoolType   = Literal["normal", "loose", "hard", "absent"]


class PetCreate(BaseModel):
    name: str = Field(max_length=100)
    species: SpeciesType
    breed: str | None = None
    birth_date: date | None = None
    sex: Literal["male", "female"] | None = None
    is_neutered: bool = False
    notes: str | None = None
    extra: dict = {}


class PetUpdate(PetCreate):
    pass


class PetOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    species: str
    breed: str | None
    birth_date: date | None
    sex: str | None
    is_neutered: bool
    avatar_url: str | None
    notes: str | None
    extra: dict
    created_at: datetime


# ─── Health Records ───────────────────────────────────────────────────────────

class HealthRecordCreate(BaseModel):
    record_type: RecordType
    title: str = Field(max_length=200)
    description: str | None = None
    value: float | None = None
    unit: str | None = None
    doc_url: str | None = None
    recorded_at: date | None = None
    vet_name: str | None = None
    clinic_name: str | None = None


class HealthRecordOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    pet_id: uuid.UUID
    record_type: str
    title: str
    description: str | None
    value: float | None
    unit: str | None
    doc_url: str | None
    recorded_at: date
    vet_name: str | None
    clinic_name: str | None
    created_at: datetime


# ─── Behaviour Diary ──────────────────────────────────────────────────────────

class BehaviourLogCreate(BaseModel):
    appetite: int | None = Field(None, ge=1, le=5)
    activity: int | None = Field(None, ge=1, le=5)
    mood:     int | None = Field(None, ge=1, le=5)
    stool:    StoolType | None = None
    weight_kg: float | None = None
    notes: str | None = None


class BehaviourLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    pet_id: uuid.UUID
    logged_at: date
    appetite: int | None
    activity: int | None
    mood: int | None
    stool: str | None
    weight_kg: float | None
    notes: str | None
    created_at: datetime


class BehaviourAlert(BaseModel):
    level: Literal["warning", "danger"]
    message: str


class BehaviourLogResponse(BaseModel):
    log: BehaviourLogOut
    alerts: list[BehaviourAlert]
