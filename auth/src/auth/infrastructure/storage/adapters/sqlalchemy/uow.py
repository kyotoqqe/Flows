from typing import Self

from shared.application.ports.repositories import TrackingRepository
from shared.infrastructure.storage.adapters.sqlalchemy.uow import SQLAlchemyUoW
from src.auth.application.ports.uow import UsersUoW
from src.auth.infrastructure.storage.adapters.sqlalchemy.repository import SQLAlchemyUsersRepository


class SQLAlchemyUsersUoW(SQLAlchemyUoW, UsersUoW):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users = TrackingRepository(SQLAlchemyUsersRepository(self._session))
        return uow
