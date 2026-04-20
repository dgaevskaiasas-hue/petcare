# app/controllers/auth_controller.py
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Response, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RefreshToken, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"id": str(user.id), "email": user.email, "role": user.role, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _create_refresh_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"id": user_id, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refreshToken",
        value=token,
        httponly=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        secure=settings.APP_ENV == "production",
    )


async def register(data: RegisterRequest, db: AsyncSession, response: Response) -> TokenResponse:
    exists = await db.scalar(
        select(User).where((User.email == data.email.lower()) | (User.username == data.username))
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email или имя пользователя уже заняты")

    user = User(
        email=data.email.lower(),
        password=pwd_context.hash(data.password),
        username=data.username,
    )
    db.add(user)
    await db.flush()  # получаем user.id до коммита

    refresh = _create_refresh_token(str(user.id))
    db.add(RefreshToken(
        user_id=user.id,
        token=refresh,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))

    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=_create_access_token(user), user=UserOut.model_validate(user))


async def login(data: LoginRequest, db: AsyncSession, response: Response) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")

    refresh = _create_refresh_token(str(user.id))
    db.add(RefreshToken(
        user_id=user.id,
        token=refresh,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))

    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=_create_access_token(user), user=UserOut.model_validate(user))


async def refresh_token(token: str | None, db: AsyncSession, response: Response) -> dict:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh-токен отсутствует")

    stored = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    if not stored:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Токен отозван или истёк")

    user = await db.get(User, stored.user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь не найден")

    # Rotation: удаляем старый, выдаём новый
    await db.delete(stored)
    new_refresh = _create_refresh_token(str(user.id))
    db.add(RefreshToken(
        user_id=user.id,
        token=new_refresh,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))

    _set_refresh_cookie(response, new_refresh)
    return {"access_token": _create_access_token(user), "token_type": "bearer"}


async def logout(token: str | None, db: AsyncSession, response: Response) -> dict:
    if token:
        stored = await db.scalar(select(RefreshToken).where(RefreshToken.token == token))
        if stored:
            await db.delete(stored)
    response.delete_cookie("refreshToken")
    return {"message": "Выход выполнен"}
