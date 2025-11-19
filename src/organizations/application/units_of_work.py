from src.core.redis.interfaces.units_of_work import RedisUnitOfWork
from src.core.database.interfaces.units_of_work import SQLAlchemyUnitOfWork

from src.organizations.interfaces.units_of_works import OrganizationRequestsUnitOfWork, OrganizationsUnitOfWork
from src.organizations.infrastructure.redis.repository import RedisOrganizationRequestsRepository
from src.organizations.infrastructure.database.repository import SQLAlchemyOrganizationsRepository

#----------------
from src.organizations.application.events import OrganizationRequestCreated

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
        self.organizations = SQLAlchemyOrganizationsRepository(session=self._session)
        return uow