from src.core.redis.interfaces.units_of_work import RedisUnitOfWork
from src.core.database.interfaces.units_of_work import SQLAlchemyUnitOfWork
from src.core.interfaces.repository import TrackingRepository

from src.organizations.organizations.interfaces.units_of_works import OrganizationRequestsUnitOfWork, OrganizationsUnitOfWork
from src.organizations.organizations.infrastructure.redis.repository import RedisOrganizationRequestsRepository
from src.organizations.organizations.infrastructure.database.repository import SQLAlchemyOrganizationsRepository


class RedisOrganizationRequestsUnitOfWork(RedisUnitOfWork, OrganizationRequestsUnitOfWork):

    async def __aenter__(self):
        uow = await super().__aenter__()
        self.organization_requests = RedisOrganizationRequestsRepository(
            redis=self._redis,
            pipeline=self._pipe
        )
        return uow

class SQLAlchemyOrganizationsUnitOfWork(SQLAlchemyUnitOfWork, OrganizationsUnitOfWork):
    
    async def __aenter__(self):
        uow = await super().__aenter__()
        self.organizations = TrackingRepository(
            repository=SQLAlchemyOrganizationsRepository(session=self._session)
        )
        return uow