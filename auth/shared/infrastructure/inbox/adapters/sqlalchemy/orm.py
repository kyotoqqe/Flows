from sqlalchemy import UUID, Column, DateTime, Integer, String, Table, UniqueConstraint, func

from shared.infrastructure.inbox.ports.message import InboxMessage
from shared.infrastructure.shared.sqlalchemy.base import mapper_registry, metadata_obj

inbox_table = Table(
    "inbox",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("message_id", UUID(as_uuid=True)),
    Column("handler_name", String(50)),
    Column("processed_at", DateTime, server_default=func.now()),
    UniqueConstraint("message_id", "handler_name", name="inbox_unq"),
)


def start_mappers():
    return mapper_registry.map_imperatively(InboxMessage, inbox_table)
