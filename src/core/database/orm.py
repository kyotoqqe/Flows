from sqlalchemy import Table, Column, Integer, String, DateTime, func, select
from sqlalchemy.orm import relationship, column_property

from src.core.database.metadata import mapper_registry

images_table = Table(
    "images",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("key", String(150), nullable=False),
    Column("alt_text", String(150), nullable=True),
    Column("checksum", String, unique=True, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
)

def start_mappers():
    from src.core.domain.value_obj import Image
    from src.profiles.domain.entities import Profile
    from src.profiles.infrastructure.database.orm import profiles_table

    mapper_registry.map_imperatively(Image, images_table, properties={
        "profiles": relationship(Profile, back_populates="image"),
        "ref_count": column_property(
            select(func.count(Profile.id))\
            .where(Profile.avatar_id == images_table.c.id)\
            .correlate_except(Profile)\
            .scalar_subquery()
        )
    })