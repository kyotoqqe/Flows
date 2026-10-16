from abc import ABC, abstractmethod
from typing import Any


class AbstractPublisher(ABC):
    @abstractmethod
    async def publish(self, message: Any):  # OutboxMessage
        raise NotImplementedError

    async def bootstrap(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
