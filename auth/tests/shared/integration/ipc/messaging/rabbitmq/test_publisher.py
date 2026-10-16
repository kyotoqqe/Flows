import json
import uuid

import pytest
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractQueue

from shared.infrastructure.ipc.messaging.adapters.rabbitmq.publisher import RabbitMQPublisher


@pytest.mark.asyncio
async def test_message_publishing_success():
    publisher = RabbitMQPublisher()
    publisher.exchange_name = "test.events.direct"
    queue_name = str(uuid.uuid4())
    publisher.router_keys_for_queues = {queue_name: ["user.created"]}

    async with publisher:
        await publisher.bootstrap()
        test_payload = {
            "message_id": "msg-12345",
            "timestamp": 1710000000,
            "type": "UserCreated",
            "correlation_id": "corr-6789",
            "body": {"user_id": 42, "email": "test@example.com"},
        }

        await publisher.publish(test_payload)

        queue: AbstractQueue = await publisher.channel.get_queue(queue_name)
        msg = await queue.get(timeout=2.0)
        assert isinstance(msg, IncomingMessage)
        async with msg.process(ignore_processed=True):
            payload = msg.body.decode()
            data = json.loads(payload)
            assert msg.message_id == "msg-12345"
            assert data == {"user_id": 42, "email": "test@example.com"}
            assert msg.type == "user.created"

        await publisher.channel.exchange_delete(publisher.exchange_name)
        await publisher.channel.queue_delete(queue_name)


@pytest.mark.asyncio
async def test_message_publishing_failed():
    publisher = RabbitMQPublisher()
    publisher.exchange_name = "test.events.direct"
    queue_name = str(uuid.uuid4())
    publisher.router_keys_for_queues = {queue_name: ["user.created"]}

    async with publisher:
        await publisher.bootstrap()
        test_payload = {
            "message_id": "msg-12345",
            "timestamp": 1710000000,
            "type": str(uuid.uuid4()),
            "correlation_id": "corr-6789",
            "body": {"user_id": 42, "email": "test@example.com"},
        }

        await publisher.channel.queue_delete("unroutable.aq")
        try:
            await publisher.publish(test_payload)
        except Exception as e:
            assert isinstance(e, TypeError)
