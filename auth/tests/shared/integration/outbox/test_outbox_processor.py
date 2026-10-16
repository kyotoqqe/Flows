import pytest
from sqlalchemy import select

from shared.infrastructure.outbox.adapters.sqlalchemy.processor import SQLAlchemyOutboxProcessor
from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus


@pytest.mark.asyncio
async def test_outbox_processor(generate_outbox_messages, sessionmaker_fixture):
    await generate_outbox_messages(200)
    processor = SQLAlchemyOutboxProcessor(sessionmaker=sessionmaker_fixture)

    async with processor:
        stmt = select(OutboxMessage)
        res = await processor._session.execute(stmt)

        for message in res.scalars().all():
            await processor.mark_message_as(message, OutboxStatus.pending)

        messages = await processor.get_pending_messages(200)
        assert len(messages) == 200
