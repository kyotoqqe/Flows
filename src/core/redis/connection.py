import redis.asyncio as redis

from src.core.redis.config import redis_settings

redis_connection = redis.ConnectionPool().from_url(
    url = f"redis://{redis_settings.redis_host}:{redis_settings.redis_port}/",
    password = redis_settings.redis_password
)

