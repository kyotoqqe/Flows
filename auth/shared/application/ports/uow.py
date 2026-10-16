from abc import ABC, abstractmethod
from typing import Self

from shared.application.commands import Command
from shared.application.events.events import IntegrationEvent
from shared.application.handlers.handlers import CommandHandler, EventHandler
from shared.application.ports.repositories import TrackingRepository
from shared.domain.events import DomainEvent
from shared.infrastructure.inbox.ports.inbox import AbstractInbox
from shared.infrastructure.outbox.ports.writer import AbstractOutboxWriter


class AbstractUoW(ABC):
    outbox: AbstractOutboxWriter
    inbox: AbstractInbox

    def __init__(self) -> None:
        self.events = []

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ):
        await self.rollback()

    async def commit(self):
        await self._save_outbox_events()
        await self._save_message_in_inbox()

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    async def _save_outbox_events(self):
        for event in self._get_events():
            await self.outbox.save(event)

    async def _save_message_in_inbox(self):
        if hasattr(self, "_message_id"):
            inbox_msg = await self.inbox.get_message(message_id=self._message_id)
            if not inbox_msg:
                await self.inbox.save(
                    message_id=self._message_id,
                    correlation_id=self._correlation_id,
                    type=self._type,
                    handler_name=self._handler_name,
                )

    def _get_events(self):
        for attr in dir(self):
            attr = getattr(self, attr)
            if isinstance(attr, TrackingRepository):
                for obj in attr.seen:
                    self.events.extend(obj.events)
        while self.events:
            yield self.events.pop(0)

    def set_inbox_info(
        self,
        handler: type[EventHandler | CommandHandler],
        message: IntegrationEvent | Command | DomainEvent,
    ):
        if isinstance(message, (IntegrationEvent, DomainEvent)):
            self._message_id = message.event_id
        elif isinstance(message, Command):
            self._message_id = message.command_id

        self._handler_name = handler.__name__
        self._type = message.__class__.__name__
        self._correlation_id = message.correlation_id
