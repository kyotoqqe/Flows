import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class ValueObj:
    pass


@dataclass(frozen=True)
class EntityId(ValueObj):
    value: UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return str(self.value)
