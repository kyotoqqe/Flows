from typing import Self

from shared.application.ports.uow import AbstractUoW
from tests.shared.fakes.inbox import FakeInbox
from tests.shared.fakes.outbox import FakeOutboxWriter


class FakeUow(AbstractUoW):
    def __init__(self) -> None:
        super().__init__()

    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.outbox = FakeOutboxWriter()
        self.inbox = FakeInbox()
        return uow

    async def rollback(self):
        return
