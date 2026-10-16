from abc import ABC, abstractmethod

from shared.application.events.events import IntegrationEvent
from shared.domain.events import DomainEvent


class AbstractOutboxWriter(ABC):
    @abstractmethod
    async def save(self, event: IntegrationEvent | DomainEvent):
        raise NotImplementedError

    def __len__(self):
        return 0
