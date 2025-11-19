from abc import ABC, abstractmethod

from src.core.interfaces.events import AbstractEvent
from src.core.interfaces.commands import AbstractCommand

class AbstractHandler(ABC):

    @abstractmethod
    def __init__(self):
        raise NotImplementedError
    
class AbstractEventHandler(AbstractHandler):
    
    @abstractmethod
    async def __call__(self, event: AbstractEvent):
        raise NotImplementedError
    
class AbstractCommandHandler(AbstractHandler):
    
    @abstractmethod
    async def __call__(self, command: AbstractCommand):
        raise NotImplementedError