from typing import Any

from shared.application.commands import Command
from shared.application.events.events import IntegrationEvent
from shared.application.handlers.handlers import CommandHandler, EventHandler
from shared.application.handlers.registry import HandlerRegistry, handlers_registry
from shared.domain.events import DomainEvent

type Message = DomainEvent | IntegrationEvent | Command
type MessageType = type[Message]
type Handler = EventHandler | CommandHandler


class MessageBus:
    def __init__(self):
        self.registry: HandlerRegistry = handlers_registry
        self._command_result: Any = None

    async def handle(self, message: Message):
        if isinstance(message, DomainEvent | IntegrationEvent):
            await self._handle_event(message)
        elif isinstance(message, Command):
            await self._handle_command(message)
        else:
            raise TypeError("Message type must be Event or Command")

    async def _handle_event(self, event: DomainEvent | IntegrationEvent):
        handlers = self.registry.get(type(event))
        for handler in handlers:
            if isinstance(handler, EventHandler):
                await handler(event)

    async def _handle_command(self, command: Command):
        try:
            handlers = self.registry.get(type(command))
            for handler in handlers:
                self._command_result = await handler(command)
        except ValueError:
            raise ValueError("Coudn`t process a command")

    @property
    def command_result(self):
        return self._command_result
