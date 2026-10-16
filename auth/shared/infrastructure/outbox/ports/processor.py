from abc import ABC, abstractmethod
from uuid import UUID

from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus


class AbstractOutboxProcessor(ABC):
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_pending_messages(self, batch_len: int) -> list[OutboxMessage]:
        pass

    @abstractmethod
    async def mark_message_as(self, message: OutboxMessage, status: OutboxStatus):
        pass

    @abstractmethod
    async def get_messages_by_event_id(self, id_list: list[UUID]) -> list[OutboxMessage]:
        pass
