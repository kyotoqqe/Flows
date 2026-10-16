from enum import Enum
from uuid import UUID


class OutboxStatus(Enum):
    pending = "Pending"
    processed = "Processed"
    failed = "Failed"


class OutboxMessage:
    def __init__(
        self,
        event_id: UUID,
        correlation_id: UUID,
        type: str,
        timestamp: int,
        payload: dict,
        status: OutboxStatus = OutboxStatus.pending,
    ):
        self.event_id = event_id
        self.correlation_id = correlation_id
        self.type = type
        self.timestamp = timestamp
        self.payload = payload
        self.status = status
        self.error: str | None = None
