from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.inbox.ports.inbox import AbstractInbox
from shared.infrastructure.inbox.ports.message import InboxMessage


class SQlAlchemyInbox(AbstractInbox):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message_id: UUID, correlation_id: UUID, type: str, handler_name: str):
        stmt = insert(InboxMessage).values(
            message_id=message_id,
            handler_name=handler_name,
            correlation_id=correlation_id,
            type=type,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_message(self, *filter, **filter_by) -> InboxMessage | None:
        stmt = select(InboxMessage).filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
