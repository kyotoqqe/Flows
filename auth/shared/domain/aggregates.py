from typing import Generic, TypeVar

from shared.domain.events import DomainEvent
from shared.domain.value_objs import EntityId

T = TypeVar("T", bound=EntityId)


class Aggregate(Generic[T]):
    def __init__(self, version_num: int) -> None:
        self.aggregate_id: T
        self.version_num = version_num
        self.events: list[DomainEvent] = []
