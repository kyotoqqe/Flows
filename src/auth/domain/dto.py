import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from src.core.domain.dto import BaseDTO

BASE64_TOKEN_EXPIRE_MINUTES = 15

@dataclass(frozen=True)
class TokenPayload(BaseDTO):
    user_id: int

@dataclass(frozen=True)
class Base64TokenPayload(TokenPayload):
    exp: str = field(
        default_factory=lambda: (datetime.now(timezone.utc) + \
                                 timedelta(minutes=BASE64_TOKEN_EXPIRE_MINUTES)).isoformat()
    )


@dataclass(frozen=True)
class JWTTokenPayload(TokenPayload):
    pass

@dataclass(frozen=True)
class Token(BaseDTO):
    access: str
    refresh: uuid.UUID