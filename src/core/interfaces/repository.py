from abc import ABC, abstractmethod

from typing import Optional, Union, Dict, Set

from src.core.interfaces.model import AbstractModel

class AbstractRepository(ABC):

    @abstractmethod
    async def get(self, *filter, **filter_by) -> Optional[AbstractModel]:
        raise NotImplementedError
    
    @abstractmethod
    async def add(self, model: AbstractModel)  -> AbstractModel:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, *filter, **filter_by):
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, model: AbstractModel, *filter, **filter_by) -> AbstractModel:
        raise NotImplementedError
    
    @abstractmethod
    async def list(self) -> list[AbstractModel]:
        raise NotImplementedError
    
class TrackingRepository:

    def __init__(self, repository: AbstractRepository):
        self.seen = set()
        self.repository = repository

    async def get(self, *filter, **filter_by):
        model = await self.repository.get(*filter, **filter_by)
        
        if model:
            self.seen.add(model)
        return model

    async def add(self, model: AbstractModel, exclude: Optional[Set] = None):
        self.seen.add(model)
        model = await self.repository.add(model, exclude)
        return model
    
    async def delete(self, *filter, **filter_by):
        #add tracking
        await self.repository.delete(*filter, **filter_by)
    
    async def update(self, model: Union[AbstractModel, Dict], *filter, **filter_by):
        self.seen.add(model)
        return await self.repository.update(model, *filter, **filter_by)

class ImagesRepository(AbstractRepository, ABC):
    pass