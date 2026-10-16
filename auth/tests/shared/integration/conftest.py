from uuid import uuid4

import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import clear_mappers

from shared.infrastructure.outbox.adapters.sqlalchemy.writer import SQLAlchemyOutboxWriter
from tests.fixtures.application.events import UserCreated
from tests.fixtures.infrastructure.shared.sqlalchemy.base import test_metadata_obj
from tests.fixtures.infrastructure.shared.sqlalchemy.config import test_postgres_db_settings
from tests.fixtures.infrastructure.shared.sqlalchemy.orm import (
    start_mappers as outbox_mapper,
)


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(test_postgres_db_settings.get_db_url, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def connection(async_engine):
    async with async_engine.connect() as conn:
        yield conn


@pytest_asyncio.fixture(scope="function")
async def sessionmaker_fixture(async_engine):
    return async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def setup_database(connection):
    outbox_mapper()
    async with connection.begin():
        await connection.run_sync(test_metadata_obj.drop_all)
        await connection.run_sync(test_metadata_obj.create_all)
        table_names = list(test_metadata_obj.tables.keys())
        print("Registered tables:", table_names)

    yield
    clear_mappers()
    async with connection.begin():
        await connection.run_sync(test_metadata_obj.drop_all)


@pytest_asyncio.fixture(scope="function")
async def generate_outbox_messages(setup_database, sessionmaker_fixture):
    async def _make(count: int):
        async with sessionmaker_fixture() as session:
            writer = SQLAlchemyOutboxWriter(session=session)
            for i in range(count):
                event = UserCreated(
                    type="UserCreated",
                    correlation_id=uuid4(),
                    timestamp=17891124516,
                    event_id=uuid4(),
                    id=22,
                    username="test",
                    is_active=True,
                )

                await writer.save(event)
            await session.commit()

    return _make

    # await session.close()
