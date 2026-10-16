from src.auth.application.ports.repository import SessionGroupsRepository, UsersRepository
from src.auth.domain.aggregate import SessionGroup, User
from tests.shared.fakes.repository import FakeRepository


class FakeUsersRepository(FakeRepository[User], UsersRepository):
    aggregate = User


class FakeSessionGroupsRepository(FakeRepository[SessionGroup], SessionGroupsRepository):
    aggregate = SessionGroup
