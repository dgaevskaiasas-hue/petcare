# app/schemas/forum.py
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SpeciesFilter = Literal["cat", "dog", "bird", "rabbit", "other"]


class PostCreate(BaseModel):
    title: str = Field(max_length=200)
    body: str = Field(min_length=10)
    species_tag: SpeciesFilter | None = None
    tags: list[str] = []


class PostUpdate(BaseModel):
    title: str = Field(max_length=200)
    body: str = Field(min_length=10)
    species_tag: SpeciesFilter | None = None


class PostOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    body: str
    species_tag: str | None
    author_name: str
    author_avatar: str | None
    like_count: int
    comment_count: int
    tags: list[str]
    created_at: datetime


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: uuid.UUID | None = None


class CommentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    post_id: uuid.UUID
    parent_id: uuid.UUID | None
    body: str
    author_name: str
    author_avatar: str | None
    created_at: datetime
    replies: list["CommentOut"] = []
