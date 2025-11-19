from abc import ABC, abstractmethod

from typing import Self

from src.core.interfaces.repository import TrackingRepository

class AbstractUnitOfWork(ABC):

    async def __aenter__(self) -> Self:
        return self
    
    async def __aexit__(self, *args, **kwargs) -> None:
        await self.rollback()
    
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
    
    @property
    def events(self):
        events = []
        for attr in dir(self):
            attr = getattr(self, attr)
            if isinstance(attr, TrackingRepository):
                events.extend(list(attr.seen))

        print(bool(events))
        while events:
            yield events.pop(0)