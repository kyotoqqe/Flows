from typing import Self

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.core.interfaces.units_of_work import AbstractUnitOfWork
from src.core.database.connection import session_maker

class SQLAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self) -> Self:
        super().__init__()
        self._session_factory: async_sessionmaker = session_maker
    
    async def __aenter__(self):
        self._session: AsyncSession = self._session_factory()
        return await super().__aenter__()
    
    async def __aexit__(self, *args, **kwargs):
        await super().__aexit__(*args, **kwargs)
        await self._session.close()

    async def commit(self):
        await self._session.commit()
    
    async def rollback(self):
        self._session.expunge_all()
        await self._session.rollback()