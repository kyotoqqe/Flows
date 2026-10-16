import asyncio

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
)
from aio_pika.exceptions import AMQPConnectionError

from shared.infrastructure.ipc.messaging.adapters.rabbitmq.config import rabbitmq_settings


class RabbitBase:
    def __init__(self):
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None

    async def get_connection(self) -> AbstractConnection:
        rabbimq_url = "amqp://guest:guest@rabbitmq:5672/"
        connection = await aio_pika.connect_robust(rabbimq_url, timeout=5)
        return connection

    @property
    def channel(self) -> AbstractChannel:
        if self._channel is None:
            raise ValueError("Please use context manager for Rabbit helper.")
        return self._channel

    async def __aenter__(self):
        self._connection = await self.get_connection()
        self._channel = await self._connection.channel(
            publisher_confirms=True
        )  # on_return_raises = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
