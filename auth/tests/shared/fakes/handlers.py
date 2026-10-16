from shared.application.dto import BaseDTO
from shared.application.events.events import IntegrationEvent
from shared.application.handlers.handlers import CommandHandler, EventHandler
from shared.domain.events import DomainEvent
from tests.fakes.commands import CreateUser


class CreateUserHandler(CommandHandler):
    async def __call__(self, cmd: CreateUser):
        print("user created")
        return BaseDTO()


class UserCreatedHandler(EventHandler):
    async def __call__(self, event: DomainEvent | IntegrationEvent) -> None:
        print("do some things with user")


class SomeCommandHandler(CommandHandler):
    async def __call__(self, cmd: CreateUser):
        print("do stuff")
