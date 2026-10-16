from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, Table, func

from shared.infrastructure.shared.sqlalchemy.base import mapper_registry, metadata_obj
from src.auth.domain.aggregate import User
from src.auth.domain.value_objs import UserRole
from src.auth.infrastructure.storage.adapters.sqlalchemy.orm.types import (
    EmailDB,
    PasswordDB,
    UserIdDB,
)

users_table = Table(
    "users",
    metadata_obj,
    Column("aggregate_id", UserIdDB(), primary_key=True),
    Column("email", EmailDB(), unique=True, nullable=False),
    Column("password_hash", PasswordDB()),
    Column("role", Enum(UserRole), nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("version_num", Integer, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),
)


def start_mappers():
    mapper_registry.map_imperatively(
        User, users_table, properties={"version_num": users_table.c.version_num}
    )
