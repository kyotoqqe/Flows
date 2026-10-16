from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from shared.application.commands import Command
from shared.application.dto import BaseDTO
from shared.application.events.events import IntegrationEvent
from shared.domain.events import DomainEvent

c = TypeVar("c", bound=Command)


class EventHandler(ABC):
    @abstractmethod
    async def __call__(self, event: DomainEvent | IntegrationEvent) -> None:
        raise NotImplementedError


class CommandHandler(ABC, Generic[c]):
    @abstractmethod
    async def __call__(self, cmd: c) -> BaseDTO | None:
        raise NotImplementedError
