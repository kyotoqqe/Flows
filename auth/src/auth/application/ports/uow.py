from abc import ABC

from shared.application.ports.repositories import TrackingRepository
from shared.application.ports.uow import AbstractUoW
from src.auth.application.ports.repository import UsersRepository, SessionGroupsRepository
from src.auth.domain.aggregate import SessionGroup, User


class UsersUoW(AbstractUoW, ABC):
    users: TrackingRepository[User, UsersRepository]


class SessionGroupsUoW(AbstractUoW, ABC):
    session_groups: TrackingRepository[SessionGroup, SessionGroupsRepository]
