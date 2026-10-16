from asyncio import events
import datetime

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.application.events.events import IntegrationEvent
from shared.domain.events import DomainEvent
from shared.infrastructure.outbox.ports.message import OutboxMessage
from shared.infrastructure.outbox.ports.writer import AbstractOutboxWriter


class SQLAlchemyOutboxWriter(AbstractOutboxWriter):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, event: IntegrationEvent | DomainEvent):

        stmt = insert(OutboxMessage).values(
            event_id=event.event_id,
            type=event.__class__.__name__,
            version=1,
            correlation_id=event.correlation_id,
            timestamp=int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000),
            payload=event.payload,
        )
        await self._session.execute(stmt)
