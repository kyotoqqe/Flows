from dataclasses import dataclass, field
from typing import Optional

from src.core.domain.entities import AggregateRoot, Entity

from src.organizations.membership.domain.value_obj import MemberRole

@dataclass
class Member(Entity):
    profile_id: int
    role: MemberRole
    description: Optional[str] = None
    can_change_organization_info: bool = field(default=False)
    can_invite_members: bool = field(default=False) 
    can_create_shows: bool = field(default=False)
    can_add_venue_requests: bool = field(default=False)

@dataclass
class Membership(AggregateRoot):
    organization_id: int
    owner: Member
    members: list[Member]
