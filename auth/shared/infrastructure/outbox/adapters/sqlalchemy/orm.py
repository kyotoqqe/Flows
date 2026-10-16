from sqlalchemy import JSON, UUID, BigInteger, Column, DateTime, Enum, Integer, String, Table, func

from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus
from shared.infrastructure.shared.sqlalchemy.base import mapper_registry, metadata_obj

outbox_table = Table(
    "outbox",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column(
        "event_id",
        UUID(as_uuid=True),
        nullable=False,
    ),
    Column("type", String(150), nullable=False),
    Column("version", Integer, nullable=False),
    Column("correlation_id", UUID(as_uuid=True), nullable=False),
    Column("timestamp", BigInteger, nullable=False),
    Column("payload", JSON, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("processed_at", DateTime),
    Column("status", Enum(OutboxStatus), default=OutboxStatus.pending, nullable=False),
    Column("error", String(150)),
)


def start_mappers():
    return mapper_registry.map_imperatively(OutboxMessage, outbox_table)
