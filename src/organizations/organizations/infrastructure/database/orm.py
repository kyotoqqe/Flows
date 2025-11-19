from sqlalchemy import func, Table, Column, Integer, String, ForeignKey, DateTime


from src.core.database.metadata import mapper_registry

organizations_table = Table(
    "organizations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("name", String(128), nullable=False),
    Column("description", String(500), nullable=True),
    Column("nickname", String(32), nullable=False, unique=True),
    Column("owner_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), nullable=False)
)

def start_mappers():
    from src.organizations.organizations.domain.entities import Organization

    mapper_registry.map_imperatively(Organization, organizations_table)