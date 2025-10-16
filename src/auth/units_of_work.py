from src.core.database.interfaces.units_of_work import SQLAlchemyUnitOfWork
from src.core.redis.interfaces.units_of_work import RedisUnitOfWork

from src.auth.interfaces.units_of_work import UsersUnitOfWork, RefreshSessionsUnitOfwork
from src.auth.infrastructure.database.repository import SQLAlchemyUsersRepository, SQLALchemyRefreshSessionsRepository
from src.auth.infrastructure.redis.repository import RedisRefreshSessionsRepository

class SQLAlchemyUsersUnitOfWork(SQLAlchemyUnitOfWork, UsersUnitOfWork):

    async def __aenter__(self):
        uow = await super().__aenter__()
        self.users = SQLAlchemyUsersRepository(self._session)
        #self.refresh_sessions = SQLALchemyRefreshSessionsRepository(self._session)
        return uow
    
class RedisRefreshSessionsUnitOfWork(RedisUnitOfWork, RefreshSessionsUnitOfwork):

    async def __aenter__(self):
        uow = await super().__aenter__()
        self.refresh_sessions = RedisRefreshSessionsRepository(
            redis=self._redis,
            pipeline=self._pipe
        )
        return uow

