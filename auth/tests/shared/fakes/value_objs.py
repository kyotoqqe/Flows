from dataclasses import dataclass

from shared.domain.value_objs import EntityId


@dataclass(frozen=True)
class TestId(EntityId):
    pass
