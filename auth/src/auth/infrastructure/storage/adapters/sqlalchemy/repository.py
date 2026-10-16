from src.auth.application.ports.repository import UsersRepository
from shared.infrastructure.storage.adapters.sqlalchemy.repository import SQLAlchemyRepository


class SQLAlchemyUsersRepository(SQLAlchemyRepository, UsersRepository):
    pass
