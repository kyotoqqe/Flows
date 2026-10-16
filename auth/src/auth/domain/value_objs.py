import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

from shared.domain.value_objs import EntityId, ValueObj
from src.auth.domain.exceptions import InvalidEmailError, WeakPassword


@dataclass(frozen=True, kw_only=True)
class UserId(EntityId):
    pass


@dataclass(frozen=True, kw_only=True)
class SessionGroupId(EntityId):
    pass


@dataclass(frozen=True, kw_only=True)
class Email(ValueObj):
    value: str

    @classmethod
    def create(cls, email: str):
        email_pattern = r"^(?!\.)([\w]{1,32}\.)*[\w]{1,32}@(?!\-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$"

        if re.fullmatch(email_pattern, email) is None:
            raise InvalidEmailError

        return cls(value=email)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, kw_only=True)
class PasswordHash(ValueObj):
    value: str

    @classmethod
    def validate_raw_password(cls, raw_password: str):
        password_pattern = (
            r"""(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,64}"""
        )

        if re.fullmatch(password_pattern, raw_password) is None:
            raise WeakPassword(
                "Password is too weak.\
                          It must be at least 8 characters long and include digits,\
                          uppercase and lowercase letters, and at least one special symbol."
            )
        return raw_password

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, kw_only=True)
class BanInfo(ValueObj):
    user_id: UserId
    reason: str | None = None
    banned_at: datetime
    expires_at: datetime | None = None
    is_active: bool = field(default=True)


class UserRole(str, Enum):
    MEMBER = auto()
    ADMIN = auto()
    OWNER = auto()


class Provider(Enum):
    GOOGLE = auto()
    SPOTIFY = auto()


@dataclass(frozen=True, kw_only=True)
class OauthProvider(ValueObj):
    user_id: UserId
    provider: Provider
    provider_user_id: str


@dataclass(frozen=True, kw_only=True)
class RefreshSessionId(EntityId):
    pass
