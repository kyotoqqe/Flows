from abc import ABC, abstractmethod
from typing import Any


class AbstractRpcClient(ABC):
    @abstractmethod
    async def call(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError
