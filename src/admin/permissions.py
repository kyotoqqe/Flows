import functools

from starlette.requests import Request

from src.auth.services import AuthService
from src.auth.units_of_work import SQLAlchemyUsersUnitOfWork, RedisRefreshSessionsUnitOfWork
from src.auth.domain.value_obj import UserRole

def only_for_superuser(func):
    @functools.wraps(func)
    async def wrapper(self, request: Request):
        access_token = request.session.get("access_token")
        service = AuthService(
            uow=SQLAlchemyUsersUnitOfWork()
        )
        user = await service.get_user(access_token)

        if user.role == UserRole.superuser:
            return await func(self, request)
        return False
    return wrapper

