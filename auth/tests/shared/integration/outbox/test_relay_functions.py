import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import select

from scripts.relay import process_message, publish_outbox_batch, retray_messages
from shared.infrastructure.ipc.messaging.adapters.rabbitmq.publisher import RabbitMQPublisher
from shared.infrastructure.outbox.adapters.sqlalchemy.processor import SQLAlchemyOutboxProcessor
from shared.infrastructure.outbox.adapters.sqlalchemy.writer import SQLAlchemyOutboxWriter
from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus
from tests.fixtures.application.events import UserBanned, UserCreated


@pytest.mark.asyncio
async def test_message_processing(generate_outbox_messages, sessionmaker_fixture):
    await generate_outbox_messages(1)

    publisher = RabbitMQPublisher()
    publisher.exchange_name = "test.events.direct"
    queue_name = str(uuid4())
    publisher.router_keys_for_queues = {queue_name: ["user.created"]}

    processor = SQLAlchemyOutboxProcessor(sessionmaker=sessionmaker_fixture)

    async with publisher:
        await publisher.bootstrap()

        async with processor:
            stmt = select(OutboxMessage)
            res = await processor._session.execute(stmt)
            msg = res.scalar_one_or_none()
            if not msg is None:
                await process_message(publisher=publisher, outbox=processor, outbox_message=msg)

            messages = await processor.get_pending_messages(1)
            assert len(messages) == 0


@pytest.mark.asyncio
async def test_multiple_batch_publishing(generate_outbox_messages, sessionmaker_fixture):
    await generate_outbox_messages(30)

    publisher = RabbitMQPublisher()
    publisher.exchange_name = "test.events.direct"
    queue_name = str(uuid4())
    print(queue_name)
    publisher.router_keys_for_queues = {queue_name: ["user.created"]}

    processor = SQLAlchemyOutboxProcessor(sessionmaker=sessionmaker_fixture)

    async with publisher:
        await publisher.bootstrap()

        tasks = []
        retray = set()
        for i in range(3):
            task = asyncio.create_task(
                publish_outbox_batch(
                    outbox=SQLAlchemyOutboxProcessor(sessionmaker=sessionmaker_fixture),
                    publisher=publisher,
                    messages_ids_for_retray=retray,
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(results)
        print(retray)

    async with processor:
        stmt = select(OutboxMessage).filter_by(status=OutboxStatus.processed)
        res = await processor._session.execute(stmt)
        assert len(res.scalars().all()) == 30


@pytest.mark.asyncio
async def test_messages_retry(setup_database, sessionmaker_fixture):
    events_id = set()
    async with sessionmaker_fixture() as session:
        writer = SQLAlchemyOutboxWriter(session=session)
        for i in range(12):
            if i < 7:
                event = UserCreated(
                    type="UserCreated",
                    correlation_id=uuid4(),
                    timestamp=17891124516,
                    event_id=uuid4(),
                    id=22,
                    username="test",
                    is_active=True,
                )
            else:
                event = UserBanned(
                    type="UserBanned",
                    correlation_id=uuid4(),
                    timestamp=17891124516,
                    event_id=uuid4(),
                    id=22,
                    reason="prost)",
                )
            events_id.add(event.event_id)
            await writer.save(event)
        await session.commit()

    publisher = RabbitMQPublisher()
    publisher.exchange_name = "test.events.direct"
    queue_name = str(uuid4())
    print(queue_name)
    publisher.router_keys_for_queues = {queue_name: ["user.created"]}

    writer = None
    processor = SQLAlchemyOutboxProcessor(sessionmaker=sessionmaker_fixture)

    async with publisher:
        await publisher.bootstrap()
        await publisher.channel.queue_delete("unroutable.aq")

        async with processor:
            await retray_messages(
                outbox=processor, publisher=publisher, messages_ids_for_retray=events_id
            )

            stmt1 = select(OutboxMessage).filter_by(status=OutboxStatus.processed)
            stmt2 = select(OutboxMessage).filter_by(status=OutboxStatus.failed)
            res1 = await processor._session.execute(stmt1)
            res2 = await processor._session.execute(stmt2)

            r1 = res1.scalars().all()
            r2 = res2.scalars().all()
            print(f"r1 {r1}")
            print(f"r2 {r2}")

            assert len(r1) == 7
            assert len(r2) == 5
