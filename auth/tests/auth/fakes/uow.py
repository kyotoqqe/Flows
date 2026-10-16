from typing import Self

from shared.application.ports.repositories import TrackingRepository
from src.auth.application.ports.uow import SessionGroupsUoW, UsersUoW
from tests.auth.fakes.repository import FakeSessionGroupsRepository, FakeUsersRepository
from tests.shared.fakes.uow import FakeUow


class FakeUsersUoW(FakeUow, UsersUoW):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users = TrackingRepository(FakeUsersRepository())
        return uow


class FakeSessionGroupsUoW(FakeUow, SessionGroupsUoW):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.session_groups = TrackingRepository(FakeSessionGroupsRepository())
        return uow
