import uuid

from sqlalchemy import UUID, TypeDecorator
from sqlalchemy.engine import Dialect

from tests.fixtures.domain.value_objs import TestId


class TestIdDBType(TypeDecorator[TestId]):
    impl = UUID

    cache_ok = True

    def process_bind_param(self, value: TestId | None, dialect: Dialect) -> uuid.UUID | None:
        if value is not None and hasattr(value, "value"):
            return value.value

    def process_result_value(self, value: uuid.UUID | None, dialect: Dialect) -> TestId | None:
        if value is not None:
            return TestId(value)
