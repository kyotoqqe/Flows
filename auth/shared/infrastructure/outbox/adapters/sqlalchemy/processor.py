from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.infrastructure.outbox.adapters.sqlalchemy.orm import outbox_table
from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus
from shared.infrastructure.outbox.ports.processor import AbstractOutboxProcessor


class SQLAlchemyOutboxProcessor(AbstractOutboxProcessor):
    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self.sessionmaker = sessionmaker

    async def __aenter__(self):
        self._session: AsyncSession = self.sessionmaker()
        return await super().__aenter__()

    async def __aexit__(self, *args, **kwargs):
        await super().__aexit__(*args, **kwargs)
        try:
            await self._session.commit()
        except Exception:
            self._session.expunge_all()
            await self._session.rollback()
        await self._session.close()

    async def get_pending_messages(self, batch_len: int):
        stmt = (
            select(OutboxMessage)
            .filter_by(status="pending")
            .with_for_update(skip_locked=True)
            .limit(batch_len)
        )
        res = await self._session.execute(stmt)
        return list(res.scalars())

    async def mark_message_as(self, message: OutboxMessage, status: OutboxStatus):
        stmt = update(OutboxMessage).filter_by(event_id=message.event_id).values(status=status)
        await self._session.execute(stmt)

    # delayed
    async def get_messages_by_event_id(self, id_list: list[UUID]):
        stmt = (
            select(OutboxMessage)
            .filter(OutboxMessage.event_id.in_(id_list))
            .with_for_update(skip_locked=True)
        )
        res = await self._session.execute(stmt)
        return list(res.scalars())
