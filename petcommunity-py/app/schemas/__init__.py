# app/schemas/__init__.py
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
)
from app.schemas.pet import (
    PetCreate,
    PetUpdate,
    PetOut,
    HealthRecordCreate,
    HealthRecordOut,
    BehaviourLogCreate,
    BehaviourLogOut,
    BehaviourAlert,
    BehaviourLogResponse,
)
from app.schemas.forum import (
    PostCreate,
    PostUpdate,
    PostOut,
    CommentCreate,
    CommentOut,
)
from app.schemas.ai import (
    ChatMessageRequest,
    ChatMessageResponse,
)
