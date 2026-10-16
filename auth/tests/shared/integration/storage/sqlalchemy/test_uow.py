import pytest
from sqlalchemy import select

from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus
from tests.fixtures.domain.aggregates import TestAggregate
from tests.fixtures.infrastructure.shared.sqlalchemy.uow import SQLAlchemyTestAggregateUow
from tests.fixtures.domain.events import UserCreated
from tests.fixtures.application.events import UserCreated as IUserCreated


@pytest.mark.asyncio
async def test_uow(setup_database, sessionmaker_fixture):
    uow = SQLAlchemyTestAggregateUow(sessionmaker_fixture)
    aggregate = TestAggregate(first_name="Anton", last_name="Mazur", age=21, version_num=1)
    d_event = UserCreated(
        id=1,
        username=aggregate.first_name,
        email=aggregate.last_name,
        is_active=True,
        password_hash="some_hash",
    )
    i_event = IUserCreated(
        type=IUserCreated.__name__,
        correlation_id=d_event.correlation_id,
        event_id=d_event.event_id,
        id=1,
        username=aggregate.first_name,
        is_active=True,
    )
    async with uow:
        await uow.test_aggregate.add(aggregate)
        uow.events.append(d_event)
        uow.events.append(i_event)
        await uow.commit()

    async with uow:
        res = await uow.test_aggregate.get(aggregate_id=aggregate.aggregate_id)
        print(res.__dict__)
        assert isinstance(res, TestAggregate)
        stmt = select(OutboxMessage).filter_by(status=OutboxStatus.pending)
        res_outbox = await uow._session.execute(stmt)
        assert len(res_outbox.scalars().all()) == 2
