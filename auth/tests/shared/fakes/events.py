from dataclasses import dataclass

from shared.application.events.events import IntegrationEvent
from shared.domain.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class IUserCreated(DomainEvent):
    id: int
    username: str
    email: str
    is_active: bool
    password_hash: str


@dataclass(frozen=True, kw_only=True)
class EmptyEvent(DomainEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UserCreated(IntegrationEvent):
    mapped_event = IUserCreated

    id: int
    username: str
    is_active: bool


@dataclass(frozen=True, kw_only=True)
class UserBanned(IntegrationEvent):
    mapped_event = IUserCreated

    id: int
    reason: str
