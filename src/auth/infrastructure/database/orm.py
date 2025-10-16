from sqlalchemy import Table, Column, Integer, String, Boolean, UUID, BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from src.core.database.metadata import mapper_registry

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False, unique=True,),
    Column("email", String(128), nullable=False, unique=True),
    Column("password", String(60), nullable=False),
    Column("active", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), nullable=False)
)

refresh_sessions_table = Table(
    "refresh_sessions",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
    Column("token", UUID, nullable=False, unique=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("expires_in", BigInteger, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False)
)


def start_mappers():
    from src.auth.domain.entities import User
    from src.auth.domain.value_obj import RefreshSession

    mapper_registry.map_imperatively(
        class_=User, 
        local_table=users_table,
        properties={
            "sessions": relationship(RefreshSession, backref="user")
        }  
    )
    mapper_registry.map_imperatively(class_=RefreshSession, local_table=refresh_sessions_table)