from dataclasses import dataclass
from typing import Generic, TypeVar

from shared.domain.value_objs import EntityId

T = TypeVar("T", bound=EntityId)


@dataclass(eq=False, kw_only=True)
class Entity(Generic[T]):
    id: T

    def __eq__(self, other: object, /) -> bool:
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
