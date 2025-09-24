from src.core.database.interfaces.units_of_work import SQLAlchemyUnitOfWork
from src.core.redis.interfaces.units_of_work import RedisUnitOfWork

from src.profiles.interfaces.units_of_work import ProfilesUnitOfWork, RelationshipsGroupsUnitOfWork, FollowRequestsUnitOfWork
from src.profiles.infrastructure.database.repository import SQLAlchemyProfilesRepository, SQLAlchemyRelationshipsGroupsRepository
from src.profiles.infrastructure.redis.repository import RedisFollowRequetstRepository

#temporary
from src.core.database.repository import SQLAlchemyImageRepository


class SQLAlchemyProfilesUnitOfWork(SQLAlchemyUnitOfWork, ProfilesUnitOfWork):

    async def __aenter__(self):
        uow = await super().__aenter__()
        self.profiles = SQLAlchemyProfilesRepository(self._session)
        self.relationships_groups = SQLAlchemyRelationshipsGroupsRepository(self._session)
        self.images = SQLAlchemyImageRepository(self._session)
        return uow

class SQLAlchemyRelationshipsGroupsUnitOfWork(SQLAlchemyUnitOfWork, RelationshipsGroupsUnitOfWork):

    async def __aenter__(self):
        uow = await super().__aenter__()
        self.relationships_groups = SQLAlchemyRelationshipsGroupsRepository(self._session)
        return uow

class RedisFollowRequestsUnitOfWork(RedisUnitOfWork, FollowRequestsUnitOfWork):
    
    async def __aenter__(self):
        uow = await super().__aenter__()
        self.follow_requests = RedisFollowRequetstRepository(
            redis = self._redis, 
            pipeline = self._pipe
        )
        return uow
