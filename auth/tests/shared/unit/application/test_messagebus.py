from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from shared.application.dto import BaseDTO
from shared.application.handlers.handlers import EventHandler
from shared.application.handlers.registry import handlers_registry
from shared.application.messagebus import MessageBus
from shared.tests.fixtures.application.commands import CreateUser
from shared.tests.fixtures.domain.events import UserCreated


@pytest.mark.asyncio
async def test_message_handling():
    messagebus = MessageBus()
    mock_handler = AsyncMock(spec=EventHandler)
    handlers_registry.register(mock_handler, UserCreated)
    event = UserCreated(
        id=1, username="test", email="a@gmail.com", password_hash="some_hash", is_active=True
    )

    await messagebus.handle(event)
    mock_handler.assert_awaited_once()
    mock_handler.assert_awaited_once_with(event)

    cmd = CreateUser(
        correlation_id=uuid4(), timestamp=1788985727924, username="test", email="a@gmail.com"
    )

    await messagebus.handle(cmd)
    assert isinstance(messagebus.command_result, BaseDTO)
