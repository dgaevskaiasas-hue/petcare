# app/routers/auth.py
from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import controllers
from app.controllers.auth_controller import login, logout, refresh_token, register
from app.middleware.auth import CurrentUser, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from config.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def _register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    return await register(data, db, response)


@router.post("/login", response_model=TokenResponse)
async def _login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    return await login(data, db, response)


@router.post("/refresh")
async def _refresh(
    response: Response,
    refreshToken: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await refresh_token(refreshToken, db, response)


@router.post("/logout")
async def _logout(
    response: Response,
    refreshToken: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await logout(refreshToken, db, response)


@router.get("/me", response_model=UserOut)
async def _me(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.user import User
    user = await db.get(User, current_user.id)
    return UserOut.model_validate(user)
