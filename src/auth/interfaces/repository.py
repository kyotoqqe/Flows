from abc import ABC

from src.core.interfaces.repository import AbstractRepository

class UsersRepository(AbstractRepository, ABC):
    pass

class RefreshSessionsRepository(AbstractRepository, ABC):
    pass