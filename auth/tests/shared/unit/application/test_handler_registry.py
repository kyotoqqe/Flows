from shared.application.exceptions import CommandAlreadyRegistrated, HandlerMappingError
from shared.application.handlers.registry import handlers_registry
from shared.tests.fixtures.application.commands import CreateUser
from shared.tests.fixtures.application.events import UserCreated
from shared.tests.fixtures.application.handlers import (
    CreateUserHandler,
    SomeCommandHandler,
    UserCreatedHandler,
)
from shared.tests.fixtures.domain.events import UserCreated as DomainUserCreated


def test_handler_registry():
    handlers_registry.register(CreateUserHandler(), CreateUser)
    handlers_registry.register(UserCreatedHandler(), UserCreated)
    handlers_registry.register(UserCreatedHandler(), DomainUserCreated)

    assert len(handlers_registry.registry) == 3


def test_handlers_and_event_mapping_failed():
    try:
        handlers_registry.register(CreateUserHandler(), UserCreated)
        handlers_registry.register(UserCreatedHandler(), CreateUser)
    except Exception as e:
        assert isinstance(e, HandlerMappingError)


def test_registry_multiple_handlers_on_command():
    try:
        handlers_registry.register(CreateUserHandler(), CreateUser)
        handlers_registry.register(SomeCommandHandler(), CreateUser)
    except Exception as e:
        assert isinstance(e, CommandAlreadyRegistrated)


def test_handlers_searching():
    handlers = handlers_registry.get(CreateUser)
    assert len(handlers) == 1
