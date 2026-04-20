# app/models/pet.py
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[str] = mapped_column(String(20), nullable=False)  # cat | dog | bird | rabbit | other
    breed: Mapped[str | None] = mapped_column(String(100))
    birth_date: Mapped[date | None] = mapped_column(Date)
    sex: Mapped[str | None] = mapped_column(String(10))
    is_neutered: Mapped[bool] = mapped_column(default=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="pets")
    health_records: Mapped[list["HealthRecord"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    behaviour_logs: Mapped[list["BehaviourLog"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    ai_chats: Mapped[list["AiChat"]] = relationship(back_populates="pet")


class HealthRecord(Base):
    __tablename__ = "health_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"))
    record_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # vaccination | analysis | diagnosis | prescription | weight | grooming
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    value: Mapped[float | None] = mapped_column(Numeric(8, 2))
    unit: Mapped[str | None] = mapped_column(String(20))
    doc_url: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    vet_name: Mapped[str | None] = mapped_column(String(150))
    clinic_name: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pet: Mapped["Pet"] = relationship(back_populates="health_records")


class BehaviourLog(Base):
    __tablename__ = "behaviour_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pets.id", ondelete="CASCADE"))
    logged_at: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    appetite: Mapped[int | None] = mapped_column(SmallInteger)   # 1–5
    activity: Mapped[int | None] = mapped_column(SmallInteger)
    mood: Mapped[int | None] = mapped_column(SmallInteger)
    stool: Mapped[str | None] = mapped_column(String(20))        # normal | loose | hard | absent
    weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    pet: Mapped["Pet"] = relationship(back_populates="behaviour_logs")
