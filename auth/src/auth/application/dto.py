import time
from dataclasses import dataclass, field


from shared.application.dto import BaseDTO
from src.auth.domain.value_objs import Provider

USER_TOKEN_ACTIVATION_LIFESPAN_MINUTES = 60 * 15


@dataclass(frozen=True, kw_only=True)
class UserActivationTokenPayload(BaseDTO):
    user_id: str
    expires_at: float = field(
        default_factory=lambda: time.time() + USER_TOKEN_ACTIVATION_LIFESPAN_MINUTES
    )


@dataclass(frozen=True, kw_only=True)
class OauthUserCredentials(BaseDTO):
    email: str
    provider_user_id: str
    provider: Provider


@dataclass(frozen=True, kw_only=True)
class TokensPair(BaseDTO):
    access_token: str
    refresh_token: str
