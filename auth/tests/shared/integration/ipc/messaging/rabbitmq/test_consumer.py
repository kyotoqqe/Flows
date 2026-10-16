import asyncio
import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from aio_pika import IncomingMessage

from shared.application.handlers.registry import handlers_registry
from shared.infrastructure.ipc.messaging.adapters.rabbitmq.consumer import RabbitMQConsumer
from shared.infrastructure.ipc.messaging.adapters.rabbitmq.publisher import RabbitMQPublisher
from tests.fixtures.application.events import UserCreated
from tests.fixtures.application.handlers import UserCreatedHandler


@pytest.mark.asyncio
async def test_message_consuming():
    publisher = RabbitMQPublisher()
    publisher.exchange_name = "test.events.direct"
    queue_name = str(uuid4())
    publisher.router_keys_for_queues = {queue_name: ["user.created", "another.event"]}
    payload_success = {
        "message_id": "msg-12345",
        "timestamp": 1710000000,
        "type": "UserCreated",
        "correlation_id": "corr-6789",
        "body": {"id": 42, "username": "test", "is_active": True},
    }

    payload_failed = {
        "message_id": "msg-12345",
        "timestamp": 1710000000,
        "type": "AnotherEvent",
        "correlation_id": "corr-6789",
        "body": {"info": "another info"},
    }

    async with publisher:
        await publisher.bootstrap()
        await publisher.publish(payload_success)
        await publisher.publish(payload_failed)

    consumer = RabbitMQConsumer()

    consumer.queue_name = queue_name
    consumer.EVENT_REGISTRY.register(UserCreated)
    print(consumer.EVENT_REGISTRY)
    mock_handler = AsyncMock(spec=UserCreatedHandler)
    handlers_registry.register(mock_handler, UserCreated)

    async with consumer:
        await consumer.bootstrap()
        consume_task = asyncio.create_task(consumer.consume())

        await asyncio.sleep(3.0)
        consume_task.cancel()

        try:
            await consume_task
        except asyncio.CancelledError:
            pass

        queue = await consumer.channel.get_queue(queue_name)
        msg = await queue.get(fail=False)
        assert msg is None
        mock_handler.assert_awaited_once()

        dlq_name = f"dead.{queue_name}"
        dlq = await consumer.channel.get_queue(dlq_name)
        dlq_msg = await dlq.get(fail=False)
        assert isinstance(dlq_msg, IncomingMessage)

        async with dlq_msg.process(ignore_processed=True):
            payload = dlq_msg.body.decode()
            body = json.loads(payload)
            assert dlq_msg.headers["x-death"][0]["routing-keys"] == ["another.event"]
            assert body == {"info": "another info"}

        await consumer.channel.queue_delete(queue_name)
        await consumer.channel.queue_delete(dlq_name)
