from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from shared.domain.aggregates import Aggregate
from src.auth.domain.events import UserBanned, UserCreated, UserDeactivated
from src.auth.domain.exceptions import (
    OauthProviderException,
    RefreshSessionIsExpired,
    RefreshSessionLimitExceeded,
    RefreshSessionNotFound,
    UserBanException,
)
from src.auth.domain.value_objs import (
    BanInfo,
    Email,
    OauthProvider,
    PasswordHash,
    Provider,
    UserId,
    UserRole,
    SessionGroupId,
)
from src.auth.domain.entities import RefreshSession

REFRESH_SESSIONS_LIMIT = 5


class User(Aggregate[UserId]):
    def __init__(
        self, email: Email, version_num: int, password_hash: PasswordHash | None = None
    ) -> None:
        super().__init__(version_num)
        self.aggregate_id = UserId()
        self.email = email
        self.password_hash = password_hash
        self.role = UserRole.MEMBER
        self.is_active = False
        self.oauth_providers: list[OauthProvider] = []
        self.ban_info: BanInfo | None = None

    @classmethod
    def create(cls, email_str: str, password_hash_str: str | None = None):
        email = Email.create(email_str)
        password_hash = PasswordHash(value=password_hash_str) if password_hash_str else None

        instance = cls(email=email, password_hash=password_hash, version_num=1)
        instance.events.append(
            UserCreated(aggregate_id=instance.aggregate_id, email=instance.email)
        )
        return instance

    def add_oauth_provider(self, provider_user_id: str, provider: Provider):
        for oauth_provider in self.oauth_providers:
            if (
                provider_user_id == oauth_provider.provider_user_id
                and provider == oauth_provider.provider
            ):
                return

        self.oauth_providers.append(
            OauthProvider(
                user_id=self.aggregate_id, provider_user_id=provider_user_id, provider=provider
            )
        )

    def activate(self):
        self.is_active = True

    def unlink_oauth_provider(self, provider: Provider):
        for oauth_provider in self.oauth_providers:
            if provider == oauth_provider.provider:
                if len(self.oauth_providers) == 1 and self.password_hash is None:
                    raise OauthProviderException("You cannot unlink the only sign-in method.")

                self.oauth_providers.remove(oauth_provider)

    def update_email(self, email_str: str):
        new_email = Email.create(email_str)
        self.email = new_email

    def update_password(self, password_hash_str: str):
        new_password_hash = PasswordHash(value=password_hash_str)
        self.password_hash = new_password_hash

    def deactivate(self):
        self.is_active = False
        self.events.append(UserDeactivated(user_id=self.aggregate_id.value))

    def ban(self, banned_by: UserId, expires_at: datetime | None = None, reason: str | None = None):
        if self.ban_info is not None:
            raise UserBanException("User already have ban")

        banned_at = datetime.now(tz=timezone.utc)
        self.ban_info = BanInfo(
            user_id=self.aggregate_id,
            reason=reason,
            banned_at=banned_at,
            expires_at=expires_at,
        )

        self.events.append(
            UserBanned(
                user_id=self.aggregate_id.value,
                reason=reason,
                expires_at=expires_at,
                banned_by=banned_by.value,
                banned_at=banned_at,
            )
        )

    def unban(self):
        self.ban_info = None


class SessionGroup(Aggregate[SessionGroupId]):
    def __init__(
        self,
        user_id: UserId,
        version_num: int,
    ) -> None:
        super().__init__(version_num)
        self.aggregate_id = SessionGroupId()
        self.user_id = user_id
        self.refresh_sessions: list[RefreshSession] = []

    @classmethod
    def create(cls, user_id: UserId):
        instance = cls(user_id=user_id, version_num=1)
        return instance

    def add_refresh_session(
        self, user_agent: str, ip_addr: IPv4Address | IPv6Address
    ) -> RefreshSession:
        if len(self.refresh_sessions) == REFRESH_SESSIONS_LIMIT:
            raise RefreshSessionLimitExceeded

        refresh_session = RefreshSession(
            session_group_id=self.aggregate_id, user_agent=user_agent, ip_addr=ip_addr
        )

        self.refresh_sessions.append(refresh_session)
        return refresh_session

    def remove_refresh_session(self, refresh_token: UUID):
        for rs in self.refresh_sessions:
            if rs.refresh_token == refresh_token:
                self.refresh_sessions.remove(rs)

    def refresh_session(self, refresh_token: UUID):
        for rs in self.refresh_sessions:
            if rs.refresh_token == refresh_token:
                if rs.is_expired():
                    raise RefreshSessionIsExpired

                self.refresh_sessions.remove(rs)

                new_refresh_session = RefreshSession(
                    session_group_id=self.aggregate_id, user_agent=rs.user_agent, ip_addr=rs.ip_addr
                )
                self.refresh_sessions.append(new_refresh_session)
                return new_refresh_session

        raise RefreshSessionNotFound

    def delete_all_refreesh_sessions(self):
        self.refresh_sessions = []

    def __len__(self) -> int:
        return len(self.refresh_sessions)
