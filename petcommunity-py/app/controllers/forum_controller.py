# app/controllers/forum_controller.py
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.forum import Comment, Like, Post, PostTag, Tag
from app.schemas.forum import CommentCreate, CommentOut, PostCreate, PostOut, PostUpdate


# ─── Posts ────────────────────────────────────────────────────────────────────

async def list_posts(
    db: AsyncSession,
    search: str | None = None,
    species: str | None = None,
    tag: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    # Используем raw SQL для агрегации — SQLAlchemy ORM плохо справляется с такими запросами
    conditions = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}

    if species:
        conditions.append("p.species_tag = :species")
        params["species"] = species

    if tag:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM post_tags pt JOIN tags t ON t.id=pt.tag_id
                WHERE pt.post_id=p.id AND t.name=:tag
            )
        """)
        params["tag"] = tag

    if search:
        conditions.append(
            "to_tsvector('russian', p.title || ' ' || p.body) @@ plainto_tsquery('russian', :search)"
        )
        params["search"] = search

    where = " AND ".join(conditions)
    sql = text(f"""
        SELECT
            p.id, p.title, p.body, p.species_tag, p.created_at,
            u.username  AS author_name,
            u.avatar_url AS author_avatar,
            COUNT(DISTINCT c.id)::int      AS comment_count,
            COUNT(DISTINCT l.user_id)::int AS like_count,
            COALESCE(
                ARRAY_AGG(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL),
                ARRAY[]::text[]
            ) AS tags
        FROM posts p
        JOIN users u ON u.id = p.author_id
        LEFT JOIN comments c ON c.post_id = p.id
        LEFT JOIN likes l    ON l.post_id  = p.id
        LEFT JOIN post_tags pt ON pt.post_id = p.id
        LEFT JOIN tags t     ON t.id = pt.tag_id
        WHERE {where}
        GROUP BY p.id, u.username, u.avatar_url
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(sql, params)
    return [dict(row._mapping) for row in result.all()]


async def get_post(post_id: uuid.UUID, db: AsyncSession) -> dict:
    sql = text("""
        SELECT p.*, u.username AS author_name, u.avatar_url AS author_avatar,
            COUNT(DISTINCT l.user_id)::int AS like_count,
            COALESCE(ARRAY_AGG(DISTINCT t.name) FILTER (WHERE t.name IS NOT NULL), ARRAY[]::text[]) AS tags
        FROM posts p
        JOIN users u ON u.id=p.author_id
        LEFT JOIN likes l ON l.post_id=p.id
        LEFT JOIN post_tags pt ON pt.post_id=p.id
        LEFT JOIN tags t ON t.id=pt.tag_id
        WHERE p.id=:post_id
        GROUP BY p.id, u.username, u.avatar_url
    """)
    result = await db.execute(sql, {"post_id": post_id})
    row = result.first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пост не найден")
    return dict(row._mapping)


async def create_post(author_id: uuid.UUID, data: PostCreate, db: AsyncSession) -> Post:
    post = Post(author_id=author_id, title=data.title, body=data.body, species_tag=data.species_tag)
    db.add(post)
    await db.flush()

    for tag_name in data.tags:
        tag = await db.scalar(select(Tag).where(Tag.name == tag_name.lower().strip()))
        if not tag:
            tag = Tag(name=tag_name.lower().strip())
            db.add(tag)
            await db.flush()
        db.add(PostTag(post_id=post.id, tag_id=tag.id))

    return post


async def update_post(post_id: uuid.UUID, author_id: uuid.UUID, data: PostUpdate, db: AsyncSession) -> Post:
    post = await _get_owned_post(post_id, author_id, db)
    post.title = data.title
    post.body = data.body
    post.species_tag = data.species_tag
    return post


async def delete_post(post_id: uuid.UUID, author_id: uuid.UUID, db: AsyncSession) -> dict:
    post = await _get_owned_post(post_id, author_id, db)
    await db.delete(post)
    return {"message": "Пост удалён"}


# ─── Likes ────────────────────────────────────────────────────────────────────

async def toggle_like(user_id: uuid.UUID, post_id: uuid.UUID, db: AsyncSession) -> dict:
    like = await db.get(Like, {"user_id": user_id, "post_id": post_id})
    if like:
        await db.delete(like)
        return {"liked": False}
    db.add(Like(user_id=user_id, post_id=post_id))
    return {"liked": True}


# ─── Comments ─────────────────────────────────────────────────────────────────

async def get_comments(post_id: uuid.UUID, db: AsyncSession) -> list[dict]:
    result = await db.scalars(
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author), selectinload(Comment.replies))
        .order_by(Comment.created_at)
    )
    comments = result.all()

    def _serialize(c: Comment) -> dict:
        return {
            "id": c.id,
            "post_id": c.post_id,
            "parent_id": c.parent_id,
            "body": c.body,
            "author_name": c.author.username,
            "author_avatar": c.author.avatar_url,
            "created_at": c.created_at,
            "replies": [_serialize(r) for r in c.replies],
        }

    return [_serialize(c) for c in comments if c.parent_id is None]


async def add_comment(
    post_id: uuid.UUID, author_id: uuid.UUID,
    data: CommentCreate, db: AsyncSession,
) -> Comment:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пост не найден")
    comment = Comment(post_id=post_id, author_id=author_id, **data.model_dump())
    db.add(comment)
    await db.flush()
    return comment


async def delete_comment(
    comment_id: uuid.UUID, author_id: uuid.UUID, db: AsyncSession,
) -> dict:
    comment = await db.get(Comment, comment_id)
    if not comment or comment.author_id != author_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа")
    await db.delete(comment)
    return {"message": "Комментарий удалён"}


# ─── Helper ───────────────────────────────────────────────────────────────────

async def _get_owned_post(post_id: uuid.UUID, author_id: uuid.UUID, db: AsyncSession) -> Post:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пост не найден")
    if post.author_id != author_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа")
    return post
