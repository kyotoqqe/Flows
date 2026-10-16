import datetime
from uuid import UUID

from shared.infrastructure.inbox.ports.inbox import AbstractInbox
from shared.infrastructure.inbox.ports.message import InboxMessage


class FakeInbox(AbstractInbox):
    def __init__(self) -> None:
        self.storage: set[InboxMessage] = set()

    async def save(self, message_id: UUID, correlation_id: UUID, type: str, handler_name: str):
        self.storage.add(
            InboxMessage(
                message_id=message_id,
                correlation_id=correlation_id,
                type=type,
                handler_name=handler_name,
                timestamp=int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000),
            )
        )

    async def get_message(self, *filter, **filter_by) -> InboxMessage | None:
        for msg in self.storage:
            for f, v in filter_by.items():
                msg_v = getattr(msg, f, None)

                if msg_v is not None and msg_v == v:
                    return msg

    def __len__(self):
        return len(self.storage)
