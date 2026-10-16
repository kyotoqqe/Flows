from abc import ABC, abstractmethod
from uuid import UUID

from shared.infrastructure.inbox.ports.message import InboxMessage


class AbstractInbox(ABC):
    @abstractmethod
    async def save(self, message_id: UUID, correlation_id: UUID, type: str, handler_name: str):
        pass

    @abstractmethod
    async def get_message(self, *filter, **filter_by) -> InboxMessage | None:
        pass

    def __len__(self):
        return 0
