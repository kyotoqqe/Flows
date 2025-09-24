from src.core.database.interfaces.repository import SQLAlchemyRepository

from src.auth.interfaces.repository import UsersRepository, RefreshSessionsRepository
from src.auth.domain.entities import User, RefreshSession


class SQLAlchemyUsersRepository(SQLAlchemyRepository, UsersRepository):
    model = User

class SQLALchemyRefreshSessionsRepository(SQLAlchemyRepository, RefreshSessionsRepository):
    model = RefreshSession