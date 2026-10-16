from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from shared.domain.events import DomainEvent
from src.auth.domain.value_objs import Email, UserId


@dataclass(frozen=True, kw_only=True)
class UserCreated(DomainEvent):
    aggregate_id: UserId
    email: Email


@dataclass(frozen=True, kw_only=True)
class UserBanned(DomainEvent):
    user_id: UUID
    banned_by: UUID
    reason: str | None = None
    expires_at: datetime | None = None
    banned_at: datetime


@dataclass(frozen=True, kw_only=True)
class UserDeactivated(DomainEvent):
    user_id: UUID
