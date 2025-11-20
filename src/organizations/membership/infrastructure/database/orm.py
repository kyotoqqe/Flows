from sqlalchemy import Table, Column, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship

from src.core.database.metadata import mapper_registry

from src.organizations.membership.domain.value_obj import MemberRole

members_table = Table(
    "members",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("profile_id", ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
    Column("role", Enum(MemberRole), default=MemberRole.member, nullable=False),
    Column("is_visible", Boolean, nullable=False, default=True),
    Column("can_change_organization_info", Boolean, nullable=False, default=False),
    Column("can_invite_members", Boolean, nullable=False, default=False),
    Column("can_create_shows", Boolean, nullable=False, default=False),
    Column("can_add_venue_requests", Boolean, nullable=False, default=False),
)

memberships_table = Table(
    "memberships",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("version_num", Integer, nullable=False, server_default="0")
)

def start_mappers():
    from src.organizations.membership.domain.entities import Member, Membership

    mapper_registry.map_imperatively(Member, members_table)

    mapper_registry.map_imperatively(
        Membership, memberships_table,
        properties = {
            "owner": relationship(Member, uselist=False),
            "members": relationship(Member, cascade="all, delete-orphan")
        }
    )