from redis.asyncio.client import Redis

from src.core.redis.connection import redis_connection
from src.core.interfaces.units_of_work import AbstractUnitOfWork

class RedisUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        super().__init__()
        self._redis = Redis().from_pool(connection_pool=redis_connection)

    async def __aenter__(self):
        self._pipe = self._redis.pipeline(transaction=True)
        await super().__aenter__()
    
    async def __aexit__(self, *args, **kwargs):
        await super().__aexit__(*args, **kwargs)
        await self._redis.close()
    
    async def commit(self):
        await self._pipe.execute()
    
    async def rollback(self):
        await self._pipe.discard()