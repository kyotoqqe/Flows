from sqlalchemy import Column, Integer, String, Table

from shared.infrastructure.outbox.adapters.sqlalchemy.orm import outbox_table
from shared.infrastructure.outbox.ports.message import OutboxMessage
from src.auth.domain.aggregate import User
from tests.fixtures.domain.aggregates import TestAggregate
from tests.fixtures.infrastructure.shared.sqlalchemy.base import (
    test_mapper_registry,
    test_metadata_obj,
)
from tests.fixtures.infrastructure.shared.sqlalchemy.type_decorators import TestIdDBType
from src.auth.infrastructure.storage.adapters.sqlalchemy.orm.orm import users_table

test_outbox_table = outbox_table.to_metadata(test_metadata_obj)
test_users_table = users_table.to_metadata(test_metadata_obj)

test_aggregate_table = Table(
    "test_aggregates",
    test_metadata_obj,
    Column("aggregate_id", TestIdDBType(), primary_key=True),
    Column("first_name", String(32), nullable=False),
    Column("last_name", String(32)),
    Column("age", Integer),
    Column("version_num", Integer, nullable=False),
)


def start_mappers():
    test_outbox_mapper = test_mapper_registry.map_imperatively(OutboxMessage, test_outbox_table)
    test_aggregate_mappeer = test_mapper_registry.map_imperatively(
        TestAggregate,
        test_aggregate_table,
        properties={
            # "aggregate_id": composite(TestId, test_aggregate_table.c.id),
            "version_num": test_aggregate_table.c.version_num,
        },
    )
    test_users_mapper = test_mapper_registry.map_imperatively(User, test_users_table)
