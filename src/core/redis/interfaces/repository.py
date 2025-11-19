import json

from redis.asyncio.client import Redis, Pipeline

from src.core.interfaces.repository import AbstractRepository
from src.core.domain.entities import AbstractModel

from typing import Optional, Union, Dict, Set

class RedisRepository(AbstractRepository):
    model: AbstractModel = None
    key_fields: list = None 

    def __init__(self, redis: Redis, pipeline: Union[Redis, Pipeline]):
        self.redis = redis
        self.pipeline = pipeline

    def _key_builder(self, strict_mode: bool = True, **kwargs):
        redis_key= f"{self.model.__name__.lower()}:"
      
        for key in self.key_fields:
            if strict_mode:
                try:
                    value = kwargs[key]
                    redis_key += f"{key}:{value}" #add :
                except KeyError:
                    raise ValueError("Not enough values to build a key") #create custom
            else:
                value = kwargs.get(key)
                redis_key += f"{key}:{value if value else '*'}"
        return redis_key

    async def get(self, scalar: bool = None,  *filter, **filter_by):
        key = self._key_builder(strict_mode=False, **filter_by)
        res = []
        async for data in self.redis.scan_iter(match=key):
            data = await self.redis.get(data)
            model_dict = json.loads(data)
            model = self.model(**model_dict)
            res.append(model)
        
        if scalar:
            return res[0]

        return res
    
    async def add(self, model: Union[AbstractModel, Dict], exclude: Optional[Set] = None, ttl: Optional[int] = None ):
        if isinstance(model, AbstractModel):
            model = await model.to_dict(exclude=exclude)
        key = self._key_builder(**model)
        if await self.redis.exists(key):
            raise ValueError(f"{self.model.__name__} with this data already exist")
        
        model_json = json.dumps(model)
        await self.pipeline.set(key, model_json)
        if ttl:
            await self.pipeline.expire(key, ttl)
        
    
    async def delete(self, *filter, **filter_by):
        key = self._key_builder(**filter_by)
        await self.pipeline.delete(key)
    
    async def update(self, model, *filter, **filter_by):
        model = await model.to_dict()

        key = self._key_builder(**model)
        if not await self.redis.exists(key):
            raise ValueError(f"{self.model.__name__} with this data dont exist")
        
        model_json = json.dumps(model)
        await self.pipeline.set(key, model_json)
    

    async def list(self):
        key = f"{self.model.__name__.lower()}:"
        res = []
        async for data in self.redis.scan_iter(match=key):
            model_dict = json.loads(data)
            model = self.model(**model_dict)
            res.append(model)
        return res