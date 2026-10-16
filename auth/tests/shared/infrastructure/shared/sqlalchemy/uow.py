from abc import ABC
from typing import Self

from shared.application.ports.repositories import TrackingRepository
from shared.application.ports.uow import AbstractUoW
from shared.infrastructure.storage.adapters.sqlalchemy.uow import SQLAlchemyUoW
from tests.fixtures.infrastructure.shared.sqlalchemy.repository import (
    SQLAlchemyTestRepository,
    TestRepository,
)


class TestAggregateUow(AbstractUoW, ABC):
    test_aggregate: TrackingRepository[TestRepository]


class SQLAlchemyTestAggregateUow(SQLAlchemyUoW, TestAggregateUow):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.test_aggregate = TrackingRepository(SQLAlchemyTestRepository(self._session))
        return uow
