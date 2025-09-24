from src.profiles.interfaces.units_of_work import ProfilesUnitOfWork
from src.profiles.services import ProfileService

class ProfileCreator:
    @staticmethod
    async def create(uow: ProfilesUnitOfWork, user_id: int, username: str):
        service = ProfileService(uow)
        return await service.create_profile(user_id=user_id, username=username)