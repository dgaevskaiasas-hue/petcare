# app/routers/forum.py
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import forum_controller as ctrl
from app.middleware.auth import CurrentUser, get_current_user, get_optional_user
from app.schemas.forum import CommentCreate, PostCreate, PostUpdate
from config.database import get_db

router = APIRouter(prefix="/forum", tags=["Forum"])


# ─── Posts ────────────────────────────────────────────────────────────────────

@router.get("/")
async def list_posts(
    search: str | None = Query(None),
    species: str | None = Query(None),
    tag: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.list_posts(db, search, species, tag, limit, offset)


@router.post("/", status_code=201)
async def create_post(
    data: PostCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await ctrl.create_post(current_user.id, data, db)
    return {"id": post.id, "title": post.title, "created_at": post.created_at}


@router.get("/{post_id}")
async def get_post(post_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await ctrl.get_post(post_id, db)


@router.put("/{post_id}")
async def update_post(
    post_id: uuid.UUID,
    data: PostUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await ctrl.update_post(post_id, current_user.id, data, db)
    return {"id": post.id, "title": post.title, "updated_at": post.updated_at}


@router.delete("/{post_id}")
async def delete_post(
    post_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.delete_post(post_id, current_user.id, db)


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.toggle_like(current_user.id, post_id, db)


# ─── Comments ─────────────────────────────────────────────────────────────────

@router.get("/{post_id}/comments")
async def get_comments(post_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await ctrl.get_comments(post_id, db)


@router.post("/{post_id}/comments", status_code=201)
async def add_comment(
    post_id: uuid.UUID,
    data: CommentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    comment = await ctrl.add_comment(post_id, current_user.id, data, db)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "parent_id": comment.parent_id,
        "body": comment.body,
        "created_at": comment.created_at,
    }


@router.delete("/{post_id}/comments/{comment_id}")
async def delete_comment(
    post_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ctrl.delete_comment(comment_id, current_user.id, db)
