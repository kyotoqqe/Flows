import json
from dataclasses import asdict
from typing import Optional, Union
from aio_pika import ExchangeType, Message, DeliveryMode

from src.core.interfaces.message_broker import MessageBroker
from src.core.rabbitmq.connection import get_connection
from src.core.interfaces.events import AbstractEvent
from src.core.interfaces.commands import Command
from src.core.messagebus import MessageBus

class RabbitMQMessageBroker(MessageBroker):
    exchange = None
    broker_exchange = None
    broker_queue = None
    event_handlers=None,
    command_handlers=None
    router_keys_for_queues: Optional[dict[str, list[str]]] = None

    def routing_key_builder(self, message: Union[AbstractEvent, Command]):
        name = message.__class__.__name__
        rouning_key = ""
        for i in range(len(name)):
            if name[i].isupper():
                rouning_key += name[i].lower() if i == 0 else f".{name[i].lower()}"
            else:
                rouning_key += name[i]
        
        return rouning_key

    def convert_routing_key(self, routing_key: str):
        name = ""

        for i in range(len(routing_key)):
            if i == 0:
              name += routing_key[i].upper()
            elif i > 0 and routing_key[i-1] == ".":
              name += routing_key[i].upper()
            elif routing_key[i] == ".":
              continue
            else:
              name += routing_key[i]
        
        return name



    async def bootstrap(self, channel):
        self.broker_exchange = await channel.declare_exchange(
            name=self.exchange,
            type=ExchangeType.DIRECT
        )

        for queue, routing_keys in self.router_keys_for_queues.items():
            queue = await channel.declare_queue(name=queue)
            if queue.name == self.queue:
                self.broker_queue = queue
            
            for routing_key in routing_keys:
                await queue.bind(self.broker_exchange, routing_key=routing_key)

    async def _on_message(self, message):
        async with message.process():
            payload = message.body.decode()
            data = json.loads(payload)
            data["type"] = self.convert_routing_key(data.get("type"))
            print(data["type"])

            messagebus = MessageBus(
                event_handlers=self.event_handlers,
                command_handlers=self.command_handlers,
                broker=self
            )
            await messagebus.handle(data)



    async def publish(self, message):
        connection = await get_connection()
        
        async with connection:
            routing_key = self.routing_key_builder(message)
            message_dict = asdict(message)
            message_dict["type"] = routing_key
            message_json = json.dumps(message_dict)

            message = Message(
                message_json.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json"
            )

            channel = await connection.channel()
            exchange = await channel.declare_exchange(name=self.exchange, type=ExchangeType.DIRECT)
            await exchange.publish(
                message=message,
                routing_key=routing_key
            )

    async def receive(self, channel):
        await channel.set_qos(prefetch_count=1)
        await self.broker_queue.consume(self._on_message)

