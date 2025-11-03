from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.auth.services import AuthService
from src.auth.units_of_work import SQLAlchemyUsersUnitOfWork, RedisRefreshSessionsUnitOfWork
from src.auth.config import cookie_settings
from src.admin.permissions import only_for_superuser


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        service = AuthService(
            uow=SQLAlchemyUsersUnitOfWork(),
            redis_uow=RedisRefreshSessionsUnitOfWork()
        )

        tokens = await service.login(
            username=email,
            password=password
        )
        
        request.session.update({"access_token": tokens.access})
        request.state.refresh_token = tokens.refresh
       
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    @only_for_superuser
    async def authenticate(self, request: Request) -> bool:
        print("puupupu")
        # Check the token in depth
        return True


        # Check the token in depth
      


authentication_backend = AdminAuth(secret_key="...")
