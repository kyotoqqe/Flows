from typing import Generic, TypeVar

from shared.application.ports.repositories import AbstractRepository
from shared.domain.aggregates import Aggregate

T = TypeVar("T", bound=Aggregate)


class FakeRepository(AbstractRepository[T], Generic[T]):
    storage: set[T] = set()

    async def get(self, *filter, **filter_by) -> T | None:
        for agg in self.storage:
            for f, v in filter_by.items():
                agg_v = getattr(agg, f, None)

                if agg_v is not None and agg_v == v:
                    return agg

    async def add(self, aggregate: T) -> T | None:
        if aggregate not in self.storage:
            self.storage.add(aggregate)

    async def delete(self, *filter, **filter_by) -> T | None:
        agg = await self.get(*filter, **filter_by)

        if agg is not None:
            self.storage.remove(agg)

    async def update(self, aggregate: T, *filter, **filter_by) -> T | None:
        return await self.get(*filter, **filter_by)
