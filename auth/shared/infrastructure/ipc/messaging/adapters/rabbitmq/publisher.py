import json
from typing import TypedDict

from aio_pika import DeliveryMode, ExchangeType
from aio_pika import Message as AioMessage
from aio_pika.abc import AbstractExchange, AbstractQueue
from pamqp.commands import Basic

from shared.infrastructure.ipc.messaging.adapters.rabbitmq.base import RabbitBase
from shared.infrastructure.ipc.messaging.ports.publisher import AbstractPublisher


# create base class from this
class RabbitMQMessage(TypedDict):
    message_id: str
    timestamp: int
    type: str
    correlation_id: str | None
    body: dict | None


class RabbitMQPublisher(RabbitBase, AbstractPublisher):
    exchange_name: str = ""
    router_keys_for_queues: dict[str, list[str]]

    def routing_key_builder(self, message_type: str):
        rouning_key = ""
        for i in range(len(message_type)):
            if message_type[i].isupper():
                rouning_key += message_type[i].lower() if i == 0 else f".{message_type[i].lower()}"
            else:
                rouning_key += message_type[i]

        return rouning_key

    async def bootstrap(self):
        self.exchange: AbstractExchange = await self.channel.declare_exchange(
            name=self.exchange_name,
            type=ExchangeType.DIRECT,
            durable=True,
            arguments={"alternate-exchange": "events.ae"},
        )
        await self.channel.declare_exchange(
            name="events.ae",
            type=ExchangeType.FANOUT,
            durable=True,
        )
        ae_queue: AbstractQueue = await self.channel.declare_queue(
            name="unroutable.aq", durable=True
        )
        await ae_queue.bind("events.ae", routing_key="")

        for queue_name, routing_keys in self.router_keys_for_queues.items():
            queue: AbstractQueue = await self.channel.declare_queue(
                name=queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "events.dlx",
                    "x-dead-letter-routing-key": f"dead.{queue_name}",
                    "x-max-length": 50_000,
                },
            )

            for routing_key in routing_keys:
                await queue.bind(self.exchange, routing_key=routing_key)

    async def publish(self, message: dict):
        routing_key = self.routing_key_builder(message["type"])

        message_body = message["body"]
        message_json = json.dumps(message_body)

        message_id = message["message_id"]

        message_for_publish = AioMessage(
            message_id=message_id,
            type=routing_key,
            timestamp=message["timestamp"],
            correlation_id=message["correlation_id"],
            body=message_json.encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        confirmation = await self.exchange.publish(
            message=message_for_publish, routing_key=routing_key, timeout=5.0, mandatory=True
        )

        if not isinstance(confirmation, Basic.Ack):
            print("Pub error")
            raise TypeError("Publishing was failed")  # custom
