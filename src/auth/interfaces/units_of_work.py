from abc import ABC

from src.core.interfaces.units_of_work import AbstractUnitOfWork

from src.auth.interfaces.repository import UsersRepository, RefreshSessionsRepository

class UsersUnitOfWork(AbstractUnitOfWork, ABC):
    users: UsersRepository

class RefreshSessionsUnitOfwork(AbstractUnitOfWork, ABC):
    refresh_sessions: RefreshSessionsRepository