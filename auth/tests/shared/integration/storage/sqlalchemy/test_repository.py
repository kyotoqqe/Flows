import pytest

from tests.fixtures.domain.aggregates import TestAggregate
from tests.fixtures.infrastructure.shared.sqlalchemy.repository import SQLAlchemyTestRepository


@pytest.mark.asyncio
async def test_repository(setup_database, sessionmaker_fixture):
    aggregate = TestAggregate(first_name="Anton", last_name="Mazur", age=21, version_num=1)

    async with sessionmaker_fixture() as session:
        repository = SQLAlchemyTestRepository(session=session)

        await repository.add(aggregate)
        res = await repository.get(aggregate_id=aggregate.aggregate_id)
        assert res.aggregate_id == aggregate.aggregate_id

        res.age = 22
        res.version_num += 1
        res_update = await repository.update(res, aggregate_id=res.aggregate_id)
        print(res_update.age, res_update.first_name, res_update.last_name)
        assert res_update.age == 22

        await repository.delete(aggregate_id=res.aggregate_id)
        res_deleted = await repository.get(aggregate_id=res.aggregate_id)
        assert res_deleted is None
