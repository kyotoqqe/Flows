from shared.domain.aggregates import Aggregate
from tests.fakes.value_objs import TestId


class TestAggregate(Aggregate[TestId]):
    def __init__(self, first_name: str, last_name: str | None, age: int, version_num: int) -> None:
        super().__init__(version_num)
        self.aggregate_id = TestId()
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
