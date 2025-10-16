from src.core.domain.services import DomainService
from src.auth.domain.rules import IsValidRefreshSessionCount

from src.profiles.interfaces.units_of_work import ProfilesUnitOfWork
from src.profiles.services import ProfileService

#rewrite use events
class ProfileCreator:
    @staticmethod
    async def create(uow: ProfilesUnitOfWork, user_id: int, username: str):
        service = ProfileService(uow)
        return await service.create_profile(user_id=user_id, username=username)

class CheckRefreshSessionCount(DomainService):
    
    def check_rule(self, sessions_count: int):
        super().check_rule(
            IsValidRefreshSessionCount(sessions_count)
        )