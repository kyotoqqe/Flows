from shared.domain.services import DomainService
from src.auth.domain.aggregate import User
from src.auth.domain.value_objs import UserRole


class UserBanningService(DomainService):
    def check_can_ban(self, user: User, target: User) -> bool:
        if user.aggregate_id == target.aggregate_id:
            return False
        if user.role == UserRole.MEMBER:
            return False
        elif user.role == UserRole.ADMIN and target.role in [UserRole.ADMIN, UserRole.OWNER]:
            return False

        return True
