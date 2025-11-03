import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from src.core.domain.dto import BaseDTO

from src.auth.domain.value_obj import UserRole
from src.auth.infrastructure.jwt.config import jwt_settings

BASE64_TOKEN_EXPIRE_MINUTES = 15

@dataclass(frozen=True)
class TokenPayload(BaseDTO):
    user_id: int

#change name
@dataclass(frozen=True)
class Base64TokenPayload(TokenPayload):
    username: str
    exp: str = field(
        default_factory=lambda: (datetime.now(timezone.utc) + \
                                 timedelta(minutes=BASE64_TOKEN_EXPIRE_MINUTES)).isoformat()
    )

class PasswordResetTokenPayload(TokenPayload):
    exp: str = field(
        default_factory=lambda: (datetime.now(timezone.utc) + \
                                 timedelta(minutes=BASE64_TOKEN_EXPIRE_MINUTES)).isoformat()
    )
@dataclass(frozen=True)
class JWTTokenPayload(TokenPayload):
    role:UserRole
    exp: str = field(
        default_factory=lambda: (datetime.now(timezone.utc) + \
                                 timedelta(minutes=jwt_settings.access_token_expire_minutes)).isoformat()
    )

@dataclass(frozen=True)
class Token(BaseDTO):
    access: str
    refresh: uuid.UUID