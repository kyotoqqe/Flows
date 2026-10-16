import asyncio
from concurrent.futures import process
import json

from aio_pika import ExchangeType
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractQueue,
)

from shared.application.messagebus import MessageBus
from shared.infrastructure.ipc.messaging.adapters.rabbitmq.base import RabbitBase
from shared.infrastructure.ipc.messaging.ports.consumer import AbstractConsumer

# move to rabbitmq settings
PREFETCH_COUNT = 20


# test message handling with exception
# test message handling with success
class RabbitMQConsumer(RabbitBase, AbstractConsumer):
    exchange_name: str = ""
    queue_name: str = ""

    def convert_routing_key(self, routing_key: str):
        name = ""

        for i in range(len(routing_key)):
            if i == 0 or i > 0 and routing_key[i - 1] == ".":
                name += routing_key[i].upper()
            elif routing_key[i] == ".":
                continue
            else:
                name += routing_key[i]

        return name

    async def bootstrap(self):
        self.queue: AbstractQueue = await self.channel.declare_queue(
            name=self.queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "events.dlx",
                "x-dead-letter-routing-key": f"dead.{self.queue_name}",
                "x-max-length": 50_000,
            },
        )

        await self.channel.declare_exchange("events.dlx", type=ExchangeType.DIRECT, durable=True)
        dlq: AbstractQueue = await self.channel.declare_queue(
            f"dead.{self.queue_name}", durable=True
        )
        await dlq.bind("events.dlx", routing_key=f"dead.{self.queue_name}")

    async def _on_message(self, message: AbstractIncomingMessage):
        async with message.process(ignore_processed=True):
            payload = message.body.decode()
            body = json.loads(payload)
            if not message.routing_key:
                await message.nack(requeue=False)
                return
            msg_type = self.convert_routing_key(message.routing_key)
            print(msg_type)
            print(self.EVENT_REGISTRY.registry)
            data = {
                "type": msg_type,
                "correlation_id": message.correlation_id,
                "timestamp": message.timestamp,
                "message_id": message.message_id,
                "body": body,
            }

            try:
                messagebus = MessageBus()
                message_for_bus = super()._get_event_or_command_from_message(data)

                await messagebus.handle(message=message_for_bus)
                await message.ack()
            except Exception as e:
                print(e)
                await message.nack(requeue=False)

    async def consume(self):
        await self.channel.set_qos(prefetch_count=PREFETCH_COUNT)
        await self.queue.consume(self._on_message)

        await asyncio.Future()
