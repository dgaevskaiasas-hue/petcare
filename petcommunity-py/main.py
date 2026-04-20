# main.py — точка входа FastAPI приложения PetCommunity
from contextlib import asynccontextmanager

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, pets, forum, ai
from app.utils.migrate import create_tables
from config.settings import settings


# ─── Socket.io (real-time: форум, уведомления) ────────────────────────────────

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.FRONTEND_URL,
)


@sio.event
async def connect(sid, environ):
    print(f"WS connected: {sid}")


@sio.event
async def join_forum(sid, data):
    await sio.enter_room(sid, "forum")


@sio.event
async def leave_forum(sid, data):
    await sio.leave_room(sid, "forum")


@sio.event
async def join_user(sid, user_id: str):
    await sio.enter_room(sid, f"user:{user_id}")


@sio.event
async def disconnect(sid):
    print(f"WS disconnected: {sid}")


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()          # создаём таблицы при старте (dev)
    yield


# ─── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="PetCommunity API",
    description="AI-powered информационный портал для владельцев домашних животных",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI — автоматически из Pydantic-схем
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router,  prefix="/api/v1")
app.include_router(pets.router,  prefix="/api/v1")
app.include_router(forum.router, prefix="/api/v1")
app.include_router(ai.router,    prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}


# ─── Монтируем Socket.io поверх ASGI ─────────────────────────────────────────

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
    )
