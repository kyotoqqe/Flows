from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from shared.application.commands import Command
from src.auth.domain.value_objs import Provider, UserRole


@dataclass(frozen=True, kw_only=True)
class RegisterUser(Command):
    email: str
    password: str


@dataclass(frozen=True, kw_only=True)
class RegisterOrLoginUserWithOauth(Command):
    code: str
    state: str
    user_agent: str
    ip_addr: IPv4Address | IPv6Address


@dataclass(frozen=True, kw_only=True)
class LoginUserWithPasword(Command):
    email: str
    password: str
    user_agent: str
    ip_addr: IPv4Address | IPv6Address


@dataclass(frozen=True, kw_only=True)
class LogOutUser(Command):
    user_id: UUID
    refresh_token: UUID


@dataclass(frozen=True, kw_only=True)
class RefreshUserSession(Command):
    user_id: UUID
    email: str
    role: UserRole
    is_active: bool
    refresh_token: UUID
    user_agent: str
    ip_addr: IPv4Address | IPv6Address


@dataclass(frozen=True, kw_only=True)
class ActivateUser(Command):
    activation_token: str


@dataclass(frozen=True, kw_only=True)
class UnlinkOauthProvider(Command):
    user_id: UUID
    provider: Provider


@dataclass(frozen=True, kw_only=True)
class BanUser(Command):
    user_id: UUID
    target_user_id: UUID
    expires_at: datetime | None = None
    reason: str | None = None


@dataclass(frozen=True, kw_only=True)
class UnbanUser(Command):
    user_id: UUID
    target_user_id: UUID


@dataclass(frozen=True, kw_only=True)
class DeactivateUser(Command):
    user_id: UUID


@dataclass(frozen=True, kw_only=True)
class DeleteRefreshSession(Command):
    user_id: UUID
    refresh_session_id: UUID
