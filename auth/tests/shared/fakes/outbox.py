import datetime

from shared.application.events.events import IntegrationEvent
from shared.domain.events import DomainEvent
from shared.infrastructure.outbox.ports.message import OutboxMessage
from shared.infrastructure.outbox.ports.writer import AbstractOutboxWriter


class FakeOutboxWriter(AbstractOutboxWriter):
    def __init__(self) -> None:
        self.storage: set[OutboxMessage] = set()

    async def save(self, event: IntegrationEvent | DomainEvent):
        self.storage.add(
            OutboxMessage(
                event_id=event.event_id,
                correlation_id=event.correlation_id,
                type=event.__class__.__name__,
                timestamp=int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000),
                payload=event.payload,
            )
        )

    def __len__(self):
        return len(self.storage)
