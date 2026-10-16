from shared.application.commands import Command
from shared.application.events.events import IntegrationEvent
from shared.application.exceptions import (
    CommandAlreadyRegistrated,
    HandlerMappingError,
    HandlerNotFound,
)
from shared.application.handlers.handlers import CommandHandler, EventHandler
from shared.domain.events import DomainEvent
from shared.infrastructure.shared.sqlalchemy.connection import sessionmaker
from src.auth.application.commands import RegisterUser
from src.auth.application.handlers import RegisterUserHandler
from src.auth.infrastructure.security.hasher import BcryptPasswordHasher
from src.auth.infrastructure.security.tokens import FernetTokenGenerator
from src.auth.infrastructure.storage.adapters.sqlalchemy.uow import SQLAlchemyUsersUoW

# move to types or something
type Message = DomainEvent | IntegrationEvent | Command
type MessageType = type[DomainEvent | IntegrationEvent | Command]
type Handler = EventHandler | CommandHandler


class HandlerRegistry:
    def __init__(self) -> None:
        self.registry: dict[MessageType, list[Handler]] = {}

    def register(self, handler: Handler, message: MessageType):
        if (
            issubclass(message, DomainEvent | IntegrationEvent)
            and isinstance(handler, CommandHandler)
        ) or (issubclass(message, Command) and isinstance(handler, EventHandler)):
            raise HandlerMappingError(
                "Does not allow register commands on event handlers ans and vice versa"
            )

        if message not in self.registry:
            self.registry[message] = [handler]
        else:
            if issubclass(message, Command):
                raise CommandAlreadyRegistrated("Only one handler could exist for one command")
            self.registry[message].append(handler)

    def get(self, message: MessageType) -> list[Handler]:
        if message not in self.registry:
            raise HandlerNotFound("Not found any handlers for this message")

        return self.registry[message]


handlers_registry = HandlerRegistry()

# register your handlers here

handlers_registry.register(
    RegisterUserHandler(
        uow=SQLAlchemyUsersUoW(sessionmaker),
        password_hasher=BcryptPasswordHasher(),
        token_generator=FernetTokenGenerator(),
    ),
    RegisterUser,
)
