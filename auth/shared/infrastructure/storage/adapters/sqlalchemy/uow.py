from typing import Self

from shared.application.ports.uow import AbstractUoW
from shared.infrastructure.inbox.adapters.sqlalchemy.inbox import SQlAlchemyInbox
from shared.infrastructure.outbox.adapters.sqlalchemy.writer import SQLAlchemyOutboxWriter
# from shared.infrastructure.shared.sqlalchemy.connection import sessionmaker


class SQLAlchemyUoW(AbstractUoW):
    def __init__(self, sessionmaker) -> None:
        super().__init__()
        self._sessionmaker = sessionmaker

    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self._session = self._sessionmaker()
        self.outbox = SQLAlchemyOutboxWriter(self._session)
        self.inbox = SQlAlchemyInbox(self._session)
        return uow

    async def __aexit__(self, *args, **kwargs):
        await super().__aexit__(*args, **kwargs)
        await self._session.close()

    async def commit(self):
        await super().commit()
        await self._session.commit()

    async def rollback(self):
        self._session.expunge_all()
        await self._session.rollback()
