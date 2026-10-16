from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from shared.domain.aggregates import Aggregate

T = TypeVar("T", bound=Aggregate)


class AbstractRepository(ABC, Generic[T]):
    aggregate: type[T]

    @abstractmethod
    async def get(self, *filter, **filter_by) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, aggregate: T) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *filter, **filter_by) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, aggregate: T, *filter, **filter_by) -> T | None:
        raise NotImplementedError

    def _to_dict(self, aggregate: T) -> dict[str, Any]:
        return {k: v for k, v in aggregate.__dict__.items() if k not in ["events"]}


R = TypeVar("R", bound=AbstractRepository[Any])


class TrackingRepository(Generic[T, R]):
    def __init__(self, repository: R):
        self.seen: set[T] = set()
        self.repository: AbstractRepository = repository

    async def get(self, *filter, **filter_by) -> T | None:
        aggregate = await self.repository.get(*filter, **filter_by)

        if aggregate:
            self.seen.add(aggregate)
        return aggregate

    async def add(self, aggregate: T) -> T | None:
        self.seen.add(aggregate)
        return await self.repository.add(aggregate)

    async def delete(self, *filter, **filter_by) -> int | None:
        await self.repository.delete(*filter, **filter_by)

    async def update(self, aggregate: T, *filter, **filter_by) -> T | None:
        self.seen.add(aggregate)
        return await self.repository.update(aggregate, *filter, **filter_by)
