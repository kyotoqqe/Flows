from sqlalchemy import func, Table, Column, ForeignKey, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship

from src.core.database.metadata import mapper_registry

from src.profiles.domain.value_obj import ProfileType

profiles_table = Table(
    "profiles",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
    Column("first_name", String(50), nullable=True),
    Column("last_name", String(50), nullable=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("username", String(50), nullable=False, unique=True),
    Column("avatar_id", ForeignKey("images.id", ondelete="SET NULL"), nullable=True),
    Column("profile_type", Enum(ProfileType), default=ProfileType.public,nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), nullable=False)
)

relationships_groups = Table(
    "relationships_groups",
    mapper_registry.metadata,
    Column("relation_id", String(50), primary_key=True, autoincrement=False),
    Column("version_num", Integer, nullable=False, server_default="0")
)

relationships_table = Table(
    "relationships",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
    Column("follower_id", ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    Column("following_id", ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    Column("relation_id", String(50), ForeignKey("relationships_groups.relation_id", ondelete="CASCADE"), nullable=False),
    Column("is_followed",Boolean, default=False, nullable=False),
    Column("is_blocked",Boolean, default=False, nullable=False),
)


def start_mappers():
    from src.profiles.domain.entities import Profile, Relationship, RelationshipGroup

    from src.core.domain.value_obj import Image

    mapper_registry.map_imperatively(
        Profile, profiles_table, properties={
            "followers": relationship(Profile, 
                                      secondary=relationships_table, 
                                      primaryjoin=profiles_table.c.id==relationships_table.c.following_id,
                                      secondaryjoin=profiles_table.c.id==relationships_table.c.follower_id,
                                      back_populates="following"),
            "following": relationship(Profile, 
                                      secondary=relationships_table, 
                                      primaryjoin=profiles_table.c.id==relationships_table.c.follower_id,
                                      secondaryjoin=profiles_table.c.id==relationships_table.c.following_id,
                                      back_populates="followers"),
            "image": relationship(Image, back_populates="profiles")
        }
    )

    relationships_mapper = mapper_registry.map_imperatively(
        Relationship, relationships_table
    )
    mapper_registry.map_imperatively(
        RelationshipGroup, relationships_groups, properties = {
            "relationships": relationship(relationships_mapper, cascade="all, delete-orphan")
        },
        
    )