import time
import uuid
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from shared.domain.entities import Entity
from src.auth.domain.value_objs import RefreshSessionId, SessionGroupId

REFRESH_TOKEN_EXPIRE_DAYS = 15


@dataclass(eq=False, kw_only=True)
class RefreshSession(Entity):
    id: RefreshSessionId = field(default_factory=RefreshSessionId)
    session_group_id: SessionGroupId
    user_agent: str
    ip_addr: IPv4Address | IPv6Address
    refresh_token: UUID = field(default_factory=uuid.uuid4)
    expires_at: float = field(
        default_factory=lambda: time.time() + (60 * 60 * 24 * REFRESH_TOKEN_EXPIRE_DAYS)
    )

    def is_expired(self) -> bool:
        return time.time() > self.expires_at
