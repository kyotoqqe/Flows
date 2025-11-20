from src.core.database.interfaces.units_of_work import SQLAlchemyUnitOfWork

from src.organizations.membership.interfaces.units_of_work import MembershipsUnitOfWork
from src.organizations.membership.infrastructure.database.repository import SQLAlchemyMembershipsRepository

class SQLAlchemyMembershipsUnitOfWork(SQLAlchemyUnitOfWork, MembershipsUnitOfWork):

    async def __aenter__(self):
        uow = await super().__aenter__()
        self.memberships = SQLAlchemyMembershipsRepository(session=self._session)
        return uow