from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from shared.application.ports.repositories import AbstractRepository
from shared.domain.aggregates import Aggregate
from shared.infrastructure.storage.exceptions import (
    StorageConcurrencyError,
    StorageDataInvalidError,
    StorageException,
)


# maybe retray TimeoutError, DisconnectionError
class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, *filter, **filter_by) -> Aggregate | None:
        try:
            stmt = select(self.aggregate).filter(*filter).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise StorageException("Failed to get aggregate") from e

    async def add(self, aggregate: Aggregate) -> Aggregate | None:
        try:
            stmt = (
                insert(self.aggregate)
                .values(**self._to_dict(aggregate))
                .on_conflict_do_nothing()
                .returning(self.aggregate)
            )
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()
        except IntegrityError as e:
            raise StorageException("Database constraint violation") from e
        except SQLAlchemyError as e:
            raise StorageException("Failed to add aggregate") from e

    async def delete(self, *filter, **filter_by) -> Aggregate | None:
        try:
            stmt = (
                delete(self.aggregate)
                .filter(*filter)
                .filter_by(**filter_by)
                .returning(self.aggregate)
            )
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise StorageException("Failed to delete aggregate") from e

    async def update(self, aggregate: Aggregate, *filter, **filter_by) -> Aggregate | None:
        try:
            stmt = (
                update(self.aggregate)
                .filter(*filter)
                .filter_by(**filter_by)
                .values(**self._to_dict(aggregate))
                .returning(self.aggregate)
            )
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()
        except IntegrityError:
            raise StorageDataInvalidError("Data integrity violation")
        except StaleDataError:
            raise StorageConcurrencyError("Row version mismatch, data is stale")
        except SQLAlchemyError as e:
            raise StorageException("Failed to update aggregate") from e

    def _to_dict(self, aggregate: Aggregate) -> dict[str, Any]:
        raw_dict = super()._to_dict(aggregate)
        if "_sa_instance_state" in raw_dict:
            del raw_dict["_sa_instance_state"]

        return raw_dict
