from abc import ABC

from shared.application.ports.repositories import AbstractRepository
from src.auth.domain.aggregate import User, SessionGroup


class UsersRepository(AbstractRepository, ABC):
    aggregate = User


class SessionGroupsRepository(AbstractRepository, ABC):
    aggregate = SessionGroup
