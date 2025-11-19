import asyncio
import aio_pika

from src.core.rabbitmq.config import rabbitmq_settings

async def get_connection():
    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust(
                host=rabbitmq_settings.rabbitmq_default_host,
                login=rabbitmq_settings.rabbitmq_default_user,
                password=rabbitmq_settings.rabbitmq_default_pass
            )
            print("✅ Connected to RabbitMQ")
            return connection
        except Exception as e:
            print(f"🐇 RabbitMQ not ready, retry {attempt+1}/10: {e}")
            await asyncio.sleep(3)
    raise RuntimeError("Failed to connect to RabbitMQ after 10 attempts")
