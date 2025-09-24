from abc import ABC, abstractmethod

from typing import Optional

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
    
class ImagesRepository(AbstractRepository, ABC):
    pass