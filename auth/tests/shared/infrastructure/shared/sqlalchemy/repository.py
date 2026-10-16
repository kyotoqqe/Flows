from abc import ABC

from shared.application.ports.repositories import AbstractRepository
from shared.infrastructure.storage.adapters.sqlalchemy.repository import SQLAlchemyRepository
from tests.fixtures.domain.aggregates import TestAggregate


class TestRepository(AbstractRepository, ABC):
    aggregate = TestAggregate


# generic
class SQLAlchemyTestRepository(TestRepository, SQLAlchemyRepository):
    pass
