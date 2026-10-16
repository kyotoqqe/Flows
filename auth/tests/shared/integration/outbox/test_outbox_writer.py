from uuid import uuid4

import pytest
from sqlalchemy import select

from shared.infrastructure.outbox.adapters.sqlalchemy.writer import SQLAlchemyOutboxWriter
from shared.infrastructure.outbox.ports.message import OutboxMessage
from tests.fixtures.application.events import UserCreated


@pytest.mark.asyncio
async def test_outbox_writer(setup_database, sessionmaker_fixture):
    async with sessionmaker_fixture() as session:
        writer = SQLAlchemyOutboxWriter(session=session)
        event = UserCreated(
            type="UserCreated",
            correlation_id=uuid4(),
            timestamp=1789112451658,
            event_id=uuid4(),
            id=22,
            username="test",
            is_active=True,
        )

        await writer.save(event)
        await session.commit()

        stmt = select(OutboxMessage)
        res = await session.execute(stmt)
        obj = res.scalar_one_or_none()
        assert isinstance(obj, OutboxMessage)

    # await session.close()
